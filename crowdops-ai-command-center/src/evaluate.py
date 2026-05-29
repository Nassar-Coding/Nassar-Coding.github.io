"""Model evaluation for the CrowdOps risk model.

Produces a detailed, machine-readable evaluation of the saved model on a
held-out test split:

    - per-class precision/recall/F1 (classification report)
    - confusion matrix data (no external plotting service required)

Output:
    reports/evaluation.json

Run from the project root with:

    python -m src.evaluate
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
from sklearn.metrics import classification_report, confusion_matrix

from src import (
    DATA_PATH,
    EVALUATION_PATH,
    MODEL_PATH,
    RISK_LEVELS,
)
from src.data import load_data
from src.features import make_train_test_split


def evaluate_model(
    model_path: Path = MODEL_PATH,
    data_path: Path = DATA_PATH,
) -> dict:
    """Evaluate the saved model and write reports/evaluation.json.

    Returns:
        The evaluation payload dictionary.

    Raises:
        FileNotFoundError: If the model artifact does not exist yet.
    """
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found at '{model_path}'. Train it first with:  python -m src.train"
        )

    pipeline = joblib.load(model_path)
    frame = load_data(data_path)

    # Re-create the same split used in training (same seed) so we evaluate on
    # data the model did not see during fitting.
    _, x_test, _, y_test = make_train_test_split(frame)
    predictions = pipeline.predict(x_test)

    # Order labels consistently as Low/Medium/High for readable matrices.
    labels = [lvl for lvl in RISK_LEVELS if lvl in set(y_test) | set(predictions)]

    report = classification_report(
        y_test,
        predictions,
        labels=labels,
        zero_division=0,
        output_dict=True,
    )
    matrix = confusion_matrix(y_test, predictions, labels=labels).tolist()

    payload = {
        "labels": labels,
        "classification_report": report,
        "confusion_matrix": {
            "labels": labels,
            "matrix": matrix,
            "description": "Rows = actual risk level, Columns = predicted risk level.",
        },
        "test_size": int(len(y_test)),
    }

    EVALUATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVALUATION_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[evaluate] Saved evaluation -> {EVALUATION_PATH}")
    return payload


def main() -> None:
    """Entry point for `python -m src.evaluate`."""
    evaluate_model()


if __name__ == "__main__":
    main()
