"""Tests for the real weather ingestion and weather-augmented feature sets.

These tests run against the committed real-schema weather sample seeded into the
isolated workspace by the session fixtures. No synthetic weather is generated.
"""
from __future__ import annotations

import pandas as pd
import pytest

from src import config, weather


def test_weather_table_built_from_real_sample(processed_frame) -> None:
    # Building the processed dataset (in conftest) also builds the weather table.
    assert config.WEATHER_DAILY_FILE.exists()
    assert config.WEATHER_SOURCE_REPORT.exists()
    table = pd.read_csv(config.WEATHER_DAILY_FILE)
    assert "date" in table.columns
    assert len(table) > 0
    assert any(c in table.columns for c in config.WEATHER_FEATURES)


def test_weather_source_report_is_real_and_no_synthetic() -> None:
    weather.build_weather_table()
    from src.utils import load_json

    report = load_json(config.WEATHER_SOURCE_REPORT)
    assert report["no_synthetic_weather"] is True
    assert report["station_id"] == "USW00094728"
    assert report["data_mode"] == "real_weather_noaa"
    # Variables actually used must be a non-empty subset of the declared set.
    assert set(report["variables_used"]).issubset(set(config.WEATHER_FEATURES))
    assert len(report["variables_used"]) > 0


def test_weather_features_present_in_processed(processed_frame) -> None:
    present = [c for c in config.WEATHER_FEATURES if c in processed_frame.columns]
    assert present, "weather columns should be present when weather sample exists"
    for column in present:
        assert processed_frame[column].notna().all()


def test_weather_feature_sets_available(processed_frame) -> None:
    available = config.available_feature_sets(list(processed_frame.columns))
    # With weather present, all four feature sets are available.
    assert "weather_augmented" in available
    assert "calendar_weather_augmented" in available
    assert "internal_historical" in available
    assert "calendar_augmented" in available


def test_weather_missing_raises_without_fabrication(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(config, "WEATHER_RAW_FILE", tmp_path / "missing_weather.csv")
    monkeypatch.setattr(config, "SAMPLE_WEATHER_FILE", tmp_path / "missing_sample.csv")
    monkeypatch.delenv("USE_SAMPLE_DATA", raising=False)
    monkeypatch.delenv("DATA_MODE", raising=False)
    assert weather.weather_available() is False
    with pytest.raises(weather.WeatherUnavailableError):
        weather.build_weather_table()
