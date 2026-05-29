"""Feature engineering for the CrowdOps risk model.

This module builds a reusable scikit-learn preprocessing pipeline using a
``ColumnTransformer`` so the *exact same* transformations are applied during
training and inference. Encoding/scaling are fit only on training data to
avoid data leakage, and the fitted transformer travels inside the model
pipeline that we persist to disk.
"""

from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    RANDOM_SEED,
    TARGET_COLUMN,
)


def split_features_target(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Separate the model features (X) from the prediction target (y).

    The ``timestamp`` column is intentionally excluded from features: it is an
    identifier/ordering field, not a generalisable predictor.
    """
    feature_columns = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    features = frame[feature_columns].copy()
    target = frame[TARGET_COLUMN].copy()
    return features, target


def build_preprocessor() -> ColumnTransformer:
    """Create the ColumnTransformer that scales numerics and encodes categoricals.

    - Numeric features  -> StandardScaler (zero mean, unit variance).
    - Categorical features -> OneHotEncoder (unknown categories handled safely
      at inference time so unseen zones/events do not crash prediction).
    """
    # ``sparse_output`` replaced ``sparse`` in modern scikit-learn; fall back
    # gracefully so the code runs across reasonable versions.
    try:
        ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:  # pragma: no cover - older scikit-learn
        ohe = OneHotEncoder(handle_unknown="ignore", sparse=False)

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            ("categorical", ohe, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )
    return preprocessor


def make_train_test_split(
    frame: pd.DataFrame,
    test_size: float = 0.2,
    seed: int = RANDOM_SEED,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Return a stratified train/test split of features and target.

    Stratifying on the target keeps the Low/Medium/High balance consistent
    across the train and test partitions.
    """
    features, target = split_features_target(frame)
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=test_size,
        random_state=seed,
        stratify=target,
    )
    return x_train, x_test, y_train, y_test
