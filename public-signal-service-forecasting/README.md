# Public Signal Service Forecasting

A reproducible real public-data ML baseline for NYC 311 service-request
forecasting and staffing decision simulation.

## Research Artifact Package

The repository includes a `research_artifacts/` folder with a research-facing
package summarising and auditing the real-data baseline. All values in these
documents are read from the committed artifacts under `reports/` and
`data/metadata/`.

- [`research_artifacts/research_memo.md`](research_artifacts/research_memo.md) - research memo (question, method, results, limitations, next steps).
- [`research_artifacts/extended_abstract.md`](research_artifacts/extended_abstract.md) - workshop-style extended abstract.
- [`research_artifacts/short_paper_draft.md`](research_artifacts/short_paper_draft.md) - 4-6 page short-paper draft (real NYC 311 + real NOAA weather).
- [`research_artifacts/results_brief.md`](research_artifacts/results_brief.md) - concise tabular results brief.
- [`research_artifacts/figure_interpretation_guide.md`](research_artifacts/figure_interpretation_guide.md) - how to read each figure.
- [`research_artifacts/claims_audit.md`](research_artifacts/claims_audit.md) - claim-by-claim audit tied to artifacts.
- [`research_artifacts/public_claims_one_pager.md`](research_artifacts/public_claims_one_pager.md) - safe and unsafe public claims at a glance.
- [`research_artifacts/reviewer_risk_register.md`](research_artifacts/reviewer_risk_register.md) - anticipated reviewer concerns and mitigations.
- [`research_artifacts/public_project_summary.md`](research_artifacts/public_project_summary.md) - public-facing project summary.
- [`research_artifacts/final_research_decision.md`](research_artifacts/final_research_decision.md) - final research decision.
- [`research_artifacts/final_project_summary.md`](research_artifacts/final_project_summary.md) - concise executive summary.
- [`research_artifacts/project_freeze_note.md`](research_artifacts/project_freeze_note.md) - final freeze note and reopen conditions.
- [`research_artifacts/paper_conversion_file_checklist.md`](research_artifacts/paper_conversion_file_checklist.md) - files needed to convert to a short/workshop paper.
- [`research_artifacts/final_release_audit.md`](research_artifacts/final_release_audit.md) - final public-release audit.

This is a research baseline package, not a finished paper, and it makes no
causal, production-readiness, or real-staffing-optimization claims.

## Project Final Status

This project (Public Signal Service Forecasting; research line: Forecasting
Service Demand with Public Signals) is a real-data NYC 311 research baseline
augmented with real NOAA weather. A robustness package (rolling-origin
validation, borough and complaint-group robustness, and decision-budget
sensitivity) shows that public-signal augmentation improves next-day forecast
accuracy consistently across folds, boroughs, and complaint groups, and improves
a stylized staffing-allocation metric in direction across crew budgets (with
budget-dependent magnitude).

- It is suitable for public presentation and for an extended-abstract / workshop
  artifact.
- It is not a full paper. The evidence supports an extended abstract / short
  paper, not full-paper drafting, per
  [`research_artifacts/final_research_decision.md`](research_artifacts/final_research_decision.md).
- It does not claim causal impact, production readiness, real dispatch impact, or
  real staffing optimization, and it makes no external-validity claim beyond NYC
  2022-2024.

The reproducible robustness artifacts are produced by
`python -m src.rolling_validation`, `python -m src.robustness_analysis`,
`python -m src.decision_sensitivity`, and `python -m src.practical_significance`.

## 1. Summary

This repository is a local, reproducible machine-learning baseline that tests
whether calendar and temporal features improve next-day NYC 311 service-request
volume forecasts, and whether improved forecasts translate into better stylized
staffing or dispatch allocation decisions. It forecasts next-day request volume
at the date x borough x complaint_group level using real NYC 311 data for
calendar years 2022-2024, and pairs the forecasting study with a transparent
staffing-allocation simulation.

## 2. What this is and is not

- This project uses real NYC 311 public data in research mode.
- This project does not use synthetic fallback data in research mode. If valid
  real data is unavailable, the build fails with a specific error.
- CI may use a small committed real-schema sample for speed and reproducibility.
- It does not claim causal effects.
- It does not claim production readiness.
- Forecast accuracy improvement is not the same as operational value; therefore
  the project includes a stylized decision simulation, which is not real
  dispatch and not a claim of real staffing optimization.

## 3. Research motivation

Service organizations must allocate finite crews against uncertain, time-varying
demand. Forecasting daily request volume and allocating capacity against it is a
classic operations-management problem. A recurring research question is whether
calendar and temporal structure adds value beyond an organization's own internal
request history, and whether any predictive gain actually improves decisions.

## 4. Research question

Can real NYC 311 service-request history, calendar features, and temporal lag
features forecast next-day service-request volume, and does improved forecast
accuracy translate into improved stylized staffing allocation decisions?

## 5. Why this is not just forecasting

A reduction in average forecast error does not automatically imply better
operational decisions, because decision quality depends on the loss structure of
the allocation problem. To make this explicit, the project includes a stylized
staffing-allocation simulation comparing an internal-historical forecast policy,
a calendar-augmented policy, and an oracle (true-demand) benchmark.

## 6. Repository structure

```
public-signal-service-forecasting/
  app.py                      Streamlit dashboard
  README.md
  LICENSE
  requirements.txt
  pyproject.toml
  scripts/
    aggregate_nyc_311_local.py  Local reducer: 36 monthly exports -> daily counts
  data/
    raw/                      real daily counts, metadata, and CI sample
    processed/                processed modelling dataset
    metadata/                 data_source_report.json
  models/                     best_forecast_model.joblib
  reports/                    metrics, comparison, evaluation, simulation, monitoring
  figures/                    generated charts
  docs/                       research brief, architecture, data/model cards, etc.
  src/                        pipeline modules
  tests/                      pytest suite
  .github/workflows/ci.yml    in-project CI copy (root copy drives the monorepo)
```

## 7. Data source: NYC 311 Service Requests

The data is NYC 311 Service Requests from NYC Open Data (Socrata dataset
`erm2-nwe9`). The fields used are `created_date`, `borough`, `complaint_type`,
and `unique_key`. Records are aggregated to observed daily counts by date,
borough, and complaint group.

## 8. Study window: 2022-2024

Only calendar years 2022, 2023, and 2024 are used. No 2025 data, no pre-2022
data, and no partial years.

## 9. No synthetic data statement

Research mode uses only real observed NYC 311 records. The project does not
generate synthetic data, does not simulate service-request demand, and does not
silently fall back to fabricated data. The previous synthetic-fallback generator
has been removed. If valid real data cannot be located or validated, the build
raises a clear `DataUnavailableError`.

## 10. Data acquisition and manual download option

The full multi-million-row export is large, so the supported path is to reduce
the monthly exports to observed daily counts locally:

1. Download the 36 monthly NYC 311 CSVs (one per month, 2022-2024), each
   containing at least `created_date`, `borough`, `complaint_type`,
   `unique_key`.
2. Run the local reducer over the folder of monthly files:

   ```bash
   python scripts/aggregate_nyc_311_local.py --input-dir <folder_of_monthly_csvs>
   ```

   This writes `nyc_311_daily_counts_2022_2024.csv` (a few MB) and a metadata
   JSON. Place the CSV at
   `data/raw/nyc_311_daily_counts_2022_2024.csv` (and, optionally, the metadata
   alongside it).

Alternatively, place a record-level export at
`data/raw/nyc_311_2022_2024.csv` (same required columns); `build_dataset` will
aggregate it in-process using the same deterministic complaint mapping.

## 11. Feature sets: internal historical, calendar, and real weather

- **Internal historical:** `borough`, `complaint_group`, `request_lag_1`,
  `request_lag_7`, `rolling_mean_7`, `rolling_mean_14`, `rolling_std_7`,
  `rolling_std_14`.
- **Calendar augmented:** all internal-historical features plus `is_weekend`,
  `is_holiday`, `day_of_week`, `month`, `quarter`, `year`, `day_of_year`,
  `week_of_year`, `is_month_start`, `is_month_end`.
- **Weather augmented:** all internal-historical features plus real NOAA daily
  weather (`precipitation_mm`, `temp_max_c`, `temp_min_c`, `temp_avg_c`,
  `snowfall_mm`, `snow_depth_mm`, `wind_speed_ms`).
- **Calendar + weather augmented:** internal-historical plus both calendar and
  real weather features.

The weather layer is real NOAA NCEI Daily Summaries (GHCN-Daily) for the NYC
Central Park station (USW00094728), 2022-2024, used as a single-station
city-level proxy (a documented limitation). No transit or event data is included
in this version. No synthetic weather is generated.

## 12. Model candidates

- Naive seasonal baseline (trailing 7-day rolling mean)
- Ridge regression
- Random forest regressor
- Gradient boosting regressor

Each non-naive model is trained on every available feature set.

## 13. Chronological validation design

A strictly chronological split by date prevents leakage: the earliest 70% of
dates are used for training, the next 15% for validation, and the latest 15% for
test. Lag and rolling features are computed per cell using only past
observations. Metrics are MAE (primary), RMSE, MAPE (safe zero handling), and
R-squared. The best model is chosen by validation MAE and refit on
train+validation before final test evaluation. See `docs/model_card.md`.

## 14. Decision simulation design

Each day, a fixed and intentionally scarce crew budget is allocated across cells
in proportion to forecasted next-day demand using a largest-remainder rule. Each
crew provides a fixed capacity; unmet demand is the positive part of actual
demand minus allocated capacity. Three policies (baseline internal-historical,
calendar-augmented, and oracle true-demand) are compared on total and weighted
unmet demand, average shortfall, high-demand coverage, allocation efficiency,
percent improvement over baseline, and the share of the gap to oracle closed.
See `docs/decision_simulation.md`.

## 15. ML lifecycle mapping

| Lifecycle stage | Module(s) | Artifact(s) |
|-----------------|-----------|-------------|
| Local aggregation | `scripts/aggregate_nyc_311_local.py` | `data/raw/nyc_311_daily_counts_2022_2024.csv` |
| Data location | `src/download_data.py` | validated real input path |
| Data processing | `src/build_dataset.py`, `src/features.py` | `data/processed/service_forecasting_dataset.csv`, `data/metadata/data_source_report.json` |
| Modelling | `src/train.py` | `models/best_forecast_model.joblib`, `reports/model_comparison.csv`, `reports/metrics.json` |
| Evaluation | `src/evaluate.py` | `reports/evaluation_report.json`, figures |
| Decision linkage | `src/decision_simulation.py` | `reports/decision_simulation_report.json`, figure |
| Inference | `src/predict.py` | next-day volume predictions |
| Monitoring | `src/monitor.py` | `reports/monitoring_report.json` |
| Serving (local) | `app.py` | Streamlit dashboard |
| Quality and CI | `tests/`, `.github/workflows/ci.yml` | test results, CI artifacts |

## 16. How to install

```bash
cd public-signal-service-forecasting
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Python 3.11 is recommended.

## 17. How to download/build data

After placing the real daily-counts file (see section 10):

```bash
python -m src.download_data     # locate and validate the real input
python -m src.build_dataset     # build the processed dataset (fails if no real data)
```

To run the pipeline on the small committed real-schema sample (as CI does):

```bash
USE_SAMPLE_DATA=1 python -m src.build_dataset
```

## 18. How to train/evaluate

```bash
python -m src.train
python -m src.evaluate
python -m src.decision_simulation
python -m src.monitor
```

Each command builds any missing upstream artifact automatically.

## 19. How to run the dashboard

```bash
streamlit run app.py
```

The dashboard reports the active data mode (`real_nyc_311` or
`sample_real_schema`), warns clearly when sample data is in use, and shows
dataset statistics, feature-set and model comparisons, evaluation metrics, the
decision simulation, a prediction explorer, monitoring output, and an artifact
inventory. It degrades gracefully when artifacts are missing.

## 20. How to run tests

```bash
pytest
ruff check .
```

Tests run fully offline using the committed real-schema sample and never write
to the real `data/`, `models/`, `reports/`, or `figures/` directories.

## 21. CI/CD

GitHub Actions only discovers workflows at the repository root, so the active
workflow is `.github/workflows/ci.yml` at the monorepo root; it runs the project
with the working directory set to `public-signal-service-forecasting`. An
in-project copy is kept for standalone-repository portability. CI runs on push
and pull request (filtered to changes under the project folder or the root
workflow), uses Python 3.11, installs dependencies, runs `ruff check .` and
`pytest`, then builds the dataset, trains, evaluates, runs the decision
simulation and monitoring, and uploads `reports/` and `figures/` as artifacts.
CI uses the small real-schema sample (`USE_SAMPLE_DATA=1`) for speed and
reproducibility and requires no secrets and no API keys.

## 22. Responsible AI and limitations

This is a local-only research baseline on real public data. It uses no external
APIs requiring keys, no cloud services, no databases, and no personal data; all
quantities are aggregate daily counts. NYC 311 reflects reporting behaviour, not
true incidence (reporting bias). The staffing simulation is stylized and does
not represent real dispatch. The project makes no causal claims and is not
production-ready, not deployed, and not integrated with any external system. See
`docs/responsible_ai.md` and `docs/limitations.md`.

## 23. Future work

Potential extensions include adding genuinely external no-key public signals
(for example weather) with full documentation; probabilistic and hierarchical
forecasting; rolling-origin validation; formal statistical tests for forecast
and decision differences; a constrained-optimization formulation of the
allocation problem; and analysis of 311 reporting bias. See
`docs/research_brief.md`.

## 24. License

Released under the MIT License. See `LICENSE`.
