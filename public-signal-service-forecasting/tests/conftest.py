"""Shared pytest fixtures.

Fixtures keep tests fast and fully offline by reusing a single processed
dataset and providing a chronologically-bounded subset plus lightweight models.
"""
from __future__ import annotations

import pandas as pd
import pytest
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge

from src import build_dataset, config


@pytest.fixture(scope="session")
def processed_frame() -> pd.DataFrame:
    """Build (if needed) and return the full processed dataset."""
    if not config.PROCESSED_DATA_FILE.exists():
        build_dataset.build_processed_dataset()
    return pd.read_csv(config.PROCESSED_DATA_FILE, parse_dates=["date"])


@pytest.fixture
def small_frame(processed_frame: pd.DataFrame) -> pd.DataFrame:
    """Return a chronologically-bounded subset for fast model training."""
    dates = sorted(processed_frame["date"].unique())[:180]
    subset = processed_frame[processed_frame["date"].isin(dates)]
    return subset.reset_index(drop=True)


@pytest.fixture
def fast_models():
    """Factory returning fresh lightweight estimators on each call.

    Fresh instances per call mirror the production ``_build_models`` contract,
    where each feature set receives its own unfitted estimators.
    """

    def _build() -> dict[str, object]:
        return {
            "ridge": Ridge(alpha=1.0, random_state=config.RANDOM_SEED),
            "random_forest": RandomForestRegressor(
                n_estimators=20,
                max_depth=8,
                n_jobs=1,
                random_state=config.RANDOM_SEED,
            ),
        }

    return _build
