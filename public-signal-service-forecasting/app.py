"""Public Signal Service Forecasting dashboard.

A real public-data study of NYC 311 service-request forecasting and a stylized
staffing-allocation simulation. The dashboard reads the outputs produced by the
pipeline and renders them, degrading gracefully when an output is missing.

Run with:

    streamlit run app.py
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from src import config
from src.predict import predict_with_details

st.set_page_config(page_title="Public Signal Service Forecasting", layout="wide")


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (ValueError, OSError):
        return None


def _missing(message: str) -> None:
    st.info(message)


def _section_overview() -> None:
    st.header("1. Overview")
    st.write(
        "This is a real public-data research baseline. It tests whether calendar "
        "and temporal features improve next-day NYC 311 service-request volume "
        "forecasts, and whether improved forecasts translate into better stylized "
        "staffing allocation decisions."
    )
    st.warning(
        "Local research baseline. Not a production system, not real dispatch, and "
        "not a causal study. Forecast-accuracy improvement is not the same as "
        "operational value, which is why a decision simulation is included."
    )

    report = _load_json(config.DATA_SOURCE_REPORT)
    if report is None:
        _missing("Run `python -m src.build_dataset` to generate the dataset and metadata.")
        return

    mode = report.get("data_mode", "unknown")
    if mode == config.DATA_MODE_REAL:
        st.success("Data mode: real NYC 311 (observed 2022-2024 service requests).")
    elif mode == config.DATA_MODE_SAMPLE:
        st.warning(
            "Data mode: sample_real_schema. A small real-schema sample is in use "
            "(CI/demo). These are not full research results."
        )
    else:
        st.info(f"Data mode: {mode}")

    columns = st.columns(4)
    rows = report.get("processed_row_count")
    columns[0].metric("Processed rows", f"{rows:,}" if isinstance(rows, int) else "n/a")
    observed = report.get("date_range_observed", ["n/a", "n/a"])
    columns[1].metric("Date range", f"{observed[0]} to {observed[1]}")
    columns[2].metric("Boroughs", len(report.get("boroughs_included", [])) or "n/a")
    columns[3].metric("Complaint groups", len(report.get("complaint_groups_included", [])) or "n/a")


def _section_research_question() -> None:
    st.header("2. Research Question")
    st.write(
        "Can real NYC 311 service-request history, calendar features, and temporal "
        "lag features forecast next-day service-request volume, and does improved "
        "forecast accuracy translate into improved stylized staffing allocation "
        "decisions?"
    )
    st.markdown(
        "- This is not just a forecasting app.\n"
        "- It connects observed public service-request data, service-operations "
        "forecasting, an internal-historical vs calendar-augmented comparison, "
        "forecast accuracy, operational decision quality, and reproducible ML "
        "engineering."
    )


def _section_data_schema() -> None:
    st.header("3. Data Source and Schema")
    report = _load_json(config.DATA_SOURCE_REPORT)
    if report is None:
        _missing("Dataset metadata not found. Run `python -m src.build_dataset`.")
        return
    st.write(f"Source: {report.get('source_name', 'n/a')}")
    st.write(
        f"Study window: {report.get('study_start_date')} to {report.get('study_end_date')}"
    )
    st.json(report)
    st.subheader("Processed columns")
    st.write(", ".join(config.PROCESSED_COLUMNS))


def _section_feature_sets() -> None:
    st.header("4. Feature Sets")
    internal = config.FEATURE_SETS["internal_historical"]
    augmented = config.FEATURE_SETS["calendar_augmented"]
    extra = [c for c in augmented if c not in internal]
    columns = st.columns(2)
    with columns[0]:
        st.subheader("Internal historical")
        st.write(internal)
    with columns[1]:
        st.subheader("Calendar augmented")
        st.write("All internal historical features plus calendar features:")
        st.write(extra)


def _section_models() -> None:
    st.header("5. Forecasting Models")
    st.markdown(
        "- Naive seasonal baseline (trailing 7-day rolling mean)\n"
        "- Ridge regression\n"
        "- Random forest regressor\n"
        "- Gradient boosting regressor\n\n"
        "Each model is trained on both feature sets. Selection is by validation "
        "MAE under a strictly chronological 70/15/15 split by date."
    )


def _section_evaluation() -> None:
    st.header("6. Evaluation Results")
    metrics = _load_json(config.METRICS_FILE)
    evaluation = _load_json(config.EVALUATION_REPORT_FILE)
    if metrics is None:
        _missing("Run `python -m src.train` then `python -m src.evaluate`.")
        return

    columns = st.columns(2)
    columns[0].metric("Best model", metrics.get("best_model", "n/a"))
    columns[1].metric("Feature set", metrics.get("best_feature_set", "n/a"))

    if evaluation is not None:
        test_metrics = evaluation.get("test_metrics", {})
        cols = st.columns(4)
        cols[0].metric("MAE", f"{test_metrics.get('mae', float('nan')):.3f}")
        cols[1].metric("RMSE", f"{test_metrics.get('rmse', float('nan')):.3f}")
        cols[2].metric("MAPE (%)", f"{test_metrics.get('mape', float('nan')):.2f}")
        cols[3].metric("R-squared", f"{test_metrics.get('r2', float('nan')):.3f}")

    st.subheader("Model comparison")
    if config.MODEL_COMPARISON_FILE.exists():
        st.dataframe(pd.read_csv(config.MODEL_COMPARISON_FILE), use_container_width=True)
    if config.FIG_FORECAST_ERROR.exists():
        st.image(str(config.FIG_FORECAST_ERROR))
    if config.FIG_ACTUAL_VS_PREDICTED.exists():
        st.subheader("Observed vs predicted (test period)")
        st.image(str(config.FIG_ACTUAL_VS_PREDICTED))


def _section_internal_vs_augmented() -> None:
    st.header("7. Internal vs Calendar-Augmented Comparison")
    metrics = _load_json(config.METRICS_FILE)
    if metrics is None:
        _missing("Run `python -m src.train` to populate this comparison.")
        return
    summary = metrics.get("internal_vs_augmented", {})
    if summary:
        rows = [
            {
                "model": model_name,
                "internal_test_mae": round(values["internal_test_mae"], 4),
                "calendar_augmented_test_mae": round(values["augmented_test_mae"], 4),
                "mae_improvement_pct": round(values["mae_improvement_pct"], 3),
                "augmented_better": values["augmented_better"],
            }
            for model_name, values in summary.items()
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    if config.FIG_INTERNAL_VS_AUGMENTED.exists():
        st.image(str(config.FIG_INTERNAL_VS_AUGMENTED))


def _section_decision_simulation() -> None:
    st.header("8. Staffing Decision Simulation")
    st.caption(
        "Stylized simulation only. It does not represent real agency dispatch and "
        "is not a claim of real staffing optimization."
    )
    report = _load_json(config.DECISION_SIMULATION_REPORT_FILE)
    if report is None:
        _missing("Run `python -m src.decision_simulation`.")
        return

    rows = []
    for name, metrics in report.get("policies", {}).items():
        row = {"policy": name}
        row.update(metrics)
        rows.append(row)
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    improvement = report.get("augmented_improvement_over_baseline", {})
    cols = st.columns(2)
    cols[0].metric(
        "Weighted-unmet reduction (%)",
        f"{improvement.get('weighted_unmet_demand_reduction_pct', float('nan')):.3f}",
    )
    cols[1].metric(
        "Gap to oracle closed (%)",
        f"{improvement.get('gap_to_oracle_closed_pct', float('nan')):.2f}",
    )
    if config.FIG_DECISION_QUALITY.exists():
        st.image(str(config.FIG_DECISION_QUALITY))


def _section_prediction_explorer() -> None:
    st.header("9. Prediction Explorer")
    if not config.BEST_MODEL_FILE.exists():
        _missing("Train a model first with `python -m src.train`.")
        return

    with st.form("prediction_form"):
        columns = st.columns(3)
        borough = columns[0].selectbox("Borough", config.BOROUGHS)
        complaint_group = columns[1].selectbox("Complaint group", config.COMPLAINT_GROUPS)
        year = columns[2].number_input("Year", min_value=2022, max_value=2024, value=2024)

        columns = st.columns(4)
        month = columns[0].number_input("Month", min_value=1, max_value=12, value=6)
        quarter = columns[1].number_input("Quarter", min_value=1, max_value=4, value=2)
        day_of_week = columns[2].number_input("Day of week (Mon=0)", min_value=0, max_value=6, value=2)
        week_of_year = columns[3].number_input("Week of year", min_value=1, max_value=53, value=22)

        columns = st.columns(4)
        day_of_year = columns[0].number_input("Day of year", min_value=1, max_value=366, value=152)
        is_weekend = columns[1].selectbox("Is weekend", [0, 1])
        is_holiday = columns[2].selectbox("Is holiday", [0, 1])
        is_month_start = columns[3].selectbox("Is month start", [0, 1])
        is_month_end = st.selectbox("Is month end", [0, 1])

        columns = st.columns(3)
        request_lag_1 = columns[0].number_input("Request lag 1", min_value=0.0, value=100.0)
        request_lag_7 = columns[1].number_input("Request lag 7", min_value=0.0, value=100.0)
        rolling_mean_7 = columns[2].number_input("Rolling mean 7", min_value=0.0, value=100.0)

        columns = st.columns(3)
        rolling_mean_14 = columns[0].number_input("Rolling mean 14", min_value=0.0, value=100.0)
        rolling_std_7 = columns[1].number_input("Rolling std 7", min_value=0.0, value=10.0)
        rolling_std_14 = columns[2].number_input("Rolling std 14", min_value=0.0, value=10.0)

        submitted = st.form_submit_button("Predict next-day volume")

    if submitted:
        record = {
            "borough": borough,
            "complaint_group": complaint_group,
            "is_weekend": is_weekend,
            "is_holiday": is_holiday,
            "day_of_week": day_of_week,
            "month": month,
            "quarter": quarter,
            "year": year,
            "day_of_year": day_of_year,
            "week_of_year": week_of_year,
            "is_month_start": is_month_start,
            "is_month_end": is_month_end,
            "request_lag_1": request_lag_1,
            "request_lag_7": request_lag_7,
            "rolling_mean_7": rolling_mean_7,
            "rolling_mean_14": rolling_mean_14,
            "rolling_std_7": rolling_std_7,
            "rolling_std_14": rolling_std_14,
        }
        details = predict_with_details(record)
        st.success(
            f"Predicted next-day request volume: "
            f"{details['predicted_next_day_request_volume']:.1f}"
        )
        st.caption(
            f"Model used: {details['model_used']} | "
            f"Feature set used: {details['feature_set_used']}"
        )


def _section_monitoring() -> None:
    st.header("10. Monitoring")
    report = _load_json(config.MONITORING_REPORT_FILE)
    if report is None:
        _missing("Run `python -m src.monitor`.")
        return
    st.json(report)


def _section_responsible_ai() -> None:
    st.header("11. Responsible AI and Limitations")
    st.markdown(
        "- Real public NYC 311 data in research mode; CI may use a small "
        "real-schema sample for speed.\n"
        "- Aggregate daily counts only; no personal or individual-level data.\n"
        "- No production dispatch; no causal claims; no real staffing optimization.\n"
        "- 311 reflects reporting behaviour, not true incidence (reporting bias).\n"
        "- See `docs/responsible_ai.md` and `docs/limitations.md` for details."
    )


def _section_artifacts() -> None:
    st.header("12. Generated Outputs")
    artifacts = {
        "Processed dataset": config.PROCESSED_DATA_FILE,
        "Data source report": config.DATA_SOURCE_REPORT,
        "Best model": config.BEST_MODEL_FILE,
        "Model comparison": config.MODEL_COMPARISON_FILE,
        "Metrics": config.METRICS_FILE,
        "Evaluation report": config.EVALUATION_REPORT_FILE,
        "Decision simulation report": config.DECISION_SIMULATION_REPORT_FILE,
        "Monitoring report": config.MONITORING_REPORT_FILE,
    }
    rows = [
        {
            "output": name,
            "path": _relative(path),
            "present": path.exists(),
        }
        for name, path in artifacts.items()
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True)


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(config.PROJECT_ROOT))
    except ValueError:
        return str(path)


def main() -> None:
    st.title("Public Signal Service Forecasting")
    st.caption(
        "A real public-data research baseline for NYC 311 service-request "
        "forecasting and staffing decision simulation."
    )
    _section_overview()
    _section_research_question()
    _section_data_schema()
    _section_feature_sets()
    _section_models()
    _section_evaluation()
    _section_internal_vs_augmented()
    _section_decision_simulation()
    _section_prediction_explorer()
    _section_monitoring()
    _section_responsible_ai()
    _section_artifacts()


main()
