# Data Availability Statement

## Sources

- **NYC 311 Service Requests** - NYC Open Data, dataset `erm2-nwe9`
  (https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9).
  Public, no authentication required. Study window 2022-01-01 to 2024-12-31.
- **NOAA NCEI Daily Summaries (GHCN-Daily)** - station USW00094728
  (NY City Central Park). Public. Study window 2022-01-01 to 2024-12-31.

## What is committed

- Aggregated real daily counts: `data/raw/nyc_311_daily_counts_2022_2024.csv`.
- Real NOAA weather export: `data/raw/nyc_central_park_weather_2022_2024.csv`.
- Provenance metadata: `data/metadata/data_source_report.json`,
  `data/metadata/weather_source_report.json`.
- Small real-schema CI samples: `data/raw/nyc_311_daily_counts_sample.csv`,
  `data/raw/nyc_central_park_weather_sample.csv`.
- Evidence artifacts: `reports/*.json`, `reports/*.csv`, `figures/*.png`.

## What is not committed (ignored)

- The large raw monthly NYC 311 exports (too large; not required - the
  aggregated daily counts are committed instead).
- The processed modelling dataset (regenerable from committed inputs).
- The trained model binary under `models/` (large, regenerable).

## Sample data for CI

Continuous integration runs in sample mode on the small committed real-schema
samples so the pipeline runs quickly and offline. The samples preserve the real
schema and the observed-count logic; they are clearly labelled as CI samples and
are not the source of the research-mode results.

## Synthetic data

No synthetic data and no synthetic weather are used anywhere. The 311 results
derive from real NYC 311 records; the weather results derive from real NOAA
records. Missing source weather variables are recorded, not fabricated; the one
derived quantity (average temperature) is the mean of observed daily maximum and
minimum and is documented in the weather source report.
