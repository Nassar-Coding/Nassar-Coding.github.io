# Final Candidate C Summary

## Project title

Public Signal Service Forecasting: calendar- and weather-augmented next-day
forecasting and stylized staffing decision simulation on real NYC 311 data.

## Dataset facts

- Source: NYC 311 Service Requests (NYC Open Data, `erm2-nwe9`); data mode
  `real_nyc_311`; no synthetic data, no synthetic fallback.
- Study window 2022-01-01 to 2024-12-31; 36 monthly files.
- Raw records read: 9,851,452; retained after filtering: 9,838,988.
- Processed rows: 43,240; five boroughs; eight complaint groups; unit
  date x borough x complaint_group; target `request_volume_next_day`.
- Real weather layer: NOAA NCEI Daily Summaries (GHCN-Daily), station
  USW00094728 (NYC Central Park), 2022-2024, 1,096 days (precipitation,
  TMAX/TMIN, derived TAVG, snowfall, snow depth, wind); single-station
  city-level proxy; no synthetic weather. No transit or event data.

## Model facts

- Best model: random forest, calendar + weather augmented feature set (one of
  four feature sets: internal-historical, calendar, weather, calendar + weather).
- Single-split test metrics: MAE 55.33, RMSE 177.48, MAPE 27.47%, R-squared
  0.648; 23.0% better than the naive seasonal baseline (MAE 71.85).
- Calendar augmentation lowers single-split test MAE for every model (random
  forest 11.03%, gradient boosting 8.57%, Ridge 0.67%); calendar is the dominant
  signal and real weather adds a smaller but consistent gain on top of it (random
  forest weather 64.10 < internal 65.28; calendar + weather 56.22 < calendar
  58.08), while Ridge does not benefit from weather.

## Decision simulation facts

- Stylized proportional allocation of a fixed crew budget; weighted unmet demand
  is the primary metric. Not real dispatch and not real optimization.
- At the baseline configuration (135 crews, 50 requests/crew): weighted unmet
  demand is 643,324 (internal), 634,614 (calendar), 641,382 (weather), 631,191
  (calendar + weather), and 597,332 (oracle); the calendar + weather policy is a
  1.886% reduction that closes 26.381% of the baseline-to-oracle gap.

## Robustness facts

- Rolling-origin (5 chronological folds): calendar augmentation wins every fold
  for every model (random forest +15.1% mean, gradient boosting +9.9%, Ridge
  +0.9%); random-forest mean fold test MAE internal 57.03, weather 56.22, calendar
  48.69, calendar + weather 47.50.
- Borough robustness: improved in all 5 boroughs (about 8.8% to 18.8%).
- Complaint-group robustness: improved in all 8 groups (about 8.9% to 25.8%).
- Decision sensitivity: calendar + weather policy better in all three crew
  budgets, but budget-dependent (0.38% scarce, 4.32% moderate, 14.53% generous).
- Practical-significance summary: forecasting evidence strong; decision evidence
  directionally consistent but budget-dependent; not full-paper ready.

## Strongest safe claim

On real NYC 311 data for 2022-2024, adding deterministic calendar features to an
internal-historical model consistently reduces next-day forecast error across
rolling-origin folds, boroughs, and complaint groups, with real NOAA weather
adding a smaller but consistent further gain on top of calendar, and this
improvement carries through in direction to a stylized staffing-allocation
simulation across scarce, moderate, and generous crew budgets.

## Blocker to full paper

The decision-quality effect is directionally consistent but budget-dependent and
rests on a single stylized allocation heuristic, the real weather signal is a
single-station city-level proxy that adds only a small gain over calendar, and the
study includes no formal forecast-difference testing. These are the gating items
for a full paper.

## Final recommendation

Use as extended abstract/workshop artifact, then pause. See
`candidate_c_final_decision.md`.

## One-paragraph public explanation

This project forecasts the next day's volume of New York City 311 service
requests for each borough and complaint type, using three years of real city
data. Adding simple calendar information (weekday, holiday, month, season) to a
model built only from past request counts consistently improves the forecasts -
across every time period, borough, and complaint type tested - and adding real
daily weather data for the city gives a small additional improvement on top of
that. The project then feeds those forecasts into a simplified crew-allocation
simulation to check whether better forecasts lead to better plans; they do, but
the size of the benefit depends heavily on how tight the crew budget is. The work
is a careful research baseline, not a deployed tool, and it makes no claims about
real city operations.

## One-paragraph academic explanation

Using real NYC 311 records (2022-2024) aggregated to a daily
borough-by-complaint-group panel, augmented with a real NOAA single-station
(NYC Central Park) daily weather layer, we evaluate whether deterministic calendar
features and real weather improve next-day volume forecasts beyond internal lag
and rolling statistics, under a strictly chronological protocol with both a single
70/15/15 split and five-fold rolling-origin validation across four feature sets.
Calendar augmentation reduces MAE for every model in every fold and for every
borough and complaint group, with the largest gains for tree ensembles; calendar
is the dominant signal and real weather adds a smaller but consistent further
gain, so the best model is a random forest on the calendar + weather set (test MAE
55.33). To probe operational relevance, we couple the forecasts to a stylized
proportional staffing-allocation simulation and measure weighted unmet demand
against an oracle bound across three crew budgets; the calendar + weather policy
dominates the internal-only policy in direction at every budget, but the effect
size is budget-dependent. The study is correlational, makes no causal or
deployment claims, and is positioned as a reproducible baseline; its forecasting
result is robust enough for an extended abstract, while a full paper would require
richer external signals beyond a single weather station, formal forecast-difference
tests, and a non-stylized decision model.
