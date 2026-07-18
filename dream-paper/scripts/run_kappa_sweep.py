"""P4 (final pass v4): global kappa granularity sweep.

Fixed design, preregistered before any result was computed:
  kappa in {1, 5, 10, 25, 50, 100}. For every kappa the city-regime integer
  budgets are recomputed from the EXISTING frozen training-window formula
  B = max(round(f * mean_daily / kappa), |S_c|) with the UNCHANGED stored
  training means in outputs/metrics/frozen_budgets.json (train_only) and the
  regime fractions of configs/decision.yml. Identical forecasts (the same
  validation-MAE-selected point forecaster and the same fitted quantile model
  as the published tables), objective, carryover rules, weights, regimes,
  seeds (20260609; the 20 published random-tie-break seeds), horizons, and
  tie-break definitions. No retuning or reselection.

Policies per city-regime-kappa cell:
  uniform, proportional (direct), point_greedy/fixed_index,
  point_greedy/random_{mean,min,max} (20 seeds), point_greedy/proportional_unmet,
  median_arm/fixed_index, implied_mean_arm/fixed_index, quantile_full, and
  quantile_full_conformal (split-conformal deltas from validation residuals,
  exactly as run_conformal_calibration.py).

The greedy-with-explicit-tie-break implementation here is an incremental-gain
variant of run_tiebreak_sensitivity.greedy_tiebreak (identical mathematics:
per-family gains change only for the family that received the unit, because
family distributions are independent). Equivalence is asserted at startup on
randomized instances against the published implementation, and the kappa=50
cells are cross-checked against the committed tiebreak_sensitivity.csv.

Output: outputs/metrics/kappa_sweep.csv (machine-readable; one row per
city-regime-kappa-policy) and kappa_sweep_summary.csv (per-cell magnitudes:
tie share, mean tied families, fixed-index and full-distribution gaps).
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
from run_tiebreak_sensitivity import greedy_tiebreak, RANDOM_SEEDS, EPS, _break_tie  # noqa: E402
from run_conformal_calibration import conformal_deltas, apply_deltas  # noqa: E402

KAPPAS = [1, 5, 10, 25, 50, 100]
RANK_TOL = 1e-9  # relative tolerance for declaring ranking ties


def fast_greedy_tiebreak(dists, weights, units, kappa, rule, fc, carry, rng,
                         collect_stats=False):
    """Incremental-gain equivalent of run_tiebreak_sensitivity.greedy_tiebreak."""
    S = len(dists)
    alloc = np.zeros(S, dtype=int)
    cur = np.array([w * d.expected_min(0.0) for d, w in zip(dists, weights)])
    gains = np.array([weights[s] * dists[s].expected_min(kappa[s]) - cur[s]
                      for s in range(S)])
    deficit = fc + carry
    n_tied_steps, tied_total = 0, 0
    for _ in range(units):
        gmax = gains.max()
        tied = np.where(gains >= gmax - EPS)[0]
        if len(tied) > 1:
            n_tied_steps += 1
            tied_total += len(tied)
            s = _break_tie(tied, rule, alloc, deficit, carry, fc, kappa, rng)
        else:
            s = int(tied[0])
        cur[s] += gains[s]
        alloc[s] += 1
        gains[s] = weights[s] * dists[s].expected_min(kappa[s] * (alloc[s] + 1)) - cur[s]
    if collect_stats:
        share = n_tied_steps / units if units else 0.0
        mean_tied = (tied_total / n_tied_steps) if n_tied_steps else 1.0
        return alloc, share, mean_tied
    return alloc, None, None


def _equivalence_check():
    rng0 = np.random.default_rng(7)
    for trial in range(30):
        S = int(rng0.integers(2, 8))
        units = int(rng0.integers(1, 40))
        kap = np.full(S, float(rng0.choice([1, 5, 50])))
        fc = rng0.uniform(0, 30, S).round(1)
        carry = rng0.uniform(0, 10, S).round(1)
        dists = [EmpiricalDemand.degenerate(fc[s] + carry[s]) for s in range(S)]
        w = np.ones(S)
        for rule in ("fixed_index", "proportional_unmet", "random"):
            a1, _, _ = greedy_tiebreak([EmpiricalDemand.degenerate(fc[s] + carry[s])
                                        for s in range(S)], w, units, kap, rule,
                                       fc, carry, np.random.default_rng(42))
            a2, _, _ = fast_greedy_tiebreak(dists, w, units, kap, rule, fc, carry,
                                            np.random.default_rng(42))
            assert np.array_equal(a1, a2), (trial, rule, a1, a2)
    print("equivalence check: fast_greedy_tiebreak == published greedy_tiebreak (30 trials x 3 rules)")


def run() -> None:
    set_seed()
    _equivalence_check()
    dcfg = load_config("decision.yml")
    fracs = dcfg["capacity"]["regimes"]
    active = json.loads((DATA_INTERIM / "active_families.json").read_text())
    preds = pd.read_parquet(DATA_PROCESSED / "test_predictions.parquet")
    vpreds = pd.read_parquet(DATA_PROCESSED / "val_predictions.parquet")
    fmetrics = pd.read_csv(OUTPUTS / "metrics" / "forecast_metrics.csv")
    frozen = json.loads((OUTPUTS / "metrics" / "frozen_budgets.json").read_text())
    cities = sorted(preds["city"].unique())
    LV = [q / 100 for q in QLEVELS]

    rows, summary = [], []
    for city in cities:
        fams = active[city]["active_families"]
        S = len(fams)
        cp = preds[preds.city == city]
        days = sorted(cp["day"].unique())
        base = cp[(cp.scope == "local") & (cp.feature_set == "internal") &
                  (cp.model == "naive_trailing7")]
        realized = pivot_matrix(base, "target", days, fams)

        vmae = fmetrics[(fmetrics.split == "val") & (fmetrics.city == city)]

        def val_mae_of(cfg3):
            r = vmae[(vmae.scope == cfg3[0]) & (vmae.feature_set == cfg3[1]) &
                     (vmae.model == cfg3[2])]
            return float(r["mae"].iloc[0])

        avail = []
        for scope, fset, model in POINT_CONFIGS:
            sub = cp[(cp.scope == scope) & (cp.feature_set == fset) & (cp.model == model)]
            if not sub.empty:
                avail.append((scope, fset, model))
        best = min(avail, key=val_mae_of)
        bsub = cp[(cp.scope == best[0]) & (cp.feature_set == best[1]) & (cp.model == best[2])]
        best_fc = pivot_matrix(bsub, "pred", days, fams)

        qrows_t = cp[(cp.model == "lgbm_quantile") & (cp.scope == "local")]
        qfc = {q / 100: pivot_matrix(qrows_t, f"q{q:02d}", days, fams) for q in QLEVELS}
        # conformal deltas from validation residuals (per city, per level),
        # exactly as run_conformal_calibration
        vq = vpreds[(vpreds.city == city) & (vpreds.model == "lgbm_quantile") &
                    (vpreds.scope == "local")]
        yv = vq["target"].to_numpy(dtype=float)
        deltas = conformal_deltas(yv, {q / 100: vq[f"q{q:02d}"].to_numpy(dtype=float)
                                       for q in QLEVELS})
        qfc_cal = apply_deltas(qfc, deltas)

        q50 = qfc[0.50]
        Tn = q50.shape[0]
        qmean = np.empty_like(q50)
        for tt in range(Tn):
            for ss in range(S):
                qmean[tt, ss] = EmpiricalDemand(LV, [qfc[q][tt, ss] for q in LV]).implied_mean()

        mean_daily = frozen["cities"][city]["train_only"]["mean_daily_demand"]

        for kappa in KAPPAS:
            for regime, f in fracs.items():
                units = max(int(round(f * mean_daily / kappa)), S)
                cfg = SimConfig(units=units, kappa=float(kappa), weights={})
                kap = cfg.kappa_vec(S)
                w = np.ones(S)

                def total_loss(alloc_fn):
                    return simulate(realized, alloc_fn, cfg, fams)["total_loss"]

                def uniform_alloc(t, carry):  # noqa: ARG001
                    return largest_remainder(np.ones(S), units)

                def proportional_alloc(t, carry):
                    return largest_remainder(np.maximum(best_fc[t], 0.0) + carry, units)

                stats = {"share": [], "tied": []}

                def point_policy(rule, rng, collect=False):
                    def alloc(t, carry):
                        dists = [EmpiricalDemand.degenerate(best_fc[t, s] + carry[s])
                                 for s in range(S)]
                        a, sh, mt = fast_greedy_tiebreak(
                            dists, w, units, kap, rule, best_fc[t].astype(float),
                            carry.astype(float), rng, collect_stats=collect)
                        if collect and sh is not None:
                            stats["share"].append(sh)
                            stats["tied"].append(mt)
                        return a
                    return alloc

                def arm_policy(fcmat, rule, rng):
                    def alloc(t, carry):
                        dists = [EmpiricalDemand.degenerate(fcmat[t, s] + carry[s])
                                 for s in range(S)]
                        a, _, _ = fast_greedy_tiebreak(
                            dists, w, units, kap, rule, fcmat[t].astype(float),
                            carry.astype(float), rng)
                        return a
                    return alloc

                def full_policy(qsrc):
                    def alloc(t, carry):
                        dists = [EmpiricalDemand(LV, [qsrc[q][t, s] + carry[s] for q in LV])
                                 for s in range(S)]
                        return greedy_allocate(dists, w, units, kap)
                    return alloc

                losses = {}
                losses["uniform"] = total_loss(uniform_alloc)
                losses["proportional"] = total_loss(proportional_alloc)
                losses["point_greedy/fixed_index"] = total_loss(
                    point_policy("fixed_index", np.random.default_rng(20260609), collect=True))
                rnd = [total_loss(point_policy("random", np.random.default_rng(sd)))
                       for sd in RANDOM_SEEDS]
                losses["point_greedy/random_mean"] = float(np.mean(rnd))
                losses["point_greedy/random_min"] = float(np.min(rnd))
                losses["point_greedy/random_max"] = float(np.max(rnd))
                losses["point_greedy/proportional_unmet"] = total_loss(
                    point_policy("proportional_unmet", np.random.default_rng(20260609)))
                losses["median_arm/fixed_index"] = total_loss(
                    arm_policy(q50, "fixed_index", np.random.default_rng(20260609)))
                losses["implied_mean_arm/fixed_index"] = total_loss(
                    arm_policy(qmean, "fixed_index", np.random.default_rng(20260609)))
                losses["quantile_full"] = total_loss(full_policy(qfc))
                losses["quantile_full_conformal"] = total_loss(full_policy(qfc_cal))

                uni, prop = losses["uniform"], losses["proportional"]
                tie_share = float(np.mean(stats["share"])) if stats["share"] else 0.0
                mean_tied = float(np.mean(stats["tied"])) if stats["tied"] else 1.0

                ordered = sorted(losses.items(), key=lambda kv: kv[1])
                ranking = []
                for i, (name, val) in enumerate(ordered):
                    if i and abs(val - ordered[i - 1][1]) <= RANK_TOL * max(abs(val), 1.0):
                        ranking.append(f"={name}")
                    else:
                        ranking.append(name)
                rank_str = " < ".join(ranking)

                for name, val in losses.items():
                    rows.append({
                        "city": city, "regime": regime, "kappa": kappa,
                        "units": units, "policy": name,
                        "total_loss": round(val, 3),
                        "pct_vs_proportional": round(100 * (1 - val / prop), 3),
                        "pct_vs_uniform": round(100 * (1 - val / uni), 3),
                    })
                summary.append({
                    "city": city, "regime": regime, "kappa": kappa, "units": units,
                    "tie_share_steps": round(tie_share, 4),
                    "mean_tied_families": round(mean_tied, 3),
                    "fixed_index_gap_pct": round(
                        100 * (1 - losses["point_greedy/fixed_index"] / prop), 3),
                    "full_dist_gap_pct": round(
                        100 * (1 - losses["quantile_full"] / prop), 3),
                    "full_conformal_gap_pct": round(
                        100 * (1 - losses["quantile_full_conformal"] / prop), 3),
                    "prop_tb_vs_direct_prop_pct": round(
                        100 * (1 - losses["point_greedy/proportional_unmet"] / prop), 3),
                    "uniform_worst": bool(losses["uniform"] >= max(
                        v for k, v in losses.items() if k != "uniform") - RANK_TOL),
                    "fixed_below_identified": bool(
                        losses["point_greedy/fixed_index"] >= max(
                            losses["proportional"],
                            losses["point_greedy/proportional_unmet"],
                            losses["quantile_full"]) - RANK_TOL),
                    "ranking": rank_str,
                })
                print(f"{city} {regime} kappa={kappa} units={units} done", flush=True)

    out = OUTPUTS / "metrics"
    pd.DataFrame(rows).to_csv(out / "kappa_sweep.csv", index=False)
    pd.DataFrame(summary).to_csv(out / "kappa_sweep_summary.csv", index=False)

    # kappa=50 consistency cross-check against the committed audited artifact
    tb = pd.read_csv(out / "tiebreak_sensitivity.csv")
    sw = pd.DataFrame(rows)
    bad = []
    for _, r in sw[(sw.kappa == 50) & (sw.policy.isin(
            ["uniform", "proportional", "point_greedy/fixed_index", "quantile_full"]))].iterrows():
        ref = tb[(tb.city == r.city) & (tb.regime == r.regime) &
                 (tb.policy == r.policy)]
        if not ref.empty and abs(ref["total_loss"].iloc[0] - r.total_loss) > 0.5:
            bad.append((r.city, r.regime, r.policy,
                        float(ref["total_loss"].iloc[0]), r.total_loss))
    if bad:
        print("WARNING kappa=50 mismatch vs committed tiebreak_sensitivity:", bad)
    else:
        print("kappa=50 cells match committed tiebreak_sensitivity.csv")
    print(f"kappa sweep complete: {len(rows)} policy rows, {len(summary)} cells")


if __name__ == "__main__":
    run()
