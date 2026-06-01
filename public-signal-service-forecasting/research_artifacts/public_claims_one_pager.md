# Public Claims One-Pager

A quick reference for describing this project safely in public. All numbers are
read from committed artifacts under `reports/` and `data/metadata/`.

## Safe title

From Forecast Accuracy to Operational Value: Public Signal Augmentation for NYC
311 Service Demand.

(Public project name: Public Signal Service Forecasting. Research line:
Forecasting Service Demand with Public Signals.)

## One-sentence summary

On real NYC 311 data (2022-2024) augmented with real NOAA weather, public-signal
augmentation consistently improves next-day service-demand forecasts, and the
improvement carries through in direction - though with attenuated,
budget-dependent magnitude - to a stylized staffing-allocation simulation.

## Safe public claims

- Uses real NYC 311 Service Requests (2022-2024) and real NOAA Central Park
  daily weather (2022-2024). No synthetic data and no synthetic weather.
- Target is the observed next-day request volume per date x borough x
  complaint_group cell.
- Four feature sets are compared (internal_historical, calendar_augmented,
  weather_augmented, calendar_weather_augmented) under a strictly chronological
  protocol with five-fold rolling-origin validation.
- Calendar features are the dominant signal; real weather adds a smaller but
  consistent further gain. Best model: random forest on calendar_weather_augmented,
  held-out test MAE 55.33 (RMSE 177.48, MAPE 27.47%, R-squared 0.648), 23.0%
  better than a naive seasonal baseline (71.85).
- The forecast improvement is robust: it holds in every rolling fold, all five
  boroughs, and all eight complaint groups.
- In a stylized staffing simulation the augmented policy reduces weighted unmet
  demand at every crew budget tested, but the magnitude is budget-dependent and
  small at the baseline budget (about 1.9%, closing about 26% of the gap to an
  oracle).
- The work is a reproducible research baseline and a workshop / short-paper /
  arXiv-style artifact.

## Unsafe claims (do not make)

- No causal effect, causal identification, or causal impact of weather/calendar
  on service demand.
- No production readiness, deployment, or integration with any real system.
- No real dispatch impact, real staffing optimization, or operational-policy
  adoption.
- No public-safety operational use.
- No external validity beyond NYC and the 2022-2024 window.
- Not full-paper, journal, or publication ready; no acceptance is implied.
- Do not claim forecast accuracy automatically equals operational value, or that
  decision gains are large or guaranteed.
- Do not claim transit or event data is used (it is not in this version).

## Reproducibility facts

- Pipeline: `python -m src.weather`, `python -m src.build_dataset`,
  `python -m src.train`, `python -m src.evaluate`,
  `python -m src.decision_simulation`, `python -m src.monitor`,
  `python -m src.rolling_validation`, `python -m src.robustness_analysis`,
  `python -m src.decision_sensitivity`, `python -m src.practical_significance`.
- Quality gate: `ruff check .` and `pytest`, run offline on a committed
  real-schema sample. Continuous integration runs the pipeline in sample mode.
- No API keys, no secrets, no paid services. Real inputs are committed (the
  aggregated daily counts and the NOAA weather CSV); the large raw monthly 311
  exports are not required in the repository.

## How to describe it in a research conversation

"It is a reproducible real-data baseline that asks whether public external
signals improve municipal service-demand forecasts and whether that improvement
transfers to an operational decision. On NYC 311 with NOAA weather, calendar
structure helps most and weather adds a small consistent gain; the
forecast-to-decision transfer is real but attenuated and budget-dependent, which
is the honest contribution. It is a workshop/short-paper artifact, not a full
paper."

## How not to describe it

Do not call it a deployed system, a dispatch optimizer, a staffing solution, a
causal study, or a finished/accepted paper. Do not imply it generalizes beyond
NYC 2022-2024. Do not describe the weather layer as more than a single-station
city-level proxy.
