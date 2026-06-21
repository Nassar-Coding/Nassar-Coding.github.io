# Draft 3 — Stage 3 Cold-Read Packet

**INTERNAL DOCUMENT — never include on the public release branch.**
For a cold reader to run AFTER Stage 3 (not by the Stage-3 agent). Source of
truth is `paper/main_ieee.pdf` (10 pp); excerpts below are for convenience.

## Title

Next-Day Reported Municipal Service-Demand Forecasting Across Four Cities:
A Reproducible Benchmark with Simulated Allocation Evaluation

## Identity sentence (abstract/intro opener)

"We present a reproducible multi-city benchmark for next-day reported municipal
service-demand forecasting and evaluate how forecast representations behave when
embedded in a controlled request-equivalent allocation simulation."

## Abstract

(See `paper/sections/abstract.tex` / `main_ieee.pdf` p.1 — identity opener;
4-city benchmark 36.8M/30.2M; reported-demand-not-need + simulation-not-
deployment boundary; calendar 10.0–14.0%, weather 3/4 + null, pooling hurts 3/4
robust to normalization; non-identification 92–100% ties; naive fixed-index
default loses to proportional in 12/12, proportional rule recovers it and a
quantile-interpolated distribution recovers most of the gap; bounded principle;
aggregate loss ≠ fairness; one-command reproducible.)

## Contribution bullets (intro)

1. **Benchmark and protocol** — four-city reported-demand benchmark, common
   service-family schema, leakage-controlled temporal evaluation, one-command
   reproducible artifact.
2. **Forecasting evidence** — calendar/weather/public-signal value; local vs
   pooled and censored transfer; uncertainty representation; Poisson count
   baseline; negative/null findings reported.
3. **Forecast-to-decision evaluation** — controlled request-equivalent
   allocation simulation; point-forecast non-identification; tie-break
   dependence; distributional representation recovers most of the fixed-index
   gap.
4. **Responsible use and veracity** — reported demand ≠ social need; aggregate
   loss ≠ fairness (family-level served fractions disclosed); provenance/guards.

## Related-work delta paragraph (prior single-city work)

"An earlier single-city study on NYC 311 by the present author brought this
template to municipal reported demand in one city. The present work differs in
scope and in kind: four heterogeneous 311 systems under one leakage-controlled
protocol; local-vs-pooled and temporally censored cross-city transfer;
forecast-to-decision coupling via a controlled allocation simulation;
characterization of point-forecast non-identification, tie-break dependence, and
family-level served-fraction tradeoffs; and a stronger provenance- and
guard-backed reproducible benchmark." (Formal citation pending — prior paper
under review.)

## Decision-section summary

Controlled scenario diagnostic (not deployment/staffing/causal). Under the equal
request-equivalent objective a degenerate point forecast leaves the objective
non-identified (92–100% tied steps); the realized outcome is set by the secondary
tie-break rule. The naive fixed-index default loses to proportional in all 12
cells (1.2–58%); a proportional secondary rule recovers proportional, and the
quantile-interpolated distribution recovers most of the gap. Bounded design
lesson; aggregate loss reductions are not fairness guarantees.

## Conclusion

(See `paper/sections/conclusion.tex` — benchmark discipline; calendar helps,
weather heterogeneous, pooling/transfer mostly hurt; non-identification and
tie-break dependence; aggregate loss hides family-level tradeoffs; report
boundaries and failure modes, not only aggregate gains.)

## Reviewer instructions (answer after reading the 10-page PDF)

1. What is the paper's main contribution in one sentence?
2. Is this more than "LightGBM on 311 data"?
3. Is the benchmark identity clear?
4. Is the decision layer understandable as a controlled simulation?
5. Does the non-identification result sound trivial, or does the paper explain
   why the empirical characterization matters?
6. Are the boundaries (reported demand, simulation, no deployment) clear?
7. What is the strongest rejection reason after reading?
8. Which one paragraph should be rewritten before submission?
9. Does the prior single-city distinction make the current contribution clear?
10. Does the paper over-hedge the decision layer into a toy, or convey a real,
    bounded design lesson?

## Post-Stage-3 decision gate (record, do not act now)

Per the Stage-3 prompt: decide on **exactly one** serious modern baseline only
if the cold reader still reads the paper as "LightGBM on 311 data / dated
baselines." If the contribution reads as a benchmark + forecast-to-decision
evaluation, add no baseline. If the decision layer reads as unclear/trivial, fix
framing, not models.
