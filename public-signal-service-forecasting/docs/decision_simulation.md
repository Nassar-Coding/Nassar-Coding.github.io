# Decision Simulation

## Purpose

The decision simulation connects forecast quality to a stylized operational
decision. A reduction in forecast error does not automatically imply better
decisions, because decision quality depends on the loss structure of the
allocation problem. The simulation makes this link explicit and reproducible.

This is a stylized simulation. **It does not represent real NYC dispatch, real
crew logistics, or any real operational system, and it is not a claim of real
staffing optimization.** It only tests whether forecast differences translate
into simulated allocation differences.

## Staffing allocation model

Each day a fixed budget of service crews is allocated across the borough x
complaint_group cells in proportion to forecasted next-day demand:

1. A forecast is produced for every cell for the next day.
2. The fixed crew budget is distributed across cells in proportion to forecast
   using a largest-remainder method, so the allocation sums exactly to the
   budget. An optional minimum number of crews per cell can guarantee coverage.
3. Each crew provides a configurable capacity (requests handled per day), so a
   cell's capacity equals its crews times the per-crew capacity.
4. Unmet demand in a cell is `max(actual_demand - allocated_capacity, 0)`.

## Policies

One policy is evaluated per feature set; the headline comparison is the
internal-history policy versus the calendar + weather policy, against an
observed-demand oracle benchmark.

- **Internal history:** allocate using the internal-history forecast.
- **Calendar + weather:** allocate using the calendar + weather forecast (the
  headline augmented policy).
- **Observed-demand oracle:** allocate using the observed realized next-day
  request volume. This is an upper-bound benchmark only, is not a forecast, and
  is not achievable in practice.

## Assumptions

- Total crews are fixed and configurable (`TOTAL_CREWS`).
- Each crew handles a fixed number of requests per day (`REQUESTS_PER_CREW`).
- Allocation is proportional to forecast, with an optional per-cell minimum.
- Higher-stakes complaint groups (Public Safety, Water, Traffic) receive larger
  weights in the weighted unmet-demand metric.
- The crew budget is intentionally scarce relative to typical daily demand
  (calibrated to roughly three quarters of mean daily requests), so allocation
  quality has a measurable effect.

## Metrics

- **Total unmet demand** - unmet demand summed across cells and days.
- **Total weighted unmet demand** - the same, weighted by complaint-group
  importance (primary decision metric).
- **Average service shortfall** - mean unmet demand per cell-day.
- **High-demand coverage rate** - fraction of high-demand cell-days (at or above
  the daily 75th percentile of actual demand) whose capacity meets demand.
- **Allocation efficiency** - served demand divided by total allocated capacity.
- **Percent improvement of calendar-augmented over baseline** - relative
  reduction in total weighted unmet demand from baseline to augmented policy.
- **Gap to oracle closed** - the share of the baseline-to-oracle headroom in
  weighted unmet demand that the augmented policy closes (100% would mean the
  augmented policy matches the oracle benchmark).

## Why decision quality matters beyond forecast accuracy

Average forecast accuracy weights all errors symmetrically and equally across
cells. Operational value does not: under a fixed, scarce budget, errors on
high-demand or high-weight cells are far more costly than errors elsewhere, and
the proportional allocation transforms forecasts non-linearly into capacity.
Reporting forecast metrics, decision metrics, and the oracle bound together
gives a more honest picture of whether better forecasts actually help.

## Limitations

- Proportional allocation is a simple heuristic, not an optimized policy.
- The simulation ignores crew travel, shift constraints, backlog carryover,
  intra-day stochastic arrivals, and substitution between cells.
- Complaint-group weights are illustrative, not calibrated to real priorities.
- Results describe this stylized setting and are not real operational savings.
