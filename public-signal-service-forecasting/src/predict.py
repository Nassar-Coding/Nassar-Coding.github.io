"""Single-record inference using the persisted best model."""
from __future__ import annotations

from typing import Any

import joblib
import numpy as np
import pandas as pd

from . import config
from .train import train_and_compare
from .utils import get_logger

LOGGER = get_logger(__name__)

# Default feature values used when a caller omits an optional field.
_DEFAULTS: dict[str, Any] = {
    "borough": "Manhattan",
    "complaint_group": "Noise",
    "temp_c": 12.0,
    "precipitation_mm": 0.0,
    "wind_speed_kmh": 14.0,
    "severe_weather": 0,
    "event_intensity": 0.25,
    "is_weekend": 0,
    "is_holiday": 0,
    "day_of_week": 2,
    "month": 6,
    "request_lag_1": 50.0,
    "request_lag_7": 50.0,
    "rolling_mean_7": 50.0,
    "rolling_mean_14": 50.0,
}


def load_model_bundle() -> dict[str, Any]:
    """Load the persisted model bundle, training first if it is missing."""
    if not config.BEST_MODEL_FILE.exists():
        LOGGER.info("Best model artifact missing; training before prediction.")
        train_and_compare()
    return joblib.load(config.BEST_MODEL_FILE)


def predict_next_day_volume(record: dict[str, Any]) -> float:
    """Predict next-day request volume for a single feature record.

    Missing fields fall back to neutral defaults. Only the columns required by
    the persisted model's feature set are used. The output is clipped to be
    non-negative because request volumes cannot be negative.
    """
    bundle = load_model_bundle()
    pipeline = bundle["pipeline"]
    feature_columns: list[str] = bundle["feature_columns"]

    merged = {**_DEFAULTS, **record}
    row = {column: merged.get(column, _DEFAULTS.get(column)) for column in feature_columns}
    frame = pd.DataFrame([row], columns=feature_columns)

    prediction = float(np.clip(pipeline.predict(frame)[0], 0.0, None))
    return prediction


def main() -> None:
    example = {
        "borough": "Brooklyn",
        "complaint_group": "Noise",
        "temp_c": 24.0,
        "precipitation_mm": 0.0,
        "wind_speed_kmh": 10.0,
        "severe_weather": 0,
        "event_intensity": 0.6,
        "is_weekend": 1,
        "is_holiday": 0,
        "day_of_week": 5,
        "month": 7,
        "request_lag_1": 95.0,
        "request_lag_7": 88.0,
        "rolling_mean_7": 90.0,
        "rolling_mean_14": 87.0,
    }
    prediction = predict_next_day_volume(example)
    LOGGER.info("Predicted next-day request volume: %.2f", prediction)


if __name__ == "__main__":
    main()
