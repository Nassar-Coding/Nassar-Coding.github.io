# Paper Figures

These are copies of the committed repository figures (`figures/*.png`), renamed
with paper-facing names. They are not regenerated here; the source figures are
produced by `python -m src.evaluate`, `python -m src.decision_simulation`,
`python -m src.decision_sensitivity`, `python -m src.rolling_validation`,
`python -m src.robustness_analysis`, and `python -m src.weather`.

| Paper figure | Source figure | Purpose |
|--------------|---------------|---------|
| figure_1_model_comparison_mae.png | figures/model_comparison_mae.png | Test MAE by model x feature set |
| figure_2_feature_set_comparison_mae.png | figures/feature_set_comparison_mae.png | Best test MAE per feature set |
| figure_3_rolling_validation_mae.png | figures/rolling_validation_mae.png | Per-fold MAE across 5 folds |
| figure_4_borough_robustness_mae.png | figures/borough_mae.png | Internal vs calendar MAE by borough |
| figure_5_complaint_group_robustness_mae.png | figures/complaint_group_mae.png | Internal vs calendar MAE by complaint group |
| figure_6_decision_sensitivity.png | figures/decision_sensitivity.png | Weighted unmet demand by crew budget |
| figure_7_actual_vs_predicted.png | figures/forecast_actual_vs_predicted.png | Observed vs predicted city-wide totals |
| figure_8_weather_feature_summary.png | figures/weather_feature_summary.png | Real NOAA daily weather series |
| figure_9_decision_quality_comparison.png | figures/decision_quality_comparison.png | Weighted unmet demand by policy (baseline budget) |
| figure_10_internal_vs_calendar_augmented_mae.png | figures/internal_vs_calendar_augmented_mae.png | Internal vs calendar MAE per model |

Note: `figures/forecast_error_by_model.png` is the same content as
`model_comparison_mae.png` (an alias) and was not duplicated.
