# 🛰️ CrowdOps AI Command Center

> A local AI engineering lifecycle demo for **crowd risk prediction** and **executive operational intelligence**.

[![CI](https://github.com/Nassar-Coding/Nassar-Coding.github.io/actions/workflows/ci.yml/badge.svg)](https://github.com/Nassar-Coding/Nassar-Coding.github.io/actions/workflows/ci.yml)

---

## Executive Summary

The **CrowdOps AI Command Center** is a complete, runnable demonstration of how
zone-level operational data can be turned into **actionable crowd-risk
intelligence** for leadership. It predicts a `risk_level` (Low / Medium / High)
for operational zones such as gates, halls, parking, exits, and service areas,
and presents the results through an executive-friendly Streamlit dashboard.

Critically, it walks through the **entire AI engineering lifecycle** — from
reproducible data generation, through feature engineering, model training,
evaluation, deployment, and monitoring, to MLOps automation via GitHub
Actions. Everything runs **locally**: no APIs, no API keys, no paid services,
no cloud, no Docker, and no database.

> **This is a local simulation and lifecycle demo built on synthetic data — not a production or real-time system.**

---

## Why This Project Matters

Large venues — stadiums, transport hubs, malls, events, pilgrimage sites —
manage crowds across dozens of zones at once. Risk does not come from a single
number; it emerges from a *combination* of density, waiting time, net inflow
(entry vs exit), and operational context (a special event, peak hour, or
weather disruption). Manual monitoring does not scale, and leadership needs a
**single, consistent risk signal** to prioritise response and communicate
clearly.

This project demonstrates the engineering thinking behind such a system: how to
frame the problem, prepare data, build a leak-free ML pipeline, select and
evaluate models, deploy a decision-support interface, and keep the model
healthy over time.

## Relevance to AI Command Centers & Operational Intelligence

This demo mirrors the core loop of a real operational command center:

- **Sense** → ingest zone-level operational signals (here, a synthetic feed).
- **Reason** → a trained model converts raw signals into a risk classification.
- **Surface** → KPIs, zone charts, and alerts presented for fast decisions.
- **Govern** → evaluation, monitoring, and responsible-AI notes keep it honest.

It is the *intelligence layer* of a command center, expressed at a scale that a
single engineer can build, run, and present — and that a COO can immediately
understand.

---

## How It Fits Week 3 (AI Visuals)

The `visuals/week3_visual_storytelling.md` kit turns this project into
**executive visual storytelling**: command-center concept and AI-lifecycle
diagrams (Mermaid), a dashboard mockup description, an infographic layout, a
before/after consulting visual, and ready-to-use **image-generation prompts**
for building polished visuals. The Streamlit dashboard itself is the live
visual artifact.

## How It Fits Week 4 (AI Multimedia)

The `visuals/week4_multimedia_briefing.md` framework converts the project into
a **90-second multimedia briefing**: a full script, a 6-scene storyboard,
voiceover text, a slide-to-video plan, on-screen text suggestions, a
responsible-AI disclosure, and **prompt examples** for generating video,
voiceover, and an executive explainer. `visuals/executive_demo_talk_track.md`
adds 3-, 5-, and 10-minute presentation scripts plus likely COO Q&A.

---

## AI Lifecycle Mapping

| # | Lifecycle Stage | Implemented In | Key Output(s) |
|---|-----------------|----------------|---------------|
| 1 | **Problem Identification** | `README.md`, `app.py` (Problem Definition) | Problem framing & target definition |
| 2 | **Data Preparation** | `src/generate_data.py`, `src/data.py` | `data/crowd_ops.csv`, validated DataFrame |
| 3 | **Feature Engineering** | `src/features.py` | `ColumnTransformer` + train/test split |
| 4 | **Model Training** | `src/train.py` | `models/crowd_risk_model.joblib`, `reports/metrics.json`, `reports/model_summary.md` |
| 5 | **Model Evaluation** | `src/evaluate.py` | `reports/evaluation.json` (report + confusion matrix) |
| 6 | **Model Deployment** | `app.py` (Streamlit) | Interactive local command-center dashboard |
| 7 | **Model Monitoring** | `src/monitor.py` | `reports/monitoring_report.json` (Healthy/Warning/Needs Review) |
| 8 | **MLOps / Maintenance** | `.github/workflows/ci.yml` | Automated lint + test + train + artifact upload |

---

## Features

- 📊 **Executive dashboard** with KPI cards (records, zones, high-risk count, avg wait, model F1).
- 🗺️ **Zone risk views**: risk distribution, average wait time by zone, density ratio by zone.
- 🤖 **Two-model training & selection** (Logistic Regression vs Random Forest) chosen by macro F1.
- 🧮 **Leak-free pipeline** using scikit-learn `ColumnTransformer` + `Pipeline` (scaling + encoding).
- 🔮 **Interactive prediction form** with auto-calculated density ratio and class probabilities.
- 🩺 **Model monitoring** with baseline comparison and health status.
- 📈 **Reproducible synthetic dataset** (2,500 rows, fixed seed) — clearly labelled, never claimed real.
- ✅ **Automated tests** (pytest) and **linting** (ruff).
- 🔁 **GitHub Actions CI** running the full pipeline and uploading metrics as an artifact.
- 🎨 **Week 3 & Week 4 presentation assets** included.

---

## Project Structure

```
crowdops-ai-command-center/
├── app.py                      # Streamlit command-center dashboard (deployment)
├── README.md                   # This file
├── requirements.txt            # Pinned/minimum dependencies (PyPI only)
├── pyproject.toml              # ruff + pytest configuration
├── data/
│   └── crowd_ops.csv           # Generated synthetic dataset (>= 2,000 rows)
├── models/
│   └── .gitkeep                # Trained model artifact lands here
├── reports/
│   └── .gitkeep                # metrics / evaluation / monitoring land here
├── visuals/
│   ├── week3_visual_storytelling.md
│   ├── week4_multimedia_briefing.md
│   └── executive_demo_talk_track.md
├── src/
│   ├── __init__.py             # Shared schema, paths, and constants
│   ├── generate_data.py        # Reproducible synthetic data generation
│   ├── data.py                 # Data loading + validation
│   ├── features.py             # Feature engineering pipeline
│   ├── train.py                # Train, compare, select, persist
│   ├── evaluate.py             # Classification report + confusion matrix
│   ├── predict.py              # Single-record inference
│   └── monitor.py              # Model-health monitoring
├── tests/
│   ├── test_data.py
│   ├── test_features.py
│   ├── test_train.py
│   └── test_predict.py
└── .github/
    └── workflows/
        └── ci.yml              # MLOps automation
```

---

## Dataset Explanation

The dataset (`data/crowd_ops.csv`) is **synthetic, generated locally with a
fixed random seed** (`RANDOM_SEED = 42`) for full reproducibility. It contains
**2,500 rows** with the following columns:

| Column | Description |
|--------|-------------|
| `timestamp` | Record time (10-minute operational ticks) |
| `zone` | Operational area (Gate A/B, Main Hall, Parking, Emergency Exit, Food Court, Service Corridor, Prayer Area) |
| `crowd_count` | People present in the zone |
| `zone_capacity` | Nominal capacity of the zone |
| `density_ratio` | `crowd_count / zone_capacity` |
| `avg_wait_time` | Average queue/wait time (minutes) |
| `entry_rate` | People entering per tick |
| `exit_rate` | People exiting per tick |
| `temperature` | Ambient temperature (°C) |
| `hour` | Hour of day (0–23) |
| `day_of_week` | Day of week (0 = Monday) |
| `event_type` | Normal Day, Peak Hour, Special Event, Maintenance Window, Weather Disruption |
| `risk_level` | **Target**: Low / Medium / High |

**Risk logic.** Risk rises with high density, high waiting time, entry
outpacing exit, and high-pressure events (Special Event, Weather Disruption).
Controlled Gaussian noise is added so the target is **not perfectly
predictable** — keeping the classification task realistic.

---

## Responsible AI & Data Disclaimer

- **Synthetic data only.** No real people, clients, venues, or events are
  represented. *(Local-only, for demonstration.)*
- **No surveillance.** No cameras, biometrics, or personal data — inputs are
  aggregate operational counts.
- **Honest framing.** A *local simulation and lifecycle demo*, **not** a
  production or real-time safety system.
- **Decision support, not automation.** Predictions assist human operators;
  they never replace human judgement in safety decisions.
- **Known limitations.** Synthetic data cannot capture all real-world dynamics.
  A real deployment would require validated data governance, fairness review
  across zones, robustness testing, and human-in-the-loop oversight.
  *(Future improvement — not implemented here.)*

---

## How to Run in VS Code

1. Open the `crowdops-ai-command-center` folder in VS Code.
2. Open a terminal (`Terminal → New Terminal`).
3. Run the commands below in order.

### Installation

```
python -m venv .venv
```

For **Windows**:

```
.venv\Scripts\activate
```

For **macOS/Linux**:

```
source .venv/bin/activate
```

```
pip install -r requirements.txt
```

### Generate the data

```
python -m src.generate_data
```

### Train the model

```
python -m src.train
```

### Run the Streamlit app

```
streamlit run app.py
```

### Run the tests

```
pytest
```

### Lint the code

```
ruff check .
```

> Optional extras: `python -m src.evaluate` (writes `reports/evaluation.json`)
> and `python -m src.monitor` (writes `reports/monitoring_report.json`).

---

## How GitHub Actions Works

The workflow at `.github/workflows/ci.yml` runs on every **push** and **pull
request** using Python 3.11. It:

1. Installs dependencies from `requirements.txt`.
2. Runs `ruff check .` (lint).
3. Runs `pytest` (automated tests).
4. Runs `python -m src.train` (exercises the full lifecycle end-to-end).
5. Uploads `reports/metrics.json` as a build **artifact**.

No secrets and no API keys are required.

---

## Demo Flow (for Presentation)

1. **Executive Overview** — headline KPIs and an honest "is / is not" framing.
2. **Problem Definition** — the operational challenge and AI framing.
3. **AI Lifecycle** — the stage-to-file mapping table.
4. **Data Overview** — recent records and the synthetic-data disclaimer.
5. **Zone Risk Dashboard** — risk distribution and per-zone charts.
6. **Train Model** — click to train; compare the two models live.
7. **Model Evaluation** — per-class metrics and confusion matrix.
8. **Predict Risk** — enter a scenario (e.g., Gate A, Special Event) → live risk + probabilities.
9. **Monitoring** — health status vs baseline.
10. **Week 3 / Week 4 / Responsible AI** — storytelling, multimedia, and governance.

---

## Screenshots

> _Placeholder — add screenshots after running the app locally._

| View | Screenshot |
|------|------------|
| Executive Overview | `docs/screenshots/overview.png` _(add me)_ |
| Zone Risk Dashboard | `docs/screenshots/dashboard.png` _(add me)_ |
| Predict Risk | `docs/screenshots/predict.png` _(add me)_ |

---

## Future Improvements

*(All future improvements — not implemented here, by design of the local scope.)*

- Validated, governed real data feeds with schema contracts.
- Time-series / streaming ingestion and online inference.
- Fairness and robustness testing across zones and conditions.
- Human-in-the-loop alert acknowledgement and incident workflow.
- Model registry and automated retraining triggers.
- Richer explainability (per-prediction feature attributions).

---

## Note on Data

**The dataset in this project is synthetic and generated locally for
demonstration purposes only. It does not represent any real client, venue,
person, or event.**
