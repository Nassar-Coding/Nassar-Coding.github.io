"""Initial-backlog (b0) / warm-up sensitivity for the decision layer
(review register #30/#50). The primary simulation starts at b0=0; this script checks
whether the claim-bearing policy ordering is sensitive to that choice by
re-running the key policies under three initial-carryover conditions:

  zero          : b0 = 0 (primary)
  warmup        : b0 = end-of-validation carryover produced by running the SAME
                  policy over the validation window with validation forecasts
  train_avg     : b0_s = the family's training-window mean daily demand
                  (start the test horizon already holding one day of stock)

For each city, regime, and policy it reports total simulated loss under each
condition and the policy ranking, and flags any change in the claim-bearing
orderings (uniform worst; fixed-index point-greedy below the identified
policies). Writes outputs/metrics/b0_sensitivity.csv. A claim-bearing
ranking reversal triggers stop condition #1.
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
from evaluation.protocol import chrono_split  # noqa: E402
from optimization.allocation import (EmpiricalDemand, SimConfig, simulate,  # noqa: E402
                                     greedy_allocate, largest_remainder)
from run_decision import POINT_CONFIGS, QLEVELS, pivot_matrix  # noqa: E402
from run_tiebreak_sensitivity import make_point_policy  # noqa: E402

LV = [q / 100 for q in QLEVELS]
CLAIM_POLICIES = ["uniform", "proportional", "point_greedy_fixed",
                  "point_greedy_proportional", "quantile_full"]


def build_policies(point_fc, qfc, cfg, fams, kap, rng):
    levels = sorted(qfc)
    w = np.ones(len(fams))

    def full_alloc(t, c):
        dists = [EmpiricalDemand(levels, [qfc[q][t, s] + c[s] for q in levels])
                 for s in range(len(fams))]
        return greedy_allocate(dists, w, cfg.units, kap)
    return {
        "uniform": lambda t, c: largest_remainder(np.ones(len(fams)), cfg.units),
        "proportional": lambda t, c: largest_remainder(np.maximum(point_fc[t], 0.0) + c, cfg.units),
        "point_greedy_fixed": make_point_policy(point_fc, cfg, fams, kap, "fixed_index", rng),
        "point_greedy_proportional": make_point_policy(point_fc, cfg, fams, kap, "proportional_unmet", rng),
        "quantile_full": full_alloc,
    }


def run() -> None:
    set_seed()
    dcfg = load_config("decision.yml")
    kappa = dcfg["kappa_base"]
    active = json.loads((DATA_INTERIM / "active_families.json").read_text())
    panel = pd.read_parquet(DATA_INTERIM / "panel_311.parquet")
    feats = pd.read_parquet(DATA_PROCESSED / "features.parquet")
    preds = pd.read_parquet(DATA_PROCESSED / "test_predictions.parquet")
    vpreds = pd.read_parquet(DATA_PROCESSED / "val_predictions.parquet")
    fmetrics = pd.read_csv(OUTPUTS / "metrics" / "forecast_metrics.csv")
    frozen = json.loads((OUTPUTS / "metrics" / "frozen_budgets.json").read_text())
    cities = sorted(preds["city"].unique())

    rows, reversals = [], 0
    for city in cities:
        fams = active[city]["active_families"]
        cp, vp = preds[preds.city == city], vpreds[vpreds.city == city]
        days, vdays = sorted(cp["day"].unique()), sorted(vp["day"].unique())
        realized = pivot_matrix(cp[(cp.scope == "local") & (cp.feature_set == "internal") &
                                   (cp.model == "naive_trailing7")], "target", days, fams)
        vreal = pivot_matrix(vp[(vp.scope == "local") & (vp.feature_set == "internal") &
                                (vp.model == "naive_trailing7")], "target", vdays, fams)
        vmae = fmetrics[(fmetrics.split == "val") & (fmetrics.city == city)]

        def val_mae_of(c3):
            r = vmae[(vmae.scope == c3[0]) & (vmae.feature_set == c3[1]) & (vmae.model == c3[2])]
            return float(r["mae"].iloc[0])
        pfc, vpfc = {}, {}
        for c3 in POINT_CONFIGS:
            s = cp[(cp.scope == c3[0]) & (cp.feature_set == c3[1]) & (cp.model == c3[2])]
            sv = vp[(vp.scope == c3[0]) & (vp.feature_set == c3[1]) & (vp.model == c3[2])]
            if not s.empty:
                pfc[c3] = pivot_matrix(s, "pred", days, fams)
            if not sv.empty:
                vpfc[c3] = pivot_matrix(sv, "pred", vdays, fams)
        best = min([c for c in POINT_CONFIGS if c in pfc], key=val_mae_of)
        best_fc, vbest_fc = pfc[best], vpfc[best]
        qfc = {q: pivot_matrix(cp[(cp.model == "lgbm_quantile") & (cp.scope == "local")],
                               f"q{int(q*100):02d}", days, fams) for q in LV}
        vqfc = {q: pivot_matrix(vp[(vp.model == "lgbm_quantile") & (vp.scope == "local")],
                                f"q{int(q*100):02d}", vdays, fams) for q in LV}

        # training-window mean daily demand per family (for the train_avg b0)
        t_end, _ = chrono_split(feats.loc[feats.city == city, "day"])
        tr = panel[(panel.city == city) & (panel.family.isin(fams)) & (panel.day <= t_end)]
        train_avg = np.array([tr[tr.family == f].groupby("day")["n"].sum().mean()
                              if not tr[tr.family == f].empty else 0.0 for f in fams])

        for regime, units in frozen["cities"][city]["train_only"]["budgets"].items():
            cfg = SimConfig(units=units, kappa=kappa, weights={})
            kap = cfg.kappa_vec(len(fams))
            test_pol = build_policies(best_fc, qfc, cfg, fams, kap, np.random.default_rng(20260609))
            val_pol = build_policies(vbest_fc, vqfc, cfg, fams, kap, np.random.default_rng(20260609))

            cond_losses = {}
            for cond in ["zero", "warmup", "train_avg"]:
                losses = {}
                for name in CLAIM_POLICIES:
                    if cond == "zero":
                        b0 = None
                    elif cond == "train_avg":
                        b0 = train_avg
                    else:  # warmup: end-of-validation carryover under the same policy
                        b0 = simulate(vreal, val_pol[name], cfg, fams)["final_carryover_vec"]
                    losses[name] = simulate(realized, test_pol[name], cfg, fams, b0=b0)["total_loss"]
                cond_losses[cond] = losses
                rank = sorted(losses, key=losses.get)
                for name in CLAIM_POLICIES:
                    rows.append({"city": city, "regime": regime, "b0_condition": cond,
                                 "policy": name, "total_loss": round(losses[name], 1),
                                 "rank": rank.index(name) + 1})

            # claim-bearing checks: uniform worst; fixed-index point-greedy below
            # the three identified policies, in every condition
            def claim_ok(losses):
                worst = max(losses, key=losses.get)
                fixed = losses["point_greedy_fixed"]
                identified = [losses["proportional"], losses["point_greedy_proportional"],
                              losses["quantile_full"]]
                return worst == "uniform" and all(fixed > x for x in identified)
            if not all(claim_ok(cond_losses[c]) for c in cond_losses):
                reversals += 1
                print(f"  CLAIM CHECK FAILED: {city}/{regime}")

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "metrics" / "b0_sensitivity.csv", index=False)
    print(f"backlog rows: {len(out)}; city-regime cells with a claim-bearing "
          f"ranking change across b0 conditions: {reversals}/12")


if __name__ == "__main__":
    run()
