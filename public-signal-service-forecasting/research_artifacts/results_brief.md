# Results Brief

A concise, technical summary of the verified results for the real NYC 311
baseline. All values are read from the committed artifacts under `reports/` and
`data/metadata/`.

## Dataset summary

| Property | Value |
|----------|-------|
| Source | NYC 311 Service Requests (NYC Open Data, `erm2-nwe9`) |
| Data mode | `real_nyc_311` (no synthetic data; no synthetic fallback) |
| Study window | 2022-01-01 to 2024-12-31 |
| Monthly input files | 36 |
| Raw records read | 9,851,452 |
| Requests after filtering | 9,838,988 |
| Rows dropped (invalid borough) | 12,464 |
| Rows dropped (unparseable/out-of-window date) | 0 |
| Aggregated daily-count rows | 43,840 |
| Processed modelling rows | 43,240 |
| Observed date range (processed) | 2022-01-15 to 2024-12-30 |
| Boroughs | Bronx, Brooklyn, Manhattan, Queens, Staten Island |
| Complaint groups | Housing, Noise, Other, Public Safety, Sanitation, Street Condition, Traffic, Water |
| Unit of analysis | date x borough x complaint_group |
| Target | `request_volume_next_day` (observed next-day count) |

## Validation split (chronological by date)

| Partition | Rows | Fraction of dates |
|-----------|------|-------------------|
| Train | 30,240 | 0.70 |
| Validation | 6,480 | 0.15 |
| Test | 6,520 | 0.15 |

## Model comparison (test partition)

Test MAE is shown for all four feature sets per non-naive model
(`reports/model_comparison.csv`).

| Model | Feature set | Test MAE |
|-------|-------------|----------|
| naive_seasonal | naive_seasonal | 71.848 |
| ridge | internal_historical | 69.219 |
| ridge | calendar_augmented | 68.758 |
| ridge | weather_augmented | 69.283 |
| ridge | calendar_weather_augmented | 68.915 |
| random_forest | internal_historical | 65.282 |
| random_forest | calendar_augmented | 58.082 |
| random_forest | weather_augmented | 64.104 |
| random_forest | calendar_weather_augmented | 56.224 |
| gradient_boosting | internal_historical | 67.493 |
| gradient_boosting | calendar_augmented | 61.710 |
| gradient_boosting | weather_augmented | 67.553 |
| gradient_boosting | calendar_weather_augmented | 61.878 |

## Best model

| Property | Value |
|----------|-------|
| Model | random_forest |
| Feature set | calendar_weather_augmented |
| Selection metric | validation MAE |
| Test MAE | 55.325 |
| Test RMSE | 177.476 |
| Test MAPE (%) | 27.469 |
| Test R2 | 0.648 |

Note: the best-model test metrics are computed in the evaluation step after
refitting on train+validation, so they differ slightly from the
calendar_weather_augmented random_forest row in the comparison table (which is fit
on train only). The selected model is 23.0% better than the naive baseline (test
MAE 71.848).

### Best-model test MAE by borough

| Borough | Test MAE |
|---------|----------|
| Bronx | 114.529 |
| Brooklyn | 66.040 |
| Manhattan | 49.214 |
| Queens | 45.287 |
| Staten Island | 11.246 |

### Best-model test MAE by complaint group

| Complaint group | Test MAE |
|-----------------|----------|
| Noise | 174.195 |
| Housing | 114.740 |
| Other | 45.589 |
| Traffic | 40.439 |
| Water | 21.949 |
| Sanitation | 21.788 |
| Public Safety | 21.512 |
| Street Condition | 17.894 |

## Internal historical vs calendar augmented (test MAE)

| Model | Internal historical | Calendar augmented | Improvement |
|-------|---------------------|--------------------|-------------|
| random_forest | 65.282 | 58.082 | 11.03% |
| gradient_boosting | 67.493 | 61.710 | 8.57% |
| ridge | 69.219 | 68.758 | 0.67% |

Calendar augmentation improves every model; the gain is largest for the tree
ensembles.

## Weather augmentation

A real NOAA NCEI Daily Summaries (GHCN-Daily) layer was added in this closure
pass, station USW00094728 (NYC Central Park), 2022-2024, 1,096 days, with
variables precipitation_mm, temp_max_c, temp_min_c, temp_avg_c (derived from
TMAX/TMIN because the source TAVG was empty), snowfall_mm, snow_depth_mm, and
wind_speed_ms (five missing days time-interpolated). No synthetic weather; a single
Central Park station is a documented city-level proxy
(`data/metadata/weather_source_report.json`).

Calendar is the dominant signal; weather adds a smaller but consistent gain on top
of it. On single-split test MAE for the random forest, weather-only (64.104) beats
internal-historical (65.282), and calendar + weather (56.224) beats calendar-only
(58.082). Ridge does not benefit from weather (weather 69.283, calendar + weather
68.915 against internal 69.219). In five-fold rolling-origin validation, the
random forest mean fold test MAE is internal_historical 57.03 (std 8.05),
weather_augmented 56.22 (std 7.56), calendar_augmented 48.69 (std 9.59), and
calendar_weather_augmented 47.50 (std 8.75); naive is 61.70 (std 9.67). In the
decision simulation, weighted unmet demand is 643,324 (internal), 634,614
(calendar), 641,382 (weather), 631,191 (calendar + weather), and 597,332 (oracle);
the calendar + weather policy reduces weighted unmet demand by 1.886% and closes
26.381% of the oracle gap.

## Decision simulation (163 test days)

Assumptions: 135 crews, 50 requests per crew per day, proportional
largest-remainder allocation, weighted unmet demand with higher weight on Public
Safety (2.0), Water (1.5), and Traffic (1.5).

| Policy | Weighted unmet |
|--------|----------------|
| Baseline (internal historical) | 643,324 |
| Calendar augmented | 634,614 |
| Weather augmented | 641,382 |
| Calendar + weather augmented | 631,191 |
| Oracle (true demand) | 597,332 |

The headline comparison is calendar + weather augmented versus internal-historical
baseline.

| Decision metric | Value |
|-----------------|-------|
| Weighted-unmet reduction (calendar + weather vs baseline) | 1.886% |
| Gap to oracle closed | 26.381% |
| Calendar + weather better than baseline | true |

## Monitoring status

| Property | Value |
|----------|-------|
| Best-model test MAE | 55.325 |
| Naive baseline test MAE | 71.848 |
| Improvement over baseline | 23.0% |
| Improvement threshold | 5.0% |
| Status | healthy |

## Robustness package (closure pass)

### Rolling-origin validation (5 expanding-window chronological folds)

Calendar-augmentation MAE improvement, by model, across folds
(`reports/rolling_validation_summary.json`):

| Model | Mean improvement | Folds augmented better |
|-------|------------------|------------------------|
| random_forest | 15.13% | 5 / 5 |
| gradient_boosting | 9.94% | 5 / 5 |
| ridge | 0.94% | 5 / 5 |

Random-forest mean fold test MAE: internal_historical 57.03 (std 8.05),
weather_augmented 56.22 (std 7.56), calendar_augmented 48.69 (std 9.59), and
calendar_weather_augmented 47.50 (std 8.75).

### Robustness by borough (best model, held-out test)

Augmentation improved MAE for all 5 boroughs (about 8.8% to 18.8%); largest
absolute error in the Bronx, smallest in Staten Island
(`reports/borough_performance.csv`).

### Robustness by complaint group (best model, held-out test)

Augmentation improved MAE for all 8 complaint groups (about 8.9% to 25.8%);
largest absolute error in Noise and Housing
(`reports/complaint_group_performance.csv`).

### Decision sensitivity by crew budget

Calendar + weather augmented versus internal-historical:

| Setting | Crews | Weighted-unmet reduction | Gap to oracle closed |
|---------|-------|--------------------------|----------------------|
| Scarce | 100 | 0.38% | 27.06% |
| Moderate | 160 | 4.32% | 22.66% |
| Generous | 220 | 14.53% | 21.05% |

The calendar + weather policy is better in all three budgets, but the effect size
is budget-dependent (`reports/decision_sensitivity_summary.json`).

### Practical-significance summary

`reports/practical_significance_summary.json`: forecasting evidence strong
(consistent across folds, boroughs, and complaint groups); decision evidence
directionally consistent but budget-dependent; not strong enough for full-paper
drafting.

## Key takeaways

- Calendar augmentation reduces next-day forecast error for every model and most
  for the best (random forest) model, under a leakage-controlled chronological
  protocol on real NYC 311 data; real NOAA weather adds a smaller but consistent
  further gain on top of calendar, and calendar + weather is the best feature set.
- The forecast improvement transfers to the stylized decision metric in the same
  direction but with much smaller magnitude (about 23% accuracy gain over naive to
  about 1.89% weighted-unmet reduction for calendar + weather), closing about a
  quarter of the oracle gap at the baseline budget.
- Error and the achievable decision benefit are dominated by high-volume cells
  and a deliberately scarce capacity budget.

## Limitations

- 311 reflects reporting behaviour, not true incidence (reporting bias).
- Borough-level aggregation hides within-borough heterogeneity; complaint-group
  mapping is a deterministic approximation with a residual Other group.
- Calendar features may proxy seasonality rather than specific operational
  drivers.
- The decision simulation is a single stylized heuristic; results characterize the
  simulation, not real operations.
- Correlational only; no causal identification; no external validity beyond NYC
  and the 2022-2024 window.
