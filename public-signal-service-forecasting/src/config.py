"""Central configuration constants for the Public Signal Service Forecasting baseline.

Research mode uses real NYC 311 Service Requests data for calendar years
2022-2024. All paths are resolved relative to the project root so that scripts
can be run from the repository root without hard-coded personal paths.
"""
from __future__ import annotations

import os
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
# Input data files
# ---------------------------------------------------------------------------
# Pre-aggregated real daily counts (date, borough, complaint_group,
# request_volume) for the full study window. This is the research-mode input.
DAILY_COUNTS_FILE: Path = RAW_DIR / "nyc_311_daily_counts_2022_2024.csv"
DAILY_COUNTS_META_FILE: Path = RAW_DIR / "nyc_311_daily_counts_2022_2024.meta.json"

# Optional manual raw export. If present, build_dataset can aggregate it
# directly (date, borough, complaint_type-level records).
MANUAL_RAW_FILE: Path = RAW_DIR / "nyc_311_2022_2024.csv"

# Small committed real-schema sample used for CI and tests only. It preserves
# the real schema and observed-count logic but is not research data.
SAMPLE_DAILY_COUNTS_FILE: Path = RAW_DIR / "nyc_311_daily_counts_sample.csv"

# ---------------------------------------------------------------------------
# Artifact file names
# ---------------------------------------------------------------------------
PROCESSED_DATA_FILE: Path = PROCESSED_DIR / "service_forecasting_dataset.csv"
DATA_SOURCE_REPORT: Path = METADATA_DIR / "data_source_report.json"

BEST_MODEL_FILE: Path = MODELS_DIR / "best_forecast_model.joblib"
MODEL_COMPARISON_FILE: Path = REPORTS_DIR / "model_comparison.csv"
METRICS_FILE: Path = REPORTS_DIR / "metrics.json"
EVALUATION_REPORT_FILE: Path = REPORTS_DIR / "evaluation_report.json"
DECISION_SIMULATION_REPORT_FILE: Path = REPORTS_DIR / "decision_simulation_report.json"
MONITORING_REPORT_FILE: Path = REPORTS_DIR / "monitoring_report.json"

# Robustness package artifacts (final closure pass).
ROLLING_VALIDATION_REPORT_FILE: Path = REPORTS_DIR / "rolling_validation_report.csv"
ROLLING_VALIDATION_SUMMARY_FILE: Path = REPORTS_DIR / "rolling_validation_summary.json"
COMPLAINT_GROUP_PERFORMANCE_FILE: Path = REPORTS_DIR / "complaint_group_performance.csv"
BOROUGH_PERFORMANCE_FILE: Path = REPORTS_DIR / "borough_performance.csv"
DECISION_SENSITIVITY_REPORT_FILE: Path = REPORTS_DIR / "decision_sensitivity_report.csv"
DECISION_SENSITIVITY_SUMMARY_FILE: Path = REPORTS_DIR / "decision_sensitivity_summary.json"
PRACTICAL_SIGNIFICANCE_FILE: Path = REPORTS_DIR / "practical_significance_summary.json"

FIG_FORECAST_ERROR: Path = FIGURES_DIR / "forecast_error_by_model.png"
FIG_INTERNAL_VS_AUGMENTED: Path = FIGURES_DIR / "internal_vs_calendar_augmented_mae.png"
FIG_DECISION_QUALITY: Path = FIGURES_DIR / "decision_quality_comparison.png"
FIG_ACTUAL_VS_PREDICTED: Path = FIGURES_DIR / "forecast_actual_vs_predicted.png"
FIG_ROLLING_VALIDATION: Path = FIGURES_DIR / "rolling_validation_mae.png"
FIG_COMPLAINT_GROUP_MAE: Path = FIGURES_DIR / "complaint_group_mae.png"
FIG_BOROUGH_MAE: Path = FIGURES_DIR / "borough_mae.png"
FIG_DECISION_SENSITIVITY: Path = FIGURES_DIR / "decision_sensitivity.png"

# Decision sensitivity crew-budget settings (scarce / moderate / generous).
# Calibrated relative to mean daily demand (~8,977 next-day requests across
# 40 cells) with REQUESTS_PER_CREW = 50.
DECISION_CREW_SETTINGS: dict[str, int] = {
    "scarce": 100,
    "moderate": 160,
    "generous": 220,
}

# ---------------------------------------------------------------------------
# Study window (real NYC 311 data; 2022-2024 only)
# ---------------------------------------------------------------------------
STUDY_START_DATE: str = "2022-01-01"
STUDY_END_DATE: str = "2024-12-31"

DATA_SOURCE_NAME: str = "NYC 311 Service Requests (NYC Open Data)"
DATA_SOURCE_URL: str = "https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9"

# ---------------------------------------------------------------------------
# Data mode handling
# ---------------------------------------------------------------------------
# Research mode uses the full real aggregated counts. CI/test mode uses the
# committed real-schema sample. Mode is selected by environment variable so CI
# can opt into the small sample without code changes.
DATA_MODE_REAL: str = "real_nyc_311"
DATA_MODE_SAMPLE: str = "sample_real_schema"


def use_sample_data() -> bool:
    """Return True if the environment requests CI/sample mode."""
    if os.environ.get("USE_SAMPLE_DATA", "").strip() in {"1", "true", "True"}:
        return True
    if os.environ.get("DATA_MODE", "").strip() == DATA_MODE_SAMPLE:
        return True
    return False


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

# Complaint groups produced by the deterministic complaint_type mapping,
# including the catch-all "Other" group.
COMPLAINT_GROUPS: list[str] = [
    "Noise",
    "Sanitation",
    "Street Condition",
    "Water",
    "Housing",
    "Traffic",
    "Public Safety",
    "Other",
]

# Higher weight complaint groups for the weighted unmet-demand decision metric.
COMPLAINT_GROUP_WEIGHTS: dict[str, float] = {
    "Noise": 1.0,
    "Sanitation": 1.0,
    "Street Condition": 1.0,
    "Water": 1.5,
    "Housing": 1.0,
    "Traffic": 1.5,
    "Public Safety": 2.0,
    "Other": 1.0,
}

# ---------------------------------------------------------------------------
# Complaint type -> complaint group mapping
# ---------------------------------------------------------------------------
# Deterministic substring rules evaluated in order; first match wins. Housing
# precedes Water so that "HEAT/HOT WATER" is classified as Housing rather than
# being captured by the "WATER" substring under Water. Documented in
# docs/data_card.md. This mirrors scripts/aggregate_nyc_311_local.py so manual
# raw exports map identically to the pre-aggregated counts.
COMPLAINT_GROUP_RULES: list[tuple[str, list[str]]] = [
    ("Noise", ["NOISE", "LOUD"]),
    (
        "Housing",
        [
            "HEAT/HOT WATER",
            "HEAT",
            "HOT WATER",
            "PLUMBING",
            "PAINT",
            "PLASTER",
            "APPLIANCE",
            "DOOR",
            "WINDOW",
            "ELECTRIC",
            "FLOORING",
            "STAIRS",
            "ELEVATOR",
            "MOLD",
            "GENERAL CONSTRUCTION",
            "HOUSING",
            "APARTMENT",
            "UNSANITARY CONDITION",
            "OUTSIDE BUILDING",
        ],
    ),
    (
        "Sanitation",
        [
            "SANITATION",
            "DIRTY",
            "MISSED COLLECTION",
            "LITTER",
            "GARBAGE",
            "RECYCLING",
            "WASTE",
            "DUMPING",
            "GRAFFITI",
            "RODENT",
            "OVERFLOWING",
        ],
    ),
    (
        "Street Condition",
        [
            "STREET CONDITION",
            "STREET LIGHT",
            "POTHOLE",
            "SIDEWALK",
            "CURB",
            "ROAD",
            "STREET SIGN",
            "TRAFFIC SIGNAL",
            "HIGHWAY",
        ],
    ),
    (
        "Water",
        ["WATER", "SEWER", "HYDRANT", "LEAK", "FLOOD", "DRAINAGE", "CATCH BASIN"],
    ),
    (
        "Traffic",
        [
            "ILLEGAL PARKING",
            "BLOCKED DRIVEWAY",
            "TRAFFIC",
            "PARKING",
            "ABANDONED VEHICLE",
            "DERELICT VEHICLE",
            "DRIVEWAY",
        ],
    ),
    (
        "Public Safety",
        [
            "ILLEGAL FIREWORKS",
            "DRUG",
            "WEAPON",
            "ASSAULT",
            "SAFETY",
            "EMERGENCY",
            "ENCAMPMENT",
            "HOMELESS",
            "ANIMAL ABUSE",
            "DISORDERLY",
            "URINATING",
            "PANHANDLING",
        ],
    ),
]

# Canonical NYC boroughs keyed by upper-cased raw value.
BOROUGH_NORMALISATION: dict[str, str] = {
    "MANHATTAN": "Manhattan",
    "BROOKLYN": "Brooklyn",
    "QUEENS": "Queens",
    "BRONX": "Bronx",
    "STATEN ISLAND": "Staten Island",
}

# Raw fields required from a manual NYC 311 export.
RAW_REQUIRED_COLUMNS: list[str] = [
    "unique_key",
    "created_date",
    "borough",
    "complaint_type",
]

# ---------------------------------------------------------------------------
# Feature set definitions
# ---------------------------------------------------------------------------
CATEGORICAL_FEATURES: list[str] = ["borough", "complaint_group"]

# Internal historical features: lagged and rolling statistics of the series.
INTERNAL_HISTORICAL_FEATURES: list[str] = [
    "request_lag_1",
    "request_lag_7",
    "rolling_mean_7",
    "rolling_mean_14",
    "rolling_std_7",
    "rolling_std_14",
]

# Calendar features derived deterministically from the date.
CALENDAR_FEATURES: list[str] = [
    "is_weekend",
    "is_holiday",
    "day_of_week",
    "month",
    "quarter",
    "year",
    "day_of_year",
    "week_of_year",
    "is_month_start",
    "is_month_end",
]

# Feature set name -> ordered list of feature columns.
FEATURE_SETS: dict[str, list[str]] = {
    "internal_historical": CATEGORICAL_FEATURES + INTERNAL_HISTORICAL_FEATURES,
    "calendar_augmented": CATEGORICAL_FEATURES
    + INTERNAL_HISTORICAL_FEATURES
    + CALENDAR_FEATURES,
}

TARGET_COLUMN: str = "request_volume_next_day"

PROCESSED_COLUMNS: list[str] = [
    "date",
    "borough",
    "complaint_group",
    "request_volume",
    "request_volume_next_day",
    "is_weekend",
    "is_holiday",
    "day_of_week",
    "month",
    "quarter",
    "year",
    "request_lag_1",
    "request_lag_7",
    "rolling_mean_7",
    "rolling_mean_14",
    "rolling_std_7",
    "rolling_std_14",
    "day_of_year",
    "week_of_year",
    "is_month_start",
    "is_month_end",
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
# Each crew handles REQUESTS_PER_CREW requests per day; the fixed crew budget is
# intentionally scarce relative to typical daily demand so that allocation
# quality has a measurable effect.
REQUESTS_PER_CREW: int = 50
TOTAL_CREWS: int = 135
MIN_CREWS_PER_CELL: int = 0
HIGH_DEMAND_QUANTILE: float = 0.75

# ---------------------------------------------------------------------------
# Random seed and primary selection metric
# ---------------------------------------------------------------------------
RANDOM_SEED: int = 42
PRIMARY_METRIC: str = "mae"
