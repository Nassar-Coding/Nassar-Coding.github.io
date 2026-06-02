# Limitations

Sources: `docs/limitations.md`, `research_artifacts/reviewer_risk_register.md`,
`research_artifacts/claims_audit.md`. See also Table 8.

- **311 reporting bias.** 311 records reporting behaviour, not true incidence.
  Reporting propensity varies across communities, channels, and time. Forecasts
  predict reported volume, not underlying need.
- **Borough-level aggregation.** The date x borough x complaint_group panel hides
  within-borough variation (for example community district or ZIP) and intra-day
  timing.
- **Complaint-group coarseness.** A deterministic substring mapping into eight
  groups (plus a residual Other) groups heterogeneous complaint types; alternative
  mappings would shift group-level counts.
- **Single-station weather proxy.** One NOAA Central Park station is joined to
  every borough by date; within-city spatial weather variation is not captured.
  Average temperature is derived from observed daily max/min because the source
  average-temperature column was empty.
- **No transit or event data.** Only weather is added as an external signal in
  this version; transit ridership and event calendars are out of scope here.
- **Stylized decision simulation.** Proportional allocation omits crew travel,
  shifts, backlog carryover, intra-day arrivals, and substitution between cells;
  results characterise the simulation, not real operations.
- **No observed dispatch decisions.** The decision layer is a counterfactual, not
  observed agency behaviour; it is not real dispatch and not staffing
  optimization.
- **No causal inference.** The study is correlational and predictive; no causal
  effect is identified or estimated.
- **External validity.** Results apply to New York City, daily granularity, the
  eight mapped complaint groups, and calendar years 2022-2024 only.

## Full-paper blockers

This artifact is workshop / short-paper / arXiv-style, not full-paper ready. The
gating items for a full paper are:

1. A non-stylized, agency-grounded decision model with an empirical service-level
   realism check (the current decision benefit is directionally consistent but
   budget-dependent and rests on a single stylized heuristic).
2. Formal forecast-difference testing (for example a Diebold-Mariano test) with
   uncertainty intervals, beyond the current consistency-across-folds evidence.
3. Broader external signals beyond a single weather station (for example
   multi-station or gridded weather, transit, events), or cross-city replication.
