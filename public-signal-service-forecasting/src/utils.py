"""Shared utility helpers: logging, JSON IO, directory setup, and metrics."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np

from . import config


def get_logger(name: str) -> logging.Logger:
    """Return a module logger with a single stream handler."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def ensure_directories() -> None:
    """Create all output directories if they do not already exist."""
    for directory in (
        config.RAW_DIR,
        config.PROCESSED_DIR,
        config.METADATA_DIR,
        config.MODELS_DIR,
        config.REPORTS_DIR,
        config.FIGURES_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)


def save_json(path: Path, payload: dict[str, Any]) -> None:
    """Write a dictionary to a JSON file with indentation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=_json_default)


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON file into a dictionary."""
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _json_default(value: Any) -> Any:
    """Serialise numpy scalar types that are not natively JSON encodable."""
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.ndarray,)):
        return value.tolist()
    raise TypeError(f"Object of type {type(value)} is not JSON serializable")


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean absolute error."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Root mean squared error."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mape(y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1.0) -> float:
    """Mean absolute percentage error with safe handling of zero values.

    Denominators are clamped to ``epsilon`` so that zero or near-zero actuals
    do not produce infinite percentage errors. Returned as a percentage.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denominator = np.maximum(np.abs(y_true), epsilon)
    return float(np.mean(np.abs((y_true - y_pred) / denominator)) * 100.0)


def r2_score_safe(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Coefficient of determination with guard against zero variance."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    if ss_tot == 0.0:
        return 0.0
    return 1.0 - ss_res / ss_tot


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Return the standard metric bundle used across the project."""
    return {
        "mae": mae(y_true, y_pred),
        "rmse": rmse(y_true, y_pred),
        "mape": mape(y_true, y_pred),
        "r2": r2_score_safe(y_true, y_pred),
    }
