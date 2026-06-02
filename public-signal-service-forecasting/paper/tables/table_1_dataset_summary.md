# Table 1: Dataset Summary

Source: `data/metadata/data_source_report.json` and
`data/metadata/weather_source_report.json`.

## Service-request data

| Property | Value |
|----------|-------|
| Source | NYC 311 Service Requests (NYC Open Data, dataset `erm2-nwe9`) |
| Data mode | real_nyc_311 (no synthetic data; no synthetic fallback) |
| Study window | 2022-01-01 to 2024-12-31 |
| Raw records | 9,851,452 |
| Processed rows | 43,240 |
| Observed date range (processed) | 2022-01-15 to 2024-12-30 |
| Unit of analysis | date x borough x complaint_group |
| Target | request_volume_next_day (observed next-day count) |
| Boroughs (5) | Bronx, Brooklyn, Manhattan, Queens, Staten Island |
| Complaint groups (8) | Housing, Noise, Other, Public Safety, Sanitation, Street Condition, Traffic, Water |

## Weather data

| Property | Value |
|----------|-------|
| Source | NOAA NCEI Daily Summaries (GHCN-Daily) |
| Station | USW00094728 (NY City Central Park) |
| Spatial treatment | single-station city-level proxy |
| Study window | 2022-01-01 to 2024-12-31 |
| Daily rows | 1,096 |
| Variables used (7) | precipitation_mm, temp_max_c, temp_min_c, temp_avg_c, snowfall_mm, snow_depth_mm, wind_speed_ms |
| Derived variable | temp_avg_c (mean of observed TMAX/TMIN; source TAVG empty) |
| Short gaps interpolated | wind_speed_ms: 5 days (all others: 0) |
| Synthetic weather | none |

The study uses only real observed data. No synthetic data and no synthetic
weather are used.
