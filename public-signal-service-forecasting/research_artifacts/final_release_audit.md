# Final Release Audit

## 1. Audit date

2026-06-01.

## 2. Branch

`research/real-nyc-311-upgrade`.

## 3. Latest commit before this audit

`f3ed33ae6d208a4da94641cf9832fa5162d7fd38` (weather-augmentation pass). This
audit pass adds the public-release cleanup on top of that commit.

## 4. Public project name

Public Signal Service Forecasting. Research line: Forecasting Service Demand with
Public Signals.

## 5. Paper-style title

From Forecast Accuracy to Operational Value: Public Signal Augmentation for NYC
311 Service Demand.

## 6. Dataset facts

Real NYC 311 Service Requests (NYC Open Data, `erm2-nwe9`), 2022-2024.
9,851,452 raw records; 9,838,988 retained after filtering; 43,240 processed rows.
Unit: date x borough x complaint_group. Target: `request_volume_next_day`
(observed next-day count). Five boroughs; eight complaint groups. No synthetic
data, no synthetic fallback.

## 7. Weather facts

Real NOAA NCEI Daily Summaries (GHCN-Daily), station USW00094728 (NY City
Central Park), 2022-2024, 1,096 days. Variables used: precipitation, daily
maximum and minimum temperature, derived average temperature (mean of observed
TMAX/TMIN because the source TAVG column was empty), snowfall, snow depth, and
wind speed. Five missing wind-speed days were filled by time interpolation of
neighbouring real observations. Single Central Park station used as a
city-level proxy (documented limitation). No synthetic weather; missing source
variables are recorded, not fabricated.

## 8. Final model facts

Best model: random forest on `calendar_weather_augmented`. Held-out test MAE
55.33, RMSE 177.48, MAPE 27.47%, R-squared 0.648; 23.0% better than the naive
seasonal baseline (test MAE 71.85). Calendar is the dominant signal; real weather
adds a smaller but consistent further gain (random forest weather-only 64.10 <
internal 65.28; calendar+weather 56.22 < calendar 58.08). Ridge does not benefit
from weather.

## 9. Final decision-simulation facts

Stylized proportional staffing-allocation simulation; not real dispatch and not
real optimization. Baseline budget (135 crews, 50 requests/crew): weighted unmet
demand 643,324 (internal), 634,614 (calendar), 641,382 (weather), 631,191
(calendar+weather), 597,332 (oracle). The calendar+weather policy reduces
weighted unmet demand by 1.886% and closes 26.381% of the baseline-to-oracle
gap. Across scarce/moderate/generous crew budgets the augmented policy is better
in all three (reductions 0.38%, 4.32%, 14.53%), but the magnitude is
budget-dependent.

## 10. Robustness facts

Five-fold rolling-origin validation: augmentation improves every model in every
fold (random forest mean +15.1%, gradient boosting +9.9%, Ridge +0.9%); the
calendar+weather random forest has the lowest mean fold MAE (47.50). Borough
robustness: improved in all 5 boroughs (about 8.8% to 18.8%). Complaint-group
robustness: improved in all 8 groups (about 8.9% to 25.8%).

## 11. Public-facing claim audit

The strongest safe claim is that public-signal augmentation consistently lowers
next-day forecast error on real NYC 311 data and transfers in direction to a
stylized staffing metric, with attenuated, budget-dependent magnitude. Safe and
unsafe claims are enumerated in `public_claims_one_pager.md` and tied to
artifacts in `claims_audit.md`. The project is described consistently as a
workshop / short-paper / arXiv-style artifact, not a full paper.

## 12. Unsafe claims removed or prohibited

The repository does not claim causal impact, causal identification, production
readiness, deployment, real dispatch impact, real staffing optimization,
public-safety operational use, external validity beyond NYC 2022-2024, full-paper
or journal readiness, or publication acceptance. It does not claim that forecast
accuracy equals operational value, nor that decision gains are large or
guaranteed. Legitimate boundary statements (for example "does not claim causal
impact", "not production-ready", "synthetic fallback was removed") are retained.

## 13. Candidate / internal terminology cleanup result

All public-facing internal candidate labels were removed. Four artifact files
were renamed (`candidate_c_final_decision.md` to `final_research_decision.md`,
`final_candidate_c_summary.md` to `final_project_summary.md`,
`candidate_c_short_paper.md` to `short_paper_draft.md`,
`candidate_c_freeze_note.md` to `project_freeze_note.md`), and all links were
updated. Remaining textual "Candidate C"/"Candidate A" wording was rewritten to
public project language. The only remaining word "candidate" appears as "model
candidates", which is ordinary modelling vocabulary, not the internal label.
No "vault", "PhD", "brand-tier", "paper bet", "de-risk", or similar internal
planning terms remain.

## 14. Personal / internal content audit result

No personal biography, academic-planning, application-strategy, employer/client,
or internal-program content is present. No personal email, phone number,
LinkedIn, or social handle is present. The only ownership reference is the
`Nassar-Coding` GitHub namespace in repository URLs, which is legitimate
ownership context.

## 15. Synthetic-data audit result

No synthetic data, no synthetic fallback, and no synthetic weather are used in
research mode. The previously removed synthetic-fallback generator is referenced
only as deprecated/removed, never as current behaviour. All 311 results derive
from real NYC 311 records and all weather results from real NOAA records.

## 16. AI-assistant-reference audit result

No references to AI assistants, coding assistants, prompt generation, or the
development conversation appear in repository content. Note: git commit author
metadata records `Claude <noreply@anthropic.com>`; this is version-control
metadata, not repository content, and git history is not rewritten.

## 17. CI/CD status

A repository-root workflow (`.github/workflows/ci.yml`) runs the project with
the working directory set to `public-signal-service-forecasting`, on Python 3.11,
in sample mode (`USE_SAMPLE_DATA=1`), executing ruff, pytest, and the pipeline;
it requires no secrets and no API keys. An in-project workflow copy is retained
for standalone-repository portability. The GitHub Actions conclusion for the
final commit must be confirmed on the repository Actions tab; this document does
not assert a green run that has not been verified there.

## 18. Final readiness judgment

The repository is clean, professional, reproducible, and public-presentation
ready. It is a workshop / short-paper / arXiv-style artifact, not full-paper
ready. The project is frozen unless future work adds stronger decision realism
(a non-stylized, agency-grounded decision model with an empirical realism check),
formal forecast-difference testing, and broader external validation. See
`project_freeze_note.md` and `final_research_decision.md`.
