"""Evaluate the best model on the held-out test set and render comparison figures."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # Headless rendering for CI and local batch runs.

import joblib
import matplotlib.pyplot as plt
import numpy as np

from . import config, features
from .train import chronological_split, load_processed_dataset, train_and_compare
from .utils import compute_metrics, ensure_directories, get_logger, load_json, save_json

LOGGER = get_logger(__name__)


def _ensure_artifacts() -> dict:
    """Ensure training artifacts exist; train if metrics or model are missing."""
    if not config.METRICS_FILE.exists() or not config.BEST_MODEL_FILE.exists():
        LOGGER.info("Training artifacts missing; running training first.")
        return train_and_compare()
    return load_json(config.METRICS_FILE)


def _evaluate_best_on_test(metrics_payload: dict) -> dict:
    """Compute test metrics and per-segment breakdowns for the best model."""
    frame = load_processed_dataset()
    _, _, test_df = chronological_split(frame)

    bundle = joblib.load(config.BEST_MODEL_FILE)
    pipeline = bundle["pipeline"]
    feature_set = bundle["feature_set"]

    x_test, y_test = features.build_feature_matrix(test_df, feature_set)
    predictions = np.clip(pipeline.predict(x_test), 0.0, None)
    overall = compute_metrics(y_test, predictions)

    test_df = test_df.copy()
    test_df["prediction"] = predictions
    test_df["abs_error"] = np.abs(test_df[config.TARGET_COLUMN] - test_df["prediction"])

    by_borough = (
        test_df.groupby("borough")["abs_error"].mean().round(4).to_dict()
    )
    by_group = (
        test_df.groupby("complaint_group")["abs_error"].mean().round(4).to_dict()
    )

    report = {
        "best_model": bundle["model_name"],
        "best_feature_set": feature_set,
        "test_metrics": overall,
        "mae_by_borough": by_borough,
        "mae_by_complaint_group": by_group,
        "test_rows": int(len(test_df)),
        "internal_vs_augmented": metrics_payload.get("internal_vs_augmented", {}),
    }
    return report, test_df


def _plot_forecast_error_by_model(comparison: list[dict]) -> None:
    """Bar chart of test MAE for every model / feature-set combination."""
    labels = [f"{row['model']}\n[{row['feature_set']}]" for row in comparison]
    values = [row["test_mae"] for row in comparison]

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(range(len(values)), values, color="#34557a")
    ax.set_xticks(range(len(values)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Test MAE (requests)")
    ax.set_title("Forecast error by model and feature set (lower is better)")
    fig.tight_layout()
    fig.savefig(config.FIG_FORECAST_ERROR, dpi=120)
    plt.close(fig)


def _plot_internal_vs_augmented(summary: dict) -> None:
    """Grouped bar chart: internal-historical vs calendar-augmented test MAE."""
    models = list(summary.keys())
    internal = [summary[m]["internal_test_mae"] for m in models]
    augmented = [summary[m]["augmented_test_mae"] for m in models]

    x = np.arange(len(models))
    width = 0.38
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - width / 2, internal, width, label="Internal historical", color="#9aa7b5")
    ax.bar(x + width / 2, augmented, width, label="Calendar augmented", color="#2f7d4f")
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=20, ha="right")
    ax.set_ylabel("Test MAE (requests)")
    ax.set_title("Internal historical vs calendar-augmented forecast error")
    ax.legend()
    fig.tight_layout()
    fig.savefig(config.FIG_INTERNAL_VS_AUGMENTED, dpi=120)
    plt.close(fig)


def _plot_actual_vs_predicted(test_df) -> None:
    """Plot observed vs predicted daily city-wide totals over the test period."""
    daily = (
        test_df.groupby("date")
        .agg(actual=(config.TARGET_COLUMN, "sum"), predicted=("prediction", "sum"))
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(daily["date"], daily["actual"], label="Observed next-day total", color="#34557a")
    ax.plot(
        daily["date"],
        daily["predicted"],
        label="Predicted next-day total",
        color="#c0623a",
        alpha=0.8,
    )
    ax.set_ylabel("City-wide next-day requests")
    ax.set_xlabel("Date (test period)")
    ax.set_title("Observed vs predicted next-day request volume (best model)")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(config.FIG_ACTUAL_VS_PREDICTED, dpi=120)
    plt.close(fig)


def evaluate() -> dict:
    """Run evaluation, write the evaluation report, and render figures."""
    ensure_directories()
    metrics_payload = _ensure_artifacts()
    report, test_df = _evaluate_best_on_test(metrics_payload)
    save_json(config.EVALUATION_REPORT_FILE, report)

    comparison = metrics_payload.get("comparison", [])
    ml_rows = [row for row in comparison if row["feature_set"] in config.FEATURE_SETS]
    if ml_rows:
        _plot_forecast_error_by_model(ml_rows)
    summary = metrics_payload.get("internal_vs_augmented", {})
    if summary:
        _plot_internal_vs_augmented(summary)
    _plot_actual_vs_predicted(test_df)

    LOGGER.info(
        "Evaluation complete. Best model %s [%s] test MAE: %.3f",
        report["best_model"],
        report["best_feature_set"],
        report["test_metrics"]["mae"],
    )
    return report


def main() -> None:
    evaluate()


if __name__ == "__main__":
    main()
