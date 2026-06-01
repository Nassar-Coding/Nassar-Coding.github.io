"""Stylized staffing-allocation simulation linking forecasts to decision quality.

Each day a fixed crew budget is allocated across borough x complaint_group cells
in proportion to forecasted next-day demand. The simulation compares a baseline
policy (internal-historical forecast), a calendar-augmented policy, and an
oracle policy (true next-day demand, benchmark only).

This is a transparent, stylized simulation. It does not represent real agency
dispatch, real crew logistics, or any real operational system, and it is not a
claim of real staffing optimization.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import config, features
from .train import chronological_split, load_processed_dataset, make_pipeline
from .utils import ensure_directories, get_logger, save_json

LOGGER = get_logger(__name__)


def _train_policy_models(
    train_df: pd.DataFrame, val_df: pd.DataFrame
) -> dict[str, object]:
    """Train one forecasting pipeline per feature set for the decision policies."""
    from sklearn.ensemble import RandomForestRegressor

    combined = pd.concat([train_df, val_df], ignore_index=True)
    models: dict[str, object] = {}
    for feature_set in config.available_feature_sets(list(combined.columns)):
        estimator = RandomForestRegressor(
            n_estimators=200,
            max_depth=14,
            min_samples_leaf=2,
            n_jobs=-1,
            random_state=config.RANDOM_SEED,
        )
        pipeline = make_pipeline(feature_set, estimator)
        x, y = features.build_feature_matrix(combined, feature_set)
        pipeline.fit(x, y)
        models[feature_set] = pipeline
    return models


def allocate_crews(
    forecast: np.ndarray,
    total_crews: int = config.TOTAL_CREWS,
    min_crews_per_cell: int = config.MIN_CREWS_PER_CELL,
) -> np.ndarray:
    """Allocate an integer crew budget proportional to forecasted demand.

    Uses a largest-remainder method so the allocation sums exactly to the crew
    budget. An optional minimum per cell guarantees baseline coverage.
    """
    forecast = np.clip(np.asarray(forecast, dtype=float), 0.0, None)
    n_cells = len(forecast)
    if n_cells == 0:
        return np.zeros(0, dtype=int)

    crews = np.full(n_cells, min_crews_per_cell, dtype=int)
    remaining = total_crews - crews.sum()
    if remaining <= 0:
        return crews

    total_forecast = forecast.sum()
    if total_forecast <= 0:
        # No signal: distribute remaining crews as evenly as possible.
        base, extra = divmod(remaining, n_cells)
        crews += base
        crews[:extra] += 1
        return crews

    exact = remaining * forecast / total_forecast
    floored = np.floor(exact).astype(int)
    crews += floored
    leftover = remaining - int(floored.sum())
    if leftover > 0:
        fractional = exact - floored
        top = np.argsort(-fractional)[:leftover]
        crews[top] += 1
    return crews


def _evaluate_policy(
    daily_groups: list[pd.DataFrame],
    forecast_column: str,
    total_crews: int = config.TOTAL_CREWS,
    requests_per_crew: int = config.REQUESTS_PER_CREW,
) -> dict[str, float]:
    """Run the allocation policy across all days and aggregate decision metrics."""
    total_weighted_unmet = 0.0
    total_unmet = 0.0
    cell_day_count = 0
    high_demand_covered = 0
    high_demand_total = 0
    total_served = 0.0
    total_capacity = 0.0

    for day in daily_groups:
        forecast = day[forecast_column].to_numpy(dtype=float)
        actual = day[config.TARGET_COLUMN].to_numpy(dtype=float)
        weights = day["complaint_group"].map(config.COMPLAINT_GROUP_WEIGHTS).to_numpy(dtype=float)

        crews = allocate_crews(forecast, total_crews=total_crews)
        capacity = crews * requests_per_crew

        unmet = np.clip(actual - capacity, 0.0, None)
        served = np.minimum(actual, capacity)

        total_weighted_unmet += float(np.sum(unmet * weights))
        total_unmet += float(np.sum(unmet))
        cell_day_count += len(actual)
        total_served += float(np.sum(served))
        total_capacity += float(np.sum(capacity))

        threshold = np.quantile(actual, config.HIGH_DEMAND_QUANTILE)
        high_mask = actual >= threshold
        high_demand_total += int(np.sum(high_mask))
        high_demand_covered += int(np.sum((capacity >= actual) & high_mask))

    coverage_rate = high_demand_covered / high_demand_total if high_demand_total else 0.0
    allocation_efficiency = total_served / total_capacity if total_capacity else 0.0
    average_shortfall = total_unmet / cell_day_count if cell_day_count else 0.0

    return {
        "total_weighted_unmet_demand": round(total_weighted_unmet, 3),
        "total_unmet_demand": round(total_unmet, 3),
        "average_service_shortfall": round(average_shortfall, 4),
        "high_demand_coverage_rate": round(coverage_rate, 4),
        "allocation_efficiency": round(allocation_efficiency, 4),
    }


def run_simulation() -> dict:
    """Execute the staffing simulation and persist the report and figure."""
    ensure_directories()
    frame = load_processed_dataset()
    train_df, val_df, test_df = chronological_split(frame)

    models = _train_policy_models(train_df, val_df)
    test_df = test_df.copy()
    for feature_set, pipeline in models.items():
        x_test, _ = features.build_feature_matrix(test_df, feature_set)
        test_df[f"forecast_{feature_set}"] = np.clip(pipeline.predict(x_test), 0.0, None)
    test_df["forecast_oracle"] = test_df[config.TARGET_COLUMN]

    daily_groups = [group for _, group in test_df.groupby("date")]

    # Evaluate one policy per available forecast feature set, plus the oracle.
    policies: dict[str, dict] = {}
    for feature_set in models:
        policies[feature_set] = _evaluate_policy(daily_groups, f"forecast_{feature_set}")
    oracle = _evaluate_policy(daily_groups, "forecast_oracle")
    policies["oracle_true_demand"] = oracle

    # The headline comparison anchors on the internal-historical baseline versus
    # the strongest available augmented policy (calendar+weather if present,
    # else calendar).
    baseline = policies["internal_historical"]
    headline_set = (
        "calendar_weather_augmented"
        if "calendar_weather_augmented" in models
        else "calendar_augmented"
    )
    augmented = policies[headline_set]

    baseline_unmet = baseline["total_weighted_unmet_demand"]
    augmented_unmet = augmented["total_weighted_unmet_demand"]
    oracle_unmet = oracle["total_weighted_unmet_demand"]
    improvement_pct = (
        (baseline_unmet - augmented_unmet) / baseline_unmet * 100.0
        if baseline_unmet
        else 0.0
    )
    headroom = baseline_unmet - oracle_unmet
    gap_closed_pct = (
        (baseline_unmet - augmented_unmet) / headroom * 100.0 if headroom else 0.0
    )

    report = {
        "description": (
            "Stylized staffing-allocation simulation. Not a real dispatch system "
            "and not a claim of real staffing optimization."
        ),
        "assumptions": {
            "requests_per_crew": config.REQUESTS_PER_CREW,
            "total_crews": config.TOTAL_CREWS,
            "min_crews_per_cell": config.MIN_CREWS_PER_CELL,
            "high_demand_quantile": config.HIGH_DEMAND_QUANTILE,
            "complaint_group_weights": config.COMPLAINT_GROUP_WEIGHTS,
            "allocation_rule": "proportional_to_forecast_largest_remainder",
        },
        "test_days": len(daily_groups),
        "headline_augmented_policy": headline_set,
        "policies": policies,
        "augmented_improvement_over_baseline": {
            "headline_augmented_policy": headline_set,
            "weighted_unmet_demand_reduction_pct": round(improvement_pct, 3),
            "augmented_better": augmented_unmet < baseline_unmet,
            "gap_to_oracle_closed_pct": round(gap_closed_pct, 3),
            "baseline_weighted_unmet": baseline_unmet,
            "augmented_weighted_unmet": augmented_unmet,
            "oracle_weighted_unmet": oracle_unmet,
        },
    }
    save_json(config.DECISION_SIMULATION_REPORT_FILE, report)
    _plot_decision_quality(baseline, augmented, oracle)

    LOGGER.info(
        "Decision simulation complete. Calendar-augmented vs baseline "
        "weighted-unmet reduction: %.2f%% (gap to oracle closed: %.1f%%)",
        improvement_pct,
        gap_closed_pct,
    )
    return report


def _plot_decision_quality(baseline: dict, augmented: dict, oracle: dict) -> None:
    """Bar chart comparing weighted unmet demand across the three policies."""
    labels = ["Baseline\n(internal)", "Calendar\naugmented", "Oracle\n(true demand)"]
    values = [
        baseline["total_weighted_unmet_demand"],
        augmented["total_weighted_unmet_demand"],
        oracle["total_weighted_unmet_demand"],
    ]
    colors = ["#9aa7b5", "#2f7d4f", "#b5942f"]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("Total weighted unmet demand (lower is better)")
    ax.set_title("Staffing decision quality by forecast policy")
    fig.tight_layout()
    fig.savefig(config.FIG_DECISION_QUALITY, dpi=120)
    plt.close(fig)


def main() -> None:
    run_simulation()


if __name__ == "__main__":
    main()
