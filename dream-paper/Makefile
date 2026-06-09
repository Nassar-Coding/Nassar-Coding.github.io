# End-to-end reproduction. Each stage reads only the outputs of the stage
# before it; `make all` rebuilds everything from the versioned raw data.

PY := python3

.PHONY: all setup acquire-weather acquire-311 panel features forecast decision tables test clean

all: panel features forecast decision tables

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

tables:
	$(PY) scripts/make_tables_figures.py

test:
	$(PY) -m pytest tests -q

clean:
	rm -rf data/interim/* data/processed/* outputs/metrics/* outputs/tables/* outputs/figures/*
