# Prof 1 and Prof 2 Revision Response Report

## 1. Executive status

All required corrections from both closure reviews are completed in one
repair pass. No core forecasting, decision, sensitivity, or inference
experiment was rerun; the only computation added is the W2 trend
diagnostic over the existing frozen configuration (with an asserted
1e-6 identity check against the E7 artifact) and the two toy mechanism
examples. Final suite: **37 passed / 0 failed / 0 skipped**
(`reproducibility/pytest_final.log`), including new guards G14–G16 and
the supplement-extended G8. Manuscript (15 pp), anonymized build, and
supplement (13 pp) recompiled from corrected sources and regenerated
fragments. Working tree clean at the final commit.

## 2. Reviewed inputs

1. Prof 1: `scientific_director_empirical_om_review.md` (MAJOR REVISION) —
   archived at `docs/findings/`.
2. Prof 2: `repository_reproducibility_closure_review.md` (MINOR REVISION) —
   archived at `docs/findings/`.
Repository version corrected: the post-C11 closure state (run id
`20260609-20260610T213950`, freeze commit `9dd97c2`); reviews' Drive
mirror of 2026-06-11 19:03 UTC.

## 3. Prof 1 correction table

| Prof 1 issue | Action taken | Files changed | Evidence | Experiment rerun required? | Status |
|---|---|---|---|---|---|
| W1 selection contradiction | Verified artifacts vs recomputed argmin (consistent — prose error, not artifact/code inconsistency). Cross-scope grid: val-MAE selects GLOBAL in Austin (15.08 vs 15.25) and SF (27.20 vs 28.97), LOCAL in Chicago/NYC. §6 sentence replaced with the two-procedure account; candidate sets named in §5; §7 selection paragraph states SF picks pooled under both criteria; implementation report §6 corrected; guard G16 re-derives the artifact | results_forecast.tex, methods.tex, results_decision.tex, paper_redesign_implementation_report.md, tests/test_guards.py | §5 of this report; G16 passing | No | DONE |
| W2 loss semantics + trend diagnostic | Loss defined in §3 as waiting-time-weighted cumulative unresolved stock; new `scripts/run_diagnostics.py` (NW lag-28 slope, trend-dominance ratio, verdict per city×regime×contrast + level series); result: 45/48 differentials and 11/12 level series trend-dominated (only Chicago/generous stationary-compatible); §7 preamble and §8 re-scope all decision intervals as descriptive except Chicago/generous; "mean daily reduction" → "average daily reduction in unresolved stock"; regime percentages flagged partly mechanical; horizon-dependence limitation added; tab10 in supplement | formulation.tex, results_decision.tex, robustness.tex, limitations.tex, scripts/run_diagnostics.py, outputs/metrics/trend_diagnostics.csv, outputs/tables/tab10_*, s_sensitivity.tex | §6 of this report | No (diagnostic re-derives series deterministically; identity asserted to 1e-6) | DONE |
| W3 policy headline + mechanism | Abstract, §7 first finding, and conclusion re-anchored: point-EV failure mode (12/12) separated from the fair-comparator statement (proportional 11/12 by 0.1–6.5%, one reversal, conditional); mechanism generalized to piecewise-flat (κω below / 0 above point estimate, both segments); deficit-side worked examples added and computed with the repository's own `greedy_allocate` ([3,1,0] vs [2,1,1]; [4,0,0] vs [2,1,1]); 11/12 edge labeled pattern-without-demonstrated-mechanism with the horizon-myopia conjecture; "policy choice matters more than forecast refinement" removed | abstract.tex, results_decision.tex, conclusion.tex, s_optimality.tex | §7 of this report | No (toy examples only) | DONE |
| W4 printed factual errors | All five fixed (caption at generator level; Austin id in manuscript AND supplement; 2019-coverage criterion; supplement Chicago window; supplement title); CITATION.cff and docs/03 also corrected | scripts/make_paper_stats.py, data.tex, s_data.tex, supplement.tex, CITATION.cff, docs/03 | §8 of this report; G14/G15 passing | No | DONE |
| Documentation supersession | First D19 marked SUPERSEDED, entries renumbered D20/D21, IDs unique, D22 appended; docs/01 supersession notice (terminology C8; equal-weights primary frozen at 9dd97c2 BEFORE the rerun; C1); docs/03 D14 note; docs/05 marked venue-not-started | docs/04, docs/01, docs/03, docs/05 | §9 of this report | No | DONE |
| Environment/reproducibility | pip-freeze declared authoritative; requirements.txt rewritten to matching major bounds and labeled development-only; reproduction command corrected in report §16, supplement s_repro untouched (already pointed at the suite) plus README | requirements.txt, README.md, implementation report | §10 of this report | No | DONE |
| Calibration caveat | One-sentence caveat in the §7 uncertainty finding (value of the available under-dispersed distribution; plausibly a lower bound); supplement notes the pooled model's better coverage (0.745–0.872, closer to nominal in 3/4 cities — verified against tab5) | results_decision.tex, s_tables.tex | artifact check in repair log | No | DONE |
| Guard hardening | G14 manuscript↔config dataset-id (all printed Socrata ids ⊆ config; stale id banned); G15 caption truthfulness (fragment + generator); G16 selection-artifact recomputation; G8 extended to supplement sections (+ one supplement token fixed: "oracle" → "hindsight myopic reference" in s_optimality) | tests/test_guards.py, s_optimality.tex | suite 37/0/0 | No | DONE |
| Missing run/test logs | 10 rerun logs verified tracked in git (`outputs/logs/`); pytest artifact created (`reproducibility/pytest_final.log`); honest command log written distinguishing verified-by-artifact from anything else (`reproducibility/command_log.md`); nothing fabricated | reproducibility/ | files committed | No | DONE |
| Minor: Spearman promotion | One sentence with ρ = 0.88–0.99 promoted into §7 (accuracy as sufficient proxy) | results_decision.tex | tab4 artifact | No | DONE |
| Minor: 311 precursor citation | Xu, Kwan, McLafferty & Wang (2017), *Applied Geography* 89:133–141, verified against the publisher before adding; one positioning clause in Related Work | references.bib, related.tex | verified search record | No | DONE |
| Minor: utcnow migration | `pd.Timestamp.now(tz='UTC')` in both run scripts (timestamp strings only; no behavioral change) | run_forecasting.py, run_decision.py | suite green | No | DONE |

## 4. Prof 2 correction table

| Prof 2 issue | Action taken | Files changed | Evidence | Experiment rerun required? | Status |
|---|---|---|---|---|---|
| R1 Table 1 caption | Fixed at generator level; fragment regenerated; G15 prevents recurrence at both fragment and generator | make_paper_stats.py, data_stats.tex (regenerated) | caption now: "eight defined service-family categories with city-specific active sets — Chicago has seven…" | No | DONE |
| R2 environment mismatch | Option 1 (preferred): pip-freeze authoritative; requirements.txt rewritten to consistent major bounds (pandas>=3.0,<4) and explicitly labeled; reproduction commands corrected everywhere | requirements.txt, README, report | §10 | No | DONE |
| R3 Austin dataset ID | `xwdj-i9he` in manuscript §4, supplement §1, docs/03; G14 added | data.tex, s_data.tex, docs/03 | grep clean; G14 passing | No | DONE |
| R4 duplicate D19 | First D19 marked SUPERSEDED-BY-D20/C11; authoritative entry renumbered D20; rewrite entry → D21; all IDs unique (verified programmatically) | docs/04 | ID-uniqueness check in repair log | No | DONE |
| R5 smaller items | (a) 2019-coverage wording fixed D14-consistently; (b) G8 extended to supplement; (c) utcnow migrated | data.tex, test_guards.py, run scripts | suite green | No | DONE |
| Missing logs + pytest artifact | Logs verified tracked (they existed in git; the Drive mirror omitted them); pytest_final.log added; command_log.md added | reproducibility/ | committed files | No | DONE |
| Optional guard hardening | Adopted in full (G14, G15, G8 extension) | test_guards.py | suite 37/0/0 | No | DONE |

## 5. Selection contradiction resolution

Verified directly: `decision_selection.csv`'s `selected_by_val_mae`
equals the recomputed argmin of validation MAE over the pre-specified
eleven-configuration grid for every city (now guard G16). The artifacts
were always consistent with the code; the manuscript sentence was the
error. Two procedures exist: (i) **within-scope** selection (per city ×
feature set × scope; five point models of that scope) feeds every
headline table/figure — among local candidates the local LightGBM wins
in all four cities; (ii) the **cross-scope** selection experiment
(eleven configurations, pooling local + the stage-censored global model)
— validation MAE there prefers the pooled model in Austin (15.08 vs
15.25; worse on test, the source of the two decision-criterion gains)
and in SF (27.20 vs 28.97; also the better test model). §5 names both
candidate sets; §6 states both facts; §7's selection paragraph now adds
the SF case explicitly; the implementation report carries the corrected
account.

## 6. Scarce-regime diagnostic

`scripts/run_diagnostics.py` re-derives the daily loss series
deterministically from the frozen inputs (identity with E7 totals
asserted to 1e-6 per policy/cell), then computes the OLS slope of each
daily paired differential with a Newey–West (lag-28) t-statistic and a
trend-dominance ratio. Result (`outputs/metrics/trend_diagnostics.csv`,
supplement tab10): **45 of 48** contrast differentials and **11 of 12**
loss level series are trend-dominated; the only stationarity-compatible
cell is Chicago/generous. Manuscript consequence: §3 defines the loss
as a waiting-time-weighted unresolved stock; §7's preamble re-scopes
every decision-contrast interval as a descriptive characterization of a
systematic, partly deterministic divergence (stationary reading retained
only for Chicago/generous); §7 stock wording replaces flow wording;
§8 reports the diagnostic and notes that block-length stability cannot
detect a common trend; limitations add queue instability and horizon
dependence; the regime-percentage pattern is flagged as partly
mechanical. Forecast-accuracy inference (§6) is unaffected and stated
as such. The diagnostic was broader than the review anticipated (it
implicates moderate/generous too, not only scarce); the conservative
descriptive framing was applied accordingly rather than minimized.

## 7. Policy-mechanism revision

Corrected mechanism (in §7 and supplement s_optimality): a degenerate
forecast distribution makes the optimizer's marginal-value profile
piecewise flat — κω for every unit below point-estimate-plus-carryover,
zero above — so under a neutral objective the greedy ordering carries no
information in either segment and allocation is tie-broken. Both
segments now carry worked examples computed with the repository's own
`greedy_allocate`: surplus (budget 12 → [6,3,3]) and deficit (budget 4,
demands 30/30/30 → greedy [3,1,0] vs proportional [2,1,1]; demands
50/30/10 → greedy [4,0,0] vs [2,1,1]). The 11/12 edge over the
full-distribution arm is labeled an observed pattern without a
demonstrated mechanism, with the horizon-myopia explanation explicitly
marked a conjecture. Changed in: abstract, §7, conclusion,
s_optimality, implementation report §11.

## 8. Factual-string correction audit

1. Table 1 caption "8 harmonized service families per city" → corrected at
   generator (`make_paper_stats.py`) and regenerated.
2. Austin `i26j-ai4z` → `xwdj-i9he` in `paper/sections/data.tex`,
   `supplement/sections/s_data.tex`, and `docs/03` (annotated).
3. "full 2019–2025 coverage" → "coverage of the 2020–2025 study window —
   set by the scope of NYC's current dataset, decision D14".
4. Supplement Chicago "study window starts 2019-01-01" → "uniform study
   window starts 2020-01-01 per decision D14".
5. Supplement title "Supplement: From Accuracy to Allocation" → U9-consistent
   title.
6. `CITATION.cff` stale title → U9 title.
7. Supplement s_optimality "crews" → "capacity units"; "oracle" →
   "hindsight myopic reference".

## 9. Documentation and decision-log reconciliation

Decision log: first D19 annotated **[SUPERSEDED by D20 / Amendment C11]**;
authoritative C11 entry renumbered **D20**; manuscript-rewrite entry
renumbered **D21**; repair pass recorded as **D22**; IDs verified unique.
`docs/01_problem_definition.md`: prepended supersession notice covering
terminology (C8), the equal-weights primary objective (frozen at
`9dd97c2`, dated before the corrected rerun — answering the
pre-registration concern directly), and train-only capacity calibration
(C1); body retained unedited for the record. `docs/03`: D14 note + Austin
id annotation. `docs/05`: marked VENUE SELECTION NOT STARTED.

## 10. Environment and reproduction correction

Authoritative environment: `reproducibility/pip-freeze.txt`
(Python 3.11.15, pandas 3.0.3, LightGBM 4.6.0, scikit-learn 1.9.0,
numpy 2.4.6). Reproduction command:
`pip install -r reproducibility/pip-freeze.txt` then `make all`,
`python3 scripts/run_diagnostics.py`, `python3 -m pytest tests -q`.
`requirements.txt` is now explicitly a development-bounds file whose
majors match the frozen environment (pandas>=3.0,<4), so the previous
silent wrong-major install cannot recur. Bit-exact reproduction is
expected under the frozen environment (seeded pipeline, Monte-Carlo-free
decision layer); artifact-level reproduction only is claimed otherwise.

## 11. Guard hardening

- **G14** (new): every Socrata dataset id printed in manuscript or
  supplement must be in `configs/data_sources.yml`; the stale Austin id
  is explicitly banned; every configured id must appear in print.
- **G15** (new): Table 1 caption truthfulness at both the generated
  fragment and the generator source ("families per city" banned;
  "Chicago has seven" required).
- **G16** (new): `decision_selection.csv`'s by-MAE choice re-derived as
  argmin of validation MAE over the eleven-configuration grid.
- **G8** (extended): terminology scan now covers
  `supplement/sections/*.tex` and `supplement.tex`.

## 12. Manuscript and supplement rebuild

`cd paper && make && make anonymous` → `paper/main.pdf` (15 pages),
`paper/main_anon.pdf`; supplement via pdflatex/bibtex ×2 →
`supplement/supplement.pdf` (13 pages, including tab10). Regenerated
fragments: `paper/sections/data_stats.tex`,
`supplement/sections/s_harmonization_tables.tex`, all
`outputs/tables/*` (32 artifacts re-hashed in `_provenance.json`).

## 13. Test results

`python3 -m pytest tests -v | tee reproducibility/pytest_final.log` →
**37 passed, 0 failed, 0 skipped** (12 core tests + guards G1–G16
including the armed manuscript/supplement terminology guard).

## 14. Files changed

Manuscript: abstract, introduction-adjacent none, data, data_stats
(regenerated), methods, formulation, results_forecast, results_decision,
robustness, limitations, conclusion, related, references.bib.
Supplement: supplement.tex, s_data, s_optimality, s_sensitivity,
s_tables. Scripts: make_paper_stats.py, make_tables_figures.py,
run_forecasting.py, run_decision.py, run_diagnostics.py (new).
Tests: test_guards.py. Docs: 01, 03, 04, 05. Reports:
paper_redesign_implementation_report.md, this file. Environment:
requirements.txt, README.md, CITATION.cff. Evidence: reproducibility/
pytest_final.log, command_log.md; outputs/metrics/trend_diagnostics.csv;
outputs/tables/tab10_*; regenerated tables/figures + provenance.

## 14b. Post-re-review note (final cleanup pass)

Re-review item verified: the identical scarce/moderate diagnostic rows
for San Francisco's three within-greedy-family contrasts in tab10 are
structurally genuine, not row duplication — at SF's scarce (26-unit) and
moderate (33-unit) budgets both greedy arms are fully saturated, every
arm serves exactly $\kappa B$ per day, and the paired differential
depends only on the allocation-difference vector, which is invariant
across those budgets; the proportional contrast and the level series
differ between the regimes (total losses 29.6M vs 16.4M), confirming
distinct simulations. The pattern occurs in no other city.

## 15. Remaining issues

- Blocking: none.
- Non-blocking: line-level external spot-check of
  `moving_block_bootstrap_ci` (Prof 2 missing-item 3) remains assigned to
  the re-closure auditor; the implementation is committed and short.
- Future work (unchanged, correctly deferred): conformal recalibration;
  trend-robust summary statistics (terminal stock / served-count
  differentials) as an alternative inference target; closure-timestamp
  data for a real operational quantity.

## 16. Re-review readiness

Ready. Every binding item in Prof 1's correction list (1–13) and every
required action in Prof 2's list (1–5 plus both optional hardenings) is
implemented, evidenced, and guarded; the suite passes with zero skips;
the tree is clean; no core result changed.

## 17. Final decision request

The package is ready for Prof 1 and Prof 2 re-closure review. No venue
selection has been performed.
