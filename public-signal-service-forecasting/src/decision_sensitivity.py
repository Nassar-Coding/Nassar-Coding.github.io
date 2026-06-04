"""Decision-simulation sensitivity across crew-budget settings.

Re-runs the stylized staffing-allocation simulation under scarce, moderate, and
generous crew budgets. For each setting it compares the internal-historical
policy, the calendar-augmented policy, and the oracle policy, and records unmet
demand, weighted unmet demand, allocation efficiency, high-demand coverage,
percent reduction versus the internal policy, and the oracle gap closed.

Outputs:
- reports/decision_sensitivity_report.csv
- reports/decision_sensitivity_summary.json
- figures/decision_sensitivity.png
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import config, features
from .decision_simulation import _evaluate_policy, _train_policy_models
from .train import chronological_split, load_processed_dataset
from .utils import ensure_directories, get_logger, save_json

LOGGER = get_logger(__name__)


def _prepare_test_forecasts() -> tuple[list[pd.DataFrame], list[str]]:
    """Train policy forecasters and attach per-policy forecasts to test days."""
    frame = load_processed_dataset()
    train_df, val_df, test_df = chronological_split(frame)
    models = _train_policy_models(train_df, val_df)
    test_df = test_df.copy()
    feature_sets = list(models)
    for feature_set, pipeline in models.items():
        x_test, _ = features.build_feature_matrix(test_df, feature_set)
        test_df[f"forecast_{feature_set}"] = np.clip(pipeline.predict(x_test), 0.0, None)
    test_df["forecast_oracle"] = test_df[config.TARGET_COLUMN]
    return [group for _, group in test_df.groupby("date")], feature_sets


def run_decision_sensitivity() -> dict:
    """Run the crew-budget sensitivity sweep and persist artifacts."""
    ensure_directories()
    daily_groups, feature_sets = _prepare_test_forecasts()
    requests_per_crew = config.REQUESTS_PER_CREW

    rows: list[dict] = []
    summary: dict = {
        "requests_per_crew": requests_per_crew,
        "test_days": len(daily_groups),
        "settings": {},
    }

    # One policy per available forecast feature set, plus oracle. The headline
    # augmented policy is calendar+weather when available, else calendar.
    policy_columns = {
        f"policy_{fs}": f"forecast_{fs}" for fs in feature_sets
    }
    policy_columns["oracle_true_demand"] = "forecast_oracle"
    baseline_policy = "policy_internal_historical"
    headline_policy = (
        "policy_calendar_weather_augmented"
        if "calendar_weather_augmented" in feature_sets
        else "policy_calendar_augmented"
    )

    for setting_name, total_crews in config.DECISION_CREW_SETTINGS.items():
        results = {
            policy: _evaluate_policy(
                daily_groups, column, total_crews=total_crews, requests_per_crew=requests_per_crew
            )
            for policy, column in policy_columns.items()
        }
        baseline_w = results[baseline_policy]["total_weighted_unmet_demand"]
        augmented_w = results[headline_policy]["total_weighted_unmet_demand"]
        oracle_w = results["oracle_true_demand"]["total_weighted_unmet_demand"]
        reduction_pct = (baseline_w - augmented_w) / baseline_w * 100.0 if baseline_w else 0.0
        headroom = baseline_w - oracle_w
        gap_closed_pct = (baseline_w - augmented_w) / headroom * 100.0 if headroom else 0.0

        for policy, metrics in results.items():
            rows.append(
                {
                    "setting": setting_name,
                    "total_crews": total_crews,
                    "daily_capacity": total_crews * requests_per_crew,
                    "policy": policy,
                    **metrics,
                }
            )

        summary["settings"][setting_name] = {
            "total_crews": total_crews,
            "daily_capacity": total_crews * requests_per_crew,
            "headline_augmented_policy": headline_policy,
            "baseline_weighted_unmet": baseline_w,
            "augmented_weighted_unmet": augmented_w,
            "oracle_weighted_unmet": oracle_w,
            "weighted_unmet_reduction_pct": round(reduction_pct, 4),
            "gap_to_oracle_closed_pct": round(gap_closed_pct, 4),
            "augmented_better": bool(augmented_w < baseline_w),
        }
        LOGGER.info(
            "Setting %s (crews=%s): reduction=%.3f%%, gap closed=%.2f%%",
            setting_name,
            total_crews,
            reduction_pct,
            gap_closed_pct,
        )

    report = pd.DataFrame(rows)
    report.to_csv(config.DECISION_SENSITIVITY_REPORT_FILE, index=False)

    reductions = [s["weighted_unmet_reduction_pct"] for s in summary["settings"].values()]
    summary["augmented_better_in_all_settings"] = bool(all(r > 0 for r in reductions))
    summary["mean_weighted_unmet_reduction_pct"] = round(float(np.mean(reductions)), 4)
    save_json(config.DECISION_SENSITIVITY_SUMMARY_FILE, summary)
    _plot(summary)

    LOGGER.info("Decision sensitivity complete across %s settings.", len(config.DECISION_CREW_SETTINGS))
    return summary


def _plot(summary: dict) -> None:
    """Bar chart of weighted unmet demand by policy across crew settings."""
    settings = list(summary["settings"].keys())
    baseline = [summary["settings"][s]["baseline_weighted_unmet"] for s in settings]
    augmented = [summary["settings"][s]["augmented_weighted_unmet"] for s in settings]
    oracle = [summary["settings"][s]["oracle_weighted_unmet"] for s in settings]

    x = np.arange(len(settings))
    width = 0.27
    headline = summary["settings"][settings[0]].get("headline_augmented_policy", "")
    aug_label = "Calendar + weather" if "calendar_weather" in headline else "Calendar"
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - width, baseline, width, label="Baseline (internal)", color="#9aa7b5")
    ax.bar(x, augmented, width, label=aug_label, color="#2f7d4f")
    ax.bar(x + width, oracle, width, label="Oracle (observed demand)", color="#b5942f")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{s}\n({summary['settings'][s]['total_crews']} crews)" for s in settings])
    ax.set_ylabel("Total weighted unmet demand (lower is better)")
    ax.set_title("Decision quality by crew budget and forecast policy")
    ax.legend()
    fig.tight_layout()
    fig.savefig(config.FIG_DECISION_SENSITIVITY, dpi=120)
    plt.close(fig)


def main() -> None:
    run_decision_sensitivity()


if __name__ == "__main__":
    main()
