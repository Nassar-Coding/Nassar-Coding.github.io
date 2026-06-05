# Architecture

This document describes the components, pipelines, and output flow of the
Public Signal Service Forecasting baseline. The system is local-only and runs
end to end without external services once the real input data is present.

## Component overview

| Component | Module | Responsibility |
|-----------|--------|----------------|
| Configuration | `src/config.py` | Central constants: paths, domain values, complaint mapping, feature sets, split fractions, simulation parameters |
| Utilities | `src/utils.py` | Logging, JSON IO, directory setup, metric functions |
| Local aggregation | `scripts/aggregate_nyc_311_local.py` | Reduce the 36 monthly NYC 311 exports to observed daily counts (run locally) |
| Data location | `src/download_data.py` | Locate and validate the real daily-counts input; fail clearly if absent (no synthetic fallback) |
| Dataset build | `src/build_dataset.py` | Validate real input, regularise the panel, add calendar/lag/rolling features and the observed next-day target |
| Feature engineering | `src/features.py` | Feature-set definitions, calendar/holiday logic, leakage-safe lags, preprocessing |
| Training | `src/train.py` | Chronological split, model/feature-set comparison, model selection |
| Evaluation | `src/evaluate.py` | Held-out test metrics and comparison figures |
| Decision simulation | `src/decision_simulation.py` | Stylized staffing allocation and decision-quality metrics |
| Inference | `src/predict.py` | Single-record next-day volume prediction |
| Monitoring | `src/monitor.py` | Compares current model MAE to the naive baseline |
| Dashboard | `app.py` | Local Streamlit research dashboard |

## Data pipeline

```mermaid
flowchart TD
    M[36 monthly NYC 311 exports] -->|scripts/aggregate_nyc_311_local.py local| N[daily counts CSV: data/raw]
    N --> A[download_data: locate and validate]
    A -->|valid real or sample input| E[build_dataset]
    A -->|no valid input| X[fail clearly: no synthetic fallback]
    E --> P[regularise panel: missing day = zero]
    P --> F[calendar features]
    F --> G[lag and rolling features per cell]
    G --> H[observed next-day target]
    H --> I[drop warmup and edge rows]
    I --> J[processed CSV: data/processed]
    J --> K[data_source_report.json: data/metadata]
```

## Modeling pipeline

```mermaid
flowchart TD
    A[processed dataset] --> B[chronological split 70/15/15 by date]
    B --> C[internal-historical feature matrix]
    B --> D[calendar-augmented feature matrix]
    C --> E[Ridge, RandomForest, GradientBoosting]
    D --> E
    B --> F[naive seasonal baseline]
    E --> G[validation MAE]
    F --> G
    G --> H[select best by validation MAE]
    H --> I[refit on train+validation]
    I --> J[best_forecast_model.joblib]
    G --> K[model_comparison.csv and metrics.json]
```

## Decision simulation pipeline

```mermaid
flowchart TD
    A[processed dataset] --> B[chronological split]
    B --> C[train internal-historical and calendar-augmented forecasters]
    C --> D[forecast test days]
    D --> E[allocate fixed crew budget per day]
    E --> F[internal-history policy]
    E --> G[calendar + weather policy]
    E --> H[observed-demand oracle benchmark]
    F --> I[decision-quality metrics]
    G --> I
    H --> I
    I --> J[decision_simulation_report.json and figure]
```

## Output flow

```mermaid
flowchart LR
    R[data/raw] --> P[data/processed]
    P --> M[models/best_forecast_model.joblib]
    P --> RM[reports/metrics.json]
    P --> MC[reports/model_comparison.csv]
    M --> ER[reports/evaluation_report.json]
    M --> DS[reports/decision_simulation_report.json]
    ER --> MO[reports/monitoring_report.json]
    RM --> F1[figures/forecast_error_by_model.png]
    RM --> F2[figures/internal_vs_calendar_augmented_mae.png]
    DS --> F3[figures/decision_quality_comparison.png]
    ER --> F4[figures/forecast_actual_vs_predicted.png]
```

## Execution order

The canonical end-to-end order is:

1. `python -m src.download_data` (locate and validate the real input)
2. `python -m src.build_dataset`
3. `python -m src.train`
4. `python -m src.evaluate`
5. `python -m src.decision_simulation`
6. `python -m src.monitor`

Each downstream module will build any missing upstream output automatically,
so individual commands can also be run in isolation. There is no synthetic
fallback: if no valid real input is present, the build fails with a specific
error.
