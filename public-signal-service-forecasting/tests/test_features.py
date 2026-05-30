"""Tests for feature engineering and the chronological split."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src import config, features
from src.train import chronological_split


def _toy_frame() -> pd.DataFrame:
    dates = pd.date_range("2022-01-01", periods=30, freq="D")
    rows = []
    for borough in ("Manhattan", "Brooklyn"):
        for group in ("Noise", "Water"):
            for offset, date in enumerate(dates):
                rows.append(
                    {
                        "date": date,
                        "borough": borough,
                        "complaint_group": group,
                        "request_volume": 10 + offset,
                    }
                )
    return pd.DataFrame(rows)


def test_calendar_features_are_added() -> None:
    frame = features.add_calendar_features(_toy_frame())
    assert {"day_of_week", "month", "is_weekend", "is_holiday"}.issubset(frame.columns)
    # 2022-01-01 is a Saturday and New Year's Day.
    new_year = frame[frame["date"] == "2022-01-01"].iloc[0]
    assert new_year["is_weekend"] == 1
    assert new_year["is_holiday"] == 1


def test_lag_features_use_only_past_values() -> None:
    frame = features.add_lag_and_rolling_features(_toy_frame())
    sample = frame[
        (frame["borough"] == "Manhattan") & (frame["complaint_group"] == "Noise")
    ].sort_values("date").reset_index(drop=True)
    # request_volume increases by 1 each day starting at 10, so lag_1 = volume - 1.
    valid = sample.dropna(subset=["request_lag_1"])
    assert np.allclose(valid["request_lag_1"], valid["request_volume"] - 1)


def test_target_is_next_day_volume() -> None:
    frame = features.add_target(_toy_frame())
    sample = frame[
        (frame["borough"] == "Manhattan") & (frame["complaint_group"] == "Noise")
    ].sort_values("date").reset_index(drop=True)
    valid = sample.dropna(subset=[config.TARGET_COLUMN])
    assert np.allclose(valid[config.TARGET_COLUMN], valid["request_volume"] + 1)


def test_build_feature_matrix_shapes(processed_frame) -> None:
    for feature_set, columns in config.FEATURE_SETS.items():
        x, y = features.build_feature_matrix(processed_frame, feature_set)
        assert list(x.columns) == columns
        assert len(x) == len(y)
    internal_cols = config.FEATURE_SETS["internal_only"]
    augmented_cols = config.FEATURE_SETS["augmented"]
    assert set(internal_cols).issubset(set(augmented_cols))
    assert len(augmented_cols) > len(internal_cols)


def test_chronological_split_preserves_order(processed_frame) -> None:
    train_df, val_df, test_df = chronological_split(processed_frame)
    assert len(train_df) > 0 and len(val_df) > 0 and len(test_df) > 0
    assert train_df["date"].max() <= val_df["date"].min()
    assert val_df["date"].max() <= test_df["date"].min()
    # No date appears in more than one partition.
    train_dates = set(train_df["date"].unique())
    val_dates = set(val_df["date"].unique())
    test_dates = set(test_df["date"].unique())
    assert train_dates.isdisjoint(val_dates)
    assert val_dates.isdisjoint(test_dates)
    assert train_dates.isdisjoint(test_dates)
