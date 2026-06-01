# Model Card

## Forecasting task

Predict observed next-day service-request volume (`request_volume_next_day`) for
each date x borough x complaint_group cell, using real NYC 311 data for
2022-2024. This is a supervised regression problem on a daily panel.

## Observed target

The target is the observed count of real 311 requests on the next calendar day
for the same cell. It is not simulated or synthetic. It is only defined when the
next row in the sorted per-cell series is exactly one calendar day later, which
prevents misalignment across any gaps.

## Feature sets

- **Internal historical:** `borough`, `complaint_group`, `request_lag_1`,
  `request_lag_7`, `rolling_mean_7`, `rolling_mean_14`, `rolling_std_7`,
  `rolling_std_14`.
- **Calendar augmented:** all internal-historical features plus `is_weekend`,
  `is_holiday`, `day_of_week`, `month`, `quarter`, `year`, `day_of_year`,
  `week_of_year`, `is_month_start`, `is_month_end`.
- **Weather augmented:** all internal-historical features plus real NOAA daily
  weather (`precipitation_mm`, `temp_max_c`, `temp_min_c`, `temp_avg_c`,
  `snowfall_mm`, `snow_depth_mm`, `wind_speed_ms`).
- **Calendar + weather augmented:** internal-historical plus both calendar and
  real weather features.

The weather layer is a genuinely external public signal: real NOAA NCEI Daily
Summaries (GHCN-Daily) for the NYC Central Park station (USW00094728), used as a
single-station city-level proxy. No transit or event data is included, and no
synthetic weather is generated. Calendar is the dominant signal; real weather
adds a smaller but consistent further gain on top of calendar.

Categorical features (`borough`, `complaint_group`) are one-hot encoded inside a
scikit-learn pipeline; numeric features pass through. The encoder and estimator
are bundled in one pipeline so the saved model scores raw feature records.

## Models

- Naive seasonal baseline (trailing 7-day rolling mean)
- Ridge regression
- Random forest regressor
- Gradient boosting regressor

Each non-naive model is trained on every available feature set.

## Metrics

MAE (primary selection metric), RMSE, MAPE (with safe handling of zero/near-zero
actuals via a clamped denominator), and R-squared.

## Validation design

A strictly chronological split prevents leakage: the earliest 70% of dates form
the training set, the next 15% the validation set, and the latest 15% the test
set. Cut points are defined on the sorted sequence of unique dates, so no date
appears in more than one partition and no later date informs an earlier
partition. Lag and rolling features are computed per cell from past observations
only. The best model is selected by validation MAE and refit on the combined
train+validation partitions before final test evaluation.

For the committed full real dataset the resulting partitions span approximately:
training 2022-01-15 to 2024-02-09, validation 2024-02-10 to 2024-07-20, and test
2024-07-21 to 2024-12-30.

## Selected model

The best (model, feature-set) combination is chosen automatically by validation
MAE and persisted to `models/best_forecast_model.joblib`. On the full real
dataset the selected model is the random forest on the calendar-augmented
feature set. The full comparison table and per-segment error breakdowns are
recorded in `reports/metrics.json` and `reports/evaluation_report.json`. Metric
values are produced at run time and reported there rather than asserted here.

## Intended use

- A reproducible real-data research baseline for whether calendar/temporal
  features improve next-day service-request forecasts.
- A scoping artifact and starting point for further experimentation.
- Local, offline experimentation and education.

## Out-of-scope use

- Real operational dispatch, staffing, or resource allocation.
- Any decision affecting individuals or public services without human oversight
  and independent validation.
- Causal claims about the effect of calendar or temporal factors on real demand.
- Production deployment; the repository is a local-only baseline and is not
  production-hardened, validated against real operations, or integrated with any
  external system.
