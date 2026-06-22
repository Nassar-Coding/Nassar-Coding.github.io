# Draft 3 — Stage 3B Overlap / Concurrent-Submission Memo

**INTERNAL DOCUMENT — never include on the public release branch.**
Branch `draft_3`.

## Literal overlap check

**Not possible in this stage — pending author action.** The prior single-city
NYC 311 paper's text is **not in the repository** (status: under secret review,
unpublished). No automated text-overlap/near-duplicate comparison can be run.
A scan of the current manuscript sources finds no verbatim block attributable
to that paper, but this cannot substitute for a literal diff against the prior
text, which only the author can supply.

## Author confirmations required before submission

The author must confirm, before submitting to IEEE BigData:

1. **Prior venue policy** — the venue where the prior single-city paper is under
   review permits an overlapping/concurrent related submission.
2. **IEEE BigData policy** — IEEE's policy on related, concurrently-under-review
   work has been checked and this submission complies (no duplicate submission
   of the same contribution).
3. **No verbatim / near-verbatim reuse** — a literal text-overlap check between
   the two papers (intro, methods, related work especially) confirms no
   unattributed reuse; any shared background is rewritten or properly cited.
4. **Shared findings framed as replication/extension** — the calendar/weather
   forecasting result that the prior single-city paper established is presented
   here as a multi-city replication/extension, **not** as new.
5. **Distinct primary contribution** — the current paper's primary contribution
   (the multi-city reproducible benchmark + the forecast-to-allocation
   non-identification / tie-breaking phenomenon and family-level tradeoff
   disclosure) is distinct from the prior paper's single-city forecasting
   finding.

## Manuscript handling (already done)

- The prior work is acknowledged in `related.tex` as "an earlier single-city
  study on NYC 311 by the present author."
- The delta is stated in prose (four cities; one leakage-controlled protocol;
  local-vs-pooled and censored transfer; forecast-to-decision coupling;
  non-identification / tie-breaking; family-level tradeoff disclosure; stronger
  provenance/guards).
- **No formal citation was fabricated.** The formal citation is a **pending
  author action** to be added once the prior paper is citable (single-blind
  permits the self-citation then).
