"""Lightweight monitoring: compare the latest model MAE against the naive baseline.

This is a local monitoring stub. It does not connect to any live system. It
compares the current best-model test MAE against the naive seasonal baseline and
records whether the model still clears a configurable improvement threshold.
"""
from __future__ import annotations

from datetime import UTC, datetime

from . import config
from .evaluate import evaluate
from .train import train_and_compare
from .utils import ensure_directories, get_logger, load_json, save_json

LOGGER = get_logger(__name__)

# Minimum relative MAE improvement over the naive baseline to be considered healthy.
_IMPROVEMENT_THRESHOLD_PCT = 5.0


def _load_metrics() -> dict:
    if not config.METRICS_FILE.exists():
        train_and_compare()
    return load_json(config.METRICS_FILE)


def _load_evaluation() -> dict:
    if not config.EVALUATION_REPORT_FILE.exists():
        evaluate()
    return load_json(config.EVALUATION_REPORT_FILE)


def _naive_test_mae(metrics: dict) -> float | None:
    for row in metrics.get("comparison", []):
        if row["model"] == "naive_seasonal":
            return float(row["test_mae"])
    return None


def run_monitoring() -> dict:
    """Compare current model MAE to the naive baseline and write a report."""
    ensure_directories()
    metrics = _load_metrics()
    evaluation = _load_evaluation()

    best_mae = float(evaluation["test_metrics"]["mae"])
    baseline_mae = _naive_test_mae(metrics)

    if baseline_mae and baseline_mae > 0:
        improvement_pct = (baseline_mae - best_mae) / baseline_mae * 100.0
    else:
        improvement_pct = 0.0

    healthy = improvement_pct >= _IMPROVEMENT_THRESHOLD_PCT
    status = "healthy" if healthy else "review_recommended"

    report = {
        "checked_at": datetime.now(UTC).isoformat(),
        "best_model": evaluation.get("best_model"),
        "best_feature_set": evaluation.get("best_feature_set"),
        "best_model_test_mae": round(best_mae, 4),
        "naive_baseline_test_mae": round(baseline_mae, 4) if baseline_mae else None,
        "improvement_over_baseline_pct": round(improvement_pct, 3),
        "improvement_threshold_pct": _IMPROVEMENT_THRESHOLD_PCT,
        "status": status,
        "notes": (
            "Local monitoring stub. Compares best-model test MAE to the naive "
            "seasonal baseline. No live data or production system is involved."
        ),
    }
    save_json(config.MONITORING_REPORT_FILE, report)
    LOGGER.info(
        "Monitoring status: %s (best MAE %.3f vs baseline %.3f, %.2f%% improvement)",
        status,
        best_mae,
        baseline_mae if baseline_mae else float("nan"),
        improvement_pct,
    )
    return report


def main() -> None:
    run_monitoring()


if __name__ == "__main__":
    main()
