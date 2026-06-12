> **VENUE SELECTION NOT STARTED.** This document is a pre-redesign draft
> retained for reference only; it predates the corrected protocol, the
> benchmark-dominant identity, and the U9 title. No venue has been selected
> or adapted to; this document will be rewritten only after Prof 1 / Prof 2
> re-closure.

# Phase 11 — Venue Strategy

## What the final contribution is

A reproducible multi-city public-operations benchmark plus an empirical
study of the forecast-accuracy → decision-value mapping (regime
dependence, ranking divergence, uncertainty value, transfer effects).
It is **not** a new learning method, **not** a deployment report, and
**not** a pure forecasting-accuracy paper. Venue fit must match that.

## Candidates compared

| Venue | Fit to contribution | Standard | Format | Risk |
|---|---|---|---|---|
| **KDD, Applied Data Science track** | strong: real public data end-to-end, reproducibility-valued, decision-relevance is an explicit ADS criterion | top-tier | ~9 pp + appendix | ADS track expects deployment-adjacent evidence; our simulation-only decision layer must be framed precisely |
| **International Journal of Forecasting** | strong: "value of forecasts" and forecast-evaluation studies are core scope; cross-city replication valued | leading field journal | no hard page limit | slower cycle; ML-benchmark framing less central |
| NeurIPS Datasets & Benchmarks | good: benchmark + protocol contribution | top-tier | 9 pp + appendix | decision-simulation component is unusual for the track; benchmark must be packaged as the headline |
| ACM SIGSPATIAL | moderate: urban data, but no spatial component in this paper | strong | 10 pp | weak fit: we deliberately removed sub-city geography |
| ECML-PKDD ADS track | good | strong (below KDD) | 16 pp LNCS | backup-tier |
| MSOM / POM | partial: decision layer fits, ML benchmark framing does not | elite OR journals | long | would require recentering on the OR model, losing the benchmark contribution |

## Decision

- **Primary: KDD Applied Data Science track.** Highest-prestige venue whose
  evaluation criteria (real data, rigorous protocol, decision relevance,
  reproducibility, honest limitations) match every element this study
  actually has. The simulation-not-deployment status is stated in the
  abstract and Section 1 so reviewers are never misled.
- **Backup: International Journal of Forecasting.** Scope-perfect for the
  central question (what is forecast accuracy worth to a decision), strong
  tradition of replication and forecast-value studies, and a journal format
  that accommodates the full supplement.

Submission deadlines, page-format files, and double-blind requirements
change year to year and MUST be re-verified against the venue site at
submission time; this repository's `paper/` builds a generic
single-column manuscript plus an anonymized variant
(`make -C paper anonymous` strips author block) as the starting point
for either venue's template.

## Dual-submission and archival plan

No dual submission. On acceptance (or upon arXiv posting if the venue
permits preprints), the repository is released publicly with a tagged
version and the raw-aggregate manifests frozen; an archival deposit
(e.g., Zenodo DOI) is created from the tag. Nothing in this plan promises
acceptance, publication, or admission outcomes.
