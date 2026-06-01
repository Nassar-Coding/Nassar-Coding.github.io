# Candidate C Freeze Note

This note freezes Candidate C after the weather-augmentation sprint. All values
are read from committed artifacts under `reports/` and `data/metadata/`.

## 1. What final Candidate C includes

- Real NYC 311 Service Requests (2022-2024): 9,851,452 raw records aggregated to
  43,240 date x borough x complaint-group rows; 5 boroughs; 8 complaint groups;
  observed next-day target. No synthetic data.
- Real NOAA daily weather (NCEI Daily Summaries, station USW00094728, NYC
  Central Park, 2022-2024): precipitation, max/min temperature, snowfall, snow
  depth, wind speed, plus a documented derived `temp_avg`. No synthetic weather.
- Four feature sets compared: internal_historical, calendar_augmented,
  weather_augmented, calendar_weather_augmented.
- Four model families: naive seasonal, Ridge, random forest, gradient boosting.
- Validation: single chronological split plus 5-fold rolling-origin; borough and
  complaint-group robustness; decision sensitivity across three crew budgets.
- A stylized staffing-allocation simulation with an oracle bound.
- A short-paper draft (`candidate_c_short_paper.md`) and the full research
  artifact package.

## 2. What was intentionally excluded

Per the sprint's hard cap: no transit data, no event-calendar data, no
cross-city replication, no DSNY/DOT operational-policy modeling, and no complex
cost-benefit modeling. Candidate A is not started, not scoped, and not present
in this repository.

## 3. Was weather successfully added

Yes. Real NOAA weather for station USW00094728 was read via the connector,
ingested by `src/weather.py`, and joined into the processed dataset
(`data/processed/weather_daily_2022_2024.csv`,
`data/metadata/weather_source_report.json`). Seven weather variables are used;
the empty source `TAVG` is recorded as missing and `temp_avg` is derived from
observed TMAX/TMIN. No weather was fabricated.

## 4. Final empirical result

- Best model: random forest on calendar_weather_augmented. Held-out test MAE
  55.33, RMSE 177.48, MAPE 27.47%, R-squared 0.648; 23.0% better than the naive
  seasonal baseline (MAE 71.85).
- Weather effect: calendar is the dominant gain; weather adds a smaller
  consistent further gain (random forest calendar 58.08 to calendar+weather
  56.22; weather-only 64.10 beats internal 65.28).
- Rolling-origin: calendar+weather random forest is the lowest-error
  configuration on average (mean MAE 47.50); augmentation improves every model
  in every fold.
- Robustness: augmentation improves all 5 boroughs and all 8 complaint groups.
- Decision simulation (baseline budget): weighted unmet demand 643,324
  (internal) to 631,191 (calendar+weather); 1.89% reduction; 26.4% of the oracle
  gap closed. Across budgets the augmented policy wins in all three settings, but
  the reduction is budget-dependent (0.38% / 4.32% / 14.53%).
- Practical significance summary: forecasting evidence strong; decision evidence
  directionally consistent but budget-dependent; not full-paper-ready.

## 5. Final paper status

- **Full paper worthy now: NO.** The forecasting result is strong and stable, but
  the decision evidence is budget-dependent and rests on a single stylized
  proportional-allocation heuristic, and there is no formal forecast-difference
  testing and no non-calendar/non-weather external comparison or cross-city
  validation.
- **Workshop / short-paper worthy now: YES.** Real dual-source public-data
  augmentation, leakage-controlled validation, segment robustness, and an honest
  forecast-to-decision analysis support a workshop / arXiv short paper.

## 6. Continue or freeze

**Freeze Candidate C** as a completed real-data research baseline and
workshop/short-paper artifact. Weather was added and modestly improved both
forecasts and the decision metric; the improvement does not change the ceiling
from workshop to full paper.

## 7. Exact condition under which Candidate C may be reopened

Reopen only if all of the following are added: (a) a non-stylized decision model
grounded in documented agency operations with an empirical service-level realism
check; (b) formal forecast-difference testing (for example Diebold-Mariano) with
uncertainty intervals; and (c) at least one additional genuinely external signal
beyond weather, or cross-city replication. Absent these, Candidate C stays
frozen.

## 8. Candidate A statement

Candidate A is not started in this repository or in this pass. No Candidate A
files were created, and no Candidate A scoping was performed. This pass is
Candidate C only.
