# Appendix

Sources: `docs/model_card.md`, `docs/data_card.md`, `docs/decision_simulation.md`,
`docs/limitations.md`, `src/features.py`, `src/config.py`, and the report CSVs.

## A. Feature definitions

- request_lag_1, request_lag_7: request volume 1 and 7 days prior, per
  (borough, complaint_group) cell.
- rolling_mean_7, rolling_mean_14: mean of the prior 7 and 14 days, per cell.
- rolling_std_7, rolling_std_14: standard deviation of the prior 7 and 14 days,
  per cell.
- Calendar: is_weekend, is_holiday, day_of_week, month, quarter, year,
  day_of_year, week_of_year, is_month_start, is_month_end (deterministic from the
  date).
- Weather (real NOAA daily): precipitation_mm, temp_max_c, temp_min_c,
  temp_avg_c, snowfall_mm, snow_depth_mm, wind_speed_ms.

All lag and rolling features use only past observations; rolling statistics are
shifted by one day so a given date depends only on strictly prior days.

## B. Feature-set definitions

See Table 2. Four sets: internal_historical; calendar_augmented (internal +
calendar); weather_augmented (internal + weather); calendar_weather_augmented
(internal + calendar + weather).

## C. Complaint-group mapping summary

Raw NYC 311 complaint types are mapped by a deterministic, order-sensitive
substring rule into eight groups: Housing, Noise, Sanitation, Street Condition,
Water, Traffic, Public Safety, and a residual Other. The mapping is documented in
`docs/data_card.md`; a residual Other group absorbs unmatched types.

## D. Chronological split

Strictly chronological by date: earliest 70% of dates for training
(30,240 rows), next 15% for validation (6,480 rows), latest 15% for test
(6,520 rows). The selected model is refit on train+validation before final test
evaluation. Source: `reports/metrics.json` (split block).

## E. Rolling-origin validation setup

Five expanding-window folds. Each fold trains on all dates up to a cut point and
tests on the following block; no future information enters training. Per-fold and
summary metrics are in `reports/rolling_validation_report.csv` and
`reports/rolling_validation_summary.json` (Table 4).

## F. Decision simulation assumptions

Stylized proportional staffing allocation. Each day a fixed crew budget is
distributed across cells in proportion to the forecast via a largest-remainder
rule; each crew handles a fixed number of requests; unmet demand is the positive
part of actual minus allocated capacity; weighted unmet demand up-weights Public
Safety, Water, and Traffic. Baseline-budget configuration: 135 crews, 50 requests
per crew, 163 test days (`reports/decision_simulation_report.json`). Policies:
internal_historical, calendar_augmented, weather_augmented,
calendar_weather_augmented, and an oracle on true next-day demand. It is not real
dispatch and uses no observed dispatch decisions.

## G. Crew-budget sensitivity setup

Three budgets: scarce (100 crews, 5,000 daily capacity), moderate (160 crews,
8,000), generous (220 crews, 11,000). Metrics per policy and budget are in
`reports/decision_sensitivity_report.csv` and
`reports/decision_sensitivity_summary.json` (Table 7).

## H. Weather-data treatment

Single NOAA station (USW00094728, Central Park) joined to all boroughs by date.
temp_avg_c derived from observed TMAX/TMIN because source TAVG was empty; five
missing wind-speed days time-interpolated from real neighbours. No synthetic
weather. Provenance: `data/metadata/weather_source_report.json`.

## I. Robustness details

Segmented MAE by borough (`reports/borough_performance.csv`, Table 5) and by
complaint group (`reports/complaint_group_performance.csv`, Table 6), comparing
internal_historical vs calendar_augmented for the random forest. Rolling-origin
stability in Table 4.

## J. Reproducibility commands

```
python -m src.weather
python -m src.build_dataset
python -m src.train
python -m src.evaluate
python -m src.decision_simulation
python -m src.monitor
python -m src.rolling_validation
python -m src.robustness_analysis
python -m src.decision_sensitivity
python -m src.practical_significance
ruff check .
pytest
```
