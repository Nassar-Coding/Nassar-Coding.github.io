"""Model training and selection for the CrowdOps risk model.

Trains two candidate models (Logistic Regression and Random Forest) inside a
preprocessing + estimator ``Pipeline``, compares them on macro-averaged
metrics, selects the best by ``f1_macro``, and persists:

    - models/crowd_risk_model.joblib   (the fitted winning pipeline)
    - reports/metrics.json             (machine-readable comparison)
    - reports/model_summary.md         (human-readable summary)

Run from the project root with:

    python -m src.train
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.pipeline import Pipeline

from src import (
    DATA_PATH,
    METRICS_PATH,
    MODEL_PATH,
    MODEL_SUMMARY_PATH,
    RANDOM_SEED,
)
from src.data import load_data
from src.features import build_preprocessor, make_train_test_split


def _candidate_models() -> dict[str, Pipeline]:
    """Build the candidate model pipelines (preprocessor + estimator)."""
    return {
        "LogisticRegression": Pipeline(
            steps=[
                ("preprocess", build_preprocessor()),
                (
                    "model",
                    LogisticRegression(max_iter=1000, random_state=RANDOM_SEED),
                ),
            ]
        ),
        "RandomForest": Pipeline(
            steps=[
                ("preprocess", build_preprocessor()),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=200,
                        max_depth=None,
                        random_state=RANDOM_SEED,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
    }


def _score_model(pipeline: Pipeline, x_test, y_test) -> dict[str, float]:
    """Compute the four headline classification metrics on the test set."""
    predictions = pipeline.predict(x_test)
    return {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "precision_macro": round(
            float(precision_score(y_test, predictions, average="macro", zero_division=0)),
            4,
        ),
        "recall_macro": round(
            float(recall_score(y_test, predictions, average="macro", zero_division=0)),
            4,
        ),
        "f1_macro": round(
            float(f1_score(y_test, predictions, average="macro", zero_division=0)),
            4,
        ),
    }


def train_models(data_path: Path = DATA_PATH) -> dict:
    """Train, compare, select, and persist the best CrowdOps risk model.

    If the dataset does not yet exist it is generated automatically so the
    command works on a fresh checkout.

    Returns:
        A dictionary describing the run (best model name + all metrics).
    """
    # Auto-generate data on a fresh checkout so `python -m src.train` just works.
    if not data_path.exists():
        from src.generate_data import save_dataset

        print("[train] Dataset not found -- generating it now...")
        save_dataset(path=data_path)

    frame = load_data(data_path)
    x_train, x_test, y_train, y_test = make_train_test_split(frame)

    results: dict[str, dict[str, float]] = {}
    fitted: dict[str, Pipeline] = {}

    for name, pipeline in _candidate_models().items():
        print(f"[train] Fitting {name} ...")
        pipeline.fit(x_train, y_train)
        results[name] = _score_model(pipeline, x_test, y_test)
        fitted[name] = pipeline
        print(f"[train]   {name} f1_macro = {results[name]['f1_macro']:.4f}")

    # Select the winner by macro F1 (balances all three risk classes).
    best_name = max(results, key=lambda n: results[n]["f1_macro"])
    best_pipeline = fitted[best_name]

    _persist_outputs(best_name, best_pipeline, results, len(frame), len(x_train), len(x_test))

    print(f"[train] Best model: {best_name} (f1_macro={results[best_name]['f1_macro']:.4f})")
    print(f"[train] Saved model -> {MODEL_PATH}")
    print(f"[train] Saved metrics -> {METRICS_PATH}")
    print(f"[train] Saved summary -> {MODEL_SUMMARY_PATH}")

    return {
        "best_model": best_name,
        "metrics": results,
        "best_metrics": results[best_name],
    }


def _persist_outputs(
    best_name: str,
    best_pipeline: Pipeline,
    results: dict[str, dict[str, float]],
    n_total: int,
    n_train: int,
    n_test: int,
) -> None:
    """Write the model artifact, metrics JSON, and Markdown summary to disk."""
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(best_pipeline, MODEL_PATH)

    metrics_payload = {
        "trained_at": datetime.now().isoformat(timespec="seconds"),
        "best_model": best_name,
        "best_metrics": results[best_name],
        "all_models": results,
        "dataset": {
            "total_rows": n_total,
            "train_rows": n_train,
            "test_rows": n_test,
        },
    }
    METRICS_PATH.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")

    _write_model_summary(best_name, results, n_total, n_train, n_test)


def _write_model_summary(
    best_name: str,
    results: dict[str, dict[str, float]],
    n_total: int,
    n_train: int,
    n_test: int,
) -> None:
    """Render a human-readable Markdown summary of the training run."""
    best = results[best_name]
    lines = [
        "# CrowdOps Risk Model -- Training Summary",
        "",
        f"_Generated: {datetime.now().isoformat(timespec='seconds')}_",
        "",
        "## Selected Model",
        "",
        f"- **Winning model:** `{best_name}` (selected by macro F1).",
        f"- **Accuracy:** {best['accuracy']:.4f}",
        f"- **Precision (macro):** {best['precision_macro']:.4f}",
        f"- **Recall (macro):** {best['recall_macro']:.4f}",
        f"- **F1 (macro):** {best['f1_macro']:.4f}",
        "",
        "## Dataset",
        "",
        f"- Total rows: {n_total:,}",
        f"- Training rows: {n_train:,}",
        f"- Test rows: {n_test:,}",
        "",
        "## Model Comparison",
        "",
        "| Model | Accuracy | Precision (macro) | Recall (macro) | F1 (macro) |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name, m in results.items():
        marker = " **(selected)**" if name == best_name else ""
        lines.append(
            f"| {name}{marker} | {m['accuracy']:.4f} | {m['precision_macro']:.4f} "
            f"| {m['recall_macro']:.4f} | {m['f1_macro']:.4f} |"
        )

    lines += [
        "",
        "## Notes",
        "",
        "- The target (`risk_level`) is derived from synthetic, local-only data.",
        "- Controlled noise is added during data generation so accuracy is",
        "  realistic rather than perfect.",
        "- The persisted artifact is a full scikit-learn `Pipeline`, so the same",
        "  preprocessing is applied automatically at inference time.",
        "",
    ]
    MODEL_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODEL_SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Entry point for `python -m src.train`."""
    train_models()


if __name__ == "__main__":
    main()
