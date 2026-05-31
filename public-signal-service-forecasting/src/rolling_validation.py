"""Rolling-origin validation on real processed NYC 311 data.

This module evaluates the naive baseline and the Ridge / random forest /
gradient boosting regressors (each on the internal-historical and
calendar-augmented feature sets) across several chronological folds. Each fold
trains on all dates up to a cut point and tests on the following block of dates,
so no future information leaks into training and no random split is used.

Outputs:
- reports/rolling_validation_report.csv   (per-fold, per-configuration metrics)
- reports/rolling_validation_summary.json (mean/std/min/max across folds)
- figures/rolling_validation_mae.png      (per-fold test MAE by configuration)
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import config, features
from .train import _build_models, _naive_predictions, load_processed_dataset, make_pipeline
from .utils import compute_metrics, ensure_directories, get_logger, save_json

LOGGER = get_logger(__name__)

# Number of rolling folds and the fraction of dates used for the initial
# training window before the first test block.
N_FOLDS: int = 5
INITIAL_TRAIN_FRACTION: float = 0.50


def _fold_date_bounds(unique_dates: np.ndarray) -> list[tuple[int, int, int]]:
    """Return (train_end, test_start, test_end) index bounds for each fold.

    The training window grows with each fold (expanding-window rolling origin);
    the test block is the next contiguous slice of dates after the training
    window. Index bounds refer to positions in the sorted unique-date array.
    """
    n_dates = len(unique_dates)
    initial_train = int(n_dates * INITIAL_TRAIN_FRACTION)
    remaining = n_dates - initial_train
    if remaining < N_FOLDS:
        raise ValueError("Not enough dates for the requested number of folds.")
    block = remaining // N_FOLDS

    bounds: list[tuple[int, int, int]] = []
    for fold in range(N_FOLDS):
        train_end = initial_train + fold * block
        test_start = train_end
        test_end = train_end + block if fold < N_FOLDS - 1 else n_dates
        bounds.append((train_end, test_start, test_end))
    return bounds


def _configurations() -> list[tuple[str, str]]:
    """Return (model_name, feature_set) configurations to evaluate per fold."""
    configs: list[tuple[str, str]] = [("naive_seasonal", "naive_seasonal")]
    for model_name in _build_models():
        for feature_set in config.FEATURE_SETS:
            configs.append((model_name, feature_set))
    return configs


def run_rolling_validation() -> dict:
    """Run rolling-origin validation and persist reports and a figure."""
    ensure_directories()
    frame = load_processed_dataset()
    unique_dates = np.sort(frame["date"].unique())
    bounds = _fold_date_bounds(unique_dates)

    rows: list[dict] = []
    for fold_index, (train_end, test_start, test_end) in enumerate(bounds):
        train_dates = set(unique_dates[:train_end])
        test_dates = set(unique_dates[test_start:test_end])
        train_df = frame[frame["date"].isin(train_dates)].reset_index(drop=True)
        test_df = frame[frame["date"].isin(test_dates)].reset_index(drop=True)

        assert max(train_dates) < min(test_dates), "Chronological order violated."

        fold_label = (
            f"fold{fold_index + 1}:"
            f"{str(min(test_dates))[:10]}..{str(max(test_dates))[:10]}"
        )
        y_test = test_df[config.TARGET_COLUMN].to_numpy(dtype=float)

        for model_name, feature_set in _configurations():
            if model_name == "naive_seasonal":
                pred = _naive_predictions(test_df)
            else:
                x_train, y_train = features.build_feature_matrix(train_df, feature_set)
                x_test, _ = features.build_feature_matrix(test_df, feature_set)
                pipeline = make_pipeline(feature_set, _build_models()[model_name])
                pipeline.fit(x_train, y_train)
                pred = np.clip(pipeline.predict(x_test), 0.0, None)

            metrics = compute_metrics(y_test, pred)
            rows.append(
                {
                    "fold": fold_index + 1,
                    "fold_label": fold_label,
                    "test_start": str(min(test_dates))[:10],
                    "test_end": str(max(test_dates))[:10],
                    "train_rows": int(len(train_df)),
                    "test_rows": int(len(test_df)),
                    "model": model_name,
                    "feature_set": feature_set,
                    **{k: round(v, 4) for k, v in metrics.items()},
                }
            )
        LOGGER.info("Completed rolling fold %s/%s (%s)", fold_index + 1, N_FOLDS, fold_label)

    report = pd.DataFrame(rows)
    report.to_csv(config.ROLLING_VALIDATION_REPORT_FILE, index=False)

    summary = _summarise(report)
    save_json(config.ROLLING_VALIDATION_SUMMARY_FILE, summary)
    _plot(report)

    LOGGER.info(
        "Rolling-origin validation complete: %s folds, %s configurations.",
        N_FOLDS,
        len(_configurations()),
    )
    return summary


def _summarise(report: pd.DataFrame) -> dict:
    """Summarise mean/std/min/max of each metric across folds per configuration."""
    summary: dict = {"n_folds": int(report["fold"].nunique()), "configurations": {}}
    for (model_name, feature_set), group in report.groupby(["model", "feature_set"]):
        key = f"{model_name}|{feature_set}"
        metric_stats = {
            metric: {
                "mean": round(float(group[metric].mean()), 4),
                "std": round(float(group[metric].std(ddof=0)), 4),
                "min": round(float(group[metric].min()), 4),
                "max": round(float(group[metric].max()), 4),
            }
            for metric in ("mae", "rmse", "mape", "r2")
        }
        summary["configurations"][key] = {
            "model": model_name,
            "feature_set": feature_set,
            **metric_stats,
        }

    # Per-fold internal-vs-calendar improvement for each model family, plus
    # whether calendar augmentation wins in every fold (consistency).
    consistency: dict = {}
    for model_name in report["model"].unique():
        if model_name == "naive_seasonal":
            continue
        internal = report[
            (report["model"] == model_name) & (report["feature_set"] == "internal_historical")
        ].set_index("fold")["mae"]
        augmented = report[
            (report["model"] == model_name) & (report["feature_set"] == "calendar_augmented")
        ].set_index("fold")["mae"]
        folds = sorted(set(internal.index) & set(augmented.index))
        per_fold = [
            {
                "fold": int(f),
                "internal_mae": round(float(internal[f]), 4),
                "calendar_augmented_mae": round(float(augmented[f]), 4),
                "improvement_pct": round(
                    float((internal[f] - augmented[f]) / internal[f] * 100.0), 4
                )
                if internal[f]
                else 0.0,
            }
            for f in folds
        ]
        improvements = [r["improvement_pct"] for r in per_fold]
        consistency[model_name] = {
            "per_fold": per_fold,
            "mean_improvement_pct": round(float(np.mean(improvements)), 4) if improvements else 0.0,
            "calendar_augmented_wins_all_folds": bool(all(i > 0 for i in improvements)),
            "n_folds_augmented_better": int(sum(i > 0 for i in improvements)),
        }
    summary["calendar_augmentation_consistency"] = consistency
    return summary


def _plot(report: pd.DataFrame) -> None:
    """Line plot of per-fold test MAE for each configuration."""
    fig, ax = plt.subplots(figsize=(11, 6))
    for (model_name, feature_set), group in report.groupby(["model", "feature_set"]):
        group = group.sort_values("fold")
        label = f"{model_name} [{feature_set}]"
        ax.plot(group["fold"], group["mae"], marker="o", label=label)
    ax.set_xlabel("Rolling fold (chronological)")
    ax.set_ylabel("Test MAE (requests)")
    ax.set_title("Rolling-origin validation: test MAE by configuration and fold")
    ax.set_xticks(sorted(report["fold"].unique()))
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(config.FIG_ROLLING_VALIDATION, dpi=120)
    plt.close(fig)


def main() -> None:
    run_rolling_validation()


if __name__ == "__main__":
    main()
