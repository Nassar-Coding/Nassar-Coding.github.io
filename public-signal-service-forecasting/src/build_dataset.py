"""Build the processed modelling dataset from real NYC 311 data.

Research mode consumes real observed daily counts for 2022-2024. There is no
synthetic fallback: if real data (or, in CI/test mode, the committed real-schema
sample) is unavailable or invalid, the build fails with a specific error.

Input resolution order:
1. CI/sample mode (USE_SAMPLE_DATA=1 or DATA_MODE=sample_real_schema): use the
   committed real-schema sample counts file.
2. Pre-aggregated real daily counts file, if present.
3. Manual raw NYC 311 export (record-level), if present; aggregated in-process.

The processed dataset adds calendar features, leakage-safe lag/rolling features,
and the observed next-day target.
"""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from . import config, features
from .utils import ensure_directories, get_logger, load_json, save_json

LOGGER = get_logger(__name__)

_DAILY_COUNT_COLUMNS = ["date", "borough", "complaint_group", "request_volume"]


class DataUnavailableError(RuntimeError):
    """Raised when no valid real input data can be located or parsed."""


def map_complaint_group(complaint_type: object) -> str:
    """Map a raw complaint_type to a complaint_group using deterministic rules."""
    if not isinstance(complaint_type, str):
        return "Other"
    text = complaint_type.strip().upper()
    if not text:
        return "Other"
    for group, keywords in config.COMPLAINT_GROUP_RULES:
        for keyword in keywords:
            if keyword in text:
                return group
    return "Other"


def _validate_daily_counts(frame: pd.DataFrame, source: Path) -> pd.DataFrame:
    """Validate and normalise a daily-counts frame."""
    missing = [c for c in _DAILY_COUNT_COLUMNS if c not in frame.columns]
    if missing:
        raise DataUnavailableError(
            f"Daily-counts file {source} is missing required column(s): {missing}. "
            f"Found columns: {list(frame.columns)}"
        )
    frame = frame[_DAILY_COUNT_COLUMNS].copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    if frame["date"].isna().any():
        raise DataUnavailableError(f"Unparseable date values found in {source}.")

    invalid_boroughs = set(frame["borough"].unique()) - set(config.BOROUGHS)
    if invalid_boroughs:
        raise DataUnavailableError(
            f"Invalid borough value(s) in {source}: {sorted(invalid_boroughs)}"
        )
    frame["request_volume"] = pd.to_numeric(frame["request_volume"], errors="coerce")
    if frame["request_volume"].isna().any() or (frame["request_volume"] < 0).any():
        raise DataUnavailableError(
            f"request_volume in {source} must be non-negative numeric values."
        )
    return frame


def _aggregate_manual_raw(source: Path) -> pd.DataFrame:
    """Aggregate a record-level NYC 311 export into daily counts."""
    LOGGER.info("Aggregating manual raw NYC 311 export: %s", source)
    raw = pd.read_csv(source, dtype=str, low_memory=False)

    lower_to_actual = {str(c).strip().lower(): c for c in raw.columns}
    missing = [c for c in config.RAW_REQUIRED_COLUMNS if c not in lower_to_actual]
    if missing:
        raise DataUnavailableError(
            f"Manual raw export {source} is missing required column(s): {missing}. "
            f"Found columns: {list(raw.columns)}"
        )
    raw = raw.rename(columns={lower_to_actual[c]: c for c in config.RAW_REQUIRED_COLUMNS})

    created = pd.to_datetime(raw["created_date"], errors="coerce")
    raw = raw.loc[created.notna()].copy()
    raw["date"] = created.loc[created.notna()].dt.normalize()

    start = pd.Timestamp(config.STUDY_START_DATE)
    end = pd.Timestamp(config.STUDY_END_DATE)
    raw = raw.loc[(raw["date"] >= start) & (raw["date"] <= end)].copy()

    borough_upper = raw["borough"].astype(str).str.strip().str.upper()
    valid = borough_upper.isin(config.BOROUGH_NORMALISATION)
    raw = raw.loc[valid].copy()
    raw["borough"] = borough_upper.loc[valid].map(config.BOROUGH_NORMALISATION)

    raw["complaint_group"] = raw["complaint_type"].map(map_complaint_group)
    counts = (
        raw.groupby(["date", "borough", "complaint_group"], observed=True)
        .size()
        .reset_index(name="request_volume")
    )
    if counts.empty:
        raise DataUnavailableError(
            f"Manual raw export {source} produced no rows within {config.STUDY_START_DATE}"
            f"..{config.STUDY_END_DATE}."
        )
    return counts


def _resolve_input() -> tuple[pd.DataFrame, str, Path]:
    """Locate and load the daily-counts input, returning (frame, data_mode, source)."""
    if config.use_sample_data():
        source = config.SAMPLE_DAILY_COUNTS_FILE
        if not source.exists():
            raise DataUnavailableError(
                f"Sample mode requested but committed sample is missing: {source}"
            )
        LOGGER.info("CI/sample mode: using committed real-schema sample %s", source)
        frame = pd.read_csv(source)
        return _validate_daily_counts(frame, source), config.DATA_MODE_SAMPLE, source

    if config.DAILY_COUNTS_FILE.exists():
        source = config.DAILY_COUNTS_FILE
        LOGGER.info("Using pre-aggregated real daily counts: %s", source)
        frame = pd.read_csv(source)
        return _validate_daily_counts(frame, source), config.DATA_MODE_REAL, source

    if config.MANUAL_RAW_FILE.exists():
        frame = _aggregate_manual_raw(config.MANUAL_RAW_FILE)
        return (
            _validate_daily_counts(frame, config.MANUAL_RAW_FILE),
            config.DATA_MODE_REAL,
            config.MANUAL_RAW_FILE,
        )

    raise DataUnavailableError(
        "No real NYC 311 data found. Provide one of:\n"
        f"  1. Pre-aggregated daily counts at {config.DAILY_COUNTS_FILE}\n"
        f"     (columns: {_DAILY_COUNT_COLUMNS}); produce it locally with\n"
        "     scripts/aggregate_nyc_311_local.py over the monthly exports, or\n"
        f"  2. A record-level NYC 311 export at {config.MANUAL_RAW_FILE}\n"
        f"     (columns: {config.RAW_REQUIRED_COLUMNS}).\n"
        "Synthetic data is intentionally not generated."
    )


def _regularise_panel(frame: pd.DataFrame) -> pd.DataFrame:
    """Reindex each cell to a complete daily grid, filling absent days with zero.

    A missing (date, borough, complaint_group) row means zero observed requests
    that day, so reindexing to the full daily range and filling with 0 yields a
    complete, regular daily panel without fabricating demand.
    """
    full_dates = pd.date_range(frame["date"].min(), frame["date"].max(), freq="D")
    pieces = []
    for (borough, group), cell in frame.groupby(["borough", "complaint_group"], sort=True):
        cell = cell.set_index("date").reindex(full_dates)
        cell["borough"] = borough
        cell["complaint_group"] = group
        cell["request_volume"] = cell["request_volume"].fillna(0.0)
        cell.index.name = "date"
        pieces.append(cell.reset_index())
    regular = pd.concat(pieces, ignore_index=True)
    return regular[_DAILY_COUNT_COLUMNS]


def build_processed_dataset() -> pd.DataFrame:
    """Construct, validate, and persist the processed modelling dataset."""
    ensure_directories()
    counts, data_mode, source = _resolve_input()
    counts = _regularise_panel(counts)

    frame = features.add_calendar_features(counts)
    frame = features.add_lag_and_rolling_features(frame)
    frame = features.add_target(frame)

    required_non_null = [
        "request_lag_1",
        "request_lag_7",
        "rolling_mean_7",
        "rolling_mean_14",
        "rolling_std_7",
        "rolling_std_14",
        config.TARGET_COLUMN,
    ]
    before = len(frame)
    frame = frame.dropna(subset=required_non_null).reset_index(drop=True)
    LOGGER.info("Dropped %s warmup/edge rows during feature construction.", before - len(frame))

    frame = frame[config.PROCESSED_COLUMNS].copy()
    for column in ("request_volume", config.TARGET_COLUMN, "request_lag_1", "request_lag_7"):
        frame[column] = frame[column].astype(float)

    frame = frame.sort_values(["date", "borough", "complaint_group"]).reset_index(drop=True)
    frame.to_csv(config.PROCESSED_DATA_FILE, index=False)

    _write_metadata(frame, counts, data_mode, source)
    LOGGER.info(
        "Wrote processed dataset: %s rows, %s columns -> %s",
        len(frame),
        frame.shape[1],
        config.PROCESSED_DATA_FILE,
    )
    return frame


def _relative_to_root(path: Path) -> str:
    """Return path relative to the project root, or the file name if outside it."""
    try:
        return str(path.relative_to(config.PROJECT_ROOT))
    except ValueError:
        return path.name


def _write_metadata(
    processed: pd.DataFrame,
    counts: pd.DataFrame,
    data_mode: str,
    source: Path,
) -> None:
    """Write the data source report, merging aggregation metadata if present."""
    aggregation_meta: dict = {}
    if data_mode == config.DATA_MODE_REAL and config.DAILY_COUNTS_META_FILE.exists():
        try:
            aggregation_meta = load_json(config.DAILY_COUNTS_META_FILE)
        except (ValueError, OSError):
            aggregation_meta = {}

    report = {
        "data_mode": data_mode,
        "source_name": config.DATA_SOURCE_NAME,
        "source_url": config.DATA_SOURCE_URL,
        "study_start_date": config.STUDY_START_DATE,
        "study_end_date": config.STUDY_END_DATE,
        "download_timestamp": datetime.now(UTC).isoformat(),
        "input_source_file": _relative_to_root(source),
        "raw_row_count": int(aggregation_meta.get("raw_rows_read", len(counts))),
        "aggregated_daily_count_rows": int(len(counts)),
        "processed_row_count": int(len(processed)),
        "date_range_observed": [
            str(processed["date"].min().date()),
            str(processed["date"].max().date()),
        ],
        "boroughs_included": sorted(processed["borough"].unique().tolist()),
        "complaint_groups_included": sorted(processed["complaint_group"].unique().tolist()),
        "fields_used": ["created_date", "borough", "complaint_type", "unique_key"],
        "fields_dropped": [
            "all other NYC 311 columns are not used in this baseline"
        ],
        "known_data_quality_issues": [
            "311 reflects reporting behaviour, not true incidence (reporting bias).",
            "Complaint-type to complaint_group mapping is a deterministic approximation.",
            "Rows with invalid/unspecified borough are dropped during aggregation.",
            "Absent (date, borough, group) rows are treated as zero observed requests.",
        ],
        "no_synthetic_data": True,
        "synthetic_fallback_used": False,
    }
    if aggregation_meta:
        report["aggregation_metadata"] = aggregation_meta
    save_json(config.DATA_SOURCE_REPORT, report)


def main() -> None:
    build_processed_dataset()


if __name__ == "__main__":
    main()
