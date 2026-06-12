# Phase 3 — Data and Operational Feasibility Audit

## Candidate environments evaluated

Requirement: public, documented, legally usable, request-level 311-style
systems with multi-year depth, daily timestamps, and native category
taxonomies, accessible through a stable API suitable for reproducible
acquisition.

| System | API | Depth | Verdict |
|---|---|---|---|
| NYC 311 (`erm2-nwe9`, NYC Open Data) | Socrata SODA | 2010– | **selected** (continuity with Paper 1) |
| Chicago 311 (`v6vf-nfxy`) | Socrata SODA | 2018-12-18– | **selected** (current system only; window starts 2019-01-01) |
| San Francisco 311 (`vw6y-z8j6`, DataSF, PDDL) | Socrata SODA | 2008– | **selected** |
| Austin 311 (`xwdj-i9he`; an earlier draft cited `i26j-ai4z` in error, corrected at the revision pass) | Socrata SODA | 2014– | **selected** |
| Boston 311 (CKAN, data.boston.gov) | CKAN | 2011– | rejected: different API/yearly-file distribution; harmonization effort not matched by added heterogeneity over the four selected |
| Kansas City 311 | Socrata | system migration in 2021 fragmented the series | rejected: temporal discontinuity inside the study window |
| Gulf-region municipal systems (Makkah, Riyadh, Jeddah, Dubai, Doha) | — | — | rejected for this paper: no public request-level open-data equivalents located; recorded as motivated future work, not forced in |

Selection criteria were stated before selection: API uniformity (reduces
acquisition-bug risk), full coverage of the 2019–2025 window, category
granularity, and size/heterogeneity spread (NYC ≫ Chicago > SF > Austin;
coastal/inland; snow/no-snow climates). Cities were not selected for fame:
Boston was excluded despite prominence, Austin included despite size.

## Weather

NOAA GHCN-Daily via the official AWS Open Data mirror (`noaa-ghcn-pds`),
one first-order station per city (Central Park, O'Hare, SF Downtown, Camp
Mabry). Single-station city-level proxy is assumption A2 (limitation,
consistent with Paper 1). Acquired 2026-06-09 with checksums; see
`data/raw/weather/*_manifest.json`.

## What the environments support — and what they do not

Supported with real evidence:
- daily request counts per native category (acquired via server-side
  aggregation; manifests record every query URL);
- harmonized service families with fully documented mappings;
- next-day and multi-day demand targets; chronological evaluation;
- weather/calendar augmentation; cross-city comparison and transfer.

NOT supported (and therefore not claimed anywhere):
- actual staffing levels, crew counts, or shift data (no city in the set
  publishes them at daily granularity) → capacity is a swept simulation
  parameter, classified sensitivity-only;
- true service effort per request (closure timestamps exist in some
  portals but conflate administrative closure with resolution; deferred);
- sub-city spatial harmonization (incompatible geographies);
- measurement of unreported need (acknowledged reporting bias).

## Operational meaning of the decision task

The stylized allocation maps to the daily planning question "how much
capacity should each service area receive tomorrow," which municipal
operations literature treats as a staffing/queueing problem under
time-varying demand (Green, Kolesar & Whitt, 2007). The simulation makes
the dependence on its stylization assumptions explicit (A4–A6) and sweeps
them; it is never described as a deployment.

## Phase 3 gate

Prediction task, decision task, operational loss, and reproducibility are
all supportable with real, legally usable public data; quantities that are
not supportable are excluded from claims and classified as sensitivity-only
simulation parameters. PASS.

> **D14 note (added at the revision pass):** references to a 2019–2025 window in this Phase 3 document predate decision D14; the frozen study window is 2020-01-01–2025-12-31 for all cities, set by the scope of NYC's current dataset.
