# Draft 3 — Stage 3B Report (page buffer, memos, completeness sweep)

**INTERNAL DOCUMENT — never include on the public release branch.**
Branch `draft_3`; from Stage 3 commit `85c9ede`.

## A1. Page-count reduction

- **Before:** content filled essentially the full 10 pages.
- **After:** effective **~9.1–9.2 pages** — measured with `mutool`: the PDF is
  10 physical pages but page 10 holds only **17 non-empty lines** (the references
  tail) versus ~120 on a full page, i.e., page 10 is ~86% empty. Under the 9.75
  hard max with comfortable buffer. No overflows; no undefined references.
- **Text-only compressions (no evidence removed):** intro 5V paragraph
  tightened (all five V's, the daily-panel modeling-unit clause, and
  Velocity-out-of-scope retained); boundary paragraph condensed; responsible-use
  closing sentence removed (its substance is in Limitations); conclusion
  continuations shortened.
- **Preserved (verified):** abstract identity sentence; prior-work delta;
  non-identification obviousness defense; bounded central principle; Table II
  (`tab11`) non-identification evidence; family-starvation disclosure; A2
  frozen-window wording; calendar 10.0–14.0%; Chicago 4,184,157; equal-request-
  equivalent wording; numeric IEEE citations.
- **Caveat-trim guard:** all five load-bearing hedges still present (fairness
  guarantee 4×; simulation/not-deployment 3×; reported-demand-not-need 4×;
  request-equivalent-capacity-not-real-workforce 1× in intro; no-causal/
  endorsement 2×). (Note: a guard caught an accidental "staffing/crews" phrase
  introduced during the trim — both are forbidden tokens — reworded to "a real
  workforce measure".)

## A2. Prior single-city paper

Unchanged from Stage 3 and consistent with the AUTHOR-PROVIDED INPUTS
(under review, unpublished). Prose delta only in `related.tex`; **formal
citation is a pending author action** (not fabricated). Distinguished on: four
cities; one common leakage-controlled protocol; pooling/transfer evaluation;
forecast-to-decision simulation; non-identification/tie-breaking; family-level
tradeoff disclosure; stronger reproducibility/provenance.

## A3. Overlap / concurrent-submission memo

Created `draft3_stage3b_overlap_memo.md`. **Literal overlap check: pending
author action** (prior paper text not in repo). The memo lists the five author
confirmations required before submission (prior-venue policy; IEEE BigData
policy on concurrent under-review work; no verbatim reuse; shared findings
framed as replication/extension; distinct primary contribution).

## A4. Completeness sweep (40-item plan)

| Item | Status |
|---|---|
| #25 "What this paper does / does not claim" box | **Substance present as prose**, not a dedicated box: intro ("no causal, deployment, or operational-guidance claim"), abstract ("not a deployment or fairness claim"), boundary paragraph. Dedicated box **consciously omitted** (page budget); recommend adding a 1–2 line box only if the cold read asks for it. |
| #31 Assumptions A1/A2/A3 callout | **A2** (one weather station per city; spatial simplification) and **A3** (target-day weather as a day-ahead proxy) are labeled where they bear on results (`data.tex`, `formulation.tex`, `limitations.tex`, `robustness.tex`). **A1 is not separately labeled**; the two material stochastic-input assumptions are A2/A3. A consolidated A1–A3 box is a **conscious omission** (page budget). |
| #33 IRB / data-governance | **Present** (supplement `s_ethics`: "All inputs are public administrative aggregates … No individual-level, household-level, or address-level information"); public aggregate open data, so no IRB applies. Main paper notes public open-data provenance. |
| #34 Compact family-composition note | **Present** — `data.tex` points to the per-city native-category composition of every family; full composition tables in supplement (`s_harmonization` / `family_composition_{city}`). |
| #16 Figure 4 legibility (grayscale) | **Legible** — compiled Figure 4 (accuracy-vs-decision) is a single-hue scatter grid (grayscale-safe); the fold-stability figure uses three line styles/shades distinguishable in grayscale. No change needed. |
| #17 Table 2 two-column legibility | **Legible** — `tab11` is a full-width `table*` at `\footnotesize`, fits the two-column layout (no overflow). |
| #32 Null/negative results as findings | **Present** — Austin weather null ("a retained null"), pooling/transfer "mostly hurt / negative result … retained," reported as findings. |

No new experiments or numbers were added to satisfy these (per instruction).

## A5. Author-decision gates (recorded; not acted on)

1. **Reviewer access to the artifact.** The repository is private; the
   reproducibility/veracity contribution is unverifiable unless reviewers can
   reach the artifact. **Author chooses at submission** among: (a) make the clean
   public-release repo public; (b) an access-controlled reviewer link
   (e.g., anonymous.4open.science or a private invite); or (c) a frozen
   Zenodo/DOI release of the exact paper commit. **No visibility change was made
   in this stage.**
2. **AI-use disclosure.** Substantial AI assistance (including manuscript prose)
   was used. IEEE has an AI-disclosure policy; the author must confirm the exact
   current requirement on IEEE's author guidelines and add an appropriate
   disclosure before camera-ready/submission. **Draft one-liner for author
   review (not finalized):** *"The author used an AI assistant (a large language
   model) for drafting, editing, and code-scaffolding support; the author
   verified all data, experiments, numbers, and final claims and takes full
   responsibility for the content."* Do not finalize wording unilaterally.

## A6. Cold-read packet

`draft3_stage3_cold_read_packet.md` is complete and self-contained (title,
abstract, four contribution bullets, related-work delta, decision-section
summary, conclusion, the ten reader questions, reader instructions). **Not
conducted; not simulated.**

## A7. Recompile / verification

- IEEE `main_ieee.pdf`: 10 physical pages, **effective ~9.1–9.2** (page 10 ~86%
  empty); no overflows; **0 undefined citations/references**; numeric IEEE
  citations intact.
- Supplement: 16 pp (untouched this stage).
- Guards: **37 passed, 0 skipped**; forbidden-token scan clean.
- No weather/window regression (frozen pinned-layer wording intact).
- No distribution=proportional equivalence overclaim ("recovers most of the
  gap").
- All Stage 1/2B/3 fixes intact (re-verified).
- Claim–evidence audit re-run after the trim: **PASS**
  (`draft3_stage3_claim_evidence_audit.md`, Stage 3B section).

## A8. Stop gates

None triggered. (One guard correctly failed mid-stage on an accidental
"staffing/crews" phrase; fixed; guards green.)

## Final git status

Clean (only untracked regenerable `data/processed`, `data/interim`).
