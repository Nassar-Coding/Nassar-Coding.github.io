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
