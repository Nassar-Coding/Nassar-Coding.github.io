# Draft 3 — Stage 1 Decision Log

**INTERNAL DOCUMENT — never include on the public release branch.**
Branch `draft_3`, from commit `360198d`.

| Decision area | Options considered | Recommendation | Evidence | Stage 2 action |
|---|---|---|---|---|
| A1 calendar-effect range | (a) keep 8.6–14.0%; (b) fixed-estimator 10.0–14.0%; (c) selected 10.2–15.6% | **(b) 10.0–14.0%** in abstract (matches the "intervals excluding zero"/`tab9` significance basis); keep `results_forecast`'s 10.2–15.6% for the selected-model headline | `forecast_metrics.csv` (lgbm cal-vs-internal = 11.9/14.0/10.0/11.2); `validation_selection.csv` (11.9/15.6/10.4/10.2); 8.6% absent except SF RF cal+wx (8.56%) | edit `abstract.tex` number only |
| A2 study vs modeled span | (a) leave "2020–2025"; (b) clarify modeled span ends Feb 2025 | **(b) clarify** | `features.parquet` ends 2025-02-05; `panel_manifest` densified to 2025-12-31; `data.tex`/Table 1 say through 2025-12-31 | add one sentence + Table-1 caption note |
| A3 Chicago exclusion count | (a) keep 4,184,158; (b) correct to 4,184,157 | **(b) correct** | raw recompute: info-only 4,184,157, aircraft 1,918,574, dup 523,055, total removed 6,625,786 = raw − kept | edit `data.tex` info-only count |
| B1 decision inference wording | (a) leave; (b) tighten residual "excluding zero" | **(a) leave (optional tighten)** — descriptive frame already established | `results_decision` preamble + trend diagnostic | optional only |
| B2 "neutral objective" | (a) keep; (b) reword to equal-weight/non-normative | **(b) reword** | 7 claim-bearing instances; equal weights are not normatively neutral | reword ~7 instances |
| B3 operational overclaim | (a) none; (b) fix | **(a) none** — all disclaimers, guard-enforced | forbidden-token scan clean | none |
| C2 additional baseline | (1) none; (2) add one; (3) defer | **(1) none; mention Poisson in main** | `models.py`, `tab21`, `tab14` — count baseline + normalized pooling present | optional main-text mention of Poisson |
| C3 fairness metric | must add / optional / journal / satisfied | **optional if space, else journal** | `tab16` per-family served exists | optional one sentence |
| D1 venue track | (1) continue main; (2) investigate special session; (3) switch if scope matches; (4) do not switch | **(1) continue main** (benchmark/Veracity fit); investigate special session only with official CFP | `ieee_bigdata_feasibility_gate.md`, venue reports | none now; obtain CFP before any switch |
| D2 5V framing | edit / keep | **keep** (A3 fix strengthens Veracity) | introduction 5V paragraph | none |
| E citation/page budget | keep plainnat / switch to IEEE numeric | **keep for now** (9 pp; numeric would only save space) | `main_ieee.pdf` 9 pp | none required |
| Paper-1 self-plagiarism | author provides text / accept partial scan | **author item (non-blocking)** | Paper 1 text not in repo; no verbatim reuse detected | none in Stage 2 |

---

## Prof 2 reclassification + Stage 2 outcomes (Draft 3 Stage 2)

Prof 2 agreed with the Stage-1 factual audit but reclassified several optional
items as mandatory. All are now implemented.

| ID | Stage-1 class | Prof 2 reclass | Stage 2 outcome |
|---|---|---|---|
| R1 family-starvation | optional | **disclosure mandatory** (metric still optional) | added a concise main-text disclosure in `responsible.tex` grounded in `tab16`: under the equal request-equivalent objective the forecast-driven full-distribution policy serves a near-zero fraction of water/sewer in all four cities (0.0000 Austin/Chicago/SF, 0.0025 NYC) and of SF public safety (0.0000); "lower aggregate loss is not a fairness guarantee" |
| R2 citation style | page-budget note | **formatting/compliance requirement** | converted `main_ieee.tex` to IEEE numeric: `\bibliographystyle{IEEEtran}` + `\usepackage[numbers,sort&compress]{natbib}`; added `paper/IEEEtran.bst` v1.12; bibtex regenerated; bracketed numeric refs, 20 numbered entries, no undefined citations; 9 pages |
| R3 BigData Volume | already satisfied | **small precision edit** | added one clause to the intro 5V Volume sentence: scale enters via acquisition/exclusion/harmonization/provenance; the predictive task is defined on daily aggregated city–family panels, not raw records |
| R4 decision-loss wording | optional | **mandatory** | replaced the residual "all paired intervals excluding zero" with descriptive blocked-resampling wording in `results_decision`; trend/nonstationarity caveat retained |
| R5 baseline criticism | reviewer misunderstanding | **conscious tradeoff** | added a main-text Poisson sentence in `results_forecast` (beats naive 11/12, dominated by selected 12/12); stated benchmark-and-protocol contribution, not an algorithmic leaderboard; deep/hierarchical baselines deferred to journal |

## Venue-track note (Part 7)

- Default route: **main IEEE BigData path** (unchanged).
- Special session / workshop: **fallback only**; would require official current
  CFP/scope verification.
- **No route switch is authorized in Stage 2.** Official IEEE BigData
  special-session scope was not re-verified this stage (no browsing performed
  for it); investigate only before final submission if a switch is considered.
