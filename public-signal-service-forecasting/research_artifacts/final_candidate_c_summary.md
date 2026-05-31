# Final Candidate C Summary

## Project title

Public Signal Service Forecasting: calendar-augmented next-day forecasting and
stylized staffing decision simulation on real NYC 311 data.

## Dataset facts

- Source: NYC 311 Service Requests (NYC Open Data, `erm2-nwe9`); data mode
  `real_nyc_311`; no synthetic data, no synthetic fallback.
- Study window 2022-01-01 to 2024-12-31; 36 monthly files.
- Raw records read: 9,851,452; retained after filtering: 9,838,988.
- Processed rows: 43,240; five boroughs; eight complaint groups; unit
  date x borough x complaint_group; target `request_volume_next_day`.

## Model facts

- Best model: random forest, calendar-augmented feature set.
- Single-split test metrics: MAE 57.26, RMSE 182.21, MAPE 28.05%, R-squared
  0.629; 20.3% better than the naive seasonal baseline (MAE 71.85).
- Calendar augmentation lowers single-split test MAE for every model (random
  forest 11.03%, gradient boosting 8.57%, Ridge 0.67%).

## Decision simulation facts

- Stylized proportional allocation of a fixed crew budget; weighted unmet demand
  is the primary metric. Not real dispatch and not real optimization.
- At the baseline configuration (135 crews, 50 requests/crew): weighted unmet
  demand falls from 643,324.5 (internal) to 634,613.5 (calendar augmented),
  a 1.35% reduction that closes 18.94% of the baseline-to-oracle gap.

## Robustness facts

- Rolling-origin (5 chronological folds): calendar augmentation wins every fold
  for every model (random forest +15.13% mean, gradient boosting +9.94%, Ridge
  +0.94%).
- Borough robustness: improved in all 5 boroughs (about 4.7% to 15.8%).
- Complaint-group robustness: improved in all 8 groups (about 5.8% to 25.7%).
- Decision sensitivity: calendar-augmented policy better in all three crew
  budgets, but budget-dependent (0.21% scarce, 3.19% moderate, 12.05% generous).
- Practical-significance summary: forecasting evidence strong; decision evidence
  directionally consistent but budget-dependent; not full-paper ready.

## Strongest safe claim

On real NYC 311 data for 2022-2024, adding deterministic calendar features to an
internal-historical model consistently reduces next-day forecast error across
rolling-origin folds, boroughs, and complaint groups, and this improvement
carries through in direction to a stylized staffing-allocation simulation across
scarce, moderate, and generous crew budgets.

## Blocker to full paper

The decision-quality effect is directionally consistent but budget-dependent and
rests on a single stylized allocation heuristic, and the study includes no
external (non-calendar) signal comparison and no formal forecast-difference
testing. These are the gating items for a full paper.

## Final recommendation

Use as extended abstract/workshop artifact, then pause. See
`candidate_c_final_decision.md`.

## One-paragraph public explanation

This project forecasts the next day's volume of New York City 311 service
requests for each borough and complaint type, using three years of real city
data. Adding simple calendar information (weekday, holiday, month, season) to a
model built only from past request counts consistently improves the forecasts -
across every time period, borough, and complaint type tested. The project then
feeds those forecasts into a simplified crew-allocation simulation to check
whether better forecasts lead to better plans; they do, but the size of the
benefit depends heavily on how tight the crew budget is. The work is a careful
research baseline, not a deployed tool, and it makes no claims about real city
operations.

## One-paragraph academic explanation

Using real NYC 311 records (2022-2024) aggregated to a daily
borough-by-complaint-group panel, we evaluate whether deterministic calendar
features improve next-day volume forecasts beyond internal lag and rolling
statistics, under a strictly chronological protocol with both a single 70/15/15
split and five-fold rolling-origin validation. Calendar augmentation reduces MAE
for every model in every fold and for every borough and complaint group, with the
largest gains for tree ensembles. To probe operational relevance, we couple the
forecasts to a stylized proportional staffing-allocation simulation and measure
weighted unmet demand against an oracle bound across three crew budgets; the
augmented policy dominates the internal-only policy in direction at every budget,
but the effect size is budget-dependent. The study is correlational, makes no
causal or deployment claims, and is positioned as a reproducible baseline; its
forecasting result is robust enough for an extended abstract, while a full paper
would require external-signal comparison, formal forecast-difference tests, and a
non-stylized decision model.
