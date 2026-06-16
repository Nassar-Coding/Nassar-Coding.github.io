"""Tie-breaking and degeneracy sensitivity for the point-forecast greedy policy.

Professor review B (#9-#16, #188): the headline "point forecasts disable the
expected-value optimizer" must be shown to be a statement about *objective
non-identification under a degenerate forecast*, not an artifact of one
particular tie-break rule. Under a neutral (equal-weights) objective and a
degenerate point forecast, every active family has the SAME marginal value
(kappa) for each unit until its own deficit boundary, so the per-unit choice
among under-served families is a tie that the greedy implementation resolves by
its secondary key. The published `greedy_allocate` resolves ties by ascending
family index (the heap's secondary tuple element).

This script re-runs the point-greedy policy on the SAME validation-MAE-selected
forecaster used by the headlines, under six explicit tie-break rules, plus two
degeneracy-removing controls (a Gaussian/Poisson-smoothed point arm, and the
quantile-interpolated full-distribution arm), and records:
  - total simulated loss per (city, regime, policy);
  - the tie frequency (share of allocation steps with >1 family at the max
    marginal value) and mean number of tied families, which quantifies how
    non-identifying the objective is under the degenerate forecast.

It writes outputs/metrics/tiebreak_sensitivity.csv and tie_frequency.csv. It
does NOT modify the pre-registered decision outputs; `greedy_allocate` itself is
unchanged. Determinism: fixed global seed; random tie-break averaged over seeds.
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
from optimization.allocation import EmpiricalDemand, SimConfig, simulate, largest_remainder  # noqa: E402
from run_decision import POINT_CONFIGS, QLEVELS, pivot_matrix  # noqa: E402

TIEBREAKS = ["fixed_index", "random", "proportional_unmet",
             "largest_carryover", "largest_forecast", "smallest_alloc"]
RANDOM_SEEDS = [20260609 + i for i in range(20)]   # random tie-break is averaged
EPS = 1e-9


def _break_tie(tied, rule, alloc, deficit, carry, fc, kappa, rng):
    """Return the chosen family index among `tied` under the named rule."""
    if rule == "fixed_index":
        return int(tied[0])                       # = published heap behavior
    if rule == "random":
        return int(rng.choice(tied))
    if rule == "proportional_unmet":              # most unmet request-equivalents
        unmet = deficit[tied] - kappa[tied] * alloc[tied]
        return int(tied[np.argmax(unmet)])
    if rule == "largest_carryover":
        return int(tied[np.argmax(carry[tied])])
    if rule == "largest_forecast":
        return int(tied[np.argmax(fc[tied])])
    if rule == "smallest_alloc":
        return int(tied[np.argmin(alloc[tied])])
    raise ValueError(rule)


def greedy_tiebreak(dists, weights, units, kappa, rule, fc, carry, rng):
    """Greedy expected-value allocation with an explicit tie-break rule.

    Equivalent to `allocation.greedy_allocate` for `rule='fixed_index'` (both
    resolve ties toward the smallest family index); other rules change only how
    ties at the maximum marginal value are resolved. Records tie statistics.
    """
    S = len(dists)
    alloc = np.zeros(S, dtype=int)
    cur = np.array([w * d.expected_min(0.0) for d, w in zip(dists, weights)])
    deficit = fc + carry                          # degenerate point value per family
    n_tied_steps, tied_total = 0, 0
    for _ in range(units):
        gains = np.array([weights[s] * dists[s].expected_min(kappa[s] * (alloc[s] + 1)) - cur[s]
                          for s in range(S)])
        gmax = gains.max()
        tied = np.where(gains >= gmax - EPS)[0]
        if len(tied) > 1:
            n_tied_steps += 1
            tied_total += len(tied)
        s = _break_tie(tied, rule, alloc, deficit, carry, fc, kappa, rng) \
            if len(tied) > 1 else int(tied[0])
        cur[s] += gains[s]
        alloc[s] += 1
    tie_share = n_tied_steps / units if units else 0.0
    mean_tied = (tied_total / n_tied_steps) if n_tied_steps else 1.0
    return alloc, tie_share, mean_tied


def smoothed_demand(point_value, scale_kind="poisson"):
    """A non-degenerate EmpiricalDemand around a point forecast.

    Removes the degeneracy WITHOUT new information: spread is a function of the
    point value only (Poisson sd=sqrt(mu); Gaussian sd=0.5*sqrt(mu) floor).
    Used to test whether merely adding residual uncertainty (not the quantile
    model) rescues the point-greedy optimizer (#15).
    """
    from scipy.stats import norm
    mu = max(float(point_value), 0.0)
    sd = np.sqrt(mu) if scale_kind == "poisson" else 0.5 * np.sqrt(mu)
    obj = EmpiricalDemand.__new__(EmpiricalDemand)
    # inverse-CDF of Normal(mu, sd) sampled on the same 99-point grid, clipped at 0
    obj.samples = np.maximum(norm.ppf(EmpiricalDemand.GRID, loc=mu, scale=max(sd, 1e-6)), 0.0)
    return obj


def make_point_policy(point_fc, cfg, fams, kap, rule, rng, smoothed=False):
    S = len(fams)
    w = np.array([cfg.weights.get(f, 1.0) for f in fams])

    def alloc(t, carryover):
        if smoothed:
            dists = [smoothed_demand(point_fc[t, s] + carryover[s]) for s in range(S)]
        else:
            dists = [EmpiricalDemand.degenerate(point_fc[t, s] + carryover[s]) for s in range(S)]
        a, _, _ = greedy_tiebreak(dists, w, cfg.units, kap, rule,
                                  point_fc[t].astype(float), carryover.astype(float), rng)
        return a
    return alloc


def tie_stats_for(point_fc, cfg, fams, kap, realized):
    """Mean tie share / mean tied-count over the test horizon for fixed-index greedy."""
    S = len(fams); w = np.ones(S)
    carry = np.zeros(S); shares, counts = [], []
    rng = np.random.default_rng(0)
    for t in range(realized.shape[0]):
        dists = [EmpiricalDemand.degenerate(point_fc[t, s] + carry[s]) for s in range(S)]
        a, ts, mt = greedy_tiebreak(dists, w, cfg.units, kap, "fixed_index",
                                    point_fc[t].astype(float), carry.astype(float), rng)
        shares.append(ts); counts.append(mt)
        workload = carry + realized[t]
        carry = workload - np.minimum(workload, kap * a)
    return float(np.mean(shares)), float(np.mean(counts))


def run() -> None:
    set_seed()
    dcfg = load_config("decision.yml")
    kappa = dcfg["kappa_base"]
    active = json.loads((DATA_INTERIM / "active_families.json").read_text())
    feats = pd.read_parquet(DATA_PROCESSED / "features.parquet")
    preds = pd.read_parquet(DATA_PROCESSED / "test_predictions.parquet")
    fmetrics = pd.read_csv(OUTPUTS / "metrics" / "forecast_metrics.csv")
    frozen = json.loads((OUTPUTS / "metrics" / "frozen_budgets.json").read_text())
    cities = sorted(preds["city"].unique())

    rows, tie_rows = [], []
    for city in cities:
        fams = active[city]["active_families"]
        cp = preds[preds.city == city]
        days = sorted(cp["day"].unique())
        base = cp[(cp.scope == "local") & (cp.feature_set == "internal") &
                  (cp.model == "naive_trailing7")]
        realized = pivot_matrix(base, "target", days, fams)

        # validation-MAE-selected config among the fixed grid (matches run_decision)
        vmae = fmetrics[(fmetrics.split == "val") & (fmetrics.city == city)]

        def val_mae_of(cfg3):
            r = vmae[(vmae.scope == cfg3[0]) & (vmae.feature_set == cfg3[1]) &
                     (vmae.model == cfg3[2])]
            return float(r["mae"].iloc[0])
        point_fcs = {}
        for scope, fset, model in POINT_CONFIGS:
            sub = cp[(cp.scope == scope) & (cp.feature_set == fset) & (cp.model == model)]
            if not sub.empty:
                point_fcs[(scope, fset, model)] = pivot_matrix(sub, "pred", days, fams)
        grid = [c for c in POINT_CONFIGS if c in point_fcs]
        best = min(grid, key=val_mae_of)
        best_fc = point_fcs[best]

        # quantile full-distribution arm (the fair distribution-aware comparator)
        qrows_t = cp[(cp.model == "lgbm_quantile") & (cp.scope == "local")]
        qfc = {q / 100: pivot_matrix(qrows_t, f"q{q:02d}", days, fams) for q in QLEVELS}
        levels = sorted(qfc)

        for regime, units in frozen["cities"][city]["train_only"]["budgets"].items():
            cfg = SimConfig(units=units, kappa=kappa, weights={})
            kap = cfg.kappa_vec(len(fams))

            # reference policies (forecast-free floor, proportional, full distribution)
            def total_loss(alloc_fn):
                return simulate(realized, alloc_fn, cfg, fams)["total_loss"]

            def uniform_alloc(t, carry):  # noqa: ARG001
                return largest_remainder(np.ones(len(fams)), units)

            def proportional_alloc(t, carry):
                return largest_remainder(np.maximum(best_fc[t], 0.0) + carry, units)

            def full_alloc(t, carry):
                from optimization.allocation import greedy_allocate
                dists = [EmpiricalDemand(levels, [qfc[q][t, s] + carry[s] for q in levels])
                         for s in range(len(fams))]
                return greedy_allocate(dists, np.ones(len(fams)), units, kap)

            uni = total_loss(uniform_alloc)
            prop = total_loss(proportional_alloc)
            full = total_loss(full_alloc)

            def emit(policy, loss):
                rows.append({"city": city, "regime": regime, "units": units,
                             "policy": policy, "total_loss": round(loss, 3),
                             "pct_vs_uniform": round(100 * (1 - loss / uni), 3),
                             "pct_vs_proportional": round(100 * (1 - loss / prop), 3)})

            emit("uniform", uni)
            emit("proportional", prop)
            emit("quantile_full", full)

            # point-greedy under each tie-break rule
            for rule in TIEBREAKS:
                if rule == "random":
                    losses = []
                    for sd in RANDOM_SEEDS:
                        rng = np.random.default_rng(sd)
                        losses.append(total_loss(
                            make_point_policy(best_fc, cfg, fams, kap, rule, rng)))
                    emit("point_greedy/random_mean", float(np.mean(losses)))
                    emit("point_greedy/random_min", float(np.min(losses)))
                    emit("point_greedy/random_max", float(np.max(losses)))
                else:
                    rng = np.random.default_rng(20260609)
                    emit(f"point_greedy/{rule}",
                         total_loss(make_point_policy(best_fc, cfg, fams, kap, rule, rng)))

            # degeneracy-removing control: Gaussian/Poisson-smoothed point arm
            rng = np.random.default_rng(20260609)
            emit("point_greedy_smoothed/fixed_index",
                 total_loss(make_point_policy(best_fc, cfg, fams, kap, "fixed_index",
                                              rng, smoothed=True)))

            # ---- Claim-B probe: are the median/implied-mean arms' losses also a
            # tie-break artifact? Both arms are degenerate point forecasts fed to
            # the SAME greedy policy, so they suffer the same non-identification.
            # Run each under the fixed-index AND the proportional secondary rule,
            # and compare to the quantile-interpolated full-distribution arm.
            q50 = qfc[0.50]
            Tn, Sn = q50.shape
            qmean = np.empty_like(q50)
            for tt in range(Tn):
                for ss in range(Sn):
                    qmean[tt, ss] = EmpiricalDemand(
                        levels, [qfc[q][tt, ss] for q in levels]).implied_mean()
            for armname, armfc in [("median_arm", q50), ("implied_mean_arm", qmean)]:
                for rule in ["fixed_index", "proportional_unmet"]:
                    rng = np.random.default_rng(20260609)
                    emit(f"{armname}/{rule}",
                         total_loss(make_point_policy(armfc, cfg, fams, kap, rule, rng)))

            ts, mt = tie_stats_for(best_fc, cfg, fams, kap, realized)
            tie_rows.append({"city": city, "regime": regime, "units": units,
                             "n_families": len(fams),
                             "tie_share_steps": round(ts, 4),
                             "mean_tied_families": round(mt, 3)})

    outm = OUTPUTS / "metrics"
    pd.DataFrame(rows).to_csv(outm / "tiebreak_sensitivity.csv", index=False)
    pd.DataFrame(tie_rows).to_csv(outm / "tie_frequency.csv", index=False)
    print(f"tiebreak rows: {len(rows)}; tie-frequency cells: {len(tie_rows)}")


if __name__ == "__main__":
    run()
