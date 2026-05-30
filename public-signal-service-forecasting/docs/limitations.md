# Limitations

This baseline is intentionally scoped. The limitations below should be read
alongside every reported result.

## Data limitations

- The default data mode is a deterministic synthetic fallback. Results obtained
  in this mode describe the modelled generating process, not real demand.
- Synthetic weather and event signals are stylized proxies, not measurements.
- The scope is a single city at daily granularity over five boroughs and seven
  complaint groups. Other cities, finer time scales, or other service types are
  out of scope.
- No personal or fine-grained data is used, which bounds the achievable
  resolution of any analysis.

## Modeling limitations

- Only classical models are used (naive baseline, Ridge, random forest, gradient
  boosting). No deep learning, probabilistic, or hierarchical forecasting is
  included.
- Hyperparameters are fixed at reasonable defaults rather than tuned through an
  extensive search.
- Point forecasts are produced without calibrated uncertainty intervals.
- The single chronological split provides one held-out evaluation rather than a
  rolling-origin or cross-validated estimate of generalization.

## Decision simulation limitations

- Allocation is a simple proportional heuristic, not an optimized policy.
- Crew travel, shift constraints, backlog carryover, intra-day stochastic
  arrivals, and substitution effects are ignored.
- Complaint-group weights are illustrative, not calibrated.
- The simulation is stylized and does not represent real dispatch or quantify
  real operational value.

## External validity limitations

- Findings do not generalize beyond the modelled setting and assumptions.
- The relative value of public signals depends on the data-generating process and
  may differ substantially with real data, other regions, or other horizons.

## Causal inference limitations

- The project is correlational and predictive, not causal.
- It does not identify or estimate the causal effect of weather, events, or any
  signal on service demand.
- Improvements in forecast accuracy or decision metrics must not be interpreted as
  causal evidence.
