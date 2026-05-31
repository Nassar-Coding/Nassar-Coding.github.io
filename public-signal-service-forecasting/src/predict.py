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
    "is_weekend": 0,
    "is_holiday": 0,
    "day_of_week": 2,
    "month": 6,
    "quarter": 2,
    "year": 2024,
    "day_of_year": 152,
    "week_of_year": 22,
    "is_month_start": 0,
    "is_month_end": 0,
    "request_lag_1": 100.0,
    "request_lag_7": 100.0,
    "rolling_mean_7": 100.0,
    "rolling_mean_14": 100.0,
    "rolling_std_7": 10.0,
    "rolling_std_14": 10.0,
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


def predict_with_details(record: dict[str, Any]) -> dict[str, Any]:
    """Predict and also return the model name and feature set used."""
    bundle = load_model_bundle()
    prediction = predict_next_day_volume(record)
    return {
        "predicted_next_day_request_volume": prediction,
        "model_used": bundle.get("model_name"),
        "feature_set_used": bundle.get("feature_set"),
    }


def main() -> None:
    example = {
        "borough": "Brooklyn",
        "complaint_group": "Noise",
        "is_weekend": 1,
        "is_holiday": 0,
        "day_of_week": 5,
        "month": 7,
        "quarter": 3,
        "year": 2024,
        "day_of_year": 200,
        "week_of_year": 29,
        "is_month_start": 0,
        "is_month_end": 0,
        "request_lag_1": 120.0,
        "request_lag_7": 110.0,
        "rolling_mean_7": 115.0,
        "rolling_mean_14": 112.0,
        "rolling_std_7": 12.0,
        "rolling_std_14": 13.0,
    }
    details = predict_with_details(example)
    LOGGER.info(
        "Predicted next-day request volume: %.2f (model=%s, feature_set=%s)",
        details["predicted_next_day_request_volume"],
        details["model_used"],
        details["feature_set_used"],
    )


if __name__ == "__main__":
    main()
