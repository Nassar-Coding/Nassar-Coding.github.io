# Research Memo: Public Signal Service Forecasting

## 1. Research question

Can real NYC 311 service-request history, calendar features, and temporal lag
features forecast next-day service-request volume, and does an improvement in
forecast accuracy translate into a measurable improvement in a stylized staffing
allocation simulation?

## 2. Motivation

Municipal service organizations must allocate finite crews against demand that
is uncertain and time-varying. Day-ahead volume forecasts are a natural input to
short-horizon staffing and dispatch planning. A recurring methodological
question is whether adding structure to a forecasting model - here, deterministic
calendar and temporal features - improves prediction beyond an organization's own
internal request history, and, more importantly, whether any such predictive gain
actually changes downstream operational decisions for the better.

## 3. Why this is an operations problem, not only a forecasting problem

A lower average forecasting error does not, by itself, imply better operational
outcomes. Operational value depends on the loss structure of the downstream
decision: under a fixed and scarce capacity budget, errors on high-demand or
high-priority cells are far more costly than errors elsewhere, and a proportional
allocation rule transforms forecasts into capacity non-linearly. This project
therefore evaluates two distinct questions - forecast performance and stylized
allocation performance - rather than assuming the first determines the second.

## 4. Data and study window

The data is real NYC 311 Service Requests from NYC Open Data (Socrata dataset
`erm2-nwe9`), for calendar years 2022-2024 only. The monthly exports
(36 files) were reduced locally to observed daily counts; the pipeline read
9,851,452 raw records. After filtering to valid boroughs and the study window,
9,838,988 requests remained (12,464 rows dropped for invalid/unspecified
borough; 0 dropped for unparseable date or out-of-window date). No synthetic data
was used and no synthetic fallback exists in the pipeline.

A real weather layer was added in this closure pass. The source is NOAA NCEI
Daily Summaries (GHCN-Daily), station USW00094728 (NYC Central Park), for
2022-2024 (1,096 days). The variables used are precipitation_mm, temp_max_c,
temp_min_c, temp_avg_c, snowfall_mm, snow_depth_mm, and wind_speed_ms. Because the
source TAVG column was empty for this station, temp_avg_c is derived as the mean
of observed daily maximum and minimum temperature; five missing wind-speed days
are filled by time interpolation of neighbouring real observations. No synthetic
weather is generated. A single Central Park station is used as a city-level proxy,
which is a documented spatial-resolution limitation.

## 5. Unit of analysis

The unit of analysis is the cell defined by date x borough x complaint_group.
The processed modelling dataset has 43,240 rows spanning observed dates
2022-01-15 to 2024-12-30 (the first 14 days are consumed by lag and rolling
warmup, and the final day has no observed next day). It covers all five NYC
boroughs (Bronx, Brooklyn, Manhattan, Queens, Staten Island) and eight complaint
groups (Housing, Noise, Other, Public Safety, Sanitation, Street Condition,
Traffic, Water).

## 6. Target variable

The target is `request_volume_next_day`: the observed count of 311 requests on
the next calendar day for the same borough x complaint_group cell. It is computed
only from observed records and is defined only when the next row in the per-cell
series is exactly one calendar day later, which prevents misalignment across any
gaps in the panel.

## 7. Feature sets

Four feature sets are compared under identical models and an identical validation
protocol:

- Internal historical: borough, complaint_group, request_lag_1, request_lag_7,
  rolling_mean_7, rolling_mean_14, rolling_std_7, rolling_std_14.
- Calendar augmented: all internal-historical features plus is_weekend,
  is_holiday, day_of_week, month, quarter, year, day_of_year, week_of_year,
  is_month_start, is_month_end.
- Weather augmented: all internal-historical features plus the real NOAA daily
  weather variables (precipitation_mm, temp_max_c, temp_min_c, temp_avg_c,
  snowfall_mm, snow_depth_mm, wind_speed_ms).
- Calendar + weather augmented: all internal-historical features plus both the
  calendar and the weather variables.

No transit or event data is used in this version. The weather signal is the real
NOAA Central Park daily series described in the data section; it is a genuinely
external public signal rather than a derived calendar feature. Lag and rolling
features are computed per cell using only past observations, with rolling
statistics shifted by one day to avoid same-day or future leakage.

## 8. Model comparison

Four model families are evaluated: a naive seasonal baseline (trailing 7-day
rolling mean), Ridge regression, a random forest regressor, and a gradient
boosting regressor. Each non-naive model is trained on all four feature sets. The
validation protocol is a strictly chronological split by date: earliest 70% of
dates for training (30,240 rows), next 15% for validation (6,480 rows), and
latest 15% for test (6,520 rows). The primary selection metric is mean absolute
error (MAE). The best model is selected by validation MAE and refit on the
combined train+validation partitions before final test evaluation.

## 9. Main empirical result

The selected model is a random forest on the calendar + weather augmented feature
set. On the held-out test partition it achieves MAE 55.33, RMSE 177.48, MAPE
27.47%, and R-squared 0.648. The naive seasonal baseline has test MAE 71.85, so
the selected model improves on it by 23.0%.

Calendar augmentation improves every model relative to its internal-historical
counterpart on single-split test MAE: random forest 65.28 to 58.08, gradient
boosting 67.49 to 61.71, and Ridge 69.22 to 68.76. The gain is largest for the
tree ensembles, which can exploit calendar structure interactively. Calendar is
the dominant signal; real weather adds a smaller but consistent gain on top of
it. For the random forest, weather-only (64.10) beats internal-historical
(65.28), and calendar + weather (56.22) beats calendar-only (58.08); Ridge does
not benefit from weather (weather 69.28, calendar + weather 68.92 against internal
69.22).

Error is concentrated in the highest-volume cells: test MAE is largest for the
Noise (174.2) and Housing (114.7) complaint groups and for the Bronx (114.5),
and smallest for Staten Island (11.2) and low-volume groups such as Street
Condition (17.9) and Public Safety (21.5).

## 10. Forecast-to-decision link

To test whether the forecast improvement carries operational meaning, a stylized
staffing-allocation simulation distributes a fixed, intentionally scarce crew
budget across cells each day in proportion to the forecast, using a
largest-remainder rule. The configuration is 135 crews, each handling 50 requests
per day (capacity calibrated to roughly three quarters of mean daily demand).
Unmet demand in a cell is the positive part of actual demand minus allocated
capacity; weighted unmet demand assigns higher weight to Public Safety, Water,
and Traffic. Policies driven by each forecast feature set are compared over 163
test days against a baseline driven by the internal-historical forecast and an
oracle policy driven by true next-day demand (an upper-bound benchmark only). The
headline comparison is the calendar + weather augmented policy versus the
internal-historical baseline.

## 11. Decision simulation result

Total weighted unmet demand is 643,324 under the internal-historical baseline,
634,614 under the calendar-augmented policy, 641,382 under the weather-augmented
policy, 631,191 under the calendar + weather augmented policy, and 597,332 under
the oracle. The calendar + weather augmented policy reduces weighted unmet demand
by 1.886% relative to the baseline and closes 26.381% of the baseline-to-oracle
gap. The high-demand coverage rate remains low under all non-oracle policies,
indicating that the scarce budget cannot cover peak cells regardless of forecast.

The key qualitative finding is that the direction is consistent - better
forecasts yield better allocation outcomes here - but the decision-quality gain
(about 1.89% for the calendar + weather policy) is much smaller than the
forecast-accuracy gain (about 23% over the naive baseline). This is exactly the
forecast-versus-decision distinction the project is designed to expose.

## 11b. Robustness package

A closure-pass robustness package tests whether the forecasting result is stable
beyond the single split. Five-fold expanding-window rolling-origin validation
shows calendar augmentation lowering MAE in every fold for every model (random
forest mean improvement 15.1%, gradient boosting 9.9%, Ridge 0.9%; each 5 of
5 folds). In mean fold test MAE, the random forest improves from internal
(57.03, std 8.05) through weather (56.22, std 7.56) and calendar (48.69, std 9.59)
to calendar + weather (47.50, std 8.75); naive is 61.70 (std 9.67). Segmented
evaluation on the held-out test partition shows the improvement holds for all
five boroughs (about 8.8% to 18.8%) and all eight complaint groups (about 8.9%
to 25.8%); error concentrates in Noise, Housing, and the Bronx. Decision
sensitivity across scarce (100 crews), moderate (160), and generous (220) budgets
shows the calendar + weather policy is better than internal-historical in all
three, but the weighted-unmet reduction is budget-dependent (0.38%, 4.32%, 14.53%
respectively, closing 27.06%, 22.66%, and 21.05% of the oracle gap). The
practical-significance summary records the forecasting evidence as strong and
the decision evidence as directionally consistent but budget-dependent, and
therefore not strong enough for full-paper drafting. The final phase decision is
recorded in `final_research_decision.md`.

## 12. What the project can claim

- It uses real, observed NYC 311 data for 2022-2024 with a documented,
  reproducible aggregation and no synthetic data, plus a real NOAA Central Park
  daily weather layer with no synthetic weather.
- Under a leakage-controlled chronological protocol, calendar augmentation
  reduces next-day forecast error for every model evaluated, and most for the
  best (random forest) model; real weather adds a smaller but consistent further
  gain on top of calendar.
- A transparent, stylized allocation simulation shows that this forecast
  improvement produces a small but consistent improvement in a weighted
  unmet-demand decision metric: the calendar + weather policy closes about a
  quarter of the gap to an oracle at the baseline budget.

This memo reflects the weather-augmentation closure pass.

## 13. What the project cannot claim

- It cannot claim a causal effect of calendar factors on service demand.
- It cannot claim production readiness, real deployment, real dispatch impact,
  or real staffing optimization; the simulation is stylized.
- It cannot claim external validity beyond New York City, daily granularity, the
  eight mapped complaint groups, and the 2022-2024 window.
- It is not a finished paper.

## 14. Limitations

- NYC 311 records reflect reporting behaviour, not true incidence (reporting
  bias); forecasts of 311 volume are forecasts of reporting, not of need.
- Borough-level aggregation hides within-borough heterogeneity.
- The complaint-type to complaint_group mapping is a deterministic approximation
  with a residual "Other" group.
- Calendar features may proxy seasonality rather than specific operational
  drivers.
- The decision simulation is a single stylized heuristic and ignores crew travel,
  shifts, backlog carryover, intra-day arrivals, and substitution.
- A single chronological split provides one held-out estimate rather than a
  rolling-origin distribution.

## 15. Next research steps

- Extend the external-signal layer beyond a single weather station (for example
  multi-station or gridded weather) and add further no-key public signals, with
  full documentation.
- Replace the single split with rolling-origin evaluation and add formal tests
  for forecast-accuracy differences (for example Diebold-Mariano) and for
  decision-quality differences across policies.
- Extend the decision layer from a proportional heuristic toward a constrained
  allocation with explicit service-level targets, and study sensitivity to the
  crew budget and complaint-group weights.
- Probe reporting bias and consider finer geography (community district or ZIP)
  while preserving the no-personal-data boundary.
