"""Tests for real-data ingestion, schema validation, and complaint mapping."""
from __future__ import annotations

import pandas as pd
import pytest

from src import build_dataset, config


def test_complaint_mapping_is_deterministic_and_correct() -> None:
    # Housing precedes Water so heat/hot-water is Housing, not Water.
    assert build_dataset.map_complaint_group("HEAT/HOT WATER") == "Housing"
    assert build_dataset.map_complaint_group("Water System") == "Water"
    assert build_dataset.map_complaint_group("Noise - Residential") == "Noise"
    assert build_dataset.map_complaint_group("Illegal Parking") == "Traffic"
    assert build_dataset.map_complaint_group("Illegal Fireworks") == "Public Safety"
    assert build_dataset.map_complaint_group("Missed Collection") == "Sanitation"
    assert build_dataset.map_complaint_group("Pothole") == "Street Condition"
    # Unknown types fall through to Other.
    assert build_dataset.map_complaint_group("New Tree Request") == "Other"
    assert build_dataset.map_complaint_group(None) == "Other"
    assert build_dataset.map_complaint_group("") == "Other"


def test_no_synthetic_data_mode_exists() -> None:
    # Only real and sample (real-schema) modes are defined; no synthetic mode.
    assert config.DATA_MODE_REAL == "real_nyc_311"
    assert config.DATA_MODE_SAMPLE == "sample_real_schema"
    modes = {config.DATA_MODE_REAL, config.DATA_MODE_SAMPLE}
    assert not any("synth" in m.lower() for m in modes)


def test_build_refuses_when_no_real_data(monkeypatch, tmp_path) -> None:
    # Point every input path at non-existent files and disable sample mode.
    monkeypatch.setattr(config, "SAMPLE_DAILY_COUNTS_FILE", tmp_path / "missing_sample.csv")
    monkeypatch.setattr(config, "DAILY_COUNTS_FILE", tmp_path / "missing_counts.csv")
    monkeypatch.setattr(config, "MANUAL_RAW_FILE", tmp_path / "missing_raw.csv")
    monkeypatch.delenv("USE_SAMPLE_DATA", raising=False)
    monkeypatch.delenv("DATA_MODE", raising=False)

    with pytest.raises(build_dataset.DataUnavailableError):
        build_dataset.build_processed_dataset()


def test_daily_counts_validation_rejects_invalid_borough(tmp_path) -> None:
    bad = pd.DataFrame(
        {
            "date": ["2022-01-01"],
            "borough": ["ATLANTIS"],
            "complaint_group": ["Noise"],
            "request_volume": [10],
        }
    )
    path = tmp_path / "bad.csv"
    bad.to_csv(path, index=False)
    with pytest.raises(build_dataset.DataUnavailableError):
        build_dataset._validate_daily_counts(pd.read_csv(path), path)


def test_daily_counts_validation_rejects_negative_volume(tmp_path) -> None:
    bad = pd.DataFrame(
        {
            "date": ["2022-01-01"],
            "borough": ["Manhattan"],
            "complaint_group": ["Noise"],
            "request_volume": [-5],
        }
    )
    path = tmp_path / "bad.csv"
    bad.to_csv(path, index=False)
    with pytest.raises(build_dataset.DataUnavailableError):
        build_dataset._validate_daily_counts(pd.read_csv(path), path)


def test_data_source_report_records_real_schema_mode(processed_frame) -> None:
    # The session build runs in sample (real-schema) mode and must say so,
    # and must explicitly record that no synthetic data was used.
    from src.utils import load_json

    report = load_json(config.DATA_SOURCE_REPORT)
    assert report["data_mode"] == config.DATA_MODE_SAMPLE
    assert report["no_synthetic_data"] is True
    assert report["synthetic_fallback_used"] is False
