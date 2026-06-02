# Paper Conversion File Checklist

Files needed to convert this repository into a small paper, arXiv-style preprint,
or workshop paper. This project is a workshop / short-paper / arXiv-style
artifact only; it is not full-paper ready.

Public project name: Public Signal Service Forecasting.
Paper-style title: From Forecast Accuracy to Operational Value: Public Signal
Augmentation for NYC 311 Service Demand.

## 1. Core paper files (CREATED in `paper/`)

The `paper/` directory has been created. Status:

- [x] `paper/main.md` - the paper body.
- [x] `paper/references.bib` - bibliography (Cui 2018 verified; NYC 311 and NOAA
  data sources; one TODO reference to verify or remove).
- [x] `paper/figures/` - 10 publication-named copies of the committed figures
  (+ README).
- [x] `paper/tables/` - 8 result tables built from `reports/` and
  `data/metadata/`.
- [x] `paper/appendix.md` - feature definitions, robustness detail, weather
  provenance.
- [x] `paper/reproducibility_statement.md` - environment, commands, data access.
- [x] `paper/data_availability_statement.md` - NYC 311 and NOAA sources.
- [x] `paper/ethics_statement.md` - aggregate-only data, reporting bias, no
  deployment.
- [x] `paper/limitations.md` - limitations and full-paper blockers.
- [x] `paper/number_audit.md`, `paper/figure_captions.md`,
  `paper/table_captions.md`, `paper/venue_notes.md`,
  `paper/submission_readiness_checklist.md`, `paper/README.md`.

Remaining manual work (not auto-generatable): final reference verification
(resolve the TODO reference; confirm data-source accessed dates), a full
related-work section, the final PDF build, venue-specific formatting, and a final
human edit. A workshop cover note and venue formatting notes can be added at
formatting time.

## 2. Existing repository files that already support the paper

- `README.md`
- `docs/research_brief.md`
- `docs/data_card.md`
- `docs/model_card.md`
- `docs/decision_simulation.md`
- `docs/limitations.md`
- `docs/architecture.md`
- `docs/responsible_ai.md`
- `research_artifacts/short_paper_draft.md` (4-6 page draft)
- `research_artifacts/extended_abstract.md`
- `research_artifacts/results_brief.md`
- `research_artifacts/claims_audit.md`
- `research_artifacts/public_claims_one_pager.md`
- `research_artifacts/reviewer_risk_register.md`
- `research_artifacts/figure_interpretation_guide.md`
- `research_artifacts/final_project_summary.md`
- `research_artifacts/final_research_decision.md`
- `research_artifacts/project_freeze_note.md`
- `reports/model_comparison.csv`
- `reports/metrics.json`
- `reports/evaluation_report.json`
- `reports/rolling_validation_summary.json`
- `reports/rolling_validation_report.csv`
- `reports/borough_performance.csv`
- `reports/complaint_group_performance.csv`
- `reports/decision_simulation_report.json`
- `reports/decision_sensitivity_summary.json`
- `reports/practical_significance_summary.json`
- `data/metadata/data_source_report.json`
- `data/metadata/weather_source_report.json`
- `figures/*.png` (model comparison, feature-set comparison, internal vs
  calendar-augmented, rolling validation, borough, complaint group, decision
  quality, decision sensitivity, actual vs predicted, weather feature summary)

## 3. Missing files still needed before arXiv/workshop submission

- `references.bib` populated with real, verified literature.
- A formal related-work section (currently only brief motivation exists).
- A final paper PDF build.
- Final title and abstract chosen for the target venue.
- Final figure captions and table captions.
- An appendix with exact feature definitions and full robustness detail.
- A reproducibility-package description and a data-license note.
- A venue-specific formatting file (template).
- A final citation audit against the literature.
- A final manual verification of every number against `reports/`.
- Optionally, a PDF build workflow if using LaTeX.

## 4. Minimum paper package (smallest viable arXiv/workshop submission)

- `paper/main.md` (or `.tex`) built from `research_artifacts/short_paper_draft.md`.
- `paper/references.bib` with the core citations.
- 3-4 figures from `figures/` (model/feature-set comparison, rolling validation,
  decision sensitivity).
- 1-2 tables from `reports/model_comparison.csv` and the decision summaries.
- `paper/reproducibility_statement.md` and
  `paper/data_availability_statement.md`.
- `docs/limitations.md` content folded into the paper.

## 5. Recommended paper package (stronger workshop submission)

- Everything in the minimum package, plus:
- A formal related-work section and a complete `references.bib`.
- `paper/appendix.*` with feature definitions, weather provenance, and full
  per-borough and per-complaint-group robustness tables.
- All ten figures with final captions, and `paper/ethics_statement.md`.
- `research_artifacts/reviewer_risk_register.md` mapped into reviewer-facing
  limitations.
- A reproducibility package description referencing the committed data and the
  CI sample mode.

## 6. Not needed yet

- Journal cover letter.
- Response-to-reviewers document.
- Production deployment docs.
- Production monitoring docs.
- IRB package (unless the target venue or an institution requires it; the data
  is aggregate and public).
- A causal-identification appendix (the project makes no causal claim).

## 7. Next action to convert to paper

Create `paper/references.bib` with real, verified literature and a formal
related-work section; that single step unblocks turning the existing
`short_paper_draft.md` into a submittable workshop draft.
