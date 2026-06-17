# Professor Review — Implementation Report

**INTERNAL DOCUMENT — never include on the public release branch.**

Target: IEEE BigData 2026. Branch: `claude/bigdata-revision` (from the full
internal record `claude/new-session-56q4pt`). Date: 2026-06-16/17.

This report records what was implemented, deferred, and rejected from the
external expert review, the experiments added, the result/claim changes, and the
final GO/NO-GO. It follows the Phase-1 triage register and the Phase-3
feasibility gate (both in this directory).

---

## 1. Headline outcome

**GO maintained.** All four claim-gating experiments were run on a fresh,
exact reproduction of the pipeline; none forced abandonment. The central
decision claim was reframed (with the author's explicit approval) from
"point forecasts disable the optimizer" to **objective non-identification**,
which the evidence supports more strongly and which is more defensible. No
published *number* changed — `make all` regenerates every headline figure to
the digit — what changed are the decision-layer *claims*, now matched to new
evidence.

The one remaining gating item is **10-page compression** (the paper currently
compiles at 16pp + 15pp supplement); this is layout, not evidence omission —
every validity result has a compact main-text form and the supplement absorbs
the grids.

## 2. Reproduction and verification

- `make all` from versioned raw data reproduced exactly: budgets
  119/153/187, 29/38/46, 26/33/41, 8/11/13; quantile coverage 0.768–0.812;
  calendar gains −11.9/−15.6/−10.4/−10.2%; pooling +1.8/+6.5/−1.2/+4.1%.
- Guard suite: **37 passed, 0 skipped** (artifact guards pass once the pipeline
  is materialized; the armed manuscript-terminology guard passes).
- Paper compiles (pdflatex, 16pp, all cross-references resolve); supplement
  compiles (15pp).

## 3. Claim-gating experiments (the four stop conditions)

All added as standalone, reproducible scripts wired into a new `make
sensitivity` stage; each reads only frozen pipeline outputs.

| # | Experiment | Script | Outcome | Stop? |
|---|---|---|---|---|
| C1 | Tie-break / non-identification | `run_tiebreak_sensitivity.py` | 92–100% of allocation steps are ties; fixed ascending-index rule loses to proportional in all 12 (−1.2 to −58%); a **proportional secondary tie-break recovers proportional fully** (−0.03 to +0.8%); the full-vs-median/mean advantage is the same artifact and **vanishes under a proportional tie-break** (12/12 → 0/12). | Reframed per author Option 1; claim narrowed. Not abandoned. |
| C2 | Conformal calibration | `run_conformal_calibration.py` | Split-conformal lifts 90% coverage 0.77–0.81 → 0.88–0.90; the calibrated full-arm decision changes by median −0.10%. | No reversal. |
| C3 | Normalized / log pooling | `run_logpool_sensitivity.py` | "Pooling hurts" holds under log1p and per-city standardization (penalty shrinks, esp. Austin +4.1→+2.0%; still worse in 3/4; SF neutral). | No reversal. |
| C4 | Horizon robustness | `run_horizon_sensitivity.py` | Claim-bearing rankings stable at 30/60/90/180/full; only the three near-tied identified policies reshuffle (<1%). | No reversal. |

## 4. Result and claim changes

- **Decision claim A (reframed).** "Point forecasts disable the expected-value
  optimizer / failure mode" → "degenerate point forecasts non-identify the
  allocation objective; realized loss is tie-break dependent; a proportional
  secondary rule or a genuine predictive distribution recovers proportional's
  performance." (abstract, `results_decision`, `conclusion`, `formulation`.)
- **Decision claim B (narrowed).** "The full distribution beats its median /
  implied-mean representations (uncertainty helps)" → "the full distribution is
  one of two equivalent ways to identify the objective; its advantage over the
  degenerate arms is the same tie-break artifact and disappears under a
  proportional tie-break; calibration does not drive it."
- **Pooling (strengthened).** Added robustness to log/standardized
  normalization; conclusion retained.
- **Calibration (upgraded).** Conformal recalibration moved from "future work"
  to a reported sensitivity (coverage restored to ~90%; decision unchanged).
- **Wording.** "disable"→"non-identify"; "full predictive distribution"→
  "quantile-interpolated predictive distribution"; "never harmed"→"did not
  increase test loss in the pre-specified grid"; "safe check"→"low-cost
  diagnostic"; "transfers to"→"is associated with"; "City agencies use"→
  "Short-horizon forecasts are a natural planning input."

## 5. Implemented items (by review section)

- **A. Framing:** three contributions stated (#1, #8); boundary moved early in
  abstract (#2, #7); density reduced (#6); 5V/veracity framing implicit via the
  benchmark contribution and dataset audit (#4, #198–#202 partial).
- **B. Decision validity:** tie-break rule stated (#10); six tie-breakers +
  proportional secondary rule + smoothed arm tested (#9, #11, #12, #15, #16);
  tie frequency reported (#13); non-identification wording (#14, #168, #173);
  b0=0 stated (#29); κ budget formula (#25); myopic≠horizon (#17, already);
  per-family served table (#22).
- **C. Decision reporting:** main tie-break table (#188, #36 family already in
  tab3); "did not increase test loss" (#44); interval caveat (#47, already).
- **D. Horizon:** horizon-length cuts (#49, #190); trend framing retained
  (#48, #52–#54).
- **E. Weather:** proxy/upper-bound wording (#55); NY conditionality (#57,
  already); missingness table (#59); lagged-weather already in prose (#56).
- **F. Baselines/pooling:** Poisson GLM baseline (#65, #66); normalized/log and
  per-city-standardized pooling (#75, #76, #77); transfer scale discussion
  (#78, #79).
- **G. Uncertainty:** split-conformal implemented (#82, #83, #92);
  quantile-interpolation + flat tails + implied-mean stated (#87, #88, #91);
  coverage/width before-after table (#84, #86); calibrated-vs-uncalibrated
  decision (#189).
- **H. Dataset:** dataset audit table with acquired/excluded/retained (#93,
  #179); exclusions already justified in prose (#94–#99).
- **I. Harmonization:** composition tables already exist (#105, #106, #181,
  #197); Chicago structural absence (#111, guard G5).
- **J. Leakage:** split-date table with exact dates (#116, #180); 11-config
  grid listed (#43); guard-suite table (#152, #192); censoring proof artifact
  exists (#120 via `pooled_censoring.json` + guard G13).
- **K. Forecasting tables:** MAE tables already exist (#127–#132); Poisson and
  normalized-pooling tables added.
- **L. Responsible:** per-family served table linked (#140); reported-demand
  framing retained (#138).
- **M. Reproducibility:** `make all` verified (#148); guard table (#152);
  provenance hashes (#154, already); `make sensitivity` stage added.

## 6. Experiments added

Five standalone scripts, all under `make sensitivity`, all provenance-tracked:
`run_tiebreak_sensitivity.py`, `run_logpool_sensitivity.py`,
`run_conformal_calibration.py`, `run_horizon_sensitivity.py`,
`run_poisson_baseline.py`. New metrics: `tiebreak_sensitivity.csv`,
`tie_frequency.csv`, `logpool_sensitivity.csv`, `conformal_calibration.csv`,
`conformal_decision.csv`, `horizon_sensitivity.csv`, `poisson_baseline.csv`.

## 7. Tables/figures added

`tab11` tie-break (main) / `tab12` full grid; `tab13`/`tab13b` conformal;
`tab14` pooling; `tab15` horizon; `tab16` per-family served; `tab17` dataset
audit; `tab18` split dates; `tab19` guard suite; `tab20` weather missingness;
`tab21` Poisson. Provenance manifest now 56 artifacts.

## 8. Deferred (journal extension) and not added

- Negative-binomial (#67), GAM (#68), deep/global neural forecasters (#74):
  journal/out of scope; the count baseline (Poisson) and normalized pooling
  cover the reviewer's substantive concern.
- DP/offline oracle (#18): rejected; a labeled non-bounding reference already
  exists and an oracle would invite the operational-realism attack.
- Multiple objective forms (#19) and extensive priority-weight scenarios (#20):
  one normative scenario retained; more deferred to journal.
- Rolling multi-window evaluation (#51), all-city core-seven harmonization
  (#113 beyond Austin), expanded related-work synthesis (#159–#164),
  spatial/fairness expansion (#142 beyond scope statement): journal.
- κ / abandonment / initial-backlog grids beyond the existing sensitivity
  suite (#24, #27, #28, #30, #32, #33, #50): the existing suite already covers
  abandonment=0.10, one-family yield ×0.70/1.30, train+val budget recalibration,
  and Austin-without-other; κ and b0 are now *stated* with the formula and the
  non-identification reframe makes the decision conclusions insensitive to
  them, so additional grids are deferred. **Partially addressed, not full.**

## 9. Requires author decision (not actioned)

- Title change (#5).
- Manual/expert harmonization-accuracy audit (#108).
- Positioning vs prior single-city Paper 1 and self-plagiarism check (#166,
  #167); bounded-novelty literature search (#160, #165) — needs the author's
  knowledge of Paper 1 and a citation pass.

## 10. Known remaining work before submission

1. **10-page IEEE compression** (#193, stop #5): paper is 16pp; move exhaustive
   grids to supplement, keep one decisive table per claim. Layout only.
2. IEEE `\documentclass` conversion (currently `article`).
3. Bounded-novelty related-work pass (author + citations).
4. Optional: a visual leakage/censoring diagram (currently provided as the
   split-date table + guard table + `pooled_censoring.json` proof).

## 11. Tests run

`python3 -m pytest tests -q` → **37 passed**. `make all` exact reproduction.
`pdflatex` paper (16pp) and supplement (15pp) compile with resolved references.
Forbidden-terminology scan of all edited `.tex` clean.

## 12. Final git state

Branch `claude/bigdata-revision`, pushed to origin. Commit SHAs:
- `eca66de` validate decision-layer claims (experiments + triage + gate)
- `0fa729b` reframe decision claim; wire validity tables
- `0316e6f` Priority-1 evidence tables + supplement integration
- (this commit) Poisson baseline + implementation report

`git status` clean apart from regenerable, untracked `data/processed` and
`data/interim` (never committed).

## 13. GO/NO-GO

**GO**, conditional only on the 10-page compression and the author-decision
items (title, Paper-1 positioning, novelty citations). The scientific validity
concerns the review raised are resolved: the decision-layer claim is now a
defensible non-identification result, uncertainty is calibrated and its role
correctly narrowed, pooling is robust to normalization, the horizon framing is
honest, reproducibility is verified, and the evidence the review asked to "see"
is tabulated. If the author prefers to avoid compression, INFORMS JDS / IJF
remain the SWITCH targets with the same evidence package.
