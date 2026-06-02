# From Forecast Accuracy to Operational Value: Public Signal Augmentation for NYC 311 Service Demand

*Public Signal Service Forecasting; research line: Forecasting Service Demand
with Public Signals. This is an arXiv-style / workshop-style research artifact,
not a finished full paper. All empirical values are read from committed
repository artifacts under `reports/` and `data/metadata/`.*

## Abstract

Day-ahead forecasts of municipal service-request volume are a natural input to
staffing and dispatch planning, but a reduction in average forecast error does
not automatically translate into better operational decisions. We study, on real
data, whether public external signals improve next-day forecasts of NYC 311
service-request volume and whether any improvement carries through to a stylized
staffing-allocation simulation. Using real NYC 311 Service Requests for
2022-2024 (9,851,452 raw records aggregated to 43,240 date x borough x
complaint_group observations) and real NOAA Central Park daily weather, we
compare four feature sets - internal_historical, calendar_augmented,
weather_augmented, and calendar_weather_augmented - across four model families
under a strictly chronological protocol with five-fold rolling-origin
validation. Calendar features deliver the largest accuracy gain; real weather
adds a smaller but consistent further gain. The best model (random forest on
calendar_weather_augmented) attains a held-out test MAE of 55.325 versus 71.848
for a naive seasonal baseline, a 23.0% reduction. A stylized proportional
staffing simulation shows the augmented policy reduces weighted unmet demand at
every crew budget tested and closes 26.381% of the gap to an oracle at the
baseline budget, but the magnitude of the decision benefit is budget-dependent.
The work is a reproducible research baseline; it makes no causal, production, or
real-dispatch claims.

## 1. Introduction

Municipal service operations must plan finite crews against demand that varies by
day of week, season, and location. Short-horizon (next-day) volume forecasts are
a standard planning input. Two questions follow. First, a predictive question:
does augmenting an internal-history forecasting model with public external
signals reduce next-day forecast error? Second, a decision question: does any
such forecast improvement actually improve the quality of a capacity allocation
built on top of the forecast?

These questions are related but distinct. Mean absolute error (MAE) weights all
errors equally across cells and days. A capacity allocation does not: under a
fixed, scarce budget, an error on a high-volume or high-priority cell is more
consequential than an error on a quiet one, and a proportional allocation maps
forecasts to capacity non-linearly. A study reporting only forecast metrics can
therefore misstate operational relevance. We treat the decision layer as a
first-class evaluation target.

This artifact contributes a reproducible, real-data baseline on NYC 311 with
real NOAA weather, an honest four-way feature-set comparison, and a transparent
forecast-to-decision simulation whose limits are stated explicitly. It is
positioned as an arXiv/workshop-style artifact, not a full paper; the gating
items for a full paper are listed in the Limitations section.

## 2. Related Work

The methodological template is the demonstration that publicly available signals
can improve operational forecasts. Cui et al. [@cui2018operational] show, in a
retail setting, that public social-media information improves daily sales
forecasts across multiple machine-learning methods, with tree-based methods
extracting more value from heterogeneous public signals than linear methods, and
they frame the contribution as feature value rather than method novelty. Our work
is in this lineage but moves from retail to municipal service operations, uses
public weather rather than social media, and adds an explicit forecast-to-decision
layer rather than stopping at forecast accuracy.

Prediction-driven prioritization in public-service and scheduling settings has
also been studied from an equity and efficiency angle [@samorani2022TODO]. We do
not make equity or causal claims; we cite this line only to situate the general
concern that the objective on top of a predictive model, not the model alone,
shapes outcomes. (TODO: verify and complete this reference, or remove it, before
submission.)

## 3. Data

Two real public sources are used; no synthetic data and no synthetic weather are
used anywhere (Table 1).

**NYC 311 Service Requests** (NYC Open Data, dataset `erm2-nwe9`) [@nyc311],
2022-2024. From 9,851,452 raw records the pipeline produces a 43,240-row
date x borough x complaint_group panel spanning observed dates 2022-01-15 to
2024-12-30 (after lag and rolling warmup). Records are mapped to eight complaint
groups (Housing, Noise, Other, Public Safety, Sanitation, Street Condition,
Traffic, Water) by a deterministic substring rule and aggregated to daily counts
over the five NYC boroughs. The forecasting target is `request_volume_next_day`,
the observed next-day request count per cell, defined only when consecutive
calendar days are present.

**NOAA NCEI Daily Summaries (GHCN-Daily)** [@noaaghcnd], station USW00094728
(NY City Central Park), 2022-2024, 1,096 daily rows. Variables used:
precipitation, daily maximum and minimum temperature, average temperature,
snowfall, snow depth, and wind speed. The source average-temperature column was
empty for this station, so average temperature is derived as the mean of observed
daily maximum and minimum; five missing wind-speed days are filled by time
interpolation of neighbouring real observations. A single Central Park station is
used as a city-level proxy (a documented spatial-resolution limitation).

## 4. Methods

We compare four feature sets (Table 2): internal_historical (lag and rolling
statistics of the series), calendar_augmented (internal plus deterministic
calendar features), weather_augmented (internal plus the seven real weather
variables), and calendar_weather_augmented (internal plus calendar plus weather).

Four model families are evaluated: a naive seasonal baseline (trailing 7-day
mean), Ridge regression, a random forest, and gradient boosting. Categorical
features (borough, complaint_group) are one-hot encoded; numeric features pass
through. Lag and rolling features use only past observations, with rolling
statistics shifted by one day to avoid same-day or future leakage.

Validation uses a strictly chronological split by date: the earliest 70% of
dates for training (30,240 rows), the next 15% for validation (6,480 rows), and
the latest 15% for test (6,520 rows). The primary metric is MAE; RMSE, MAPE (with
safe handling of near-zero actuals), and R-squared are also reported. The best
configuration by validation MAE is refit on train+validation before the final
test evaluation. Separately, five expanding-window rolling-origin folds assess
stability.

The decision layer is a stylized staffing-allocation simulation. Each day a
fixed crew budget is distributed across cells in proportion to the forecast using
a largest-remainder rule. Unmet demand in a cell is the positive part of actual
demand minus allocated capacity; weighted unmet demand assigns higher weight to
Public Safety, Water, and Traffic. Policies driven by each feature set are
compared against an oracle that allocates on true next-day demand.

## 5. Forecasting Results

On the single chronological split (Table 3), calendar augmentation improves test
MAE for every model. For the random forest, MAE falls from 65.282
(internal_historical) to 58.082 (calendar_augmented). Real weather adds a smaller
consistent gain: weather_augmented (64.104) beats internal_historical (65.282),
and calendar_weather_augmented (56.224) beats calendar_augmented (58.082). Ridge
does not benefit from weather (internal 69.219; weather 69.283; calendar+weather
68.915).

The selected model is the random forest on calendar_weather_augmented. Refit on
train+validation, its held-out test metrics are MAE 55.325, RMSE 177.476, MAPE
27.469%, and R-squared 0.648 - a 23.0% MAE reduction over the naive seasonal
baseline (71.848). Figures 1 and 2 show forecast error by model/feature set and
the best test MAE per feature set; Figure 7 shows observed versus predicted
city-wide next-day totals over the test period; Figure 8 summarises the real
weather series.

## 6. Forecast-to-Decision Simulation

At the baseline budget (135 crews, 50 requests per crew, 163 test days; source
`reports/decision_simulation_report.json`), total weighted unmet demand is
643,324 under the internal-historical policy, 634,614 under calendar, 641,382
under weather, and 631,191 under calendar+weather, versus an oracle of 597,332.
The calendar+weather policy reduces weighted unmet demand by 1.886% and closes
26.381% of the baseline-to-oracle gap (Figure 9).

Across crew budgets (Table 7, Figure 6) the calendar+weather policy is better
than the baseline in all three settings, but the magnitude grows with capacity:
the weighted-unmet reduction is 0.38% (scarce, 100 crews), 4.32% (moderate, 160),
and 14.53% (generous, 220). The direction is consistent; the size is not. The
headline contrast - an approximately 11-15% forecast-accuracy gain versus a
roughly 1.9% decision-quality gain at the baseline budget - is the central
observation: average accuracy and operational value are not the same thing, and a
scarce budget with demand concentrated in a few large cells limits how much any
forecast can help.

## 7. Robustness Checks

Five-fold expanding-window rolling-origin validation (Table 4, Figure 3) shows
calendar augmentation lowering MAE in every fold for every model (random forest
mean +15.13%, gradient boosting +9.94%, Ridge +0.94%; each 5 of 5 folds), with
calendar_weather_augmented the lowest mean fold MAE (47.497) for the random
forest. Segmented analysis shows the random-forest improvement of calendar over
internal-historical holds for all five boroughs (about 8.8% to 18.8%; Table 5,
Figure 4) and all eight complaint groups (about 8.9% to 25.8%; Table 6,
Figure 5). Absolute error concentrates in the highest-volume segments (Noise,
Housing; the Bronx).

## 8. Limitations

The study is correlational and makes no causal claim. NYC 311 reflects reporting
behaviour, not true incidence (reporting bias), so forecasts predict reported
volume. Weather is a single Central Park station used as a city-level proxy.
Borough-level aggregation hides within-borough variation; the complaint-group
mapping is a deterministic approximation with a residual Other group. No transit
or event data is included in this version. The staffing simulation is a stylized
proportional heuristic - not real dispatch, not staffing optimization, not
validated against any real policy - and omits crew travel, shifts, backlog,
intra-day timing, and substitution; it uses no observed dispatch decisions.
Results apply to NYC and 2022-2024 only. Full details and mitigations are in
`paper/limitations.md` and Table 8.

Gating items for a full paper: a non-stylized, agency-grounded decision model
with an empirical service-level realism check; formal forecast-difference testing
(for example a Diebold-Mariano test) with uncertainty intervals; and broader
external signals beyond a single weather station, or cross-city replication.

## 9. Reproducibility

All values here are read from committed artifacts under `reports/` and
`data/metadata/`. The pipeline is run with `python -m src.weather`,
`python -m src.build_dataset`, `python -m src.train`, `python -m src.evaluate`,
`python -m src.decision_simulation`, `python -m src.monitor`,
`python -m src.rolling_validation`, `python -m src.robustness_analysis`,
`python -m src.decision_sensitivity`, and `python -m src.practical_significance`.
The quality gate is `ruff check .` and `pytest`, run offline on a committed
real-schema sample; continuous integration runs the pipeline in that sample mode.
No API keys or secrets are required. See `paper/reproducibility_statement.md` and
`paper/data_availability_statement.md`.

## 10. Conclusion

On real NYC 311 data augmented with real NOAA weather, public-signal augmentation
consistently improves next-day service-demand forecasts - calendar most, weather
a smaller consistent increment on top - across rolling folds, boroughs, and
complaint groups. The improvement transfers in direction to a stylized staffing
allocation but with attenuated, budget-dependent magnitude. The artifact is
suitable as a workshop / short-paper / arXiv-style contribution and a reproducible
baseline. It is not full-paper ready without a non-stylized decision model,
formal forecast-difference testing, and broader external signals or cities.
