"""Train and compare forecasting models across feature sets.

Two feature sets (internal-historical and calendar-augmented) are each evaluated
with a naive seasonal baseline and three regularised/ensemble regressors using a
strictly chronological train/validation/test split. The best model by validation
MAE is refit on train+validation and persisted for inference.
"""
from __future__ import annotations

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline

from . import config, features
from .build_dataset import build_processed_dataset
from .utils import compute_metrics, ensure_directories, get_logger, save_json

LOGGER = get_logger(__name__)


def load_processed_dataset() -> pd.DataFrame:
    """Load the processed dataset, building it first if it does not exist."""
    if not config.PROCESSED_DATA_FILE.exists():
        LOGGER.info("Processed dataset missing; building it now.")
        build_processed_dataset()
    frame = pd.read_csv(config.PROCESSED_DATA_FILE, parse_dates=["date"])
    return frame.sort_values(["date", "borough", "complaint_group"]).reset_index(drop=True)


def chronological_split(
    frame: pd.DataFrame,
    train_fraction: float = config.TRAIN_FRACTION,
    validation_fraction: float = config.VALIDATION_FRACTION,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split by date into train/validation/test, preserving chronological order.

    No future dates leak into earlier partitions: the cut points are defined on
    the sorted sequence of unique dates.
    """
    unique_dates = np.sort(frame["date"].unique())
    n_dates = len(unique_dates)
    train_end = int(n_dates * train_fraction)
    val_end = int(n_dates * (train_fraction + validation_fraction))

    train_dates = set(unique_dates[:train_end])
    val_dates = set(unique_dates[train_end:val_end])
    test_dates = set(unique_dates[val_end:])

    train_df = frame[frame["date"].isin(train_dates)].reset_index(drop=True)
    val_df = frame[frame["date"].isin(val_dates)].reset_index(drop=True)
    test_df = frame[frame["date"].isin(test_dates)].reset_index(drop=True)
    return train_df, val_df, test_df


def _build_models() -> dict[str, object]:
    """Return the set of regressors to evaluate (excluding the naive baseline)."""
    return {
        "ridge": Ridge(alpha=1.0, random_state=config.RANDOM_SEED),
        "random_forest": RandomForestRegressor(
            n_estimators=200,
            max_depth=14,
            min_samples_leaf=2,
            n_jobs=-1,
            random_state=config.RANDOM_SEED,
        ),
        "gradient_boosting": GradientBoostingRegressor(
            n_estimators=200,
            max_depth=3,
            learning_rate=0.05,
            random_state=config.RANDOM_SEED,
        ),
    }


def make_pipeline(feature_set: str, model: object) -> Pipeline:
    """Wrap a regressor with the feature-set preprocessor."""
    return Pipeline(
        steps=[
            ("preprocess", features.make_preprocessor(feature_set)),
            ("model", model),
        ]
    )


def _naive_predictions(frame: pd.DataFrame) -> np.ndarray:
    """Naive seasonal baseline: predict the trailing 7-day rolling mean."""
    return np.clip(frame["rolling_mean_7"].to_numpy(dtype=float), 0.0, None)


def train_and_compare() -> dict:
    """Train all model/feature-set combinations and persist comparison artifacts."""
    ensure_directories()
    frame = load_processed_dataset()
    train_df, val_df, test_df = chronological_split(frame)
    LOGGER.info(
        "Split sizes -> train: %s, validation: %s, test: %s",
        len(train_df),
        len(val_df),
        len(test_df),
    )

    comparison_rows: list[dict] = []
    fitted: dict[tuple[str, str], Pipeline] = {}

    # Naive seasonal baseline (feature-set independent, reported once).
    naive_val = compute_metrics(val_df[config.TARGET_COLUMN].to_numpy(), _naive_predictions(val_df))
    naive_test = compute_metrics(test_df[config.TARGET_COLUMN].to_numpy(), _naive_predictions(test_df))
    comparison_rows.append(
        _comparison_row("naive_seasonal", "naive_seasonal", naive_val, naive_test)
    )

    feature_sets = config.available_feature_sets(list(frame.columns))
    LOGGER.info("Evaluating feature sets: %s", list(feature_sets))
    for feature_set in feature_sets:
        x_train, y_train = features.build_feature_matrix(train_df, feature_set)
        x_val, y_val = features.build_feature_matrix(val_df, feature_set)
        x_test, y_test = features.build_feature_matrix(test_df, feature_set)

        for model_name, estimator in _build_models().items():
            pipeline = make_pipeline(feature_set, estimator)
            pipeline.fit(x_train, y_train)

            val_pred = np.clip(pipeline.predict(x_val), 0.0, None)
            test_pred = np.clip(pipeline.predict(x_test), 0.0, None)
            val_metrics = compute_metrics(y_val, val_pred)
            test_metrics = compute_metrics(y_test, test_pred)

            comparison_rows.append(
                _comparison_row(model_name, feature_set, val_metrics, test_metrics)
            )
            fitted[(model_name, feature_set)] = pipeline
            LOGGER.info(
                "Trained %s [%s] -> val MAE: %.3f, test MAE: %.3f",
                model_name,
                feature_set,
                val_metrics["mae"],
                test_metrics["mae"],
            )

    comparison = pd.DataFrame(comparison_rows)
    comparison.to_csv(config.MODEL_COMPARISON_FILE, index=False)

    best_key = _select_best(fitted, val_df)
    best_model_name, best_feature_set = best_key
    best_pipeline = _refit_best(best_key, train_df, val_df)

    joblib.dump(
        {
            "pipeline": best_pipeline,
            "feature_set": best_feature_set,
            "feature_columns": config.FEATURE_SETS[best_feature_set],
            "model_name": best_model_name,
            "target": config.TARGET_COLUMN,
        },
        config.BEST_MODEL_FILE,
    )

    metrics_payload = {
        "primary_metric": config.PRIMARY_METRIC,
        "best_model": best_model_name,
        "best_feature_set": best_feature_set,
        "split": {
            "train_rows": int(len(train_df)),
            "validation_rows": int(len(val_df)),
            "test_rows": int(len(test_df)),
            "train_fraction": config.TRAIN_FRACTION,
            "validation_fraction": config.VALIDATION_FRACTION,
        },
        "comparison": comparison_rows,
        "internal_vs_augmented": _internal_vs_augmented_summary(comparison_rows),
    }
    save_json(config.METRICS_FILE, metrics_payload)
    LOGGER.info(
        "Best model: %s [%s]; artifacts written to reports/ and models/.",
        best_model_name,
        best_feature_set,
    )
    return metrics_payload


def _comparison_row(
    model_name: str, feature_set: str, val_metrics: dict, test_metrics: dict
) -> dict:
    row = {"model": model_name, "feature_set": feature_set}
    for key, value in val_metrics.items():
        row[f"val_{key}"] = value
    for key, value in test_metrics.items():
        row[f"test_{key}"] = value
    return row


def _select_best(fitted: dict[tuple[str, str], Pipeline], val_df: pd.DataFrame) -> tuple[str, str]:
    """Select the best (model, feature_set) by validation MAE among ML models."""
    best_key: tuple[str, str] | None = None
    best_mae = float("inf")
    for key, pipeline in fitted.items():
        _, feature_set = key
        x_val, y_val = features.build_feature_matrix(val_df, feature_set)
        pred = np.clip(pipeline.predict(x_val), 0.0, None)
        current = compute_metrics(y_val, pred)["mae"]
        if current < best_mae:
            best_mae = current
            best_key = key
    assert best_key is not None
    return best_key


def _refit_best(
    best_key: tuple[str, str], train_df: pd.DataFrame, val_df: pd.DataFrame
) -> Pipeline:
    """Refit the best pipeline on the combined train+validation partitions."""
    model_name, feature_set = best_key
    combined = pd.concat([train_df, val_df], ignore_index=True)
    combined = combined.sort_values(["date", "borough", "complaint_group"]).reset_index(drop=True)
    x_combined, y_combined = features.build_feature_matrix(combined, feature_set)
    pipeline = make_pipeline(feature_set, _build_models()[model_name])
    pipeline.fit(x_combined, y_combined)
    return pipeline


def _internal_vs_augmented_summary(rows: list[dict]) -> dict:
    """Summarise test MAE for internal-historical vs calendar-augmented per model."""
    summary: dict[str, dict] = {}
    by_key = {(row["model"], row["feature_set"]): row for row in rows}
    model_names = {row["model"] for row in rows if row["feature_set"] in config.FEATURE_SETS}
    for model_name in sorted(model_names):
        internal = by_key.get((model_name, "internal_historical"))
        augmented = by_key.get((model_name, "calendar_augmented"))
        if internal is None or augmented is None:
            continue
        internal_mae = internal["test_mae"]
        augmented_mae = augmented["test_mae"]
        improvement = (
            (internal_mae - augmented_mae) / internal_mae * 100.0 if internal_mae else 0.0
        )
        summary[model_name] = {
            "internal_test_mae": internal_mae,
            "augmented_test_mae": augmented_mae,
            "mae_improvement_pct": improvement,
            "augmented_better": augmented_mae < internal_mae,
        }
    return summary


def main() -> None:
    train_and_compare()


if __name__ == "__main__":
    main()
