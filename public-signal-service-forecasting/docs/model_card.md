# Model Card

## Forecasting task

Predict next-day service-request volume (`request_volume_next_day`) for each
date x borough x complaint-group cell. This is a supervised regression problem
on a daily panel.

## Feature sets

- **Internal-only:** `borough`, `complaint_group`, `day_of_week`, `month`,
  `is_weekend`, `is_holiday`, `request_lag_1`, `request_lag_7`, `rolling_mean_7`,
  `rolling_mean_14`.
- **Public-signal augmented:** all internal-only features plus `temp_c`,
  `precipitation_mm`, `wind_speed_kmh`, `severe_weather`, and `event_intensity`.

Categorical features (`borough`, `complaint_group`) are one-hot encoded inside a
scikit-learn pipeline; numeric features are passed through. Because the encoder
and estimator are bundled in one pipeline, the saved model can score raw feature
records directly.

The public-signal features represent forecastable, exogenous conditions aligned
with the prediction horizon. In the synthetic data-generating process, today's
weather and event signals influence both today's and the following day's volume
(an aftermath effect), so they carry legitimate predictive information about the
next-day target without leaking the target itself.

## Models

- **Naive seasonal baseline:** predicts the trailing 7-day rolling mean.
- **Ridge regression:** linear baseline with L2 regularization.
- **Random forest regressor.**
- **Gradient boosting regressor.**

Each non-naive model is trained on both feature sets.

## Metrics

- **MAE** (primary selection metric),
- **RMSE**,
- **MAPE** with safe handling of zero/near-zero actuals (denominator clamped),
- **R-squared**.

## Validation design

A strictly chronological split is used to prevent leakage of future information:
the earliest 70% of dates form the training set, the next 15% the validation set,
and the latest 15% the test set. Cut points are defined on the sorted sequence of
unique dates, so no date appears in more than one partition and no later date
informs an earlier partition. Lag and rolling features are computed per cell from
past observations only. The best model is selected by validation MAE and refit on
the combined train+validation partitions before final test evaluation.

## Selected model

The best (model, feature-set) combination is chosen automatically by validation
MAE and persisted to `models/best_forecast_model.joblib`. The selection, along
with the full comparison table and per-segment error breakdowns, is recorded in
`reports/metrics.json` and `reports/evaluation_report.json`. Concrete metric
values depend on the active data mode and are produced at run time rather than
asserted here.

## Intended use

- A reproducible research baseline for studying whether public signals improve
  service-request forecasts.
- A scoping artifact and starting point for further experimentation.
- Local, offline experimentation and education.

## Out-of-scope use

- Real operational dispatch, staffing, or resource allocation.
- Any decision affecting individuals or public services without human oversight
  and independent validation.
- Causal claims about the effect of weather or events on real service demand.
- Production deployment. The repository is a local-only baseline and is not
  production-hardened, validated against real operations, or integrated with any
  external system.
