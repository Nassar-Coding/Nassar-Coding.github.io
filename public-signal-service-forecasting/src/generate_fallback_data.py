"""Deterministic synthetic-public-style data generator (fallback mode).

This module produces a reproducible synthetic dataset that mimics the schema of
an aggregated NYC 311 service-request feed joined with public weather-like and
event-like signals. It is used when real public data cannot be downloaded.

The generated data is explicitly labelled as a synthetic fallback. It does not
represent real service requests, real weather, or real city operations.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd

from . import config
from .utils import ensure_directories, get_logger, save_json

LOGGER = get_logger(__name__)

# Relative baseline daily volume per borough (population/activity proxy).
_BOROUGH_BASE: dict[str, float] = {
    "Manhattan": 1.30,
    "Brooklyn": 1.25,
    "Queens": 1.10,
    "Bronx": 0.95,
    "Staten Island": 0.55,
}

# Relative baseline daily volume per complaint group.
_GROUP_BASE: dict[str, float] = {
    "Sanitation": 60.0,
    "Noise": 80.0,
    "Street Condition": 45.0,
    "Water": 30.0,
    "Housing": 55.0,
    "Traffic": 40.0,
    "Public Safety": 35.0,
}

# Weather/event sensitivity coefficients per complaint group.
_PRECIP_SENSITIVITY: dict[str, float] = {
    "Sanitation": 0.05,
    "Noise": -0.10,
    "Street Condition": 0.35,
    "Water": 0.45,
    "Housing": 0.10,
    "Traffic": 0.30,
    "Public Safety": 0.05,
}
_TEMP_SENSITIVITY: dict[str, float] = {
    "Sanitation": 0.010,
    "Noise": 0.020,
    "Street Condition": 0.004,
    "Water": 0.006,
    "Housing": 0.002,
    "Traffic": 0.008,
    "Public Safety": 0.012,
}
_EVENT_SENSITIVITY: dict[str, float] = {
    "Sanitation": 0.10,
    "Noise": 0.40,
    "Street Condition": 0.05,
    "Water": 0.05,
    "Housing": 0.05,
    "Traffic": 0.35,
    "Public Safety": 0.30,
}


def _build_date_index() -> pd.DatetimeIndex:
    start = datetime.fromisoformat(config.FALLBACK_START_DATE)
    dates = [start + timedelta(days=offset) for offset in range(config.FALLBACK_NUM_DAYS)]
    return pd.DatetimeIndex(dates)


def _generate_weather(dates: pd.DatetimeIndex, rng: np.random.Generator) -> pd.DataFrame:
    """Generate city-wide daily weather-like signals with seasonality."""
    day_of_year = dates.dayofyear.to_numpy(dtype=float)
    seasonal = np.sin(2.0 * np.pi * (day_of_year - 110.0) / 365.25)

    temp_c = 12.0 + 12.0 * seasonal + rng.normal(0.0, 2.5, size=len(dates))

    # Precipitation: most days dry, occasional rain events, heavier in some seasons.
    rain_prob = 0.28 + 0.05 * np.cos(2.0 * np.pi * (day_of_year - 30.0) / 365.25)
    is_rainy = rng.random(len(dates)) < rain_prob
    precip_amount = rng.gamma(shape=2.0, scale=4.0, size=len(dates))
    precipitation_mm = np.where(is_rainy, precip_amount, 0.0)

    wind_speed_kmh = np.abs(rng.normal(14.0, 6.0, size=len(dates)) + 0.4 * precipitation_mm)

    severe_weather = (
        (precipitation_mm > 20.0) | (wind_speed_kmh > 35.0)
    ).astype(int)

    return pd.DataFrame(
        {
            "date": dates,
            "temp_c": np.round(temp_c, 2),
            "precipitation_mm": np.round(precipitation_mm, 2),
            "wind_speed_kmh": np.round(wind_speed_kmh, 2),
            "severe_weather": severe_weather,
        }
    )


def _generate_events(dates: pd.DatetimeIndex, rng: np.random.Generator) -> np.ndarray:
    """Generate a city-wide event-intensity index in [0, 1]."""
    day_of_week = dates.dayofweek.to_numpy()
    base = 0.25 + 0.15 * (day_of_week >= 4)  # busier Fri/Sat/Sun
    spikes = rng.random(len(dates)) < 0.06
    intensity = base + np.where(spikes, rng.uniform(0.3, 0.6, size=len(dates)), 0.0)
    intensity = intensity + rng.normal(0.0, 0.05, size=len(dates))
    return np.clip(intensity, 0.0, 1.0)


def generate_fallback_dataframe() -> pd.DataFrame:
    """Generate the full synthetic raw dataset as a tidy DataFrame.

    The next-day target is later derived in :mod:`src.build_dataset` by shifting
    the observed ``request_volume`` within each (borough, complaint_group) group,
    so the target is an observed-style next-day value rather than a deterministic
    transform of the same-day features.
    """
    rng = np.random.default_rng(config.RANDOM_SEED)
    dates = _build_date_index()

    weather = _generate_weather(dates, rng)
    event_intensity = _generate_events(dates, rng)
    weather["event_intensity"] = np.round(event_intensity, 4)

    day_of_year = dates.dayofyear.to_numpy(dtype=float)
    day_of_week = dates.dayofweek.to_numpy()
    is_weekend = day_of_week >= 5

    records: list[pd.DataFrame] = []
    for borough in config.BOROUGHS:
        borough_factor = _BOROUGH_BASE[borough]
        for group_index, group in enumerate(config.COMPLAINT_GROUPS):
            group_base = _GROUP_BASE[group]

            # Yearly seasonality with a deterministic group-specific phase shift.
            phase = (group_index * 13) % 90
            seasonal = 1.0 + 0.18 * np.sin(
                2.0 * np.pi * (day_of_year - phase) / 365.25
            )

            # Weekly pattern: noise peaks on weekends, others dip slightly.
            weekly = np.ones(len(dates))
            if group == "Noise":
                weekly = np.where(is_weekend, 1.35, 0.95)
            elif group in ("Traffic", "Street Condition"):
                weekly = np.where(is_weekend, 0.80, 1.10)
            else:
                weekly = np.where(is_weekend, 0.90, 1.05)

            weather_effect = (
                1.0
                + _PRECIP_SENSITIVITY[group] * (weather["precipitation_mm"].to_numpy() / 10.0)
                + _TEMP_SENSITIVITY[group] * (weather["temp_c"].to_numpy() - 12.0)
                + 0.30 * weather["severe_weather"].to_numpy()
                * (1.0 if group in ("Public Safety", "Traffic", "Water") else 0.4)
            )
            weather_effect = np.clip(weather_effect, 0.3, 3.0)
            event_effect = np.clip(1.0 + _EVENT_SENSITIVITY[group] * event_intensity, 0.5, 2.5)

            # Aftermath effect: a storm or major event today also drives elevated
            # requests the following day (cleanup, follow-up, backlog). Blending in
            # the previous day's drivers means same-day public signals carry genuine
            # predictive information about the next-day target without leakage.
            prev_weather = np.concatenate([weather_effect[:1], weather_effect[:-1]])
            prev_event = np.concatenate([event_effect[:1], event_effect[:-1]])
            combined_weather = 0.6 * weather_effect + 0.4 * prev_weather
            combined_event = 0.6 * event_effect + 0.4 * prev_event

            mean_volume = (
                group_base
                * borough_factor
                * seasonal
                * weekly
                * combined_weather
                * combined_event
            )
            mean_volume = np.clip(mean_volume, 1.0, None)

            # Poisson draw gives integer, observation-style counts with noise.
            volume = rng.poisson(mean_volume).astype(int)

            cell = pd.DataFrame(
                {
                    "date": dates,
                    "borough": borough,
                    "complaint_group": group,
                    "request_volume": volume,
                }
            )
            records.append(cell)

    frame = pd.concat(records, ignore_index=True)
    frame = frame.merge(weather, on="date", how="left")
    frame = frame.sort_values(["borough", "complaint_group", "date"]).reset_index(drop=True)
    return frame


def write_fallback_data() -> pd.DataFrame:
    """Generate and persist the synthetic fallback raw dataset plus metadata."""
    ensure_directories()
    frame = generate_fallback_dataframe()
    frame.to_csv(config.RAW_DATA_FILE, index=False)

    metadata = {
        "data_mode": "synthetic_fallback",
        "generated_at": datetime.now(UTC).isoformat(),
        "random_seed": config.RANDOM_SEED,
        "row_count": int(len(frame)),
        "num_days": config.FALLBACK_NUM_DAYS,
        "start_date": config.FALLBACK_START_DATE,
        "boroughs": config.BOROUGHS,
        "complaint_groups": config.COMPLAINT_GROUPS,
        "note": (
            "Synthetic fallback data generated deterministically with seed 42. "
            "This data does not represent real NYC 311 requests, real weather, "
            "or real city operations."
        ),
    }
    save_json(config.DATA_SOURCE_REPORT, metadata)
    LOGGER.info(
        "Wrote synthetic fallback raw data: %s rows -> %s",
        len(frame),
        config.RAW_DATA_FILE,
    )
    return frame


def main() -> None:
    write_fallback_data()


if __name__ == "__main__":
    main()
