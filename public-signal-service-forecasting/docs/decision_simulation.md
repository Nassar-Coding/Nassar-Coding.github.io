# Decision Simulation

## Purpose

The decision simulation connects forecast quality to a stylized operational
decision. It exists because a reduction in forecast error does not automatically
imply better decisions: decision quality depends on the loss structure of the
allocation problem. The simulation makes this link explicit, transparent, and
reproducible.

This is a stylized simulation. **It does not represent real agency dispatch, real
crew logistics, or any real operational system.**

## Staffing allocation model

Each day, a fixed budget of service crews is allocated across the 35
borough x complaint-group cells in proportion to forecasted next-day demand:

1. A forecast is produced for every cell for the next day.
2. The fixed crew budget is distributed across cells in proportion to forecasted
   demand using a largest-remainder method, so the allocation sums exactly to the
   budget. An optional minimum number of crews per cell can guarantee baseline
   coverage.
3. Each crew provides a configurable capacity (requests handled per day), so each
   cell receives a capacity equal to its crews times the per-crew capacity.
4. Unmet demand in a cell is `max(actual_demand - allocated_capacity, 0)`.

## Policies

- **Baseline policy:** allocate using the internal-only forecast.
- **Augmented policy:** allocate using the public-signal augmented forecast.
- **Oracle policy:** allocate using true next-day demand. This is a benchmark
  upper bound only and is not achievable in practice.

## Assumptions

- Total crews are fixed and configurable (`TOTAL_CREWS`).
- Each crew handles a fixed number of requests per day (`REQUESTS_PER_CREW`).
- Allocation is proportional to forecasted demand, with an optional per-cell
  minimum (`MIN_CREWS_PER_CELL`).
- Higher-stakes complaint groups (Public Safety, Water, Traffic) receive larger
  weights in the weighted unmet-demand metric.
- The default crew budget is intentionally scarce relative to typical daily
  demand, so that allocation quality has a measurable effect.

## Metrics

- **Total weighted unmet demand** - unmet demand summed across cells and days,
  weighted by complaint-group importance (primary decision metric).
- **Average service shortfall** - mean unmet demand per cell-day.
- **High-demand coverage rate** - fraction of high-demand cell-days (at or above
  the daily 75th percentile of actual demand) whose capacity meets actual demand.
- **Allocation efficiency** - served demand divided by total allocated capacity.
- **Percent improvement of augmented over baseline** - relative reduction in
  total weighted unmet demand from the baseline policy to the augmented policy.

## Why decision quality matters beyond forecast accuracy

Average forecast accuracy weights all errors symmetrically and equally across
cells. Operational value does not: under a fixed, scarce budget, errors on
high-demand or high-weight cells are far more costly than errors elsewhere, and
the proportional allocation transforms forecasts non-linearly into capacity.
Reporting both forecast metrics and decision metrics, together with the oracle
bound, gives a more honest picture of whether better forecasts actually help.

## Limitations

- Proportional allocation is a simple heuristic, not an optimized policy.
- The simulation ignores crew travel, shift constraints, carryover backlog,
  stochastic intra-day arrivals, and substitution between cells.
- Complaint-group weights are illustrative, not calibrated to real priorities.
- Results, especially under the synthetic fallback, describe the modelled setting
  and should not be read as real operational savings.
