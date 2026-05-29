"""CrowdOps AI Command Center -- local Streamlit dashboard.

A local AI engineering lifecycle demo for crowd risk prediction and executive
operational intelligence. Everything runs on your machine: no APIs, no keys,
no cloud, no database.

Run from the project root with:

    streamlit run app.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src import (
    DATA_PATH,
    EVALUATION_PATH,
    EVENT_TYPES,
    METRICS_PATH,
    MODEL_PATH,
    MONITORING_PATH,
    PROJECT_ROOT,
    RISK_LEVELS,
    ZONES,
)
from src.data import dataset_summary, load_data
from src.predict import predict_risk

# Brand palette -- calm corporate blue-gray suitable for executive viewing.
RISK_COLORS = {"Low": "#2E8B57", "Medium": "#E1A100", "High": "#C0392B"}

st.set_page_config(
    page_title="CrowdOps AI Command Center",
    page_icon="🛰️",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Cached loaders (so re-runs stay fast without re-reading from disk each time).
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def _load_dataframe(_mtime: float) -> pd.DataFrame:
    """Load the dataset. ``_mtime`` busts the cache when the file changes."""
    return load_data(DATA_PATH)


def get_dataframe() -> pd.DataFrame | None:
    """Return the dataset if it exists, else None (handled by callers)."""
    if not DATA_PATH.exists():
        return None
    return _load_dataframe(DATA_PATH.stat().st_mtime)


def _read_json(path: Path) -> dict | None:
    """Read a JSON report if present, else return None."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _read_text(relative: str) -> str | None:
    """Read a project markdown asset if present."""
    path = PROJECT_ROOT / relative
    return path.read_text(encoding="utf-8") if path.exists() else None


def latest_f1() -> float | None:
    """Return the latest model macro F1 from metrics.json, if available."""
    metrics = _read_json(METRICS_PATH)
    if metrics:
        return float(metrics["best_metrics"]["f1_macro"])
    return None


# ---------------------------------------------------------------------------
# Sidebar navigation.
# ---------------------------------------------------------------------------
SECTIONS = [
    "Executive Overview",
    "Problem Definition",
    "AI Lifecycle",
    "Data Overview",
    "Zone Risk Dashboard",
    "Train Model",
    "Model Evaluation",
    "Predict Risk",
    "Monitoring",
    "Week 3 Visual Storytelling",
    "Week 4 Multimedia Briefing",
    "Responsible AI Notes",
]


def main() -> None:
    st.sidebar.title("🛰️ CrowdOps")
    st.sidebar.caption("Local AI Command Center")
    section = st.sidebar.radio("Navigate", SECTIONS, label_visibility="collapsed")
    st.sidebar.divider()
    st.sidebar.info(
        "Local-only demo. Synthetic data. No APIs, keys, cloud, or database. "
        "Not a production system."
    )

    st.title("CrowdOps AI Command Center")
    st.caption(
        "A local AI engineering lifecycle demo for crowd risk prediction and "
        "executive operational intelligence."
    )

    render = {
        "Executive Overview": render_executive_overview,
        "Problem Definition": render_problem_definition,
        "AI Lifecycle": render_ai_lifecycle,
        "Data Overview": render_data_overview,
        "Zone Risk Dashboard": render_zone_dashboard,
        "Train Model": render_train,
        "Model Evaluation": render_evaluation,
        "Predict Risk": render_predict,
        "Monitoring": render_monitoring,
        "Week 3 Visual Storytelling": lambda: render_markdown_asset(
            "visuals/week3_visual_storytelling.md", "Week 3 Visual Storytelling"
        ),
        "Week 4 Multimedia Briefing": lambda: render_markdown_asset(
            "visuals/week4_multimedia_briefing.md", "Week 4 Multimedia Briefing"
        ),
        "Responsible AI Notes": render_responsible_ai,
    }
    render[section]()


# ---------------------------------------------------------------------------
# Section renderers.
# ---------------------------------------------------------------------------
def render_kpis(frame: pd.DataFrame) -> None:
    """Render the headline KPI cards."""
    summary = dataset_summary(frame)
    f1 = latest_f1()
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Records", f"{summary['total_records']:,}")
    col2.metric("Operational Zones", summary["total_zones"])
    col3.metric("High-Risk Records", f"{summary['high_risk_records']:,}")
    col4.metric("Avg Wait (min)", summary["avg_wait_time"])
    col5.metric("Model F1 (macro)", f"{f1:.3f}" if f1 is not None else "Not trained")


def render_executive_overview() -> None:
    st.header("Executive Overview")
    st.write(
        "This command center demonstrates how zone-level operational data can be "
        "converted into **actionable crowd risk intelligence**. It walks through a "
        "complete, local AI engineering lifecycle -- from data to a deployed, "
        "monitored model -- using the kind of dashboard a duty manager or COO "
        "would consult during operations."
    )

    frame = get_dataframe()
    if frame is None:
        _missing_data_notice()
        return

    render_kpis(frame)
    st.divider()
    st.subheader("What this is (and is not)")
    col_a, col_b = st.columns(2)
    with col_a:
        st.success(
            "**It is:**\n\n"
            "- A local AI command center *simulation*\n"
            "- A full ML lifecycle demo (data → model → monitoring)\n"
            "- An executive-friendly decision-support mockup\n"
            "- A reusable consulting storytelling asset"
        )
    with col_b:
        st.warning(
            "**It is not:**\n\n"
            "- A real-time production system\n"
            "- Connected to cameras, sensors, or IoT\n"
            "- Using real client or venue data\n"
            "- Dependent on any cloud service or API"
        )


def render_problem_definition() -> None:
    st.header("Problem Definition")
    st.subheader("The operational challenge")
    st.write(
        "Large venues -- stadiums, transport hubs, malls, events -- manage crowds "
        "across many zones simultaneously: gates, halls, parking, exits, food "
        "courts, corridors, and prayer areas. Operations teams must spot **where "
        "risk is building** before it becomes a safety or service problem."
    )
    st.subheader("Why prediction matters")
    st.markdown(
        "- Manual monitoring does not scale across dozens of zones.\n"
        "- Risk emerges from a *combination* of signals (density, waiting time, "
        "net inflow, event context) -- not one number.\n"
        "- Leadership needs a single, consistent risk signal to prioritise "
        "response and communicate clearly."
    )
    st.subheader("The AI framing")
    st.info(
        "**Task:** Multi-class classification.\n\n"
        "**Target:** `risk_level` ∈ {Low, Medium, High}.\n\n"
        "**Inputs:** crowd_count, zone_capacity, density_ratio, avg_wait_time, "
        "entry_rate, exit_rate, temperature, hour, day_of_week, zone, event_type."
    )


def render_ai_lifecycle() -> None:
    st.header("AI Lifecycle")
    st.write(
        "Every stage of the AI engineering lifecycle is implemented in this "
        "project. The table maps each stage to the exact files and outputs."
    )
    lifecycle = pd.DataFrame(
        [
            ("1. Problem Identification", "README.md, this app", "Problem & target defined"),
            ("2. Data Preparation", "src/generate_data.py, src/data.py", "data/crowd_ops.csv"),
            ("3. Feature Engineering", "src/features.py", "ColumnTransformer pipeline"),
            ("4. Model Training", "src/train.py", "models/crowd_risk_model.joblib"),
            ("5. Model Evaluation", "src/evaluate.py", "reports/evaluation.json"),
            ("6. Model Deployment", "app.py (Streamlit)", "Interactive dashboard"),
            ("7. Model Monitoring", "src/monitor.py", "reports/monitoring_report.json"),
            ("8. MLOps / Maintenance", ".github/workflows/ci.yml", "Automated CI pipeline"),
        ],
        columns=["Lifecycle Stage", "Implemented In", "Key Output"],
    )
    st.table(lifecycle)
    st.caption(
        "Flow: Problem → Data → Features → Train → Evaluate → Deploy → Monitor → "
        "Maintain (and back to Data as conditions change)."
    )


def render_data_overview() -> None:
    st.header("Data Overview")
    frame = get_dataframe()
    if frame is None:
        _missing_data_notice()
        return

    render_kpis(frame)
    st.divider()
    st.subheader("Recent operational zone records")
    st.dataframe(frame.tail(15), use_container_width=True)

    st.subheader("Column reference")
    st.markdown(
        "- **timestamp** — record time (10-minute operational ticks)\n"
        "- **zone** — operational area (gate, hall, parking, etc.)\n"
        "- **crowd_count / zone_capacity** — people present vs nominal capacity\n"
        "- **density_ratio** — crowd_count / zone_capacity\n"
        "- **avg_wait_time** — average queue/wait minutes\n"
        "- **entry_rate / exit_rate** — people in/out per tick\n"
        "- **temperature** — ambient °C\n"
        "- **hour / day_of_week** — temporal context\n"
        "- **event_type** — operational context\n"
        "- **risk_level** — target: Low / Medium / High"
    )
    st.info(
        "Data is **synthetic and reproducible** (fixed random seed). "
        "It is for demonstration only and is not real client or venue data."
    )


def render_zone_dashboard() -> None:
    st.header("Zone Risk Dashboard")
    frame = get_dataframe()
    if frame is None:
        _missing_data_notice()
        return

    render_kpis(frame)
    st.divider()

    # Chart 1: risk level distribution.
    st.subheader("Risk level distribution")
    risk_counts = (
        frame["risk_level"].value_counts().reindex(RISK_LEVELS).fillna(0).astype(int)
    )
    fig1, ax1 = plt.subplots(figsize=(6, 3.2))
    ax1.bar(
        risk_counts.index,
        risk_counts.values,
        color=[RISK_COLORS[r] for r in risk_counts.index],
    )
    ax1.set_ylabel("Records")
    ax1.set_xlabel("Risk level")
    for i, v in enumerate(risk_counts.values):
        ax1.text(i, v, f"{v:,}", ha="center", va="bottom", fontsize=9)
    st.pyplot(fig1)
    plt.close(fig1)

    col_left, col_right = st.columns(2)

    # Chart 2: average wait time by zone.
    with col_left:
        st.subheader("Average wait time by zone")
        wait_by_zone = frame.groupby("zone")["avg_wait_time"].mean().sort_values()
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        ax2.barh(wait_by_zone.index, wait_by_zone.values, color="#34607D")
        ax2.set_xlabel("Avg wait time (min)")
        st.pyplot(fig2)
        plt.close(fig2)

    # Chart 3: density ratio by zone.
    with col_right:
        st.subheader("Average density ratio by zone")
        density_by_zone = frame.groupby("zone")["density_ratio"].mean().sort_values()
        fig3, ax3 = plt.subplots(figsize=(5, 4))
        ax3.barh(density_by_zone.index, density_by_zone.values, color="#7D5234")
        ax3.set_xlabel("Density ratio (crowd / capacity)")
        st.pyplot(fig3)
        plt.close(fig3)

    st.subheader("High-risk records by zone")
    high_by_zone = (
        frame[frame["risk_level"] == "High"]["zone"].value_counts().rename("high_risk_records")
    )
    st.dataframe(high_by_zone, use_container_width=True)


def render_train() -> None:
    st.header("Train Model")
    st.write(
        "Train and compare two models (Logistic Regression and Random Forest) "
        "and persist the best one by macro F1. This runs locally on your machine."
    )
    if not DATA_PATH.exists():
        st.warning(
            "No dataset found yet. The training step will generate it automatically, "
            "or you can run `python -m src.generate_data` first."
        )

    if st.button("🚀 Train / Retrain model", type="primary"):
        with st.spinner("Training models locally... this may take a moment."):
            from src.train import train_models

            result = train_models()
        st.success(
            f"Done. Best model: **{result['best_model']}** "
            f"(F1 macro = {result['best_metrics']['f1_macro']:.4f})."
        )
        st.cache_data.clear()

    metrics = _read_json(METRICS_PATH)
    if metrics:
        st.subheader("Latest training run")
        st.caption(f"Trained at: {metrics.get('trained_at', 'unknown')}")
        comparison = pd.DataFrame(metrics["all_models"]).T
        st.dataframe(comparison, use_container_width=True)
        st.info(f"Selected model: **{metrics['best_model']}** (by macro F1).")
    else:
        st.info("No training metrics yet. Click the button above to train the model.")


def render_evaluation() -> None:
    st.header("Model Evaluation")
    if not MODEL_PATH.exists():
        st.warning("No trained model found. Train one first in the **Train Model** section.")
        return

    if st.button("Run evaluation"):
        with st.spinner("Evaluating model on held-out test data..."):
            from src.evaluate import evaluate_model

            evaluate_model()
        st.success("Evaluation complete.")

    evaluation = _read_json(EVALUATION_PATH)
    if not evaluation:
        st.info("No evaluation report yet. Click **Run evaluation** above.")
        return

    st.subheader("Per-class performance")
    report = evaluation["classification_report"]
    rows = {k: v for k, v in report.items() if k in evaluation["labels"]}
    st.dataframe(pd.DataFrame(rows).T, use_container_width=True)

    st.subheader("Confusion matrix")
    labels = evaluation["confusion_matrix"]["labels"]
    matrix = evaluation["confusion_matrix"]["matrix"]
    cm_df = pd.DataFrame(
        matrix,
        index=[f"actual {lbl}" for lbl in labels],
        columns=[f"pred {lbl}" for lbl in labels],
    )
    st.dataframe(cm_df, use_container_width=True)
    st.caption(evaluation["confusion_matrix"]["description"])


def render_predict() -> None:
    st.header("Predict Risk")
    st.write(
        "Enter operational conditions for a zone and get a predicted risk level. "
        "`density_ratio` is calculated automatically from crowd count and capacity."
    )
    if not MODEL_PATH.exists():
        st.warning(
            "No trained model found. Train one first in the **Train Model** section, "
            "or run `python -m src.train`."
        )
        return

    with st.form("predict_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            zone = st.selectbox("Zone", ZONES)
            crowd_count = st.number_input("Crowd count", min_value=0, value=750, step=10)
            zone_capacity = st.number_input("Zone capacity", min_value=1, value=1000, step=10)
        with col2:
            avg_wait_time = st.number_input("Avg wait time (min)", min_value=0.0, value=14.0, step=0.5)
            entry_rate = st.number_input("Entry rate (per tick)", min_value=0, value=120, step=5)
            exit_rate = st.number_input("Exit rate (per tick)", min_value=0, value=80, step=5)
        with col3:
            temperature = st.number_input("Temperature (°C)", min_value=-10.0, value=36.0, step=0.5)
            hour = st.slider("Hour of day", 0, 23, 18)
            day_of_week = st.slider("Day of week (0=Mon)", 0, 6, 4)
        event_type = st.selectbox("Event type", EVENT_TYPES, index=EVENT_TYPES.index("Special Event"))

        density_ratio = round(crowd_count / zone_capacity, 3) if zone_capacity else 0.0
        st.caption(f"Calculated density ratio: **{density_ratio}**")
        submitted = st.form_submit_button("Predict risk", type="primary")

    if submitted:
        record = {
            "zone": zone,
            "crowd_count": crowd_count,
            "zone_capacity": zone_capacity,
            "density_ratio": density_ratio,
            "avg_wait_time": avg_wait_time,
            "entry_rate": entry_rate,
            "exit_rate": exit_rate,
            "temperature": temperature,
            "hour": hour,
            "day_of_week": day_of_week,
            "event_type": event_type,
        }
        result = predict_risk(record)
        if result.get("error"):
            st.error(result["error"])
            return

        predicted = result["predicted_risk"]
        color = RISK_COLORS.get(predicted, "#333333")
        st.markdown(
            f"<h2 style='color:{color};'>Predicted risk: {predicted}</h2>",
            unsafe_allow_html=True,
        )

        probabilities = result.get("probabilities")
        if probabilities:
            st.subheader("Class probabilities")
            proba_df = (
                pd.DataFrame(
                    {"probability": probabilities}
                )
                .reindex(RISK_LEVELS)
                .fillna(0.0)
            )
            st.bar_chart(proba_df)
            st.dataframe(proba_df, use_container_width=True)


def render_monitoring() -> None:
    st.header("Monitoring")
    st.write(
        "A lightweight, local stand-in for model-health monitoring. It compares "
        "the latest macro F1 to a stored baseline and reports a status."
    )
    if not METRICS_PATH.exists():
        st.warning("No metrics found. Train the model first in **Train Model**.")
        return

    if st.button("Run monitoring check"):
        from src.monitor import run_monitoring

        run_monitoring()
        st.success("Monitoring check complete.")

    report = _read_json(MONITORING_PATH)
    if not report:
        st.info("No monitoring report yet. Click **Run monitoring check** above.")
        return

    status = report["status"]
    status_style = {
        "Healthy": st.success,
        "Warning": st.warning,
        "Needs Review": st.error,
    }.get(status, st.info)
    status_style(f"**Status: {status}** — {report['message']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Current F1 (macro)", f"{report['current_f1_macro']:.4f}")
    col2.metric("Baseline F1 (macro)", f"{report['baseline_f1_macro']:.4f}")
    col3.metric("Drop from baseline", f"{report['f1_drop_from_baseline']:.4f}")
    st.caption(f"Checked at: {report['checked_at']}")


def render_markdown_asset(relative: str, title: str) -> None:
    st.header(title)
    content = _read_text(relative)
    if content is None:
        st.warning(f"Asset not found: `{relative}`.")
        return
    st.markdown(content)


def render_responsible_ai() -> None:
    st.header("Responsible AI Notes")
    st.markdown(
        "This project is built with responsible AI practices appropriate for a "
        "local demonstration:"
    )
    st.markdown(
        "- **Synthetic data only.** No real people, clients, or venues are "
        "represented. Data is generated locally with a fixed seed.\n"
        "- **No surveillance.** There is no camera, biometric, or personal-data "
        "processing. Inputs are aggregate operational counts.\n"
        "- **Honest framing.** This is a *local simulation and lifecycle demo*, "
        "not a production or real-time safety system.\n"
        "- **Decision support, not automation.** Predictions are intended to "
        "assist human operators, never to replace human judgement in safety "
        "decisions.\n"
        "- **Transparency.** Metrics, evaluation, and monitoring are written to "
        "readable files in `reports/` for inspection.\n"
        "- **Known limitations.** Synthetic data cannot capture all real-world "
        "dynamics; a real deployment would require validated data, fairness "
        "review across zones, and human oversight."
    )
    st.info(
        "For any real deployment, add: validated data governance, human-in-the-"
        "loop sign-off, fairness/robustness testing, and an incident process. "
        "(Future improvement — not implemented here.)"
    )


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------
def _missing_data_notice() -> None:
    st.warning(
        "No dataset found at `data/crowd_ops.csv`.\n\n"
        "Generate it by running **one** of these from the project root:\n\n"
        "```\npython -m src.generate_data\n```\n"
        "...or just open the **Train Model** section, which generates data "
        "automatically before training."
    )


if __name__ == "__main__":
    main()
