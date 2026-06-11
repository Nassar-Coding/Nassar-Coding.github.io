# Next-Day Municipal Service-Demand Forecasting Across Four Cities
### A Benchmark with a Controlled Simulated Capacity-Allocation Evaluation

Reproducible four-city study of next-day reported 311 service demand
(New York, Chicago, San Francisco, Austin; 2020–2025) with an explicitly
simulated family-level capacity-allocation evaluation. Companion
repository for the manuscript in `paper/` and supplement in `supplement/`.

**Data:** official open-data 311 portals + NOAA GHCN-Daily (AWS Open Data
mirror). **No synthetic demand or weather data are used anywhere.**

## What is claimed — and not claimed

This is a predictive and *simulational* study. The allocation layer is a
transparent simulation over abstract request-equivalent capacity units
under hypothetical service-pressure regimes; none of its parameters
estimates any city's actual capacity, productivity, or queues, and it is
not a deployment and implies no city involvement or endorsement.
Forecast targets are *reported* request volumes, which under-represent
need in less-reporting communities (Kontokosta & Hong, 2021). The
governing protocol (frozen training-only budgets, validation-only
selection, temporal censoring of pooled/transfer training, same-model
uncertainty contrast) is enforced by an automated guard suite
(`tests/test_guards.py`, G1–G13) that fails the build on violation.

## Reproduce everything

```bash
pip install -r requirements.txt
make test          # core tests + protocol guards

# 1. acquisition (raw aggregates + provenance manifests are versioned here;
#    re-run only to refresh from the sources)
make acquire-weather       # NOAA GHCN-Daily
make acquire-311           # official Socrata portals (runs via
                           # .github/workflows/acquire-311-data.yml where
                           # the portals are unreachable)

# 2. full pipeline: panel -> features -> forecasts -> simulated decisions
#    -> inference -> artifacts
make all
python3 -m pytest tests -q   # full guard suite must pass post-run
```

Deterministic seed `20260609`; the decision layer is Monte-Carlo-free.
Governing protocol: `docs/06_redesign_specification.md` (+ Amendment
C11); review gates: `docs/07_review_gates.md`; implementation report:
`paper_redesign_implementation_report.md`.

## Layout

```
configs/        data sources, family harmonization, frozen decision protocol
src/            acquisition / preprocessing / features / forecasting /
                optimization / evaluation
scripts/        experiment drivers, inference, artifact generation
tests/          core tests + guards G1–G13
data/raw/       acquired daily aggregates + JSON provenance manifests
outputs/        metrics, tables, figures (+ provenance hashes)
docs/           research log: problem definition, audits, decision log,
                redesign spec, review gates, findings
artifacts/      isolated pre-redesign outputs (superseded; kept for audit)
paper/          manuscript source; supplement/ supplementary material
```

## Data licensing

Only server-side daily aggregates (counts per day × native category) are
stored, with exact query URLs, retrieval timestamps, and SHA-256
checksums in `data/raw/*/**_manifest.json`. Record-level data remain at
the city portals; acquisition scripts retrieve them reproducibly.
Sources: NYC Open Data, Chicago Data Portal, DataSF (PDDL), City of
Austin Open Data, NOAA GHCN-Daily (AWS Open Data Program).
