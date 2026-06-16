# Professor Review Triage Register

**INTERNAL DOCUMENT — never include on the public release branch.** It
references review/venue strategy and uses planning language excluded from
public artifacts by guard G7/G8.

Target: IEEE BigData 2026. Branch: `claude/bigdata-revision` (from the full
internal record). Date: 2026-06-16.

## Classification legend

1. Already satisfied (evidence in current code/manuscript)
2. Must fix before IEEE BigData
3. Should fix before IEEE BigData if feasible
4. Move to supplement
5. Journal-extension work
6. Reject / do not implement (would over-expand or distort)
7. Requires decision from author

"New run?" = requires re-executing a pipeline stage or a new experiment
(vs. text/table-only). Risk = consequence if left unfixed for BigData.

---

## How the current artifact already stands (grounding)

Verified by direct reading of the code and `.tex` sources on this branch:

- **Simulation boundary** is pervasive (`formulation.tex`, `limitations.tex`,
  `responsible.tex`, allocation docstrings): "abstract request-equivalent
  capacity units", "simulation", "no causal/deployment/operational claim".
- **Tie-break mechanism** is already explained with worked deficit/surplus
  examples in `supplement/sections/s_optimality.tex` and `results_decision.tex`
  ("allocation is decided by tie-breaking"). The *experiment* testing
  alternative tie-breakers does **not** exist yet, and the abstract still uses
  "disable"/"failure mode".
- **Tie-break rule (confirmed in code):** `greedy_allocate` pushes
  `(-(gain), s, nxt)` to a heap, so ties resolve on `s` — **fixed ascending
  family-index order**. Under equal weights every family's marginal value is
  `kappa` until its deficit boundary, so point-greedy concentrates units on
  low-index families. This is almost certainly *why* it loses to proportional.
- **Initial backlog** `b0 = 0` (confirmed: `simulate()` sets
  `carryover = np.zeros(S)`); not currently stated in the manuscript.
- **Trend/horizon:** a Newey–West trend diagnostic exists (`robustness.tex`,
  `trend_diagnostics.csv`, `tab10`); explicit horizon-length cuts
  (30/60/90/180/full) do **not** exist.
- **Existing result tables** (in `outputs/tables/`): tab1/tab1b/tab2 (MAE),
  tab3/tab3b (decision policy grid), tab4 (rank agreement), tab5 (quantile),
  tab6 (selection), tab7 (sensitivity), tab8 (decision inference), tab9
  (forecast inference), tab10 (trend), family_composition_{city}. So a large
  share of the "needed table" items already have artifacts.
- **Pooling** is raw-count LightGBM with city indicators — **no log/normalized
  variant**. This is the most legitimate forecasting validity gap.
- **Quantile calibration:** coverage reported (77–81% at nominal 90%);
  conformal is "future work" only. No calibrated-vs-uncalibrated decision run.
- **Guards:** 16 guards (25 test functions) enforce the protocol incl.
  forbidden-terminology scans and provenance hashes; described in prose, not a
  table.
- **Pipeline runs** in this environment (numpy/pandas/sklearn/lightgbm/
  statsmodels present; raw aggregated data on disk). `make all` is being
  re-executed to verify one-command reproduction.

---

## A. Core contribution and framing

| # | Prof | Class | Action | Artifact | New run? | Risk if unfixed |
|---|---|---|---|---|---|---|
| 1 | Crit | 2 | Restate as exactly **three** contributions (benchmark / leakage-controlled forecasting eval / simulated allocation study); fold the 4 commitments under #2 | `introduction.tex` | no | High — reviewer can't locate the contribution |
| 2 | Crit | 1→2 | Already pervasive; add one explicit boundary sentence to the abstract early | `abstract.tex` | no | Med |
| 3 | High | 3 | Sweep remaining "optimization/optimizer" → "simulated allocation / expected-value policy" except when naming the math | all sections | no | Med |
| 4 | High | 2 | Add 5V/veracity/provenance framing sentence (ties to 198–202) | `introduction.tex`,`conclusion.tex` | no | Med |
| 5 | Med | 7 | Title change is the author's call; current title is honest | — | no | Low |
| 6 | Med | 3 | Reduce abstract numeric density to dataset size, calendar gain, pooling/transfer, point-vs-distribution | `abstract.tex` | no | Low |
| 7 | Med | 3 | Move simulation boundary earlier in abstract | `abstract.tex` | no | Low |
| 8 | Med | 3 | Split contributions vs findings into separate paragraphs | `introduction.tex` | no | Low |

## B. Decision-layer validity (the crux)

| # | Prof | Class | Action | Artifact | New run? | Risk |
|---|---|---|---|---|---|---|
| 9 | Crit | 2 | Add tie-breaking sensitivity experiment | `allocation.py`,`run_decision.py`,new table | **yes** | **Fatal** — headline may be a tie-break artifact |
| 10 | Crit | 2 | State the exact rule: deterministic ascending family index | `formulation.tex`/`methods.tex` | no | Crit |
| 11 | Crit | 2 | Implement ≥5 tie-breakers (fixed, random×seeds, proportional, largest-carryover, largest-forecast, smallest-alloc) | `allocation.py` | **yes** | Crit |
| 12 | Crit | 2 | Point-greedy + proportional secondary rule policy | `allocation.py` | **yes** | Crit |
| 13 | Crit | 2 | Empirical tie-frequency / flat-region diagnostic (supplement worked examples already exist) | new metric | **yes** | High |
| 14 | Crit | 2 | Reframe "optimizer failure" → "objective non-identification under degenerate forecasts" | `abstract.tex`,`results_decision.tex` | no | Crit |
| 15 | High | 3 | Smoothed point arm (Gaussian/Poisson residual band around point fc) | `allocation.py`,`run_decision.py` | **yes** | Med — reviewer "just add noise" |
| 16 | High | 3 | Regularized policy = proportional-deviation penalty (≈ #12) | `allocation.py` | **yes** | Med |
| 17 | High | 1 | Already stated (myopic ≠ horizon-optimal) in `formulation.tex`+docstring | — | no | Low |
| 18 | Med | 6 | DP oracle rejected for BigData; labeled non-bounding reference already exists; explain why omitted | `formulation.tex` | no | Low |
| 19 | Med | 5 | Alternative objective forms → journal | — | no | Low |
| 20 | High | 5/7 | One normative scenario exists; more weight scenarios = journal/author | — | no | Med |
| 21 | Med | 3 | State exact normative weights + "illustrative only" (already in `decision.yml`) | supplement | no | Low |
| 22 | High | 2 | Per-family unserved-stock table (data already in `decision_metrics.csv`) | new table | no* | High — claimed but not shown |
| 23 | High | 1→3 | "request-equivalent unit ≠ worker/crew/truck" — reinforce in main text | `formulation.tex` | no | Med |
| 24 | High | 3 | State κ=50 is an arbitrary scale; add κ sweep | `decision.yml`,run | **yes** | Med |
| 25 | High | 1→3 | Add explicit budget formula `B=round(f·mean_train/κ)` (in code already) | `formulation.tex` | no | Med |
| 26 | Med | 3 | State rounding = `round()`, floored at family count; note Austin | `formulation.tex` | no | Low |
| 27 | High | 3 | Austin small-budget check via κ sweep / fractional capacity | run | **yes** | Med |
| 28 | Med | 3 | κ ∈ {25,50,100} grid | run | **yes** | Low |
| 29 | Crit | 2 | State `b0 = 0` explicitly | `formulation.tex` | no | Crit (cheap) |
| 30 | High | 3 | Initial-backlog sensitivity (b0=0 / warm-up / train-avg) | run | **yes** | Med |
| 31 | Med | 1 | Already "simulated unresolved request-equivalent carryover" | — | no | Low |
| 32 | Med | 3 | Abandonment grid {0.05,0.10,0.20} | `decision.yml`,run | **yes** | Low |
| 33 | Med | 3 | (= #32) | — | yes | Low |
| 34 | Low | 1 | Limitation stated | — | no | Low |
| 35 | Med | 1 | Limitation stated | — | no | Low |

\* #22 needs only a table-builder addition; the per-family numbers already
exist in `served_fraction_by_family`/`loss_share_by_family`.

## C. Decision-result reporting

| # | Prof | Class | Action | Artifact | New run? | Risk |
|---|---|---|---|---|---|---|
| 36 | Crit | 1 | `tab3_decision_all`+`tab3b_decision_main` exist — ensure one is in main | tables | no | Crit→Low |
| 37 | High | 1 | abs loss + % reduction both in `decision_metrics.csv` | — | no | Low |
| 38 | High | 1 | paired diffs+CIs in `decision_inference.csv`/`tab8` | — | no | Low |
| 39 | Med | 4 | policy ranking → supplement | tab | no | Low |
| 40 | High | 1→2 | proportional-vs-distribution across 12 cells: ensure visible table | `tab8`/new | no | Med |
| 41 | High | 1 | full-vs-median/implied in `tab8` | — | no | Low |
| 42 | High | 1 | decision-vs-MAE selection in `tab6`/`decision_selection.csv` | — | no | Low |
| 43 | High | 2 | List all 11 configs explicitly (`POINT_CONFIGS`) | supplement/methods | no | Med |
| 44 | Med | 2 | "never harmed" → "did not increase test loss in the pre-specified grid" | `results_decision.tex` | no | Med |
| 45 | Med | 3 | Keep Fig 4 but lean on tables | — | no | Low |
| 46 | Med | 3 | Clarify Fig 4 is the point-greedy diagnostic; add distribution/proportional view if space | figure | maybe | Low |
| 47 | Med | 1 | Caveat already in `results_decision.tex`/`robustness.tex`; echo in caption | caption | no | Low |

## D. Horizon dependence and trend

| # | Prof | Class | Action | Artifact | New run? | Risk |
|---|---|---|---|---|---|---|
| 48 | High | 2 | Keep trend honesty; add horizon sensitivity | run+table | **yes** | High |
| 49 | Crit | 2 | Horizon cuts 30/60/90/180/full (re-slice `daily_loss`; cheap) | `run_decision.py` | **yes** | High |
| 50 | High | 3 | Warm-up sensitivity (≈ #30) | run | **yes** | Med |
| 51 | Med | 5 | Rolling/multiple test windows → journal | — | no | Low |
| 52 | Med | 1 | Level vs diff trends both reported in `robustness.tex` | — | no | Low |
| 53 | High | 1 | "descriptive under trend" already explicit | — | no | Low |
| 54 | Med | 2 | Ensure no "significant" for trend-dominated contrasts (= #125) | sections | no | Med |

## E. Forecasting task / information set

| # | Prof | Class | Action | Artifact | New run? | Risk |
|---|---|---|---|---|---|---|
| 55 | Crit | 1→2 | A3 stated; sharpen to "proxy / upper-bound" wording | `formulation.tex`,`abstract.tex` | no | Med |
| 56 | High | 2 | Promote lagged-weather to a compact main table (numbers exist in prose) | new table | no | Med |
| 57 | High | 1 | NY conditionality stated | — | no | Low |
| 58 | Med | 1 | A2 one-station limitation stated | — | no | Low |
| 59 | Med | 3 | Weather missingness rates table | supplement | **yes**(compute) | Low |
| 60 | Med | 1 | ≤7-day linear interpolation stated | — | no | Low |
| 61 | Med | 3 | Justify snow=0 by station convention | supplement | no | Low |
| 62 | Low | 1 | Calendar features listed in `methods.tex` | — | no | Low |
| 63 | Med | 1 | Lag windows "end at day t" stated | — | no | Low |
| 64 | Low | 1 | One-hot specs stated | — | no | Low |

## F. Forecasting baselines and models

| # | Prof | Class | Action | Artifact | New run? | Risk |
|---|---|---|---|---|---|---|
| 65 | High | 3 | Add count-data baseline (Poisson) | `models.py` | **yes** | Med |
| 66 | High | 3 | Poisson GLM (statsmodels) with calendar/weather/lags | `models.py`,`run_forecasting.py` | **yes** | Med |
| 67 | Med | 5 | NB baseline → journal unless overdispersion forces it | — | no | Low |
| 68 | Med | 6 | GAM → journal/omit | — | no | Low |
| 69 | Low | 1 | Ridge kept, not sole baseline (Poisson added) | — | no | Low |
| 70 | Low | 1 | RF caveat fine | — | no | Low |
| 71 | Med | 1→3 | Fixed-hyperparameter justification stated; reinforce | `methods.tex` | no | Low |
| 72 | High | 2 | Hyperparameter table (verify/extend `s_models.tex`) | supplement | no | Med |
| 73 | Med | 3 | Runtime/compute from this run (`s_compute.tex`) | supplement | no | Low |
| 74 | Med | 6 | No deep model — reject; do log-pooling instead | — | no | Low |
| 75 | Crit | 2 | **Normalized/log1p global pooling** | `run_forecasting.py` | **yes** | **Fatal** — "pooling hurts" may be a scale artifact (STOP cond. #3) |
| 76 | High | 2 | (= #75) per-city standardized / mean-scaled targets | run | **yes** | Crit |
| 77 | Med | 3 | City-specific intercept / post-hoc scaling | run | **yes** | Med |
| 78 | Med | 2 | Reframe zero-shot transfer as diagnostic | `results_forecast.tex` | no | Med |
| 79 | High | 3 | Scale-normalized transfer comparison | run | **yes** | Med |
| 80 | Med | 3 | within- vs cross-scope selection table/diagram | supplement | no | Low |
| 81 | Low | 1 | "validation-selected" defined; consistent | — | no | Low |

## G. Probabilistic forecasting and uncertainty

| # | Prof | Class | Action | Artifact | New run? | Risk |
|---|---|---|---|---|---|---|
| 82 | Crit | 2 | Split-conformal calibration sensitivity | `run_forecasting.py` | **yes** | **High** (STOP cond. #2) |
| 83 | Crit | 2 | Conformal moved from "future work" to implemented sensitivity | run | **yes** | High |
| 84 | High | 1 | Pinball loss in `quantile_metrics.csv`/`tab5` | — | no | Low |
| 85 | High | 3 | Family-level coverage | compute | **yes** | Med |
| 86 | Med | 3 | Interval width / sharpness | compute | **yes** | Low |
| 87 | High | 2 | "full distribution" → "quantile-interpolated predictive distribution" | all sections | no | Med |
| 88 | Crit | 2 | State interpolation exactly (linear inverse-CDF, 99-pt grid [.01,.99]) + tails (flat clamp) | `methods.tex` | no | Crit |
| 89 | High | 3 | Tail-extrapolation sensitivity | run | **yes** | Med |
| 90 | Med | 3 | Crossing frequency before non-crossing correction | compute | **yes** | Low |
| 91 | High | 2 | Implied-mean construction = mean of 99-pt samples (state) | `methods.tex` | no | Med |
| 92 | Crit | 2 | Calibrated-vs-uncalibrated distribution-aware allocation table | run | **yes** | **Crit** (STOP cond. #2) |

## H. Dataset construction and exclusions

| # | Prof | Class | Action | Artifact | New run? | Risk |
|---|---|---|---|---|---|---|
| 93 | High | 2 | Consolidated dataset audit table (acquired/excluded/retained per city) | new table | no | Med |
| 94 | High | 1 | Exclusions justified in `data.tex`/`s_data.tex` | — | no | Low |
| 95 | High | 1 | Chicago info-only (4,184,158) stated | — | no | Low |
| 96 | High | 1 | Chicago aircraft (1,918,574) stated | — | no | Low |
| 97 | Med | 3 | Name exact Chicago duplicate flag/column | supplement | no | Low |
| 98 | Med | 3 | Name exact SF duplicate field | supplement | no | Low |
| 99 | Low | 1 | NYC dual-method agreement (270,978) stated | — | no | Low |
| 100 | Med | 1 | Study window (D14) justified | — | no | Low |
| 101 | High | 3/5 | COVID sensitivity (exclude-2020) — fold stability partly mitigates | run | **yes** | Med |
| 102 | Med | 3 | Mention COVID/structural breaks in `data.tex` | — | no | Low |
| 103 | Med | 1 | Manifests/checksums/timestamps; mutability noted | — | no | Low |
| 104 | Low | 3 | License/source-terms table | supplement | no | Low |

## I. Harmonization and city comparability

| # | Prof | Class | Action | Artifact | New run? | Risk |
|---|---|---|---|---|---|---|
| 105 | Crit | 1 | Harmonization audit exists (`s_harmonization*`, family_composition) | — | no | Low |
| 106 | Crit | 1 | Family-composition table exists per city | — | no | Low |
| 107 | High | 3 | Austin "other" top-category audit (from `family_composition_austin.csv`) | supplement | no | Med |
| 108 | High | 7 | Manual/expert mapping-accuracy audit — needs author | — | no | Med |
| 109 | Med | 4 | Ambiguous-category list → supplement | — | no | Low |
| 110 | Med | 1 | Ordered-precedence example present (noise before housing) | — | no | Low |
| 111 | High | 1 | Chicago no-noise structural (G5 guard) | — | no | Low |
| 112 | Med | 1 | "operationally analogous planning buckets" used | — | no | Low |
| 113 | Med | 1 | Austin exclude-other sensitivity exists | — | no | Low |
| 114 | Med | 3 | Note granularity differences | `data.tex` | no | Low |
| 115 | Med | 3 | State volume (not per-capita rate) rationale | `formulation.tex` | no | Low |

## J. Evaluation design and leakage control

| # | Prof | Class | Action | Artifact | New run? | Risk |
|---|---|---|---|---|---|---|
| 116 | High | 2 | Print exact train/val/test dates (from `chrono_split`) | new table | no | Med |
| 117 | Med | 2 | State split is per-city chronological | `methods.tex` | no | Low |
| 118 | High | 3 | Validation-only-selection protocol diagram/table | new fig/table | no | Med |
| 119 | Med | 1 | Refit on train+val stated | — | no | Low |
| 120 | Crit | 3 | Pooled-censoring diagram (proof in `pooled_censoring.json`) | new fig/table | no | Med |
| 121 | High | 3 | Transfer censor dates (G3 enforces) | supplement | no | Low |
| 122 | High | 1→3 | Preprocessing-leakage statement (scaling/encoding train-fit) | `methods.tex` | no | Low |
| 123 | Med | 4 | Fold windows table (from `fold_metrics.csv`) | supplement | no | Low |
| 124 | Med | 1 | 28-day block justified; 14/56 sensitivity exists | — | no | Low |
| 125 | Med | 2 | "interval excludes zero" not "significant" (= #54) | all sections | no | Med |
| 126 | Med | 1 | Directional-consistency emphasis present | — | no | Low |

## K. Forecasting results presentation

| # | Prof | Class | Action | Artifact | New run? | Risk |
|---|---|---|---|---|---|---|
| 127 | High | 1 | Full MAE table `tab1`/`tab2` | — | no | Low |
| 128 | High | 1 | Absolute baseline MAE in `tab1` | — | no | Low |
| 129 | Med | 1 | Selected-model table `validation_selection.csv` | — | no | Low |
| 130 | High | 2 | Weather marginal-effect table (= #56/#184) | new table | no | Med |
| 131 | Med | 1 | Austin null visible | — | no | Low |
| 132 | High | 1→3 | Pooled/local table `tab9` | — | no | Low |
| 133 | High | 3 | Transfer table (loco rows in `forecast_metrics.csv`) | new table | no | Low |
| 134 | Med | 4/5 | Family-level forecasting MAE → supplement | — | maybe | Low |
| 135 | Med | 3 | Normalized MAE / MASE column | compute | **yes** | Low |
| 136 | Low | 1 | MAE primary; no MAPE | — | no | Low |
| 137 | Med | 3 | State MAE maps to allocation loss | `methods.tex` | no | Low |

## L. Responsible AI / fairness / governance

| # | Prof | Class | Action | Artifact | New run? | Risk |
|---|---|---|---|---|---|---|
| 138 | High | 1 | "reported demand" used throughout | — | no | Low |
| 139 | High | 3 | Add "bias varies by complaint type, not only neighborhood" | `responsible.tex` | no | Low |
| 140 | High | 2 | Per-family unserved table (= #22) — the section claims it | new table | no | High |
| 141 | Med | 1→3 | Human-oversight paragraph present; strengthen | `responsible.tex` | no | Low |
| 142 | Med | 1 | Citywide scope boundary stated | — | no | Low |
| 143 | High | 1 | Weights = value judgment, stated | — | no | Low |
| 144 | High | 1 | "not automated deployment" stated | — | no | Low |
| 145 | Low | 3 | Add privacy-acknowledgement sentence | `responsible.tex` | no | Low |

## M. Reproducibility and artifact

| # | Prof | Class | Action | Artifact | New run? | Risk |
|---|---|---|---|---|---|---|
| 146 | Crit | 1 | Public-release repo exists | — | no | Low |
| 147 | Med | 1 | Self-contained artifact | — | no | Low |
| 148 | Crit | 2 | Fresh `make all` reproduction — **verifying now** | pipeline | **yes** | Crit |
| 149 | High | 1→3 | `requirements.txt`+pip-freeze; add exact versions | `s_compute.tex` | no | Low |
| 150 | Med | 1 | Raw is aggregated/small; scripts+manifests | — | no | Low |
| 151 | High | 1 | Manifests + `_provenance.json` checksums | — | no | Low |
| 152 | High | 2 | Guard-suite table (16 guards) | new table | no | Med |
| 153 | Low | 4 | Briefly explain forbidden-term scan neutrally | supplement | no | Low |
| 154 | High | 1 | Provenance hashes bind tables/figures | — | no | Low |
| 155 | Med | 3/4 | Data dictionary (from `feature_registry.json`) | supplement | no | Low |
| 156 | Med | 1 | `make all` documented | — | no | Low |
| 157 | Med | 1 | Centralized seed 20260609 (`set_seed`) | — | no | Low |
| 158 | High | 1→3 | Test-perturbation guards (G1/G2) — explain in guard table | supplement | no | Low |

## N. Related work

| # | Prof | Class | Action | Artifact | New run? | Risk |
|---|---|---|---|---|---|---|
| 159 | High | 3/5 | Expand synthesis within page budget; rest journal | `related.tex` | no | Med |
| 160 | High | 7 | Targeted multi-city-311 literature search (author confirms) | `related.tex` | no | Med |
| 161 | High | 5 | Public-sector allocation literature → journal | — | no | Low |
| 162 | Med | 5 | OR forecast-to-decision literature → journal | — | no | Low |
| 163 | Med | 5 | Calibration-for-optimization literature → journal | — | no | Low |
| 164 | Med | 5 | Urban transfer-learning literature → journal | — | no | Low |
| 165 | Crit | 2 | Bound all novelty claims ("we are not aware of…") | `related.tex`,`introduction.tex` | no | Crit |
| 166 | High | 7 | Position vs prior single-city Paper 1 — needs author | `related.tex` | no | High |
| 167 | High | 7 | Confirm no reused text from Paper 1 — needs author | — | no | High |

## O. Writing and claim control

| # | Prof | Class | Action | Artifact | New run? | Risk |
|---|---|---|---|---|---|---|
| 168 | Crit | 2 | "disable" → "non-identifies allocation among tied optima" (gated by #9) | `abstract.tex`,`results_decision.tex` | no | Crit |
| 169 | Med | 2/3 | "restores gradient" → "restores a non-flat marginal-value profile under the quantile-interpolated distribution" | `results_decision.tex` | no | Low |
| 170 | Med | 2 | "safe check" → "low-cost diagnostic" | `results_decision.tex` | no | Low |
| 171 | Med | 2 | "never harming" → "did not harm in the tested city-regime grid" | `results_decision.tex` | no | Low |
| 172 | High | 1→2 | "competitive" quantified by `tab8`; ensure all 12 visible | tables | no | Med |
| 173 | High | 2 | "general failure mode" → "generalizable *mechanism* under degenerate forecasts" | `abstract.tex` | no | Med |
| 174 | High | 1 | Repo justifies "benchmark" | — | no | Low |
| 175 | Med | 2 | "transfers to decision value" → "is associated with lower simulated loss within fixed policies" | `abstract.tex`,`results_decision.tex` | no | Low |
| 176 | Low | 3 | "City agencies use…" → "Short-horizon forecasts are a natural planning input" | `abstract.tex` | no | Low |
| 177 | Med | 1→2 | "planning capacity" → "simulated capacity" sweep | sections | no | Low |
| 178 | Low | 1 | Service-pressure regimes defined mathematically | — | no | Low |

## P. Tables and figures needed

| # | Prof | Class | Status / action | New run? |
|---|---|---|---|---|
| 179 | High | 2 | Dataset audit table — **new** | no |
| 180 | High | 2 | Split-date table — **new** | no |
| 181 | Crit | 1 | Harmonization table — exists | no |
| 182 | High | 2 | Model-config table — verify/extend `s_models` | no |
| 183 | High | 1 | Forecasting result table — `tab1`/`tab2` | no |
| 184 | High | 2 | Weather marginal-value table — **new** | no |
| 185 | High | 1→3 | Pooled/transfer table — `tab9`/new | no |
| 186 | High | 2 | Quantile calibration table — extend `tab5` (+width,+conformal) | yes |
| 187 | Crit | 1 | Decision policy table — `tab3` | no |
| 188 | Crit | 2 | Tie-break sensitivity table — **new** | yes |
| 189 | Crit | 2 | Calibrated-uncertainty decision table — **new** | yes |
| 190 | High | 2 | Horizon sensitivity table — **new** | yes |
| 191 | High | 2 | Per-family unserved table — **new** (data exists) | no |
| 192 | Med | 2 | Guard-suite table — **new** | no |

## Q. Supplement structure

| # | Prof | Class | Action |
|---|---|---|---|
| 193 | High | 2 | Keep decision/harmonization/calibration/tie-break evidence in main where it bears the claim |
| 194 | Med | 1 | Exhaustive grids already in `tab2`/supplement |
| 195 | Med | 1 | Worked optimizer examples already in `s_optimality.tex` |
| 196 | Med | 1 | Sensitivities in `s_sensitivity.tex` |
| 197 | High | 1 | Mapping rules in `s_harmonization.tex` |

## R. IEEE BigData-specific risk

| # | Prof | Class | Action |
|---|---|---|---|
| 198 | High | 2 | Emphasize benchmark/veracity/value/public-data framing |
| 199 | Med | 1→2 | Sell as benchmark + protocol + decision study, not algorithm |
| 200 | High | 2 | State plainly: raw acquisition large, modeling panel intentionally interpretable |
| 201 | Med | 2 | Connect to 5Vs (Volume/Variety/Value/Veracity; Velocity weak) |
| 202 | Med | 2 | Name the responsible-dataset-development angle in intro/conclusion |

---

## Counts

- Already satisfied (1): ~70 items
- Must fix before BigData (2): ~55 items
- Should fix if feasible (3): ~45 items
- Supplement (4): ~8
- Journal-extension (5): ~12
- Reject (6): 4 (#18 DP-oracle, #68 GAM, #74 deep model, partial #19)
- Author decision (7): 6 (#5 title, #20 weights, #108 mapping audit, #160/#166/#167 Paper-1 positioning)

## New experiments required (the whole experimental program)

1. **Tie-break sensitivity** (#9,11,12,13,15,16,188) — claim-gating (STOP #1)
2. **Log/normalized global pooling + normalized transfer** (#75,76,77,79) — claim-gating (STOP #3)
3. **Split-conformal calibration + calibrated decision** (#82,83,92,189) — claim-gating (STOP #2)
4. **Horizon-length cuts** (#48,49,190) — cheap re-slice
5. **Poisson GLM baseline** (#65,66)
6. **κ sweep / fractional capacity** (#24,27,28) and **initial-backlog/warm-up** (#30,50) and **abandonment grid** (#32,33)
7. **Per-family coverage / interval width / crossing freq / tail sensitivity** (#85,86,89,90)
8. Table-only (no new model fit): per-family unserved (#22/191), dataset audit (#179), split dates (#180), weather marginal (#56/184), guard table (#192), pooled/transfer (#185), normalized MAE (#135), weather missingness (#59).

The three claim-gating experiments are run first; any reversal triggers the
corresponding stop condition and a pause for author decision.
