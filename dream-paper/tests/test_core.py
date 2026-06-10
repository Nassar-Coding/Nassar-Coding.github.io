"""Unit tests for harmonization, leakage controls, allocation, and the simulator."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from common.runtime import us_federal_holidays  # noqa: E402
from features.build_features import add_internal_features, calendar_frame  # noqa: E402
from preprocessing.build_panel import compile_rules, map_category, densify  # noqa: E402
from optimization.allocation import (EmpiricalDemand, SimConfig, greedy_allocate,  # noqa: E402
                                     largest_remainder, make_policy, simulate)
from evaluation.protocol import chrono_split, split_masks, rolling_origin_folds  # noqa: E402


FAM_CFG = {"families": [
    {"name": "noise", "priority_weight": 1.0, "patterns": ["noise"]},
    {"name": "water_sewer", "priority_weight": 3.0, "patterns": ["water", "sewer"]},
    {"name": "other", "priority_weight": 1.0, "patterns": []},
]}


class TestHarmonization:
    def test_first_match_wins_and_is_deterministic(self):
        rules = compile_rules(FAM_CFG)
        assert map_category("Noise - Residential", rules) == "noise"
        assert map_category("Water System", rules) == "water_sewer"
        assert map_category("NOISE about water", rules) == "noise"  # order matters
        assert map_category("Pothole", rules) == "other"
        assert map_category(None, rules) == "other"

    def test_densify_inserts_explicit_zeros(self):
        panel = pd.DataFrame({
            "city": ["x", "x"],
            "day": pd.to_datetime(["2024-01-01", "2024-01-03"]),
            "family": ["noise", "noise"],
            "n": [5, 7],
        })
        out = densify(panel)
        assert len(out) == 3
        mid = out[(out.day == "2024-01-02")]
        assert mid["n"].iloc[0] == 0


class TestLeakage:
    def make_series(self, n=60):
        days = pd.date_range("2024-01-01", periods=n, freq="D")
        return pd.DataFrame({"city": "x", "family": "noise", "day": days,
                             "n": np.arange(n, dtype=float)})

    def test_lag_and_rolling_use_only_past(self):
        g = add_internal_features(self.make_series())
        row = g.iloc[40]
        t = row["n"]
        assert row["lag_1"] == t                       # lag_1 = n[t]
        assert row["lag_7"] == t - 6                   # n[t-6]
        assert row["target"] == t + 1                  # y = n[t+1]
        # rolling mean of last 7 obs ending at t: mean(t-6..t)
        assert row["roll_mean_7"] == pytest.approx(t - 3)
        # nothing derived from the target day except the target itself
        assert row["roll_mean_7"] < row["target"]

    def test_calendar_features_describe_target_day(self):
        days = pd.Series(pd.to_datetime(["2024-07-03"]))  # target day = July 4
        cal = calendar_frame(days)
        assert cal["cal_is_holiday"].iloc[0] == 1

    def test_split_is_chronological_and_disjoint(self):
        days = pd.Series(pd.date_range("2020-01-01", periods=1000, freq="D"))
        t_end, v_end = chrono_split(days)
        tr, va, te = split_masks(days, t_end, v_end)
        assert (days[tr].max() < days[va].min()) and (days[va].max() < days[te].min())
        assert int(tr.sum() + va.sum() + te.sum()) == 1000

    def test_rolling_folds_never_train_on_future(self):
        days = pd.Series(pd.date_range("2020-01-01", periods=700, freq="D"))
        for tr, ev in rolling_origin_folds(days):
            assert days[tr].max() < days[ev].min()


class TestHolidays:
    def test_known_holidays(self):
        h = us_federal_holidays(2024)
        import datetime as dt
        assert dt.date(2024, 7, 4) in h
        assert dt.date(2024, 11, 28) in h          # Thanksgiving 2024
        assert dt.date(2024, 6, 19) in h           # Juneteenth
        assert dt.date(2020, 6, 19) not in us_federal_holidays(2020)


class TestAllocation:
    def test_largest_remainder_exact_budget(self):
        x = largest_remainder(np.array([1.0, 1.0, 1.0]), 10)
        assert x.sum() == 10 and x.min() >= 3

    def test_greedy_matches_bruteforce_on_small_instance(self):
        rng = np.random.default_rng(0)
        dists = [EmpiricalDemand([0.05, 0.5, 0.95], sorted(rng.uniform(0, 100, 3)))
                 for _ in range(3)]
        w = np.array([1.0, 2.0, 3.0])
        units, kappa = 6, np.full(3, 10.0)
        best = greedy_allocate(dists, w, units, kappa)
        best_val = sum(w[s] * dists[s].expected_min(kappa[s] * best[s]) for s in range(3))
        # brute force all integer allocations
        vals = []
        for a in range(units + 1):
            for b in range(units + 1 - a):
                c = units - a - b
                vals.append(sum(w[s] * d.expected_min(kappa[s] * x)
                                for s, (d, x) in enumerate(zip(dists, (a, b, c)))))
        assert best_val == pytest.approx(max(vals), rel=1e-9)

    def test_simulator_conserves_workload(self):
        demand = np.array([[10.0, 30.0], [20.0, 0.0], [0.0, 50.0]])
        cfg = SimConfig(units=2, kappa=10.0, weights={"a": 1.0, "b": 1.0})
        pol = make_policy("uniform", cfg, ["a", "b"])
        res = simulate(demand, pol, cfg, ["a", "b"])
        # with zero abandonment, served + final carryover must equal total demand
        assert res["total_served"] + res["final_carryover"] == pytest.approx(demand.sum())
        assert res["total_served"] <= demand.sum()
        assert res["final_carryover"] >= demand.sum() - cfg.units * 10.0 * len(demand) - 1e-9

    def test_hindsight_reference_beats_uniform_here_but_is_not_a_bound(self):
        rng = np.random.default_rng(1)
        demand = rng.poisson(40, size=(30, 4)).astype(float)
        fams = list("abcd")
        cfg = SimConfig(units=3, kappa=30.0, weights={f: 1.0 for f in fams})
        uni = simulate(demand, make_policy("uniform", cfg, fams), cfg, fams)
        ref = simulate(demand, make_policy("hindsight_myopic_reference", cfg,
                                           fams, realized=demand), cfg, fams)
        # weak dominance holds on this instance; the reference remains
        # myopic and is NOT asserted to be a horizon-optimal bound (C6)
        assert ref["total_loss"] <= uni["total_loss"] + 1e-9

    def test_quantile_policy_uses_full_budget(self):
        fams = list("ab")
        cfg = SimConfig(units=5, kappa=10.0, weights={f: 1.0 for f in fams})
        qfc = {q: np.full((3, 2), v) for q, v in
               zip([0.05, 0.5, 0.95], [10.0, 30.0, 90.0])}
        pol = make_policy("greedy_ev_quantile", cfg, fams, quantile_fc=qfc)
        units = pol(0, np.zeros(2))
        assert units.sum() == 5
