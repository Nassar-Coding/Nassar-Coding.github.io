# Draft 3 — Stage 1 Factual-Trust Audit and Revision Gate

**INTERNAL DOCUMENT — never include on the public release branch.**

Stage 1 is verification only: no manuscript rewriting, no claim changes, no new
experiments. This memo decides what must be fixed in Stage 2.

## 1. Branch and starting commit

- Branch: **`draft_3`** (created this stage; did not previously exist).
- Starting commit: **`360198d`** ("IEEE BigData compression: official IEEEtran
  build = 9 pages"), inherited from `claude/bigdata-revision`.

## 2. Files inspected

`paper/main_ieee.tex` + `main_ieee.pdf` (9 pp, IEEEtran v1.8b); `paper/main.tex`
+ `main.pdf` (17 pp); `supplement/` (16 pp); `paper/sections/*.tex`;
`supplement/sections/*.tex`; `outputs/metrics/forecast_metrics.csv`,
`validation_selection.csv`, `decision_metrics.csv`, sensitivity CSVs;
`outputs/tables/*` incl. `tab9`, `tab11`, `tab17`, `_provenance.json`;
`data/interim/panel_manifest.json`; `data/raw/311/chicago_*`;
`data/processed/features.parquet`; `configs/service_families.yml`;
`src/preprocessing/build_panel.py`; `src/forecasting/models.py`; `tests/`;
`paper/references.bib`/`main.bbl`; the implementation/compression reports;
`ieee_bigdata_feasibility_gate.md`; git log. **No required artifact missing.**

---

## 3. Gate A — Numerical consistency

### A1. Calendar-effect numbers — **Confirmed issue, must fix**

Two ranges appear, describing two *different* comparisons:

| Range | Location | Comparison | Traces? |
|---|---|---|---|
| **8.6–14.0%** | `abstract.tex` l.15 | (stated as) "calendar augmentation reduces next-day error in every city, intervals excluding zero" | **No** — see below |
| **10.2–15.6%** | `results_forecast.tex` l.7–11 | validation-selected calendar vs validation-selected internal (test MAE) | **Yes**, exactly |

Recomputed from `forecast_metrics.csv` / `validation_selection.csv`:

- **Fixed-estimator** LightGBM calendar-vs-internal: NYC 11.9, Chicago 14.0, SF
  **10.0**, Austin 11.2 → **10.0–14.0%**.
- **Validation-selected** calendar-vs-internal: NYC 11.9, Chicago 15.6, SF 10.4,
  Austin 10.2 → **10.2–15.6%** (matches `results_forecast`).
- The value **8.6%** appears nowhere as a calendar effect; the only ~8.6 in the
  data is SF random-forest *calendar+weather*-vs-internal (8.56%) — a different
  feature set and model.

**Conclusion:** the abstract's `8.6–14.0%` lower bound is **stale**. The upper
bound (14.0%) matches the fixed-estimator effect, but the lower bound does not.
The abstract and `results_forecast` also cite *different* comparisons. **Stage-2
fix:** set the abstract to the fixed-estimator range **10.0–14.0%** (its
"intervals excluding zero" claim matches the `tab9` fixed-estimator significance
test), or harmonize to the selected `10.2–15.6%`. Not a NO-GO: the correct values
are traceable.

### A2. Study-window vs modeled-span — **Confirmed issue, must fix (hard gate)**

| Span | Start | End | Source |
|---|---|---|---|
| Acquisition / study window | 2020-01-01 | 2025-12-31 | `data.tex`, manifests |
| Retained raw | 2020-01-01 | 2025-12-31 | manifests |
| Densified panel | 2020-01-01 | **2025-12-31** | `panel_manifest.json` (`panel_date_range`) |
| **Feature availability (modeled span)** | 2020-01-28 | **2025-02-05** | `features.parquet` |
| Forecast test span | ~2024-05 | **2025-02-05** | last 15% of features |
| Decision-evaluation span | ~2024-05 | **2025-02-05** | same test window |

The main paper says "study window 2020-01-01 through 2025-12-31" (`data.tex`
l.18) and Table 1's caption repeats it with "Days 2192" (the densified panel),
**implying the full 2020–2025 is modeled**. The actual modeled / forecast-
evaluation span **ends 2025-02-05** (acquired 311 data runs out there; the panel
is densified with zeros to the configured window end). The supplement split-date
table already shows test ending Feb 2025, but the **main paper blurs the spans**.
**Stage-2 fix:** one clarifying sentence in Data/Methods distinguishing the
*study/acquisition window* (2020–2025) from the *modeled / forecast-evaluation
span* (through early Feb 2025), and a Table-1 caption note. Reconcilable → not a
NO-GO.

### A3. Chicago exclusion arithmetic — **Confirmed issue, must fix (Veracity)**

Recomputed from `data/raw/311/chicago_daily_by_category.csv.gz` with the exact
config patterns and the `build_panel` order (duplicates dropped first, then
info-only/aircraft via OR-mask over the remainder):

| Component | Manuscript prose | **Actual (recomputed)** |
|---|---|---|
| 311 information-only calls | 4,184,**158** | **4,184,157** |
| Aircraft-noise filings | 1,918,574 | 1,918,574 ✓ |
| Source-flagged duplicates | 523,055 | 523,055 ✓ |
| **Component sum** | **6,625,787** | **6,625,786** |
| Total removed (raw 11,309,296 − kept 4,683,510) | — | **6,625,786** |

The info-only count is **off by one (+1)**: prose 4,184,158 vs data 4,184,157
(no component overlap; the two exclusion patterns are disjoint). The prose sum
(6,625,787) therefore exceeds the true total removed (6,625,786) by one record.
**Stage-2 fix:** change `data.tex` info-only count to **4,184,157**. Reconcilable
→ not a NO-GO, but a Veracity-relevant must-fix.

---

## 4. Gate B — Decision-layer interpretation

### B1. Deterministic loss vs inference — **Already fixed / not present**

`results_decision`'s preamble explicitly reads the intervals as "descriptive
characterizations of a systematic, partly deterministic divergence within the
simulation", retaining a stationary reading only for Chicago/generous; the trend
diagnostic (Sec. 8) backs this. No "statistically significant", "robust", or
"confidence interval" wording survives in the decision sections. One residual
"all paired intervals excluding zero" (`results_decision` l.70) sits *inside*
that descriptive frame. **Optional tightening** only; not a must-fix.

### B2. "Neutral objective" language — **Confirmed issue, must fix**

`neutral`/`neutral (equal-weights) objective` appears in `formulation` l.36,
`results_decision` l.4/22/47, `robustness` l.41, `conclusion` l.14,
`limitations` l.17 (≈7 claim-bearing instances). Equal request-equivalent
weights are *not* normatively neutral. (The two `results_forecast` "neutral"
hits — l.38/56 — refer to the pooling result, not the objective; leave those.)
**Stage-2 fix:** reword to "equal request-equivalent weights" / "a deliberately
simple equal-weight objective (not a normative priority policy)". The paper
already qualifies it partially ("under the normative-priority sensitivity the
gap compresses"), so this is a contained wording pass.

### B3. Operational-overclaim scan — **Already fixed / not present**

Every match for staffing/capacity/crew/deployment/social-need/causal is a
**disclaimer** ("makes no claim about any city's real capacity…", "not a
deployable dispatch tool", "Reported requests are not social need", "no causal,
deployment, or operational-guidance claim"). Guard G7/G8 enforces the forbidden
tokens; the scan is clean. No claim-bearing overclaim remains.

---

## 5. Gate C — Forecasting / baseline / fairness

### C1. Baseline inventory

| Model | Where | Role |
|---|---|---|
| Naive trailing-7 | main + supplement | baseline floor (decision reference) |
| Seasonal-naive-7 | main + supplement | baseline |
| Ridge | supplement (`tab2`) / selection | candidate |
| Random forest | supplement / selection | candidate (selected in some cells) |
| LightGBM point | main headline + supplement | primary point model |
| LightGBM quantile | main + supplement | predictive distribution (decision arms) |
| Pooled / global (raw) | main (`results_forecast`) | negative-result candidate |
| Pooled (log1p / per-city-z) | main (results) + `tab14` | normalization robustness |
| Zero-shot transfer (LOCO, censored) | main + supplement | negative diagnostic |
| **Poisson GLM** | supplement (`tab21`, `s_models`) | count baseline (beats naive 11/12, dominated by selected 0/12) |

### C2. New baseline needed? — **Recommendation: option 1 (no new baseline)**

The set already includes a count-data baseline (Poisson) and a fairness-relevant
pooling-normalization study. The paper is a benchmark/protocol paper, not an
algorithm paper; a weak deep/foundation baseline would invite a "weak baseline"
critique and risks page-count/reproducibility churn. **Recommend: add no new
baseline; ensure Poisson and normalized pooling are clearly *mentioned* in the
main paper** (Poisson is currently supplement-only). Optional, not a must-fix.

### C3. Fairness / family-starvation metric — **Optional if space allows / journal**

Per-family served fractions exist (`tab16`, `decision_metrics`), and the
responsible-use section reports per-family visibility. A compact **worst-family
(minimum) served fraction** would sharpen the fairness argument but is not
essential for the benchmark contribution. **Recommend: optional (one sentence
if the page budget allows) or journal extension.** Do not implement in Stage 1.

---

## 6. Gate D — Venue / track positioning

### D1. Main track vs special session — **Recommendation: option 1 (continue main path)**

The paper's contribution is a reproducible public-data **benchmark + evaluation
protocol + Veracity** story, not algorithmic novelty — a legitimate fit for
IEEE BigData's applications/benchmarks space (the feasibility gate already
recorded GO, with a Government-Track / Big-Data-Benchmarks orientation). Main-
track risk: reviewers expecting systems/algorithm novelty (mitigated by the
explicit benchmark framing). Special-session risk: scope mismatch / unknown CFP.
**A route switch would require the official current IEEE BigData CFP and special-
session list, which are not in the repo and were not browsed.** Recommend
continue main path; investigate a special session only if its official scope
strongly matches. Do not switch now.

### D2. 5V framing adequacy — **Already satisfied**

Intro 5V paragraph: Volume (36.8M acquired / 30.2M retained — supported), Variety
(four cities, distinct 311 systems, calendar, NOAA weather — supported), Veracity
(provenance manifests, exclusions, guards, reproduction — supported; **the A3
off-by-one weakens this until fixed**), Value (forecast-to-decision evaluation —
supported), Velocity (explicitly out of scope). No edit needed beyond fixing A3.

---

## 7. Gate E — Page budget / evidence visibility

Official IEEEtran build = **9 pages** (references included); ~1 page of budget
remaining. All spine items visible:

| Spine item | Main-paper location | Supplement | Sufficient? |
|---|---|---|---|
| Simulation boundary | abstract, formulation, limitations | s_ethics | ✓ |
| Non-identification / tie-break **table** | results_decision (`tab11`, full-width) | `tab12` | ✓ (in main) |
| b₀ / initial-carryover | robustness | `tab22_b0` | ✓ |
| Conformal calibration | results_forecast | `tab13` | ✓ |
| Normalized/log pooling | results_forecast | `tab14` | ✓ |
| Horizon sensitivity | robustness | `tab15` | ✓ |
| Dataset/protocol audit | Table 1 (`data_stats`) | `tab17`,`tab18` | ✓ |
| Leakage/censoring protocol | methods | `tab18`, `pooled_censoring.json` | ✓ |
| Guard/reproducibility | methods + repro statement | `tab19`, `s_repro` | ✓ |
| Limitations | limitations | s_ethics | ✓ |

Citation style is currently `plainnat` (author-year); switching to IEEE numeric
would *save* space, so the bib style is **not** a page-budget risk. No spine
item is at risk from the Stage-2 fixes (all are number/word edits + ≤2 clarifying
sentences).

---

## 8. Classification table

| Issue | Classification | Evidence checked | Result | Stage 2 action | Stop gate? |
|---|---|---|---|---|---|
| A1 calendar 8.6% | Confirmed — must fix | `forecast_metrics`, `validation_selection`, `tab9`, abstract | 8.6% stale; true fixed-estimator 10.0–14.0%, selected 10.2–15.6% | set abstract to 10.0–14.0% (or harmonize to 10.2–15.6%) | No |
| A2 span blur | Confirmed — must fix | `features.parquet`, `panel_manifest`, `data.tex`, `data_stats` | modeled span ends 2025-02-05; paper implies through 2025-12-31 | add study-window vs modeled-span clarification + Table 1 note | No |
| A3 Chicago off-by-one | Confirmed — must fix | raw Chicago CSV, `build_panel`, config, `panel_manifest` | info-only 4,184,158→**4,184,157**; total 6,625,786 | correct info-only count in `data.tex` | No |
| B1 inferential wording | Already fixed / not present | `results_decision`, `robustness` | descriptive framing present; 1 residual in-frame | optional: tighten l.70 | No |
| B2 "neutral objective" | Confirmed — must fix | 7 instances across sections | not normatively neutral | reword to "equal request-equivalent weights / deliberately simple" | No |
| B3 operational overclaim | Already fixed / not present | all sections + guards | all disclaimers; guard-enforced | none | No |
| C2 new baseline | Reviewer misunderstanding / optional | `models.py`, `tab21`, `tab14` | set sufficient; Poisson supplement-only | optional: mention Poisson in main | No |
| C3 fairness metric | Optional if space / journal | `tab16`, `decision_metrics`, responsible | per-family served exists | optional: worst-family served fraction | No |
| D1 venue track | Requires author decision (default: continue) | feasibility gate, venue reports | benchmark fit for main track | continue main; CFP needed to consider special session | No |
| D2 5V framing | Already satisfied | introduction | all Vs supported | none (A3 strengthens Veracity) | No |
| E spine visibility | Already satisfied | `main_ieee.pdf` 9pp, sections | all 15 present, 1pp budget | none | No |

---

## 9. Recommended Stage-2 actions (targeted; no rewriting)

1. **A3** — `data.tex`: info-only `4{,}184{,}158` → `4{,}184{,}157` (and confirm
   the implied Chicago total/Veracity sentence reads 6,625,786 if stated).
2. **A1** — `abstract.tex`: `8.6--14.0\%` → `10.0--14.0\%` (fixed-estimator
   calendar effect; matches the "intervals excluding zero" / `tab9` claim).
3. **A2** — `data.tex`/`methods.tex` + Table 1 caption: add one sentence
   distinguishing the study/acquisition window (2020–2025) from the modeled /
   forecast-evaluation span (through early Feb 2025; panel densified to the
   window end).
4. **B2** — reword the ~7 "neutral objective" instances to "equal
   request-equivalent weights" / "deliberately simple equal-weight objective
   (not a normative priority policy)".
5. *Optional (if budget allows):* mention Poisson in the main paper (C2); tighten
   `results_decision` l.70 (B1); add a worst-family served-fraction sentence (C3).
6. Recompile `main_ieee.pdf`; re-run guards + forbidden scan; re-verify ≤10 pp
   and 0 undefined refs.

All four must-fixes are number/word edits plus ≤2 clarifying sentences — no
experiments, no claim changes, no table/figure revisions, well within the 1-page
budget.

## 10. Stop-gate check

| Stop gate | Triggered? |
|---|---|
| 1 calendar values untraceable | **No** — true values traced (10.0–14.0% / 10.2–15.6%); only the stale 8.6% needs correcting |
| 2 span inconsistency irreconcilable | **No** — fully reconciled (modeled span ends 2025-02-05) |
| 3 Chicago arithmetic irreconcilable | **No** — reconciled (info-only 4,184,157; total 6,625,786) |
| 4 unsupported operational claim in IEEE paper | **No** — all disclaimed |
| 5 non-identification table not in main | **No** — `tab11` is in the main paper |
| 6 paper exceeds 10 pages | **No** — 9 pages |
| 7 citation fix would exceed 10 pages | **No** — numeric style would save space |
| 8 required artifacts missing | **No** — all present |

**No stop gate triggered.**

## 11. Verdict

**Stage 1 GO — proceed to Stage 2 targeted implementation.** Four confirmed
must-fix issues (A1, A2, A3, B2), all small and contained; several optional
improvements; one standing author item (venue track default = continue; Paper-1
self-plagiarism diff still needs that paper's text but does not block Stage 2).

---

## Addendum — Prof 2 reclassification (Draft 3 Stage 2)

Prof 2 agreed with this factual audit and reclassified several Stage-1 optional
items as **mandatory**; all are implemented in Stage 2 (see
`draft3_stage2_implementation_report.md`):

- **R1 (family starvation):** optional → **disclosure mandatory**. Added in
  `responsible.tex`, grounded in `tab16` (water/sewer served ≈0 in all four
  cities; SF public safety served ≈0).
- **R2 (citation style):** page-budget note → **compliance requirement**.
  `main_ieee.tex` converted to IEEE numeric (`IEEEtran.bst`, `[numbers]natbib`).
- **R3 (Volume framing):** already satisfied → **small precision edit**. Intro
  Volume clause clarifies the modeling unit is daily aggregate panels.
- **R4 (decision-loss wording):** optional → **mandatory**. Residual "intervals
  excluding zero" replaced with descriptive wording.
- **R5 (baseline criticism):** "reviewer misunderstanding" → **conscious
  tradeoff**. Poisson mentioned in main text; deep baselines deferred to journal.

The A1/A2/A3/B2 must-fixes are likewise implemented. A2 provenance was resolved
during Stage 2: the modeled span ends 2025-02-05 because `build_features` drops
rows with missing weather (`dropna(subset=weather_cols)`) and NOAA GHCN-Daily
the pinned NOAA GHCN-Daily layer for the four stations covers only through 2025-02-06; real 311
observations through 2025-12-31 are retained in the densified panel but not
modeled — a documented reason, so stop gate #2 is **not** triggered.
