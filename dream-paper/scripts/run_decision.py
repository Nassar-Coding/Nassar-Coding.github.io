"""Corrected decision-layer evaluation (redesign C1, C2, C5, C6, C7, C9, C10).

Everything simulated here concerns ABSTRACT request-equivalent capacity
units under HYPOTHETICAL service-pressure regimes; no quantity models any
city's actual staffing, productivity, or queues.

Protocol:
  - Budgets are calibrated from the TRAINING window only and frozen in
    outputs/metrics/frozen_budgets.json BEFORE any validation-stage
    selection; the identical budgets are used for validation selection and
    the single test evaluation (C1, C2). A train+validation calibration is
    produced only as a labeled sensitivity.
  - The uncertainty contrast uses ONE fitted quantile model: its median
    arm, implied-mean arm, and full-distribution arm (C5).
  - Metrics: raw simulated unmet demand, % reduction vs the uniform floor,
    served fractions, final simulated carryover; paired moving-block
    bootstrap CIs on daily loss differentials (C6). No gap-closure
    normalization exists anywhere.
  - Decision-based vs MAE-based validation selection is evaluated as a
    falsifiable question with gains/harms/ties and CIs (C7).
  - Family sets come from the authoritative active-family manifest (C10).
    Austin's `other` (U3): the PRIMARY analysis retains it and reports its
    served fraction and loss share separately; the labeled sensitivity
    excludes it with budgets recomputed train-only over the 7 retained
    families.

Outputs: outputs/metrics/{frozen_budgets.json, decision_metrics.csv,
decision_inference.csv, decision_selection.csv, decision_sensitivity.csv,
run_id.json (updated)}.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from common.runtime import DATA_INTERIM, DATA_PROCESSED, OUTPUTS, load_config, set_seed, write_json  # noqa: E402
from evaluation.protocol import chrono_split  # noqa: E402
from optimization.allocation import (SimConfig, make_policy, simulate,  # noqa: E402
                                     EmpiricalDemand, moving_block_bootstrap_ci)

POINT_CONFIGS = [  # fixed pre-specified grid (register U1); not a selection product
    ("local", "internal", "naive_trailing7"),
    ("local", "internal", "seasonal_naive7"),
    ("local", "internal", "ridge"),
    ("local", "internal", "random_forest"),
    ("local", "internal", "lgbm_point"),
    ("local", "calendar", "random_forest"),
    ("local", "calendar", "lgbm_point"),
    ("local", "calendar_weather", "ridge"),
    ("local", "calendar_weather", "random_forest"),
    ("local", "calendar_weather", "lgbm_point"),
    ("global", "calendar_weather", "lgbm_point"),
]
QLEVELS = (5, 25, 50, 75, 95)


def pivot_matrix(df: pd.DataFrame, value_col: str, days, families) -> np.ndarray:
    p = df.pivot_table(index="day", columns="family", values=value_col, aggfunc="first")
    p = p.reindex(index=days, columns=families)
    if p.isna().any().any():
        raise RuntimeError("prediction matrix has holes; check upstream predictions")
    return p.to_numpy(dtype=float)


def compute_frozen_budgets(panel: pd.DataFrame, feats_days: dict, active: dict,
                           dcfg: dict) -> dict:
    """Budgets from pre-test calibration windows only (C1).

    `feats_days` maps city -> the feature table's day series, whose 70/15/15
    chronological split defines the training and validation boundaries used
    everywhere else in the project.
    """
    kappa = dcfg["kappa_base"]
    regimes = dcfg["capacity"]["regimes"]
    out = {"kappa_base": kappa, "calibration_primary": "train_only",
           "cities": {}}
    for city, days in feats_days.items():
        t_end, v_end = chrono_split(days)
        fams = active[city]["active_families"]
        sub = panel[(panel.city == city) & (panel.family.isin(fams))]
        for tag, end in [("train_only", t_end), ("train_plus_validation", v_end)]:
            window = sub[sub.day <= end]
            mean_daily = float(window.groupby("day")["n"].sum().mean())
            budgets = {r: max(int(round(f * mean_daily / kappa)), len(fams))
                       for r, f in regimes.items()}
            entry = out["cities"].setdefault(city, {})
            entry[tag] = {"mean_daily_demand": round(mean_daily, 2),
                          "boundary_date": str(pd.Timestamp(end).date()),
                          "budgets": budgets}
        # Austin excluded-other recalibration shares the same protocol
        if city == "austin" and dcfg.get("austin_other_sensitivity"):
            fams_x = [f for f in fams if f != "other"]
            sub_x = panel[(panel.city == city) & (panel.family.isin(fams_x))]
            window = sub_x[sub_x.day <= chrono_split(days)[0]]
            mean_daily = float(window.groupby("day")["n"].sum().mean())
            out["cities"][city]["train_only_other_excluded"] = {
                "mean_daily_demand": round(mean_daily, 2),
                "budgets": {r: max(int(round(f * mean_daily / kappa)), len(fams_x))
                            for r, f in regimes.items()}}
    return out


def run() -> None:
    set_seed()
    dcfg = load_config("decision.yml")
    kappa = dcfg["kappa_base"]
    inf = dcfg["inference"]
    active = json.loads((DATA_INTERIM / "active_families.json").read_text())
    panel = pd.read_parquet(DATA_INTERIM / "panel_311.parquet")
    feats = pd.read_parquet(DATA_PROCESSED / "features.parquet")
    preds = pd.read_parquet(DATA_PROCESSED / "test_predictions.parquet")
    vpreds = pd.read_parquet(DATA_PROCESSED / "val_predictions.parquet")
    fmetrics = pd.read_csv(OUTPUTS / "metrics" / "forecast_metrics.csv")
    cities = sorted(preds["city"].unique())

    # ---- C1: freeze budgets from pre-test data BEFORE any selection -------
    feats_days = {c: feats.loc[feats.city == c, "day"] for c in cities}
    frozen = compute_frozen_budgets(panel, feats_days, active, dcfg)
    write_json(OUTPUTS / "metrics" / "frozen_budgets.json", frozen)

    eq_w = {}      # equal weights: empty dict -> weight 1.0 everywhere
    norm_w = dcfg["objective"]["sensitivity_normative_weights"]
    yield_mults = dcfg["service_yield"]["one_family_multipliers"]

    rows, sens_rows, inf_rows, sel_rows = [], [], [], []

    all_blocks = [inf["block_length_days"]] + list(inf.get("block_length_sensitivity", []))

    def bootstrap(diff, block=None):
        return moving_block_bootstrap_ci(diff, block=block or inf["block_length_days"],
                                         n_boot=inf["n_resamples"], seed=inf["seed"])

    for city in cities:
        fams = active[city]["active_families"]
        cp = preds[preds.city == city]
        days = sorted(cp["day"].unique())
        base = cp[(cp.scope == "local") & (cp.feature_set == "internal") &
                  (cp.model == "naive_trailing7")]
        realized = pivot_matrix(base, "target", days, fams)

        qrows_t = cp[(cp.model == "lgbm_quantile") & (cp.scope == "local")]
        qfc = {q / 100: pivot_matrix(qrows_t, f"q{q:02d}", days, fams) for q in QLEVELS}
        q50 = qfc[0.50]
        # implied mean of the piecewise-linear distribution, cellwise
        levels = sorted(qfc)
        T, S = q50.shape
        qmean = np.empty_like(q50)
        for t in range(T):
            for s in range(S):
                qmean[t, s] = EmpiricalDemand(levels, [qfc[q][t, s] for q in levels]).implied_mean()

        point_fcs = {}
        for scope, fset, model in POINT_CONFIGS:
            sub = cp[(cp.scope == scope) & (cp.feature_set == fset) & (cp.model == model)]
            if not sub.empty:
                point_fcs[(scope, fset, model)] = pivot_matrix(sub, "pred", days, fams)

        # validation-MAE-selected config among the fixed grid (C3-consistent)
        vmae = fmetrics[(fmetrics.split == "val") & (fmetrics.city == city)]
        def val_mae_of(cfg3):
            r = vmae[(vmae.scope == cfg3[0]) & (vmae.feature_set == cfg3[1]) &
                     (vmae.model == cfg3[2])]
            return float(r["mae"].iloc[0])
        grid = [c for c in POINT_CONFIGS if c in point_fcs]
        best_by_valmae = min(grid, key=val_mae_of)

        # validation window matrices (for C7 selection sims)
        vc = vpreds[vpreds.city == city]
        vdays = sorted(vc["day"].unique())
        vreal = pivot_matrix(vc[(vc.scope == "local") & (vc.feature_set == "internal") &
                                (vc.model == "naive_trailing7")], "target", vdays, fams)
        vpoint_fcs = {}
        for cfg3 in grid:
            sub = vc[(vc.scope == cfg3[0]) & (vc.feature_set == cfg3[1]) &
                     (vc.model == cfg3[2])]
            if not sub.empty:
                vpoint_fcs[cfg3] = pivot_matrix(sub, "pred", vdays, fams)

        for regime, units in frozen["cities"][city]["train_only"]["budgets"].items():
            cfg = SimConfig(units=units, kappa=kappa, weights=eq_w)
            daily = {}

            def run_one(kind, label, **kw):
                pol = make_policy(kind, cfg, fams, realized=realized, **kw)
                res = simulate(realized, pol, cfg, fams)
                daily[(kind, label)] = res["daily_loss"]
                rows.append({"city": city, "regime": regime, "units": units,
                             "policy": kind, "config": label,
                             "total_loss": res["total_loss"],
                             "final_carryover": res["final_carryover"],
                             "served_fraction_other":
                                 res["served_fraction_by_family"].get("other"),
                             "loss_share_other":
                                 res["loss_share_by_family"].get("other"),
                             "served_fraction_by_family": json.dumps(
                                 res["served_fraction_by_family"])})
                return res["total_loss"]

            uni_loss = run_one("uniform", "uniform")
            run_one("hindsight_myopic_reference", "hindsight_myopic_reference")
            for cfg3 in grid:
                label = "/".join(cfg3)
                run_one("proportional", label, point_fc=point_fcs[cfg3])
                run_one("greedy_ev_point", label, point_fc=point_fcs[cfg3])
            run_one("greedy_ev_point", "quantile/median_arm", point_fc=q50)
            run_one("greedy_ev_point", "quantile/implied_mean_arm", point_fc=qmean)
            run_one("greedy_ev_quantile", "quantile/full_arm", quantile_fc=qfc)

            for r in rows:
                if r["city"] == city and r["regime"] == regime and "pct_reduction_vs_uniform" not in r:
                    r["pct_reduction_vs_uniform"] = round(
                        100 * (1 - r["total_loss"] / uni_loss), 3)

            # ---- pre-named inference contrasts (C6) ------------------------
            best_label = "/".join(best_by_valmae)
            contrasts = [
                ("full_vs_median_arm",
                 daily[("greedy_ev_quantile", "quantile/full_arm")],
                 daily[("greedy_ev_point", "quantile/median_arm")]),
                ("full_vs_implied_mean_arm",
                 daily[("greedy_ev_quantile", "quantile/full_arm")],
                 daily[("greedy_ev_point", "quantile/implied_mean_arm")]),
                ("valbest_vs_naive_greedy",
                 daily[("greedy_ev_point", best_label)],
                 daily[("greedy_ev_point", "local/internal/naive_trailing7")]),
                ("greedy_vs_proportional_valbest",
                 daily[("greedy_ev_point", best_label)],
                 daily[("proportional", best_label)]),
            ]
            for name, a, b in contrasts:
                for blk in all_blocks:
                    mean, lo, hi = bootstrap(a - b, block=blk)
                    inf_rows.append({"city": city, "regime": regime, "contrast": name,
                                     "mean_daily_loss_diff": round(mean, 3),
                                     "ci95_lo": round(lo, 3), "ci95_hi": round(hi, 3),
                                     "n_days": len(a), "block_length": blk,
                                     "is_primary_block":
                                         blk == inf["block_length_days"]})

            # ---- C7: selection experiment under the SAME frozen budgets ----
            v_cfg = SimConfig(units=units, kappa=kappa, weights=eq_w)
            val_dec_loss = {}
            for cfg3, vfc in vpoint_fcs.items():
                pol = make_policy("greedy_ev_point", v_cfg, fams, point_fc=vfc)
                val_dec_loss[cfg3] = simulate(vreal, pol, v_cfg, fams)["total_loss"]
            by_dec = min(val_dec_loss, key=val_dec_loss.get)
            by_mae = best_by_valmae
            a = daily[("greedy_ev_point", "/".join(by_dec))]
            b = daily[("greedy_ev_point", "/".join(by_mae))]
            if by_dec == by_mae:
                verdict, mean, lo, hi = "tie_same_choice", 0.0, 0.0, 0.0
            else:
                mean, lo, hi = bootstrap(a - b)
                verdict = ("gain" if hi < 0 else "harm" if lo > 0 else "tie_ci_overlaps_zero")
            sel_rows.append({"city": city, "regime": regime,
                             "selected_by_val_mae": "/".join(by_mae),
                             "selected_by_val_decision": "/".join(by_dec),
                             "test_loss_mae_choice": float(np.sum(b)),
                             "test_loss_decision_choice": float(np.sum(a)),
                             "mean_daily_diff": round(mean, 3),
                             "ci95_lo": round(lo, 3), "ci95_hi": round(hi, 3),
                             "verdict": verdict})

        # ---- sensitivity scenarios (C9 grid; key policies, all regimes) ----
        def sens_run(scenario, sim_cfg, fams_s, realized_s, point_fc, qfc_s, units, regime):
            for kind, label, kw in [
                ("uniform", "uniform", {}),
                ("proportional", "valbest", {"point_fc": point_fc}),
                ("greedy_ev_point", "valbest", {"point_fc": point_fc}),
                ("greedy_ev_quantile", "quantile/full_arm", {"quantile_fc": qfc_s}),
                ("hindsight_myopic_reference", "hindsight_myopic_reference", {}),
            ]:
                pol = make_policy(kind, sim_cfg, fams_s, realized=realized_s, **kw)
                res = simulate(realized_s, pol, sim_cfg, fams_s)
                sens_rows.append({"scenario": scenario, "city": city,
                                  "regime": regime, "units": units,
                                  "policy": kind, "config": label,
                                  "total_loss": res["total_loss"],
                                  "final_carryover": res["final_carryover"]})

        best_fc = point_fcs[best_by_valmae]
        for regime, units in frozen["cities"][city]["train_only"]["budgets"].items():
            sens_run("normative_weights",
                     SimConfig(units=units, kappa=kappa, weights=norm_w),
                     fams, realized, best_fc, qfc, units, regime)
            for fam in fams:                       # U7: one family at a time
                for mult in yield_mults:
                    kvec = np.array([kappa * (mult if f == fam else 1.0)
                                     for f in fams])
                    sens_run(f"yield_{fam}_x{int(round(mult * 100)):03d}",
                             SimConfig(units=units, kappa=kvec, weights=eq_w),
                             fams, realized, best_fc, qfc, units, regime)
            sens_run("abandonment_10",
                     SimConfig(units=units, kappa=kappa, weights=eq_w,
                               abandonment=dcfg["carryover"]["sensitivity_abandonment"]),
                     fams, realized, best_fc, qfc, units, regime)
        for regime, units in frozen["cities"][city]["train_plus_validation"]["budgets"].items():
            sens_run("budgets_train_plus_validation",
                     SimConfig(units=units, kappa=kappa, weights=eq_w),
                     fams, realized, best_fc, qfc, units, regime)
        if city == "austin" and dcfg.get("austin_other_sensitivity"):
            fx = [f for f in fams if f != "other"]
            ix = [fams.index(f) for f in fx]
            realized_x = realized[:, ix]
            best_fc_x = best_fc[:, ix]
            qfc_x = {q: qfc[q][:, ix] for q in qfc}
            for regime, units in frozen["cities"][city]["train_only_other_excluded"]["budgets"].items():
                sens_run("austin_other_excluded_recalibrated",
                         SimConfig(units=units, kappa=kappa, weights=eq_w),
                         fx, realized_x, best_fc_x, qfc_x, units, regime)

    out = OUTPUTS / "metrics"
    pd.DataFrame(rows).to_csv(out / "decision_metrics.csv", index=False)
    pd.DataFrame(inf_rows).to_csv(out / "decision_inference.csv", index=False)
    pd.DataFrame(sel_rows).to_csv(out / "decision_selection.csv", index=False)
    pd.DataFrame(sens_rows).to_csv(out / "decision_sensitivity.csv", index=False)
    # run-id stamp for the stale-artifact guard (G11)
    rid_path = out / "run_id.json"
    rid = json.loads(rid_path.read_text()) if rid_path.exists() else {}
    rid["decision_run_completed"] = pd.Timestamp.now(tz='UTC').isoformat()
    write_json(rid_path, rid)
    print(f"decision rows: {len(rows)}; inference: {len(inf_rows)}; "
          f"selection: {len(sel_rows)}; sensitivity: {len(sens_rows)}")


if __name__ == "__main__":
    run()
