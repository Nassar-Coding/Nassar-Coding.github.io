# Paper Redesign Implementation Report

Generated after the corrected-protocol rerun (run id `20260609-20260610T213950`),
before any review gate or manuscript work. All numbers below regenerate from
the commands in §16.

## 1. Executive status

The corrected pipeline (E1–E12) completed end-to-end under the frozen
protocol, including the owner-directed Amendment C11 rerun (targeted
pooled-model stage censoring resolving review finding R1-F1 as a
DETECTED-AND-CORRECTED temporal-validity defect; guard G13 proves the
boundary at fit time: pooled val-stage max training day 2023-07-29 =
min train-end, test-stage 2024-05-04 = min validation-end; 123/24 rows
censored). The full test suite passes: **32 passed, 0 failed, 1 skipped** —
the single skip is the stage-gated manuscript-terminology guard (G8), armed
by `docs/.manuscript_rewritten` and intentionally inactive until the rewrite
phase; **zero artifact-related skips, zero stale-output violations** (G11
passed). Two pre-redesign headline claims did not survive the corrected
protocol and are replaced (§11–12). The package is ready for the three
review gates. The manuscript and supplement are untouched.

## 2. Frozen protocol and config hashes (sha256, first 16)

| File | Hash |
|---|---|
| configs/decision.yml | `f53408a95957b4b1` |
| configs/data_sources.yml | `83e1777981ed1041` |
| configs/service_families.yml | `1c35ea8d74b4d3cb` |

Protocol freeze commit: `9dd97c2` (2026-06-10 21:26 UTC).
Pre-redesign baseline (U10): `a7635919d6133105534cc54ef1620841b36b9c14`,
branch `claude/new-session-56q4pt`, 2026-06-10 06:13 UTC, pushed and
recoverable; local tag `pre-redesign`.

## 3. Commands executed (in order, after freeze)

```
python3 src/preprocessing/build_panel.py      # logs: outputs/logs/rerun_panel.log
python3 src/features/build_features.py        # logs: outputs/logs/rerun_features.log
python3 scripts/run_forecasting.py            # E1-E5; logs: rerun_forecasting.log
python3 scripts/run_decision.py               # E6-E10; logs: rerun_decision.log
python3 scripts/run_inference.py              # E11; logs: rerun_inference.log
python3 scripts/make_tables_figures.py        # E12; logs: rerun_artifacts.log
python3 scripts/make_paper_stats.py           # E12 (LaTeX stat fragments)
python3 -m pytest tests -v                    # guard suite
```

## 4. Stages completed (all verified by outputs and logs)

E1–E5 forecasting (404 metric rows; 300 fold rows; quantile val+test fits
per U8) · E6 frozen budgets (train-only; austin 8/11/13, chicago 29/38/46,
nyc 119/153/187, sf 26/33/41 units at κ=50) · E7 decision evaluation (324
rows) · E8 decision inference (144 rows = 4 contrasts × 3 blocks × 12
city-regimes) · E9 selection experiment (12 rows) · E10 sensitivities
(1,125 rows; U7 per-family yield grid, normative weights, abandonment,
train+val budgets, Austin-other-excluded) · E11 forecast inference (60
rows) · E12 tables/figures with provenance manifest. Nothing outside the
register ran.

## 5. Tests and guard results

Final state after Amendment C11 and the manuscript rewrite: **33 passed /
0 failed / 0 skipped** — G1–G13 all enforce on the regenerated artifacts,
and the manuscript-terminology guard (G8) is armed and passes against the
rewritten sections, README, and main.tex. Environment per
`reproducibility/pip-freeze.txt` (Python 3.11.15, pandas 3.0.3, LightGBM
4.6.0, scikit-learn 1.9.0).

## 6. Forecasting outputs (validation-selected headlines; effect sizes with
95% moving-block bootstrap CIs in tab9; all CIs stable across 14/28/56-day
blocks)

- Validation-selected test MAE (local): calendar improves on internal in
  every city (austin 16.53→14.84, chicago 60.37→50.94, nyc 207.02→182.38,
  sf 35.18→31.53); calendar+weather best in nyc/chicago/sf; weather adds
  nothing in Austin (the null is retained).
- Validation-only selection genuinely differs from the invalid test-min
  rule on the internal set (random_forest selected for austin/chicago,
  ridge for sf).
- Censored zero-shot transfer degrades MAE by +5.4% (sf), +39.1%
  (chicago), +64.8% (austin), +148.5% (nyc) versus local models.
- Pooled-vs-local (post-C11): pooling raises test MAE significantly in
  austin (+4.1%), chicago (+6.5%), and nyc (+1.8%) and is neutral in sf
  (-1.2%, n.s.); validation selection picks the LOCAL calendar+weather
  LightGBM in all four cities.
- Quantile model (U8 fitting): test 90% interval coverage 0.768–0.812
  (under-dispersed; reported, not repaired).

## 7. Decision outputs (equal weights primary; frozen train-only budgets)

- **Proportional allocation is the strongest policy in 11 of 12
  city-regime pairs**, beating the full-distribution greedy policy by
  0.1–6.5% (descriptive); the exception is sf/generous (+1.3% for the
  full arm).
- Within the greedy class, the full distribution significantly beats the
  median arm and the implied-mean arm in **12/12** pairs (CI < 0).
- Forecast quality matters within a fixed policy: validation-selected
  best beats trailing-mean naive under greedy in **12/12** pairs (CI < 0).
- Greedy-vs-proportional: proportional significantly better in **12/12**
  pairs (CI > 0) — reversing the pre-redesign claim (§12).
- Selection experiment (C7, falsifiable, post-C11): 9 of 12 settings
  select the same model under both rules; 2 gains (austin
  scarce/moderate), 1 CI-tie, 0 harms. Decision-based selection mostly
  agrees with MAE-based selection and never harmed; it is not
  established as generally superior. (Pre-C11, the contaminated pooled
  model had inflated validation scores, manufacturing 7/12 disagreements
  and 4 apparent harms — corrected by Amendment C11.)

## 8. Inference outputs

`decision_inference.csv` (144 rows) and `significance_tests.csv` (60 rows):
paired moving-block bootstrap, 28-day primary with 14/56-day sensitivity,
2,000 resamples, seed 20260609. **0 of 48 decision contrast conclusions
flip across block lengths.**

## 9. Tables and figures regenerated

22 files hashed in `outputs/tables/_provenance.json` under run id
`20260609-20260610T213950`: tab1/tab1b (validation-selected headlines),
tab2 (exhaustive grid, supplement-only), tab3/tab3b (decision; hindsight
reference excluded from the main view per U6), tab4 (rank agreement), tab5
(quantile), tab6 (selection), tab7 (sensitivity), tab8/tab9 (inference),
fig1–fig4. No gap-closure or oracle metric exists anywhere (G7 enforced).

## 10. Stale artifacts isolated

All pre-redesign metrics/tables/figures moved to
`artifacts/stale_pre_redesign/` (also recoverable at `a7635919`); none are
referenced by any regenerated artifact (G11 hash check passed). The
pre-redesign compiled PDFs in `paper/` and `supplement/` remain on disk as
the untouched pre-redesign manuscript and are superseded only at the
rewrite phase.

## 11. Supported claims (conditional on this corrected evidence)

1. Calendar augmentation reduces next-day error in all four systems
   (validation-selected, CI-backed).
2. Target-day weather value is heterogeneous: present in nyc/chicago/sf,
   null in austin.
3. Temporally censored zero-shot transfer is weak-to-strongly harmful and
   heterogeneous (+5% to +149% MAE); pooled training (stage-censored per
   C11) significantly raises error in three of four cities and is neutral
   in the fourth.
4. Under equal weights and pre-specified hypothetical service-pressure
   regimes, the simple proportional rule dominates the greedy
   expected-value policy family in 11/12 settings — allocation-policy
   choice matters more than forecast refinement within this simulation.
5. Distributional information has significant positive value *within* the
   greedy policy class (12/12), but does not overturn proportional
   dominance.
6. Forecast quality transfers to simulated decision value within a fixed
   policy (12/12).
7. Decision-loss-based validation selection mostly coincides with
   MAE-based selection (9/12), occasionally gains (2/12), and never
   harmed in this benchmark; it is not established as generally superior.
8. Conclusions are robust to block length (0/48 flips), Austin-`other`
   treatment (identical policy ordering in both treatments — Austin claims
   need NOT be narrowed), abandonment, train+val budgets, and one-family
   yield perturbations (worst case: nyc/generous, noise ×1.30; ordering
   direction unchanged).

## 12. Unsupported or prohibited claims

- REVERSED by the corrected protocol: "the expected-value greedy policy
  beats proportional allocation" (pre-redesign artifact of normative
  weights + test-calibrated budgets). The old direction may not be cited.
- NOT supported: decision-based model selection as a recommendation; any
  oracle/gap-closure framing; any uncertainty-policy superiority claim
  outside the greedy class.
- PROHIBITED regardless of results (findings §10): staffing/crew language,
  observed backlog, real capacity or productivity, deployment, causal
  public value, fairness improvement, city endorsement, measurement of
  social need, horizon-optimal oracle, novel-algorithm claims.

## 13. Remaining scientific risks

Quantile under-dispersion (coverage 0.77–0.81) is unrepaired; the
proportional-dominance result is conditional on equal weights and the
stylized carryover dynamics (the normative-weight sensitivity shows the
greedy family closing most of the gap, so the policy ranking is
objective-dependent — the manuscript must state this conditionality);
single-station weather (A2) and the day-ahead-forecast premise (A3) remain
documented assumptions; hyperparameters are fixed a priori, not tuned.

## 14. Remaining engineering risks

`pd.Timestamp.utcnow()` emits a FutureWarning under pandas 3.0.3 (works,
but should migrate to `now(tz="UTC")`); LOCO retrains inside the
forecasting script (acceptable runtime ~13 min total); the bootstrap is
pure-Python loops (adequate at this scale).

## 15. Files changed (baseline a763591 → this report)

Configs: decision.yml (new). Docs: 06_redesign_specification.md (new),
findings/ (new). Code: run_decision.py (rewritten), run_forecasting.py,
make_tables_figures.py, run_inference.py (new), allocation.py,
build_panel.py. Tests: test_guards.py (new), test_core.py. Artifacts:
outputs/* regenerated; artifacts/stale_pre_redesign/ (isolation). Paper and
supplement: UNCHANGED.

## 16. Reproduction commands

```
pip install -r requirements.txt
python3 -m pytest tests -q                    # 30 passed expected post-rerun
python3 src/preprocessing/build_panel.py
python3 src/features/build_features.py
python3 scripts/run_forecasting.py
python3 scripts/run_decision.py
python3 scripts/run_inference.py
python3 scripts/make_tables_figures.py
python3 scripts/make_paper_stats.py
python3 -m pytest tests -q                    # guard suite re-check
```
Deterministic: seed 20260609 everywhere; the decision layer is
Monte-Carlo-free; raw data pinned by SHA-256 manifests.

## 17. Review gates and manuscript status

All three review gates were conducted and PASSED
(`docs/07_review_gates.md`): the Methodologist review surfaced one new
finding (R1-F1, pooled boundary overlap), resolved by owner-directed
Amendment C11 as a detected-and-corrected defect with guard G13; the
Data/Code/Reproducibility audit verified bit-exact determinism and full
provenance; the Responsible-AI review imposed binding manuscript framing
constraints (F6/F7), now satisfied. The manuscript and supplement were
rewritten AFTER the gates under the U9 working title ("Next-Day
Municipal Service-Demand Forecasting Across Four Cities: A Benchmark
with a Controlled Simulated Capacity-Allocation Evaluation"), built
solely from the corrected artifacts, with F2/F3/F6/F7 statements
included; compiled main (14 pp), anonymized variant, and supplement
(10 pp) are in `paper/` and `supplement/`.
