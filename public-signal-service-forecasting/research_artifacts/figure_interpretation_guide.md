# Figure Interpretation Guide

This guide explains each figure in `figures/`. All figures are generated from the
committed real-data artifacts by `python -m src.evaluate` and
`python -m src.decision_simulation`. Four figures are present and none are
missing.

## 1. forecast_error_by_model.png

- What it shows: a bar chart of test MAE for every model and feature-set
  combination (naive seasonal baseline, and Ridge / random forest / gradient
  boosting on each of the internal-historical and calendar-augmented sets).
- How to read it: shorter bars are better (lower test MAE). Compare each model's
  internal-historical bar with its calendar-augmented bar to see the effect of
  calendar features; compare all bars with the naive baseline.
- Key takeaway: the calendar-augmented random forest has the lowest test MAE in
  the comparison table (58.08), and calendar augmentation lowers the bar for every
  model.
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

- What it shows: a bar chart of total weighted unmet demand for the three policies
  (baseline internal-historical, calendar-augmented, and oracle true-demand).
- How to read it: lower bars are better. The distance from the baseline bar to the
  oracle bar is the maximum achievable improvement; the calendar-augmented bar
  sits between them.
- Key takeaway: the calendar-augmented policy reduces weighted unmet demand by
  1.35% over the baseline and closes 18.94% of the baseline-to-oracle gap.
- Do not overclaim: the simulation is stylized and is not real dispatch; the
  oracle is an unattainable benchmark; the absolute values depend on the assumed
  crew budget and complaint-group weights.

## Optional additional figures (not currently generated)

The four figures above cover the core narrative. Two optional figures could be
added later, strictly from existing artifacts, if a richer presentation is needed:

- Per-borough or per-complaint-group test MAE for the best model (values already
  in `reports/evaluation_report.json`), to visualise where error concentrates.
- A baseline-vs-augmented-vs-oracle panel for unweighted unmet demand and
  allocation efficiency (values already in
  `reports/decision_simulation_report.json`).

These are recommended only if a presentation needs them; they are not required for
the current results and should be generated from the reports, never from
fabricated values.
