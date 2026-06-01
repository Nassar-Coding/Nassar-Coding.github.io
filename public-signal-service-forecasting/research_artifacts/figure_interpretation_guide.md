# Figure Interpretation Guide

This guide explains each figure in `figures/`. All figures are generated from the
committed real-data artifacts by `python -m src.evaluate` and
`python -m src.decision_simulation`.

## 1. forecast_error_by_model.png

- What it shows: a bar chart of test MAE for every model and feature-set
  combination (naive seasonal baseline, and Ridge / random forest / gradient
  boosting on each of the four feature sets: internal-historical,
  calendar-augmented, weather-augmented, and calendar + weather augmented), now
  13 bars.
- How to read it: shorter bars are better (lower test MAE). Compare each model's
  internal-historical bar with its calendar-, weather-, and calendar + weather
  bars to see the effect of each augmentation; compare all bars with the naive
  baseline.
- Key takeaway: the calendar + weather random forest has the lowest test MAE in
  the comparison table (56.22); calendar is the dominant signal, and real weather
  adds a smaller but consistent further gain on top of it.
- Do not overclaim: bars are point estimates from a single chronological test
  split, not confidence intervals; small differences should not be read as
  statistically distinguishable.

## 2. internal_vs_calendar_augmented_mae.png

- What it shows: a grouped bar chart comparing internal-historical versus
  calendar-augmented test MAE for each non-naive model.
- How to read it: within each model, the two bars are the two feature sets; the
  drop from the internal-historical bar to the calendar-augmented bar is the
  accuracy gain from adding calendar features.
- Key takeaway: the gain is positive for all three models and largest for the
  random forest (65.28 to 58.08, 11.03%).
- Do not overclaim: the gain is associational under this protocol; it does not
  identify a causal mechanism, and calendar features may proxy seasonality rather
  than a specific operational driver.

## 3. forecast_actual_vs_predicted.png

- What it shows: observed versus predicted city-wide next-day request totals over
  the test period for the best model (the predictions and actuals are summed
  across all cells per day).
- How to read it: the two lines should track each other; gaps indicate days where
  the aggregate forecast over- or under-shoots. Aggregating to a city-wide total
  is a readability choice and averages out cell-level error.
- Key takeaway: the best model follows the overall day-to-day level and weekly
  pattern of total demand across the test window.
- Do not overclaim: close tracking of city-wide totals is easier than cell-level
  accuracy; this plot does not reflect the per-cell errors that drive the decision
  simulation, and it is descriptive rather than a goodness-of-fit test.

## 4. decision_quality_comparison.png

- What it shows: a bar chart of total weighted unmet demand for the policies
  driven by each feature set (baseline internal-historical, calendar-augmented,
  weather-augmented, calendar + weather augmented) and the oracle true-demand
  benchmark.
- How to read it: lower bars are better. The distance from the baseline bar to the
  oracle bar is the maximum achievable improvement; the feature-set policy bars
  sit between them.
- Key takeaway: the calendar + weather policy reduces weighted unmet demand by
  1.886% over the baseline and closes 26.381% of the baseline-to-oracle gap.
- Do not overclaim: the simulation is stylized and is not real dispatch; the
  oracle is an unattainable benchmark; the absolute values depend on the assumed
  crew budget and complaint-group weights.

## 5. rolling_validation_mae.png

- What it shows: per-fold test MAE for every model and feature-set configuration
  across the five expanding-window chronological folds.
- How to read it: each line is one configuration; the x-axis is the fold
  (chronological). Compare each model's internal-historical line with its
  calendar-augmented line within and across folds.
- Key takeaway: the calendar-augmented lines sit below their internal-historical
  counterparts in every fold for every model (random forest mean improvement
  15.1%, gradient boosting 9.9%, Ridge 0.9%), showing the forecasting effect is
  stable, not a one-split artifact; in mean fold test MAE the random forest
  improves from internal (57.03) through weather (56.22) and calendar (48.69) to
  calendar + weather (47.50).
- Do not overclaim: fold-to-fold MAE varies with the test window; the lines show
  consistency of the gap, not a formal significance test.

## 6. complaint_group_mae.png

- What it shows: internal-historical vs calendar-augmented test MAE for the best
  model (random forest), by complaint group.
- How to read it: within each group, the lower (green) bar is the
  calendar-augmented MAE. Groups are ordered by augmented MAE.
- Key takeaway: augmentation improves all eight groups (about 8.9% to 25.8%);
  absolute error is largest for Noise and Housing.
- Do not overclaim: absolute error scales with group volume; smaller bars for
  low-volume groups do not mean those groups are modelled better in relative
  terms.

## 7. borough_mae.png

- What it shows: internal-historical vs calendar-augmented test MAE for the best
  model, by borough.
- How to read it: within each borough, the lower (green) bar is the
  calendar-augmented MAE.
- Key takeaway: augmentation improves all five boroughs (about 8.8% to 18.8%);
  absolute error is largest for the Bronx and smallest for Staten Island.
- Do not overclaim: borough differences in absolute error reflect volume, not
  necessarily model quality.

## 8. decision_sensitivity.png

- What it shows: total weighted unmet demand for the policies (baseline
  internal-historical, augmented, oracle) under scarce, moderate, and generous
  crew budgets.
- How to read it: within each budget group, compare the bars; lower is better.
  Compare across budget groups to see how the gaps change with capacity.
- Key takeaway: the calendar + weather policy beats the baseline in all three
  budgets, but the margin grows with capacity (0.38% scarce, 4.32% moderate,
  14.53% generous), so the decision benefit is budget-dependent.
- Do not overclaim: the simulation is stylized; the budget levels are
  illustrative; absolute values depend on the allocation rule and weights.

## 9. feature_set_comparison_mae.png

- What it shows: a bar chart of the best test MAE achieved per feature set across
  models, for the four feature sets: internal-historical, calendar-augmented,
  weather-augmented, and calendar + weather augmented.
- How to read it: shorter bars are better (lower test MAE). The progression from
  internal-historical through weather and calendar to calendar + weather shows the
  marginal contribution of each augmentation.
- Key takeaway: calendar + weather has the lowest best test MAE (56.22); calendar
  is the dominant signal, weather-only (64.10) edges past internal-historical
  (65.28), and adding weather on top of calendar lowers MAE further (58.08 to
  56.22).
- Do not overclaim: these are point estimates from a single chronological test
  split, not confidence intervals; the weather increment over calendar is small.

## 10. model_comparison_mae.png

- What it shows: an alias view of forecast error by model and feature set - test
  MAE for the naive baseline and every model x feature-set combination across the
  four feature sets, now 13 bars.
- How to read it: shorter bars are better. Group bars by model to compare the four
  feature sets within each model, or scan across models within a feature set.
- Key takeaway: tree ensembles benefit most from augmentation; the calendar +
  weather random forest is the lowest bar (56.22), while Ridge changes little
  across feature sets.
- Do not overclaim: single-split point estimates; small bar differences are not
  necessarily distinguishable, and Ridge does not benefit from weather.

## 11. weather_feature_summary.png

- What it shows: panels of the real NOAA NCEI Daily Summaries (GHCN-Daily) daily
  series for station USW00094728 (NYC Central Park), 2022-2024 - precipitation,
  maximum/minimum/average temperature, snowfall, snow depth, and wind speed.
- How to read it: each panel is one weather variable over the study window; the
  series show the seasonal and day-to-day variation of the external signal fed
  into the weather feature sets.
- Key takeaway: the weather layer is real observed data (no synthetic weather);
  temp_avg_c is derived from observed max/min because the source TAVG was empty,
  and five missing wind days are time-interpolated.
- Do not overclaim: this is a single-station city-level proxy, not spatially
  resolved weather; the panels are descriptive and do not imply any causal effect
  of weather on demand.

## Optional additional figures (not currently generated)

The eight figures above cover the core narrative. Two optional figures could be
added later, strictly from existing artifacts, if a richer presentation is needed:

- Per-borough or per-complaint-group test MAE for the best model (values already
  in `reports/evaluation_report.json`), to visualise where error concentrates.
- A baseline-vs-augmented-vs-oracle panel for unweighted unmet demand and
  allocation efficiency (values already in
  `reports/decision_simulation_report.json`).

These are recommended only if a presentation needs them; they are not required for
the current results and should be generated from the reports, never from
fabricated values.
