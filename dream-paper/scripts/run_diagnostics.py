"""W2 diagnostic: trend/stationarity of daily decision-loss differentials.

The decision loss is a waiting-time-weighted unresolved STOCK: a request
unresolved for k days contributes k times to the cumulative loss. Under
the scarce regime (capacity fixed at 70% of training-mean demand) the
simulated queue is supercritical, so daily losses — and potentially the
paired differentials the block bootstrap operates on — can carry a
deterministic trend, which weakens stationarity-based inference.

This script re-derives the daily loss series DETERMINISTICALLY from the
same frozen inputs as E7 (the simulation is Monte-Carlo-free; identity
with E7 is asserted by matching each policy's total loss to
decision_metrics.csv to 1e-6), then reports, per city x regime x
pre-named contrast:

  - OLS slope of the daily differential on the day index;
  - Newey-West (Bartlett, lag 28) t-statistic for the slope;
  - trend-dominance ratio |slope| * (T/2) / |mean differential|
    (the share of the mean attributable to a linear drift);
  - a verdict: 'trending' if |t| > 1.96 and dominance > 0.5,
    else 'stationary-compatible'.

Interpretation rule used by the manuscript: where the differential is
'trending', block-bootstrap CIs are reported as DESCRIPTIVE of a partly
deterministic divergence, not as stationary inference.

Output: outputs/metrics/trend_diagnostics.csv (consumed as tab10).
No experiment is rerun; this is a diagnostic re-derivation over the
frozen protocol's existing configuration and predictions.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from common.runtime import DATA_INTERIM, DATA_PROCESSED, OUTPUTS, load_config, set_seed  # noqa: E402
from optimization.allocation import SimConfig, make_policy, simulate, EmpiricalDemand  # noqa: E402
from run_decision import POINT_CONFIGS, QLEVELS, pivot_matrix  # noqa: E402

CONTRASTS = ["full_vs_median_arm", "full_vs_implied_mean_arm",
             "valbest_vs_naive_greedy", "greedy_vs_proportional_valbest"]


def nw_slope_t(y: np.ndarray, lag: int = 28):
    """OLS slope on time index with Newey-West (Bartlett) standard error."""
    T = len(y)
    t = np.arange(T, dtype=float)
    t_c = t - t.mean()
    beta = float((t_c * (y - y.mean())).sum() / (t_c ** 2).sum())
    resid = (y - y.mean()) - beta * t_c
    x = t_c / (t_c ** 2).sum()          # so that beta = sum(x_i * y_i)
    u = x * resid
    gamma0 = float((u * u).sum())
    var = gamma0
    for ell in range(1, lag + 1):
        w = 1 - ell / (lag + 1)
        var += 2 * w * float((u[ell:] * u[:-ell]).sum())
    se = np.sqrt(max(var, 1e-300))
    return beta, beta / se


def main() -> None:
    set_seed()
    dcfg = load_config("decision.yml")
    kappa = dcfg["kappa_base"]
    active = json.loads((DATA_INTERIM / "active_families.json").read_text())
    frozen = json.loads((OUTPUTS / "metrics" / "frozen_budgets.json").read_text())
    preds = pd.read_parquet(DATA_PROCESSED / "test_predictions.parquet")
    fmetrics = pd.read_csv(OUTPUTS / "metrics" / "forecast_metrics.csv")
    dm = pd.read_csv(OUTPUTS / "metrics" / "decision_metrics.csv")

    rows = []
    for city in sorted(preds["city"].unique()):
        fams = active[city]["active_families"]
        cp = preds[preds.city == city]
        days = sorted(cp["day"].unique())
        base = cp[(cp.scope == "local") & (cp.feature_set == "internal") &
                  (cp.model == "naive_trailing7")]
        realized = pivot_matrix(base, "target", days, fams)
        qrows = cp[(cp.model == "lgbm_quantile") & (cp.scope == "local")]
        qfc = {q / 100: pivot_matrix(qrows, f"q{q:02d}", days, fams) for q in QLEVELS}
        levels = sorted(qfc)
        T, S = qfc[0.5].shape
        qmean = np.empty_like(qfc[0.5])
        for t in range(T):
            for s in range(S):
                qmean[t, s] = EmpiricalDemand(
                    levels, [qfc[q][t, s] for q in levels]).implied_mean()

        val = fmetrics[(fmetrics.split == "val") & (fmetrics.city == city)]
        def vmae(c3):
            r = val[(val.scope == c3[0]) & (val.feature_set == c3[1]) &
                    (val.model == c3[2])]
            return float(r["mae"].iloc[0])
        best = min(POINT_CONFIGS, key=vmae)
        def fc_of(c3):
            sub = cp[(cp.scope == c3[0]) & (cp.feature_set == c3[1]) &
                     (cp.model == c3[2])]
            return pivot_matrix(sub, "pred", days, fams)
        best_fc = fc_of(best)
        naive_fc = fc_of(("local", "internal", "naive_trailing7"))

        for regime, units in frozen["cities"][city]["train_only"]["budgets"].items():
            cfg = SimConfig(units=units, kappa=kappa, weights={})
            daily = {}
            def run_one(kind, label, check_label, **kw):
                pol = make_policy(kind, cfg, fams, realized=realized, **kw)
                res = simulate(realized, pol, cfg, fams)
                ref = dm[(dm.city == city) & (dm.regime == regime) &
                         (dm.policy == kind) & (dm.config == check_label)]
                assert abs(res["total_loss"] - float(ref.total_loss.iloc[0])) < 1e-6, \
                    f"re-derived series diverges from E7 artifact: {city}/{regime}/{check_label}"
                daily[label] = res["daily_loss"]
            run_one("greedy_ev_quantile", "full", "quantile/full_arm", quantile_fc=qfc)
            run_one("greedy_ev_point", "median", "quantile/median_arm", point_fc=qfc[0.5])
            run_one("greedy_ev_point", "imean", "quantile/implied_mean_arm", point_fc=qmean)
            run_one("greedy_ev_point", "best_g", "/".join(best), point_fc=best_fc)
            run_one("greedy_ev_point", "naive_g", "local/internal/naive_trailing7",
                    point_fc=naive_fc)
            run_one("proportional", "best_p", "/".join(best), point_fc=best_fc)

            pairs = {"full_vs_median_arm": daily["full"] - daily["median"],
                     "full_vs_implied_mean_arm": daily["full"] - daily["imean"],
                     "valbest_vs_naive_greedy": daily["best_g"] - daily["naive_g"],
                     "greedy_vs_proportional_valbest": daily["best_g"] - daily["best_p"]}
            for name, diff in pairs.items():
                beta, tstat = nw_slope_t(diff, lag=28)
                mean = float(diff.mean())
                dominance = abs(beta) * (len(diff) / 2) / max(abs(mean), 1e-12)
                verdict = ("trending" if abs(tstat) > 1.96 and dominance > 0.5
                           else "stationary-compatible")
                rows.append({"city": city, "regime": regime, "contrast": name,
                             "n_days": len(diff),
                             "mean_daily_diff": round(mean, 3),
                             "ols_slope_per_day": round(beta, 5),
                             "newey_west_t": round(tstat, 3),
                             "trend_dominance_ratio": round(dominance, 3),
                             "verdict": verdict})
            # level-series context: is the scarce queue itself trending?
            beta_l, t_l = nw_slope_t(daily["best_p"], lag=28)
            rows.append({"city": city, "regime": regime,
                         "contrast": "LEVEL_proportional_valbest",
                         "n_days": len(daily["best_p"]),
                         "mean_daily_diff": round(float(daily["best_p"].mean()), 3),
                         "ols_slope_per_day": round(beta_l, 5),
                         "newey_west_t": round(t_l, 3),
                         "trend_dominance_ratio": np.nan,
                         "verdict": "trending" if abs(t_l) > 1.96 else "stationary-compatible"})

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "metrics" / "trend_diagnostics.csv", index=False)
    print(out[out.contrast != "LEVEL_proportional_valbest"]
          .groupby(["regime", "verdict"]).size().to_string())
    print(f"\n{len(out)} diagnostic rows written")


if __name__ == "__main__":
    main()
