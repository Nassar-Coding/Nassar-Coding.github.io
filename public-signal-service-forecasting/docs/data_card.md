# Data Card

## Summary

The modelling dataset is a daily panel indexed by date x borough x complaint
group, augmented with weather-like and event-like public signals and derived
lag/rolling features. The repository supports two data modes and records the
active mode in `data/metadata/data_source_report.json`.

## Data source modes

- **`real_public_data`** - Reserved for a fully documented, key-free public
  ingestion. The included `download_data` routine attempts a bounded, key-free
  download of a public NYC 311 export and archives a sample.
- **`synthetic_fallback`** - A deterministic synthetic dataset generated with a
  fixed seed when real data is unavailable or when a reproducible offline run is
  required. **Unless the metadata explicitly records otherwise, the active mode
  is `synthetic_fallback`.**

The full heterogeneous public export is large and would require a non-trivial,
separately validated aggregation and weather-join step to match the exact daily
borough x complaint-group schema used here. To keep the data contract honest and
fully reproducible offline, the modelling pipeline uses the deterministic
synthetic schema; any downloaded public sample is archived for transparency but
is not silently relabelled as the modelling source.

## Schema

| Column | Type | Description |
|--------|------|-------------|
| `date` | date | Observation date |
| `borough` | category | One of five boroughs |
| `complaint_group` | category | One of seven complaint groups |
| `request_volume` | float | Observed request count on `date` |
| `request_volume_next_day` | float | Target: observed request count on the next day |
| `temp_c` | float | Daily mean temperature (degrees Celsius), public signal |
| `precipitation_mm` | float | Daily precipitation (mm), public signal |
| `wind_speed_kmh` | float | Daily wind speed (km/h), public signal |
| `severe_weather` | int | Severe-weather indicator (0/1), public signal |
| `event_intensity` | float | Event-intensity proxy in [0, 1], public signal |
| `is_weekend` | int | Weekend indicator (0/1) |
| `is_holiday` | int | US public-holiday indicator (0/1) |
| `day_of_week` | int | Day of week (Monday=0) |
| `month` | int | Calendar month (1-12) |
| `request_lag_1` | float | Request volume on the previous day, per cell |
| `request_lag_7` | float | Request volume seven days prior, per cell |
| `rolling_mean_7` | float | Mean of the prior 7 days, per cell |
| `rolling_mean_14` | float | Mean of the prior 14 days, per cell |

Lag and rolling features are computed strictly within each
(borough, complaint_group) group using only past observations, and rolling means
are shifted by one day so no same-day or future information leaks into a feature.

## Synthetic fallback generation logic

When `synthetic_fallback` is active, raw data is generated deterministically
(seed 42) for roughly three years across all 35 borough x complaint-group cells,
yielding well over 10,000 processed rows. The generating process combines:

- a borough activity factor and a complaint-group base level,
- yearly seasonality with a group-specific phase,
- weekly patterns (for example, elevated noise complaints on weekends),
- weather effects (precipitation, temperature, and severe-weather sensitivities
  that differ by complaint group),
- an event-intensity effect,
- a one-day **aftermath effect** so that a storm or major event today also
  elevates requests the following day, giving same-day public signals genuine
  predictive information about the next-day target,
- Poisson sampling so that counts are integer, observation-style values with
  noise rather than a deterministic function of the features.

The target `request_volume_next_day` is then derived by shifting the observed
`request_volume` one day forward within each cell. It is therefore an
observed-style next-day value, not a direct copy or deterministic transform of
the same-day features.

## Limitations

- Synthetic data reflects an assumed generating process; results characterize
  that process, not real-world demand.
- The synthetic weather and event signals are stylized proxies, not measured
  observations.
- The single-city, daily, borough x complaint-group scope is intentionally
  narrow and limits external validity.

## Privacy statement

No personal data, no individual-level records, and no personally identifiable
information are used or generated. All quantities are aggregate daily counts and
synthetic or public-style signals. The repository uses no authentication, no
geocoding, and no private data.
