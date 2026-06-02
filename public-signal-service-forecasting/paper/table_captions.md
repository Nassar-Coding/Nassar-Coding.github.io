# Table Captions

Sources: `paper/tables/*.md`, the report artifacts, and
`research_artifacts/results_brief.md`.

## Table 1 - table_1_dataset_summary.md
- Caption: Summary of the real NYC 311 service-request data and the real NOAA
  Central Park weather data, with study window, sizes, and provenance.
- Key takeaway: real data only; 9,851,452 raw 311 records to 43,240 processed
  rows; 1,096 daily weather rows; no synthetic data or weather.
- Avoid: do not imply borough-level weather; it is a single-station proxy.

## Table 2 - table_2_feature_sets.md
- Caption: Definitions of the four feature sets.
- Key takeaway: augmentation adds deterministic calendar features and/or real
  weather features to the internal-historical base.
- Avoid: do not describe calendar features as external signals; weather is the
  external signal.

## Table 3 - table_3_model_comparison.md
- Caption: Held-out test metrics for all model x feature-set combinations, plus
  the selected refit model.
- Key takeaway: random forest on calendar+weather is best; selected refit test
  MAE 55.325.
- Avoid: single-split point estimates; not statistically tested differences.

## Table 4 - table_4_rolling_validation.md
- Caption: Five-fold rolling-origin mean fold MAE and calendar-augmentation
  consistency by model.
- Key takeaway: augmentation wins every fold for every model; effect is stable.
- Avoid: consistency is not a formal significance test.

## Table 5 - table_5_borough_robustness.md
- Caption: Internal vs calendar-augmented test MAE by borough (random forest).
- Key takeaway: all five boroughs improve.
- Avoid: absolute error tracks volume, not model quality.

## Table 6 - table_6_complaint_group_robustness.md
- Caption: Internal vs calendar-augmented test MAE by complaint group (random
  forest).
- Key takeaway: all eight groups improve.
- Avoid: do not read low-volume small bars as better relative performance.

## Table 7 - table_7_decision_sensitivity.md
- Caption: Stylized staffing-simulation weighted unmet demand by policy and crew
  budget, with reductions and gap-to-oracle.
- Key takeaway: augmented policy better at every budget; magnitude is
  budget-dependent.
- Avoid: stylized, not real dispatch; not staffing optimization.

## Table 8 - table_8_limitations_and_mitigations.md
- Caption: Limitations and their current mitigations / honest framing.
- Key takeaway: the main risks (reporting bias, single-station weather, stylized
  decision layer, no causal inference) are documented, not hidden.
- Avoid: do not present mitigations as if they remove the limitations.
