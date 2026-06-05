# Reproducibility

This document describes how to reproduce the results reported in the paper
**"From Forecast Accuracy to Operational Value: Public Signal Augmentation for
NYC 311 Service Demand."**

## Public data sources

- **NYC 311 Service Requests** — NYC Open Data, Socrata dataset `erm2-nwe9`
  ("311 Service Requests from 2020 to Present"):
  https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9
  Fields used: `created_date`, `borough`, `complaint_type`, `unique_key`.
- **NOAA NCEI Daily Summaries (GHCN-Daily)** — station `USW00094728`
  (NY City Central Park):
  https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily

## Study window and expected row counts

- Study window: **2022-01-01 to 2024-12-31** (calendar years 2022–2024 only).
- Raw NYC 311 records read: **9,851,452**.
- Processed panel: **43,240** rows at the date × borough × complaint-group level
  (5 boroughs × 8 complaint groups), observed range 2022-01-15 to 2024-12-30.
- Weather: **1,096** daily rows, 7 variables.

## Environment

- Python 3.11.
- Install dependencies: `pip install -r requirements.txt`.
- Fixed random seed (42) throughout.

## Data preparation

The full multi-million-row 311 export is large, so the supported path reduces the
36 monthly exports to observed daily counts locally:

```bash
python scripts/aggregate_nyc_311_local.py --input-dir <folder_of_monthly_csvs>
```

Place the resulting `nyc_311_daily_counts_2022_2024.csv` at
`data/raw/nyc_311_daily_counts_2022_2024.csv`. Provide the NOAA Central Park
export as described in `docs/data_card.md`.

## Command sequence

```bash
python -m src.download_data            # locate and validate the real input
python -m src.build_dataset            # build the processed dataset
python -m src.train                    # train models, select by validation MAE
python -m src.evaluate                 # held-out test metrics and figures
python -m src.decision_simulation      # baseline-budget decision simulation
python -m src.decision_sensitivity     # crew-budget sensitivity
python -m src.rolling_validation       # five-fold rolling-origin validation
python -m src.robustness_analysis      # per-borough and per-complaint-group
python -m src.practical_significance   # consistency summary
```

## Expected headline metrics

- Best model: random forest on the **calendar + weather** feature set.
- Held-out test MAE **55.325** vs naive seasonal **71.848** (a **23.0%** reduction);
  RMSE 177.476, MAPE 27.469%, R² 0.648.
- Rolling-origin: calendar augmentation lowers MAE in all 5 of 5 folds for every
  model; calendar + weather random forest mean fold MAE **47.497**.
- Robustness: improvement holds for all 5 boroughs and all 8 complaint groups.
- Decision (baseline budget, 135 crews): calendar + weather reduces weighted
  unmet demand by **1.886%** and closes **26.381%** of the gap to the
  observed-demand oracle; the effect is budget-dependent across the three tested
  budgets.

## Where outputs are stored

- Numeric outputs: `reports/` (CSV and JSON).
- Figures: `figures/` (pipeline outputs) and `paper/figures/` (paper versions).
- Final paper: `paper/output/` (PDF and Word) with `paper/number_audit.md`
  tracing every numeric claim to a committed output.

## Data integrity statements

- **No synthetic data or synthetic weather is used for any reported result.** If
  valid real data cannot be located or validated, the build fails with a clear
  error.
- The continuous-integration sample (`USE_SAMPLE_DATA=1`) is used only to test
  that the pipeline executes; it is **not** used to produce any reported paper
  result.
