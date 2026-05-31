"""Shared pytest fixtures.

Tests run fully offline and never touch the real ``data/``, ``models/``,
``reports/``, or ``figures/`` directories: every artifact path in ``config`` is
redirected to a session-scoped temporary directory. The committed real-schema
sample (``nyc_311_daily_counts_sample.csv``) is copied into the temporary raw
directory and the build runs in sample mode, so tests exercise the real-data
code path on real NYC 311 rows without any synthetic data generation.
"""
from __future__ import annotations

import shutil
from collections.abc import Iterator
from pathlib import Path

import pandas as pd
import pytest
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge

from src import build_dataset, config

# Location of the committed real-schema sample in the actual repository.
_REPO_SAMPLE = config.SAMPLE_DAILY_COUNTS_FILE

_DIR_ATTRS: dict[str, tuple[str, ...]] = {
    "RAW_DIR": ("data", "raw"),
    "PROCESSED_DIR": ("data", "processed"),
    "METADATA_DIR": ("data", "metadata"),
    "MODELS_DIR": ("models",),
    "REPORTS_DIR": ("reports",),
    "FIGURES_DIR": ("figures",),
}
_FILE_ATTRS: dict[str, tuple[str, ...]] = {
    "DAILY_COUNTS_FILE": ("data", "raw", "nyc_311_daily_counts_2022_2024.csv"),
    "DAILY_COUNTS_META_FILE": ("data", "raw", "nyc_311_daily_counts_2022_2024.meta.json"),
    "MANUAL_RAW_FILE": ("data", "raw", "nyc_311_2022_2024.csv"),
    "SAMPLE_DAILY_COUNTS_FILE": ("data", "raw", "nyc_311_daily_counts_sample.csv"),
    "PROCESSED_DATA_FILE": ("data", "processed", "service_forecasting_dataset.csv"),
    "DATA_SOURCE_REPORT": ("data", "metadata", "data_source_report.json"),
    "BEST_MODEL_FILE": ("models", "best_forecast_model.joblib"),
    "MODEL_COMPARISON_FILE": ("reports", "model_comparison.csv"),
    "METRICS_FILE": ("reports", "metrics.json"),
    "EVALUATION_REPORT_FILE": ("reports", "evaluation_report.json"),
    "DECISION_SIMULATION_REPORT_FILE": ("reports", "decision_simulation_report.json"),
    "MONITORING_REPORT_FILE": ("reports", "monitoring_report.json"),
    "FIG_FORECAST_ERROR": ("figures", "forecast_error_by_model.png"),
    "FIG_INTERNAL_VS_AUGMENTED": ("figures", "internal_vs_calendar_augmented_mae.png"),
    "FIG_DECISION_QUALITY": ("figures", "decision_quality_comparison.png"),
    "FIG_ACTUAL_VS_PREDICTED": ("figures", "forecast_actual_vs_predicted.png"),
}


@pytest.fixture(scope="session", autouse=True)
def isolated_artifacts(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    """Redirect artifact paths to a temp dir and seed the real-schema sample."""
    base = tmp_path_factory.mktemp("artifacts")
    monkeypatch = pytest.MonkeyPatch()

    for attr, parts in _DIR_ATTRS.items():
        directory = base.joinpath(*parts)
        directory.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(config, attr, directory)
    for attr, parts in _FILE_ATTRS.items():
        monkeypatch.setattr(config, attr, base.joinpath(*parts))

    # Seed the committed real-schema sample into the isolated raw directory and
    # force sample mode so the build uses real rows offline.
    if _REPO_SAMPLE.exists():
        shutil.copyfile(_REPO_SAMPLE, config.SAMPLE_DAILY_COUNTS_FILE)
    monkeypatch.setenv("USE_SAMPLE_DATA", "1")

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
    dates = sorted(processed_frame["date"].unique())
    subset = processed_frame[processed_frame["date"].isin(dates)]
    return subset.reset_index(drop=True)


@pytest.fixture
def tiny_raw_counts() -> pd.DataFrame:
    """A tiny hand-built real-schema daily-counts frame for unit tests.

    This is a minimal valid sample of the real schema (date, borough,
    complaint_group, request_volume). It is not research data and is not
    synthetic demand: it is a fixed fixture for exercising schema and feature
    logic deterministically.
    """
    rows = []
    dates = pd.date_range("2022-01-01", periods=20, freq="D")
    for offset, date in enumerate(dates):
        rows.append(
            {
                "date": date,
                "borough": "Manhattan",
                "complaint_group": "Noise",
                "request_volume": 100 + offset,
            }
        )
        rows.append(
            {
                "date": date,
                "borough": "Brooklyn",
                "complaint_group": "Water",
                "request_volume": 50 + 2 * offset,
            }
        )
    return pd.DataFrame(rows)


@pytest.fixture
def fast_models():
    """Factory returning fresh lightweight estimators on each call."""

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
