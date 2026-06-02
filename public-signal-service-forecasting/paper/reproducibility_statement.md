# Reproducibility Statement

- Repository: `public-signal-service-forecasting` (within the
  `Nassar-Coding/Nassar-Coding.github.io` repository).
- Branch: `research/real-nyc-311-upgrade`.
- Python: 3.11 (see `pyproject.toml`; CI uses Python 3.11).
- Dependencies: pinned in `requirements.txt` (pandas, numpy, scikit-learn,
  matplotlib, joblib, streamlit; dev: pytest, ruff). No API keys, no secrets.

## Install

```
cd public-signal-service-forecasting
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Build data, train, evaluate, robustness

```
python -m src.weather                 # ingest real NOAA weather -> weather table
python -m src.build_dataset           # build processed dataset (joins weather)
python -m src.train                   # train all model/feature-set combinations
python -m src.evaluate                # held-out test metrics and figures
python -m src.decision_simulation     # stylized staffing simulation
python -m src.monitor                 # MAE-vs-naive monitoring
python -m src.rolling_validation      # 5-fold rolling-origin validation
python -m src.robustness_analysis     # borough and complaint-group robustness
python -m src.decision_sensitivity    # crew-budget sensitivity
python -m src.practical_significance  # practical-significance summary
```

## Quality gate

```
ruff check .
pytest
```

## CI status note

A repository-root GitHub Actions workflow (`.github/workflows/ci.yml`) runs the
project with the working directory set to `public-signal-service-forecasting`,
on Python 3.11, in sample mode (`USE_SAMPLE_DATA=1`), executing ruff, pytest, and
the pipeline, and uploading reports and figures as artifacts. It requires no
secrets and no API keys. The latest-commit CI conclusion should be confirmed on
the repository Actions tab before relying on it.

## Sample-mode CI explanation

CI runs in sample mode using small committed real-schema samples
(`data/raw/nyc_311_daily_counts_sample.csv`,
`data/raw/nyc_central_park_weather_sample.csv`) so the pipeline runs quickly and
offline. Research-mode numbers in this paper are produced from the full real
inputs, not the CI sample. Tests redirect all artifact paths to a temporary
directory, so running the test suite does not overwrite the committed real
artifacts.

## Raw data note

The large raw monthly NYC 311 exports are not committed. The committed inputs are
the aggregated real daily counts (`data/raw/nyc_311_daily_counts_2022_2024.csv`)
and the real NOAA weather export
(`data/raw/nyc_central_park_weather_2022_2024.csv`), plus the two small CI
samples. The trained model binary (`models/`) is not committed (large,
regenerable). The processed dataset is regenerable from the committed inputs.

## Exact artifacts used in this paper

`reports/model_comparison.csv`, `reports/metrics.json`,
`reports/evaluation_report.json`, `reports/rolling_validation_summary.json`,
`reports/rolling_validation_report.csv`, `reports/borough_performance.csv`,
`reports/complaint_group_performance.csv`,
`reports/decision_simulation_report.json`,
`reports/decision_sensitivity_report.csv`,
`reports/decision_sensitivity_summary.json`,
`reports/practical_significance_summary.json`, `reports/monitoring_report.json`,
`data/metadata/data_source_report.json`,
`data/metadata/weather_source_report.json`, and `figures/*.png`.
