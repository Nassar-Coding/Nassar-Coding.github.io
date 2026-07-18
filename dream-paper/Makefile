# End-to-end reproduction. Each stage reads only the outputs of the stage
# before it; `make all` rebuilds everything from the versioned raw data.

PY := python3

.PHONY: all setup acquire-weather acquire-311 panel features forecast decision sensitivity tables test clean

all: panel features forecast decision sensitivity tables

setup:
	$(PY) -m pip install -r requirements.txt

# Acquisition. The 311 step requires network access to the city portals;
# in the sandboxed research environment it runs via the GitHub Actions
# workflow .github/workflows/acquire-311-data.yml instead (same script).
acquire-weather:
	$(PY) src/acquisition/fetch_weather.py --config configs/data_sources.yml --out data/raw/weather

acquire-311:
	$(PY) src/acquisition/fetch_311.py --config configs/data_sources.yml --out data/raw/311

panel:
	$(PY) src/preprocessing/build_panel.py

features:
	$(PY) src/features/build_features.py

forecast:
	$(PY) scripts/run_forecasting.py

decision:
	$(PY) scripts/run_decision.py

# Targeted validity sensitivities added for the external-review revision:
# tie-break / objective non-identification, normalized pooling, conformal
# recalibration, and horizon-length robustness. Each reads only frozen
# pipeline outputs and writes its own metrics file.
sensitivity:
	$(PY) scripts/run_tiebreak_sensitivity.py
	$(PY) scripts/run_logpool_sensitivity.py
	$(PY) scripts/run_conformal_calibration.py
	$(PY) scripts/run_horizon_sensitivity.py
	$(PY) scripts/run_backlog_sensitivity.py
	$(PY) scripts/run_poisson_baseline.py

tables:
	$(PY) scripts/make_tables_figures.py

kappa:
	$(PY) scripts/run_kappa_sweep.py

test:
	$(PY) -m pytest tests -q

clean:
	rm -rf data/interim/* data/processed/* outputs/metrics/* outputs/tables/* outputs/figures/*
