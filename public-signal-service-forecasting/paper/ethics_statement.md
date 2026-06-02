# Ethics Statement

Sources: `docs/responsible_ai.md`, `docs/limitations.md`,
`research_artifacts/public_claims_one_pager.md`.

- **Public data only.** The study uses public NYC 311 Service Requests and public
  NOAA weather. No authentication, no private data, and no personal data are
  used.
- **Aggregate analysis.** All quantities are aggregate daily counts at the
  date x borough x complaint_group level. No individual-level records are used or
  produced.
- **No individual-level decisioning.** The work does not make or support any
  decision about individuals.
- **No production deployment.** This is a local research baseline. It is not
  deployed and is not integrated with any real system.
- **No public-safety use.** The project is not public-safety software and must not
  be used to make real public-safety, dispatch, or staffing decisions.
- **No causal claims.** The study is correlational and predictive; it does not
  identify or estimate any causal effect.
- **No real dispatch optimization.** The staffing simulation is a stylized
  proportional heuristic and is not a real dispatch or staffing optimizer.
- **Reporting-bias warning.** NYC 311 reflects who reports and how requests are
  categorized, not true underlying incidence. Reporting propensity varies across
  communities and time, so forecasts of 311 volume are forecasts of reporting,
  not of need, and must not be interpreted as measures of true demand or used in
  ways that could compound existing inequities.
