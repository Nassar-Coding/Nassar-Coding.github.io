"""Tests for processed dataset construction (real-schema sample in tests)."""
from __future__ import annotations

import numpy as np

from src import config
from src.build_dataset import build_processed_dataset


def test_processed_dataset_has_required_columns(processed_frame) -> None:
    # The base processed columns must always be present and in order; weather
    # columns may be appended when a real weather export is available.
    assert list(processed_frame.columns)[: len(config.PROCESSED_COLUMNS)] == config.PROCESSED_COLUMNS
    extra = [c for c in processed_frame.columns if c not in config.PROCESSED_COLUMNS]
    assert set(extra).issubset(set(config.WEATHER_FEATURES))


def test_processed_dataset_is_non_empty(processed_frame) -> None:
    # The committed real-schema sample yields a few thousand rows.
    assert len(processed_frame) > 1000


def test_target_is_observed_next_day_count(processed_frame) -> None:
    assert config.TARGET_COLUMN in processed_frame.columns
    target = processed_frame[config.TARGET_COLUMN]
    assert np.issubdtype(target.dtype, np.number)
    assert target.notna().all()
    assert (target >= 0).all()
    # Observed counts are whole numbers.
    assert np.allclose(target.to_numpy(), np.round(target.to_numpy()))


def test_lag_and_rolling_features_present(processed_frame) -> None:
    for column in (
        "request_lag_1",
        "request_lag_7",
        "rolling_mean_7",
        "rolling_mean_14",
        "rolling_std_7",
        "rolling_std_14",
    ):
        assert column in processed_frame.columns
        assert processed_frame[column].notna().all()


def test_calendar_features_present(processed_frame) -> None:
    for column in ("quarter", "year", "day_of_year", "week_of_year",
                   "is_month_start", "is_month_end"):
        assert column in processed_frame.columns
    assert set(processed_frame["year"].unique()).issubset({2022, 2023, 2024})
    assert processed_frame["quarter"].between(1, 4).all()


def test_build_returns_metadata_file() -> None:
    build_processed_dataset()
    assert config.DATA_SOURCE_REPORT.exists()
    assert config.PROCESSED_DATA_FILE.exists()
