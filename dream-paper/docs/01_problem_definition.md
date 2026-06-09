# Phase 1 — Scientific Problem Definition

## Phenomenon

Daily volume of reported 311 service requests in large U.S. cities, and the
quality of the daily service-capacity allocation decisions that short-horizon
forecasts of that volume are used to support.

The study explicitly targets **reported demand** (administrative records of
requests), not underlying social need. The two differ because of documented
socio-spatial disparities in reporting behaviour (Kontokosta & Hong, 2021).

## Prediction task

- **Unit of analysis:** (city *c*, harmonized service family *s*, day *t*).
  Service families harmonize each city's native request taxonomy into eight
  operationally analogous families by deterministic, versioned keyword rules
  (`configs/service_families.yml`). Families are *analogous*, not identical,
  across cities; native-category compositions are reported per city and the
  harmonization is treated as a documented modelling choice, not a fact.
- **Target:** next-day request count `y[c,s,t+1]`.
- **Decision time / information cutoff:** end of day *t*. All endogenous
  features (lags, rolling statistics) use data through day *t* only.
  Target-day weather is the realized GHCN-Daily observation for day *t+1*,
  used as a stand-in for a day-ahead weather forecast; this is a documented
  assumption (A3 in the assumption register) tested by a lagged-weather-only
  sensitivity variant.
- **Uncertainty object:** the conditional distribution of `y[c,s,t+1]`,
  represented by quantile forecasts at levels {0.05, 0.25, 0.5, 0.75, 0.95}.

## Operational decision

Each evening, a planner with a fixed city budget of `B_c` interchangeable
crews (each able to resolve `kappa` requests the next day) allocates whole
crews across the eight service families for day *t+1*. Unserved demand
carries over as backlog into following days. Families carry priority weights
(public-safety-like families weighted above amenity-like families). The
decision loss is cumulative priority-weighted unserved demand over the test
period. This is a **stylized simulation** of capacity allocation — not a
deployment, and not a claim about any city's actual dispatch practice.

## Research questions

**Primary (RQ1).** Across multiple city 311 systems and capacity regimes,
when do improvements in next-day forecast accuracy translate into
improvements in downstream allocation quality, and when do the two rankings
diverge?

**Secondary.**
- **RQ2.** Do the public-signal (calendar, weather) accuracy gains observed
  in NYC (Paper 1) replicate in other cities under an identical protocol?
- **RQ3.** Does using forecast *uncertainty* (quantile-based allocation)
  improve decision quality over point-forecast proportional allocation,
  holding the underlying model fixed?
- **RQ4.** Does pooling cities into a single global model help or harm
  per-city forecast accuracy and decision quality (including negative
  transfer)?

## Falsifiable hypotheses

- **H1 (replication).** Calendar-augmented models reduce held-out next-day
  MAE versus internal-history-only models in every city.
  *Falsified if* any city shows no improvement on the final test split.
- **H2 (regime dependence).** The decision-quality gain from a given
  accuracy gain depends systematically on the capacity regime
  (scarce / moderate / generous budgets).
  *Falsified if* relative decision gains are statistically indistinguishable
  across regimes in all cities.
- **H3 (ranking divergence).** For at least one city-regime pair, the model
  ranking by forecast MAE differs from the ranking by decision loss.
  *Falsified if* rankings agree everywhere.
- **H4 (uncertainty value).** Quantile-informed allocation weakly dominates
  proportional point-forecast allocation under scarce capacity.
  *Falsified if* it is worse under scarcity in most cities.
- **H5 (transfer).** A pooled global model changes per-city accuracy by a
  measurable amount; direction is an open empirical question and a negative
  (harmful) transfer result is retained as a finding.

## Dominant contribution

A reproducible multi-city benchmark and evaluation showing **how the mapping
from forecast accuracy to operational decision value varies across cities,
capacity regimes, and uncertainty handling** — extending the single-city
forecast-to-decision analysis of Paper 1 into a cross-city, uncertainty-aware,
backlog-aware setting.

## Scope exclusions

- No sub-city spatial allocation (no false spatial harmonization across
  cities with incompatible geographies).
- No causal claims; the study is predictive and simulational.
- No claim of deployment, city endorsement, or measurement of social need.
- No staffing data: capacity budgets are simulation parameters swept over a
  grid, classified as *sensitivity-only* quantities (Phase 7 register).
- Gulf-region cities are future work: no comparable public request-level
  311 data are currently available to this project.

## Assumption register

| ID | Assumption | Classification | Treatment |
|----|------------|----------------|-----------|
| A1 | Native-category → family keyword mapping is operationally meaningful | defensibly derived | versioned config + per-city composition tables |
| A2 | One GHCN station approximates city-level weather exposure | documented simplification | limitation; consistent with Paper 1 |
| A3 | Realized next-day weather ≈ day-ahead weather forecast | assumed | sensitivity variant with lagged weather only |
| A4 | Crews interchangeable, fixed productivity `kappa` | sensitivity-only | swept; stylization stated everywhere |
| A5 | Backlog carries over without abandonment | sensitivity-only | abandonment-rate sensitivity |
| A6 | Priority weights (safety-like > amenity-like) | assumed | varied in sensitivity analysis |
| A7 | Reported demand is the planning-relevant signal | scope condition | responsible-AI section addresses divergence from need |

## Validity threats

1. **Construct:** harmonized families may not be comparable workloads across
   cities → report native compositions; never claim identity.
2. **Internal:** leakage through rolling features or target-day weather →
   leakage unit tests; lagged-weather sensitivity.
3. **External:** four U.S. cities with Socrata portals are not "cities in
   general" → stated; city selection criteria documented in Phase 3.
4. **Statistical:** correlated errors across families/days → blocked
   temporal evaluation, paired bootstrap on daily totals.
5. **Simulation realism:** decision results conditional on A4–A6 → full
   parameter sweeps; conclusions restricted to qualitative regime patterns.

## Advancement gate (Phase 1)

The problem is operationally defined (unit, cutoff, target, loss all exact),
falsifiable (H1–H5), and testable with real public data. PASS.
