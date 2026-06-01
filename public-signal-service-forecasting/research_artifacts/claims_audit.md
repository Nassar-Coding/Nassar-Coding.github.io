# Claims Audit

Every claim the project makes is tied to a committed artifact. Confidence
reflects how directly the artifact supports the claim. "Safe to say publicly"
indicates whether the claim can be stated in a public summary without
qualification beyond the noted caveats.

## Supported claims

| Claim | Supported by | Evidence location | Confidence | Safe publicly? | Notes |
|-------|--------------|-------------------|------------|----------------|-------|
| Real NYC 311 data was used | `data/metadata/data_source_report.json` | `data_mode: "real_nyc_311"`, `source_name`, `source_url` | High | Yes | Source is NYC Open Data `erm2-nwe9`. |
| No synthetic data was used | metadata + repository state | `no_synthetic_data: true`, `synthetic_fallback_used: false`; synthetic generator removed from `src/` | High | Yes | `src/generate_fallback_data.py` deleted; build raises an error if real data absent. |
| Study window is 2022-2024 | metadata | `study_start_date: 2022-01-01`, `study_end_date: 2024-12-31` | High | Yes | Observed processed range 2022-01-15 to 2024-12-30 after warmup. |
| 9,851,452 raw records read | metadata | `raw_row_count`; `aggregation_metadata.raw_rows_read` | High | Yes | 9,838,988 remain after filtering; 12,464 dropped for invalid borough. |
| 43,240 processed rows | metadata + dataset | `processed_row_count: 43240` | High | Yes | Aggregated daily-count rows before warmup: 43,840. |
| 36 monthly input files | metadata | `aggregation_metadata.input_files_count: 36` | High | Yes | File list recorded in metadata. |
| Unit is date x borough x complaint_group | dataset + docs | `data/processed/...csv` columns; `docs/data_card.md` | High | Yes | Five boroughs, eight complaint groups. |
| Target is observed next-day count | `src/features.py`; docs | `add_target` (gap-aware shift); `docs/model_card.md` | High | Yes | Computed only from observed records. |
| Best model is random_forest + calendar_weather_augmented | `reports/metrics.json`, `reports/evaluation_report.json` | `best_model`, `best_feature_set` | High | Yes | Selected by validation MAE. |
| Best-model test MAE approx 55.33 | `reports/evaluation_report.json` | `test_metrics.mae = 55.325` | High | Yes | RMSE 177.48, MAPE 27.47%, R2 0.648. |
| Calendar features improved accuracy for all models | `reports/model_comparison.csv`, `reports/metrics.json` | RF 65.28 to 58.08, GB 67.49 to 61.71, Ridge 69.22 to 68.76 | High | Yes | Largest gain for random forest. |
| Real NOAA weather was used (station USW00094728, NYC Central Park) | `data/metadata/weather_source_report.json` | NOAA NCEI Daily Summaries (GHCN-Daily), 2022-2024, 1,096 days | High | Yes | Variables: precipitation, TMAX/TMIN, derived TAVG, snowfall, snow depth, wind. |
| No synthetic weather was used | `data/metadata/weather_source_report.json` | real observed series; 5 missing wind days time-interpolated only | High | Yes | temp_avg_c derived from observed TMAX/TMIN because source TAVG empty. |
| Weather adds a small consistent forecast gain on top of calendar | `reports/model_comparison.csv` | RF weather 64.10 < internal 65.28; calendar+weather 56.22 < calendar 58.08 | High | Yes, with caveat | Calendar dominant; Ridge does not benefit from weather. |
| Calendar + weather is the best feature set (test MAE 55.33) | `reports/evaluation_report.json`, `reports/model_comparison.csv` | selected model metrics | High | Yes | Refit on train+validation. |
| Selected model beats naive baseline by 23.0% | `reports/monitoring_report.json` | `improvement_over_baseline_pct` | High | Yes | Naive test MAE 71.848. |
| Decision simulation: calendar + weather improves allocation outcome | `reports/decision_simulation_report.json` | `weighted_unmet_demand_reduction_pct: 1.886`, better than baseline true | High | Yes, with caveat | Improvement is small (about 1.89%). |
| Calendar + weather policy closes about 26.4% of oracle gap at baseline budget | `reports/decision_simulation_report.json` | `gap_to_oracle_closed_pct: 26.381` | High | Yes | Oracle is an upper-bound benchmark only. |
| Decision benefit is budget-dependent | `reports/decision_sensitivity_summary.json` | reductions 0.38% / 4.32% / 14.53% across budgets | High | Yes | Better in all three; magnitude grows with capacity. |
| Leakage-controlled chronological split (70/15/15) | `reports/metrics.json`; `src/train.py` | `split` block; `chronological_split` | High | Yes | Lag/rolling features use past only. |

## Robustness claims (closure pass)

| Claim | Supported by | Evidence location | Confidence | Safe publicly? | Notes |
|-------|--------------|-------------------|------------|----------------|-------|
| Calendar augmentation wins in every rolling fold for every model | `reports/rolling_validation_summary.json` | `calendar_augmentation_consistency` (RF 5/5, GB 5/5, Ridge 5/5) | High | Yes | 5 expanding-window folds; mean improvements RF 15.13%, GB 9.94%, Ridge 0.94%. |
| Improvement holds for all five boroughs | `reports/borough_performance.csv` | `augmented_better` true for 5/5 | High | Yes | Range about 8.8% to 18.8%. |
| Improvement holds for all eight complaint groups | `reports/complaint_group_performance.csv` | `augmented_better` true for 8/8 | High | Yes | Range about 8.9% to 25.8%. |
| Augmented decision policy better at every crew budget | `reports/decision_sensitivity_summary.json` | `augmented_better_in_all_settings: true` | High | Yes, with caveat | Magnitude budget-dependent (0.38%, 4.32%, 14.53%). |
| Decision effect is budget-dependent | `reports/decision_sensitivity_summary.json` | per-setting reductions | High | Yes | Must be stated alongside the decision claim. |
| Not strong enough for full-paper drafting | `reports/practical_significance_summary.json` | `strong_enough_for_full_paper_drafting: false` | High | Yes | Forecasting strong; decision evidence budget-dependent. |

## Boundary (negative) claims that must be preserved

| Claim | Supported by | Evidence location | Confidence | Safe publicly? | Notes |
|-------|--------------|-------------------|------------|----------------|-------|
| No causal effect is claimed | docs | `docs/limitations.md` (causal section); `docs/research_brief.md` | High | Yes | Study is correlational/predictive. |
| No production readiness is claimed | docs | `docs/model_card.md` (out-of-scope); `docs/responsible_ai.md` | High | Yes | Local-only baseline. |
| No real dispatch impact is claimed | report + docs | `decision_simulation_report.json` description; `docs/decision_simulation.md` | High | Yes | Simulation is stylized. |
| No real staffing optimization is claimed | report + docs | same as above | High | Yes | Proportional heuristic, not optimization. |
| Reporting bias limits interpretation | docs + metadata | `docs/limitations.md`; `known_data_quality_issues` | High | Yes | 311 reflects reporting, not incidence. |
| Decision simulation is stylized | docs + report | `docs/decision_simulation.md`; report `description` | High | Yes | Omits travel, shifts, backlog, substitution. |
| No external validity beyond NYC 2022-2024 | docs | `docs/limitations.md` (external validity) | High | Yes | Single city, daily, eight groups. |

## Unsupported claims (must not be used anywhere)

| Claim | Status | Notes |
|-------|--------|-------|
| Calendar features cause changes in demand | Unsupported | No causal identification; do not state. |
| Weather causes changes in service demand | Unsupported | Weather is a correlational predictor only; no causal claim. |
| Transit or event data was used | Unsupported | Only real NOAA weather was added; no transit or event signals. |
| The model is ready for deployment / production | Unsupported | Not validated operationally. |
| The simulation reflects real NYC dispatch outcomes | Unsupported | Stylized heuristic only. |
| Results generalize to other cities or periods | Unsupported | Out of study scope. |
| The project is full-paper ready or a finished/publishable paper | Unsupported | `strong_enough_for_full_paper_drafting: false`; it is a research baseline package. |

## Audit result

All positive empirical claims used in the research artifacts are traceable to a
specific committed artifact and use the exact values from those artifacts. All
boundary claims (no causal, no production, no real dispatch, no real optimization,
reporting-bias and stylized-simulation caveats, no external validity) are present
in the documentation and preserved across the package. No unsupported claim is
used in any artifact.
