# Draft 3 — Stage 2 Implementation Report

**INTERNAL DOCUMENT — never include on the public release branch.**

## 1–3. Branch / commits

- Branch: **`draft_3`**.
- Starting commit: **`15f96e7`** (Stage-1 audit).
- Final commit: see §16 / chat (this commit).

## 4–5. Edits made and files changed

**Manuscript (`paper/sections/`):** `abstract.tex`, `data.tex`, `data_stats.tex`,
`results_forecast.tex`, `results_decision.tex`, `formulation.tex`,
`robustness.tex`, `conclusion.tex`, `limitations.tex`, `responsible.tex`,
`introduction.tex`.
**Supplement (`supplement/sections/`):** `s_negative.tex`, `s_sensitivity.tex`,
`s_optimality.tex`, `s_tables.tex`.
**Build/config:** `scripts/make_paper_stats.py` (Table-1 generator: `table*` +
modeled-span caption), `paper/main_ieee.tex` (IEEE numeric citations),
`paper/IEEEtran.bst` (new, v1.12), `paper/main_ieee.bbl` (regenerated),
`paper/main_ieee.pdf`, `paper/main.pdf`, `supplement/supplement.pdf`.
**Audit docs:** `draft3_stage1_factual_trust_audit.md`,
`draft3_stage1_decision_log.md`, this report.

## 6. A1 — calendar-effect numbers (before/after)

- `abstract.tex`: **`8.6--14.0\%`** → **`10.0--14.0\%`** (fixed-estimator
  LightGBM calendar effect; matches the "intervals excluding zero" basis).
- `results_forecast.tex`: the validation-selected per-city numbers
  (11.9/15.6/10.4/10.2) are now explicitly labeled "a validation-selected
  comparison spanning **10.2–15.6%**", and a separate sentence adds the
  fixed-estimator effect "**10.0–14.0%** … all 28-day block-bootstrap intervals
  excluding zero". Abstract and body now report the same fixed-estimator range,
  with the selected range labeled as a distinct comparison.
- Verified: no `8.6--14` remains in any manuscript/supplement source.

## 7. A2 — study-window vs modeled-span provenance (resolved)

Per-city verification of the raw/retained data and the feature build:

| Span | Range | Source |
|---|---|---|
| 311 acquisition / study window | 2020-01-01 → 2025-12-31 | manifests, `data_sources.yml` |
| **Retained 311 (real, nonzero)** | 2020-01-01 → **2025-12-31** | raw daily CSVs (329 nonzero days after 2025-02-05, all four cities) |
| Densified panel | 2020-01-01 → 2025-12-31 | `panel_311.parquet` |
| **NOAA GHCN-Daily weather** | 2019-01-01 → **2025-02-06** | `weather_daily.parquet` |
| **Feature-supported modeled span** | 2020-01-28 → **2025-02-05** | `features.parquet` |
| Forecast / decision evaluation | ~2024-05 → 2025-02-05 | last 15% of features |

**Root cause (confirmed):** `build_features` calls
`feats.dropna(subset=weather_cols)` (line 96), so the single shared feature
panel — used by *every* feature set — is bounded by weather availability. NOAA
GHCN-Daily for the four stations ends 2025-02-06; with the target-day join
(weather day − 1) this caps the modeled span at 2025-02-05. **Real 311
observations through 2025-12-31 exist and are retained in the panel, but are not
modeled** because the shared weather-joined panel drops them. This is a
documented reason → **stop gate #2 not triggered**.

**Manuscript clarification added** (`data.tex` + Table-1 caption + supplement
`s_tables`): the 311 acquisition / study window and densified panel span
2020–2025-12-31, while the modeled span (all forecasting and decision
evaluation) runs 2020-01-28 → 2025-02-05, bounded by weather availability; later
311 observations are retained but not modeled.

## 8. A3 — Chicago exclusion count (before/after)

Recomputed from the raw Chicago CSV with the exact config patterns and
`build_panel` order: info-only **4,184,157**, aircraft 1,918,574, duplicates
523,055; total removed **6,625,786** = raw 11,309,296 − kept 4,683,510.

- `data.tex`: info-only **`4{,}184{,}158`** → **`4{,}184{,}157`**.
- Component sum is now 6,625,786, matching raw − kept exactly. No `4,184,158` or
  `6,625,787` remains in the manuscript/supplement.

## 9. B2 — "neutral objective" replacements (10 total)

Main paper (7): `formulation` (→ "equal request-equivalent weights … a
deliberately simple equal-weight choice, not a normatively neutral or normative
priority policy"); `results_decision` ×3 ("equal request-equivalent-weights
objective" / "equal-weight objective"); `robustness`, `conclusion`
("equal-weight objective"); `limitations` ("equal request-equivalent-weights
objective; Equal weights are a deliberately simple choice, not a normatively
neutral one"). Supplement (3): `s_negative`, `s_sensitivity`, `s_optimality`
("equal-weight objective"). No claim-bearing "neutral objective" remains.

## 10. Family-starvation disclosure (text + source)

Added to `responsible.tex`, grounded in `tab16_perfamily_served.csv` (moderate
regime, full-distribution arm): *"under the equal request-equivalent objective
the forecast-driven full-distribution policy attains low aggregate loss while
serving a near-zero fraction of the low-volume water/sewer family in all four
cities (and of public safety in San Francisco) … Lower aggregate simulated loss
is therefore not a fairness guarantee."* Evidence: water/sewer served fraction
0.0000 (Austin, Chicago, SF), 0.0025 (NYC); SF public safety 0.0000.

## 11. BigData Volume / modeling-unit clarification (text)

Added to the intro 5V Volume clause: *"this scale enters through acquisition,
exclusion, harmonization, and provenance, while the predictive task itself is
defined on daily aggregated city–family panels rather than on the raw records
directly."*

## 12. Poisson baseline response (text + source)

Added to `results_forecast`: *"a Poisson GLM (supplement) beats the naive
trailing mean in 11 of 12 (city, feature-set) cells but is dominated by the
validation-selected models in all 12; consistent with this being a
benchmark-and-protocol contribution rather than an algorithmic leaderboard, we
add no further models here and defer modern deep or hierarchical baselines to a
journal version."* Source: `poisson_baseline.csv` (beats naive 11/12; beats
selected 0/12, i.e., dominated 12/12).

## 13. Citation-style conversion summary

`main_ieee.tex`: `\usepackage[round]{natbib}` → `\usepackage[numbers,sort&compress]{natbib}`;
`\bibliographystyle{plainnat}` → `\bibliographystyle{IEEEtran}`. Added
`paper/IEEEtran.bst` v1.12 (verified header). bibtex regenerated `main_ieee.bbl`
(20 numbered entries, `\begin{thebibliography}{10}`). Citations render as
bracketed numbers; `\citet` renders "Author [N]" (acceptable IEEE form).
**No undefined citations, no `?` markers**, no author-year style in the IEEE
build. The article `main.tex` keeps `plainnat` (reference version, unchanged).

## 14. Page count before / after

- IEEE `main_ieee.pdf`: **9 pages → 9 pages** (numeric citations did not change
  the count; no overflows >15 pt).
- Article `main.pdf`: 17 pages. Supplement: 16 pages.

## 15. Guard / test result

`pytest tests -q` → **37 passed, 0 skipped** after all edits (including the
Table-1 caption change — guard G15 strings "Chicago has seven" preserved).
Forbidden-token scan clean; final manuscript scan free of "neutral objective",
stale `8.6--14`, and stale Chicago counts.

## 16. Stop gates

| Stop gate | Triggered? |
|---|---|
| 1 A2 provenance irreconcilable | **No** — weather-bounded, documented |
| 2 real post-2025-02-05 obs excluded w/o reason | **No** — reason is weather availability; now documented |
| 3 numeric citations break refs / exceed 10 pp | **No** — 9 pp, all resolve |
| 4 family-starvation contradicts decision-value framing | **No** — coexists; framed as "not a fairness guarantee" |
| 5 any edit hides non-identification/tie-break | **No** — `tab11` unchanged, in main |
| 6 operational/deployment/etc. claim introduced | **No** — scan clean |
| 7 guards fail | **No** — 37/37 |
| 8 compile fails | **No** — all compile |
| 9 page count >10 unfixable | **No** — 9 pp |

**No stop gate triggered.**

## Verdict

**Stage 2 complete — proceed to Stage 3 manuscript refinement.** All four
Stage-1 must-fixes (A1, A2, A3, B2) and all five Prof 2 reclassifications
(R1–R5) are implemented and verified. IEEE build 9 pages, numeric citations, 0
unresolved references, guards 37/37. Standing non-blocking item: the Paper-1
self-plagiarism diff (its text is still unavailable). No submission; repository
private.
