# Candidate C: Final Decision

This document closes the Candidate C phase. All values are read from committed
artifacts under `reports/` and `data/metadata/` and reflect the real NYC 311
dataset (not the small CI sample).

## 1. What was Candidate C?

Candidate C is a real-data research baseline asking whether calendar-augmented
forecasting improves next-day NYC 311 service-request volume prediction, and
whether any forecast improvement translates into measurable improvement in a
stylized staffing-allocation simulation. The unit of analysis is
date x borough x complaint_group and the target is `request_volume_next_day`.

## 2. What was built?

A complete, reproducible local pipeline: data location and validation
(`src/download_data.py`), aggregation and feature construction
(`src/build_dataset.py`, `src/features.py`), model training and selection
(`src/train.py`), evaluation (`src/evaluate.py`), a stylized decision simulation
(`src/decision_simulation.py`), monitoring (`src/monitor.py`), a Streamlit
dashboard (`app.py`), and a robustness package added in this closure pass:
rolling-origin validation (`src/rolling_validation.py`), segmented robustness by
borough and complaint group (`src/robustness_analysis.py`), decision-budget
sensitivity (`src/decision_sensitivity.py`), and a practical-significance summary
(`src/practical_significance.py`). The repository also includes documentation,
tests, CI, and a research-artifact package.

## 3. What data was used?

Real NYC 311 Service Requests (NYC Open Data, `erm2-nwe9`) for calendar years
2022-2024. The pipeline read 9,851,452 raw records and retained 9,838,988 after
filtering; the processed modelling panel has 43,240 rows over five boroughs and
eight complaint groups, spanning observed dates 2022-01-15 to 2024-12-30. No
synthetic data and no synthetic fallback are used anywhere.

## 4. What did the models show?

On the single chronological 70/15/15 split, the selected model is a random forest
on the calendar-augmented feature set with test MAE 57.26 (RMSE 182.21, MAPE
28.05%, R-squared 0.629), improving on the naive seasonal baseline (test MAE
71.85) by 20.3%. Calendar augmentation lowered test MAE for every model: random
forest 65.28 to 58.08 (11.03%), gradient boosting 67.49 to 61.71 (8.57%), and
Ridge 69.22 to 68.76 (0.67%).

## 5. What did rolling-origin validation show?

Across five expanding-window chronological folds, calendar augmentation lowered
MAE in every fold for every model: random forest improved by a mean of 15.13%
(5 of 5 folds), gradient boosting by 9.94% (5 of 5), and Ridge by 0.94% (5 of 5).
The random-forest calendar-augmented configuration had mean fold MAE 48.69 (std
9.59), versus 57.03 (std 8.05) for its internal-historical counterpart. The
direction and consistency of the forecasting effect are therefore stable, not an
artifact of one split.

## 6. What did borough robustness show?

On the held-out test partition, calendar augmentation improved MAE for all five
boroughs (5 of 5), with improvements ranging from about 4.7% (Bronx) to about
15.8% (Queens). Absolute error scales with borough volume (largest for the Bronx,
smallest for Staten Island), but the augmentation gain is present everywhere.

## 7. What did complaint-group robustness show?

Calendar augmentation improved MAE for all eight complaint groups (8 of 8), with
improvements ranging from about 5.8% (Housing) to about 25.7% (Street Condition).
Absolute error is largest for the high-volume Noise and Housing groups; the
augmentation gain is present across all groups.

## 8. What did decision sensitivity show?

Under three crew budgets, the calendar-augmented policy reduced weighted unmet
demand relative to the internal-historical policy in all three settings, but the
magnitude is strongly budget-dependent: 0.21% under a scarce budget (100 crews),
3.19% under a moderate budget (160 crews), and 12.05% under a generous budget
(220 crews). The share of the baseline-to-oracle gap closed ranged from about
14.5% to 17.5%. The direction is consistent; the size is not.

## 9. What is the strongest safe claim?

On real NYC 311 data for 2022-2024, adding deterministic calendar features to an
internal-historical forecasting model produces a consistent reduction in
next-day forecast error - in every rolling-origin fold, every borough, and every
complaint group - and this improvement carries through, in direction, to a
stylized staffing-allocation simulation across scarce, moderate, and generous
crew budgets.

## 10. What is the strongest unsafe claim that must not be made?

That calendar-augmented forecasting causes, or would deliver, a specific
operational improvement in real NYC staffing or dispatch. The decision result is
from a single stylized proportional-allocation heuristic, its magnitude depends
on the assumed crew budget, and the study is correlational on reported (not true)
demand. No causal, production, real-dispatch, or real-optimization claim is
supportable.

## 11. Is this full-paper worthy now?

No. The forecasting evidence is strong and stable, but the decision evidence,
while directionally consistent, is budget-dependent and rests on one stylized
decision model. `reports/practical_significance_summary.json` records
`forecasting_evidence_strong = true`, `decision_evidence_strong = false`, and
`strong_enough_for_full_paper_drafting = false`. A full paper would need an
external-signal comparison, formal forecast-difference testing, and a richer
decision model (see item 14).

## 12. Is this extended-abstract/workshop worthy now?

Yes. The forecasting contribution is real-data, leakage-controlled, and robust
across folds and segments; the forecast-to-decision framing is clear and honestly
reports an attenuated, budget-dependent decision effect. This is a suitable basis
for an extended abstract or workshop artifact in operations management,
information systems, or applied analytics venues.

## 13. Should Candidate C continue, pause, or be archived?

Use as an extended-abstract/workshop artifact, then pause. The baseline is sound
and the forecasting result is defensible, but the marginal research value of
continuing to a full paper is gated on specific additional work that has not yet
been done.

## 14. What exact work would be required to convert it into a full paper?

1. External-signal comparison: add genuinely exogenous, no-key public signals
   (for example weather) and re-run the internal vs augmented comparison to
   separate calendar/seasonality effects from external information.
2. Formal inference: replace informal consistency with statistical tests for
   forecast-accuracy differences across folds (for example Diebold-Mariano) and
   report uncertainty intervals.
3. Richer decision model: move beyond a single proportional heuristic to a
   constrained allocation with explicit service-level targets, and characterise
   when forecast gains do and do not translate into decision gains.
4. Robustness and bias: analyse 311 reporting bias, test finer geography within
   the no-personal-data boundary, and assess temporal stability beyond the
   2022-2024 window.
5. Positioning: a literature review situating the contribution against existing
   service-demand forecasting and forecast-to-decision work.

## 15. Final recommendation

Use as extended abstract/workshop artifact, then pause.
