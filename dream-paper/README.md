# From Accuracy to Allocation: When Do Better Municipal Demand Forecasts Make Better Staffing Decisions?

A reproducible four-city study of 311 service-request demand forecasting and
its downstream capacity-allocation value. Companion repository for the
manuscript in `paper/` and supplement in `supplement/`.

**Cities:** New York, Chicago, San Francisco, Austin (official open-data
311 systems, 2019–2025). **Weather:** NOAA GHCN-Daily via the official AWS
Open Data mirror. **No synthetic demand or weather data are used anywhere.**

## What is claimed — and not claimed

This is a predictive and *simulational* study. The allocation layer is a
stylized model of daily capacity planning (assumptions A1–A7,
`docs/01_problem_definition.md`); it is not a deployment and implies no
city involvement or endorsement. Forecast targets are *reported* request
volumes, which are known to under-represent need in less-reporting
communities (Kontokosta & Hong, 2021).

## Reproduce everything

```bash
pip install -r requirements.txt
make test          # unit tests (harmonization, leakage, allocation, simulator)

# 1. acquisition (raw data + provenance manifests are already versioned here;
#    re-run only to refresh from the sources)
make acquire-weather       # NOAA GHCN-Daily (reachable everywhere)
make acquire-311           # needs access to the four Socrata portals; in the
                           # sandboxed research environment this ran via
                           # .github/workflows/acquire-311-data.yml (same script)

# 2. full pipeline: panel -> features -> forecasts -> decisions -> artifacts
make all
```

Every table and figure in the manuscript is written to `outputs/` by
`scripts/make_tables_figures.py`; nothing in the paper is hand-computed.
Deterministic seed: `GLOBAL_SEED = 20260609` (`src/common/runtime.py`).

## Layout

```
configs/        data sources, service-family harmonization (versioned rules)
src/            acquisition / preprocessing / features / forecasting /
                optimization / evaluation
scripts/        experiment drivers + table/figure generation
tests/          unit tests incl. leakage and allocation-optimality checks
data/raw/       acquired daily aggregates + JSON provenance manifests (versioned)
data/interim/   regenerable (gitignored)
data/processed/ regenerable (gitignored)
outputs/        metrics, tables, figures (regenerable, versioned for audit)
docs/           phase-by-phase research log (problem definition, novelty
                audit, feasibility audit, decision register, ...)
paper/          manuscript source
supplement/     supplementary material source
```

## Data licensing

Only server-side daily aggregates (counts per day × native category) are
stored here, with the exact query URLs, retrieval timestamps, and SHA-256
checksums in `data/raw/*/**_manifest.json`. Record-level data remain at the
city portals; acquisition scripts retrieve them reproducibly. Sources: NYC
Open Data, Chicago Data Portal, DataSF (PDDL), City of Austin Open Data,
NOAA GHCN-Daily (AWS Open Data Program).
