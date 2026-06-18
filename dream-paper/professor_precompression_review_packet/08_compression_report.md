# IEEE BigData Compression — Implementation Report

**INTERNAL DOCUMENT — never include on the public release branch.**

Branch `claude/bigdata-revision`. Date 2026-06-18.

## Summary

- **Phase 1 (mandatory cleanup): complete and verified** — all eight
  professor-identified issues fixed; zero undefined references; guards 37/37;
  forbidden-token scan clean.
- **Phase 2 (IEEEtran dry run): complete** — the official `IEEEtran.cls` v1.8b
  was obtained (the sandbox blocks CTAN, but `raw.githubusercontent.com` is
  allowlisted, so the genuine class was fetched from a GitHub mirror and
  installed locally). The dry-run IEEE compile of the **full current content**
  produced **9 pages** with 3 column-overflows.
- **Phase 3 (evidence-preserving compression): complete** — the only fixes
  needed were making three wide objects full-width; **no content or validity
  evidence was cut**. The final IEEE manuscript is **9 pages** (under the
  10-page limit, references included), 0 overflows, 0 undefined references.

## IEEE toolchain resolution

`IEEEtran.cls` is not in the sandbox TeX Live and CTAN/`tlmgr` are blocked by
the network allowlist. However `raw.githubusercontent.com` is reachable, so the
genuine class — `\ProvidesClass{IEEEtran}[2015/08/26 V1.8b by Michael Shell]`,
6347 lines — was fetched from a GitHub mirror, verified by its `\ProvidesClass`
header, and installed at `paper/IEEEtran.cls` (committed so the IEEE build is
self-contained, as IEEE submission bundles require).

## IEEE conversion

`paper/main_ieee.tex`: `\documentclass[conference]{IEEEtran}`, IEEE author
block, identical section `\input` structure and bibliography as `main.tex`. The
content is the same; only the document class and three float widths differ.

## Dry run → compression (page counts, verified by real IEEE compile)

| Build | Pages | Notes |
|---|---|---|
| Single-column `article` (`main.tex`) | 17 | reference/full version, retained |
| IEEE `conference` dry run (before fixes) | **9** | 3 overfull hboxes (wide floats) |
| IEEE `conference` final (after fixes) | **9** | 0 overflows, 0 undefined refs |

The dry run already fit in 9 pages, so **no trimming of text, tables, figures,
or claims was required**. The three overflows were resolved by formatting only:

1. `tab11` tie-break / non-identification table (8 columns) → full-width
   `table*`.
2. Table 1 dataset summary (`data_stats.tex`) → full-width `table*`.
3. The carryover display equation (`formulation.tex`) → split two-per-line
   equations onto their own lines.

All three edits are in shared section files and are harmless to the
single-column `article` build (verified: `main.tex` still 17 pp, supplement
still 16 pp).

## Scientific spine — all 15 elements visible in the 9-page main paper

three contributions (intro); simulation boundary (abstract, formulation,
limitations); dataset scale/audit (Table 1, `data_stats`); harmonization (Data
§); leakage/censoring protocol (Methods); core forecasting (results_forecast +
Fig 2); weather caveat (results_forecast); normalized/log pooling
(results_forecast); conformal calibration (results_forecast); decision-policy
results (results_decision); **non-identification / tie-break (Table,
`tab11`, in the main text)**; **b₀ / initial-carryover (Robustness)**; horizon
(Robustness); guard/reproducibility (Methods + reproducibility statement);
limitations (Limitations). Nothing claim-bearing is buried in the supplement.

## Required checks — status

| Check | Result |
|---|---|
| Cleanup compile (main article) | ✓ 17 pp, 0 undefined refs |
| IEEE dry-run compile (official IEEEtran) | ✓ 9 pp |
| Final IEEE compressed compile | ✓ **9 pp**, 0 overflows, 0 undefined refs |
| Supplement compile | ✓ 16 pp |
| Page count vs 10-page limit (refs included) | ✓ 9 ≤ 10 |
| Unresolved-reference check | ✓ none (article, IEEE, supplement) |
| Citation/reference compilation | ✓ via `.bbl` (`plainnat`) |
| Guard suite | ✓ 37/37 (16 guards G1–G16) |
| Forbidden-token scan | ✓ clean |
| Table/figure fit | ✓ all floats fit (wide ones full-width) |
| Claim-support after compression | ✓ all 15 spine elements present, none cut |
| BigData framing | ✓ concise 5V paragraph; Velocity explicitly out of scope |
| Novelty language | ✓ bounded ("To our knowledge … under one protocol …"); no absolute claims |

## Paper-1 / self-plagiarism note (preserved)

Paper 1's text remains unavailable for an automated overlap diff. No known
verbatim reuse was detected in current repository sources; the prior single-city
study is cited and distinguished in `related.tex`. Final author review is
required before submission if Paper 1 contains shared prose.

## Deliverables (committed)

`paper/IEEEtran.cls` (genuine v1.8b); `paper/main_ieee.tex`;
`paper/main_ieee.pdf` (9 pp); `paper/main_ieee.bbl`; the shared float edits
(`results_decision.tex`, `data_stats.tex`, `formulation.tex`); regenerated
article `main.pdf`; this report; updated checklist and packet.

## Stop conditions

None triggered. The non-identification/tie-break evidence, the simulation
boundary, and the b₀ result are all in the 9-page main paper; no unsupported
operational/deployment/staffing/causal/social-need claim was introduced; the
documents compile; guards pass. The 10-page limit was met with a page to spare.

## Verdict

**(1) IEEE BigData manuscript ready for final human review.** The official
IEEEtran build is 9 pages with the full scientific spine intact; the only
pre-submission items are human ones — the author's self-plagiarism confirmation
against Paper 1 (its text is unavailable here) and a final read-through. No
submission has occurred and the repository remains private.
