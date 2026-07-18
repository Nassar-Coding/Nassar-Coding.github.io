# Corrections record

## R1-F1: pooled-model temporal-boundary contamination (corrected)

**Defect.** Per-city chronological split boundaries differ by 1–2 calendar
days across the four cities. The original pooled ("global") model fits used
each city's own boundary row-wise, so a pooled fit could contain a small
number of other-city rows (~0.1% of pooled training rows) that were
contemporaneous with the earliest evaluation days of another city. This was
a scientific defect, not a formatting issue: it inflated the contaminated
pooled model's validation scores and thereby changed model-selection
results.

**Discovery.** 2026-06-11, during the documented pre-submission review-gate
process (gate 1, methodologist review; finding logged as R1-F1 in
`docs/07_review_gates.md`). Discovery state is preserved in commit
`4ba0068` ("Review gates 1-3 conducted and documented").

**Correction.** Commit `e5592bb` ("Amendment C11 executed: pooled-model
stage censoring (R1-F1 detected-and-corrected); G13 added; full rerun;
gates closed", 2026-06-11T18:49:36Z). Pooled fits are now stage-censored:
validation-stage fits use only rows dated no later than the earliest
training cutoff across cities; test-stage fits no later than the earliest
validation cutoff. Guard G13 (`tests/test_guards.py`) enforces the rule
with a fit-time proof manifest (`outputs/metrics/pooled_censoring.json`)
and fails the build if any pooled training row crosses the stage boundary.

**Impact on published analyses.**
- Affected: pooled/global model results, censored transfer rows, and the
  cross-scope selection experiment. After the correction the
  selection-experiment outcome changed from 7/12 disagreements with 4
  apparent harms to 9/12 agreements, 2 gains, 0 harms; the earlier
  disagreement was substantially an artifact of the contaminated pooled
  model's inflated validation scores.
- Unaffected: local (per-city) model fits, the frozen capacity budgets,
  the evaluation windows, and the allocation-simulation mechanics.

**Regeneration.** All forecasts, simulations, tables, figures, and
manuscript values were regenerated after the correction; the
provenance-hash guard (G11) verifies that every released manuscript
artifact derives from the corrected run. Pre-correction outputs are
retained under `audit/pre_fix_outputs/` for audit and are not used by the
paper.

**Corrected release.** The public release tag and archival DOI (recorded in
`README.md` and `CITATION.cff` when minted) point only to the corrected
version.
