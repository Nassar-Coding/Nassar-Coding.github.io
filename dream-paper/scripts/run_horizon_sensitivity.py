"""Horizon-length sensitivity of the decision-layer policy ranking (review register
#48-#50, #190). Cumulative simulated unresolved-stock loss is non-stationary
under the carryover dynamics, so policy rankings could in principle depend on
the evaluation horizon. We recompute the cumulative loss of the key policies at
the first 30, 60, 90, 180 test days and the full horizon, and report the policy
ranking at each cut. A ranking reversal across horizons would trigger stop
condition #4. Writes outputs/metrics/horizon_sensitivity.csv.
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
from run_decision import POINT_CONFIGS, QLEVELS, pivot_matrix  # noqa: E402
from run_tiebreak_sensitivity import make_point_policy  # noqa: E402

HORIZONS = [30, 60, 90, 180, None]   # None = full
LV = [q / 100 for q in QLEVELS]


def run() -> None:
    set_seed()
    dcfg = load_config("decision.yml")
    kappa = dcfg["kappa_base"]
    active = json.loads((DATA_INTERIM / "active_families.json").read_text())
    preds = pd.read_parquet(DATA_PROCESSED / "test_predictions.parquet")
    fmetrics = pd.read_csv(OUTPUTS / "metrics" / "forecast_metrics.csv")
    frozen = json.loads((OUTPUTS / "metrics" / "frozen_budgets.json").read_text())
    cities = sorted(preds["city"].unique())

    rows = []
    for city in cities:
        fams = active[city]["active_families"]
        cp = preds[preds.city == city]
        days = sorted(cp["day"].unique())
        realized = pivot_matrix(
            cp[(cp.scope == "local") & (cp.feature_set == "internal") &
               (cp.model == "naive_trailing7")], "target", days, fams)
        vmae = fmetrics[(fmetrics.split == "val") & (fmetrics.city == city)]

        def val_mae_of(c3):
            r = vmae[(vmae.scope == c3[0]) & (vmae.feature_set == c3[1]) & (vmae.model == c3[2])]
            return float(r["mae"].iloc[0])
        point_fcs = {}
        for c3 in POINT_CONFIGS:
            sub = cp[(cp.scope == c3[0]) & (cp.feature_set == c3[1]) & (cp.model == c3[2])]
            if not sub.empty:
                point_fcs[c3] = pivot_matrix(sub, "pred", days, fams)
        best = min([c for c in POINT_CONFIGS if c in point_fcs], key=val_mae_of)
        best_fc = point_fcs[best]
        qfc = {q: pivot_matrix(cp[(cp.model == "lgbm_quantile") & (cp.scope == "local")],
                               f"q{int(q*100):02d}", days, fams) for q in LV}

        for regime, units in frozen["cities"][city]["train_only"]["budgets"].items():
            cfg = SimConfig(units=units, kappa=kappa, weights={})
            kap = cfg.kappa_vec(len(fams)); w = np.ones(len(fams)); levels = sorted(LV)
            rng = np.random.default_rng(20260609)

            def daily(pol):
                return simulate(realized, pol, cfg, fams)["daily_loss"]

            policies = {
                "uniform": lambda t, c: largest_remainder(np.ones(len(fams)), units),
                "proportional": lambda t, c: largest_remainder(np.maximum(best_fc[t], 0.0) + c, units),
                "point_greedy_fixed": make_point_policy(best_fc, cfg, fams, kap, "fixed_index", rng),
                "point_greedy_proportional": make_point_policy(best_fc, cfg, fams, kap, "proportional_unmet", rng),
            }

            def full_alloc(t, c):
                dists = [EmpiricalDemand(levels, [qfc[q][t, s] + c[s] for q in levels])
                         for s in range(len(fams))]
                return greedy_allocate(dists, w, units, kap)
            policies["quantile_full"] = full_alloc

            series = {k: daily(p) for k, p in policies.items()}
            T = len(realized)
            for H in HORIZONS:
                h = T if H is None else min(H, T)
                cum = {k: float(np.sum(v[:h])) for k, v in series.items()}
                rank = sorted(cum, key=cum.get)  # ascending loss = best first
                rows.append({"city": city, "regime": regime, "horizon": ("full" if H is None else H),
                             "best_policy": rank[0], "worst_policy": rank[-1],
                             "ranking": ">".join(rank),
                             **{f"loss_{k}": round(cum[k], 1) for k in policies}})

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "metrics" / "horizon_sensitivity.csv", index=False)
    # does the ranking (ignoring uniform floor) change across horizons within a cell?
    reversals = 0
    for (city, regime), g in out.groupby(["city", "regime"]):
        ranks = g.set_index("horizon")["ranking"].to_dict()
        # compare ordering of the 4 forecast policies across horizons
        def core(r): return [p for p in r.split(">") if p != "uniform"]
        base = core(ranks[g["horizon"].iloc[0]])
        if any(core(v) != base for v in ranks.values()):
            reversals += 1
    print(out[["city", "regime", "horizon", "ranking"]].to_string(index=False))
    print(f"\ncity-regime cells with a forecast-policy ranking change across horizons: "
          f"{reversals}/12")


if __name__ == "__main__":
    run()
