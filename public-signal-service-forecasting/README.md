# Public Signal Service Forecasting

This repository contains the reproducibility package for the paper **"From
Forecast Accuracy to Operational Value: Public Signal Augmentation for NYC 311
Service Demand."** It includes the code, derived summary outputs, figures, and
documentation needed to reproduce the reported results from the stated public
data sources.

The study is predictive and correlational. It uses real public NYC 311 and NOAA
data for 2022–2024; no synthetic data or synthetic weather is used for the
reported analysis. The decision layer is a stylized staffing-allocation
simulation, not a deployed dispatch system or a staffing-optimization tool.

## Paper

The final paper and the materials used to produce it are in `paper/`:

- `paper/output/public_signal_service_forecasting_final_submission.pdf` — final PDF.
- `paper/output/public_signal_service_forecasting_final_submission.docx` — final Word document.
- `paper/output/content.py`, `build_pdf.py`, `build_docx.py` — the single shared
  content source and the two generators that render the PDF and Word documents.
- `paper/references.bib` — the bibliography (all entries cited in the paper).
- `paper/number_audit.md` — every numeric claim traced to a committed output.
- `paper/figures/` — the figures used in the paper.

See `REPRODUCIBILITY.md` for the exact reproduction path.

## 1. Summary

The repository tests whether public external signals improve next-day forecasts
of NYC 311 service-request volume, and whether any improvement carries through to
a stylized staffing-allocation simulation. It forecasts the observed next-day
request count at the date × borough × complaint-group level using real NYC 311
data for 2022–2024, augmented with real NOAA Central Park weather, and pairs the
forecasting study with a transparent staffing-allocation simulation.

The headline result: the best model (a random forest on the calendar + weather
feature set) attains a held-out test MAE of 55.325 versus 71.848 for a naive
seasonal baseline (a 23.0% reduction). The augmented policy reduces weighted
unmet demand at all three tested crew budgets and closes 26.381% of the gap to an
observed-demand oracle at the baseline budget, with budget-dependent magnitude.

## 2. Claim boundaries

- Real NYC 311 public data is used for the reported results; the build fails with
  a clear error if valid real data is unavailable.
- No synthetic data or synthetic weather is used for any reported result.
- The continuous-integration sample is used only to test that the pipeline runs;
  it is not used to produce any reported paper result.
- The study is predictive and correlational and makes no causal claim.
- Forecast accuracy improvement is not the same as operational value; the
  stylized decision simulation uses no observed dispatch decisions, is not
  deployed, and is not a claim of real staffing optimization.
- Results apply to NYC and 2022–2024 only; weather is a single Central Park
  station used as a city-level proxy.

## 3. Research question

Can real NYC 311 service-request history, calendar features, and real weather
forecast the observed next-day request volume, and does improved forecast
accuracy translate into improved stylized staffing-allocation decisions?

## 4. Data source: NYC 311 Service Requests

The data is NYC 311 Service Requests from NYC Open Data (Socrata dataset
`erm2-nwe9`, "311 Service Requests from 2020 to Present"). The fields used are
`created_date`, `borough`, `complaint_type`, and `unique_key`. Records are
aggregated to observed daily counts by date, borough, and complaint group.

## 5. Study window: 2022–2024

Only calendar years 2022, 2023, and 2024 are used: no 2025 data, no pre-2022
data, and no partial years. From 9,851,452 raw records the preprocessing
procedure yields a 43,240-row date × borough × complaint-group panel.

## 6. Feature sets

- **Internal history:** `borough`, `complaint_group`, `request_lag_1`,
  `request_lag_7`, `rolling_mean_7`, `rolling_mean_14`, `rolling_std_7`,
  `rolling_std_14`.
- **Calendar:** internal history plus `is_weekend`, `is_holiday`, `day_of_week`,
  `month`, `quarter`, `year`, `day_of_year`, `week_of_year`, `is_month_start`,
  `is_month_end`.
- **Weather:** internal history plus real NOAA daily weather (`precipitation_mm`,
  `temp_max_c`, `temp_min_c`, `temp_avg_c`, `snowfall_mm`, `snow_depth_mm`,
  `wind_speed_ms`).
- **Calendar + weather:** internal history plus both calendar and real weather.

The weather layer is real NOAA NCEI Daily Summaries (GHCN-Daily) for the NYC
Central Park station (USW00094728), 2022–2024, 1,096 daily rows, used as a
single-station city-level proxy (a documented limitation). No transit or event
data is included. No synthetic weather is generated.

## 7. Models

- Naive seasonal baseline (trailing 7-day mean)
- Ridge regression
- Random forest regressor
- Gradient boosting regressor

Each non-naive model is trained on every available feature set. Hyperparameters
are listed in the paper (Appendix I).

## 8. Chronological validation

A strictly chronological split by date prevents leakage: the earliest 70% of
dates for training, the next 15% for validation, and the latest 15% for test.
Lag and rolling features are computed per cell using only past observations.
Metrics are MAE (primary), RMSE, MAPE (computed with the denominator floored at
one request), and R². The best model is chosen by validation MAE and refit on
train + validation before the final test evaluation. Five expanding-window
rolling-origin folds assess stability. See `docs/model_card.md`.

## 9. Decision simulation

Each day, a fixed crew budget is allocated across cells in proportion to
forecasted next-day demand using a largest-remainder rule. Each crew provides a
fixed capacity; unmet demand is the positive part of actual demand minus
allocated capacity, with higher weights for Public Safety, Water, and Traffic.
The decision simulation compares the internal-history policy, the calendar +
weather policy, and an observed-demand oracle benchmark (which allocates using
the observed realized next-day request volume). See `docs/decision_simulation.md`.

## 10. Repository structure

```
public-signal-service-forecasting/
  app.py                       Streamlit dashboard
  README.md
  REPRODUCIBILITY.md
  CITATION.cff
  LICENSE
  requirements.txt
  pyproject.toml
  scripts/
    aggregate_nyc_311_local.py  Local reducer: 36 monthly exports -> daily counts
  data/
    raw/                       real daily counts, metadata, and CI sample
    processed/                 processed modelling dataset (regenerable)
    metadata/                  data and weather source reports
  models/                      trained model (regenerable)
  reports/                     metrics, comparison, evaluation, simulation, robustness
  figures/                     generated charts
  docs/                        architecture, data/model cards, decision sim, limitations
  paper/                       final paper, generators, references, figures, number audit
  src/                         pipeline modules
  tests/                       pytest suite
  .github/workflows/ci.yml     pipeline smoke-test on the committed sample
```

## 11. Install

```bash
cd public-signal-service-forecasting
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Python 3.11 is recommended.

## 12. Reproduce the reported results

See `REPRODUCIBILITY.md` for the full path, including the expected row counts and
headline metrics. In brief, after placing the public NYC 311 and NOAA inputs:

```bash
python -m src.download_data
python -m src.build_dataset
python -m src.train
python -m src.evaluate
python -m src.decision_simulation
python -m src.decision_sensitivity
python -m src.rolling_validation
python -m src.robustness_analysis
python -m src.practical_significance
```

The headline paper numbers are read from the committed outputs in `reports/` and
the final figures in `figures/` and `paper/figures/`.

## 13. Tests

```bash
pytest
```

Tests run fully offline using the committed real-schema sample and never write to
the real `data/`, `models/`, `reports/`, or `figures/` directories. The sample is
used only to exercise the pipeline; it produces no reported paper result.

## 14. License

Released under the MIT License. See `LICENSE`.
