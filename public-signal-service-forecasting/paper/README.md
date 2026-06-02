# Paper Package

This folder is a draft arXiv-style / workshop-style paper package for the project
Public Signal Service Forecasting (research line: Forecasting Service Demand with
Public Signals). It assembles the paper body, supporting statements, tables, and
figures from the committed repository evidence artifacts. It is a draft package,
not a finished or full paper.

## How to read this folder

- `main.md` - the main paper body (Title, Abstract, Introduction, Related Work,
  Data, Methods, Forecasting Results, Forecast-to-Decision Simulation, Robustness
  Checks, Limitations, Reproducibility, Conclusion). Start here.
- `references.bib` - bibliography; one verified entry (Cui et al. 2018), two data
  sources, and one TODO reference to verify or remove before submission.
- `tables/` - eight tables built from committed reports and metadata.
- `figures/` - ten figures copied from the committed repository figures, with a
  README mapping each to its source.
- `figure_captions.md`, `table_captions.md` - captions, key takeaways, and
  overclaims to avoid.

## Support statements

- `reproducibility_statement.md` - environment, commands, CI/sample-mode note.
- `data_availability_statement.md` - sources, what is committed/ignored.
- `ethics_statement.md` - public/aggregate data, reporting bias, no deployment.
- `limitations.md` - limitations and full-paper blockers.
- `number_audit.md` - every numeric claim traced to a committed artifact.
- `venue_notes.md` - arXiv/workshop suitability and what is not claimed.
- `submission_readiness_checklist.md` - status and remaining manual work.

## What remains before arXiv/workshop upload

Verify or remove the TODO reference, confirm data-source accessed dates, write a
full related-work section if the venue requires it, do a final human edit, and
format to the target venue template and build a PDF. See
`submission_readiness_checklist.md`.

## Claims boundary

This package makes no causal, production-readiness, deployment, real-dispatch, or
real-staffing-optimization claims, and no full-paper or publication-readiness
claim. It uses only real NYC 311 and real NOAA weather data; no synthetic data and
no synthetic weather.
