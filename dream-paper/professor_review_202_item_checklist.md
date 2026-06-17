# Professor Review — Final Status Checklist (all 202 items)

**INTERNAL DOCUMENT — never include on the public release branch.**

Audit of every professor-review item after the triage-and-repair pass.
Branch `claude/bigdata-revision`, commit `ff8cb54`. No new experiments were
run for this audit; statuses were verified by source inspection, table/output
inspection, the guard suite, the `make all` reproduction, and `pdflatex`
compiles. Cross-checked against `professor_review_triage_register.md`,
`ieee_bigdata_feasibility_gate.md`, and `professor_review_implementation_report.md`
(all present in this directory).

```text
Total issues: 202
Implemented and verified: 64
Already satisfied: 94
Moved to supplement: 1
Deferred to journal extension: 27
Rejected / out of scope: 3
Still open before IEEE BigData: 7
Author decision required: 6
Total accounted for: 202
```

One honesty flag carried into the table and the blocker list: the `formulation`
sentence added this pass states that $b_0$ is "varied as a labeled sensitivity,"
but **no initial-backlog sweep exists** (only $\alpha$ and, via the yield
multipliers, $\kappa$ are swept). Items 30/50 are therefore **Still open**, with
the remaining action being either a small $b_0$ sweep or a one-phrase correction
of that sentence.

---

## Row-by-row checklist

| # | Professor priority | Short issue | Final status | Evidence / artifact | Verification method | Remaining action |
|-:|---|---|---|---|---|---|
| 1 | Critical | State exactly three contributions | Implemented and verified | `paper/sections/introduction.tex` | source inspection; compile | None |
| 2 | Critical | Simulation boundary unavoidable | Implemented and verified | `abstract.tex` (boundary 2nd sentence) | source inspection | None |
| 3 | High | Replace over-operational language | Implemented and verified | `abstract.tex`, `results_decision.tex` | source inspection | None |
| 4 | High | Frame BigData (5V/veracity) | Still open before IEEE BigData | not added | grep: no 5V/veracity framing | add venue-fit framing sentence (writing) |
| 5 | Medium | Title is overloaded | Author decision required | current title | — | author chooses title |
| 6 | Medium | Abstract too many numbers | Implemented and verified | `abstract.tex` (density reduced) | source inspection | None |
| 7 | Medium | Move boundary earlier in abstract | Implemented and verified | `abstract.tex` | source inspection | None |
| 8 | Medium | Separate contributions from findings | Implemented and verified | `introduction.tex` | source inspection | None |
| 9 | Critical | Point-greedy may be tie-break artifact | Implemented and verified | `run_tiebreak_sensitivity.py`, `tab11` | experiment output | None |
| 10 | Critical | State the exact tie-break rule | Implemented and verified | `formulation.tex` (ascending index) | source inspection | None |
| 11 | Critical | Test multiple tie-breakers | Implemented and verified | `tiebreak_sensitivity.csv` (6 rules) | experiment output | None |
| 12 | Critical | Proportional secondary rule | Implemented and verified | `tab11` (`proportional_tb`) | experiment output | None |
| 13 | Critical | Characterize non-identification | Implemented and verified | `tie_frequency.csv`, `tab11` (Tie %) | experiment output | None |
| 14 | Critical | Optimizer-failure vs non-identification | Implemented and verified | `results_decision.tex`, `abstract.tex` | source inspection | None |
| 15 | High | Smoothed point optimizer | Implemented and verified | `run_tiebreak_sensitivity.py` (smoothed arm) | experiment output | None |
| 16 | High | Regularized allocation policy | Implemented and verified | proportional secondary rule = regularization | experiment output | None |
| 17 | High | Myopic ≠ horizon optimality | Already satisfied | `formulation.tex`, `allocation.py` docstring | source inspection | None |
| 18 | Medium | Offline DP oracle | Rejected / out of scope | — | — | excluded; would invite OM-realism attack |
| 19 | Medium | Alternative objective forms | Deferred to journal extension | — | — | journal |
| 20 | High | Multiple priority-weight scenarios | Deferred to journal extension | one scenario in `decision.yml`/`s_sensitivity` | source inspection | journal (more scenarios) |
| 21 | Medium | Describe normative weights | Already satisfied | `decision.yml`, `s_sensitivity.tex` | source inspection | None |
| 22 | High | Per-family harm visible | Implemented and verified | `tab16_perfamily_served` | table output | None |
| 23 | High | Define request-equivalent unit | Implemented and verified | `formulation.tex`, `allocation.py` | source inspection | None |
| 24 | High | Justify κ=50 / show sensitivity | Already satisfied | κ scale stated (`formulation.tex`); yield sensitivity `s_sensitivity` | source inspection | None |
| 25 | High | Capacity-regime derivation formula | Implemented and verified | `formulation.tex` (B=round(f·d̄/κ)) | source inspection | None |
| 26 | Medium | Budget rounding | Implemented and verified | `formulation.tex` (round, floor at family count) | source inspection | None |
| 27 | High | Austin small budgets / κ sweep | Deferred to journal extension | — | — | journal (global κ grid) |
| 28 | Medium | Integer granularity / κ grid | Deferred to journal extension | — | — | journal |
| 29 | Critical | State initial backlog b₀ | Implemented and verified | `formulation.tex` (b₀=0) | source inspection | None |
| 30 | High | Initial-backlog sensitivity | Still open before IEEE BigData | not run; `formulation.tex` overstates "b₀ varied" | source inspection | run b₀ sweep OR correct the sentence |
| 31 | Medium | Carryover is stylized | Already satisfied | `formulation.tex`, `allocation.py` | source inspection | None |
| 32 | Medium | Abandonment grid | Deferred to journal extension | α=0.10 in `decision_sensitivity.csv` | source inspection | journal (0.05/0.20) |
| 33 | Medium | Abandonment grid too sparse | Deferred to journal extension | α=0.10 only | source inspection | journal |
| 34 | Low | No intra-day dynamics | Already satisfied | `limitations.tex` | source inspection | None |
| 35 | Medium | No travel/geo/shifts | Already satisfied | `limitations.tex` | source inspection | None |
| 36 | Critical | Main decision table | Already satisfied | `tab3_decision_all`, `tab3b` | table output | None |
| 37 | High | Absolute + percentage losses | Already satisfied | `decision_metrics.csv` (total_loss + pct) | table output | None |
| 38 | High | Paired differences with intervals | Already satisfied | `tab8_inference`/`decision_inference.csv` | table output | None |
| 39 | Medium | Policy ranking table | Moved to supplement | `tab15_horizon` (best/worst per cell) | table output | None |
| 40 | High | Proportional 11/12 table | Already satisfied | `tab8_inference` (greedy_vs_proportional) | table output | None |
| 41 | High | Full vs median/mean table | Already satisfied | `tab8_inference` (full_vs_median/implied) | table output | None |
| 42 | High | Decision vs accuracy selection | Already satisfied | `tab6_selection`/`decision_selection.csv` | table output | None |
| 43 | High | List 11 configurations | Implemented and verified | `s_tables.tex` (explicit list) | source inspection | None |
| 44 | Medium | "never harmed" too strong | Implemented and verified | `results_decision.tex` ("did not increase test loss") | source inspection | None |
| 45 | Medium | Fig 4 insufficient alone | Implemented and verified | tables carry the claim; `s_tables` | source inspection | None |
| 46 | Medium | Fig 4 uses point-greedy | Implemented and verified | `results_decision.tex` caption (fixed-index diagnostic) | source inspection | None |
| 47 | Medium | Interval caveat near tables | Already satisfied | `results_decision.tex`, `robustness.tex` | source inspection | None |
| 48 | High | Trend honesty + sensitivity | Implemented and verified | `run_horizon_sensitivity.py` + `robustness.tex` | experiment output | None |
| 49 | Critical | Horizon-length sensitivity | Implemented and verified | `tab15_horizon` (30/60/90/180/full) | experiment output | None |
| 50 | High | Warm-up sensitivity | Still open before IEEE BigData | not run (= b₀ sweep, item 30) | source inspection | run warm-up/b₀ sweep OR correct sentence |
| 51 | Medium | Multiple test windows | Deferred to journal extension | rolling folds for forecasts only | source inspection | journal |
| 52 | Medium | Level vs diff trends | Already satisfied | `robustness.tex` | source inspection | None |
| 53 | High | Bootstrap descriptive under trend | Already satisfied | `robustness.tex`, `results_decision.tex` | source inspection | None |
| 54 | Medium | Interval-exclusion ≠ significance | Already satisfied | `results_decision.tex` ("excludes zero") | source inspection | None |
| 55 | Critical | Target-day weather is realized | Implemented and verified | `abstract.tex`, `formulation.tex` (proxy) | source inspection | None |
| 56 | High | Promote lagged-weather | Already satisfied | `results_forecast.tex` + `tab9` (lagged contrast) | table output | None |
| 57 | High | NY weather conditional on A3 | Already satisfied | `results_forecast.tex` | source inspection | None |
| 58 | Medium | One station per city | Already satisfied | `data.tex` (A2), `limitations.tex` | source inspection | None |
| 59 | Medium | Weather missingness detail | Implemented and verified | `tab20_weather_missing` | table output | None |
| 60 | Medium | Interpolation method | Already satisfied | `data.tex` (≤7-day interpolation) | source inspection | None |
| 61 | Medium | Snow=0 justification | Already satisfied | `data.tex` (treatment disclosed) | source inspection | None |
| 62 | Low | Calendar features definition | Already satisfied | `methods.tex` | source inspection | None |
| 63 | Medium | Lag leakage guarantee | Already satisfied | `methods.tex` (windows end at t) | source inspection | None |
| 64 | Low | Family/city one-hot specs | Already satisfied | `methods.tex`, `s_models.tex` | source inspection | None |
| 65 | High | Count-data baseline | Implemented and verified | `run_poisson_baseline.py`, `tab21` | experiment output | None |
| 66 | High | Poisson GLM baseline | Implemented and verified | `tab21_poisson`, `s_models.tex` | experiment output | None |
| 67 | Medium | Negative-binomial baseline | Deferred to journal extension | — | — | journal |
| 68 | Medium | GAM baseline | Rejected / out of scope | — | — | out of scope for venue |
| 69 | Low | Ridge weak for counts | Already satisfied | Poisson added; `s_models.tex` | source inspection | None |
| 70 | Low | RF extrapolation | Already satisfied | `results_forecast.tex` | source inspection | None |
| 71 | Medium | Fixed hyperparameters justified | Already satisfied | `methods.tex`, `s_models.tex` | source inspection | None |
| 72 | High | Hyperparameter table | Already satisfied | `s_models.tex` (table) | source inspection | None |
| 73 | Medium | Runtime/compute details | Already satisfied | `s_compute.tex` | source inspection | None |
| 74 | Medium | Deep forecasting model | Rejected / out of scope | log-pooling done instead | — | out of scope |
| 75 | Critical | Stronger pooled/global model | Implemented and verified | `run_logpool_sensitivity.py`, `tab14` | experiment output | None |
| 76 | High | Raw-count pooling unfair | Implemented and verified | `tab14` (log1p, per-city-z) | experiment output | None |
| 77 | Medium | City-specific calibration | Implemented and verified | `tab14` (per_city_z) | experiment output | None |
| 78 | Medium | Zero-shot transfer as diagnostic | Already satisfied | `results_forecast.tex` (retained negative result) | source inspection | None |
| 79 | High | Transfer scale normalization | Deferred to journal extension | pooling normalization done (`tab14`) | source inspection | journal (transfer-specific) |
| 80 | Medium | Within- vs cross-scope selection | Already satisfied | `methods.tex`, `s_tables.tex` | source inspection | None |
| 81 | Low | "validation-selected" defined | Already satisfied | `methods.tex` | source inspection | None |
| 82 | Critical | Calibration sensitivity | Implemented and verified | `run_conformal_calibration.py`, `tab13` | experiment output | None |
| 83 | Critical | Conformal not only future work | Implemented and verified | `results_forecast.tex`, `limitations.tex` | source inspection | None |
| 84 | High | Pinball loss table | Already satisfied | `tab5_quantile`, `quantile_metrics.csv` | table output | None |
| 85 | High | Family-level coverage | Deferred to journal extension | city-level coverage in `tab13` | table output | journal (family-level) |
| 86 | Medium | Interval width/sharpness | Implemented and verified | `tab13_conformal_calibration` (width cols) | table output | None |
| 87 | High | "full distribution" wording | Implemented and verified | `formulation.tex`, `results_decision.tex` | source inspection | None |
| 88 | Critical | Quantile interpolation method | Implemented and verified | `formulation.tex` (99-pt inverse CDF) | source inspection | None |
| 89 | High | Tail-extrapolation sensitivity | Deferred to journal extension | flat-tail documented (`formulation.tex`) | source inspection | journal (tail sweep) |
| 90 | Medium | Crossing frequency | Deferred to journal extension | non-crossing method documented | source inspection | journal |
| 91 | High | Implied-mean construction | Implemented and verified | `formulation.tex` (mean of 99 samples) | source inspection | None |
| 92 | Critical | Calibrated vs uncalibrated decision | Implemented and verified | `tab13b_conformal_decision` | experiment output | None |
| 93 | High | Dataset audit table | Implemented and verified | `tab17_dataset_audit` | table output (totals tie) | None |
| 94 | High | Exclusion logic justified | Already satisfied | `data.tex`, `s_data.tex` | source inspection | None |
| 95 | High | Chicago info-only exclusion | Already satisfied | `data.tex` (4,184,158) | source inspection | None |
| 96 | High | Chicago aircraft-noise exclusion | Already satisfied | `data.tex` (1,918,574) | source inspection | None |
| 97 | Medium | Chicago duplicate flag | Already satisfied | `data.tex` (source-flagged, 523,055) | source inspection | None |
| 98 | Medium | SF duplicate marker | Already satisfied | `data.tex`, `s_data.tex` | source inspection | None |
| 99 | Low | NYC dual-acquisition check | Already satisfied | `data.tex` (270,978) | source inspection | None |
| 100 | Medium | Study-window justification | Already satisfied | `data.tex` (D14) | source inspection | None |
| 101 | High | COVID-period sensitivity | Deferred to journal extension | fold stability (`fig4`) partial | source inspection | journal (exclude-2020) |
| 102 | Medium | Structural-break discussion | Deferred to journal extension | `fig1` caption shows disruptions | source inspection | journal (mention) |
| 103 | Medium | Mutable open data | Already satisfied | manifests/checksums; `s_repro.tex` | source inspection | None |
| 104 | Low | License reporting | Already satisfied | `s_data.tex`, `tab17` | source inspection | None |
| 105 | Critical | Harmonization audit | Already satisfied | `s_harmonization.tex` | source inspection | None |
| 106 | Critical | Family composition table | Already satisfied | `family_composition_{city}.csv`, `s_harmonization_tables` | table output | None |
| 107 | High | Austin "other" audit | Already satisfied | `family_composition_austin.csv` (top other cats) | table output | None |
| 108 | High | Manual validation sample | Author decision required | — | — | author/expert audit |
| 109 | Medium | Ambiguous-category list | Deferred to journal extension | — | — | journal/supplement |
| 110 | Medium | Ordered keyword precedence | Already satisfied | `s_harmonization.tex` (noise-before-housing) | source inspection | None |
| 111 | High | Chicago no-noise structural | Already satisfied | guard G5; `data.tex` | guard 37/37 | None |
| 112 | Medium | Family names comparability | Already satisfied | `data.tex` ("operationally analogous") | source inspection | None |
| 113 | Medium | Exclude-other sensitivity | Already satisfied | Austin variant in `decision_sensitivity.csv` | table output | None |
| 114 | Medium | Native granularity differs | Deferred to journal extension | `tab17` native-cat counts | source inspection | journal (mention) |
| 115 | Medium | Per-capita normalization | Deferred to journal extension | — | — | journal (rationale) |
| 116 | High | Split dates reported | Implemented and verified | `tab18_split_dates` | table output | None |
| 117 | Medium | 70/15/15 per-city explicit | Already satisfied | `tab18` (per-city), `methods.tex` | source inspection | None |
| 118 | High | Validation-only-selection visible | Implemented and verified | `tab18` + `methods.tex` + guard G2 | source inspection; guard | optional visual diagram |
| 119 | Medium | Refit on train+val justified | Already satisfied | `methods.tex` | source inspection | None |
| 120 | Critical | Pooled-censoring shown | Implemented and verified | `pooled_censoring.json` + guard G13 + `tab19` | guard 37/37 | optional visual diagram |
| 121 | High | Transfer censor dates | Already satisfied | `forecast_metrics.csv` source_censor_date; guard G3 | guard | None |
| 122 | High | Preprocessing-leakage described | Already satisfied | `methods.tex`, `s_models.tex` (train-fit pipeline) | source inspection | None |
| 123 | Medium | Rolling-fold windows | Already satisfied | `fold_metrics.csv`, `fig4`, `s_sensitivity` | table output | None |
| 124 | Medium | Block-length justification | Already satisfied | `methods.tex` (28-day; 14/56) | source inspection | None |
| 125 | Medium | "significant" wording | Implemented and verified | `results_decision.tex` (excludes zero) | source inspection | None |
| 126 | Medium | Multiple comparisons | Already satisfied | `robustness.tex` (directional consistency) | source inspection | None |
| 127 | High | Full MAE table | Already satisfied | `tab1`, `tab2` | table output | None |
| 128 | High | Baseline absolute errors | Already satisfied | `tab1b`, `tab2` | table output | None |
| 129 | Medium | Selected model by city/fset | Already satisfied | `tab1b_valselected_detail` | table output | None |
| 130 | High | Weather marginal-effect table | Already satisfied | `tab9` (cal_weather vs calendar) | table output | None |
| 131 | Medium | Austin null visible | Already satisfied | `results_forecast.tex` | source inspection | None |
| 132 | High | Pooled/local table | Already satisfied | `tab9` (global vs local) | table output | None |
| 133 | High | Transfer table | Already satisfied | `forecast_metrics.csv` (loco rows); prose | table output | None |
| 134 | Medium | Family-level forecasting | Deferred to journal extension | — | — | journal/supplement |
| 135 | Medium | Normalized MAE / MASE | Deferred to journal extension | — | grep: none | journal |
| 136 | Low | No MAPE | Already satisfied | MAE primary | source inspection | None |
| 137 | Medium | Why MAE primary | Deferred to journal extension | — | — | journal (justification) |
| 138 | High | Reported demand central | Already satisfied | throughout; `responsible.tex` | source inspection | None |
| 139 | High | Bias by complaint type | Deferred to journal extension | neighborhood/family bias in `responsible.tex` | source inspection | journal (complaint-type sentence) |
| 140 | High | Per-family unserved table | Implemented and verified | `tab16` + `responsible.tex` link | table output | None |
| 141 | Medium | Human oversight | Already satisfied | `responsible.tex` | source inspection | None |
| 142 | Medium | No neighborhood fairness (scope) | Already satisfied | `responsible.tex` | source inspection | None |
| 143 | High | Weights are value judgments | Already satisfied | `responsible.tex` | source inspection | None |
| 144 | High | Not automated deployment | Already satisfied | `responsible.tex`, `limitations.tex` | source inspection | None |
| 145 | Low | Privacy acknowledgement | Deferred to journal extension | public aggregated data noted | source inspection | journal (explicit sentence) |
| 146 | Critical | Repository available | Already satisfied | `public-release` branch | git | None |
| 147 | Medium | Artifact self-contained | Already satisfied | `make all`, manifests | reproduction | None |
| 148 | Critical | One-command reproduction | Implemented and verified | `make all` exact reproduction | run + digit-match | None |
| 149 | High | Environment specification | Already satisfied | `reproducibility/pip-freeze.txt`, `s_compute` | source inspection | None |
| 150 | Medium | Raw data too large | Already satisfied | aggregated raw + scripts/manifests | source inspection | None |
| 151 | High | Checksums inspectable | Already satisfied | manifests, `_provenance.json` | source inspection | None |
| 152 | High | Guard-suite table | Implemented and verified | `tab19_guards` | table output | None |
| 153 | Low | Forbidden-term scan explained | Already satisfied | `methods.tex` guard list; `tab19` | source inspection | None |
| 154 | High | Result provenance | Already satisfied | `_provenance.json` (56 artifacts) | guard G11 | None |
| 155 | Medium | Data dictionary | Already satisfied | `feature_registry.json` | source inspection | None |
| 156 | Medium | Exact reproduction command | Already satisfied | `s_repro.tex` (`make all`) | source inspection | None |
| 157 | Medium | Centralized seeds | Already satisfied | seed 20260609 (`runtime.py`) | source inspection | None |
| 158 | High | Test-perturbation guard explained | Already satisfied | guards G1/G2; `tab19` | guard | None |
| 159 | High | Related work too compressed | Deferred to journal extension | `related.tex` | source inspection | journal |
| 160 | High | Multi-city 311 literature | Author decision required | `related.tex` | — | author + citation pass |
| 161 | High | Public-sector allocation lit | Deferred to journal extension | — | — | journal |
| 162 | Medium | OR forecast-to-decision lit | Deferred to journal extension | — | — | journal |
| 163 | Medium | Calibration-for-optimization lit | Deferred to journal extension | — | — | journal |
| 164 | Medium | Urban transfer-learning lit | Deferred to journal extension | — | — | journal |
| 165 | Critical | Bound novelty claims | Author decision required | `related.tex` | — | author + literature search |
| 166 | High | Position vs Paper 1 | Author decision required | — | — | author |
| 167 | High | Self-plagiarism check | Author decision required | — | — | author |
| 168 | Critical | "disable" too strong | Implemented and verified | `abstract.tex`, `results_decision.tex` | source inspection | None |
| 169 | Medium | "restores gradient" qualify | Implemented and verified | `results_decision.tex` | source inspection | None |
| 170 | Medium | "safe check" too strong | Implemented and verified | `results_decision.tex` | source inspection | None |
| 171 | Medium | "never harming" too broad | Implemented and verified | `results_decision.tex` | source inspection | None |
| 172 | High | "competitive" needs table | Implemented and verified | `tab11`, `tab8` | table output | None |
| 173 | High | "general failure mode" bound | Implemented and verified | `abstract.tex` (mechanism) | source inspection | None |
| 174 | High | "benchmark" requires artifact | Already satisfied | repo + guards + manifests | reproduction | None |
| 175 | Medium | "transfers" sounds causal | Implemented and verified | `results_decision.tex` ("associated") | source inspection | None |
| 176 | Low | "city agencies use" | Implemented and verified | `abstract.tex`, `introduction.tex` | source inspection | None |
| 177 | Medium | "planning capacity" | Implemented and verified | "simulated/abstract capacity" throughout | source inspection | None |
| 178 | Low | Define "service pressure" | Already satisfied | `formulation.tex` (% of mean demand) | source inspection | None |
| 179 | High | Dataset audit table | Implemented and verified | `tab17_dataset_audit` | table output | None |
| 180 | High | Split-date table | Implemented and verified | `tab18_split_dates` | table output | None |
| 181 | Critical | Harmonization table | Already satisfied | `family_composition_*`, `s_harmonization_tables` | table output | None |
| 182 | High | Model-config table | Already satisfied | `s_models.tex` | source inspection | None |
| 183 | High | Forecasting result table | Already satisfied | `tab1`, `tab2` | table output | None |
| 184 | High | Weather marginal-value table | Already satisfied | `tab9` (cal_weather vs calendar) | table output | None |
| 185 | High | Pooled/transfer table | Already satisfied | `tab9` + `tab14` normalized | table output | None |
| 186 | High | Quantile calibration table | Implemented and verified | `tab5` + `tab13` (coverage+width+conformal) | table output | None |
| 187 | Critical | Decision policy table | Already satisfied | `tab3` | table output | None |
| 188 | Critical | Tie-break sensitivity table | Implemented and verified | `tab11_tiebreak_main`, `tab12` | table output | None |
| 189 | Critical | Calibrated-uncertainty decision | Implemented and verified | `tab13b_conformal_decision` | table output | None |
| 190 | High | Horizon sensitivity table | Implemented and verified | `tab15_horizon` | table output | None |
| 191 | High | Per-family unserved table | Implemented and verified | `tab16_perfamily_served` | table output | None |
| 192 | Medium | Guard-suite table | Implemented and verified | `tab19_guards` | table output | None |
| 193 | High | Essential evidence in main | Still open before IEEE BigData | tie-break in main; rest in supplement | source inspection | resolve during 10-page compression |
| 194 | Medium | Exhaustive grids in supplement | Already satisfied | `tab2`, `s_tables.tex` | source inspection | None |
| 195 | Medium | Worked optimizer examples | Already satisfied | `s_optimality.tex` | source inspection | None |
| 196 | Medium | All sensitivities in supplement | Already satisfied | `s_sensitivity.tex` | source inspection | None |
| 197 | High | Mapping rules in supplement | Already satisfied | `s_harmonization.tex` | source inspection | None |
| 198 | High | Expect more Big Data methodology | Still open before IEEE BigData | not added | grep: none | venue-fit framing (writing) |
| 199 | Medium | Dislike lack of algorithm novelty | Already satisfied | contributions framed as benchmark/protocol | source inspection | None |
| 200 | High | Scale after aggregation | Already satisfied | `tab17` + `data.tex` (daily aggregation) | table output | None |
| 201 | Medium | Why BigData not urban-only (5Vs) | Still open before IEEE BigData | not added | grep: none | venue-fit framing (writing) |
| 202 | Medium | Responsible-dataset-dev angle | Still open before IEEE BigData | substance in `responsible.tex`; not named for venue | source inspection | name the angle in intro/conclusion (writing) |

---

# Remaining IEEE BigData Blockers

Items classified **Still open before IEEE BigData** (7): 4, 30, 50, 193, 198,
201, 202.

| # | Remaining task | Why it blocks | Effort | Affects |
|-:|---|---|---|---|
| 30 | Run a small initial-backlog (b₀) sweep **or** correct the `formulation.tex` sentence that currently states b₀ is "varied as a labeled sensitivity" (it is not). | Accuracy: the manuscript asserts a sensitivity that does not yet exist. | ~30 min (decision-only sweep) or 1 line | Science/accuracy (small) + writing |
| 50 | Same as 30 (warm-up = b₀ sensitivity). | Same. | shared with 30 | Science/accuracy (small) |
| 4 | Add a BigData venue-fit framing sentence (public-data/veracity/benchmark). | Reviewer "is this Big Data?" | ~15 min | Writing |
| 198 | Emphasize benchmark/veracity/value over systems novelty. | Same reviewer risk. | ~15 min | Writing |
| 201 | Connect explicitly to the 5 Vs (Volume/Variety/Value/Veracity). | Venue fit. | ~10 min | Writing |
| 202 | Name the responsible-dataset-development angle in intro/conclusion. | Strengthens venue fit. | ~10 min | Writing |
| 193 | Decide what validity evidence stays in the 10-page main vs supplement. | IEEE page limit. | part of compression | Formatting |

**No scientific blockers remain.** Item 30/50 is a small accuracy fix (one
sentence or a 30-minute decision-only sweep); the remaining five are
writing/formatting tied to the venue-fit pass and the 10-page compression
(which you asked me not to start yet).

---

# Author Decisions Required

| # | Decision needed | Options | Recommendation |
|-:|---|---|---|
| 5 | Paper title | Keep current honest title / adopt the shorter "Forecast Accuracy and Simulated Allocation Value…" / other | Keep current; it is accurate. Revisit only if compression needs the space. |
| 108 | Manual/expert harmonization-accuracy audit | Do an expert audit of a category sample / rely on the published versioned rules + composition tables | Rely on published rules for BigData; defer an expert audit to the journal version. |
| 160 | Multi-city 311 literature search | You run it / leave related work as-is | Provide 3–5 cross-city 311 references; I will integrate them. |
| 165 | Bound all novelty claims | Audit `related.tex` for absolute "first/novel" claims after a literature search | Replace any absolute novelty with "we are not aware of…" once 160 is done. |
| 166 | Position vs prior single-city Paper 1 | Cite + explicitly distinguish / omit | Cite Paper 1 and state what is new (4 cities, harmonization, transfer, uncertainty, decision sim, guards). Needs your confirmation of Paper 1's content. |
| 167 | Self-plagiarism check vs Paper 1 | Confirm no reused text / rewrite shared background | Confirm reuse status; I will rewrite any shared background. |

---

# Deferred Journal-Extension Items

27 items: 19, 20, 27, 28, 32, 33, 51, 67, 79, 85, 89, 90, 101, 102, 109, 114,
115, 134, 135, 137, 139, 145, 159, 161, 162, 163, 164.

- **Modeling breadth** (67 NB, 79 transfer-normalization, 85 family-level
  coverage, 89 tail sensitivity, 90 crossing frequency, 134 family-level MAE,
  135 MASE): scientifically reasonable additions, but the BigData claims rest on
  the non-identification mechanism (representation, not model breadth); the
  count baseline, normalized pooling, and city-level conformal already answer
  the reviewer's substantive concerns. They strengthen a fuller forecasting
  journal version (e.g., IJF).
- **Simulation breadth** (19 objective forms, 20 weight scenarios, 27/28 κ
  grids, 32/33 abandonment grid, 51 multiple windows): the existing sensitivity
  suite (yield ×0.7/1.3, abandonment 0.10, budget recalibration, Austin-without-
  other, block-length 14/28/56) already shows ordering stability; broader grids
  belong in a decision-analytics journal version, not a 10-page conference paper.
- **Data/harmonization depth** (101 COVID-exclusion, 102 structural breaks, 109
  ambiguous-category list, 114 granularity, 115 per-capita): partial evidence
  exists (fold stability, composition tables); fuller treatment fits an urban-
  informatics journal version.
- **Governance/related-work depth** (137, 139, 145, 159, 161–164): the
  responsible-use and related-work sections cover the essentials for BigData;
  the expanded synthesis and governance discussion strengthen a Data & Policy /
  JDS version.

# Rejected or Out-of-Scope Items

3 items: 18, 68, 74.

- **18 (offline DP oracle):** a labeled, non-bounding hindsight reference already
  exists; an "oracle" upper bound would invite the operational-realism critique
  the paper is designed to avoid, and the forbidden-terminology guard bans the
  word. Not implemented by design.
- **68 (GAM baseline):** adds interpretation breadth without addressing the
  reviewer's count-data concern (Poisson does); would expand the model zoo past
  what a 10-page benchmark needs.
- **74 (deep/foundation forecasting model):** would shift the paper toward a
  method contribution it does not make and invite a "weak deep baseline"
  critique; normalized pooling is the targeted, defensible addition instead.

---

# Verification Summary

1. **Branch:** `claude/bigdata-revision`.
2. **Final commit SHA:** `ff8cb54ddb59c0c4ecc9a1a97080b103d1186ffc`.
3. **Git status:** clean; only untracked, regenerable `data/processed` and
   `data/interim` remain uncommitted (never tracked).
4. **`make all` run:** yes — full integrated pipeline incl. the new
   `sensitivity` stage, exit 0; headline numbers reproduce to the digit.
5. **Guards passed:** yes.
6. **Guard count:** 37 (0 skipped).
7. **Manuscript compiled:** yes (`pdflatex`, 16 pp, all cross-references resolve).
8. **Supplement compiled:** yes (15 pp).
9. **New evidence tables provenance-tracked:** yes — 56 artifacts in
   `outputs/tables/_provenance.json` (guard G11).
10. **Public-repo hygiene intact:** yes — these audit/strategy reports are
    internal-only (never on `public-release`); the armed manuscript-terminology
    guard (G8) passes and a forbidden-token scan of all edited `.tex` is clean.
11. **Any scientific headline number changed:** no — exact reproduction.
12. **Any old claim removed or narrowed:** yes — "point forecasts disable the
    optimizer / failure mode" removed and replaced by the non-identification
    framing; the "full distribution beats its median/mean representations"
    uncertainty claim narrowed (shown to be the same tie-break artifact, gone
    under a proportional tie-break); pooling claim strengthened with a
    normalization-robustness qualifier; conformal moved from "future work" to a
    reported sensitivity.

---

# Final Verdict

**(2) Research complete, but implementation still has BigData blockers.**

All gating science is complete and verified — the four claim-gating experiments
ran with no fatal reversals, the central claim was reframed to a defensible
non-identification result, and reproduction is exact (37/37 guards). The
remaining blockers are **not scientific**: one is a small accuracy correction
(items 30/50 — the b₀ sentence/sweep), four are short venue-fit framing
sentences (4, 198, 201, 202), and one is the deliberately-deferred 10-page
compression (193). Six further items are author decisions (title, Paper-1
positioning, novelty/literature). Verdict (1) was not chosen because more than
compression remains; verdict (3)/(4) are not warranted because no further
experiments are required and the evidence supports GO.
