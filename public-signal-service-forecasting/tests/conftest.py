"""Shared pytest fixtures.

Fixtures keep tests fast and fully offline by reusing a single processed
dataset and providing a chronologically-bounded subset plus lightweight models.

All artifact paths are redirected to a session-scoped temporary directory so the
test suite never reads from or writes to the real ``data/``, ``models/``,
``reports/``, or ``figures/`` directories. Real artifacts are therefore produced
only by the actual pipeline commands, never by pytest.
"""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pandas as pd
import pytest
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge

from src import build_dataset, config

# Mapping of config attribute name -> path relative to the temporary base.
# Directory attributes come first so file attributes resolve under them.
_DIR_ATTRS: dict[str, tuple[str, ...]] = {
    "RAW_DIR": ("data", "raw"),
    "PROCESSED_DIR": ("data", "processed"),
    "METADATA_DIR": ("data", "metadata"),
    "MODELS_DIR": ("models",),
    "REPORTS_DIR": ("reports",),
    "FIGURES_DIR": ("figures",),
}
_FILE_ATTRS: dict[str, tuple[str, ...]] = {
    "RAW_DATA_FILE": ("data", "raw", "service_requests_raw.csv"),
    "PROCESSED_DATA_FILE": ("data", "processed", "service_forecasting_dataset.csv"),
    "DATA_SOURCE_REPORT": ("data", "metadata", "data_source_report.json"),
    "BEST_MODEL_FILE": ("models", "best_forecast_model.joblib"),
    "MODEL_COMPARISON_FILE": ("reports", "model_comparison.csv"),
    "METRICS_FILE": ("reports", "metrics.json"),
    "EVALUATION_REPORT_FILE": ("reports", "evaluation_report.json"),
    "DECISION_SIMULATION_REPORT_FILE": ("reports", "decision_simulation_report.json"),
    "MONITORING_REPORT_FILE": ("reports", "monitoring_report.json"),
    "FIG_FORECAST_ERROR": ("figures", "forecast_error_by_model.png"),
    "FIG_INTERNAL_VS_AUGMENTED": ("figures", "internal_vs_augmented_mae.png"),
    "FIG_DECISION_QUALITY": ("figures", "decision_quality_comparison.png"),
}


@pytest.fixture(scope="session", autouse=True)
def isolated_artifacts(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    """Redirect every artifact path in ``config`` to a temporary directory.

    This runs automatically for the whole session so that no test touches the
    real repository artifact directories.
    """
    base = tmp_path_factory.mktemp("artifacts")
    monkeypatch = pytest.MonkeyPatch()

    for attr, parts in _DIR_ATTRS.items():
        directory = base.joinpath(*parts)
        directory.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(config, attr, directory)
    for attr, parts in _FILE_ATTRS.items():
        monkeypatch.setattr(config, attr, base.joinpath(*parts))

    try:
        yield base
    finally:
        monkeypatch.undo()


@pytest.fixture(scope="session")
def processed_frame(isolated_artifacts: Path) -> pd.DataFrame:
    """Build (in the isolated workspace if needed) and return the dataset."""
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
