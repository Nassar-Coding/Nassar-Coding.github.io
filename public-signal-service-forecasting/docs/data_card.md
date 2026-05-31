# Data Card

## Summary

The modelling dataset is a daily panel indexed by date x borough x
complaint_group, built from real NYC 311 Service Requests for calendar years
2022-2024, with deterministic calendar features and leakage-safe lag/rolling
features. The active data mode is recorded in
`data/metadata/data_source_report.json`.

## Data source

- **Source:** NYC 311 Service Requests, NYC Open Data (Socrata dataset
  `erm2-nwe9`).
- **Study window:** 2022-01-01 to 2024-12-31 (calendar years 2022, 2023, 2024
  only). No 2025 data, no pre-2022 data, no partial years.
- **Acquisition:** the monthly NYC 311 exports are reduced locally to observed
  daily counts with `scripts/aggregate_nyc_311_local.py`, producing
  `data/raw/nyc_311_daily_counts_2022_2024.csv`. The pipeline consumes that
  file directly. A record-level export placed at
  `data/raw/nyc_311_2022_2024.csv` is also supported and aggregated in-process.

## Raw fields used

| Raw field | Use |
|-----------|-----|
| `created_date` | Parsed to the observation date; filtered to the study window |
| `borough` | Validated against the five NYC boroughs; normalised capitalisation |
| `complaint_type` | Mapped to a complaint_group (deterministic rules) |
| `unique_key` | Row identity during aggregation (counted as request volume) |

All other NYC 311 columns are intentionally not used in this baseline.

## Aggregation logic

For each (date, borough, complaint_group) cell the observed request count is the
number of 311 records created on that date in that borough whose complaint_type
maps to that group. Counts are summed across the monthly files. Absent
(date, borough, complaint_group) rows mean zero observed requests that day; the
build reindexes each cell to a complete daily grid and fills missing days with
zero, which makes the panel regular without fabricating demand.

The next-day target `request_volume_next_day` is the observed request volume on
the following calendar day for the same cell. It is only defined when the next
row in the sorted per-cell series is exactly one day later.

## Complaint grouping logic

`complaint_type` is mapped to one of eight groups with deterministic,
order-sensitive substring rules (first match wins): Noise, Housing, Sanitation,
Street Condition, Water, Traffic, Public Safety, and a catch-all Other. Housing
is evaluated before Water so that "HEAT/HOT WATER" is classified as Housing
rather than being captured by the "WATER" substring under Water. The mapping is
implemented identically in `scripts/aggregate_nyc_311_local.py` (local
aggregation) and `src/config.py` / `src/build_dataset.py` (in-process
aggregation of a manual export).

## Borough handling

Only the five valid NYC boroughs are kept (Manhattan, Brooklyn, Queens, Bronx,
Staten Island). Rows with "Unspecified" or other invalid borough values are
dropped during aggregation and counted in the aggregation metadata.

## Schema

| Column | Type | Description |
|--------|------|-------------|
| `date` | date | Observation date |
| `borough` | category | One of five boroughs |
| `complaint_group` | category | One of eight complaint groups |
| `request_volume` | float | Observed request count on `date` |
| `request_volume_next_day` | float | Target: observed request count on the next day |
| `is_weekend` | int | Weekend indicator (0/1) |
| `is_holiday` | int | US public-holiday indicator (0/1) |
| `day_of_week` | int | Day of week (Monday=0) |
| `month` | int | Calendar month (1-12) |
| `quarter` | int | Calendar quarter (1-4) |
| `year` | int | Calendar year |
| `request_lag_1` | float | Request volume on the previous day, per cell |
| `request_lag_7` | float | Request volume seven days prior, per cell |
| `rolling_mean_7` | float | Mean of the prior 7 days, per cell |
| `rolling_mean_14` | float | Mean of the prior 14 days, per cell |
| `rolling_std_7` | float | Std of the prior 7 days, per cell |
| `rolling_std_14` | float | Std of the prior 14 days, per cell |
| `day_of_year` | int | Day of year (1-366) |
| `week_of_year` | int | ISO week number |
| `is_month_start` | int | Month-start indicator (0/1) |
| `is_month_end` | int | Month-end indicator (0/1) |

Lag and rolling features are computed strictly within each (borough,
complaint_group) series using only past observations; rolling statistics are
shifted by one day so no same-day or future information leaks into a feature.

## No synthetic data

This project uses real observed NYC 311 data in research mode. It does not use
synthetic data, does not generate synthetic fallback data, and does not simulate
service-request demand. If valid real data is unavailable, the build fails with
a specific error rather than fabricating data.

## CI / sample-data distinction

A small committed real-schema sample, `data/raw/nyc_311_daily_counts_sample.csv`
(the first 120 days of the real observed counts), is used for tests and CI
(`USE_SAMPLE_DATA=1` or `DATA_MODE=sample_real_schema`). It preserves the real
schema and the observed-count target logic but is a reduced slice for speed and
reproducibility; it is labelled `sample_real_schema` in the data source report
and is not a source of research results.

## Privacy statement

No personal data, no individual-level records, and no personally identifiable
information are used. All quantities are aggregate daily counts by borough and
complaint group. The pipeline uses no authentication, no API keys, and no
geocoding.

## Limitations

- 311 reflects reporting behaviour, not true incidence (reporting bias).
- The complaint_type to complaint_group mapping is a deterministic
  approximation and groups heterogeneous types.
- Borough-level aggregation discards finer geography.
- See `docs/limitations.md` for the full list.
