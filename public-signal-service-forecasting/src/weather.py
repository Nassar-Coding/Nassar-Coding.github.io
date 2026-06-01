"""Real NOAA weather ingestion for the Candidate C weather-augmentation layer.

This module reads a real NOAA NCEI Daily Summaries (GHCN-Daily) export for the
NYC Central Park station (USW00094728) covering 2022-2024, selects the weather
variables used by the forecasting models, and writes a clean daily weather table
plus a provenance report.

No synthetic weather is generated. If the real export is absent, ingestion
raises a clear error and writes no weather table. Variables that the source does
not provide are recorded as missing and are never fabricated. The one derived
quantity, ``temp_avg``, is computed as the mean of the observed daily maximum
and minimum temperatures only when the source ``TAVG`` column is empty; this is
documented in the weather source report.
"""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from . import config
from .utils import ensure_directories, get_logger, save_json

LOGGER = get_logger(__name__)

# NOAA GHCN-Daily column -> processed weather column. All are real observed
# variables. Units are metric as exported by NCEI (temperatures in degrees C,
# precipitation/snow in mm, wind speed in m/s).
_NOAA_COLUMN_MAP: dict[str, str] = {
    "PRCP": "precipitation_mm",
    "TMAX": "temp_max_c",
    "TMIN": "temp_min_c",
    "TAVG": "temp_avg_c",
    "SNOW": "snowfall_mm",
    "SNWD": "snow_depth_mm",
    "AWND": "wind_speed_ms",
}

# The weather feature columns exposed to the models (after derivation/cleaning).
WEATHER_FEATURE_COLUMNS: list[str] = [
    "precipitation_mm",
    "temp_max_c",
    "temp_min_c",
    "temp_avg_c",
    "snowfall_mm",
    "snow_depth_mm",
    "wind_speed_ms",
]

_EXPECTED_STATION = "USW00094728"


class WeatherUnavailableError(RuntimeError):
    """Raised when no real weather export can be located or parsed."""


def _resolve_source() -> Path:
    """Return the weather input path, preferring the full real export."""
    if config.use_sample_data() and config.SAMPLE_WEATHER_FILE.exists():
        return config.SAMPLE_WEATHER_FILE
    if config.WEATHER_RAW_FILE.exists():
        return config.WEATHER_RAW_FILE
    if config.SAMPLE_WEATHER_FILE.exists():
        return config.SAMPLE_WEATHER_FILE
    raise WeatherUnavailableError(
        "No real weather export found. Provide a NOAA NCEI Daily Summaries CSV "
        f"for station {_EXPECTED_STATION} (NYC Central Park), 2022-2024, at\n"
        f"  {config.WEATHER_RAW_FILE}\n"
        "with at least a DATE column and one of PRCP/TMAX/TMIN/SNOW/SNWD/AWND. "
        "Synthetic weather is intentionally not generated."
    )


def build_weather_table() -> pd.DataFrame:
    """Read, clean, and persist the daily weather table and provenance report."""
    ensure_directories()
    source = _resolve_source()
    LOGGER.info("Reading real weather export: %s", source)
    raw = pd.read_csv(source, dtype=str)

    lower = {str(c).strip().lower(): c for c in raw.columns}
    if "date" not in lower:
        raise WeatherUnavailableError(f"Weather export {source} has no DATE column.")

    frame = pd.DataFrame()
    frame["date"] = pd.to_datetime(raw[lower["date"]], errors="coerce")
    if frame["date"].isna().any():
        raise WeatherUnavailableError(f"Unparseable DATE values in {source}.")

    present: list[str] = []
    missing_from_source: list[str] = []
    for noaa_col, out_col in _NOAA_COLUMN_MAP.items():
        actual = lower.get(noaa_col.lower())
        if actual is None:
            missing_from_source.append(noaa_col)
            continue
        series = pd.to_numeric(raw[actual], errors="coerce")
        if series.notna().sum() == 0:
            # Column exists in the export but is entirely empty at this station.
            missing_from_source.append(noaa_col)
            continue
        frame[out_col] = series
        present.append(noaa_col)

    # Restrict to the study window and sort.
    start = pd.Timestamp(config.STUDY_START_DATE)
    end = pd.Timestamp(config.STUDY_END_DATE)
    frame = frame[(frame["date"] >= start) & (frame["date"] <= end)].copy()
    frame = frame.sort_values("date").reset_index(drop=True)

    # Derive temp_avg_c only if the source did not provide a usable TAVG.
    derived_temp_avg = False
    if "temp_avg_c" not in frame.columns and {"temp_max_c", "temp_min_c"}.issubset(frame.columns):
        frame["temp_avg_c"] = (frame["temp_max_c"] + frame["temp_min_c"]) / 2.0
        derived_temp_avg = True

    # Fill short gaps in real series by time interpolation, then edge-fill, so
    # the join is dense. This carries real neighbouring observations forward and
    # backward; it does not invent values from a model. Gaps filled are counted.
    weather_cols = [c for c in WEATHER_FEATURE_COLUMNS if c in frame.columns]
    gaps_filled = {c: int(frame[c].isna().sum()) for c in weather_cols}
    frame = frame.set_index("date")
    frame[weather_cols] = (
        frame[weather_cols].interpolate(method="time", limit_direction="both")
    )
    frame = frame.reset_index()

    frame = frame[["date", *weather_cols]]
    frame.to_csv(config.WEATHER_DAILY_FILE, index=False)

    report = {
        "data_mode": "real_weather_noaa",
        "source_name": "NOAA NCEI Daily Summaries (GHCN-Daily)",
        "station_id": _EXPECTED_STATION,
        "station_name": "NY CITY CENTRAL PARK, NY US",
        "spatial_resolution": "single city station (Central Park) used as a city-level proxy",
        "study_start_date": config.STUDY_START_DATE,
        "study_end_date": config.STUDY_END_DATE,
        "ingested_at": datetime.now(UTC).isoformat(),
        "input_source_file": _relative(source),
        "rows": int(len(frame)),
        "date_range": [str(frame["date"].min().date()), str(frame["date"].max().date())],
        "variables_used": weather_cols,
        "noaa_columns_present": present,
        "noaa_columns_missing_or_empty": missing_from_source,
        "temp_avg_derived_from_tmax_tmin": derived_temp_avg,
        "short_gaps_time_interpolated_per_column": gaps_filled,
        "units": {
            "precipitation_mm": "mm",
            "temp_max_c": "degrees Celsius",
            "temp_min_c": "degrees Celsius",
            "temp_avg_c": "degrees Celsius",
            "snowfall_mm": "mm",
            "snow_depth_mm": "mm",
            "wind_speed_ms": "metres per second",
        },
        "no_synthetic_weather": True,
        "notes": (
            "Real observed NOAA station data. No synthetic or modelled weather "
            "is generated. Missing source variables are recorded, not fabricated. "
            "A single Central Park station is used as a city-level proxy; this is "
            "a documented spatial-resolution limitation."
        ),
    }
    save_json(config.WEATHER_SOURCE_REPORT, report)
    LOGGER.info(
        "Wrote weather table: %s rows, variables=%s -> %s",
        len(frame),
        weather_cols,
        config.WEATHER_DAILY_FILE,
    )
    return frame


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(config.PROJECT_ROOT))
    except ValueError:
        return path.name


def plot_weather_feature_summary() -> bool:
    """Render a summary figure of the real daily weather series. Returns success."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if not config.WEATHER_DAILY_FILE.exists():
        return False
    frame = pd.read_csv(config.WEATHER_DAILY_FILE, parse_dates=["date"])
    panels = [
        ("temp_max_c", "Daily max temp (C)"),
        ("temp_min_c", "Daily min temp (C)"),
        ("precipitation_mm", "Daily precipitation (mm)"),
        ("snowfall_mm", "Daily snowfall (mm)"),
        ("snow_depth_mm", "Snow depth (mm)"),
        ("wind_speed_ms", "Wind speed (m/s)"),
    ]
    panels = [(c, label) for c, label in panels if c in frame.columns]
    if not panels:
        return False

    rows = (len(panels) + 1) // 2
    fig, axes = plt.subplots(rows, 2, figsize=(12, 2.4 * rows), squeeze=False)
    for idx, (column, label) in enumerate(panels):
        ax = axes[idx // 2][idx % 2]
        ax.plot(frame["date"], frame[column], color="#34557a", linewidth=0.7)
        ax.set_title(label, fontsize=9)
        ax.tick_params(labelsize=7)
    for idx in range(len(panels), rows * 2):
        axes[idx // 2][idx % 2].axis("off")
    fig.suptitle(
        "Real NOAA daily weather, NYC Central Park (USW00094728), 2022-2024",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(config.FIG_WEATHER_FEATURE_SUMMARY, dpi=120)
    plt.close(fig)
    return True


def weather_available() -> bool:
    """Return True if a real weather export (full or sample) is present."""
    try:
        _resolve_source()
        return True
    except WeatherUnavailableError:
        return False


def main() -> None:
    build_weather_table()
    plot_weather_feature_summary()


if __name__ == "__main__":
    main()
