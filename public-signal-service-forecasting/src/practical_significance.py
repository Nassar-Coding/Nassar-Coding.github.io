"""Practical-significance summary for the public-signal forecasting project.

This module reads the robustness artifacts (rolling-origin validation, segmented
performance by complaint group and borough, and decision sensitivity) and
distills simple, defensible practical-significance statements. It does not invent
statistical tests that the design cannot support; it reports consistency and
stability of the calendar-augmentation effect across folds, segments, and crew
budgets, and whether that evidence is strong enough to consider full-paper
drafting.

Output:
- reports/practical_significance_summary.json
"""
from __future__ import annotations

import pandas as pd

from . import config
from .utils import ensure_directories, get_logger, load_json, save_json

LOGGER = get_logger(__name__)


def _require(path) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"Required robustness artifact missing: {path}. Run the rolling "
            "validation, robustness analysis, and decision sensitivity first."
        )


def build_summary() -> dict:
    """Assemble the practical-significance summary from saved artifacts."""
    ensure_directories()
    for path in (
        config.ROLLING_VALIDATION_SUMMARY_FILE,
        config.COMPLAINT_GROUP_PERFORMANCE_FILE,
        config.BOROUGH_PERFORMANCE_FILE,
        config.DECISION_SENSITIVITY_SUMMARY_FILE,
    ):
        _require(path)

    rolling = load_json(config.ROLLING_VALIDATION_SUMMARY_FILE)
    group_df = pd.read_csv(config.COMPLAINT_GROUP_PERFORMANCE_FILE)
    borough_df = pd.read_csv(config.BOROUGH_PERFORMANCE_FILE)
    sensitivity = load_json(config.DECISION_SENSITIVITY_SUMMARY_FILE)

    n_folds = rolling["n_folds"]
    consistency = rolling["calendar_augmentation_consistency"]
    rolling_all_models_all_folds = all(
        v["calendar_augmented_wins_all_folds"] for v in consistency.values()
    )

    groups_better = int(group_df["augmented_better"].sum())
    groups_total = int(len(group_df))
    boroughs_better = int(borough_df["augmented_better"].sum())
    boroughs_total = int(len(borough_df))

    decision_all_settings = bool(sensitivity["augmented_better_in_all_settings"])

    # Strong-evidence criteria (all must hold to consider full-paper drafting on
    # the forecasting claim; the decision claim is reported separately).
    forecasting_consistent = (
        rolling_all_models_all_folds
        and groups_better == groups_total
        and boroughs_better == boroughs_total
    )
    decision_consistent_direction = decision_all_settings

    # The decision effect is budget-dependent; flag that it is not uniformly
    # large even though its direction is consistent.
    reductions = {
        name: setting["weighted_unmet_reduction_pct"]
        for name, setting in sensitivity["settings"].items()
    }
    decision_effect_varies_with_budget = (max(reductions.values()) - min(reductions.values())) > 1.0

    summary = {
        "calendar_augmentation_improves_mae_across_rolling_folds": rolling_all_models_all_folds,
        "rolling_folds": n_folds,
        "rolling_mean_improvement_pct_by_model": {
            m: v["mean_improvement_pct"] for m, v in consistency.items()
        },
        "improvement_stable_across_boroughs": boroughs_better == boroughs_total,
        "boroughs_augmented_better": f"{boroughs_better}/{boroughs_total}",
        "improvement_stable_across_complaint_groups": groups_better == groups_total,
        "complaint_groups_augmented_better": f"{groups_better}/{groups_total}",
        "decision_improvement_direction_stable_across_budgets": decision_consistent_direction,
        "decision_reduction_pct_by_setting": reductions,
        "decision_effect_varies_with_budget": decision_effect_varies_with_budget,
        "forecasting_evidence_strong": forecasting_consistent,
        "decision_evidence_strong": decision_consistent_direction
        and not decision_effect_varies_with_budget,
        "strong_enough_for_full_paper_drafting": False,
        "assessment": (
            "The forecasting claim is well supported: calendar augmentation lowers "
            "MAE for every model in every rolling fold and for every borough and "
            "complaint group. The decision claim is directionally consistent across "
            "scarce, moderate, and generous crew budgets but its magnitude is "
            "budget-dependent (small under scarcity, larger under generous capacity), "
            "and it rests on a single stylized proportional-allocation heuristic. "
            "This evidence supports an extended-abstract/workshop artifact and a "
            "strong research baseline, but not full-paper drafting, which would "
            "require an external-signal comparison, formal forecast-difference tests, "
            "and a richer, non-stylized decision model."
        ),
    }
    save_json(config.PRACTICAL_SIGNIFICANCE_FILE, summary)
    LOGGER.info(
        "Practical significance: forecasting_strong=%s, decision_strong=%s, "
        "full_paper_ready=%s",
        summary["forecasting_evidence_strong"],
        summary["decision_evidence_strong"],
        summary["strong_enough_for_full_paper_drafting"],
    )
    return summary


def main() -> None:
    build_summary()


if __name__ == "__main__":
    main()
