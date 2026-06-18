# IEEE BigData 2026 — 10-Page Compression Plan

**INTERNAL DOCUMENT — never include on the public release branch.**

Branch `claude/bigdata-revision`, commit `b95c8b9`. **This is a plan only — do
not execute the compression until it is reviewed.** It specifies what stays in
the 10-page main paper and what moves to the supplement, preserving every piece
of validity evidence the review pass added.

---

## 0. Starting point and the central realization

- Current build: `paper/main.tex` is **17 pp in single-column `article`**
  (`11pt`, 1-inch margins); the supplement is 16 pp.
- Target: **IEEE BigData full paper = 10 pages incl. references**, IEEE
  conference two-column (`IEEEtran`, 10pt).
- **The documentclass conversion alone recovers most of the budget.** A
  single-column `article` page holds roughly half the text of an IEEE
  two-column page, so 17 article pages map to ≈ 8.5–9.5 IEEE two-column pages
  *before any cutting*. The compression is therefore **mostly a format
  conversion plus modest trimming and table relocation**, not drastic deletion.
- Consequence: we do **not** need to move decision-layer validity evidence out
  of the main paper. The non-identification result, the simulation boundary, and
  the leakage protocol all stay in the main text.

Do not restore the old "point forecasts disable the optimizer" claim. Keep the
narrowed Claim B. Make no deployment/staffing/backlog/causal/social-need claims.

---

## 1. Required main-paper retention (the 14 elements) — all stay, compactly

| # | Element | Where in main | Form |
|-:|---|---|---|
| 1 | Three contributions | Intro | the existing (1)(2)(3) sentence |
| 2 | Simulation boundary (sim≠deployment; reported≠need; request-equivalent≠crews; carryover≠observed) | Abstract + Formulation + one Limitations bullet | keep verbatim |
| 3 | Dataset scale + audit summary | Data §, `tab17` (compact) | 5-row audit table |
| 4 | Harmonization summary | Data § | one paragraph; full composition → supplement |
| 5 | Leakage/censoring protocol | Methods §, `tab18` split dates | compact dated table + prose; full proof → supplement |
| 6 | Core forecasting results | Results-Forecast §, `tab1` | validation-selected MAE table |
| 7 | Weather information-set caveat | Results-Forecast § | the A3 proxy + lagged-weather sentence |
| 8 | Normalized/log pooled sensitivity | Results-Forecast § | the one-sentence robustness result |
| 9 | Conformal calibration sensitivity | Results-Forecast § | coverage 77–81→88–90% sentence |
| 10 | Main decision-policy results | Results-Decision §, `tab3b`/`tab8` | compact policy/contrast numbers |
| 11 | Non-identification / tie-break result | Results-Decision §, **`tab11`** | **stays in main — the headline** |
| 12 | Horizon sensitivity | Robustness § | one sentence (stability statement) |
| 13 | Guard / reproducibility evidence | Methods § + a reproducibility paragraph | prose; `tab19` guard table → supplement |
| 14 | Limitations | Limitations § | keep all bullets (do not cut to save space) |

---

## 2. Figures — keep up to 3 in main, move 1

Actual compiled numbering: **Fig 1** = four-city panel overview; **Fig 2** =
accuracy gain by feature set; **Fig 3** = rolling-origin fold stability;
**Fig 4** = accuracy vs simulated decision value (the fixed-index diagnostic).

- **Keep:** Fig 1 (panel overview — Variety/Veracity), Fig 2 (accuracy gain),
  and **Fig 4** (accuracy vs simulated decision value — secondary but useful).
- **Move to supplement if space is tight:** **Fig 3** (rolling-origin fold
  stability) — supports a one-sentence robustness claim that can cite the
  supplement figure.

## 3. Tables — main vs supplement

**Stay in main (compact):**
- `tab1` validation-selected test MAE (core forecasting).
- `tab11` tie-break / non-identification (the headline decision evidence).
- One compact decision contrast block from `tab8` (proportional-vs-distribution
  and full-vs-median/mean, 12 cells → a small summary).
- `tab17` dataset audit (5 rows).
- `tab18` split dates (4 rows) — or fold into a protocol figure.

**Move to / keep in supplement:**
- `tab2` exhaustive MAE grid; `tab1b` selection detail.
- `tab12` full tie-break grid; `tab13/13b` conformal; `tab14` pooling;
  `tab15` horizon; `tab16` per-family served; `tab19` guards; `tab20` weather
  missingness; `tab21` Poisson; `tab22_b0` initial-carryover; `tab3/tab3b`
  full decision grid; `tab4/tab5/tab6/tab7/tab9/tab10`; family-composition
  tables. (Most already live in `s_tables`/`s_sensitivity`.)

## 4. Section-by-section compression actions

| Section | Action | Notes |
|---|---|---|
| Abstract | keep | already tightened this pass |
| Introduction | keep 3 contributions + governing question + 5V paragraph; trim the design-commitments list to 2 sentences | the (i)–(iv) detail is restated in Methods |
| Related work | compress to **three clusters**: 311/urban analytics; forecasting-to-decisions; cross-city pooling/transfer | move the capacity-planning and urban-computing paragraphs' detail to a sentence each; full version → supplement/journal |
| Formulation + Methods | **merge** into one "Benchmark and protocol" section; keep the loss equation, budget formula, tie-break rule, quantile-interpolation, leakage protocol | remove duplicated split/refit prose |
| Data + Data-stats | **merge**; keep audit table + harmonization paragraph + weather paragraph | full composition + exclusions detail → supplement (already there) |
| Results-Forecast | keep calendar/weather/pooling/transfer/conformal as 4 short paragraphs + `tab1` | exhaustive grid stays in supplement |
| Results-Decision | keep non-identification (`tab11`) + narrowed uncertainty + selection paragraphs | full grids → supplement |
| Robustness | compress to **one paragraph**: trend diagnostic + block-length + sensitivity suite (abandonment/yield/budget/Austin-other/b₀) all "unchanged" | tables already in supplement |
| Responsible | keep to one tight paragraph (reported-demand, per-family visibility, weights-are-values, oversight) | |
| Limitations | **keep all** — do not cut | credibility, not padding |
| Conclusion | keep; trim continuations sentence | |

## 5. Claims that must stay visible (do not move to supplement)

1. Objective **non-identification** under degenerate point forecasts + the
   tie-break table (`tab11`).
2. The simulation boundary (sim, reported demand, request-equivalent units,
   simulated carryover).
3. The three contributions and the benchmark/reproducibility framing.
4. Calendar-everywhere / weather-heterogeneous / pooling-and-transfer-hurt
   (with the normalization-robustness qualifier).
5. Conformal calibration exists and does not change the decision result.
6. The limitations.

## 6. Claims to remove or narrow

- None new. The reframe is already done: keep "non-identification," keep the
  **narrowed** Claim B (full distribution = one of two equivalent identifiers),
  keep the pooling result *with* the normalization qualifier. Do **not** restore
  "disable the optimizer" or "full predictive distribution beats its
  representations" as an unqualified uncertainty win.

## 7. Mechanical conversion checklist (for the execution pass, once approved)

1. Switch `\documentclass[11pt]{article}` → `\documentclass[conference]{IEEEtran}`
   (10pt two-column); replace `\maketitle`/author block with IEEE form.
2. Re-flow tables to `\begin{table}`/`table*` two-column floats; shrink wide
   tables (`\footnotesize`, drop non-essential columns to the supplement copy).
3. Apply the section merges in §4; move the relocated tables/figure to the
   supplement `\input` list (most are already there).
4. Compile; measure pages; trim related work and robustness first if over 10.
5. Keep references — they count toward the 10 pages; use the IEEE bibstyle.
6. Re-run the guard suite and the forbidden-token scan after the rewrite (the
   manuscript-terminology guard is armed).

## 8. Risk check against NO-GO

The NO-GO rule (compression forces hiding decision-layer validity,
harmonization, simulation boundary, or leakage controls) is **not triggered**:
every one of those has a compact main-text form in §1, and the supplement
already exists to hold the exhaustive evidence. Expected post-conversion length
before trimming is ≈ 8.5–9.5 IEEE pages, leaving headroom.

**Plan verdict: a 10-page IEEE BigData paper preserving all essential validity
evidence is feasible; the compression is primarily a format conversion plus the
§4 merges. Await review before executing.**
