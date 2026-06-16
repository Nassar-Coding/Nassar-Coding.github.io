# IEEE BigData 2026 Feasibility Gate

**INTERNAL DOCUMENT — never include on the public release branch.**

Date: 2026-06-16. Branch: `claude/bigdata-revision`. Decision deadline frame:
full paper 2026-08-21.

This gate follows the Phase-1 triage register. It answers the eight Phase-3
questions and issues a GO / NO-GO / SWITCH recommendation.

---

## 1. Which professor issues are true BigData blockers?

Blockers (rejection-capable on their own), all Class 2:

- **Contribution clarity** (#1, #8): exactly three contributions, findings
  separated.
- **Decision-layer validity** (#9–#14, #168, #173): the "point forecasts
  disable the optimizer" claim must be shown to be a *non-identification*
  result robust to (or honestly conditioned on) the tie-break rule. This is
  the single highest rejection risk.
- **Uncertainty calibration** (#82, #83, #88, #92): the distribution-aware
  decision result must survive — or be explicitly bounded against — conformal
  recalibration, and the "distribution" must be named a *quantile-interpolated*
  one with stated interpolation/tails.
- **Normalized pooling** (#75, #76): "pooling hurts" must not be a raw-count
  scale artifact.
- **Weather information set** (#55): target-day weather named a proxy/upper
  bound (already largely done).
- **Leakage protocol visibility** (#116, #120, #165): exact split dates, a
  censoring diagram/table, and bounded novelty claims.
- **Reproducibility** (#148): a clean `make all` must regenerate the headline
  numbers.
- **Evidence-in-main tables** (#22/#140 per-family unserved, #188 tie-break,
  #189 calibrated decision, #190 horizon, #179/#180 audit/split): claims the
  text makes must be visibly tabulated.

Everything else is Class 1 (already satisfied), 3 (polish), 4 (supplement), 5
(journal), 6 (reject), or 7 (author).

## 2. Which can be fixed within the deadline?

All blockers. The experimental cost is low: the full pipeline (`make all`)
runs end-to-end in this environment in minutes, the decision layer is
Monte-Carlo-free and fast, and most "needed tables" already have artifacts or
derive from existing metric CSVs. The dominant cost is **writing and 10-page
compression**, not computation.

## 3. Which require new experiments?

- Tie-break sensitivity (decision rerun only).
- Log/normalized global pooling + normalized transfer (forecasting rerun).
- Split-conformal calibration + calibrated decision (forecasting + decision).
- Horizon-length cuts (decision rerun; cheap re-slice).
- Poisson GLM baseline (forecasting rerun).
- κ / abandonment / initial-backlog grids (decision rerun).
- Family coverage / interval width / crossing freq / tail sensitivity
  (computed from quantile outputs).

## 4. Which require a full rerun?

Only changes that touch forecasting (pooling, Poisson, conformal) need a
forecasting rerun, which automatically cascades to decision + tables. Decision-
only items (tie-break, horizon, κ, abandonment, backlog, per-family) need only
`make decision tables`. There is no multi-hour or GPU dependency.

## 5. Which should move to journal extension?

NB/GAM/deep forecasting models (#67, #68, #74), alternative objective forms
(#19), extensive priority-weight scenarios (#20), DP oracle (#18), rolling
multi-window evaluation (#51), full related-work overhaul (#161–#164),
spatial/fairness expansion (#142 beyond a scope statement), all-city core-seven
harmonization (#113 beyond Austin). None is needed for a defensible BigData
paper.

## 6. Which would exceed BigData scope?

Deep/foundation forecasting models, an operations-management treatment of the
allocator (real queues/shifts/skills), and spatial equity modeling. All are
**rejected** for this venue; adding them would invite the very
operational-realism attack the paper is designed to avoid.

## 7. Does a 10-page BigData paper remain possible without hiding essential evidence?

**Yes, but tightly.** The main paper must carry, in compact form: three
contributions; a dataset+harmonization audit (one table each); a
protocol/leakage table with exact dates; a forecasting MAE table (incl.
calendar/weather marginal and pooled/transfer); a quantile calibration table
(coverage + width + conformal); the decision policy grid; the tie-break
sensitivity (compact); horizon sensitivity (compact); and the simulation
boundary + limitations (uncompressed). The supplement (already substantial:
`s_optimality`, `s_harmonization*`, `s_sensitivity`, `s_models`, `s_repro`,
`s_negative`, `s_compute`, `s_data`, `s_ethics`, `s_tables`) absorbs exhaustive
grids, worked examples, the guard table, per-family detail, missingness, and
all secondary sensitivities. Because the heaviest evidence already exists in
compact table form, compression does not force omission of validity evidence —
it forces moving *exhaustive* evidence to the supplement, which is acceptable.

The binding risk is the opposite of omission: cramming. The mitigation is to
keep one decisive table per claim in the main text and push the grids down.

## 8. GO / NO-GO

### Recommendation: **GO**, conditional on three claim-gating experiments.

The paper is, on inspection, substantially more complete than the 202-item
register implies — roughly a third of the items are already satisfied, and the
genuine gaps are a tractable, in-environment experimental program plus a
disciplined rewrite. The contribution, decision-layer validity (after the
tie-break experiment and non-identification reframing), calibration (after
conformal), normalized pooling, harmonization audit, leakage protocol, and
reproducibility can all be credibly represented in main + supplement. That
satisfies the GO rule.

**GO is conditional on the three claim-gating experiments not silently
breaking the narrative:**

- **C1 — Tie-break (STOP #1).** Expected outcome: a smarter tie-breaker
  (proportional secondary) largely closes the point-greedy gap, *confirming*
  that the result is objective **non-identification**, not optimizer failure —
  which is the reframing the professor asks for (#14) and which the supplement
  already supports. This is a strengthening, not a reversal. **Only if** a
  fixed/forecast-based tie-breaker makes point-greedy beat the
  quantile-interpolated distribution would the headline be eliminated → then
  STOP and ask.
- **C2 — Conformal (STOP #2).** Expected outcome: widening under-dispersed
  intervals *increases* distributional gradient, so the full-arm advantage
  holds or strengthens. **Only if** calibration makes the median/implied-mean
  arms match or beat the full arm would the uncertainty finding reverse → STOP
  and ask.
- **C3 — Log-pooling (STOP #3).** Highest genuine reversal probability. If
  log1p/standardized global pooling **beats** local models, the "pooling
  hurts" conclusion flips. That is a legitimate, publishable finding, but it
  changes a headline → STOP and ask before rewriting that claim.

If any condition triggers, the fallback is not abandonment but a pause for the
author's decision, with INFORMS JDS / IJF as the venue alternative if the
evidence package grows past what 10 pages can hold (the SWITCH rule).

### Why not NO-GO

NO-GO is warranted only if page compression forces hiding decision-layer
validity, harmonization, the simulation boundary, or leakage controls. It does
not: each has a compact main-text form, and the supplement exists to hold the
rest.

### Why not SWITCH (yet)

SWITCH to a journal is the right call only if the repaired evidence package
genuinely cannot fit 10+supplement pages, or if a claim-gating experiment
forces a much larger reframe. Neither is established pre-experiment. Re-evaluate
SWITCH after C1–C3.

---

## Execution order (Phase 4, if GO)

1. Verify `make all` reproduction (in progress) — gates everything (#148).
2. **C1 tie-break**, **C3 log-pooling**, **C2 conformal** — run first; resolve
   stop conditions before touching prose.
3. Priority-1 decision/forecasting tables + horizon + per-family.
4. Priority-1 manuscript reframing (non-identification, quantile-interpolated,
   "did not increase test loss", proxy weather, bounded novelty, 3
   contributions, 5V framing).
5. Priority-2 (Poisson, κ/abandonment/backlog grids, calibration detail,
   guard/hyperparameter tables).
6. Re-run guard suite; refresh provenance; re-verify reproduction; update
   reports.
