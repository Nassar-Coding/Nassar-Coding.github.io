"""Tests for single-record prediction and the missing-model fallback."""

from __future__ import annotations

from src import RISK_LEVELS
from src.generate_data import save_dataset
from src.predict import predict_risk
from src.train import train_models

EXAMPLE_RECORD = {
    "zone": "Gate A",
    "crowd_count": 750,
    "zone_capacity": 1000,
    "density_ratio": 0.75,
    "avg_wait_time": 14,
    "entry_rate": 120,
    "exit_rate": 80,
    "temperature": 36,
    "hour": 18,
    "day_of_week": 4,
    "event_type": "Special Event",
}


def _train_temp_model(tmp_path, monkeypatch):
    """Train a model into a temp dir and return its path."""
    import src.train as train_module

    data_path = tmp_path / "crowd_ops.csv"
    model_path = tmp_path / "crowd_risk_model.joblib"
    monkeypatch.setattr(train_module, "MODEL_PATH", model_path)
    monkeypatch.setattr(train_module, "METRICS_PATH", tmp_path / "metrics.json")
    monkeypatch.setattr(train_module, "MODEL_SUMMARY_PATH", tmp_path / "summary.md")

    save_dataset(path=data_path, n_rows=2000, seed=31)
    train_models(data_path=data_path)
    return model_path


def test_predict_returns_valid_risk_level(tmp_path, monkeypatch) -> None:
    model_path = _train_temp_model(tmp_path, monkeypatch)
    result = predict_risk(EXAMPLE_RECORD, model_path=model_path)

    assert result["predicted_risk"] in RISK_LEVELS
    assert result.get("error") is None


def test_predict_returns_probabilities_that_sum_to_one(tmp_path, monkeypatch) -> None:
    model_path = _train_temp_model(tmp_path, monkeypatch)
    result = predict_risk(EXAMPLE_RECORD, model_path=model_path)

    probabilities = result["probabilities"]
    assert probabilities is not None
    assert set(probabilities).issubset(set(RISK_LEVELS))
    assert abs(sum(probabilities.values()) - 1.0) < 1e-6


def test_predict_derives_density_ratio_when_missing(tmp_path, monkeypatch) -> None:
    model_path = _train_temp_model(tmp_path, monkeypatch)
    record = dict(EXAMPLE_RECORD)
    record.pop("density_ratio")  # force auto-derivation
    result = predict_risk(record, model_path=model_path)
    assert result["predicted_risk"] in RISK_LEVELS


def test_predict_missing_model_returns_safe_fallback(tmp_path) -> None:
    missing_model = tmp_path / "does_not_exist.joblib"
    result = predict_risk(EXAMPLE_RECORD, model_path=missing_model)
    assert result["predicted_risk"] is None
    assert result["probabilities"] is None
    assert "error" in result and result["error"]
