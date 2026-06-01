# Public-Data Feature Augmentation for Municipal Service-Request Forecasting: From Forecast Accuracy to Stylized Staffing Decisions

## Abstract

We study whether augmenting an internal-history forecasting model with public
external signals improves next-day forecasts of municipal service-request volume,
and whether any forecast improvement carries through to a stylized staffing
allocation. Using real New York City 311 Service Requests for calendar years
2022-2024 (9,851,452 raw records aggregated to 43,240 date x borough x
complaint-group observations) and real NOAA daily weather for the NYC Central
Park station, we compare four feature sets - internal-historical,
calendar-augmented, weather-augmented, and calendar+weather-augmented - across
four model families under a strictly chronological protocol with rolling-origin
validation. Calendar features deliver the largest accuracy gain; real weather
adds a smaller but consistent further improvement. The best model
(random forest, calendar+weather) attains a held-out test MAE of 55.33 versus
71.85 for a naive seasonal baseline (a 23.0% reduction). A stylized
proportional staffing simulation shows the augmented forecast reduces weighted
unmet demand and closes 26.4% of the gap to an oracle at the baseline crew
budget, but the size of the decision benefit depends strongly on the crew
budget. The work is a reproducible research baseline; it makes no causal,
production, or real-dispatch claims.

## 1. Introduction

Short-horizon forecasts of service-request volume are a natural input to
staffing and dispatch planning. A standard question is whether public external
signals add predictive value beyond an organization's own request history, and a
distinct question is whether better forecasts actually improve downstream
operational decisions, which depends on the loss structure of the allocation
problem rather than on average accuracy alone. This paper addresses both
questions on real public data. The contribution is deliberately scoped: it is a
first research artifact / workshop-style study, not a full paper, and it reports
an honest, attenuated forecast-to-decision transfer rather than an operational
optimization.

## 2. Data

Two real public sources are used, both observed (no synthetic data):

- **NYC 311 Service Requests** (NYC Open Data, dataset `erm2-nwe9`), 2022-2024.
  From 9,851,452 raw records, 9,838,988 remain after filtering to the five
  valid boroughs and the study window. Records are mapped to eight complaint
  groups by a deterministic substring rule and aggregated to daily counts,
  yielding a 43,240-row date x borough x complaint-group panel over observed
  dates 2022-01-15 to 2024-12-30 (after lag/rolling warmup).
- **NOAA NCEI Daily Summaries (GHCN-Daily)**, station USW00094728
  (NY City Central Park), 2022-2024, 1,096 days. Variables used:
  precipitation, daily maximum and minimum temperature, snowfall, snow depth,
  and average wind speed. The source `TAVG` column was empty for this station,
  so a documented `temp_avg` is derived as the mean of the observed daily
  maximum and minimum; no other variable is derived. Five missing wind-speed
  days are filled by time interpolation of neighbouring real observations. A
  single Central Park station is used as a city-level proxy, a documented
  spatial-resolution limitation.

The forecasting target is the observed next-day request volume per cell,
computed only when consecutive calendar days are present.

## 3. Methods

Four feature sets are compared:

1. **internal_historical**: borough, complaint group, and lag/rolling statistics
   (lag-1, lag-7, rolling mean and standard deviation over 7 and 14 days).
2. **calendar_augmented**: internal plus deterministic calendar features
   (weekend, holiday, day-of-week, month, quarter, year, day-of-year,
   week-of-year, month-start, month-end).
3. **weather_augmented**: internal plus the seven real weather variables.
4. **calendar_weather_augmented**: internal plus calendar plus weather.

Four model families are evaluated: a naive seasonal baseline (trailing 7-day
mean), Ridge regression, a random forest, and gradient boosting. Lag/rolling
features use only past observations; rolling statistics are shifted by one day.
Validation uses a strictly chronological split by date (70% train, 15%
validation, 15% test) and, separately, five expanding-window rolling-origin
folds. The primary metric is MAE; RMSE, MAPE (safe zero handling), and R-squared
are also reported. The best configuration by validation MAE is refit on
train+validation before final test evaluation.

## 4. Results

### 4.1 Forecast accuracy (single chronological split, test MAE)

| Model | internal | calendar | weather | calendar+weather |
|-------|---------:|---------:|--------:|-----------------:|
| naive_seasonal | 71.848 | - | - | - |
| ridge | 69.219 | 68.758 | 69.283 | 68.915 |
| random_forest | 65.282 | 58.082 | 64.104 | 56.224 |
| gradient_boosting | 67.493 | 61.710 | 67.553 | 61.878 |

The selected model is the random forest on the calendar+weather feature set.
Refit on train+validation, its held-out test metrics are **MAE 55.33, RMSE
177.48, MAPE 27.47%, R-squared 0.648**, a 23.0% MAE reduction over the naive
seasonal baseline (71.85).

Two findings stand out. Calendar features provide the dominant gain
(random forest 65.28 to 58.08, about 11%). Real weather provides a smaller,
consistent further gain: weather alone improves the random forest over internal
(65.28 to 64.10), and adding weather on top of calendar improves it further
(58.08 to 56.22). Linear Ridge does not benefit, consistent with weather and
calendar effects being non-linear and interacting, which tree ensembles capture.

### 4.2 Rolling-origin validation (mean test MAE across 5 folds)

| Configuration | mean MAE | std |
|---------------|---------:|----:|
| random_forest calendar_weather_augmented | 47.50 | 8.75 |
| random_forest calendar_augmented | 48.69 | 9.59 |
| random_forest weather_augmented | 56.22 | 7.56 |
| random_forest internal_historical | 57.03 | 8.05 |
| naive_seasonal | 61.70 | 9.67 |

Across all five folds, calendar augmentation improves every model
(random forest mean +15.1%, gradient boosting +9.9%, Ridge +0.9%; each 5/5
folds), and calendar+weather is the lowest-error configuration on average. The
ordering is stable, not a single-split artifact.

### 4.3 Robustness by segment (best model, held-out test)

Augmentation improves MAE for **all 5 boroughs** (improvement range about
8.8% to 18.8%) and **all 8 complaint groups** (about 8.9% to 25.8%). Absolute
error concentrates in the highest-volume segments (Noise, Housing; the Bronx).

## 5. Forecast-to-decision simulation

A stylized staffing simulation allocates a fixed, scarce crew budget across
cells each day in proportion to the forecast (largest-remainder rule). Unmet
demand in a cell is the positive part of actual demand minus allocated capacity;
weighted unmet demand assigns higher weight to Public Safety, Water, and
Traffic. Policies driven by each feature set are compared against an oracle that
allocates on true next-day demand.

At the baseline budget (135 crews, 50 requests/crew), total weighted unmet
demand falls from 643,324 (internal) to 631,191 (calendar+weather), versus an
oracle of 597,332 - a **1.89% reduction** that closes **26.4%** of the
baseline-to-oracle gap. Weather-only (641,382) helps less than calendar-only
(634,614); calendar+weather is best among non-oracle policies.

Across crew budgets the augmented policy is better in **all three** settings,
but the magnitude is budget-dependent: weighted-unmet reduction is 0.38% (scarce,
100 crews), 4.32% (moderate, 160), and 14.53% (generous, 220); the oracle gap
closed ranges about 21% to 27%. The direction is consistent; the size is not.

## 6. Why forecast accuracy alone is insufficient

The headline contrast is between an approximately 11-15% forecast-accuracy gain
and a roughly 1.9% decision-quality gain at the baseline budget. Average MAE
weights all errors equally; the allocation does not, and a scarce budget plus
demand concentrated in a few large cells caps how much any forecast can help.
Reporting forecast metrics, decision metrics, and an oracle bound together gives
a more honest account of operational value than accuracy alone.

## 7. Limitations

The study is correlational and makes no causal claim. NYC 311 reflects reporting
behaviour, not true incidence (reporting bias), so forecasts predict reported
volume. Weather is a single-station city-level proxy. Borough-level aggregation
hides within-borough variation; the complaint-group mapping is a deterministic
approximation with a residual "Other" group. The staffing simulation is a
stylized proportional heuristic - not real dispatch, not staffing optimization,
not validated against any real policy - and omits crew travel, shifts, backlog,
intra-day timing, and substitution. Results apply to NYC, daily granularity, and
2022-2024 only.

## 8. Conclusion

On real NYC 311 data augmented with real NOAA weather, public-signal
augmentation consistently improves next-day forecast accuracy - calendar most,
weather a smaller consistent increment on top - across rolling folds, boroughs,
and complaint groups. The improvement transfers in direction to a stylized
staffing allocation but with attenuated, budget-dependent magnitude. The
artifact is suitable as a workshop / short-paper contribution and a reproducible
baseline. It is not full-paper-worthy without a non-stylized decision model,
formal forecast-difference testing, and broader external signals and cities.

## 9. Reproducibility note

All results are produced by the repository pipeline from the committed real
inputs: `python -m src.weather`, `python -m src.build_dataset`,
`python -m src.train`, `python -m src.evaluate`, `python -m src.decision_simulation`,
`python -m src.rolling_validation`, `python -m src.robustness_analysis`,
`python -m src.decision_sensitivity`, and `python -m src.practical_significance`.
Numbers in this draft are read from `reports/` and `data/metadata/`. Tests run
offline on a committed real-schema sample (`pytest`), and continuous integration
runs the pipeline in that sample mode. No synthetic data and no synthetic
weather are used anywhere.
