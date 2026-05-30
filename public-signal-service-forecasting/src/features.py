"""Feature engineering: calendar features, lag/rolling features, and matrices.

Lag and rolling features are computed strictly within each
(borough, complaint_group) group using only past observations, which prevents
leakage of future information into the training data.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

from . import config


def _easter_date(year: int) -> pd.Timestamp:
    """Compute Easter Sunday using the anonymous Gregorian algorithm."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    m = (32 + 2 * e + 2 * i - h - k) % 7
    n = (a + 11 * h + 22 * m) // 451
    month = (h + m - 7 * n + 114) // 31
    day = ((h + m - 7 * n + 114) % 31) + 1
    return pd.Timestamp(year=year, month=month, day=day)


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> pd.Timestamp:
    """Return the date of the nth given weekday of a month (weekday: Mon=0)."""
    first = pd.Timestamp(year=year, month=month, day=1)
    offset = (weekday - first.dayofweek) % 7
    return first + pd.Timedelta(days=offset + 7 * (n - 1))


def _last_weekday(year: int, month: int, weekday: int) -> pd.Timestamp:
    """Return the date of the last given weekday of a month."""
    if month == 12:
        next_month = pd.Timestamp(year=year + 1, month=1, day=1)
    else:
        next_month = pd.Timestamp(year=year, month=month + 1, day=1)
    last_day = next_month - pd.Timedelta(days=1)
    offset = (last_day.dayofweek - weekday) % 7
    return last_day - pd.Timedelta(days=offset)


def holiday_dates_for_year(year: int) -> set[pd.Timestamp]:
    """Return a deterministic set of major US public holidays for a year.

    This is a self-contained approximation (observed-date shifting is omitted)
    used only to derive an ``is_holiday`` indicator without external packages.
    """
    holidays: set[pd.Timestamp] = {
        pd.Timestamp(year=year, month=1, day=1),  # New Year's Day
        pd.Timestamp(year=year, month=7, day=4),  # Independence Day
        pd.Timestamp(year=year, month=11, day=11),  # Veterans Day
        pd.Timestamp(year=year, month=12, day=25),  # Christmas Day
        pd.Timestamp(year=year, month=6, day=19),  # Juneteenth
        _nth_weekday(year, 1, 0, 3),  # MLK Day (3rd Mon Jan)
        _nth_weekday(year, 2, 0, 3),  # Presidents Day (3rd Mon Feb)
        _last_weekday(year, 5, 0),  # Memorial Day (last Mon May)
        _nth_weekday(year, 9, 0, 1),  # Labor Day (1st Mon Sep)
        _nth_weekday(year, 10, 0, 2),  # Columbus Day (2nd Mon Oct)
        _nth_weekday(year, 11, 3, 4),  # Thanksgiving (4th Thu Nov)
    }
    return holidays


def _holiday_lookup(dates: pd.Series) -> set[pd.Timestamp]:
    years = sorted({int(year) for year in dates.dt.year.unique()})
    lookup: set[pd.Timestamp] = set()
    for year in years:
        lookup.update(holiday_dates_for_year(year))
    return lookup


def add_calendar_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add day_of_week, month, is_weekend, and is_holiday columns."""
    frame = frame.copy()
    frame["date"] = pd.to_datetime(frame["date"])
    frame["day_of_week"] = frame["date"].dt.dayofweek.astype(int)
    frame["month"] = frame["date"].dt.month.astype(int)
    frame["is_weekend"] = (frame["day_of_week"] >= 5).astype(int)

    holiday_set = _holiday_lookup(frame["date"])
    normalized = frame["date"].dt.normalize()
    frame["is_holiday"] = normalized.isin(holiday_set).astype(int)
    return frame


def add_lag_and_rolling_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add lag and rolling-mean features computed per group using past data only.

    Rolling means are shifted by one day so that the value for a given date only
    uses strictly prior observations.
    """
    frame = frame.copy()
    frame = frame.sort_values(["borough", "complaint_group", "date"]).reset_index(drop=True)
    grouped = frame.groupby(["borough", "complaint_group"], sort=False)["request_volume"]

    frame["request_lag_1"] = grouped.shift(1)
    frame["request_lag_7"] = grouped.shift(7)
    frame["rolling_mean_7"] = grouped.shift(1).rolling(window=7, min_periods=7).mean()
    frame["rolling_mean_14"] = grouped.shift(1).rolling(window=14, min_periods=14).mean()
    return frame


def add_target(frame: pd.DataFrame) -> pd.DataFrame:
    """Add the next-day request volume target per group (observed-style)."""
    frame = frame.copy()
    frame = frame.sort_values(["borough", "complaint_group", "date"]).reset_index(drop=True)
    grouped = frame.groupby(["borough", "complaint_group"], sort=False)["request_volume"]
    frame[config.TARGET_COLUMN] = grouped.shift(-1)
    return frame


def build_feature_matrix(
    frame: pd.DataFrame, feature_set: str
) -> tuple[pd.DataFrame, np.ndarray]:
    """Return the feature DataFrame and target array for a named feature set."""
    if feature_set not in config.FEATURE_SETS:
        raise ValueError(f"Unknown feature set: {feature_set}")
    columns = config.FEATURE_SETS[feature_set]
    features = frame[columns].copy()
    target = frame[config.TARGET_COLUMN].to_numpy(dtype=float)
    return features, target


def make_preprocessor(feature_set: str) -> ColumnTransformer:
    """Build a ColumnTransformer that one-hot encodes categorical features."""
    numeric = [
        column
        for column in config.FEATURE_SETS[feature_set]
        if column not in config.CATEGORICAL_FEATURES
    ]
    return ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                config.CATEGORICAL_FEATURES,
            ),
            ("numeric", "passthrough", numeric),
        ]
    )
