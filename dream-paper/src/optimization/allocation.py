"""Stylized daily capacity-allocation simulation with backlog carryover.

Setting (Phase 7 definition, docs/01_problem_definition.md):
  - planner allocates B integer crews across families each evening;
  - a crew resolves `kappa` requests of its family the next day;
  - workload of family s on day t+1 = observable backlog b[s] + new demand;
  - served = min(workload, kappa * crews); unserved is weighted by the
    family priority weight and (1 - abandonment) of it carries to the
    next day as backlog.

Quantity classification (research constitution):
  observed            : daily demand by family (administrative counts)
  defensibly derived  : backlog dynamics (accounting identity given A4/A5)
  sensitivity-only    : B (capacity regime), kappa, abandonment rate
  assumed             : priority weights (varied in sensitivity analysis)

Policies:
  uniform        : equal crews per family (simple operational heuristic)
  proportional   : crews proportional to point forecast + backlog
                   (largest-remainder rounding; Paper 1's policy, made
                   backlog-aware)
  greedy_ev      : greedy exact maximization of expected weighted served
                   requests under the forecast distribution (point forecast
                   => degenerate distribution; quantile forecast =>
                   piecewise-linear CDF). Greedy is optimal because
                   E[min(D, c)] is concave in capacity c.
  oracle         : greedy_ev with the realized demand (hindsight bound;
                   reported as a bound, never as an achievable policy)
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field

import numpy as np


@dataclass
class SimConfig:
    crews: int
    kappa: float = 50.0
    abandonment: float = 0.0
    priority_weights: dict = field(default_factory=dict)


def largest_remainder(shares: np.ndarray, total: int) -> np.ndarray:
    """Apportion `total` integer crews proportionally to non-negative shares."""
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

    Represented by support points (levels q in QS, values v_q). Expected
    served E[min(D, c)] is computed by sampling the inverse CDF on a fixed
    grid (deterministic, no Monte Carlo noise).
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

    def expected_min(self, c: float) -> float:
        return float(np.minimum(self.samples, c).mean())


def greedy_allocate(dists: list, weights: np.ndarray, crews: int, kappa: float) -> np.ndarray:
    """Exactly maximize sum_s w_s * E[min(D_s, kappa*x_s)] over integer x with sum x = crews.

    Marginal gains of successive crews within a family are non-increasing
    (concavity of E[min(D, c)] in c), so the greedy algorithm is optimal.
    """
    S = len(dists)
    alloc = np.zeros(S, dtype=int)
    cur_val = np.array([w * d.expected_min(0.0) for d, w in zip(dists, weights)])
    heap = []
    for s in range(S):
        nxt = weights[s] * dists[s].expected_min(kappa)
        heapq.heappush(heap, (-(nxt - cur_val[s]), s, nxt))
    for _ in range(crews):
        neg_gain, s, nxt = heapq.heappop(heap)
        alloc[s] += 1
        cur_val[s] = nxt
        nxt2 = weights[s] * dists[s].expected_min(kappa * (alloc[s] + 1))
        heapq.heappush(heap, (-(nxt2 - cur_val[s]), s, nxt2))
    return alloc


def simulate(demand: np.ndarray, allocator, cfg: SimConfig, families: list) -> dict:
    """Run the day-by-day simulation.

    demand    : array [T, S] of realized new demand per day and family
    allocator : callable(day_index, backlog_vector) -> integer crews [S]
    Returns cumulative and per-day metrics.
    """
    T, S = demand.shape
    w = np.array([cfg.priority_weights.get(f, 1.0) for f in families])
    backlog = np.zeros(S)
    daily = []
    for t in range(T):
        crews = allocator(t, backlog.copy())
        assert crews.sum() == cfg.crews, "allocation must use the full budget"
        workload = backlog + demand[t]
        served = np.minimum(workload, cfg.kappa * crews)
        unserved = workload - served
        daily.append({
            "unmet_weighted": float((w * unserved).sum()),
            "unmet_raw": float(unserved.sum()),
            "served": float(served.sum()),
            "backlog_end": float(unserved.sum() * (1 - cfg.abandonment)),
            "unmet_by_family": (w * unserved).tolist(),
        })
        backlog = unserved * (1 - cfg.abandonment)
    out = {
        "total_unmet_weighted": float(sum(d["unmet_weighted"] for d in daily)),
        "total_unmet_raw": float(sum(d["unmet_raw"] for d in daily)),
        "total_served": float(sum(d["served"] for d in daily)),
        "final_backlog": float(daily[-1]["backlog_end"]),
        "unmet_weighted_by_family": np.array([d["unmet_by_family"] for d in daily]).sum(axis=0).tolist(),
        "daily_unmet_weighted": [d["unmet_weighted"] for d in daily],
    }
    return out


def make_policy(kind: str, cfg: SimConfig, families: list,
                point_fc: np.ndarray | None = None,
                quantile_fc: dict | None = None,
                realized: np.ndarray | None = None):
    """Build allocator callables. Forecast arrays are [T, S]; quantile_fc maps level -> [T, S]."""
    S = len(families)
    w = np.array([cfg.priority_weights.get(f, 1.0) for f in families])

    if kind == "uniform":
        def alloc(t, backlog):  # noqa: ARG001
            return largest_remainder(np.ones(S), cfg.crews)
    elif kind == "proportional":
        def alloc(t, backlog):
            return largest_remainder(np.maximum(point_fc[t], 0.0) + backlog, cfg.crews)
    elif kind == "greedy_ev_point":
        def alloc(t, backlog):
            dists = [EmpiricalDemand.degenerate(point_fc[t, s] + backlog[s]) for s in range(S)]
            return greedy_allocate(dists, w, cfg.crews, cfg.kappa)
    elif kind == "greedy_ev_quantile":
        levels = sorted(quantile_fc)
        def alloc(t, backlog):
            dists = [EmpiricalDemand(levels, [quantile_fc[q][t, s] + backlog[s] for q in levels])
                     for s in range(S)]
            return greedy_allocate(dists, w, cfg.crews, cfg.kappa)
    elif kind == "oracle":
        def alloc(t, backlog):
            dists = [EmpiricalDemand.degenerate(realized[t, s] + backlog[s]) for s in range(S)]
            return greedy_allocate(dists, w, cfg.crews, cfg.kappa)
    else:
        raise ValueError(f"unknown policy kind: {kind}")
    return alloc
