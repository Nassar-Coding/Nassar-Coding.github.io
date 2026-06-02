# Venue Notes

Sources: `research_artifacts/final_research_decision.md`,
`research_artifacts/project_freeze_note.md`,
`research_artifacts/practical_significance_summary.json` (via reports), and
background framing on public-data feature augmentation in operations forecasting.

## arXiv-style technical report

Suitable now. The artifact is real-data, leakage-controlled, reproducible, and
honestly scoped, with committed evidence artifacts and a number audit. An
arXiv-style technical report is an appropriate home for it as-is, after reference
verification and a final human edit.

## Workshop submission

Suitable as a short paper / extended abstract for operations-management,
information-systems, or applied-analytics workshops. The forecasting result is
robust across folds and segments, and the forecast-to-decision framing with an
oracle bound is a clean, honest contribution.

## POM-style future paper conditions

A production-and-operations-management-style full paper would require moving
beyond the present scope. The methodological lineage (public-data feature
augmentation for operational forecasting) supports a POM-level contribution, but
the decision-link must become non-stylized and the evidence must be strengthened
(see below).

## Why not full-paper ready

`reports/practical_significance_summary.json` records
`forecasting_evidence_strong = true`, `decision_evidence_strong = false`, and
`strong_enough_for_full_paper_drafting = false`. The forecasting result is strong
and stable, but the decision evidence is directionally consistent yet
budget-dependent and rests on a single stylized proportional-allocation heuristic,
and there is no formal forecast-difference testing and only a single external
signal (one weather station).

## What full-paper conversion would need

1. A non-stylized, agency-grounded decision model with an empirical service-level
   realism check.
2. Formal forecast-difference testing (for example a Diebold-Mariano test) with
   uncertainty intervals.
3. Broader external signals beyond a single weather station (multi-station or
   gridded weather, transit, events), or cross-city replication.
4. A complete related-work section and a fully verified bibliography.

## What not to claim

No causal impact, no production readiness, no deployment, no real dispatch
optimization, no real staffing optimization, no public-safety use, no external
validity beyond NYC 2022-2024, and no full-paper or publication readiness.
