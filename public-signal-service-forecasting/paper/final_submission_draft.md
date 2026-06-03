# From Forecast Accuracy to Operational Value: Public Signal Augmentation for NYC 311 Service Demand

*arXiv-style / workshop-style research artifact. The study is predictive and
correlational; it makes no causal, production-readiness, real-dispatch, or
full-paper-readiness claim. All empirical values are read from committed
repository artifacts under `reports/` and `data/metadata/`.*

## Abstract

Day-ahead forecasts of municipal service-request volume are a natural input to
staffing and dispatch planning, yet a reduction in average forecast error does
not automatically translate into better operational decisions. We ask, on real
data, two questions: do public external signals improve next-day forecasts of NYC
311 service-request volume, and does any improvement carry through to a stylized
staffing-allocation simulation? Using real NYC 311 Service Requests for 2022-2024
(9,851,452 raw records aggregated to 43,240 date x borough x complaint_group
observations) and real NOAA Central Park daily weather, we compare four feature
sets - internal_historical, calendar_augmented, weather_augmented, and
calendar_weather_augmented - across four model families under a strictly
chronological protocol with five-fold rolling-origin validation. Calendar
features deliver the largest accuracy gain; real weather adds a smaller but
consistent further gain. The best model, a random forest on
calendar_weather_augmented, attains a held-out test mean absolute error (MAE) of
55.325 versus 71.848 for a naive seasonal baseline, a 23.0% reduction. A stylized
proportional staffing simulation shows the augmented policy reduces weighted unmet
demand at every crew budget tested and closes 26.381% of the gap to an oracle at
the baseline budget, but the magnitude of the decision benefit is
budget-dependent. The central finding is that the forecast gains are real and
robust, while the decision gains are smaller and conditional on capacity. The work
is a reproducible baseline; no synthetic data or synthetic weather is used.

## 1. Introduction

Municipal service operations plan finite crews against demand that varies by day
of week, season, and location. Short-horizon (next-day) volume forecasts are a
standard planning input. Two questions follow. First, a predictive question: does
augmenting an internal-history forecasting model with public external signals
reduce next-day forecast error? Second, a decision question: does any such
forecast improvement actually improve the quality of a capacity allocation built
on top of the forecast?

These questions are related but distinct. Mean absolute error weights all errors
equally across cells and days. A capacity allocation does not: under a fixed,
scarce budget, an error on a high-volume or high-priority cell is more
consequential than an error on a quiet one, and a proportional allocation maps
forecasts to capacity non-linearly. A study reporting only forecast metrics can
therefore misstate operational relevance.

We make three contributions. (i) A reproducible, real-data baseline on NYC 311
augmented with real NOAA weather, with a leakage-controlled chronological
protocol. (ii) An honest four-way feature-set comparison isolating the marginal
value of calendar features and of real weather. (iii) A transparent
forecast-to-decision simulation that measures whether forecast gains transfer to
a stylized allocation, with the result reported as it is: directionally positive
but budget-dependent. The study is predictive and correlational and is positioned
as an arXiv/workshop artifact, not a full paper; gating items for a stronger paper
are stated in Section 8.

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

Prediction-driven prioritization in service and scheduling settings has been
studied from an equity and efficiency angle [@samorani2022overbooked]. We make no
equity or causal claim; we cite this line only to situate the general point that
the objective placed on top of a predictive model, not the model alone, shapes
outcomes - which motivates our separate evaluation of the decision layer.

## 3. Data

Two real public sources are used; no synthetic data and no synthetic weather are
used anywhere. Table 1 summarizes both.

**NYC 311 Service Requests** (NYC Open Data, Socrata dataset `erm2-nwe9`,
"311 Service Requests from 2010 to Present") [@nyc311], restricted to 2022-2024.
From 9,851,452 raw records the pipeline produces a 43,240-row
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
snowfall, snow depth, and wind speed. The source average-temperature field was
empty for this station, so average temperature is derived as the mean of observed
daily maximum and minimum; five missing wind-speed days are filled by time
interpolation of neighbouring real observations. A single Central Park station is
used as a city-level proxy, a documented spatial-resolution limitation.

**Table 1: Dataset summary.**

| Property | Value |
|----------|-------|
| Service data | NYC 311 Service Requests (NYC Open Data, `erm2-nwe9`) |
| Study window | 2022-01-01 to 2024-12-31 |
| Raw records | 9,851,452 |
| Processed rows | 43,240 (date x borough x complaint_group) |
| Observed range (processed) | 2022-01-15 to 2024-12-30 |
| Boroughs / complaint groups | 5 / 8 |
| Target | request_volume_next_day (observed next-day count) |
| Weather source | NOAA NCEI Daily Summaries (GHCN-Daily) |
| Weather station | USW00094728 (NY City Central Park); single-station proxy |
| Weather rows / variables | 1,096 / 7 |
| Synthetic data or weather | none |

## 4. Methods

We compare four feature sets: internal_historical (lag and rolling statistics of
the per-cell series), calendar_augmented (internal plus deterministic calendar
features), weather_augmented (internal plus the seven real weather variables), and
calendar_weather_augmented (internal plus calendar plus weather). Full feature
definitions are in Appendix A.

Four model families are evaluated: a naive seasonal baseline (trailing 7-day
mean), Ridge regression, a random forest, and gradient boosting. Categorical
features (borough, complaint_group) are one-hot encoded; numeric features pass
through. Lag and rolling features use only past observations, with rolling
statistics shifted by one day to avoid same-day or future leakage.

Validation uses a strictly chronological split by date: the earliest 70% of dates
for training (30,240 rows), the next 15% for validation (6,480 rows), and the
latest 15% for test (6,520 rows). The primary metric is MAE; RMSE, MAPE (with safe
handling of near-zero actuals), and R-squared are also reported. The best
configuration by validation MAE is refit on train+validation before the final
test evaluation. Separately, five expanding-window rolling-origin folds assess
stability.

The decision layer is a stylized staffing-allocation simulation. Each day a fixed
crew budget is distributed across cells in proportion to the forecast using a
largest-remainder rule. Each crew handles a fixed number of requests; unmet demand
in a cell is the positive part of actual demand minus allocated capacity; weighted
unmet demand assigns higher weight to Public Safety, Water, and Traffic. Policies
driven by each feature set are compared against an oracle that allocates on true
next-day demand (an upper bound only). Full assumptions are in Appendix D.

## 5. Forecasting Results

Calendar augmentation improves test MAE for every model, and real weather adds a
smaller consistent gain on top of it. For the random forest, MAE falls from 65.282
(internal_historical) to 58.082 (calendar_augmented); weather alone improves the
internal model (64.104 versus 65.282), and calendar+weather is best (56.224 on the
train-only fit). Ridge does not benefit from weather (internal 69.219, weather
69.283, calendar+weather 68.915). Figure 2 shows the best test MAE per feature
set; the full per-model results are in Table 3 (trimmed below; complete table in
Appendix G).

**Table 3 (selected rows): held-out test MAE by model and feature set.** Lower is
better. Full 13-row table in Appendix G.

| Model | Feature set | Test MAE |
|-------|-------------|---------:|
| naive_seasonal | naive_seasonal | 71.848 |
| random_forest | internal_historical | 65.282 |
| random_forest | calendar_augmented | 58.082 |
| random_forest | weather_augmented | 64.104 |
| random_forest | calendar_weather_augmented | 56.224 |
| gradient_boosting | calendar_weather_augmented | 61.878 |
| ridge | calendar_weather_augmented | 68.915 |

The selected model (by validation MAE, refit on train+validation) is the random
forest on calendar_weather_augmented, with held-out test MAE 55.325, RMSE 177.476,
MAPE 27.469%, and R-squared 0.648 - a 23.0% MAE reduction over the naive seasonal
baseline (71.848). Figure 7 shows observed versus predicted city-wide next-day
totals over the test period, which track the overall level and weekly pattern of
demand.

## 6. Forecast-to-Decision Simulation

At the baseline budget (135 crews, 50 requests per crew, 163 test days), total
weighted unmet demand is 643,324 under the internal-historical policy and 631,191
under calendar+weather, versus an oracle of 597,332: the augmented policy reduces
weighted unmet demand by 1.886% and closes 26.381% of the baseline-to-oracle gap.

Across crew budgets (Table 7, Figure 6) the calendar+weather policy is better than
the baseline in all three settings, but the magnitude grows with capacity: the
weighted-unmet reduction is 0.38% (scarce, 100 crews), 4.32% (moderate, 160), and
14.53% (generous, 220). The headline contrast - an approximately 11-15%
forecast-accuracy gain versus a roughly 1.9% decision-quality gain at the baseline
budget - is the central observation: average accuracy and operational value are
not the same, and a scarce budget with demand concentrated in a few large cells
limits how much any forecast can help.

**Table 7: decision sensitivity by crew budget.** Stylized simulation; total
weighted unmet demand (lower is better); calendar+weather versus
internal-historical.

| Setting | Crews | Internal | Calendar+Weather | Oracle | Reduction | Gap to oracle closed |
|---------|------:|---------:|-----------------:|-------:|----------:|---------------------:|
| scarce | 100 | 941,817 | 938,211 | 928,491 | 0.38% | 27.06% |
| moderate | 160 | 454,073 | 434,469 | 367,553 | 4.32% | 22.66% |
| generous | 220 | 164,197 | 140,346 | 50,865 | 14.53% | 21.05% |

## 7. Robustness Checks

Five-fold expanding-window rolling-origin validation (Figure 3; full table in
Appendix C) shows calendar augmentation lowering MAE in every fold for every
model: mean improvement 15.13% for the random forest, 9.94% for gradient boosting,
and 0.94% for Ridge, each in all 5 of 5 folds. The calendar_weather_augmented
random forest has the lowest mean fold MAE (47.497). Segmented analysis (random
forest, internal vs calendar; Appendix G) shows the improvement holds for all five
boroughs (about 8.8% to 18.8%) and all eight complaint groups (about 8.9% to
25.8%); absolute error concentrates in the highest-volume segments (Noise,
Housing; the Bronx). The forecast improvement is therefore consistent across folds
and segments, not an artifact of one split.

## 8. Limitations

The study is predictive and correlational and makes no causal claim. NYC 311
reflects reporting behaviour, not true incidence (reporting bias), so forecasts
predict reported volume. Weather is a single Central Park station used as a
city-level proxy. Borough-level aggregation hides within-borough variation; the
complaint-group mapping is a deterministic approximation with a residual Other
group. No transit or event data is included. The staffing simulation is a stylized
proportional heuristic - not real dispatch, not staffing optimization, not
validated against any real policy - and omits crew travel, shifts, backlog,
intra-day timing, and substitution; it uses no observed dispatch decisions.
Results apply to NYC and 2022-2024 only.

Gating items for a stronger (full) paper: a non-stylized, agency-grounded decision
model with an empirical service-level realism check; formal forecast-difference
testing (for example a Diebold-Mariano test) with uncertainty intervals; and
broader external signals beyond a single weather station, or cross-city
replication.

## 9. Conclusion

On real NYC 311 data augmented with real NOAA weather, public-signal augmentation
consistently improves next-day service-demand forecasts - calendar most, weather a
smaller consistent increment - across rolling folds, boroughs, and complaint
groups. The improvement transfers in direction to a stylized staffing allocation
but with attenuated, budget-dependent magnitude. The forecast gains are real and
robust; the decision gains are smaller and conditional on capacity. The artifact
is a reproducible baseline suitable as a workshop / short-paper / arXiv-style
contribution.

## Reproducibility Statement

All values are read from committed artifacts under `reports/` and
`data/metadata/`. The pipeline is run with `python -m src.weather`,
`python -m src.build_dataset`, `python -m src.train`, `python -m src.evaluate`,
`python -m src.decision_simulation`, `python -m src.monitor`,
`python -m src.rolling_validation`, `python -m src.robustness_analysis`,
`python -m src.decision_sensitivity`, and `python -m src.practical_significance`,
on Python 3.11. The quality gate is `ruff check .` and `pytest`, run offline on a
committed real-schema sample; continuous integration runs the pipeline in that
sample mode. No API keys or secrets are required. The committed inputs are the
aggregated real daily counts and the real NOAA weather export; the large raw
monthly exports and the trained model binary are not committed.

## Data Availability Statement

NYC 311 Service Requests are public via NYC Open Data (Socrata dataset
`erm2-nwe9`) [@nyc311]. NOAA NCEI Daily Summaries (GHCN-Daily) for station
USW00094728 are public [@noaaghcnd]. The study window is 2022-2024. The aggregated
daily counts and the NOAA export used here are committed; the large raw monthly
311 exports and the processed modelling dataset are regenerable and not committed;
small real-schema samples are committed for continuous integration. No synthetic
data and no synthetic weather are used.

## Ethics Statement

The study uses public data only, at an aggregate date x borough x complaint_group
level; no individual-level records and no personal data are used or produced. It
makes no individual-level decisions, is not deployed, and is not public-safety
software. It makes no causal claim and no real dispatch or staffing optimization
claim. NYC 311 reflects reporting behaviour, not true incidence; reporting
propensity varies across communities and time, so forecasts of 311 volume are
forecasts of reporting, not of need, and must not be read as measures of true
demand or used in ways that could compound existing inequities.

## Appendix

**A. Feature and feature-set definitions.** Lag features (request_lag_1,
request_lag_7) and rolling statistics (rolling_mean_7/14, rolling_std_7/14) per
(borough, complaint_group) cell, using only past observations with a one-day
shift. Calendar features: is_weekend, is_holiday, day_of_week, month, quarter,
year, day_of_year, week_of_year, is_month_start, is_month_end. Weather features:
precipitation_mm, temp_max_c, temp_min_c, temp_avg_c, snowfall_mm, snow_depth_mm,
wind_speed_ms. Feature sets: internal_historical; calendar_augmented (internal +
calendar); weather_augmented (internal + weather); calendar_weather_augmented
(internal + calendar + weather). See Table 2.

**B. Complaint-group mapping.** Raw complaint types are mapped by a deterministic,
order-sensitive substring rule into eight groups (Housing, Noise, Sanitation,
Street Condition, Water, Traffic, Public Safety, and a residual Other).

**C. Chronological split and rolling-origin setup.** Chronological 70/15/15 split
by date (30,240 / 6,480 / 6,520 rows). Five expanding-window rolling-origin folds;
each fold trains on all dates up to a cut point and tests on the next block, with
no future information in training. Per-fold metrics are in
`reports/rolling_validation_report.csv`; the summary (Figure 3 source) is in
`reports/rolling_validation_summary.json`.

**D. Decision-simulation assumptions.** Stylized proportional allocation via a
largest-remainder rule; baseline-budget configuration 135 crews x 50 requests per
crew over 163 test days; weighted unmet demand up-weights Public Safety, Water, and
Traffic; an oracle allocates on true next-day demand. Not real dispatch; uses no
observed dispatch decisions.

**E. Crew-budget sensitivity.** Three budgets - scarce (100 crews, 5,000 daily
capacity), moderate (160 / 8,000), generous (220 / 11,000); per-policy results in
`reports/decision_sensitivity_report.csv` and `..._summary.json` (Table 7).

**F. Weather-data treatment.** Single NOAA station (USW00094728) joined to all
boroughs by date; temp_avg_c derived from observed TMAX/TMIN (source TAVG empty);
five missing wind-speed days time-interpolated from real neighbours; no synthetic
weather (`data/metadata/weather_source_report.json`). See Figure 8.

**G. Full results tables.** Complete 13-row model comparison
(`reports/model_comparison.csv`; Figure 1), per-borough robustness
(`reports/borough_performance.csv`; Figure 4), and per-complaint-group robustness
(`reports/complaint_group_performance.csv`; Figure 5). Internal vs
calendar-augmented per model is shown in Figure 10. A baseline-budget policy
comparison with the oracle is in Figure 9.

**H. Reproducibility commands.** See the Reproducibility Statement.

## Figures

Main figures: Figure 2 (`figure_2_feature_set_comparison_mae.png`), Figure 3
(`figure_3_rolling_validation_mae.png`), Figure 6
(`figure_6_decision_sensitivity.png`), Figure 7
(`figure_7_actual_vs_predicted.png`). Appendix figures: Figure 1
(`figure_1_model_comparison_mae.png`), Figure 4
(`figure_4_borough_robustness_mae.png`), Figure 5
(`figure_5_complaint_group_robustness_mae.png`), Figure 8
(`figure_8_weather_feature_summary.png`), Figure 9
(`figure_9_decision_quality_comparison.png`), Figure 10
(`figure_10_internal_vs_calendar_augmented_mae.png`). Captions: see
`paper/figure_captions.md`.

## References

See `paper/references.bib`: `cui2018operational`, `samorani2022overbooked`,
`nyc311`, `noaaghcnd`.
