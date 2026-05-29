"""Data loading and validation for the CrowdOps dataset.

This module is the single entry point for reading ``data/crowd_ops.csv`` into
a validated pandas DataFrame. It checks the schema, fills any accidental
missing values, and raises clear, actionable errors when something is wrong.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src import (
    CATEGORICAL_FEATURES,
    DATA_PATH,
    NUMERIC_FEATURES,
    REQUIRED_COLUMNS,
    TARGET_COLUMN,
)


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load and validate the CrowdOps dataset.

    Args:
        path: Path to the CSV file. Defaults to ``data/crowd_ops.csv``.

    Returns:
        A validated pandas DataFrame with no missing values.

    Raises:
        FileNotFoundError: If the dataset file does not exist.
        ValueError: If required columns are missing or the file is empty.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at '{path}'. "
            "Generate it first with:  python -m src.generate_data"
        )

    frame = pd.read_csv(path)

    if frame.empty:
        raise ValueError(f"Dataset at '{path}' is empty. Re-generate it with src.generate_data.")

    _validate_columns(frame)
    frame = _handle_missing_values(frame)
    return frame


def _validate_columns(frame: pd.DataFrame) -> None:
    """Ensure every required column is present; raise a clear error if not."""
    missing = [col for col in REQUIRED_COLUMNS if col not in frame.columns]
    if missing:
        raise ValueError(
            "Dataset is missing required columns: "
            f"{missing}. Expected columns: {REQUIRED_COLUMNS}"
        )


def _handle_missing_values(frame: pd.DataFrame) -> pd.DataFrame:
    """Fill any missing values defensively.

    The synthetic generator never produces missing values, but real-world
    feeds might. We fill numeric columns with the median and categorical
    columns with the mode so downstream pipelines never break.
    """
    frame = frame.copy()

    for col in NUMERIC_FEATURES:
        if col in frame.columns and frame[col].isna().any():
            frame[col] = frame[col].fillna(frame[col].median())

    for col in CATEGORICAL_FEATURES:
        if col in frame.columns and frame[col].isna().any():
            mode = frame[col].mode(dropna=True)
            fill_value = mode.iloc[0] if not mode.empty else "Unknown"
            frame[col] = frame[col].fillna(fill_value)

    # Drop any row that is still missing the target -- we cannot train on it.
    if frame[TARGET_COLUMN].isna().any():
        frame = frame.dropna(subset=[TARGET_COLUMN]).reset_index(drop=True)

    return frame


def dataset_summary(frame: pd.DataFrame) -> dict:
    """Return a small dictionary of headline stats for dashboards/KPIs."""
    return {
        "total_records": int(len(frame)),
        "total_zones": int(frame["zone"].nunique()),
        "high_risk_records": int((frame[TARGET_COLUMN] == "High").sum()),
        "avg_wait_time": round(float(frame["avg_wait_time"].mean()), 2),
        "risk_distribution": frame[TARGET_COLUMN].value_counts().to_dict(),
    }
