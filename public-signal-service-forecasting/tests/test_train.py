"""Tests for training, model comparison, and artifact creation."""
from __future__ import annotations

from src import config, train
from src.utils import load_json


def test_training_creates_artifacts(monkeypatch, small_frame, fast_models) -> None:
    monkeypatch.setattr(train, "load_processed_dataset", lambda: small_frame)
    monkeypatch.setattr(train, "_build_models", fast_models)

    payload = train.train_and_compare()

    assert config.METRICS_FILE.exists()
    assert config.BEST_MODEL_FILE.exists()
    assert config.MODEL_COMPARISON_FILE.exists()
    assert payload["primary_metric"] == "mae"
    assert payload["best_feature_set"] in config.FEATURE_SETS


def test_both_feature_sets_are_evaluated(monkeypatch, small_frame, fast_models) -> None:
    monkeypatch.setattr(train, "load_processed_dataset", lambda: small_frame)
    monkeypatch.setattr(train, "_build_models", fast_models)
    train.train_and_compare()

    metrics = load_json(config.METRICS_FILE)
    feature_sets = {row["feature_set"] for row in metrics["comparison"]}
    assert "internal_only" in feature_sets
    assert "augmented" in feature_sets
    assert "naive_seasonal" in feature_sets


def test_comparison_rows_have_metric_fields(monkeypatch, small_frame, fast_models) -> None:
    monkeypatch.setattr(train, "load_processed_dataset", lambda: small_frame)
    monkeypatch.setattr(train, "_build_models", fast_models)
    train.train_and_compare()

    metrics = load_json(config.METRICS_FILE)
    for row in metrics["comparison"]:
        for field in ("val_mae", "val_rmse", "val_mape", "val_r2", "test_mae"):
            assert field in row
            assert isinstance(row[field], (int, float))


def test_internal_vs_augmented_summary_present(monkeypatch, small_frame, fast_models) -> None:
    monkeypatch.setattr(train, "load_processed_dataset", lambda: small_frame)
    monkeypatch.setattr(train, "_build_models", fast_models)
    payload = train.train_and_compare()

    summary = payload["internal_vs_augmented"]
    assert summary
    for model_summary in summary.values():
        assert "internal_test_mae" in model_summary
        assert "augmented_test_mae" in model_summary
        assert "augmented_better" in model_summary
