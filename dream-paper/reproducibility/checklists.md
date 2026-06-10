# Checklists (manuscript package)

## Submission checklist
- [x] Title/abstract match the evidence; no overclaim of novelty, deployment, causality, or endorsement
- [x] One central contribution (accuracy→allocation mapping across cities/regimes) stated in §1
- [x] All baselines retained in tables regardless of ranking
- [x] Negative results included (Austin weather null; negative transfer; interval under-dispersion)
- [x] Limitations section enumerates A1–A7 and scope exclusions
- [x] Anonymized build available (`paper/main_anon.pdf`)
- [x] References verified against primary sources (docs/02, D11)
- [ ] Venue-specific template/page-limit reflow — to be done against the chosen venue's current kit (docs/05_venue_strategy.md)

## Reproducibility checklist
- [x] All data public; acquisition scripts with exact query URLs committed
- [x] Raw layers versioned with SHA-256 manifests; never overwritten (interim/processed regenerate)
- [x] Single deterministic seed (20260609); no Monte Carlo in the decision layer
- [x] `make all` regenerates every number, table, and figure
- [x] Unit tests cover harmonization determinism, leakage controls, split chronology, allocation optimality (greedy = brute force), simulator conservation
- [x] Environment pinned (reproducibility/pip-freeze.txt, Python 3.11)
- [x] Acquisition-integrity events documented (decision log D6, D13, D17)

## Ethics / responsible-AI checklist
- [x] No individual-level data acquired or stored (server-side daily aggregates only)
- [x] Reported demand explicitly distinguished from social need throughout
- [x] Priority weights exposed as normative configuration and swept
- [x] Per-family unserved-demand distributions reported per policy
- [x] Simulation-not-deployment stated in abstract, §1, §8, limitations
- [x] No city involvement, endorsement, or deployment implied

## Data statement
Sources: NYC Open Data (erm2-nwe9), Chicago Data Portal (v6vf-nfxy),
DataSF (vw6y-z8j6, PDDL), City of Austin (xwdj-i9he), NOAA GHCN-Daily
(AWS Open Data, noaa-ghcn-pds). Acquired 2026-06-09 via committed
scripts; 36,840,931 records acquired, 30,215,145 retained after
documented exclusions; manifests in data/raw/. Counts for recent periods
may drift as portals backfill; manifests pin what this paper used.

## Limitations statement (summary)
Stylized decision layer (A4–A6, swept); reported demand ≠ need; one
weather station per city; target-day weather assumes day-ahead forecast
availability (A3, bounded by sensitivity variant); four U.S. Socrata
cities only; no causal claims; quantile intervals under-dispersed.
