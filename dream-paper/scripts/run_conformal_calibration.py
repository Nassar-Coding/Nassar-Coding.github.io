"""C2: split-conformal recalibration of the quantile model and its effect on the
distribution-aware allocation (professor #82, #83, #86, #92).

The published quantile model is sharp but under-dispersed (90% intervals cover
~77-81%). This script applies split-conformal recalibration using VALIDATION
residuals only, reports calibrated coverage and interval width, and re-runs the
full quantile-interpolated distribution arm of the decision layer on the
calibrated quantiles, comparing simulated loss calibrated vs uncalibrated.

Per-level additive conformal shift (marginal, per city):
  delta_tau = empirical tau-quantile of {y_val - qhat_tau(x_val)}
  qtilde_tau(x) = qhat_tau(x) + delta_tau,  re-sorted for non-crossing.
By construction P(y <= qtilde_tau)=tau on validation; conformal coverage holds
on test under exchangeability.

A reversal of the distribution-aware result under calibration would trigger
stop condition #2. Writes conformal_calibration.csv and conformal_decision.csv.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common.runtime import DATA_INTERIM, DATA_PROCESSED, OUTPUTS, load_config, set_seed  # noqa: E402
from optimization.allocation import (EmpiricalDemand, SimConfig, simulate,  # noqa: E402
                                     greedy_allocate, largest_remainder)
from run_decision import QLEVELS, pivot_matrix  # noqa: E402

LV = [q / 100 for q in QLEVELS]


def conformal_deltas(yv, qv):
    """Per-level additive shift from validation residuals (marginal, per city)."""
    return {q: float(np.quantile(yv - qv[q], q)) for q in LV}


def apply_deltas(qmat, deltas):
    """Shift then enforce non-crossing by cumulative max across sorted levels."""
    levels = sorted(qmat)
    stacked = np.maximum.accumulate(
        np.stack([qmat[q] + deltas[q] for q in levels], axis=0), axis=0)
    return {q: np.maximum(stacked[i], 0.0) for i, q in enumerate(levels)}


def run() -> None:
    set_seed()
    dcfg = load_config("decision.yml")
    kappa = dcfg["kappa_base"]
    active = json.loads((DATA_INTERIM / "active_families.json").read_text())
    vpreds = pd.read_parquet(DATA_PROCESSED / "val_predictions.parquet")
    tpreds = pd.read_parquet(DATA_PROCESSED / "test_predictions.parquet")
    frozen = json.loads((OUTPUTS / "metrics" / "frozen_budgets.json").read_text())
    cities = sorted(tpreds["city"].unique())

    cal_rows, dec_rows = [], []
    for city in cities:
        fams = active[city]["active_families"]
        tq = tpreds[(tpreds.city == city) & (tpreds.scope == "local") &
                    (tpreds.model == "lgbm_quantile")]
        vq = vpreds[(vpreds.city == city) & (vpreds.scope == "local") &
                    (vpreds.model == "lgbm_quantile")]
        tdays = sorted(tq["day"].unique())
        vdays = sorted(vq["day"].unique())
        # validation residual stats per level (flattened over family-days)
        yv = vq["target"].to_numpy(dtype=float)
        qv = {q: vq[f"q{int(q*100):02d}"].to_numpy(dtype=float) for q in LV}
        deltas = conformal_deltas(yv, qv)

        # test matrices
        yt = tq["target"].to_numpy(dtype=float)
        qt_flat = {q: tq[f"q{int(q*100):02d}"].to_numpy(dtype=float) for q in LV}
        qt_cal_flat = apply_deltas(qt_flat, deltas)

        def cover(lo, hi):
            return float(np.mean((yt >= lo) & (yt <= hi)))
        cal_rows.append({
            "city": city,
            "coverage90_uncal": round(cover(qt_flat[0.05], qt_flat[0.95]), 4),
            "coverage90_conformal": round(cover(qt_cal_flat[0.05], qt_cal_flat[0.95]), 4),
            "width90_uncal": round(float(np.mean(qt_flat[0.95] - qt_flat[0.05])), 3),
            "width90_conformal": round(float(np.mean(qt_cal_flat[0.95] - qt_cal_flat[0.05])), 3),
            "delta_q05": round(deltas[0.05], 3), "delta_q95": round(deltas[0.95], 3)})

        # decision: full arm on uncalibrated vs calibrated quantiles
        qfc = {q: pivot_matrix(tq, f"q{int(q*100):02d}", tdays, fams) for q in LV}
        qfc_cal = {}
        for q in LV:
            tqc = tq.copy()
            tqc[f"q{int(q*100):02d}"] = qt_cal_flat[q]
            qfc_cal[q] = pivot_matrix(tqc, f"q{int(q*100):02d}", tdays, fams)
        base = tpreds[(tpreds.city == city) & (tpreds.scope == "local") &
                      (tpreds.feature_set == "internal") &
                      (tpreds.model == "naive_trailing7")]
        realized = pivot_matrix(base, "target", tdays, fams)

        for regime, units in frozen["cities"][city]["train_only"]["budgets"].items():
            cfg = SimConfig(units=units, kappa=kappa, weights={})
            kap = cfg.kappa_vec(len(fams)); w = np.ones(len(fams))
            levels = sorted(LV)

            def full_arm(qf):
                def alloc(t, carry):
                    dists = [EmpiricalDemand(levels, [qf[q][t, s] + carry[s] for q in levels])
                             for s in range(len(fams))]
                    return greedy_allocate(dists, w, units, kap)
                return alloc

            def prop(t, carry):
                # proportional uses the median arm as its point forecast
                return largest_remainder(np.maximum(qfc[0.50][t], 0.0) + carry, units)

            unc = simulate(realized, full_arm(qfc), cfg, fams)["total_loss"]
            cal = simulate(realized, full_arm(qfc_cal), cfg, fams)["total_loss"]
            prp = simulate(realized, prop, cfg, fams)["total_loss"]
            dec_rows.append({"city": city, "regime": regime, "units": units,
                             "full_uncal_loss": round(unc, 1),
                             "full_conformal_loss": round(cal, 1),
                             "proportional_loss": round(prp, 1),
                             "conformal_vs_uncal_pct": round(100 * (cal - unc) / unc, 3),
                             "conformal_vs_prop_pct": round(100 * (cal - prp) / prp, 3)})

    outm = OUTPUTS / "metrics"
    pd.DataFrame(cal_rows).to_csv(outm / "conformal_calibration.csv", index=False)
    pd.DataFrame(dec_rows).to_csv(outm / "conformal_decision.csv", index=False)
    print("=== CALIBRATION (per city) ===")
    print(pd.DataFrame(cal_rows).to_string(index=False))
    dd = pd.DataFrame(dec_rows)
    print("\n=== DECISION: conformal-calibrated vs uncalibrated full arm ===")
    print(f"  calibrated changes full-arm loss by median {dd.conformal_vs_uncal_pct.median():+.2f}% "
          f"(range {dd.conformal_vs_uncal_pct.min():+.2f}..{dd.conformal_vs_uncal_pct.max():+.2f}%)")
    print(f"  calibrated full arm vs proportional: median {dd.conformal_vs_prop_pct.median():+.2f}% "
          f"(negative = full arm better)")


if __name__ == "__main__":
    run()
