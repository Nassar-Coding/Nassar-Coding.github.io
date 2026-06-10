"""Simulated daily capacity allocation over abstract request-equivalent units.

Everything here is an explicit simulation (redesign C8): "units" are
abstract capacity units, each resolving `kappa` request-equivalents per
day (optionally family-specific under the heterogeneous-yield sensitivity);
"carryover" is simulated unresolved request-equivalent carryover, not any
observed municipal queue. No quantity models actual staffing, crews,
shifts, productivity, or dispatch.

Quantity classification (research constitution):
  observed            : daily reported demand by active family
  defensibly derived  : carryover accounting identity given the stated yield
  sensitivity-only    : budgets (hypothetical service-pressure regimes),
                        kappa, abandonment, objective weights, yield vector

Policies:
  uniform        : equal units per active family (forecast-free floor)
  proportional   : largest-remainder apportionment of forecast + carryover
  greedy_ev      : exact maximization of expected weighted served
                   request-equivalents under the forecast distribution
                   (degenerate for point forecasts; piecewise-linear from
                   quantiles). Greedy is optimal because E[min(D, c)] is
                   concave in capacity c.
  hindsight_myopic_reference :
                   greedy_ev with realized demand. Per-day myopic; NOT a
                   horizon-optimal bound under carryover and may be
                   exceeded (redesign C6). Reported only as a labeled,
                   non-bounding reference; never used as a denominator.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field

import numpy as np


@dataclass
class SimConfig:
    units: int                                  # abstract capacity units per day
    kappa: object = 50.0                        # scalar or per-family vector
    abandonment: float = 0.0
    weights: dict = field(default_factory=dict)  # objective weights per family

    def kappa_vec(self, n_families: int) -> np.ndarray:
        k = np.asarray(self.kappa, dtype=float)
        return np.full(n_families, float(k)) if k.ndim == 0 else k


def largest_remainder(shares: np.ndarray, total: int) -> np.ndarray:
    """Apportion `total` integer units proportionally to non-negative shares."""
    shares = np.maximum(np.asarray(shares, dtype=float), 0.0)
    if shares.sum() <= 0:
        shares = np.ones_like(shares)
    quota = shares / shares.sum() * total
    base = np.floor(quota).astype(int)
    rem = total - base.sum()
    if rem > 0:
        order = np.argsort(-(quota - base))
        base[order[:rem]] += 1
    return base


class EmpiricalDemand:
    """Piecewise-linear demand distribution from quantile forecasts.

    Expected served E[min(D, c)] is evaluated exactly for the discrete
    distribution defined by linear interpolation of the inverse CDF through
    the forecast quantiles on a fixed grid (deterministic, no Monte Carlo).
    """

    GRID = np.linspace(0.01, 0.99, 99)

    def __init__(self, quantile_levels, quantile_values):
        qs = np.asarray(quantile_levels, dtype=float)
        vs = np.maximum(np.asarray(quantile_values, dtype=float), 0.0)
        order = np.argsort(qs)
        self.samples = np.interp(self.GRID, qs[order], vs[order])

    @classmethod
    def degenerate(cls, value: float):
        obj = cls.__new__(cls)
        obj.samples = np.full(99, max(float(value), 0.0))
        return obj

    def implied_mean(self) -> float:
        return float(self.samples.mean())

    def expected_min(self, c: float) -> float:
        return float(np.minimum(self.samples, c).mean())


def greedy_allocate(dists: list, weights: np.ndarray, units: int,
                    kappa: np.ndarray) -> np.ndarray:
    """Exactly maximize sum_s w_s E[min(D_s, kappa_s x_s)] s.t. sum x = units.

    Marginal gains within a family are non-increasing (concavity), so the
    greedy algorithm is optimal.
    """
    S = len(dists)
    alloc = np.zeros(S, dtype=int)
    cur_val = np.array([w * d.expected_min(0.0) for d, w in zip(dists, weights)])
    heap = []
    for s in range(S):
        nxt = weights[s] * dists[s].expected_min(kappa[s])
        heapq.heappush(heap, (-(nxt - cur_val[s]), s, nxt))
    for _ in range(units):
        neg_gain, s, nxt = heapq.heappop(heap)
        alloc[s] += 1
        cur_val[s] = nxt
        nxt2 = weights[s] * dists[s].expected_min(kappa[s] * (alloc[s] + 1))
        heapq.heappush(heap, (-(nxt2 - cur_val[s]), s, nxt2))
    return alloc


def simulate(demand: np.ndarray, allocator, cfg: SimConfig, families: list) -> dict:
    """Day-by-day simulation over the active family set.

    demand    : [T, S] realized reported demand per day and active family
    allocator : callable(day_index, carryover_vector) -> integer units [S]
    """
    T, S = demand.shape
    w = np.array([cfg.weights.get(f, 1.0) for f in families])
    kap = cfg.kappa_vec(S)
    carryover = np.zeros(S)
    daily_loss, served_by_family, demand_by_family = [], np.zeros(S), np.zeros(S)
    loss_by_family = np.zeros(S)
    for t in range(T):
        alloc = allocator(t, carryover.copy())
        assert alloc.sum() == cfg.units, "allocation must use the full budget"
        workload = carryover + demand[t]
        served = np.minimum(workload, kap * alloc)
        unserved = workload - served
        daily_loss.append(float((w * unserved).sum()))
        loss_by_family += w * unserved
        served_by_family += served
        demand_by_family += demand[t]
        carryover = unserved * (1 - cfg.abandonment)
    with np.errstate(invalid="ignore", divide="ignore"):
        served_frac = np.where(demand_by_family > 0,
                               np.minimum(served_by_family / demand_by_family, 1.0),
                               1.0)
    return {
        "total_loss": float(np.sum(daily_loss)),
        "total_served": float(served_by_family.sum()),
        "daily_loss": np.asarray(daily_loss),
        "final_carryover": float(carryover.sum()),
        "served_fraction_by_family": {f: round(float(v), 4)
                                      for f, v in zip(families, served_frac)},
        "loss_share_by_family": {f: (round(float(v / loss_by_family.sum()), 4)
                                     if loss_by_family.sum() > 0 else 0.0)
                                 for f, v in zip(families, loss_by_family)},
    }


def make_policy(kind: str, cfg: SimConfig, families: list,
                point_fc: np.ndarray | None = None,
                quantile_fc: dict | None = None,
                realized: np.ndarray | None = None):
    """Build allocator callables. Forecast arrays are [T, S]; quantile_fc maps level -> [T, S]."""
    S = len(families)
    w = np.array([cfg.weights.get(f, 1.0) for f in families])
    kap = cfg.kappa_vec(S)

    if kind == "uniform":
        def alloc(t, carryover):  # noqa: ARG001
            return largest_remainder(np.ones(S), cfg.units)
    elif kind == "proportional":
        def alloc(t, carryover):
            return largest_remainder(np.maximum(point_fc[t], 0.0) + carryover, cfg.units)
    elif kind == "greedy_ev_point":
        def alloc(t, carryover):
            dists = [EmpiricalDemand.degenerate(point_fc[t, s] + carryover[s])
                     for s in range(S)]
            return greedy_allocate(dists, w, cfg.units, kap)
    elif kind == "greedy_ev_quantile":
        levels = sorted(quantile_fc)
        def alloc(t, carryover):
            dists = [EmpiricalDemand(levels, [quantile_fc[q][t, s] + carryover[s]
                                              for q in levels])
                     for s in range(S)]
            return greedy_allocate(dists, w, cfg.units, kap)
    elif kind == "hindsight_myopic_reference":
        def alloc(t, carryover):
            dists = [EmpiricalDemand.degenerate(realized[t, s] + carryover[s])
                     for s in range(S)]
            return greedy_allocate(dists, w, cfg.units, kap)
    else:
        raise ValueError(f"unknown policy kind: {kind}")
    return alloc


def moving_block_bootstrap_ci(diff: np.ndarray, block: int = 28,
                              n_boot: int = 2000, seed: int = 20260609):
    """Percentile CI for the mean of a dependent daily series via circular
    moving-block bootstrap. Returns (mean, lo95, hi95)."""
    diff = np.asarray(diff, dtype=float)
    T = len(diff)
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(T / block))
    means = np.empty(n_boot)
    for b in range(n_boot):
        starts = rng.integers(0, T, n_blocks)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel() % T
        means[b] = diff[idx[:T]].mean()
    return float(diff.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))
