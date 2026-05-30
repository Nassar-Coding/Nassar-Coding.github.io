"""Central configuration constants for the Public Signal Service Forecasting baseline.

All paths are resolved relative to the project root so that scripts can be run
from the repository root without hard-coded personal paths.
"""
from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]

DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DIR: Path = DATA_DIR / "raw"
PROCESSED_DIR: Path = DATA_DIR / "processed"
METADATA_DIR: Path = DATA_DIR / "metadata"

MODELS_DIR: Path = PROJECT_ROOT / "models"
REPORTS_DIR: Path = PROJECT_ROOT / "reports"
FIGURES_DIR: Path = PROJECT_ROOT / "figures"

# ---------------------------------------------------------------------------
# Artifact file names
# ---------------------------------------------------------------------------
RAW_DATA_FILE: Path = RAW_DIR / "service_requests_raw.csv"
PROCESSED_DATA_FILE: Path = PROCESSED_DIR / "service_forecasting_dataset.csv"
DATA_SOURCE_REPORT: Path = METADATA_DIR / "data_source_report.json"

BEST_MODEL_FILE: Path = MODELS_DIR / "best_forecast_model.joblib"
MODEL_COMPARISON_FILE: Path = REPORTS_DIR / "model_comparison.csv"
METRICS_FILE: Path = REPORTS_DIR / "metrics.json"
EVALUATION_REPORT_FILE: Path = REPORTS_DIR / "evaluation_report.json"
DECISION_SIMULATION_REPORT_FILE: Path = REPORTS_DIR / "decision_simulation_report.json"
MONITORING_REPORT_FILE: Path = REPORTS_DIR / "monitoring_report.json"

FIG_FORECAST_ERROR: Path = FIGURES_DIR / "forecast_error_by_model.png"
FIG_INTERNAL_VS_AUGMENTED: Path = FIGURES_DIR / "internal_vs_augmented_mae.png"
FIG_DECISION_QUALITY: Path = FIGURES_DIR / "decision_quality_comparison.png"

# ---------------------------------------------------------------------------
# Domain values
# ---------------------------------------------------------------------------
BOROUGHS: list[str] = [
    "Manhattan",
    "Brooklyn",
    "Queens",
    "Bronx",
    "Staten Island",
]

COMPLAINT_GROUPS: list[str] = [
    "Sanitation",
    "Noise",
    "Street Condition",
    "Water",
    "Housing",
    "Traffic",
    "Public Safety",
]

# Higher weight complaint groups for the weighted unmet-demand decision metric.
COMPLAINT_GROUP_WEIGHTS: dict[str, float] = {
    "Sanitation": 1.0,
    "Noise": 1.0,
    "Street Condition": 1.0,
    "Water": 1.5,
    "Housing": 1.0,
    "Traffic": 1.5,
    "Public Safety": 2.0,
}

# ---------------------------------------------------------------------------
# Synthetic fallback generation parameters
# ---------------------------------------------------------------------------
RANDOM_SEED: int = 42
FALLBACK_START_DATE: str = "2021-01-01"
FALLBACK_NUM_DAYS: int = 1100  # 1100 days x 35 cells = 38,500 rows (> 10,000)

# ---------------------------------------------------------------------------
# Public download configuration (no authentication, no API key)
# ---------------------------------------------------------------------------
# NYC Open Data 311 export endpoint. Network access is optional; if the
# download fails for any reason the pipeline falls back to synthetic data.
NYC_311_CSV_URL: str = (
    "https://data.cityofnewyork.us/api/views/erm2-nwe9/rows.csv?accessType=DOWNLOAD"
)
DOWNLOAD_TIMEOUT_SECONDS: int = 30

# ---------------------------------------------------------------------------
# Feature set definitions
# ---------------------------------------------------------------------------
CATEGORICAL_FEATURES: list[str] = ["borough", "complaint_group"]

INTERNAL_NUMERIC_FEATURES: list[str] = [
    "day_of_week",
    "month",
    "is_weekend",
    "is_holiday",
    "request_lag_1",
    "request_lag_7",
    "rolling_mean_7",
    "rolling_mean_14",
]

PUBLIC_SIGNAL_FEATURES: list[str] = [
    "temp_c",
    "precipitation_mm",
    "wind_speed_kmh",
    "severe_weather",
    "event_intensity",
]

# Feature set name -> ordered list of feature columns.
FEATURE_SETS: dict[str, list[str]] = {
    "internal_only": CATEGORICAL_FEATURES + INTERNAL_NUMERIC_FEATURES,
    "augmented": CATEGORICAL_FEATURES
    + INTERNAL_NUMERIC_FEATURES
    + PUBLIC_SIGNAL_FEATURES,
}

TARGET_COLUMN: str = "request_volume_next_day"

PROCESSED_COLUMNS: list[str] = [
    "date",
    "borough",
    "complaint_group",
    "request_volume",
    "request_volume_next_day",
    "temp_c",
    "precipitation_mm",
    "wind_speed_kmh",
    "severe_weather",
    "event_intensity",
    "is_weekend",
    "is_holiday",
    "day_of_week",
    "month",
    "request_lag_1",
    "request_lag_7",
    "rolling_mean_7",
    "rolling_mean_14",
]

# ---------------------------------------------------------------------------
# Validation split fractions (chronological)
# ---------------------------------------------------------------------------
TRAIN_FRACTION: float = 0.70
VALIDATION_FRACTION: float = 0.15
# Test fraction is the remaining 0.15.

# ---------------------------------------------------------------------------
# Decision simulation parameters
# ---------------------------------------------------------------------------
REQUESTS_PER_CREW: int = 25
TOTAL_CREWS: int = 60
MIN_CREWS_PER_CELL: int = 0
HIGH_DEMAND_QUANTILE: float = 0.75

# ---------------------------------------------------------------------------
# Primary selection metric
# ---------------------------------------------------------------------------
PRIMARY_METRIC: str = "mae"
