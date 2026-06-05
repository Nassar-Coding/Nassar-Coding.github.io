# Number Audit

Every numeric claim in the paper, traced to a committed repository output. All
values are read from `reports/`, `data/metadata/`, or computed directly from
those files. "Verified" means the value matches the cited source.

| Claim | Value | Source | In paper | Verified | Notes |
|-------|-------|--------|----------|:--------:|-------|
| Raw 311 records | 9,851,452 | data/metadata/data_source_report.json (raw_row_count) | Abstract, §3, Table 1 | yes | |
| Processed rows | 43,240 | data/metadata/data_source_report.json (processed_row_count) | Abstract, §3, Table 1 | yes | |
| Study window | 2022-01-01 to 2024-12-31 | data_source_report.json | §3, Table 1 | yes | |
| Observed processed date range | 2022-01-15 to 2024-12-30 | data_source_report.json (date_range_observed) | §3, Table 1 | yes | after warmup |
| Boroughs | 5 | data_source_report.json (boroughs_included) | §3, Table 1 | yes | |
| Complaint groups | 8 | data_source_report.json (complaint_groups_included) | §3, Table 1 | yes | |
| Weather station | USW00094728 | data/metadata/weather_source_report.json (station_id) | §3, Table 1 | yes | Central Park |
| Weather daily rows | 1,096 | weather_source_report.json (rows) | §3, Table 1 | yes | |
| Weather variables used | 7 | weather_source_report.json (variables_used) | §3, Table 1, Table A1 | yes | |
| temp_avg derived | true | weather_source_report.json (temp_avg_derived_from_tmax_tmin) | §3, Appendix F | yes | source TAVG empty |
| Wind-speed gaps interpolated | 5 | weather_source_report.json (short_gaps_time_interpolated_per_column) | §3, Appendix F | yes | others 0 |
| Train/val/test rows | 30,240 / 6,480 / 6,520 | reports/metrics.json (split) | §4, Appendix C | yes | |
| Naive seasonal test MAE | 71.848 | reports/model_comparison.csv | §5, Table 2, Table A3 | yes | |
| RF internal_historical test MAE | 65.282 | reports/model_comparison.csv | §5, Table 2, Table A3 | yes | |
| RF calendar_augmented test MAE | 58.082 | reports/model_comparison.csv | §5, Table 2, Table A3 | yes | |
| RF weather_augmented test MAE | 64.104 | reports/model_comparison.csv | §5, Table 2, Table A3 | yes | |
| RF calendar_weather_augmented test MAE (train-only) | 56.224 | reports/model_comparison.csv | §5, Table 2, Table A3 | yes | fit on train only |
| Ridge internal/weather/cal+weather test MAE | 69.219 / 69.283 / 68.915 | reports/model_comparison.csv | §5, Table A3 | yes | Ridge no weather gain |
| Best model | random_forest, calendar_weather_augmented | reports/evaluation_report.json | Abstract, §5 | yes | refit on train+val |
| Best test MAE | 55.325 | reports/evaluation_report.json (test_metrics.mae) | Abstract, §5 | yes | 55.32472... |
| Best test RMSE | 177.476 | reports/evaluation_report.json | §5, Table A3 | yes | 177.47628... |
| Best test MAPE | 27.469% | reports/evaluation_report.json | §5, Table A3 | yes | 27.46940... |
| Best test R² | 0.648 | reports/evaluation_report.json | Abstract, §5, Table A3 | yes | 0.64779... |
| Improvement over naive | 23.0% | reports/monitoring_report.json (improvement_over_baseline_pct 22.998) | Abstract, §5 | yes | rounds to 23.0 |
| Rolling folds | 5 | reports/rolling_validation_summary.json (n_folds) | §7, Table A2 | yes | |
| Rolling calendar improvement RF/GB/Ridge | 15.13% / 9.94% / 0.94% | rolling_validation_summary.json (consistency) | §7 | yes | all 5/5 folds |
| Rolling RF mean fold MAE: internal/weather/calendar/cal+weather | 57.027 / 56.222 / 48.690 / 47.497 | rolling_validation_summary.json | Table A2 | yes | naive 61.701 |
| Borough improvement range | 8.84% to 18.78% | reports/borough_performance.csv | §7, Table A4 | yes | all 5 better |
| Complaint-group improvement range | 8.91% to 25.82% | reports/complaint_group_performance.csv | §7, Table A5 | yes | all 8 better |
| Decision baseline-budget weighted unmet (internal) | 643,324 | reports/decision_simulation_report.json | §6 | yes | 643,324.5 |
| Decision baseline-budget weighted unmet (cal+weather) | 631,191 | reports/decision_simulation_report.json | §6 | yes | |
| Decision baseline-budget weighted unmet (oracle) | 597,332 | reports/decision_simulation_report.json | §6 | yes | observed-demand oracle |
| Decision baseline reduction | 1.886% | reports/decision_simulation_report.json | Abstract, §6 | yes | |
| Decision baseline gap-to-oracle closed | 26.381% | reports/decision_simulation_report.json | Abstract, §6 | yes | |
| Sensitivity reductions (scarce/moderate/generous) | 0.38% / 4.32% / 14.53% | reports/decision_sensitivity_summary.json | §6, Table 3 | yes | better in all 3 |
| Sensitivity gap-to-oracle (scarce/moderate/generous) | 27.06% / 22.66% / 21.05% | reports/decision_sensitivity_summary.json | Table 3 | yes | |
| Sensitivity weighted-unmet by policy/budget | see Table 3 | reports/decision_sensitivity_report.csv | Table 3 | yes | exact CSV values |
| Best-model segment MAE (borough/group) | see evaluation_report | reports/evaluation_report.json (mae_by_*) | (appendix discussion) | yes | cal+weather segments; distinct from Tables A4-A5, which compare internal vs calendar |

## Notes on two distinct segment views

- Tables A4 and A5 (borough and complaint-group robustness) come from
  `reports/borough_performance.csv` and `reports/complaint_group_performance.csv`,
  which compare internal_historical vs calendar_augmented for the random forest.
- `reports/evaluation_report.json` also reports per-segment MAE for the selected
  calendar_weather_augmented model; those values differ and are not used in
  Tables A4-A5 to avoid conflating the two comparisons.

## Result

All numeric claims in the paper, its tables, the appendix, and the captions are
traceable to a committed output and verified against it. No number is taken from
memory or invented.
