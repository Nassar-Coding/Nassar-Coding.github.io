"""Experiment 2 — forecast-to-decision evaluation with backlog and capacity regimes.

For every city and capacity regime (scarce/moderate/generous = capacity
covering 70% / 90% / 110% of mean daily test-window demand), simulate the
daily allocation under each policy:

  uniform                         no forecast (operational heuristic floor)
  proportional + each point model largest-remainder on forecast+backlog
  greedy_ev_point + each model    expected-value greedy, degenerate dist
  greedy_ev_quantile              expected-value greedy on lgbm_quantile dist
  oracle                          hindsight bound (never an achievable policy)

Also runs (Phase 8) decision-based model selection: the model chosen by
validation decision loss vs the model chosen by validation MAE, both then
evaluated on the test window; and sensitivity sweeps over priority weights
and abandonment.

Outputs: outputs/metrics/decision_metrics.csv
         outputs/metrics/decision_selection.csv
         outputs/metrics/decision_sensitivity.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from common.runtime import DATA_PROCESSED, OUTPUTS, load_config, set_seed  # noqa: E402
from optimization.allocation import SimConfig, make_policy, simulate  # noqa: E402

KAPPA = 50.0
REGIMES = {"scarce": 0.7, "moderate": 0.9, "generous": 1.1}
POINT_CONFIGS = [  # (scope, feature_set, model) point-forecast configs to evaluate
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


def pivot_matrix(df: pd.DataFrame, value_col: str, days, families) -> np.ndarray:
    p = df.pivot_table(index="day", columns="family", values=value_col, aggfunc="first")
    p = p.reindex(index=days, columns=families)
    if p.isna().any().any():
        raise RuntimeError("prediction matrix has holes; check upstream predictions")
    return p.to_numpy(dtype=float)


def run() -> None:
    set_seed()
    fam_cfg = load_config("service_families.yml")
    weights = {f["name"]: f["priority_weight"] for f in fam_cfg["families"]}

    preds = pd.read_parquet(DATA_PROCESSED / "test_predictions.parquet")
    vpreds = pd.read_parquet(DATA_PROCESSED / "val_predictions.parquet")
    cities = sorted(preds["city"].unique())

    rows, sel_rows, sens_rows = [], [], []
    for city in cities:
        cp = preds[preds.city == city]
        days = sorted(cp["day"].unique())
        families = sorted(cp["family"].unique())
        base = cp[(cp.scope == "local") & (cp.feature_set == "internal") &
                  (cp.model == "naive_trailing7")]
        realized = pivot_matrix(base, "target", days, families)
        mean_daily_total = realized.sum(axis=1).mean()

        qrows_city = cp[(cp.model == "lgbm_quantile") & (cp.scope == "local")]
        quantile_fc = {q / 100: pivot_matrix(qrows_city, f"q{q:02d}", days, families)
                       for q in (5, 25, 50, 75, 95)}

        for regime, frac in REGIMES.items():
            crews = max(int(round(frac * mean_daily_total / KAPPA)), len(families))
            cfg = SimConfig(crews=crews, kappa=KAPPA, priority_weights=weights)

            def run_policy(kind, label, point_fc=None, qfc=None):
                pol = make_policy(kind, cfg, families, point_fc=point_fc,
                                  quantile_fc=qfc, realized=realized)
                res = simulate(realized, pol, cfg, families)
                rows.append({"city": city, "regime": regime, "crews": crews,
                             "policy": kind, "config": label,
                             "total_unmet_weighted": res["total_unmet_weighted"],
                             "total_unmet_raw": res["total_unmet_raw"],
                             "final_backlog": res["final_backlog"],
                             "unmet_by_family": res["unmet_weighted_by_family"]})
                return res["total_unmet_weighted"]

            run_policy("uniform", "uniform")
            run_policy("oracle", "oracle")
            run_policy("greedy_ev_quantile", "local/calendar_weather/lgbm_quantile",
                       qfc=quantile_fc)
            for scope, fset, model in POINT_CONFIGS:
                sub = cp[(cp.scope == scope) & (cp.feature_set == fset) & (cp.model == model)]
                if sub.empty:
                    continue
                fc = pivot_matrix(sub, "pred", days, families)
                label = f"{scope}/{fset}/{model}"
                run_policy("proportional", label, point_fc=fc)
                run_policy("greedy_ev_point", label, point_fc=fc)

            # ---- decision-based vs accuracy-based model selection (Phase 8)
            vcity = vpreds[vpreds.city == city]
            vdays = sorted(vcity["day"].unique())
            vreal = pivot_matrix(vcity[(vcity.scope == "local") &
                                       (vcity.feature_set == "internal") &
                                       (vcity.model == "naive_trailing7")],
                                 "target", vdays, sorted(vcity["family"].unique()))
            v_mean = vreal.sum(axis=1).mean()
            v_crews = max(int(round(frac * v_mean / KAPPA)), len(families))
            v_cfg = SimConfig(crews=v_crews, kappa=KAPPA, priority_weights=weights)
            val_scores = {}
            for scope, fset, model in POINT_CONFIGS:
                sub = vcity[(vcity.scope == scope) & (vcity.feature_set == fset) &
                            (vcity.model == model)]
                if sub.empty:
                    continue
                vfc = pivot_matrix(sub, "pred", vdays, families)
                pol = make_policy("greedy_ev_point", v_cfg, families, point_fc=vfc)
                dec_loss = simulate(vreal, pol, v_cfg, families)["total_unmet_weighted"]
                mae_val = float((sub["target"] - sub["pred"]).abs().mean())
                val_scores[(scope, fset, model)] = (mae_val, dec_loss)
            by_mae = min(val_scores, key=lambda k: val_scores[k][0])
            by_dec = min(val_scores, key=lambda k: val_scores[k][1])
            sel_rows.append({"city": city, "regime": regime,
                             "selected_by_mae": "/".join(by_mae),
                             "selected_by_decision": "/".join(by_dec),
                             "agree": by_mae == by_dec})

        # ---- sensitivity: priority weights equalized; abandonment 10% -----
        crews = max(int(round(0.9 * mean_daily_total / KAPPA)), len(families))
        best_fc = pivot_matrix(cp[(cp.scope == "local") &
                                  (cp.feature_set == "calendar_weather") &
                                  (cp.model == "lgbm_point")], "pred", days, families)
        for tag, w_override, aband in [("equal_weights", {f: 1.0 for f in families}, 0.0),
                                       ("abandonment_10", weights, 0.10)]:
            cfg = SimConfig(crews=crews, kappa=KAPPA, abandonment=aband,
                            priority_weights=w_override)
            for kind, label, kw in [
                ("uniform", "uniform", {}),
                ("proportional", "lgbm_point", {"point_fc": best_fc}),
                ("greedy_ev_point", "lgbm_point", {"point_fc": best_fc}),
                ("greedy_ev_quantile", "lgbm_quantile", {"qfc": quantile_fc}),
                ("oracle", "oracle", {}),
            ]:
                pol = make_policy(kind, cfg, families,
                                  point_fc=kw.get("point_fc"),
                                  quantile_fc=kw.get("qfc"), realized=realized)
                res = simulate(realized, pol, cfg, families)
                sens_rows.append({"city": city, "sensitivity": tag, "policy": kind,
                                  "config": label,
                                  "total_unmet_weighted": res["total_unmet_weighted"]})

    out = OUTPUTS / "metrics"; out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out / "decision_metrics.csv", index=False)
    pd.DataFrame(sel_rows).to_csv(out / "decision_selection.csv", index=False)
    pd.DataFrame(sens_rows).to_csv(out / "decision_sensitivity.csv", index=False)
    print(f"decision rows: {len(rows)}; selection rows: {len(sel_rows)}; sensitivity: {len(sens_rows)}")


if __name__ == "__main__":
    run()
