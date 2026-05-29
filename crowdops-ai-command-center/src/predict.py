"""Single-record inference for the CrowdOps risk model.

Loads the persisted pipeline and predicts the risk level for one operational
record supplied as a dictionary. Because the saved artifact is a full
scikit-learn ``Pipeline``, preprocessing (scaling + encoding) is applied
automatically -- callers only provide raw field values.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from src import (
    CATEGORICAL_FEATURES,
    MODEL_PATH,
    NUMERIC_FEATURES,
)

# Fields a caller must provide. ``density_ratio`` can be derived automatically
# from crowd_count / zone_capacity if it is not supplied.
INPUT_FIELDS = [
    "zone",
    "crowd_count",
    "zone_capacity",
    "density_ratio",
    "avg_wait_time",
    "entry_rate",
    "exit_rate",
    "temperature",
    "hour",
    "day_of_week",
    "event_type",
]


def _prepare_record(record: dict) -> pd.DataFrame:
    """Validate/normalise an input dict into a one-row DataFrame for the model."""
    record = dict(record)  # shallow copy so we never mutate the caller's dict

    # Derive density_ratio if missing (or zero) and capacity is available.
    if not record.get("density_ratio"):
        capacity = record.get("zone_capacity") or 0
        crowd = record.get("crowd_count") or 0
        record["density_ratio"] = round(crowd / capacity, 3) if capacity else 0.0

    feature_columns = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    missing = [col for col in feature_columns if col not in record]
    if missing:
        raise ValueError(f"Missing required input fields: {missing}")

    return pd.DataFrame([{col: record[col] for col in feature_columns}])


def predict_risk(record: dict, model_path: Path = MODEL_PATH) -> dict:
    """Predict the crowd risk level for a single operational record.

    Args:
        record: Dictionary of input fields (see ``INPUT_FIELDS``).
        model_path: Location of the persisted model pipeline.

    Returns:
        On success::

            {
                "predicted_risk": "High",
                "probabilities": {"Low": 0.05, "Medium": 0.22, "High": 0.73}
            }

        If the model file is missing, a safe fallback dict is returned with an
        ``error`` message instead of raising -- so the dashboard never crashes::

            {"predicted_risk": None, "probabilities": None, "error": "..."}
    """
    if not Path(model_path).exists():
        return {
            "predicted_risk": None,
            "probabilities": None,
            "error": (
                f"Model not found at '{model_path}'. "
                "Train it first with:  python -m src.train"
            ),
        }

    pipeline = joblib.load(model_path)
    frame = _prepare_record(record)

    predicted = str(pipeline.predict(frame)[0])

    probabilities = None
    if hasattr(pipeline, "predict_proba"):
        proba = pipeline.predict_proba(frame)[0]
        classes = list(pipeline.classes_)
        probabilities = {
            str(cls): round(float(p), 4) for cls, p in zip(classes, proba, strict=True)
        }

    return {"predicted_risk": predicted, "probabilities": probabilities}


def main() -> None:
    """Demo entry point: predicts risk for the example record from the brief."""
    example = {
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
    result = predict_risk(example)
    print("[predict] Example input:", example)
    print("[predict] Result:", result)


if __name__ == "__main__":
    main()
