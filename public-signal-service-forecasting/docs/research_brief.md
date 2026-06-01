# Research Brief

## Research question

Can real NYC 311 service-request history, calendar features, and temporal lag
features forecast next-day service-request volume, and does improved forecast
accuracy translate into improved stylized staffing allocation decisions?

## Motivation from operations management

Municipal and service organizations must allocate finite crews against demand
that is uncertain and time-varying. Forecasting daily service-request volume and
allocating capacity against it is a classic operations-management problem at the
intersection of demand forecasting and capacity allocation. A recurring question
in technology-and-operations-management and information-systems research is
whether additional structure - here, calendar and temporal features - adds value
beyond an organization's own internal request history, and whether any
predictive gain actually improves decisions.

## Why the target is observed

The target is the observed count of real 311 requests on the next calendar day
for each borough x complaint_group cell. It is computed only from observed
public records, never simulated. This keeps the predictive claim grounded in
real demand rather than an assumed generating process.

## Baseline vs calendar-augmented comparison

The study compares two feature sets under identical models and an identical
chronological validation protocol:

- **Internal historical:** borough, complaint_group, and lag/rolling statistics
  (lag-1, lag-7, rolling mean and standard deviation over 7 and 14 days).
- **Calendar augmented:** all internal-historical features plus deterministic
  calendar features (weekend, holiday, day-of-week, month, quarter, year,
  day-of-year, week-of-year, month-start, month-end).

Each feature set is trained with a naive seasonal baseline, Ridge regression, a
random forest, and gradient boosting. The primary selection metric is MAE on a
held-out, chronologically later test set. The comparison spans four feature sets:
internal-historical, calendar-augmented, weather-augmented (real NOAA daily
weather for the NYC Central Park station, a genuinely external public signal used
as a single-station city-level proxy), and calendar + weather augmented. No
transit or event data is included in this version, and no synthetic weather is
generated.

## Decision-link logic

A stylized staffing-allocation simulation distributes a fixed, scarce crew
budget across cells in proportion to forecasted next-day demand. Three policies
are compared: baseline (internal-historical forecast), calendar-augmented, and
an oracle (true next-day demand) upper bound. Decision quality is measured with
total and weighted unmet demand, average shortfall, high-demand coverage,
allocation efficiency, the percent improvement of augmented over baseline, and
the share of the gap to the oracle that the augmented policy closes.

## What this repository can and cannot show

It **can**:

- quantify whether calendar/temporal augmentation reduces forecast error on real
  NYC 311 data under a leakage-controlled chronological protocol;
- demonstrate a transparent, reproducible link from forecast quality to a
  stylized operational decision metric;
- provide a clean, testable real-data baseline for further study.

It **cannot**:

- prove a causal effect of calendar factors on service demand;
- represent real agency dispatch, real crew logistics, or real operational value;
- generalize beyond the modelled one-city, daily, borough x complaint-group
  scope and the 2022-2024 window;
- substitute for a validated, peer-reviewed study.

## How this could evolve into a paper

Natural extensions include: adding genuinely external no-key public signals
(for example weather) with full documentation; probabilistic and hierarchical
forecasting; rolling-origin cross-validation; formal statistical tests for
forecast-accuracy differences (for example Diebold-Mariano) and for
decision-quality differences across policies; a constrained-optimization
formulation of the allocation problem with service-level constraints; and
analysis of reporting bias in 311 data.
