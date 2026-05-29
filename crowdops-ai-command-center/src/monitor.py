"""Lightweight model-health monitoring for the CrowdOps risk model.

Compares the latest training run's ``f1_macro`` against a stored baseline and
emits a simple health status. This is a local, file-based stand-in for the
kind of drift/performance monitoring a real MLOps platform would automate.

Output:
    reports/monitoring_report.json

Status thresholds:
    - drop > 0.10 from baseline -> "Needs Review"
    - drop > 0.05 from baseline -> "Warning"
    - otherwise                 -> "Healthy"

Run from the project root with:

    python -m src.monitor
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from src import METRICS_PATH, MONITORING_PATH

# Health thresholds (drop in f1_macro relative to baseline).
WARNING_DROP = 0.05
REVIEW_DROP = 0.10


def _classify_status(baseline_f1: float | None, current_f1: float) -> tuple[str, float]:
    """Return (status, drop) given a baseline and current macro F1."""
    if baseline_f1 is None:
        # First ever run -> establish the baseline, report healthy.
        return "Healthy", 0.0

    drop = round(baseline_f1 - current_f1, 4)
    if drop > REVIEW_DROP:
        return "Needs Review", drop
    if drop > WARNING_DROP:
        return "Warning", drop
    return "Healthy", drop


def run_monitoring(
    metrics_path: Path = METRICS_PATH,
    monitoring_path: Path = MONITORING_PATH,
) -> dict:
    """Compare latest metrics to a baseline and write a monitoring report.

    The baseline is persisted inside the monitoring report itself, so the very
    first run establishes the baseline and subsequent runs compare against it.

    Returns:
        The monitoring report dictionary.

    Raises:
        FileNotFoundError: If metrics.json does not exist (train first).
    """
    if not metrics_path.exists():
        raise FileNotFoundError(
            f"Metrics not found at '{metrics_path}'. Train first with:  python -m src.train"
        )

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    current_f1 = float(metrics["best_metrics"]["f1_macro"])

    # Load a previous baseline from any earlier monitoring report, if present.
    baseline_f1: float | None = None
    if monitoring_path.exists():
        try:
            previous = json.loads(monitoring_path.read_text(encoding="utf-8"))
            baseline_f1 = float(previous.get("baseline_f1_macro"))
        except (ValueError, TypeError, json.JSONDecodeError):
            baseline_f1 = None

    status, drop = _classify_status(baseline_f1, current_f1)

    report = {
        "checked_at": datetime.now().isoformat(timespec="seconds"),
        "current_f1_macro": round(current_f1, 4),
        "baseline_f1_macro": round(baseline_f1, 4) if baseline_f1 is not None else round(current_f1, 4),
        "f1_drop_from_baseline": drop,
        "status": status,
        "thresholds": {"warning_drop": WARNING_DROP, "review_drop": REVIEW_DROP},
        "message": _status_message(status, drop),
    }

    monitoring_path.parent.mkdir(parents=True, exist_ok=True)
    monitoring_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"[monitor] Status: {status} | current f1_macro={current_f1:.4f} | drop={drop:.4f}")
    print(f"[monitor] Saved monitoring report -> {monitoring_path}")
    return report


def _status_message(status: str, drop: float) -> str:
    """Human-friendly explanation for the dashboard."""
    if status == "Needs Review":
        return (
            f"Macro F1 dropped {drop:.3f} below baseline (> {REVIEW_DROP}). "
            "Investigate data drift or retrain on fresh data."
        )
    if status == "Warning":
        return (
            f"Macro F1 dropped {drop:.3f} below baseline (> {WARNING_DROP}). "
            "Monitor closely and consider retraining soon."
        )
    return "Model performance is within the healthy range relative to baseline."


def main() -> None:
    """Entry point for `python -m src.monitor`."""
    run_monitoring()


if __name__ == "__main__":
    main()
