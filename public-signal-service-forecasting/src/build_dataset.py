"""Build the processed modelling dataset from raw data.

If raw data is not present, the synthetic fallback generator is invoked first.
The processed dataset contains calendar features, lag and rolling features, and
the next-day target, with leakage-prone initial rows removed.
"""
from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd

from . import config, features
from .generate_fallback_data import write_fallback_data
from .utils import ensure_directories, get_logger, load_json, save_json

LOGGER = get_logger(__name__)


def _load_or_create_raw() -> tuple[pd.DataFrame, str]:
    """Load raw data, generating the synthetic fallback if necessary."""
    if not config.RAW_DATA_FILE.exists():
        LOGGER.info("Raw data not found; generating synthetic fallback dataset.")
        write_fallback_data()
        data_mode = "synthetic_fallback"
    else:
        data_mode = _existing_data_mode()
    raw = pd.read_csv(config.RAW_DATA_FILE, parse_dates=["date"])
    return raw, data_mode


def _existing_data_mode() -> str:
    """Read the recorded data mode from metadata, defaulting to fallback."""
    if config.DATA_SOURCE_REPORT.exists():
        try:
            return str(load_json(config.DATA_SOURCE_REPORT).get("data_mode", "synthetic_fallback"))
        except (ValueError, OSError):
            return "synthetic_fallback"
    return "synthetic_fallback"


def build_processed_dataset() -> pd.DataFrame:
    """Construct, validate, and persist the processed modelling dataset."""
    ensure_directories()
    raw, data_mode = _load_or_create_raw()

    frame = features.add_calendar_features(raw)
    frame = features.add_lag_and_rolling_features(frame)
    frame = features.add_target(frame)

    # Drop rows with undefined lag/rolling features or an undefined target.
    required_non_null = [
        "request_lag_1",
        "request_lag_7",
        "rolling_mean_7",
        "rolling_mean_14",
        config.TARGET_COLUMN,
    ]
    before = len(frame)
    frame = frame.dropna(subset=required_non_null).reset_index(drop=True)
    LOGGER.info("Dropped %s warmup/edge rows during feature construction.", before - len(frame))

    # Enforce column order and presence.
    frame = frame[config.PROCESSED_COLUMNS].copy()
    for column in ("request_volume", config.TARGET_COLUMN, "request_lag_1", "request_lag_7"):
        frame[column] = frame[column].astype(float)

    frame = frame.sort_values(["date", "borough", "complaint_group"]).reset_index(drop=True)
    frame.to_csv(config.PROCESSED_DATA_FILE, index=False)

    _update_metadata(frame, data_mode)
    LOGGER.info(
        "Wrote processed dataset: %s rows, %s columns -> %s",
        len(frame),
        frame.shape[1],
        config.PROCESSED_DATA_FILE,
    )
    return frame


def _update_metadata(frame: pd.DataFrame, data_mode: str) -> None:
    """Augment the data source report with processed-dataset statistics."""
    existing: dict = {}
    if config.DATA_SOURCE_REPORT.exists():
        try:
            existing = load_json(config.DATA_SOURCE_REPORT)
        except (ValueError, OSError):
            existing = {}

    existing.update(
        {
            "data_mode": data_mode,
            "processed_at": datetime.now(UTC).isoformat(),
            "processed_row_count": int(len(frame)),
            "date_min": str(frame["date"].min().date()),
            "date_max": str(frame["date"].max().date()),
            "borough_count": int(frame["borough"].nunique()),
            "complaint_group_count": int(frame["complaint_group"].nunique()),
            "columns": list(frame.columns),
        }
    )
    save_json(config.DATA_SOURCE_REPORT, existing)


def main() -> None:
    build_processed_dataset()


if __name__ == "__main__":
    main()
