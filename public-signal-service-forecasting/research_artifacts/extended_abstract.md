# From Forecast Accuracy to Operational Value: Calendar- and Weather-Augmented Forecasting for NYC 311 Service Requests

## Abstract

Day-ahead forecasts of service-request volume are a natural input to
short-horizon staffing and dispatch planning in municipal operations. Yet
improvements in average forecast accuracy do not automatically translate into
better operational decisions, because decision quality depends on the loss
structure of the downstream allocation problem rather than on symmetric average
error. This work presents a reproducible real-data baseline that evaluates both
sides of this gap on New York City 311 Service Requests for calendar years
2022-2024 augmented with real NOAA daily weather for the NYC Central Park
station. We forecast next-day request volume at the date x borough x
complaint_group level and compare four feature sets - internal-historical (lagged
and rolling statistics of the series), calendar-augmented (internal features plus
deterministic calendar indicators), weather-augmented (internal features plus the
real weather variables), and calendar + weather augmented - under four model
families and a strictly chronological validation protocol. We then connect the
forecasts to a stylized staffing-allocation simulation that distributes a fixed,
scarce crew budget in proportion to the forecast, and we measure decision quality
with weighted unmet demand and related metrics, including the share of the gap to
an oracle policy that each forecast closes. Calendar augmentation is the dominant
signal and reduces test mean absolute error for every model; real weather adds a
smaller but consistent further gain on top of calendar. The best model (a random
forest on the calendar + weather set) attains a held-out test MAE of 55.33 versus
71.85 for the naive seasonal baseline, a 23.0% reduction, and the resulting
allocation improves weighted unmet demand by about 1.89%, closing roughly 26% of
the baseline-to-oracle gap at the baseline crew budget. The consistent but
attenuated transfer from forecast accuracy to decision quality is the central
empirical observation. The study is correlational, uses only observed public
data, and makes no causal, deployment, or operational-optimization claims.

## Problem definition

Consider a service operation that receives complaint-driven requests and must
plan capacity one day in advance. For each operational cell - here a combination
of borough and complaint category - the planner would like a forecast of the next
day's request volume in order to position a limited number of crews. Two
questions follow. First, a predictive question: does augmenting an internal,
history-only forecasting model with calendar and temporal structure reduce
next-day forecast error? Second, a decision question: does any such forecast
improvement actually improve the quality of a capacity allocation built on top of
the forecast?

These questions are related but distinct. Mean absolute error weights all errors
equally across cells and days. An operational allocation does not: under a fixed,
scarce budget, an error on a high-volume or high-priority cell can be far more
consequential than an error on a quiet one, and a proportional allocation maps
forecasts to capacity in a way that is not linear in the forecast error. A study
that reports only forecast metrics therefore risks overstating - or, in
principle, understating - operational relevance. We treat the decision layer as a
first-class evaluation target.

## Data and methodology

The data is real NYC 311 Service Requests obtained from NYC Open Data (Socrata
dataset `erm2-nwe9`). We restrict attention to calendar years 2022-2024 and to
four raw fields: created date, borough, complaint type, and a unique request
identifier. The 36 monthly exports were reduced locally to observed daily counts;
the pipeline read 9,851,452 raw records and retained 9,838,988 after dropping
12,464 rows with invalid or unspecified borough and applying the study-window
filter (no rows had unparseable or out-of-window dates). Complaint types are
mapped to eight groups (Noise, Housing, Sanitation, Street Condition, Water,
Traffic, Public Safety, and a residual Other) using a deterministic,
order-sensitive substring rule in which Housing is evaluated before Water so that
heat and hot-water complaints are not absorbed by the Water rule. The processed
modelling panel contains 43,240 rows over date x borough x complaint_group cells,
spanning observed dates 2022-01-15 to 2024-12-30 after lag and rolling warmup.

A real weather layer was added in this closure pass. The source is NOAA NCEI
Daily Summaries (GHCN-Daily), station USW00094728 (NYC Central Park), for
2022-2024 (1,096 days), with variables precipitation_mm, temp_max_c, temp_min_c,
temp_avg_c, snowfall_mm, snow_depth_mm, and wind_speed_ms. Because the source
TAVG column was empty for this station, temp_avg_c is derived as the mean of
observed daily maximum and minimum temperature, and five missing wind-speed days
are filled by time interpolation of neighbouring real observations; no synthetic
weather is generated. A single Central Park station is used as a city-level proxy,
which is a documented spatial-resolution limitation.

The forecasting target is the observed next-day request volume for each cell,
computed only from observed records and defined only when consecutive calendar
days are present. Four feature sets are compared. The internal-historical set
contains the borough and complaint group plus lag-1, lag-7, and rolling mean and
standard deviation over 7 and 14 days. The calendar-augmented set adds is_weekend,
is_holiday, day_of_week, month, quarter, year, day_of_year, week_of_year,
is_month_start, and is_month_end. The weather-augmented set adds the real NOAA
daily weather variables to the internal-historical features, and the
calendar + weather augmented set adds both the calendar indicators and the weather
variables. No transit or event data is used. All lag and rolling features are
computed within each cell using only past observations, with rolling statistics
shifted by one day to prevent same-day or future leakage.

We evaluate four model families: a naive seasonal baseline that predicts the
trailing seven-day mean, Ridge regression, a random forest, and gradient
boosting. Categorical features are one-hot encoded inside a pipeline; numeric
features pass through. Validation uses a strictly chronological split by date -
70% of dates for training (30,240 rows), the next 15% for validation (6,480),
and the latest 15% for test (6,520) - so no future date informs an earlier
partition. The primary selection metric is mean absolute error; we also report
RMSE, MAPE with safe handling of near-zero actuals, and R-squared. The best
configuration by validation MAE is refit on train plus validation before the
final test evaluation.

The decision layer is a stylized staffing-allocation simulation. Each test day, a
fixed budget of 135 crews, each able to handle 50 requests, is distributed across
cells in proportion to the forecast using a largest-remainder rule (capacity is
calibrated to roughly three quarters of mean daily demand, making the budget
deliberately scarce). Unmet demand in a cell is the positive part of actual demand
minus allocated capacity; weighted unmet demand assigns higher weight to Public
Safety, Water, and Traffic. We compare policies driven by each forecast feature
set over 163 test days against a baseline driven by the internal-historical
forecast and an oracle policy driven by true next-day demand that serves only as
an upper bound; the headline comparison is the calendar + weather augmented policy
versus the internal-historical baseline.

## Results

Calendar augmentation improves forecast accuracy for every model on the test
partition. Test MAE falls from 65.28 to 58.08 for the random forest (an 11.03%
improvement), from 67.49 to 61.71 for gradient boosting (8.57%), and from 69.22 to
68.76 for Ridge (0.67%). Calendar is the dominant signal; real weather adds a
smaller but consistent further gain on top of it. For the random forest,
weather-only test MAE (64.10) beats internal-historical (65.28), and the
calendar + weather set (56.22) beats calendar-only (58.08); Ridge does not benefit
from weather (weather 69.28, calendar + weather 68.92 against internal 69.22). The
selected model is the calendar + weather augmented random forest, refit on
train+validation, with test MAE 55.33, RMSE 177.48, MAPE 27.47%, and R-squared
0.648; it improves on the naive seasonal baseline (test MAE 71.85) by 23.0%.
Errors are concentrated in the highest-volume segments - the Noise and Housing
complaint groups and the Bronx - and are smallest for Staten Island and low-volume
groups, consistent with absolute error scaling with cell volume.

In the decision simulation, total weighted unmet demand is 643,324 under the
internal-historical baseline, 634,614 under the calendar-augmented policy, 641,382
under the weather-augmented policy, 631,191 under the calendar + weather augmented
policy, and 597,332 under the oracle. The calendar + weather augmented policy
reduces weighted unmet demand by 1.886% relative to the baseline and closes
26.381% of the baseline-to-oracle gap. The high-demand coverage rate stays low
across all non-oracle policies, reflecting a budget that cannot cover peak cells
regardless of forecast quality.

The headline observation is the contrast in magnitudes: an approximately 23%
forecast-accuracy gain for the best model over naive corresponds to an
approximately 1.89% decision-quality gain. The transfer from accuracy to
operational value is real and directionally consistent but strongly attenuated,
which is precisely the effect a joint forecast-and-decision evaluation is meant to
surface.

A robustness package confirms that the forecasting result is not an artifact of a
single split. Five-fold expanding-window rolling-origin validation shows calendar
augmentation lowering MAE in every fold for every model (mean improvement 15.1%
for the random forest, 9.9% for gradient boosting, 0.9% for Ridge); in mean fold
test MAE the random forest improves from internal (57.03) through weather (56.22)
and calendar (48.69) to calendar + weather (47.50). The improvement holds for all
five boroughs (about 8.8% to 18.8%) and all eight complaint groups (about 8.9% to
25.8%). A crew-budget sensitivity sweep shows the calendar + weather allocation
policy dominating the internal-only policy in direction under scarce, moderate,
and generous budgets, while the magnitude of the decision benefit grows with
capacity (weighted-unmet reductions of 0.38%, 4.32%, and 14.53% respectively). The
forecasting evidence is thus robust; the decision evidence is directionally robust
but budget-dependent.

## Managerial and operational implications

For planners, the result is a caution and a method rather than a recommendation.
The caution is that reporting forecast accuracy alone can misrepresent operational
value; a model that wins on MAE may deliver only a fraction of that advantage once
it passes through a capacity-constrained allocation. The method is to evaluate the
decision metric directly and to bound it with an oracle, so that the realized gain
can be read against the maximum achievable gain. In this baseline, the
calendar + weather forecast is preferable on both forecast and decision grounds,
but the practical size of the decision benefit is modest and is dominated by the
scarcity of the capacity budget. None of this constitutes a real staffing policy:
the allocation is a transparent heuristic on observed reporting data, not a
validated dispatch rule.

## Limitations

The study is correlational and makes no causal claim about the effect of calendar
factors on demand. NYC 311 reflects reporting behaviour rather than true
incidence, so forecasts predict reported volume, not underlying need, and may
encode reporting biases that vary across communities and time. Borough-level
aggregation hides within-borough heterogeneity, and the complaint-group mapping is
a deterministic approximation with a residual Other category. The decision layer
is a single stylized heuristic that omits crew travel, shifts, backlog carryover,
intra-day arrival timing, and substitution between cells; its results characterize
the simulation, not real operations. A single chronological split yields one
held-out estimate rather than a distribution, and findings do not generalize
beyond New York City, daily granularity, and the 2022-2024 window. The work is a
research baseline, not a finished paper, and is not production-ready or deployed.

## Future work

Three extensions are natural. First, extend the external-signal layer beyond a
single weather station - for example multi-station or gridded weather - and add
further no-key public signals, with full documentation, to test whether richer
exogenous signals add more value beyond calendar structure than the modest gain
observed here. Second, strengthen the evaluation with rolling-origin
cross-validation and formal statistical tests for both forecast-accuracy
differences and decision-quality differences across policies. Third, develop the
decision layer from a proportional heuristic toward a constrained allocation with
explicit service-level targets, and study sensitivity to the crew budget and the
complaint-group weights, while analyzing reporting bias and considering finer
geography within the no-personal-data boundary.
