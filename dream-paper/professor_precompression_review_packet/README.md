# Pre-Compression Review Packet

**For internal review before IEEE BigData 10-page compression.**
Branch `claude/bigdata-revision`. Prepared 2026-06-17.

This packet collects everything requested for sign-off **before** the 10-page
compression is executed. The compression itself has **not** been done (it was
explicitly deferred pending this review).

## Contents

| File | What it is |
|---|---|
| `01_main_manuscript_precompression.pdf` | Current compiled main paper (single-column `article`, **17 pp**). This is the full, uncompressed manuscript with all repairs applied. |
| `02_supplement.pdf` | Current compiled supplement (**16 pp**) — exhaustive grids, sensitivities, harmonization composition, guard table, provenance. |
| `03_compression_plan.md` | The approved-pending 10-page compression plan: main-vs-supplement allocation preserving all required validity evidence; documents that the `article`→IEEEtran two-column conversion alone recovers most of the 17→10-page budget. |
| `04_status_checklist.md` | Row-by-row status of all 202 professor-review items (73 implemented / 95 already satisfied / 1 supplement / 28 journal / 3 rejected / 1 still-open=compression / 1 author=self-plagiarism diff). |
| `05_b0_sensitivity_summary.csv/.tex` | The initial-carryover (b₀) sensitivity summary: mean policy rank under b₀=0, validation warm-up, and training-average conditions. |
| `06_b0_sensitivity_full.csv` | Full per-cell b₀ sensitivity (city × regime × policy × condition × loss × rank). |

## Current status

- **Research and implementation are complete.** All four claim-gating
  experiments (tie-break/non-identification, conformal calibration,
  normalized/log pooling, horizon) were run on an exact reproduction of the
  pipeline; none forced abandonment. The central decision claim is the
  **objective non-identification** result (degenerate point forecasts collapse
  the marginal-value profile, so realized allocation loss is determined by the
  secondary tie-break rule); the old "point forecasts disable the optimizer"
  framing has been removed and is **not** restored.
- **b₀ sensitivity is now run and supports the formulation claim.** Under all
  three initial-carryover conditions the claim-bearing ordering (uniform worst;
  fixed-index point-greedy below the three identified policies) **held in 12/12**
  city-regime cells (changed in 0/12). The manuscript sentence stating b₀ is
  varied as a labeled sensitivity is therefore backed by evidence.
- **BigData framing has been added** — a concise 5V paragraph in the
  introduction (Volume / Variety / Veracity / Value; Velocity explicitly out of
  scope: no real-time, streaming, or deployment claim).
- **The only remaining IEEE BigData item is the 10-page compression** (plan in
  `03_compression_plan.md`). A literal self-plagiarism diff against the prior
  single-city paper still awaits that paper's text and is a final human-review
  item; no verbatim reuse was detected in current sources.
- **The repository remains private.** The clean public-release repository has
  not been made public.
- **No submission has occurred.** Nothing has been submitted anywhere.

## Verification at this snapshot

- Main paper and supplement compile (`pdflatex`); 17 pp / 16 pp.
- Guard suite: 16 protocol guards (G1–G16), **37-test suite passes (0 skipped)**;
  forbidden-token scan clean.
- `make all` reproduces every headline number to the digit; provenance manifest
  covers 58 artifacts.
