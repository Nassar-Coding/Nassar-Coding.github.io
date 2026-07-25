# Next-Day Municipal Service-Demand Forecasting Across Four Cities
### A Benchmark with a Controlled Simulated Capacity-Allocation Evaluation — companion repository

Reproducible four-city benchmark of next-day reported 311 service demand
(New York, Chicago, San Francisco, Austin; 2020–2025) coupled to a
controlled request-equivalent capacity-allocation simulation. This is the
public archival release for the IEEE BigData 2026 submission.

- **Release:** tag `RELEASE_TAG_PENDING` at commit `RELEASE_COMMIT_PENDING`
- **Archival DOI:** `DOI_PENDING` (minted on deposit; see CITATION.cff)
- **Final PDF hashes:** `PDF_SHA256SUMS.txt` — computed only at release build time, after the DOI/URL/tag above are inserted and both PDFs rebuilt; any hash quoted before that step is INTERIM and non-final
- **Corrections record:** `CORRECTIONS.md` (includes the R1-F1
  pooled-censoring correction; pre-correction outputs are under
  `audit/pre_fix_outputs/`)

## What is claimed — and not claimed

This is a predictive and *simulational* study. The allocation layer is a
transparent simulation over abstract request-equivalent capacity units
under hypothetical service-pressure regimes; none of its parameters
estimates any city's actual capacity, productivity, or queues, and it is
not a deployment and implies no city involvement or endorsement.
Forecast targets are *reported* request volumes, which under-represent
need in less-reporting communities. The protocol (frozen training-only
budgets, validation-only selection, temporal censoring of pooled and
transfer training, same-model uncertainty contrast) is enforced by an
automated guard suite (`tests/test_guards.py`, guards G1–G16, 37 tests)
that fails the build on violation.

## Requirements

- **CPU only — no GPU is used or required.**
- Python 3.11 (pinned environment: `reproducibility/pip-freeze.txt`).
- ~2 GB disk for the repository incl. frozen raw aggregates and outputs;
  ~4 GB free recommended during the build. 8 GB RAM is sufficient.
- Download size: the repository clone (frozen aggregates included; no
  external data download is needed for the full build).
- End-to-end runtime (`make all` from the frozen raw layer): roughly
  30–60 minutes on a 4-core laptop-class CPU; the optional κ-granularity
  sweep (`make kappa`) adds a comparable amount.
- LaTeX (pdflatex + bibtex, e.g. TeX Live) to compile the PDFs; the IEEE
  class/style files used by the build are committed in `paper/`.

## Quick start

```bash
pip install -r reproducibility/pip-freeze.txt   # pinned environment

# smoke test (seconds): core tests + code-level guards
python -m pytest tests -q

# verify frozen input integrity against the committed manifests
python scripts/verify_manifests.py

# full pipeline from the frozen raw layer:
# panel -> features -> forecasts -> simulated decisions -> inference -> artifacts
make all
python scripts/run_diagnostics.py     # trend diagnostic
python -m pytest tests -q             # full 37-test guard suite must pass

# optional additional sensitivities reported in the paper/supplement
make kappa                            # global kappa-granularity sweep
python scripts/run_weather_causal_sensitivity.py

# compile the manuscript and supplement
export SOURCE_DATE_EPOCH=1780963200   # pins PDF timestamps for byte-stable builds
cd paper       && pdflatex main_ieee && bibtex main_ieee && pdflatex main_ieee && pdflatex main_ieee
cd ../supplement && pdflatex supplement && pdflatex supplement
```

Expected end state: 37/37 tests pass; regenerated tables and figures are
byte-consistent with `outputs/` (provenance hashes are re-derived and
checked by guard G11); the compiled main paper is 10 pages, and both PDFs
match `PDF_SHA256SUMS.txt` up to embedded timestamps.

## Frozen data vs. live portals (important)

The raw layer under `data/raw/` is **frozen** at the acquisition
timestamps recorded in the manifests. City 311 portals backfill and
revise historical records continuously, so re-running the acquisition
scripts against the live portals WILL yield slightly different counts.
Every number in the paper is defined against the frozen layer. Live
re-acquisition (`make acquire-weather`, `make acquire-311`) is provided
for refresh studies, not for reproducing the paper, and requires network
access to the portals.

Determinism: global seed `20260609`; the decision layer is
Monte-Carlo-free (the random tie-break arm averages 20 fixed seeds).

## Layout

```
configs/         data sources, family harmonization, frozen decision protocol
src/             acquisition / preprocessing / features / forecasting /
                 optimization / evaluation
scripts/         experiment drivers, inference, artifact generation
tests/           core tests + protocol guards (G1–G16; 37 tests)
data/raw/        frozen daily aggregates + JSON provenance manifests
outputs/         metrics, tables, figures (+ provenance hashes)
audit/           pre-correction outputs retained for audit (CORRECTIONS.md)
reproducibility/ pinned environment (pip-freeze) and execution evidence
paper/           manuscript source and final PDF; supplement/ likewise
```

## Licensing

Code: MIT (`LICENSE`). Data redistribution terms per source:
`DATA_LICENSES.md`. Citation metadata: `CITATION.cff`.
