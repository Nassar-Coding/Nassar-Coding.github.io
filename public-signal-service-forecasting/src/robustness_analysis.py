"""Robustness of forecast accuracy by complaint group and by borough.

For each segment (complaint group, and borough) this module compares the
internal-historical and calendar-augmented feature sets for the best model
family (random forest) on the held-out test partition of the chronological
split, using exactly the same split as training/evaluation.

Outputs:
- reports/complaint_group_performance.csv  (+ figures/complaint_group_mae.png)
- reports/borough_performance.csv          (+ figures/borough_mae.png)
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import config, features
from .train import (
    _build_models,
    chronological_split,
    load_processed_dataset,
    make_pipeline,
)
from .utils import compute_metrics, ensure_directories, get_logger

LOGGER = get_logger(__name__)

# Best model family for the segmented comparison.
_MODEL_NAME = "random_forest"


def _fit_predict_both_feature_sets(
    train_df: pd.DataFrame, test_df: pd.DataFrame
) -> pd.DataFrame:
    """Return the test frame with predictions for each available feature set."""
    test_df = test_df.copy()
    for feature_set in config.available_feature_sets(list(train_df.columns)):
        x_train, y_train = features.build_feature_matrix(train_df, feature_set)
        x_test, _ = features.build_feature_matrix(test_df, feature_set)
        pipeline = make_pipeline(feature_set, _build_models()[_MODEL_NAME])
        pipeline.fit(x_train, y_train)
        test_df[f"pred_{feature_set}"] = np.clip(pipeline.predict(x_test), 0.0, None)
    return test_df


def _augmented_set_name(columns: list[str]) -> str:
    """Strongest available augmented feature set for segment comparison."""
    available = config.available_feature_sets(columns)
    if "calendar_weather_augmented" in available:
        return "calendar_weather_augmented"
    return "calendar_augmented"


def _segment_table(test_df: pd.DataFrame, segment_column: str) -> pd.DataFrame:
    """Build a per-segment MAE comparison: internal vs strongest augmented set."""
    y_col = config.TARGET_COLUMN
    augmented_col = f"pred_{_augmented_set_name(list(test_df.columns))}"
    rows: list[dict] = []
    for segment, group in test_df.groupby(segment_column):
        actual = group[y_col].to_numpy(dtype=float)
        internal = compute_metrics(actual, group["pred_internal_historical"].to_numpy())
        augmented = compute_metrics(actual, group[augmented_col].to_numpy())
        internal_mae = internal["mae"]
        augmented_mae = augmented["mae"]
        improvement = (
            (internal_mae - augmented_mae) / internal_mae * 100.0 if internal_mae else 0.0
        )
        rows.append(
            {
                segment_column: segment,
                "n_test_rows": int(len(group)),
                "mean_actual_next_day": round(float(actual.mean()), 3),
                "internal_historical_mae": round(internal_mae, 4),
                "calendar_augmented_mae": round(augmented_mae, 4),
                "mae_improvement_pct": round(improvement, 4),
                "augmented_better": bool(augmented_mae < internal_mae),
                "internal_historical_rmse": round(internal["rmse"], 4),
                "calendar_augmented_rmse": round(augmented["rmse"], 4),
            }
        )
    table = pd.DataFrame(rows).sort_values("calendar_augmented_mae", ascending=False)
    return table.reset_index(drop=True)


def _plot_segment(table: pd.DataFrame, segment_column: str, path) -> None:
    """Grouped bar chart of internal vs calendar-augmented MAE per segment."""
    labels = table[segment_column].astype(str).tolist()
    internal = table["internal_historical_mae"].to_numpy()
    augmented = table["calendar_augmented_mae"].to_numpy()
    x = np.arange(len(labels))
    width = 0.38

    fig, ax = plt.subplots(figsize=(max(8, len(labels) * 1.1), 5))
    ax.bar(x - width / 2, internal, width, label="Internal historical", color="#9aa7b5")
    ax.bar(x + width / 2, augmented, width, label="Calendar augmented", color="#2f7d4f")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylabel("Test MAE (requests)")
    ax.set_title(f"Test MAE by {segment_column.replace('_', ' ')} (random forest)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def run_robustness_analysis() -> dict:
    """Run segmented robustness analysis and persist reports and figures."""
    ensure_directories()
    frame = load_processed_dataset()
    train_df, val_df, test_df = chronological_split(frame)
    # Use train+validation for fitting, mirroring the final-model protocol.
    fit_df = pd.concat([train_df, val_df], ignore_index=True)
    test_df = _fit_predict_both_feature_sets(fit_df, test_df)

    group_table = _segment_table(test_df, "complaint_group")
    group_table.to_csv(config.COMPLAINT_GROUP_PERFORMANCE_FILE, index=False)
    _plot_segment(group_table, "complaint_group", config.FIG_COMPLAINT_GROUP_MAE)

    borough_table = _segment_table(test_df, "borough")
    borough_table.to_csv(config.BOROUGH_PERFORMANCE_FILE, index=False)
    _plot_segment(borough_table, "borough", config.FIG_BOROUGH_MAE)

    LOGGER.info(
        "Robustness analysis complete. Complaint groups augmented-better: %s/%s; "
        "boroughs augmented-better: %s/%s.",
        int(group_table["augmented_better"].sum()),
        len(group_table),
        int(borough_table["augmented_better"].sum()),
        len(borough_table),
    )
    return {
        "complaint_group": group_table.to_dict(orient="records"),
        "borough": borough_table.to_dict(orient="records"),
    }


def main() -> None:
    run_robustness_analysis()


if __name__ == "__main__":
    main()
