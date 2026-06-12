# Repository Reproducibility Closure Review — Agent 1b
**Reviewed object:** corrected repository package `dream_paper_complete_repository` (Drive upload of 2026-06-11 19:03 UTC; run id `20260609-20260610T213950`; freeze commit `9dd97c2`)
**Defect checklist:** Agent 1b original review (flaws 7.1–7.4, 7.6; consolidated defects C1–C10) — note these are MY defect IDs; the package's own register uses an unrelated C1–C11/U/G/E numbering, cited below as "redesign-Cn"
**Method:** byte-exact source downloads (base64) of all claim-critical code and configs; direct reads of the frozen-protocol config, guard suite, decision log, manuscript sources, and output proof manifests; cross-checks of three independent artifacts against the implementation report. No file was edited; nothing was rerun; nothing was written to Drive.
**Scope discipline:** review only. Out-of-scope observations are flagged and routed, not acted on.

---

## 1. Verdict

**MINOR REVISION.**

Every invalidating defect from the original review is closed with verifiable evidence — code, frozen artifacts, and guards that genuinely fail on violation. No scientific result in the corrected package is invalidated by anything found in this closure pass. What remains are four residual defects (two pre-existing, two newly found) confined to the manuscript text, the environment specification, and the decision-log record, plus two package-completeness gaps. They are individually small, but two of them put factually wrong statements into the compiled manuscript, so the package cannot be called closed until they are fixed.

---

## 2. Closure status of the original defect checklist

| ID | Original defect | Status | Evidence (verified directly) |
|---|---|---|---|
| C1 (7.1) | Capacity budgets from test-window demand | **CLOSED** | `compute_frozen_budgets()` calibrates from panel days ≤ train end only (train+val as labeled sensitivity); frozen to `frozen_budgets.json` **before** any selection; file verified: train-only budgets austin 8/11/13, chicago 29/38/46, nyc 119/153/187, sf 26/33/41, boundary dates all pre-test. Guard G1 is a true falsification test: +500 perturbation of test-window demand leaves budgets bit-identical. |
| C2 | Selection sims under different budgets than test sims | **CLOSED** | Selection experiment (`v_cfg`) uses the same frozen `units` per regime as the test simulation; verified in `run_decision.py`. |
| C3 (7.2) | Test-MAE model selection in headline figure | **CLOSED** | Selection frozen at source into `validation_selection.csv` (argmin of validation MAE); `tab1`, `tab1b`, and `fig2` consume only that artifact; exhaustive grid demoted to supplement (`tab2`). No `.min()` over test metrics exists in the reporting code. Guards G2 tie the artifact to argmin(val) and prove invariance to test-metric corruption. |
| C4 (7.3) | Zero-shot transfer trained on the future | **CLOSED — stricter than my proposed fix** | Source rows censored at held city's `v_end − 1 day`, correctly accounting for the t+1 target label (my own sandbox patch had a one-day label leak; theirs does not). Scope renamed `loco_zero_shot_censored` with per-row `source_censor_date`; G3 recomputes every cutoff and asserts no uncensored scope remains. |
| C5 (7.4) | Uncertainty contrast across different fitted models | **CLOSED** | Three arms (q50, implied-mean, full distribution) all derived from the one fitted `lgbm_quantile` prediction set inside `run_decision.py`; U8 two-stage fitting (train-only → val outputs; train+val refit → single test pass) removes the training asymmetry and gives the quantile model validation predictions; `lgbm_point` remains a separate labeled benchmark; quantile model excluded from the selection candidate set by config. Paired contrasts `full_vs_median_arm`, `full_vs_implied_mean_arm` with moving-block bootstrap CIs. |
| C6 (7.6) | Oracle-gap metric; false bound semantics | **CLOSED** | No gap normalization anywhere in decision or reporting code; policy renamed `hindsight_myopic_reference`; config declares `is_bound: false`, supplementary-diagnostic-only (U6); excluded from the main decision table; G7 forbids the gap tokens in every output table. |
| C7 | Decision-log sweep claim unmatched by code | **CLOSED** | Sensitivity grid is real (normative weights; one-family yield multipliers 0.70/1.30 over every active family; abandonment 0.10; train+val budgets; Austin-other-excluded recalibration) and G9 asserts the output scenario set equals the config grid exactly, per city. D9's "swept" claim is now true. |
| C8 | "8 harmonized service families per city" vs Chicago = 7 | **OPEN — residual defect R1 below** | Code-level half closed (authoritative `active_families.json`; G5 enforces structural absence ≠ zero rows; G12 enforces simulation families = manifest). The generated caption is not closed. |
| C9 | Selection consequences never reported | **CLOSED** | `decision_selection.csv` records both choices, both held-out test losses, paired CI, and a gain/harm/tie verdict per cell; reported post-C11 as 9 same / 2 gains / 1 CI-tie / 0 harms with the honest conclusion "not established as generally superior." |
| C10 | requirements.txt contradicts actual environment | **OPEN — residual defect R2 below** | `requirements.txt` byte-identical to pre-redesign. |

**Amendment C11 (pooled boundary overlap, R1-F1):** verified end-to-end. `pooled_stage_cutoffs()` takes the minimum train-end / validation-end across cities; `pooled_censoring.json` proves the fit-time boundary (max val-stage training day 2023-07-29 = min train-end; max test-stage day 2024-05-04 = min validation-end; 123/24 rows censored — exactly the report's numbers); G13 recomputes the boundaries independently and requires censored rows > 0.

**Guard-suite quality (the original Block A requirement that tests FAIL on violation):** G1, G2, G3, G9, G10, G11, G13 are genuine falsification tests (perturbation-invariance, recomputation, hash checks), not presence checks. G4 (same-model arms) and G7/G8 (terminology) are weaker presence/token checks — adequate, with the G8 scope gap noted in R5.

---

## 3. Residual defects (all confirmed by direct inspection)

**R1 — False caption in the compiled manuscript (my C8, surviving).** `make_paper_stats.py` is byte-identical to the pre-redesign file and still emits *"8 harmonized service families per city"* into `paper/sections/data_stats.tex` (verified in the regenerated fragment), which `data.tex` `\input`s into the rewritten manuscript. The claim is contradicted by the table directly beneath it (Chicago panel rows 15,344 = 2,192 × 7 vs 17,536 = 2,192 × 8 elsewhere) and by the manuscript's own correct prose one paragraph later ("Chicago has no noise family at all"). Because the generator script is unchanged, any future rerun **re-creates** the error even if the .tex is hand-fixed — fix the script, not the fragment. Severity: minor but submission-blocking (factual error in Table 1 caption). G8 cannot catch it (its token list targets prohibited framing, not this phrase). *Routing: manuscript-rewrite scope (text), engineering scope (script + optional guard).*

**R2 — Reproduction command builds the wrong environment (my C10, surviving, now sharper).** `requirements.txt` still pins `pandas>=2.1,<3`; the recorded run environment is `pandas==3.0.3` (`reproducibility/pip-freeze.txt`, verified as a real pinned freeze). The implementation report's own first reproduction step, `pip install -r requirements.txt`, therefore installs a different pandas major version than the one that produced every number in the package — and the code contains pandas-3-specific logic. Whether outputs reproduce bit-exactly under pandas 2.x is unverified and doubtful. For a *reproducibility closure*, this is the most consequential residual item. Severity: moderate; scientific results unaffected (the actual run environment is recorded and internally consistent), but the advertised one-command reproduction path is broken as documented. *Routing: engineering / reproducibility scope.*

**R3 — Wrong Austin dataset identifier in the manuscript (new).** `paper/sections/data.tex` cites Austin as `i26j-ai4z`; the authoritative `configs/data_sources.yml` (verified unchanged and matching the acquisition manifests via G10) uses `xwdj-i9he`. A reader following the paper queries the wrong dataset. G10 guards config↔manifests but nothing guards manuscript↔config. Severity: minor but submission-blocking (provenance error in print). *Routing: manuscript-rewrite scope; optionally engineering scope for a manuscript-id guard.*

**R4 — Duplicate, contradictory D19 entries in the decision log (new).** Two entries both numbered D19: the first dispositions R1-F1 as "documented as a limitation rather than corrected"; the second records it "RESOLVED by Amendment C11 … not a documented limitation." The second supersedes the first, but the first is not marked superseded and the ID is duplicated (the rewrite entry now labeled D20 should be D21). The code matches the second entry; the first is stale. An append-only log is correct practice — but supersession must be explicit and IDs unique, or the record yields contradictory citations. Severity: minor; documentation integrity only. *Routing: documentation scope.*

**R5 — Smaller wording/scope items.** (a) `data.tex` states the city-selection criterion "full 2019–2025 coverage," inconsistent with the 2020-start window and NYC's dataset scope stated in the same paragraph (the criterion predates D14; as written it asserts something false of NYC). (b) G8's manuscript scan covers `paper/sections/*.tex`, README, and `main.tex` but not the supplement sections. (c) `pd.Timestamp.utcnow()` FutureWarning, already self-reported (report §14). *Routing: (a) manuscript scope; (b)–(c) engineering scope.*

---

## 4. Missing items (per the prompt's missing-evidence protocol)

1. **Run logs.** `outputs/logs/` is empty in this Drive mirror, while the report cites `outputs/logs/rerun_*.log` per stage. Needed to corroborate the execution narrative independently of the outputs. Cannot fully verify: the stage-by-stage execution account (§3–4). **Non-blocking** — the outputs themselves are internally consistent and hash-manifested, and the pipeline is re-runnable.
2. **Test-execution artifact.** No pytest log exists in the mirror; the "33 passed / 0 failed / 0 skipped" claim is therefore re-runnable but not evidenced by an artifact. Cannot verify without it: that the guard suite was executed against exactly these artifacts. **Non-blocking** for the same reason; recommend the Data/Code auditor re-execute `python3 -m pytest tests -q` at acceptance.
3. **Line-level verification of `src/optimization/allocation.py`** (current version: `implied_mean()`, `moving_block_bootstrap_ci()`, the hindsight policy docstring, `SimConfig(units=, weights=)`). Verified only through import surface, guard coverage (G4/G6), and output consistency. The bootstrap implementation underwrites every CI in the paper, so it is the single highest-value remaining spot-check. Cannot fully verify without it: numerical correctness of the CI machinery. **Non-blocking** for this closure verdict; assigned to the Data/Code/Reproducibility auditor scope.
4. Row counts of the metrics CSVs (404/324/144/12/1,125/60) were corroborated by file sizes only, not parsed. **Non-blocking**, mechanically checkable.

Nothing missing is blocking; the closure verdict stands on the evidence inspected.

---

## 5. Out-of-scope flags (routed, not reviewed here)

- Quantile under-dispersion (coverage 0.77–0.81, disclosed, unrepaired) and the objective-conditionality of proportional dominance — scientific limitations already bound by F2/F3 framing constraints; *Methodologist / Statistician scope* if further treatment is desired.
- Venue selection and submission formatting — explicitly excluded by this prompt; *Publication Strategist scope*.
- Whether the rewritten manuscript's claims match §11–12 of the implementation report sentence-by-sentence — *manuscript review gate scope*; this closure verified only the defect-checklist-relevant fragments (`data.tex`, `data_stats.tex`, `main.tex`).

---

## 6. Required actions before the package is closed (owner decision; not executed by this review)

1. Fix the caption in `make_paper_stats.py` (e.g., "eight defined families; active sets vary by city — Chicago has seven"), regenerate `data_stats.tex`, recompile the PDFs. (R1)
2. Correct the Austin identifier in `data.tex` to `xwdj-i9he` and recompile. (R3)
3. Reconcile `requirements.txt` with `pip-freeze.txt` (align the pins, or document pip-freeze as the authoritative environment and adjust the report's reproduction command). (R2)
4. Renumber/mark the decision log: first D19 annotated SUPERSEDED-BY-AMENDMENT-C11 (or renumbered), rewrite entry renumbered accordingly. (R4)
5. Optional hardening: add the false-caption phrase and a manuscript↔config dataset-id check to the guard suite; extend G8 to supplement sections; fix the 2019-coverage wording. (R5)

None of these requires re-running any experiment; items 1–2 require regenerating one LaTeX fragment and recompiling.

---

## 7. Closure statement

The corrected package resolves all five invalidating defects and both protocol-consistency defects from the original review, with falsification-grade guards and frozen proof artifacts that this review verified independently. The remaining work is editorial and environmental, not scientific: two factually wrong strings in the manuscript, one stale dependency pin that breaks the documented reproduction path, and one decision-log numbering fault. **MINOR REVISION; re-closure after items 1–4 is expected to be a same-day check.**
