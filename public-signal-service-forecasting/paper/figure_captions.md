# Figure Captions

Sources: `figures/*.png`, `research_artifacts/figure_interpretation_guide.md`,
and the report artifacts. Each entry gives the paper filename, the original repo
figure, a caption, the key takeaway, and an overclaim to avoid.

## Figure 1 - figure_1_model_comparison_mae.png (from figures/model_comparison_mae.png)
- Caption: Held-out test MAE for the naive baseline and every model x feature-set
  combination across the four feature sets.
- Key takeaway: tree ensembles benefit most from augmentation; the
  calendar+weather random forest is the lowest non-naive bar (56.224 train-only).
- Avoid: these are point estimates from one chronological split, not confidence
  intervals.

## Figure 2 - figure_2_feature_set_comparison_mae.png (from figures/feature_set_comparison_mae.png)
- Caption: Best test MAE achieved per feature set across models.
- Key takeaway: calendar is the dominant signal; weather-only edges past
  internal-historical, and calendar+weather is lowest.
- Avoid: the weather increment over calendar is small; do not overstate it.

## Figure 3 - figure_3_rolling_validation_mae.png (from figures/rolling_validation_mae.png)
- Caption: Per-fold test MAE by configuration across five expanding-window
  chronological folds.
- Key takeaway: calendar augmentation lowers MAE in every fold for every model;
  the effect is stable, not a one-split artifact.
- Avoid: fold-to-fold MAE varies with the test window; this shows consistency,
  not a formal significance test.

## Figure 4 - figure_4_borough_robustness_mae.png (from figures/borough_mae.png)
- Caption: Internal-historical vs calendar-augmented test MAE by borough (random
  forest).
- Key takeaway: augmentation improves all five boroughs (about 8.8% to 18.8%).
- Avoid: absolute error reflects borough volume, not model quality.

## Figure 5 - figure_5_complaint_group_robustness_mae.png (from figures/complaint_group_mae.png)
- Caption: Internal-historical vs calendar-augmented test MAE by complaint group
  (random forest).
- Key takeaway: augmentation improves all eight groups (about 8.9% to 25.8%).
- Avoid: smaller bars for low-volume groups do not mean better relative modelling.

## Figure 6 - figure_6_decision_sensitivity.png (from figures/decision_sensitivity.png)
- Caption: Total weighted unmet demand by policy under scarce, moderate, and
  generous crew budgets.
- Key takeaway: the augmented policy beats the baseline at every budget, but the
  margin grows with capacity (budget-dependent).
- Avoid: the simulation is stylized; budget levels are illustrative.

## Figure 7 - figure_7_actual_vs_predicted.png (from figures/forecast_actual_vs_predicted.png)
- Caption: Observed vs predicted city-wide next-day request totals over the test
  period for the best model.
- Key takeaway: the best model follows the overall day-to-day level and weekly
  pattern of total demand.
- Avoid: city-wide totals average out cell-level error; this is descriptive, not
  a goodness-of-fit test.

## Figure 8 - figure_8_weather_feature_summary.png (from figures/weather_feature_summary.png)
- Caption: Real NOAA daily weather series for the Central Park station over
  2022-2024.
- Key takeaway: shows the real observed weather variables used as features.
- Avoid: this is one station used as a city-level proxy; not borough-level
  weather.

## Figure 9 - figure_9_decision_quality_comparison.png (from figures/decision_quality_comparison.png)
- Caption: Total weighted unmet demand by policy at the baseline crew budget, with
  the oracle benchmark.
- Key takeaway: calendar+weather reduces weighted unmet demand 1.886% over
  baseline and closes 26.381% of the baseline-to-oracle gap.
- Avoid: stylized simulation; the oracle is an unattainable benchmark.

## Figure 10 - figure_10_internal_vs_calendar_augmented_mae.png (from figures/internal_vs_calendar_augmented_mae.png)
- Caption: Internal-historical vs calendar-augmented test MAE per non-naive model.
- Key takeaway: calendar augmentation helps all three models, most for the random
  forest.
- Avoid: associational under this protocol; no causal mechanism is identified.

Note: `figures/forecast_error_by_model.png` exists in the repo and is the same
content as `model_comparison_mae.png` (an alias); it was not duplicated into
`paper/figures/`.
