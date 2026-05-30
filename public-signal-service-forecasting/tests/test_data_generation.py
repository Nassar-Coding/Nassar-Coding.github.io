"""Tests for synthetic fallback data generation."""
from __future__ import annotations

from src import config
from src.generate_fallback_data import generate_fallback_dataframe, write_fallback_data


def test_fallback_dataframe_has_minimum_rows() -> None:
    frame = generate_fallback_dataframe()
    assert len(frame) >= 10000


def test_fallback_dataframe_has_expected_schema() -> None:
    frame = generate_fallback_dataframe()
    expected = {
        "date",
        "borough",
        "complaint_group",
        "request_volume",
        "temp_c",
        "precipitation_mm",
        "wind_speed_kmh",
        "severe_weather",
        "event_intensity",
    }
    assert expected.issubset(set(frame.columns))


def test_fallback_dataframe_is_deterministic() -> None:
    first = generate_fallback_dataframe()
    second = generate_fallback_dataframe()
    assert first["request_volume"].tolist() == second["request_volume"].tolist()


def test_fallback_values_are_valid() -> None:
    frame = generate_fallback_dataframe()
    assert (frame["request_volume"] >= 0).all()
    assert (frame["precipitation_mm"] >= 0).all()
    assert set(frame["borough"].unique()) == set(config.BOROUGHS)
    assert set(frame["complaint_group"].unique()) == set(config.COMPLAINT_GROUPS)


def test_write_fallback_creates_files() -> None:
    write_fallback_data()
    assert config.RAW_DATA_FILE.exists()
    assert config.DATA_SOURCE_REPORT.exists()
