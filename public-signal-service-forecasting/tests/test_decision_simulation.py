"""Tests for the staffing decision simulation."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src import config, decision_simulation
from src.utils import load_json


def test_allocate_crews_sums_to_budget() -> None:
    forecast = np.array([10.0, 20.0, 30.0, 5.0])
    crews = decision_simulation.allocate_crews(forecast, total_crews=60)
    assert crews.sum() == 60
    assert (crews >= 0).all()


def test_allocate_crews_is_proportional() -> None:
    forecast = np.array([10.0, 90.0])
    crews = decision_simulation.allocate_crews(forecast, total_crews=100, min_crews_per_cell=0)
    # The larger forecast must receive at least as many crews.
    assert crews[1] > crews[0]


def test_allocate_crews_handles_zero_forecast() -> None:
    forecast = np.zeros(4)
    crews = decision_simulation.allocate_crews(forecast, total_crews=20)
    assert crews.sum() == 20


def test_evaluate_policy_returns_required_metrics() -> None:
    day = pd.DataFrame(
        {
            "borough": ["Manhattan"] * 4,
            "complaint_group": ["Water", "Noise", "Traffic", "Public Safety"],
            "forecast": [40.0, 10.0, 30.0, 20.0],
            config.TARGET_COLUMN: [50.0, 8.0, 35.0, 25.0],
        }
    )
    metrics = decision_simulation._evaluate_policy([day], "forecast")
    for field in (
        "total_weighted_unmet_demand",
        "average_service_shortfall",
        "high_demand_coverage_rate",
        "allocation_efficiency",
    ):
        assert field in metrics
        assert isinstance(metrics[field], float)


def test_run_simulation_writes_report(monkeypatch, small_frame, fast_models) -> None:
    def fake_policy_models(train_df, val_df):
        from src import features
        from src.train import make_pipeline

        combined = pd.concat([train_df, val_df], ignore_index=True)
        models = {}
        for feature_set in config.FEATURE_SETS:
            pipeline = make_pipeline(feature_set, fast_models()["random_forest"])
            x, y = features.build_feature_matrix(combined, feature_set)
            pipeline.fit(x, y)
            models[feature_set] = pipeline
        return models

    monkeypatch.setattr(decision_simulation, "load_processed_dataset", lambda: small_frame)
    monkeypatch.setattr(decision_simulation, "_train_policy_models", fake_policy_models)

    report = decision_simulation.run_simulation()
    assert config.DECISION_SIMULATION_REPORT_FILE.exists()
    assert "internal_historical" in report["policies"]
    assert "calendar_augmented" in report["policies"]
    assert "oracle_true_demand" in report["policies"]
    assert "gap_to_oracle_closed_pct" in report["augmented_improvement_over_baseline"]

    saved = load_json(config.DECISION_SIMULATION_REPORT_FILE)
    assert saved["test_days"] > 0
