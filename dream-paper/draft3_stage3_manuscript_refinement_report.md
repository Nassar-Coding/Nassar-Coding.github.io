# Draft 3 — Stage 3 Manuscript Refinement Report

**INTERNAL DOCUMENT — never include on the public release branch.**

1. **Branch:** `draft_3`.
2. **Starting commit:** `4a80e9b` (Stage 2B).
3. **Final commit:** this commit (see chat).

4. **Title before/after:** unchanged — "Next-Day Reported Municipal
   Service-Demand Forecasting Across Four Cities: A Reproducible Benchmark with
   Simulated Allocation Evaluation." It already hooks multi-city, reported
   municipal service-demand forecasting, reproducible benchmark, and simulated
   allocation evaluation, and retains "Next-Day" (v2 preference). No change
   needed.

5. **Abstract before/after:** before — opened on motivation, ended on the vague
   "representation can matter as much as accuracy," no fairness caveat. after —
   opens with the identity sentence; foregrounds the 4-city benchmark, reported-
   demand-not-need + simulation-not-deployment boundary, calendar 10.0–14.0% /
   weather / pooling results, non-identification (92–100% ties) with the
   naive-default framing, the two recovering remedies (proportional rule recovers
   proportional; distribution recovers *most of* the gap), the bounded principle,
   and the fairness caveat. All audited numbers preserved.

6. **Identity sentence added:** "We present a reproducible multi-city benchmark
   for next-day reported municipal service-demand forecasting and evaluate how
   forecast representations behave when embedded in a controlled
   request-equivalent allocation simulation." (abstract opener + intro para 1.)

7. **Contribution bullets before/after:** before — "exactly three contributions"
   (benchmark / forecasting eval / decision study), partly result-flavored.
   after — four ordered groups: (1) Benchmark & protocol; (2) Forecasting
   evidence (incl. Poisson, negatives/nulls); (3) Forecast-to-decision
   evaluation (non-identification, tie-break dependence, distribution recovers
   most of the gap); (4) Responsible use & veracity (reported≠need, loss≠fairness
   with family disclosure, provenance/guards).

8. **Prior single-city paper positioning / citation status:** handled by
   **prose delta** in `related.tex`; **formal citation is a pending author
   action** (the prior NYC 311 paper is under review/unpublished, so per the
   AUTHOR-PROVIDED INPUTS rule it is not fabricated). Single-blind permits the
   self-reference once available.

9. **How the current paper differs from the prior single-city paper** (in
   `related.tex`): four heterogeneous 311 systems under one leakage-controlled
   protocol (vs one city); local-vs-pooled and temporally censored cross-city
   transfer; forecast-to-decision coupling via a controlled allocation
   simulation (vs stopping at accuracy); non-identification / tie-break analysis
   and family-level served-fraction disclosure; and a stronger provenance- and
   guard-backed reproducible benchmark. Stated without overstating novelty.

10. **Non-identification "obviousness" defense (added, ~3 sentences,
    `results_decision`):** "That ties arise under a symmetric coverage objective
    is not in itself surprising; the empirical question is whether this
    non-identification is rare enough to ignore or pervasive enough to govern the
    downstream conclusion. On real multi-city municipal data it is pervasive ---
    92–100% of allocation steps are ties … across four heterogeneous demand
    structures." The 1.2–58% cost is presented as the cost of the naive
    fixed-index default that the remedies recover.

11. **Central-claim reframe text (`results_decision`, abstract):** "When
    forecasts feed a discrete coverage-type objective with symmetric per-unit
    value, predictive representation and the secondary tie-break rule are
    first-class design choices, not implementation details … stated only for the
    tested objective, regimes, reported municipal demand, and simulated
    request-equivalent allocation; a forecast-to-decision design phenomenon, not
    deployment evidence." Replaced the vague "representation matters as much as
    accuracy."

12. **Decision-section edits:** added the obviousness defense and the bounded
    principle; kept the controlled-scenario framing (not deployment/staffing/
    causal, equal request-equivalent weights not normatively neutral, loss ≠
    fairness) while asserting the finding confidently (tone: bounded scenario,
    real design lesson). The family-starvation cross-reference (Stage 2B) is
    intact.

13. **Related-work edits:** expanded the prior-work delta; retained the gap
    statement ("no prior work evaluates 311 forecasting across multiple cities
    under one protocol, nor couples it to an explicit allocation loss"); no new
    citations added (no bloat).

14. **Conclusion edits:** removed the "distribution recovers proportional
    performance" equivalence overclaim → "recovers most of the fixed-index gap";
    added the family-level-tradeoff sentence and the "report boundaries and
    failure modes, not only aggregate gains" close. No forbidden terms.

15. **BigData framing edits:** none needed — the concise 5V paragraph (Volume
    with daily-panel modeling-unit clause, Variety, Veracity, Value, Velocity out
    of scope) is intact and non-defensive.

16. **A2 frozen-window wording verification:** intact — `data.tex`,
    `data_stats.tex` caption, and `s_tables.tex` use the frozen pinned-layer
    framing; scan for "bounded by NOAA / weather availability / weather-bounded"
    is clean.

17. **Stage-1/2B fixes intact:** abstract 10.0–14.0% (1 occurrence), no `8.6--14`
    anywhere; Chicago info-only 4,184,157, no `4,184,158` / `6,625,787`; no
    "neutral objective"; numeric IEEE citations intact; family-starvation
    disclosure + headline cross-reference present; A2 frozen-window intact.

18. **Modern-baseline decision (deferred):** no baseline added in Stage 3.
    Recorded as a **post-Stage-3 decision gate**: add at most one serious modern
    baseline only if the cold reader still reads the paper as "LightGBM on 311
    data / dated baselines"; otherwise fix framing, not models.

19. **Special-session fit (record only):** the reframed multi-city / forecast-to-
    decision / public-sector-data identity could fit an urban-data special
    session; **no route change is made** — default remains main IEEE BigData, and
    any switch requires the official current CFP (Stage 2B decision).

20. **Page count before/after:** 9 pp → **10 pp** (IEEE, references included; no
    overflows). The design-commitments paragraph was compressed to keep within
    budget; further headroom (5V/caveat tightening) exists if final formatting
    needs it.

21. **Guard/test result:** `pytest tests -q` → **37 passed, 0 skipped**;
    forbidden-token scan clean; numeric citations resolve (0 undefined).

22. **Stop gates:** none triggered. Prior-work delta is defensible without
    overstating novelty (citation pending, not a stop); paper at 10 pp (not
    over); non-identification neither overclaimed nor trivialized; decision
    section not over-hedged; no forbidden claims; Stage-1/2B fixes preserved;
    compiles; citations intact.

## Verdict

**Stage 3 complete — proceed to external cold read and final submission
compliance.** Claim–evidence audit: **PASS** (`draft3_stage3_claim_evidence_audit.md`).
Cold-read packet prepared (`draft3_stage3_cold_read_packet.md`).
