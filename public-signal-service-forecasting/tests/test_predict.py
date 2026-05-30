"""Tests for single-record inference."""
from __future__ import annotations

import joblib
import pytest

from src import config, features, predict
from src.train import make_pipeline


@pytest.fixture
def trained_bundle(small_frame, fast_models):
    """Train a small pipeline and persist a model bundle for inference tests."""
    feature_set = "augmented"
    pipeline = make_pipeline(feature_set, fast_models()["random_forest"])
    x, y = features.build_feature_matrix(small_frame, feature_set)
    pipeline.fit(x, y)
    bundle = {
        "pipeline": pipeline,
        "feature_set": feature_set,
        "feature_columns": config.FEATURE_SETS[feature_set],
        "model_name": "random_forest",
        "target": config.TARGET_COLUMN,
    }
    joblib.dump(bundle, config.BEST_MODEL_FILE)
    return bundle


def test_prediction_returns_non_negative_number(trained_bundle) -> None:
    record = {
        "borough": "Brooklyn",
        "complaint_group": "Noise",
        "temp_c": 22.0,
        "precipitation_mm": 1.0,
        "wind_speed_kmh": 12.0,
        "severe_weather": 0,
        "event_intensity": 0.5,
        "is_weekend": 1,
        "is_holiday": 0,
        "day_of_week": 5,
        "month": 7,
        "request_lag_1": 80.0,
        "request_lag_7": 75.0,
        "rolling_mean_7": 78.0,
        "rolling_mean_14": 76.0,
    }
    prediction = predict.predict_next_day_volume(record)
    assert isinstance(prediction, float)
    assert prediction >= 0.0


def test_prediction_handles_missing_fields(trained_bundle) -> None:
    prediction = predict.predict_next_day_volume({"borough": "Queens"})
    assert isinstance(prediction, float)
    assert prediction >= 0.0
