# arXiv / Workshop Structure Plan

Planning document for the next writing pass. It recommends how to structure the
submission built from the existing `paper/` package. It adds no new empirical
results, makes no new claims, and changes no other files. All empirical values
referenced here already exist in `paper/number_audit.md` and the committed
artifacts; they are repeated only as planning context, not as new findings.

Paper title (current): From Forecast Accuracy to Operational Value: Public Signal
Augmentation for NYC 311 Service Demand.

---

## 1. What kind of paper this is

Primary classification: an **arXiv applied-ML / operations-analytics technical
report**. Equally suitable, with light trimming, as a **workshop short paper /
extended abstract** (operations management, information systems, or applied
analytics / ML-for-operations workshops).

It is **not** a conference full paper or journal paper yet.

Justification, tied to the evidence already in the package:
- Strengths that support arXiv/workshop: real data end to end (NYC 311 2022-2024;
  NOAA Central Park weather), a leakage-controlled chronological protocol, a
  four-way feature-set comparison, five-fold rolling-origin validation,
  per-borough and per-complaint-group robustness, a transparent forecast-to-
  decision simulation with an oracle bound, a number audit, and a clean
  reproducibility story.
- Why not full paper (already recorded as `strong_enough_for_full_paper_drafting
  = false`): no formal forecast-difference test (e.g., Diebold-Mariano) with
  uncertainty intervals; the decision layer is a single stylized proportional
  heuristic; only one external signal (a single weather station); single city and
  window. These are method-depth gaps, not data-integrity gaps.

Net: the contribution is a careful, honest baseline plus a forecast-to-decision
framing. That is exactly what arXiv technical reports and applied workshops
reward; it is below the novelty/identification bar of a main conference track.

---

## 2. Best target structure

Keep the current `main.md` section order; it is already close to the standard
applied-ML empirical structure. The change for submission is **economy** (move
detail to the appendix) and **placement** of end-matter, not reordering.

### Recommended main-paper section order

1. **Title + Abstract** - state problem, data, the two questions (accuracy and
   decision), headline numbers, and the honest decision caveat.
2. **Introduction** - motivation, the accuracy-vs-decision gap, contributions
   list, explicit "this is a baseline / technical report" framing.
3. **Related Work** - short; the public-data-augmentation lineage and the
   forecast-vs-decision distinction. Keep it to one tight paragraph or two.
4. **Data** - NYC 311 aggregation to date x borough x complaint_group; NOAA
   single-station weather; provenance and the no-synthetic statement.
5. **Methods** - feature sets, models, chronological split, decision-simulation
   definition. Push exact feature lists to the appendix.
6. **Forecasting Results** - the model/feature-set comparison and the selected
   model's test metrics.
7. **Forecast-to-Decision Simulation** - baseline-budget result plus the
   budget-sensitivity sweep; the attenuated, budget-dependent transfer.
8. **Robustness (condensed)** - rolling-origin consistency + one sentence each on
   borough and complaint-group robustness; full tables to appendix.
9. **Limitations** - condensed; full table to appendix.
10. **Conclusion** - what is shown, what is not, and the path to a stronger paper.

End-matter (short, after Conclusion, before references): **Reproducibility
Statement**, **Data Availability Statement**, **Ethics Statement** - each 3-6
lines in the main body with pointers to the appendix/repo. These are expected by
arXiv/ML-workshop norms and should not be buried.

### Recommended appendix section order

A. Feature definitions and the four feature-set definitions (from
   `table_2_feature_sets.md` / `appendix.md`).
B. Complaint-group mapping summary.
C. Chronological split details and rolling-origin setup.
D. Decision-simulation assumptions (crews, per-crew capacity, weighting,
   largest-remainder allocation, oracle).
E. Crew-budget sensitivity setup and full table (`table_7`).
F. Weather-data treatment (single-station proxy; derived temp_avg; interpolated
   wind days).
G. Full per-segment robustness tables (`table_5`, `table_6`) and the full
   13-row model comparison (`table_3`).
H. Reproducibility commands and artifact list.

### What each section must accomplish (one line each)

- Abstract: make the accuracy-to-decision gap and the honest result legible in
  150-200 words.
- Intro: justify why a decision metric is evaluated, not just MAE.
- Related Work: locate the contribution in the public-signal-augmentation lineage
  without overclaiming novelty.
- Data: establish real-data integrity and the unit of analysis.
- Methods: make the protocol leakage-proof and reproducible on the page.
- Forecasting Results: show calendar dominates, weather adds a small consistent
  gain, best test MAE 55.325 (23.0% over naive).
- Decision Simulation: show direction-consistent but budget-dependent transfer.
- Robustness: show the forecast gain is not a one-split artifact.
- Limitations: pre-empt reviewer objections honestly.
- Conclusion: state the ceiling and the upgrade path.

---

## 3. Figure/table strategy

Target economy for a short paper / technical report: about **4-5 figures and 3
tables in the main body**, the rest appendix-only. The package has 10 figures and
8 tables, so most move to the appendix or are merged.

### Figures - main body (4-5)

- `figure_2_feature_set_comparison_mae.png` - cleanest single view of the
  central forecasting result (best MAE per feature set). **Main.**
- `figure_3_rolling_validation_mae.png` - shows stability across folds. **Main.**
- `figure_6_decision_sensitivity.png` - the budget-dependent decision result.
  **Main.**
- `figure_7_actual_vs_predicted.png` - one intuitive fit visual. **Main
  (optional, recommended).**
- `figure_9_decision_quality_comparison.png` - baseline-budget policy comparison
  with oracle. **Main OR appendix** (keep if space; it pairs with the decision
  section).

### Figures - appendix-only

- `figure_1_model_comparison_mae.png` (full 13-bar version; overlaps with
  Figure 2 - keep the detailed one in the appendix).
- `figure_4_borough_robustness_mae.png`, `figure_5_complaint_group_robustness_mae.png`
  (segment detail).
- `figure_8_weather_feature_summary.png` (data-provenance visual).

### Figures - omit/merge

- `figure_10_internal_vs_calendar_augmented_mae.png` is a subset of the model
  comparison; **omit** from the paper (or fold into Figure 1 in the appendix).
  Note that `forecast_error_by_model.png` was already excluded as an alias.

### Tables - main body (3)

- `table_3_model_comparison.md` - the core results table (can be trimmed to the
  best row per model + naive in main; full 13 rows to appendix).
- `table_7_decision_sensitivity.md` - the decision result across budgets.
- `table_1_dataset_summary.md` - compact data summary (or merge into the Data
  section prose if space is tight).

### Tables - appendix-only

- `table_2_feature_sets.md`, `table_4_rolling_validation.md`,
  `table_5_borough_robustness.md`, `table_6_complaint_group_robustness.md`,
  `table_8_limitations_and_mitigations.md`.

### What to omit

- The internal-vs-calendar figure (redundant with model comparison).
- The full 13-row model table in the main body (keep a trimmed version; full in
  appendix).
- Do not introduce any new figure or table; the package is complete.

---

## 4. Writing strategy

### Abstract should emphasize

The two-question framing (does public-signal augmentation improve next-day
forecasts; does it improve a downstream allocation), the headline forecasting
result (best test MAE 55.325, 23.0% over naive; calendar dominant, weather a
small consistent add), and the honest decision finding (direction-consistent but
budget-dependent). One clause stating it is a reproducible baseline / technical
report.

### Introduction should emphasize

Why average forecast error and operational value are not the same thing under a
scarce, prioritised allocation; that the paper evaluates the decision layer as a
first-class target; a short explicit contributions list; and the scoping
statement (baseline, no causal/production claims).

### Related Work should and should not claim

- Should: place the work in the public-data feature-augmentation lineage
  (`cui2018operational`, verified) and the general point that the objective on
  top of a predictive model shapes outcomes.
- Should not: claim novelty of method, claim equity/causal results, or lean on
  the unverified prioritization-disparity reference. **Resolve `samorani2022TODO`
  (verify full metadata) or drop the sentence and the entry** before submission;
  do not submit with a TODO citation key.

### How to frame the forecast-to-decision contribution

Frame the attenuated, budget-dependent transfer as **the finding**, not a
weakness: better forecasts help the allocation in every budget tested, but the
size of the benefit depends on capacity, and average accuracy gains overstate
operational value under scarcity. The oracle bound makes the ceiling explicit.
This honesty is the paper's distinctive value.

### How to frame limitations without self-defeating

State each limitation with its scope and a one-line reason it does not invalidate
the contribution (e.g., single-station weather is a documented proxy, not a
fabricated signal; the decision sim is stylized and labelled as such; reporting
bias means the target is reported volume, which the paper says plainly). Keep the
"what would make it stronger" items in the Conclusion so limitations read as a
roadmap, not a retreat.

---

## 5. Venue / arXiv positioning

- **Primary arXiv category: cs.LG** (machine learning; applied empirical
  forecasting with a decision-evaluation angle).
- **Reasonable cross-lists: stat.AP** (applied statistics / real-data forecasting)
  and **cs.CY** (computers and society; municipal/public-services data with a
  reporting-bias discussion). Optionally **stat.ML**.
- Reads as: **arXiv technical report now; workshop short paper now**; not a main
  conference track submission.
- To make it stronger later (conference/full paper): add a formal
  forecast-difference test with uncertainty intervals; replace the stylized
  allocation with a non-stylized, service-level-constrained decision model and an
  empirical realism check; add external signals beyond one weather station
  (multi-station/gridded, transit, events) or cross-city replication; expand
  related work.

---

## 6. Submission-risk checklist

### Overclaims to avoid

- No causal impact / causal identification; the study is correlational.
- No production readiness, deployment, or integration.
- No real dispatch or staffing optimization; the simulation is stylized.
- No external validity beyond NYC 2022-2024.
- Do not let the title phrase "Operational Value" imply realized operational
  value; the body must keep it framed as a stylized, budget-dependent simulation.
- Do not present the decision gain as large or guaranteed.

### Missing pieces to fix before submission

- Resolve or remove `samorani2022TODO` (no TODO citations in a submission).
- Confirm accessed dates / DOI-version for `nyc311` and `noaaghcnd`.
- Expand Related Work to the depth the chosen venue expects.
- Produce the final formatted draft and a PDF in the venue template (separate
  pass; not done here).
- Finalize main-vs-appendix figure/table numbering after the economy cuts.

### Formatting / source-hygiene risks (arXiv)

- Ensure figures are submission-grade (PNG is acceptable for arXiv; if moving to
  LaTeX, prefer vector/PDF where available and embed fonts).
- No absolute local paths in the compiled source; use relative paths.
- Include a complete `.bib`; ensure every in-text citation resolves and no TODO
  keys remain.
- If a workshop requires anonymization, strip the repository/owner identifier and
  any acknowledgements for the review copy.
- Keep the source package minimal (no large data, no model binaries); the repo
  already ignores those.

### Citation risks

- Exactly one fully verified reference (`cui2018operational`); two data sources
  with minor TODOs; one unverified paper. Do not add citations without
  verification; verify or cut.

### Figure/table risks

- Redundancy (Figure 1 vs 2; Figure 10 subset) - apply the economy in section 3.
- Ensure captions in the final draft match the trimmed numbering; the existing
  `figure_captions.md` / `table_captions.md` are keyed to the current names.

---

## 7. Final recommendation

The current materials **are sufficient to write the final submission draft**,
conditional on the named TODOs (resolve/remove the Samorani reference, confirm
data accessed dates) and the figure/table economy in section 3. No new
experiments are required for an arXiv/workshop submission.

### Suggested next prompt for the writing pass

"Create `paper/final_submission_draft.md` from `paper/main.md`, applying
`paper/arxiv_structure_plan.md`: keep the section order, move detail to an
appendix, include only the recommended main-body figures (2, 3, 6, 7, and
optionally 9) and tables (trimmed 3, 7, 1), add short Reproducibility / Data
Availability / Ethics end-matter, and resolve the Samorani reference (verify full
metadata or remove it and its sentence). Do not change any empirical numbers; keep
them consistent with `paper/number_audit.md`. Make no causal, production, real-
dispatch, or full-paper-readiness claims. Then update the submission readiness
checklist." A later, separate pass can format to a venue template and build the
PDF.
