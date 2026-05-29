"""Tests for the feature engineering pipeline."""

from __future__ import annotations

from src import CATEGORICAL_FEATURES, NUMERIC_FEATURES
from src.features import (
    build_preprocessor,
    make_train_test_split,
    split_features_target,
)
from src.generate_data import generate_dataframe


def test_split_features_target_excludes_timestamp_and_target() -> None:
    frame = generate_dataframe(n_rows=300, seed=11)
    features, target = split_features_target(frame)
    assert "timestamp" not in features.columns
    assert "risk_level" not in features.columns
    assert set(features.columns) == set(NUMERIC_FEATURES + CATEGORICAL_FEATURES)
    assert len(features) == len(target)


def test_preprocessor_fit_transform_runs() -> None:
    frame = generate_dataframe(n_rows=400, seed=12)
    features, _ = split_features_target(frame)
    preprocessor = build_preprocessor()
    transformed = preprocessor.fit_transform(features)
    # Output rows must match input rows; columns expand due to one-hot encoding.
    assert transformed.shape[0] == len(features)
    assert transformed.shape[1] >= len(NUMERIC_FEATURES)


def test_train_test_split_shapes_and_stratification() -> None:
    frame = generate_dataframe(n_rows=1000, seed=13)
    x_train, x_test, y_train, y_test = make_train_test_split(frame, test_size=0.2)
    assert len(x_train) + len(x_test) == len(frame)
    assert len(y_train) == len(x_train)
    assert len(y_test) == len(x_test)
    # Roughly 20% in the test split.
    assert abs(len(x_test) / len(frame) - 0.2) < 0.02
