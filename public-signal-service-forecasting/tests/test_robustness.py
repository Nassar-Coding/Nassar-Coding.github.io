"""Tests for the robustness package: rolling validation, segmented performance,
decision sensitivity, and the practical-significance summary.

All tests run in the isolated sample (real-schema) workspace provided by the
session fixtures, so they never overwrite production artifacts and never use
synthetic data.
"""
from __future__ import annotations

import pandas as pd

from src import (
    config,
    decision_sensitivity,
    practical_significance,
    robustness_analysis,
    rolling_validation,
)
from src.utils import load_json


def test_rolling_validation_creates_reports(processed_frame, monkeypatch) -> None:
    # Use a small number of folds to keep the test fast.
    monkeypatch.setattr(rolling_validation, "N_FOLDS", 2)
    summary = rolling_validation.run_rolling_validation()

    assert config.ROLLING_VALIDATION_REPORT_FILE.exists()
    assert config.ROLLING_VALIDATION_SUMMARY_FILE.exists()
    assert config.FIG_ROLLING_VALIDATION.exists()
    assert summary["n_folds"] >= 2


def test_rolling_validation_uses_multiple_folds(processed_frame, monkeypatch) -> None:
    monkeypatch.setattr(rolling_validation, "N_FOLDS", 3)
    rolling_validation.run_rolling_validation()
    report = pd.read_csv(config.ROLLING_VALIDATION_REPORT_FILE)
    assert report["fold"].nunique() == 3


def test_rolling_validation_preserves_chronological_order(processed_frame, monkeypatch) -> None:
    monkeypatch.setattr(rolling_validation, "N_FOLDS", 3)
    rolling_validation.run_rolling_validation()
    report = pd.read_csv(config.ROLLING_VALIDATION_REPORT_FILE)
    # Each later fold tests a strictly later (or equal-start, non-overlapping)
    # date block; test_start must be non-decreasing in fold order.
    starts = (
        report[["fold", "test_start"]]
        .drop_duplicates()
        .sort_values("fold")["test_start"]
        .tolist()
    )
    assert starts == sorted(starts)


def test_robustness_creates_segment_files(processed_frame) -> None:
    robustness_analysis.run_robustness_analysis()
    assert config.COMPLAINT_GROUP_PERFORMANCE_FILE.exists()
    assert config.BOROUGH_PERFORMANCE_FILE.exists()
    assert config.FIG_COMPLAINT_GROUP_MAE.exists()
    assert config.FIG_BOROUGH_MAE.exists()

    group_df = pd.read_csv(config.COMPLAINT_GROUP_PERFORMANCE_FILE)
    borough_df = pd.read_csv(config.BOROUGH_PERFORMANCE_FILE)
    for column in ("internal_historical_mae", "calendar_augmented_mae", "augmented_better"):
        assert column in group_df.columns
        assert column in borough_df.columns
    assert len(borough_df) >= 1
    assert len(group_df) >= 1


def test_decision_sensitivity_creates_report(processed_frame) -> None:
    decision_sensitivity.run_decision_sensitivity()
    assert config.DECISION_SENSITIVITY_REPORT_FILE.exists()
    assert config.DECISION_SENSITIVITY_SUMMARY_FILE.exists()
    assert config.FIG_DECISION_SENSITIVITY.exists()

    report = pd.read_csv(config.DECISION_SENSITIVITY_REPORT_FILE)
    # Three settings x three policies.
    assert set(report["setting"].unique()) == set(config.DECISION_CREW_SETTINGS)
    assert {"baseline_internal_historical", "calendar_augmented", "oracle_true_demand"}.issubset(
        set(report["policy"].unique())
    )


def test_practical_significance_summary_created(processed_frame) -> None:
    # Ensure upstream artifacts exist in the isolated workspace first.
    rolling_validation.run_rolling_validation()
    robustness_analysis.run_robustness_analysis()
    decision_sensitivity.run_decision_sensitivity()

    summary = practical_significance.build_summary()
    assert config.PRACTICAL_SIGNIFICANCE_FILE.exists()
    for key in (
        "calendar_augmentation_improves_mae_across_rolling_folds",
        "improvement_stable_across_boroughs",
        "improvement_stable_across_complaint_groups",
        "decision_improvement_direction_stable_across_budgets",
        "strong_enough_for_full_paper_drafting",
    ):
        assert key in summary

    saved = load_json(config.PRACTICAL_SIGNIFICANCE_FILE)
    assert isinstance(saved["strong_enough_for_full_paper_drafting"], bool)


def test_robustness_uses_real_schema_not_synthetic(processed_frame) -> None:
    # The active data mode in the isolated workspace is the real-schema sample;
    # there is no synthetic mode anywhere in config.
    report = load_json(config.DATA_SOURCE_REPORT)
    assert report["data_mode"] == config.DATA_MODE_SAMPLE
    assert report["no_synthetic_data"] is True
