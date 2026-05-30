# Public Signal Service Forecasting

A reproducible public-data ML baseline for service-request forecasting and
staffing decision simulation.

## 1. Summary

This repository is a local, reproducible machine-learning baseline that tests
whether public external signals (weather, calendar, holidays, and operational
context) improve municipal service-request volume forecasts, and whether improved
forecasts translate into better staffing or dispatch allocation decisions. It
forecasts next-day request volume at the date x borough x complaint-group level
and pairs the forecasting study with a transparent staffing-allocation
simulation.

## 2. What this is and is not

- This **is** a research baseline: a baseline implementation, a scoping artifact,
  and a foundation for further experimentation.
- This is **not** just a forecasting app. It deliberately connects public-data
  feature augmentation, service-operations forecasting, forecast accuracy,
  operational decision quality, and reproducible ML engineering.
- This project is a research baseline.
- It uses public data if available, otherwise a deterministic synthetic fallback.
- It does not claim causal effects.
- It does not claim production readiness.
- Forecast-accuracy improvement is not the same as operational value; therefore
  the project includes a decision simulation.

## 3. Research motivation

Service organizations must allocate finite crews against uncertain, time-varying
demand. Forecasting daily request volume and allocating capacity against it is a
classic operations-management problem. A recurring question in
technology-and-operations-management and information-systems research is whether
*external* public signals add value beyond an organization's own internal
operational history, and whether any predictive gain actually improves decisions.

## 4. Research question

Do public external signals such as weather, calendar features, holidays, and
operational context improve service-request volume forecasts, and do those
forecast improvements translate into better staffing allocation decisions?

## 5. Why this is not just forecasting

A reduction in average forecast error does not automatically imply better
operational decisions, because decision quality depends on the loss structure of
the allocation problem, not only on symmetric average accuracy. To make this
explicit, the project includes a stylized staffing-allocation simulation and
compares an internal-only forecast policy, a public-signal augmented policy, and
an oracle (true-demand) benchmark.

## 6. Repository structure

```
public-signal-service-forecasting/
  app.py                      Streamlit dashboard
  README.md
  LICENSE
  requirements.txt
  pyproject.toml
  .gitignore
  data/
    raw/                      raw input data (generated/downloaded)
    processed/                processed modelling dataset
    metadata/                 data_source_report.json
  models/                     best_forecast_model.joblib
  reports/                    metrics, comparison, evaluation, simulation, monitoring
  figures/                    generated charts
  docs/                       research brief, architecture, data/model cards, etc.
  src/                        pipeline modules
  tests/                      pytest suite
  .github/workflows/ci.yml    CI pipeline
```

## 7. Data source strategy

A hybrid strategy is used:

1. Prefer real public data if it can be downloaded without authentication and
   without API keys. `python -m src.download_data` attempts a bounded, key-free
   download of a public NYC 311 export and archives a sample.
2. If a live download is unavailable, blocked, rate-limited, or unstable, the
   pipeline generates a deterministic synthetic-public-style dataset with the same
   schema and clearly labels it as a synthetic fallback.
3. The repository runs end to end without internet access once raw data is
   present.

## 8. Synthetic fallback disclosure

Aggregating the full heterogeneous public export into the exact daily
borough x complaint-group schema (with matched weather joins) is a non-trivial,
separately validated step. To keep the data contract honest and fully
reproducible offline, the modelling pipeline uses the deterministic synthetic
schema by default. **Unless `data/metadata/data_source_report.json` explicitly
records otherwise, the active data mode is `synthetic_fallback`.** Synthetic data
is generated with fixed seed 42 and does not represent real NYC 311 requests,
real weather, or real city operations. See `docs/data_card.md`.

## 9. Feature sets

- **Internal-only baseline:** `borough`, `complaint_group`, `day_of_week`,
  `month`, `is_weekend`, `is_holiday`, `request_lag_1`, `request_lag_7`,
  `rolling_mean_7`, `rolling_mean_14`.
- **Public-signal augmented:** all internal-only features plus `temp_c`,
  `precipitation_mm`, `wind_speed_kmh`, `severe_weather`, and `event_intensity`.

## 10. Model candidates

- Naive seasonal baseline (trailing 7-day rolling mean)
- Ridge regression
- Random forest regressor
- Gradient boosting regressor

Each non-naive model is trained on both feature sets.

## 11. Evaluation design

A strictly chronological split prevents leakage: the earliest 70% of dates are
used for training, the next 15% for validation, and the latest 15% for test. Lag
and rolling features are computed per cell using only past observations. Metrics
are MAE (primary), RMSE, MAPE (with safe zero handling), and R-squared. The best
model is chosen by validation MAE and refit on train+validation before final test
evaluation. See `docs/model_card.md`.

## 12. Decision simulation design

Each day, a fixed and intentionally scarce crew budget is allocated across the 35
cells in proportion to forecasted next-day demand using a largest-remainder rule.
Each crew provides a fixed capacity; unmet demand is the positive part of actual
demand minus allocated capacity. Three policies (baseline internal-only, augmented
public-signal, and oracle true-demand) are compared on total weighted unmet
demand, average service shortfall, high-demand coverage rate, and allocation
efficiency. See `docs/decision_simulation.md`.

## 13. ML lifecycle mapping

| Lifecycle stage | Module(s) | Artifact(s) |
|-----------------|-----------|-------------|
| Data acquisition | `src/download_data.py`, `src/generate_fallback_data.py` | `data/raw/`, `data/metadata/data_source_report.json` |
| Data processing | `src/build_dataset.py`, `src/features.py` | `data/processed/service_forecasting_dataset.csv` |
| Modelling | `src/train.py` | `models/best_forecast_model.joblib`, `reports/model_comparison.csv`, `reports/metrics.json` |
| Evaluation | `src/evaluate.py` | `reports/evaluation_report.json`, figures |
| Decision linkage | `src/decision_simulation.py` | `reports/decision_simulation_report.json`, figure |
| Inference | `src/predict.py` | next-day volume predictions |
| Monitoring | `src/monitor.py` | `reports/monitoring_report.json` |
| Serving (local) | `app.py` | Streamlit dashboard |
| Quality and CI | `tests/`, `.github/workflows/ci.yml` | test results, CI artifacts |

## 14. How to install

```bash
cd public-signal-service-forecasting
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Python 3.11 is recommended.

## 15. How to run locally

From the `public-signal-service-forecasting` directory:

```bash
python -m src.download_data        # optional; safe fallback if unavailable
python -m src.build_dataset
python -m src.train
python -m src.evaluate
python -m src.decision_simulation
python -m src.monitor
```

Each command will build any missing upstream artifact automatically.

## 16. How to run the dashboard

```bash
streamlit run app.py
```

The dashboard reports whether the active data is real or synthetic fallback,
shows dataset statistics, model and feature-set comparisons, evaluation metrics,
the decision simulation, a manual prediction form, monitoring output, and an
artifact inventory. It degrades gracefully when artifacts are missing.

## 17. How to run tests

```bash
pytest
ruff check .
```

Tests run fully offline and require no internet access.

## 18. CI/CD

A GitHub Actions workflow (`.github/workflows/ci.yml`) runs on push and pull
request using Python 3.11. It installs dependencies, runs `ruff check .` and
`pytest`, then runs the dataset build, training, evaluation, decision simulation,
and monitoring, and uploads `reports/` and `figures/` as build artifacts. It
requires no secrets and no API keys.

## 19. Responsible AI and limitations

This is a local-only research baseline. It uses no external APIs requiring keys,
no cloud services, no databases, and no personal data. The staffing simulation is
stylized and does not represent real dispatch. The project makes no causal claims
and is not production-ready, not deployed, and not integrated with any external
system. See `docs/responsible_ai.md` and `docs/limitations.md`.

## 20. Future work

Potential extensions include a fully documented real-data ingestion and join
pipeline; probabilistic and hierarchical forecasting; rolling-origin validation;
formal statistical tests for forecast and decision differences; a constrained
optimization formulation of the allocation problem; and signal-group ablations.
See `docs/research_brief.md`.

## 21. License

Released under the MIT License. See `LICENSE`.
