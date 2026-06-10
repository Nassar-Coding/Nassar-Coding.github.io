# Independent Full-Repository Scientific Proofs — Consolidated Findings

## Purpose

The complete research package was subjected to two independent full-repository scientific proofs.

Each proof examined the project as an integrated research system, including:

- raw-data provenance;
- acquisition manifests;
- preprocessing;
- harmonization;
- forecasting code;
- chronological evaluation;
- transfer experiments;
- probabilistic forecasting;
- decision simulation;
- capacity construction;
- model-selection logic;
- statistical outputs;
- tables and figures;
- manuscript;
- supplement;
- decision logs;
- tests;
- environment specifications;
- and reproducibility claims.

The purpose was not to obtain stylistic feedback or general opinions.

The purpose was to determine whether:

1. the executable code matched the stated protocol;
2. the reported results matched what the code actually computed;
3. the scientific claims were supported by the experimental design;
4. the operational interpretation was proportionate to the observed evidence;
5. the repository was internally consistent and reproducible;
6. the paper could advance without redesign.

Both proofs independently reached the same governing conclusion:

> **REDESIGN**

The project remains scientifically valuable and worth pursuing, but the current decision-layer results and several headline claims cannot be treated as valid final evidence.

---

# 1. Shared Final Judgment

Both proofs agree that the project should not be stopped.

The following foundations are substantial and salvageable:

- official multi-city data acquisition;
- raw aggregate preservation;
- source manifests and checksums;
- chronological panel construction;
- deterministic service-family harmonization;
- four-city forecasting infrastructure;
- simple and advanced forecasting baselines;
- local and pooled forecasting models;
- rolling-origin evaluation;
- quantile forecast generation;
- the core allocation engine;
- deterministic experiment generation;
- reproducibility-oriented repository structure.

However, both proofs also agree that the current paper cannot advance unchanged because several defects alter the experimental estimand itself.

These are not merely manuscript-language problems.

They require:

- protocol correction;
- code correction;
- automated guards;
- experiment reruns;
- regenerated outputs;
- narrower claims;
- and a rewritten paper after the corrected results exist.

---

# 2. Independently Confirmed Invalidating Defects

## 2.1 Test outcomes determine capacity regimes

The current decision code constructs scarce, moderate, and generous capacity regimes from realized mean demand in the final test window.

This means the test outcomes help define the environment in which the policies are evaluated.

Consequences:

- the test period is not untouched;
- the capacity-to-demand relation is partly imposed retrospectively;
- regime comparisons are contaminated;
- all current decision-layer results must be rerun.

Both proofs classify this as an invalidating design defect.

## 2.2 Validation and test decision environments are inconsistent

The validation-stage decision selection and final test-stage evaluation use separately recalculated budgets.

Therefore, a model may be selected under one simulated operating regime and evaluated under another.

This breaks the intended validation-to-test logic.

The same frozen capacity budgets must be used for both model selection and final evaluation.

## 2.3 Headline forecasting results use test-set selection

The current reporting code identifies the minimum test MAE within a feature set and presents that as the headline result.

The underlying per-configuration measurements may be valid, but the headline selection procedure is not.

Consequences:

- the test set influences which model is presented as best;
- the stated untouched-test protocol is violated;
- significance tests and headline comparisons may refer to different estimands;
- affected forecast tables and figures must be regenerated using validation-only selection.

## 2.4 Zero-shot transfer uses future source-city data

The current leave-one-city-out experiment trains on all available dates from the source cities.

This allows contemporaneous and later source-city observations to enter training relative to the held-out city’s test period.

Consequences:

- the transfer estimates are temporally leaked;
- the reported zero-shot degradation cannot be treated as final evidence;
- the experiment must be rerun with stage-specific temporal censoring or removed.

## 2.5 The uncertainty experiment is confounded

The current point-policy and quantile-policy comparison uses separately trained models, different objectives, and different training procedures.

Therefore, the contrast does not isolate the value of distributional information.

A valid primary comparison must use the same fitted probabilistic model and compare:

- a collapsed point representation;
- versus the full predictive distribution.

All other inputs must remain identical.

## 2.6 The oracle-gap metric is invalid

The current hindsight reference is myopic under carryover dynamics.

It is not a horizon-optimal upper bound and may be exceeded.

Consequences:

- “oracle gap closed” is mathematically misleading;
- values above 100% demonstrate that the reference is not a valid bound;
- “oracle,” “achievable range,” “gap closed,” and related terminology must be removed;
- raw loss and baseline-relative improvement must replace the current normalization.

## 2.7 Decision-based model selection is not established as superior

The current analysis emphasizes that decision-based validation changes model choice.

Changing the selected model is not evidence of improvement.

The held-out results reported in the reviewed package are mixed, including gains, harms, and ties.

Therefore:

- the current recommendation is unsupported;
- decision-based selection must be treated as a falsifiable empirical question;
- the experiment must report held-out gains, harms, ties, confidence intervals, and practical significance.

## 2.8 Operational terminology exceeds the evidence

The project does not observe:

- daily staffing;
- actual crews;
- shifts;
- worker skills;
- service times;
- real productivity;
- real service capacity;
- actual municipal backlog;
- actual allocation decisions;
- dispatch;
- deployment;
- service completion.

The current decision layer is a transparent simulation over request-equivalent units.

Approved interpretation:

- abstract capacity units;
- hypothetical service-pressure regimes;
- simulated carryover;
- simulated unmet reported demand;
- family-level allocation within a stylized model.

Prohibited interpretation:

- actual staffing;
- real crew allocation;
- observed backlog reduction;
- deployment-ready operations;
- actual municipal capacity;
- causal service improvement.

## 2.9 Sensitivity claims exceed the implemented code

The decision log and manuscript imply that capacity, productivity, abandonment, and priority assumptions were broadly swept.

The code does not implement that full claim.

The corrected project must:

- specify the exact sensitivity grid;
- move all claim-critical values into configuration files;
- ensure code and decision-log claims match;
- avoid using the word “sweep” when only one or two checks were run.

## 2.10 City-family structure is not fully balanced

The project defines eight possible harmonized families, but active sets vary by city.

Examples:

- Chicago has no active noise family;
- Austin has a large heterogeneous residual `other` category.

Structural absence is not ordinary zero demand.

The corrected pipeline must use city-specific active family sets.

Austin’s `other` category requires a dedicated sensitivity analysis.

---

# 3. Shared View of What Remains Valid

Both proofs preserve the following elements.

## 3.1 Data and provenance

Retain:

- official source data;
- server-side daily aggregation;
- retrieval manifests;
- checksums;
- raw-data preservation;
- documented exclusions;
- reproducible acquisition scripts.

No new city is required.

No raw data should be altered.

## 3.2 Study design foundation

Retain:

- the four-city set;
- the 2020–2025 study window;
- city-by-active-family-by-day prediction units;
- next-day reported-demand forecasting;
- chronological train, validation, and test structure;
- rolling-origin evaluation;
- strong naive baselines;
- ridge, random forest, LightGBM, and quantile LightGBM;
- local and pooled forecasting infrastructure.

## 3.3 Harmonization

Retain the frozen deterministic harmonization rules, subject to:

- generation of an authoritative active-family manifest;
- structural-absence handling;
- audit of residual `other` categories;
- explicit cross-city comparability limits.

## 3.4 Forecasting evidence

The per-configuration local and pooled forecast measurements are potentially valid measurements.

What must change is:

- selection;
- aggregation;
- labeling;
- inference;
- and which results are elevated to headline claims.

## 3.5 Simulation engine

The core allocation engine and one-period greedy logic remain useful.

They must be corrected at the protocol and interpretation layers:

- pre-test capacity regimes;
- city-specific active-family sets;
- same-model uncertainty comparison;
- corrected metrics;
- explicit simulated terminology;
- decision-effect uncertainty analysis.

## 3.6 Reproducibility infrastructure

Retain:

- deterministic seeds;
- environment specifications;
- Makefile structure;
- generated artifacts;
- unit tests;
- configuration-driven experiments;
- number-to-code traceability.

Expand the test suite to enforce the redesigned protocol.

---

# 4. Shared Scientific Reframing

Both proofs agree that the current paper should no longer present itself as an empirical staffing study.

The strongest defensible identity is:

> **A benchmark-dominant empirical study of next-day reported municipal service-demand forecasting across four cities, with a controlled and explicitly simulated family-level capacity-allocation evaluation.**

The forecasting evidence is currently stronger than the operations evidence.

The decision analysis remains scientifically important, but only as a bounded simulated evaluation.

The paper may study:

- when forecast rankings and decision rankings align;
- when allocation policy matters more than forecast refinement;
- whether distributional information changes decisions;
- how decision effects vary across hypothetical service-pressure regimes;
- whether pooled learning helps or harms across heterogeneous systems;
- whether validation decision loss improves held-out model selection.

The paper may not claim:

- observed staffing effects;
- real municipal operating improvements;
- actual backlog control;
- actual service productivity;
- deployment;
- causal public value;
- fairness improvement;
- universal municipal generalization.

---

# 5. Shared Corrected Research Question

A defensible governing question is:

> Across heterogeneous municipal 311 reporting systems, under pre-specified hypothetical service-pressure regimes, when do differences in next-day forecasts of reported administrative demand produce materially different outcomes in a transparent simulated family-level capacity allocation, and when are predictive rankings sufficient proxies for simulated decision rankings?

This question:

- does not assume forecast improvement creates decision improvement;
- does not assume scarcity has a universal directional effect;
- distinguishes reported demand from social need;
- makes the simulation boundary explicit;
- remains answerable with the available data.

---

# 6. Shared Core Mechanism

The central mechanism accepted by both proofs is:

> Integer allocation thresholds and the forecast-to-policy mapping can amplify, compress, or redirect the downstream effect of predictive differences under fixed simulated service pressure.

Implications to test:

- two forecasts with different MAE may induce the same allocation;
- two forecasts with similar MAE may induce different allocations near thresholds;
- allocation policy may matter more than forecast refinement;
- distributional information may matter only in specific regimes;
- high overall rank agreement may coexist with top-choice instability.

This mechanism must be tested rather than assumed.

---

# 7. Shared Required Redesign Decisions

## 7.1 Capacity

Use frozen pre-test capacity budgets.

Primary recommendation:

- derive the main budgets from training data only;
- freeze them before validation decision selection;
- use the same budgets for validation and test.

A training-plus-validation calibration may be included as a pre-specified sensitivity analysis.

Capacity must be described as hypothetical service pressure, not actual city capacity.

## 7.2 Forecast selection

Use validation-only model selection.

For each city and feature set:

1. select using validation criteria;
2. freeze the selected configuration;
3. evaluate once on test;
4. report exhaustive test tables only as supplementary descriptive evidence.

## 7.3 Transfer

Use stage-specific temporal censoring:

- validation-stage source data end at the target training cutoff;
- test-stage source data end at the target validation cutoff.

## 7.4 Uncertainty

Use one fitted quantile model.

Compare:

- its median;
- optionally its implied mean;
- its full quantile representation.

The separately trained point model remains a forecasting benchmark, not the primary uncertainty comparator.

## 7.5 Metrics

Primary decision metrics:

- raw unweighted simulated unmet demand;
- raw scenario-weighted simulated unmet demand;
- absolute paired loss difference;
- percentage reduction relative to the uniform baseline;
- paired temporal block-bootstrap confidence intervals;
- family-level served fractions;
- final simulated carryover.

The myopic hindsight policy may remain as a labeled non-bounding reference.

## 7.6 Objective weights

Use equal weights as the primary neutral objective.

Use one normative priority-weight scenario as sensitivity analysis.

Do not imply that the weights are official or socially validated.

## 7.7 Service yield

Use one homogeneous request-equivalent base case.

Add one family-heterogeneous service-yield sensitivity scenario.

Do not claim that either represents observed productivity.

## 7.8 Carryover

Use the term:

- simulated unresolved request-equivalent carryover.

Do not use:

- observed backlog;
- actual municipal queue.

## 7.9 Active families

Generate one authoritative city-specific active-family manifest.

Requirements:

- Chicago noise is structurally absent;
- ordinary zero days remain valid for active families;
- Austin `other` is audited;
- Austin decision results are repeated with `other` excluded or isolated;
- if conclusions depend on `other`, those results must be narrowed.

## 7.10 Decision selection

Compare:

- validation-MAE selection;
- validation-decision-loss selection.

Freeze both choices before test.

Report:

- held-out gains;
- harms;
- ties;
- confidence intervals;
- practical significance;
- city-specific instability.

---

# 8. Shared Required Reruns

The following must be rerun.

## Forecasting

- headline validation-selected forecast comparisons;
- fixed-estimator feature effects;
- local-versus-pooled comparison where selection is involved;
- temporally valid zero-shot transfer;
- affected significance tests;
- affected figures and tables.

## Decision analysis

- every capacity regime;
- every decision policy;
- ranking agreement;
- policy-versus-forecast contrasts;
- same-model uncertainty comparison;
- decision-based model selection;
- sensitivity analysis;
- decision uncertainty intervals;
- all decision tables and figures.

## Artifact generation

Regenerate:

- tables;
- figures;
- metric files;
- manifests;
- captions;
- supplement outputs;
- repository summaries.

No old decision result may remain in the new scientific package.

---

# 9. Shared Required Automated Guards

The redesigned repository must contain tests that fail if:

1. test outcomes affect capacity calibration;
2. test metrics affect model selection;
3. future source-city observations enter transfer training;
4. point and distributional policies use different fitted models;
5. structural absence is encoded as ordinary zero;
6. active-family allocation violates the budget;
7. myopic hindsight is described as a bound;
8. an oracle-gap or gap-closed metric reappears;
9. decision-log claims disagree with implemented sensitivity settings;
10. source IDs or study dates conflict across files;
11. stale artifacts enter manuscript-facing outputs;
12. code and configuration disagree on active families.

No rerun is acceptable until all guards pass.

---

# 10. Shared Claim Boundaries

## Permitted claims, conditional on corrected results

The redesigned paper may claim:

- calendar augmentation is stable or heterogeneous across the four systems;
- realized target-day weather proxies have heterogeneous predictive value;
- pooling helps, harms, or has mixed effects;
- temporally valid transfer is weak, harmful, neutral, or heterogeneous;
- forecast and decision rankings are broadly aligned or locally divergent;
- policy effects exceed forecast effects in specified simulated regimes;
- distributional information has positive, null, or negative value under a controlled same-model comparison;
- decision-based validation improves, harms, or does not change held-out decision loss;
- decision effects vary across pre-specified hypothetical service-pressure regimes;
- key conclusions are robust or fragile to residual-category and service-yield assumptions.

## Prohibited claims regardless of corrected results

The redesigned paper may not claim:

- observed staffing improvements;
- actual crew-allocation performance;
- actual municipal backlog reduction;
- real capacity estimation;
- real productivity estimation;
- deployment readiness;
- causal service improvement;
- causal public-value improvement;
- city endorsement;
- institutional validation;
- measurement of social need;
- fairness improvement;
- full operational harmonization across cities;
- a horizon-optimal oracle;
- a new forecasting algorithm;
- a new optimization algorithm;
- a new decision-focused learning method;
- an absolute first-of-kind contribution.

---

# 11. Areas of Minor Difference Between the Two Proofs

The two proofs do not materially disagree on the diagnosis or redesign.

Their differences concern emphasis.

## 11.1 Paper identity

One proof classifies the redesigned paper as benchmark-dominant.

The other classifies the current valid evidence as mixed, with forecasting dominant.

Combined interpretation:

> The corrected paper should be benchmark-dominant, with forecasting as the strongest validated empirical evidence and simulated decision analysis as the main evaluative extension.

## 11.2 Capacity reference period

Both accept pre-test calibration.

One allows training plus validation.

The stricter combined primary recommendation is training-only, because validation decision selection must use the same frozen environment later used for test evaluation.

Training-plus-validation may be reported as sensitivity analysis.

## 11.3 Sensitivity breadth

One proof proposes a broad redesign register.

The other recommends a compact dependency-driven implementation.

Combined decision:

- run only sensitivities required for construct validity;
- do not expand automatically;
- add further analysis only if a core finding is unstable.

---

# 12. Binding Implementation Order

1. Freeze the redesign specification and governing configuration files.
2. Correct source metadata and active-family structure.
3. Implement protocol corrections atomically.
4. Add and pass all automated guards.
5. Rebuild the full pipeline from versioned raw inputs.
6. Regenerate corrected forecasting results.
7. Regenerate corrected decision results.
8. Compute dependence-aware statistical inference.
9. Regenerate all tables, figures, and manifests.
10. Isolate all stale prior artifacts.
11. Conduct specialist method review.
12. Conduct data and reproducibility audit.
13. Conduct responsible-AI and public-systems review.
14. Rewrite the venue-neutral manuscript.
15. Conduct final scientific closure.
16. Select and adapt to a venue only after the science is frozen.

---

# 13. Final Consolidated Decision

**REDESIGN — IMPLEMENT**

The two independent full-repository proofs converge on the same scientific conclusion.

The project is not invalid as a whole.

Its strongest components should be preserved.

Its defective experimental protocol must be replaced.

Its affected experiments must be rerun.

Its claims must be narrowed to what the corrected evidence supports.

The correct objective is not to defend the existing manuscript.

The correct objective is to produce the strongest truthful version of the research from the valid data, code, and scientific question already built.
