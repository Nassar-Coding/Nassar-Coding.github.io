# Draft 3 — Stage 2B: Frozen-Window Decision and Veracity Wording Fix

**INTERNAL DOCUMENT — never include on the public release branch.**

## 1–3. Branch / commits

- Branch: **`draft_3`**.
- Starting commit: **`2135950`** (Stage 2).
- Final commit: this commit (see chat).

## 4. Decision (recorded)

**For the IEEE BigData submission, the frozen common weather-joined evaluation
window is retained. Weather is NOT refreshed and the pipeline is NOT rerun.**

## 5. Rationale (not refreshing weather in Draft 3)

Refreshing weather would reopen every audited number, table, figure, guard
record, and claim; the manuscript is already compressed, numerically audited,
and under the IEEE page limit; the acceptance bottleneck is contribution
identity/framing, not test-window length; a longer deterministic decision path
would not address the simulation-vs-inference limitation; and a layer-aligned
weather refresh belongs to a later journal/long-term-artifact version.

## 6. A2 wording — exact provenance and corrected text

**Verified provenance (this stage).** Both layers were acquired in the same
run on **2026-06-09** (configured window 2019/2020-01-01 to 2026-01-01). The
311 layer covers nonzero observations **through 2025-12-31** (329 nonzero days
after 2025-02-05, all four cities); the NOAA GHCN-Daily layer in the pinned
`noaa-ghcn-pds` mirror covers the four stations **through 2025-02-06**
(`weather_daily.parquet`, raw GHCN `date` max 2025-02-06). `build_features`
drops rows with missing weather (`dropna(subset=weather_cols)`), so the single
shared weather-joined panel — and every feature set — ends **2025-02-05**.

**Honesty note / deviation from prescribed wording.** The Stage-2B prompt's
suggested phrase "the 311 layer was *later* refreshed through 2025-12-31" is not
what the manifests show: **both layers were retrieved on the same day**; the
weather mirror simply covers these stations only through 2025-02-06 while 311
covers through 2025-12-31. I therefore used accurate wording — "the NOAA
GHCN-Daily layer acquired for this benchmark covers the four stations through
2025-02-06, whereas the 311 layer covers through 2025-12-31" — rather than the
"later refreshed" phrasing. No claim of general NOAA unavailability is made.

**Corrected wording (replacing the Stage-2 "bounded by weather availability"):**
- `data.tex`: "The modeled span … is fixed by a frozen weather-joined
  evaluation panel … The NOAA GHCN-Daily layer acquired for this benchmark
  covers the four stations through 2025-02-06, whereas the 311 layer covers
  through 2025-12-31; the later 311 observations are therefore retained in the
  panel but lie outside this frozen common evaluation window and are not
  modeled."
- `supplement/s_tables.tex`: full pinned-layer paragraph ("All feature sets
  share a single weather-joined evaluation panel. The NOAA GHCN-Daily layer
  acquired for this benchmark spans 2019-01-01 to 2025-02-06 for the four
  stations; … the 311 layer covers through 2025-12-31, so later 311 observations
  are retained … but lie outside this frozen common evaluation window …").
- Removed all unqualified "weather availability" / "weather-bounded" /
  "GHCN-Daily availability" wording (scan now clean in the manuscript).

## 7. Table 1 caption / prose status

`data_stats.tex` caption now distinguishes (i) acquired/retained 2020–2025
counts (the densified window the table summarizes) from (ii) the shorter modeled
span — "the frozen weather-joined common evaluation panel — through 2025-02-05,
so not all retained requests enter modeling (see text)." The data-section prose
(Task 2 items 1–4) makes the same distinction. Guard G15 strings preserved
("Chicago has seven"; no "families per city").

## 8. Generator status

`scripts/make_paper_stats.py` (the Table-1 generator) updated to emit the same
caption wording and `table*`, so regeneration will not revert the fix.

## 9. Budget-consistency verification

`compute_frozen_budgets(panel, feats_days, …)` derives budgets from the
**feature-day (modeled-span) chronological split**: it computes the training
mean over `panel[sub.day <= t_end]`, where `t_end` is the 70% boundary of the
feature days (≈ 2023-08, well before 2025-02). Post-Feb-2025 retained
observations never enter the budget means. **Budget derivation is unaffected**
(budgets 119/153/187, 29/38/46, 26/33/41, 8/11/13 unchanged).

## 10. Family-starvation cross-reference (Task 3)

Added in `results_decision.tex` immediately after the 18–23% / 38–70% / 60–93%
loss-reduction sentence: "These aggregate simulated-loss reductions are not
fairness guarantees: the responsible-use discussion and the supplement show that
some low-volume families receive near-zero served fractions under the equal
request-equivalent objective." (No new metric; grounded in the existing
`tab16` / responsible-use disclosure.)

## 11. B1 descriptive-wording verification (Task 4)

Decision sections were already descriptive. Two residual uses of "significant"
(both *forecast* contrasts, legitimately inferential under the paper's framing)
were softened as a minimal precaution: `s_negative` "raises test MAE
significantly" → "raises test MAE … each 28-day block-bootstrap interval
excluding zero"; `results_forecast` fixed-estimator calendar effect "significant"
→ "consistent … intervals excluding zero". Scan for statistical-significance /
causal / policy-effect wording in all sections is now **clean**.

## 12. IEEEtran.bst provenance (Task 5)

- Path: `paper/IEEEtran.bst`. Version header: **V1.12 (2007/01/11)** (Michael
  Shell / Daly makebst lineage). Source: GitHub mirror
  `vbajpai/ieeetran-conf-preamble` (CTAN is blocked by the sandbox allowlist).
- It is the official IEEEtran **numeric** style; the reference list is numbered
  (`\begin{thebibliography}{10}`, 20 entries) and the PDF uses bracketed numeric
  citations `[N]` with no undefined citations.
- A newer canonical version (v1.14, 2015) exists but was not obtainable from the
  trusted mirror this stage (bardsoftware copy 404s). v1.12 produces correct IEEE
  numeric output, so per the prompt it does **not** block Stage 3; obtaining
  v1.14 from an official source is a pre-final-submission nicety.

## 13. Page count after edits

IEEE `main_ieee.pdf`: **9 pages** (unchanged; no overflows). Article `main.pdf`
17 pp; supplement 16 pp.

## 14. Guard / test result

`pytest tests -q` → **37 passed, 0 skipped**. Forbidden-token scan clean.

## 15. Stop gates

| Stop gate | Triggered? |
|---|---|
| 1 A2 untruthful w/o admitting accidental mismatch | **No** — truthful frozen-window wording; pinned weather layer ends 2025-02-06, 311 to 2025-12-31, same-day acquisition |
| 2 modeled-span clarification contradicts a headline | **No** |
| 3 family-starvation undermines decision claim beyond a caveat | **No** — one concise caveat |
| 4 page count >10 unfixable | **No** — 9 pp |
| 5 guards fail | **No** — 37/37 |
| 6 main compile fails | **No** |
| 7 supplement compile fails | **No** |
| 8 numeric citations break | **No** — intact |
| 9 operational/etc. claim introduced | **No** |

**No stop gate triggered.**

## 16. Final git status

Clean (only untracked regenerable `data/processed`, `data/interim`).

## Verdict

**Stage 2B complete — proceed to Stage 3 manuscript refinement.**
