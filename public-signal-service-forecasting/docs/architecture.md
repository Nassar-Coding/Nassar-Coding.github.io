# Architecture

This document describes the components, pipelines, and artifact flow of the
Public Signal Service Forecasting baseline. The system is local-only and runs
end to end without external services once raw data is present.

## Component overview

| Component | Module | Responsibility |
|-----------|--------|----------------|
| Configuration | `src/config.py` | Central constants: paths, domain values, feature sets, split fractions, simulation parameters |
| Utilities | `src/utils.py` | Logging, JSON IO, directory setup, metric functions |
| Data acquisition | `src/download_data.py` | Best-effort, key-free public download with safe fallback |
| Synthetic generation | `src/generate_fallback_data.py` | Deterministic synthetic-public-style raw data (seed 42) |
| Dataset build | `src/build_dataset.py` | Calendar, lag, rolling features and next-day target |
| Feature engineering | `src/features.py` | Feature-set definitions, calendar/holiday logic, preprocessing |
| Training | `src/train.py` | Chronological split, model/feature-set comparison, model selection |
| Evaluation | `src/evaluate.py` | Held-out test metrics and comparison figures |
| Decision simulation | `src/decision_simulation.py` | Stylized staffing allocation and decision-quality metrics |
| Inference | `src/predict.py` | Single-record next-day volume prediction |
| Monitoring | `src/monitor.py` | Compares current model MAE to the naive baseline |
| Dashboard | `app.py` | Local Streamlit research dashboard |

## Data pipeline

```mermaid
flowchart TD
    A[download_data] -->|success| B[raw public sample archived]
    A -->|failure or unavailable| C[generate_fallback_data]
    B --> C
    C --> D[raw CSV: data/raw]
    D --> E[build_dataset]
    E --> F[calendar features]
    F --> G[lag and rolling features per group]
    G --> H[next-day target]
    H --> I[drop warmup and edge rows]
    I --> J[processed CSV: data/processed]
    J --> K[data_source_report.json: data/metadata]
```

## Modeling pipeline

```mermaid
flowchart TD
    A[processed dataset] --> B[chronological split 70/15/15]
    B --> C[internal-only feature matrix]
    B --> D[augmented feature matrix]
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
    B --> C[train internal and augmented forecasters]
    C --> D[forecast test days]
    D --> E[allocate fixed crew budget per day]
    E --> F[baseline policy: internal forecast]
    E --> G[augmented policy: public-signal forecast]
    E --> H[oracle policy: true demand benchmark]
    F --> I[decision-quality metrics]
    G --> I
    H --> I
    I --> J[decision_simulation_report.json and figure]
```

## Artifact flow

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
    RM --> F2[figures/internal_vs_augmented_mae.png]
    DS --> F3[figures/decision_quality_comparison.png]
```

## Execution order

The canonical end-to-end order is:

1. `python -m src.download_data` (optional; safe fallback if unavailable)
2. `python -m src.build_dataset`
3. `python -m src.train`
4. `python -m src.evaluate`
5. `python -m src.decision_simulation`
6. `python -m src.monitor`

Each downstream module will build any missing upstream artifact automatically,
so individual commands can also be run in isolation.
