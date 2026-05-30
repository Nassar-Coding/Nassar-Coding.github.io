"""Tests for processed dataset construction."""
from __future__ import annotations

import numpy as np

from src import config
from src.build_dataset import build_processed_dataset


def test_processed_dataset_has_required_columns(processed_frame) -> None:
    assert list(processed_frame.columns) == config.PROCESSED_COLUMNS


def test_processed_dataset_has_minimum_rows(processed_frame) -> None:
    assert len(processed_frame) >= 10000


def test_target_column_exists_and_is_numeric(processed_frame) -> None:
    assert config.TARGET_COLUMN in processed_frame.columns
    target = processed_frame[config.TARGET_COLUMN]
    assert np.issubdtype(target.dtype, np.number)
    assert target.notna().all()
    assert (target >= 0).all()


def test_lag_and_rolling_features_present(processed_frame) -> None:
    for column in ("request_lag_1", "request_lag_7", "rolling_mean_7", "rolling_mean_14"):
        assert column in processed_frame.columns
        assert processed_frame[column].notna().all()


def test_build_returns_metadata_file() -> None:
    build_processed_dataset()
    assert config.DATA_SOURCE_REPORT.exists()
    assert config.PROCESSED_DATA_FILE.exists()
