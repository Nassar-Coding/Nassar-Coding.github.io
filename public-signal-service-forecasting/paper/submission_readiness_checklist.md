# Submission Readiness Checklist

## Files created

- paper/main.md
- paper/references.bib
- paper/appendix.md
- paper/reproducibility_statement.md
- paper/data_availability_statement.md
- paper/ethics_statement.md
- paper/limitations.md
- paper/number_audit.md
- paper/figure_captions.md
- paper/table_captions.md
- paper/venue_notes.md
- paper/submission_readiness_checklist.md (this file)
- paper/README.md
- paper/figures/ (10 figures + README)
- paper/tables/ (8 tables)

## Figures copied (10)

figure_1_model_comparison_mae, figure_2_feature_set_comparison_mae,
figure_3_rolling_validation_mae, figure_4_borough_robustness_mae,
figure_5_complaint_group_robustness_mae, figure_6_decision_sensitivity,
figure_7_actual_vs_predicted, figure_8_weather_feature_summary,
figure_9_decision_quality_comparison,
figure_10_internal_vs_calendar_augmented_mae.

- Not copied: `figures/forecast_error_by_model.png` (same content as
  model_comparison_mae.png; alias).
- No listed figure was missing; none were fabricated.

## Tables created (8)

table_1_dataset_summary, table_2_feature_sets, table_3_model_comparison,
table_4_rolling_validation, table_5_borough_robustness,
table_6_complaint_group_robustness, table_7_decision_sensitivity,
table_8_limitations_and_mitigations.

## References

- Complete and verified: Cui et al. 2018 (`cui2018operational`).
- Data sources (verified id/URL; minor TODO on exact accessed date / DOI version):
  `nyc311`, `noaaghcnd`.
- Incomplete (TODO, must verify or remove before submission):
  `samorani2022TODO` - exact author list, title, venue, volume, pages, DOI not
  verified.

## Numbers verified

All numeric claims in main.md, tables, appendix, and captions are traced to a
committed artifact in `paper/number_audit.md` and verified against it.

## Manual checks remaining

- Verify or remove the `samorani2022TODO` reference; confirm exact accessed dates
  and any DOI/version for `nyc311` and `noaaghcnd`.
- Write a full related-work section (currently brief) if targeting a workshop with
  a related-work requirement.
- Final human read-through and copy-edit of main.md.
- Confirm figure and table numbering matches the final main.md ordering at build
  time.

## Venue formatting remaining

- Convert main.md to the target venue template (LaTeX or the venue's Markdown),
  build a PDF, choose the final title/abstract for the venue, and finalize figure
  and table captions in the template.

## Final verdict

Paper package DRAFT READY. It is not ready for arXiv/workshop upload until the
manual reference verification (especially the TODO reference), a final human
edit, and venue formatting are completed. The package makes no causal,
production-readiness, full-paper-readiness, or real-dispatch-optimization claims.
