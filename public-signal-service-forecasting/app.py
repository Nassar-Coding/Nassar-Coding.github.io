"""Public Signal Service Forecasting dashboard.

A local research baseline for service-request forecasting and staffing decision
simulation. This dashboard reads artifacts produced by the pipeline and renders
them; it gracefully reports when an artifact has not yet been generated.

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
from src.predict import predict_next_day_volume

st.set_page_config(
    page_title="Public Signal Service Forecasting",
    layout="wide",
)


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
        "This is a local research baseline that tests whether public external "
        "signals improve municipal service-request forecasting, and whether "
        "improved forecasts translate into better staffing allocation decisions."
    )
    st.warning(
        "Local research baseline. Not a production system and not real dispatch. "
        "By default it runs on a clearly labelled deterministic synthetic dataset."
    )

    report = _load_json(config.DATA_SOURCE_REPORT)
    if report is None:
        _missing("Run `python -m src.build_dataset` to generate the dataset and metadata.")
        return

    mode = report.get("data_mode", "unknown")
    label = "Synthetic fallback" if mode == "synthetic_fallback" else "Real public data"
    columns = st.columns(4)
    columns[0].metric("Data mode", label)
    columns[1].metric("Processed rows", f"{report.get('processed_row_count', 'n/a'):,}"
                      if isinstance(report.get("processed_row_count"), int) else "n/a")
    columns[2].metric("Boroughs", report.get("borough_count", "n/a"))
    columns[3].metric("Complaint groups", report.get("complaint_group_count", "n/a"))
    if report.get("date_min") and report.get("date_max"):
        st.caption(f"Date range: {report['date_min']} to {report['date_max']}")


def _section_research_question() -> None:
    st.header("2. Research Question")
    st.write(
        "Do public external signals such as weather, calendar features, holidays, "
        "and operational context improve service-request volume forecasts, and do "
        "those forecast improvements translate into better staffing allocation "
        "decisions?"
    )
    st.markdown(
        "- This is not just a forecasting app.\n"
        "- It connects public-data feature augmentation, service-operations "
        "forecasting, forecast accuracy, operational decision quality, and "
        "reproducible ML engineering.\n"
        "- Forecast-accuracy improvement is not the same as operational value, "
        "which is why a decision simulation is included."
    )


def _section_data_schema() -> None:
    st.header("3. Data Source and Schema")
    report = _load_json(config.DATA_SOURCE_REPORT)
    if report is None:
        _missing("Dataset metadata not found. Run `python -m src.build_dataset`.")
        return
    st.json(report)
    st.subheader("Processed columns")
    st.write(", ".join(config.PROCESSED_COLUMNS))


def _section_feature_sets() -> None:
    st.header("4. Feature Sets")
    internal = config.FEATURE_SETS["internal_only"]
    augmented = config.FEATURE_SETS["augmented"]
    extra = [c for c in augmented if c not in internal]
    columns = st.columns(2)
    with columns[0]:
        st.subheader("Internal-only baseline")
        st.write(internal)
    with columns[1]:
        st.subheader("Public-signal augmented")
        st.write("All internal features plus:")
        st.write(extra)


def _section_models() -> None:
    st.header("5. Forecasting Models")
    st.markdown(
        "- Naive seasonal baseline (trailing 7-day rolling mean)\n"
        "- Ridge regression\n"
        "- Random forest regressor\n"
        "- Gradient boosting regressor\n\n"
        "Each model is trained on both feature sets. Selection is by validation "
        "MAE under a strictly chronological 70/15/15 split."
    )


def _section_evaluation() -> None:
    st.header("6. Evaluation Results")
    metrics = _load_json(config.METRICS_FILE)
    evaluation = _load_json(config.EVALUATION_REPORT_FILE)
    if metrics is None:
        _missing("Run `python -m src.train` then `python -m src.evaluate`.")
        return

    st.subheader("Best model")
    columns = st.columns(2)
    columns[0].metric("Model", metrics.get("best_model", "n/a"))
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
        comparison = pd.read_csv(config.MODEL_COMPARISON_FILE)
        st.dataframe(comparison, use_container_width=True)
    if config.FIG_FORECAST_ERROR.exists():
        st.image(str(config.FIG_FORECAST_ERROR))


def _section_internal_vs_augmented() -> None:
    st.header("7. Internal vs Public-Signal Augmented Comparison")
    metrics = _load_json(config.METRICS_FILE)
    if metrics is None:
        _missing("Run `python -m src.train` to populate this comparison.")
        return
    summary = metrics.get("internal_vs_augmented", {})
    if summary:
        rows = []
        for model_name, values in summary.items():
            rows.append(
                {
                    "model": model_name,
                    "internal_test_mae": round(values["internal_test_mae"], 4),
                    "augmented_test_mae": round(values["augmented_test_mae"], 4),
                    "mae_improvement_pct": round(values["mae_improvement_pct"], 3),
                    "augmented_better": values["augmented_better"],
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    if config.FIG_INTERNAL_VS_AUGMENTED.exists():
        st.image(str(config.FIG_INTERNAL_VS_AUGMENTED))


def _section_decision_simulation() -> None:
    st.header("8. Staffing Decision Simulation")
    st.caption(
        "Stylized simulation only. It does not represent real agency dispatch."
    )
    report = _load_json(config.DECISION_SIMULATION_REPORT_FILE)
    if report is None:
        _missing("Run `python -m src.decision_simulation`.")
        return

    policies = report.get("policies", {})
    rows = []
    for name, metrics in policies.items():
        row = {"policy": name}
        row.update(metrics)
        rows.append(row)
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    improvement = report.get("augmented_improvement_over_baseline", {})
    st.metric(
        "Augmented vs baseline weighted-unmet reduction (%)",
        f"{improvement.get('weighted_unmet_demand_reduction_pct', float('nan')):.3f}",
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
        month = columns[2].number_input("Month", min_value=1, max_value=12, value=6)

        columns = st.columns(4)
        temp_c = columns[0].number_input("Temperature (C)", value=18.0)
        precipitation_mm = columns[1].number_input("Precipitation (mm)", min_value=0.0, value=0.0)
        wind_speed_kmh = columns[2].number_input("Wind speed (km/h)", min_value=0.0, value=12.0)
        event_intensity = columns[3].slider("Event intensity", 0.0, 1.0, 0.3)

        columns = st.columns(4)
        severe_weather = columns[0].selectbox("Severe weather", [0, 1])
        is_weekend = columns[1].selectbox("Is weekend", [0, 1])
        is_holiday = columns[2].selectbox("Is holiday", [0, 1])
        day_of_week = columns[3].number_input("Day of week (Mon=0)", min_value=0, max_value=6, value=2)

        columns = st.columns(4)
        request_lag_1 = columns[0].number_input("Request lag 1", min_value=0.0, value=50.0)
        request_lag_7 = columns[1].number_input("Request lag 7", min_value=0.0, value=50.0)
        rolling_mean_7 = columns[2].number_input("Rolling mean 7", min_value=0.0, value=50.0)
        rolling_mean_14 = columns[3].number_input("Rolling mean 14", min_value=0.0, value=50.0)

        submitted = st.form_submit_button("Predict next-day volume")

    if submitted:
        record = {
            "borough": borough,
            "complaint_group": complaint_group,
            "temp_c": temp_c,
            "precipitation_mm": precipitation_mm,
            "wind_speed_kmh": wind_speed_kmh,
            "severe_weather": severe_weather,
            "event_intensity": event_intensity,
            "is_weekend": is_weekend,
            "is_holiday": is_holiday,
            "day_of_week": day_of_week,
            "month": month,
            "request_lag_1": request_lag_1,
            "request_lag_7": request_lag_7,
            "rolling_mean_7": rolling_mean_7,
            "rolling_mean_14": rolling_mean_14,
        }
        prediction = predict_next_day_volume(record)
        st.success(f"Predicted next-day request volume: {prediction:.1f}")


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
        "- Local-only research baseline; not deployed and not production-ready.\n"
        "- Uses public-style data, defaulting to a labelled synthetic fallback.\n"
        "- No personal data; no real dispatch; no causal claims.\n"
        "- Synthetic results characterize the modelled process, not real demand.\n"
        "- See `docs/responsible_ai.md` and `docs/limitations.md` for details."
    )


def _section_artifacts() -> None:
    st.header("12. System Artifacts")
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
        {"artifact": name, "path": str(path.relative_to(config.PROJECT_ROOT)), "present": path.exists()}
        for name, path in artifacts.items()
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True)


def main() -> None:
    st.title("Public Signal Service Forecasting")
    st.caption(
        "A local research baseline for service-request forecasting and staffing "
        "decision simulation."
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
