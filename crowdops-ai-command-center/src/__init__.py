"""CrowdOps AI Command Center.

A local, no-API AI engineering lifecycle demo for crowd risk prediction.

This package contains the full machine learning lifecycle:
    - generate_data : reproducible synthetic dataset generation
    - data          : data loading and validation
    - features      : feature engineering pipeline (scikit-learn)
    - train         : model training and selection
    - evaluate      : model evaluation reports
    - predict       : single-record inference
    - monitor       : lightweight model-health monitoring

Everything runs locally. No external APIs, keys, cloud, or databases.
"""

__version__ = "1.0.0"

# Canonical schema shared across modules so that data generation, validation,
# feature engineering, and the Streamlit app all agree on the contract.
TARGET_COLUMN = "risk_level"

RISK_LEVELS = ["Low", "Medium", "High"]

ZONES = [
    "Gate A",
    "Gate B",
    "Main Hall",
    "Parking Area",
    "Emergency Exit",
    "Food Court",
    "Service Corridor",
    "Prayer Area",
]

EVENT_TYPES = [
    "Normal Day",
    "Peak Hour",
    "Special Event",
    "Maintenance Window",
    "Weather Disruption",
]

# Feature groups used by the scikit-learn ColumnTransformer.
NUMERIC_FEATURES = [
    "crowd_count",
    "zone_capacity",
    "density_ratio",
    "avg_wait_time",
    "entry_rate",
    "exit_rate",
    "temperature",
    "hour",
    "day_of_week",
]

CATEGORICAL_FEATURES = ["zone", "event_type"]

# Full ordered list of columns expected in data/crowd_ops.csv.
REQUIRED_COLUMNS = [
    "timestamp",
    "zone",
    "crowd_count",
    "zone_capacity",
    "density_ratio",
    "avg_wait_time",
    "entry_rate",
    "exit_rate",
    "temperature",
    "hour",
    "day_of_week",
    "event_type",
    "risk_level",
]

# Single source of truth for the random seed -> reproducible everywhere.
RANDOM_SEED = 42

# ---------------------------------------------------------------------------
# Project paths (pathlib-based, resolved relative to this package).
# Using a single set of path constants keeps every script runnable from the
# project root regardless of the current working directory.
# ---------------------------------------------------------------------------
from pathlib import Path  # noqa: E402  (kept here so paths stay with the schema)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

DATA_PATH = DATA_DIR / "crowd_ops.csv"
MODEL_PATH = MODELS_DIR / "crowd_risk_model.joblib"
METRICS_PATH = REPORTS_DIR / "metrics.json"
MODEL_SUMMARY_PATH = REPORTS_DIR / "model_summary.md"
EVALUATION_PATH = REPORTS_DIR / "evaluation.json"
MONITORING_PATH = REPORTS_DIR / "monitoring_report.json"

