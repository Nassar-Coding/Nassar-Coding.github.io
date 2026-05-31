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

Two feature sets are compared under identical models and an identical validation
protocol:

- Internal historical: borough, complaint_group, request_lag_1, request_lag_7,
  rolling_mean_7, rolling_mean_14, rolling_std_7, rolling_std_14.
- Calendar augmented: all internal-historical features plus is_weekend,
  is_holiday, day_of_week, month, quarter, year, day_of_year, week_of_year,
  is_month_start, is_month_end.

No external weather, transit, or event data is used in this version, so the
comparison is framed as internal-historical versus calendar-augmented, not as
external-signal augmentation. Lag and rolling features are computed per cell using
only past observations, with rolling statistics shifted by one day to avoid
same-day or future leakage.

## 8. Model comparison

Four model families are evaluated: a naive seasonal baseline (trailing 7-day
rolling mean), Ridge regression, a random forest regressor, and a gradient
boosting regressor. Each non-naive model is trained on both feature sets. The
validation protocol is a strictly chronological split by date: earliest 70% of
dates for training (30,240 rows), next 15% for validation (6,480 rows), and
latest 15% for test (6,520 rows). The primary selection metric is mean absolute
error (MAE). The best model is selected by validation MAE and refit on the
combined train+validation partitions before final test evaluation.

## 9. Main empirical result

The selected model is a random forest on the calendar-augmented feature set. On
the held-out test partition it achieves MAE 57.26, RMSE 182.21, MAPE 28.05%, and
R-squared 0.629. The naive seasonal baseline has test MAE 71.85, so the selected
model improves on it by 20.3%.

Calendar augmentation improves every model relative to its internal-historical
counterpart on test MAE: random forest 65.28 to 58.08 (11.03% improvement),
gradient boosting 67.49 to 61.71 (8.57%), and Ridge 69.22 to 68.76 (0.67%). The
gain is largest for the tree ensembles, which can exploit calendar structure
interactively.

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
and Traffic. Three policies are compared over 163 test days: a baseline driven by
the internal-historical forecast, a calendar-augmented policy, and an oracle
policy driven by true next-day demand (an upper-bound benchmark only).

## 11. Decision simulation result

Total weighted unmet demand is 643,324.5 under the baseline policy, 634,613.5
under the calendar-augmented policy, and 597,332.0 under the oracle. The
calendar-augmented policy reduces weighted unmet demand by 1.35% relative to the
baseline and closes 18.94% of the baseline-to-oracle gap. Total (unweighted)
unmet demand and average service shortfall move in the same direction
(551,381 to 543,322; 84.57 to 83.33 per cell-day), and allocation efficiency
rises slightly (0.955 to 0.962). The high-demand coverage rate remains low under
all non-oracle policies, indicating that the scarce budget cannot cover peak
cells regardless of forecast.

The key qualitative finding is that the direction is consistent - better
forecasts yield better allocation outcomes here - but the decision-quality gain
(about 1.35%) is much smaller than the forecast-accuracy gain (about 11% for the
best model). This is exactly the forecast-versus-decision distinction the project
is designed to expose.

## 11b. Robustness package

A closure-pass robustness package tests whether the forecasting result is stable
beyond the single split. Five-fold expanding-window rolling-origin validation
shows calendar augmentation lowering MAE in every fold for every model (random
forest mean improvement 15.13%, gradient boosting 9.94%, Ridge 0.94%; each 5 of
5 folds). Segmented evaluation on the held-out test partition shows the
improvement holds for all five boroughs (about 4.7% to 15.8%) and all eight
complaint groups (about 5.8% to 25.7%). Decision sensitivity across scarce
(100 crews), moderate (160), and generous (220) budgets shows the
calendar-augmented policy is better in all three, but the weighted-unmet
reduction is budget-dependent (0.21%, 3.19%, 12.05% respectively). The
practical-significance summary records the forecasting evidence as strong and
the decision evidence as directionally consistent but budget-dependent, and
therefore not strong enough for full-paper drafting. The final phase decision is
recorded in `candidate_c_final_decision.md`.

## 12. What the project can claim

- It uses real, observed NYC 311 data for 2022-2024 with a documented,
  reproducible aggregation and no synthetic data.
- Under a leakage-controlled chronological protocol, calendar augmentation
  reduces next-day forecast error for every model evaluated, and most for the
  best (random forest) model.
- A transparent, stylized allocation simulation shows that this forecast
  improvement produces a small but consistent improvement in a weighted
  unmet-demand decision metric, closing about a fifth of the gap to an oracle.

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

- Add genuinely external, no-key public signals (for example weather) with full
  documentation, and re-run the same internal-versus-augmented comparison.
- Replace the single split with rolling-origin evaluation and add formal tests
  for forecast-accuracy differences (for example Diebold-Mariano) and for
  decision-quality differences across policies.
- Extend the decision layer from a proportional heuristic toward a constrained
  allocation with explicit service-level targets, and study sensitivity to the
  crew budget and complaint-group weights.
- Probe reporting bias and consider finer geography (community district or ZIP)
  while preserving the no-personal-data boundary.
