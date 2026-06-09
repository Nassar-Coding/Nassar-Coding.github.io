# Research Decision Log

Chronological record of binding scientific and engineering decisions, with
rationale. (Phases refer to the 11-phase execution plan.)

| # | Phase | Decision | Rationale / alternative rejected |
|---|---|---|---|
| D1 | 1 | One dominant contribution: the accuracy→decision-value mapping across cities/regimes; multi-city replication, uncertainty, and transfer are supporting axes | A "do everything" paper (events, mobility, digital twins) would dilute falsifiability; vision doc itself warns against forcing every component in |
| D2 | 1 | Unit = (city, family, day); no sub-city geography | Cross-city spatial units are incompatible (boroughs/wards/neighborhoods); false harmonization forbidden |
| D3 | 3 | Cities: NYC, Chicago, SF, Austin (all Socrata) | API uniformity reduces acquisition-bug risk; Boston (CKAN) rejected; KC rejected (2021 system migration mid-window); Gulf cities lack public request-level data → future work |
| D4 | 3/4 | Acquire server-side daily aggregates, not record-level dumps | Record-level (~30M rows) adds no information for a daily panel, slows acquisition, and raises redistribution concerns; aggregates + manifests are fully reproducible |
| D5 | 4 | Sandbox network policy blocks Socrata portals → acquisition runs in GitHub Actions (unrestricted runners) committing raw aggregates + manifests to the branch | Only honest path to real data from this environment; provenance preserved (query URLs, timestamps, SHA-256) |
| D6 | 4 | Full-window grouped queries timed out on NYC (180 s read timeout, 5 attempts) → chunk queries by calendar year | Identical results (groups never span years); each query stays inside portal limits. Failure preserved in run #1 logs (run id 27227530526) |
| D7 | 5 | Models: 2 naive baselines, ridge, random forest, LightGBM(+quantile). No deep/foundation models | Panel is ~10k rows/city-family-day scale per fit; deep models add tuning-budget asymmetry without scientific necessity; constitution forbids complexity for prestige. Recorded as scope, not as a claim that they cannot help |
| D8 | 6 | Uncertainty via quantile GBM with non-crossing enforcement; evaluated by pinball + interval coverage | Direct, well-understood, feeds the allocation layer without distributional assumptions |
| D9 | 7 | Decision = integer crew allocation across families with backlog carryover; capacity/productivity/abandonment/weights classified sensitivity-only and swept | No city publishes daily staffing; inventing a fixed value would be a hidden assumption; sweeping makes conditionality explicit |
| D10 | 8 | Decision-aware axis = (a) expected-value greedy policies (point and quantile), (b) decision-loss-based model selection. No SPO/end-to-end training | With 8-dim separable concave allocation, the policy layer is exactly optimizable given any forecast distribution, so the binding question is information (point vs quantile vs oracle) and selection, not gradient plumbing; end-to-end training deferred and stated as future work |
| D11 | 2 | Literature verified via web search against publisher pages/arXiv/DBLP; one citation (Wang et al. cross-city) kept as arXiv because the venue version could not be confirmed | Constitution: no unverified citation metadata |
| D12 | 4 | Chicago "311 INFORMATION ONLY CALL" and aviation-routed "AIRCRAFT NOISE COMPLAINT" excluded; SF "Case is a Duplicate" excluded; Chicago duplicate=true dropped | Documented non-service or duplicate records; reasons in configs/service_families.yml; counts in panel manifest |
| D13 | 4 | First NYC export-path acquisition REJECTED and deleted: sum of aggregated counts (21,152,185) exceeded records scanned (19,669,371), caused by a mid-stream retry merging rows from a failed partial attempt; fixed by per-attempt counters merged only on success; NYC re-acquired with the fixed script | Constitution: data integrity; the discrepancy was caught by the scanned-vs-aggregated invariant check before any downstream use |
| D14 | 3/4 | Study window moved to 2020-01-01..2025-12-31 for ALL cities | NYC erm2-nwe9 is scoped "2020 to Present" (no 2019 rows exist); a uniform window preserves cross-city comparability |
