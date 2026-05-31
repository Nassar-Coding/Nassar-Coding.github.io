# Public Signal Service Forecasting: Project Summary

## What this project does

This project is a reproducible, real-data machine-learning baseline for
forecasting next-day service-request volume in New York City and for testing
whether better forecasts lead to better operational decisions. It forecasts the
number of NYC 311 service requests for the next calendar day, separately for each
combination of borough and complaint category, and then feeds those forecasts
into a transparent staffing-allocation simulation to measure their operational
value.

## Why the problem matters

Service organizations plan limited crews against demand that shifts by day of
week, season, and location. Day-ahead forecasts are a natural planning input, but
a forecast that looks accurate on average is not necessarily useful for
decisions: under a tight capacity budget, mistakes on busy or high-priority cells
matter far more than mistakes on quiet ones. The project is built around this
distinction. It evaluates both how accurate the forecasts are and how much that
accuracy actually helps a downstream allocation, which is the gap that purely
predictive studies tend to leave unexamined.

## What data is used

The project uses real NYC 311 Service Requests from NYC Open Data for calendar
years 2022 through 2024. The 36 monthly exports were reduced locally to observed
daily counts; the pipeline processed 9,851,452 raw records and retained
9,838,988 after removing rows with invalid boroughs and applying the
study-window filter. The modelling dataset has 43,240 rows at the
date-by-borough-by-complaint-group level, covering all five boroughs and eight
complaint groups (Housing, Noise, Public Safety, Sanitation, Street Condition,
Traffic, Water, and a residual Other). No synthetic data is used anywhere; if
real data is unavailable, the pipeline stops with a clear error rather than
fabricating values.

## What models are compared

Four model families are compared: a naive seasonal baseline, Ridge regression, a
random forest, and gradient boosting. Each is trained on two feature sets - an
internal-historical set built only from past request counts (lags and rolling
mean/standard deviation), and a calendar-augmented set that adds deterministic
calendar features such as weekend, holiday, day of week, month, quarter, year,
and week of year. Evaluation uses a strictly chronological split (the earliest
70% of dates for training, the next 15% for validation, the latest 15% for test),
so the model is always tested on dates later than those it learned from.

## What the result shows

Adding calendar features improves accuracy for every model, and most for the best
model, a random forest: its test mean absolute error falls from 65.3 to 58.1, an
11% improvement. The selected calendar-augmented random forest reaches a test MAE
of about 57.3 and beats the naive baseline by about 20%. In the staffing
simulation - where a fixed, deliberately scarce crew budget is allocated in
proportion to the forecast - the calendar-augmented forecast reduces weighted
unmet demand by about 1.35% over the internal-only baseline and closes roughly
19% of the gap to an idealized oracle that knows true demand.

The forecasting improvement is robust: across five rolling time windows it holds
for every model, and on the test period it holds for every borough and every
complaint type. The staffing benefit holds in direction across tight, moderate,
and generous crew budgets, but its size grows with the budget, so the operational
payoff is real yet conditional rather than guaranteed.

## Why the decision simulation matters

The most informative result is the contrast between the two numbers: an 11% gain
in forecast accuracy produces only about a 1.35% gain in the decision metric. The
improvement is real and consistent in direction, but much smaller than the
accuracy gain alone would suggest, because a scarce budget and the concentration
of demand in a few large cells limit how much any forecast can help. This is
exactly why the project measures decision quality directly instead of assuming
that a better forecast is automatically a better plan.

## Limitations

The work is correlational and makes no causal claims. NYC 311 data reflects who
reports and how requests are categorized, not true underlying need, so forecasts
predict reported volume and may carry reporting biases. Borough-level aggregation
hides finer variation, and the complaint-group mapping is a deterministic
approximation. The staffing simulation is a stylized heuristic; it is not real
dispatch, not a staffing optimization, and not validated against any real policy.
Results apply to New York City and the 2022-2024 window and should not be assumed
to generalize. This is a research baseline, not a finished paper or a
production system.

## How to reproduce it

Install the dependencies, place the aggregated daily-counts file in `data/raw/`
(or run the included local aggregation script over the monthly exports), then run
the pipeline end to end:

```bash
pip install -r requirements.txt
python -m src.build_dataset
python -m src.train
python -m src.evaluate
python -m src.decision_simulation
python -m src.monitor
streamlit run app.py
```

Tests and linting run offline with `pytest` and `ruff check .`, using a small
committed real-schema sample so the full pipeline can be exercised quickly in
continuous integration.
