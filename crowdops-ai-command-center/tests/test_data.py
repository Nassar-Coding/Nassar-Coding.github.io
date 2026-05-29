"""Tests for dataset generation and loading."""

from __future__ import annotations

import pandas as pd

from src import REQUIRED_COLUMNS, RISK_LEVELS
from src.data import dataset_summary, load_data
from src.generate_data import generate_dataframe, save_dataset


def test_generate_dataframe_has_required_columns() -> None:
    frame = generate_dataframe(n_rows=300, seed=1)
    assert list(frame.columns) == REQUIRED_COLUMNS


def test_generate_dataframe_minimum_rows() -> None:
    # The full dataset must contain at least 2,000 rows.
    frame = generate_dataframe()
    assert len(frame) >= 2000


def test_risk_level_values_are_valid() -> None:
    frame = generate_dataframe(n_rows=500, seed=2)
    assert set(frame["risk_level"].unique()).issubset(set(RISK_LEVELS))


def test_generation_is_reproducible() -> None:
    a = generate_dataframe(n_rows=200, seed=7)
    b = generate_dataframe(n_rows=200, seed=7)
    pd.testing.assert_frame_equal(a, b)


def test_density_ratio_consistency() -> None:
    frame = generate_dataframe(n_rows=200, seed=3)
    # density_ratio is the (3-decimal rounded) crowd_count / zone_capacity, so
    # it must match the raw ratio within one rounding unit.
    raw_ratio = frame["crowd_count"] / frame["zone_capacity"]
    assert (abs(frame["density_ratio"] - raw_ratio) <= 1e-3).all()


def test_save_and_load_roundtrip(tmp_path) -> None:
    csv_path = tmp_path / "crowd_ops.csv"
    save_dataset(path=csv_path, n_rows=2000, seed=4)
    assert csv_path.exists()

    frame = load_data(csv_path)
    assert len(frame) >= 2000
    assert list(frame.columns) == REQUIRED_COLUMNS


def test_load_missing_file_raises(tmp_path) -> None:
    missing = tmp_path / "nope.csv"
    try:
        load_data(missing)
    except FileNotFoundError as exc:
        assert "generate_data" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected FileNotFoundError for missing dataset")


def test_dataset_summary_keys(tmp_path) -> None:
    csv_path = tmp_path / "crowd_ops.csv"
    save_dataset(path=csv_path, n_rows=2000, seed=5)
    summary = dataset_summary(load_data(csv_path))
    for key in ("total_records", "total_zones", "high_risk_records", "avg_wait_time"):
        assert key in summary
    assert summary["total_records"] >= 2000
