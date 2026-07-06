# Reviewer Task Tracker v2 — Integration Log (Khamis & Fatimah)

**INTERNAL DOCUMENT — never include on the public release branch.**
Branch `draft_3`, starting from commit `d274829` (clean tree verified).
This log is the traceability record required by the tracker's Rules sheet:
every edit maps to a Task ID; gates record PASS/FAIL with evidence.

Em-dash baseline (before any Group 4 work): 50 `---` occurrences across
`paper/sections/*.tex` (abstract 3, conclusion 2, data 9, data_stats 3,
formulation 6, introduction 7, responsible 2, results_decision 11,
results_forecast 4, robustness 3).

Prior-study mention baseline: exactly 2 locations
(`related.tex` lines 5–7 "An earlier single-city study … present author";
`data.tex` line 60 "single-city study this work extends"); supplement clean.

Page baseline: 10 physical pages, page 10 at 17/109 non-empty lines
(~9.16 effective) before Group 1.

---

## Group 1 — Contribution & Identity Alignment

**Hierarchy (written once, per G1-T2):**
1. **Primary artifact** — the reproducible four-city benchmark: harmonized
   data + leakage-controlled protocol + guard suite, one-command
   regeneration; its evaluation protocol includes the controlled
   request-equivalent allocation simulation as a *measurement instrument*
   (a component of the benchmark, not a standalone simulation study).
2. **Headline empirical finding** — degenerate point forecasts leave the
   equal request-equivalent objective non-identified (92–100% of steps
   tied), so the secondary tie-break rule sets the realized outcome; a
   proportional secondary rule recovers proportional performance and a
   genuine predictive distribution removes most of the non-identification
   gap.
3. **Supporting evidence** — the forecasting layer (calendar, weather,
   pooling/transfer, uncertainty, Poisson baseline, retained nulls).
   *Responsible use* is a property of the protocol (practice), not a
   numbered contribution.

- **G1-T1** (`introduction.tex`) — the governing question is now the single,
  explicitly labeled research question: "The single research question of
  the study, the question this instrument is built to answer, is: …".
  No second question exists. DONE.
- **G1-T2** (six locations) — title (unchanged, already states
  benchmark-primary + allocation-evaluation instrument), abstract ("the
  paper's primary artifact"; "yields the paper's headline finding"),
  introduction (hierarchy paragraph above), Sec VII(b) ("the paper's
  headline finding, the result the benchmark's decision-evaluation
  instrument exists to measure"), conclusion ("the benchmark and its
  protocol are the primary contribution. The headline finding is what the
  coupled simulation reveals … The supporting forecasting evidence …").
  DONE.
- **G1-T3** (`introduction.tex`) — four co-equal numbered bullets replaced
  by the explicit hierarchy; responsible use recast as "enforced as a
  property of the protocol rather than claimed as a contribution". DONE.
- **G1-T4** (title) — verified aligned with the chosen hierarchy; PRIOR
  DECISION respected (short, retains "Next-Day"). NO CHANGE NEEDED
  (recorded rationale: the title already promises exactly the hierarchy:
  reproducible benchmark primary, simulated allocation evaluation as the
  instrument).
- **G1-T5** (`introduction.tex`) — explicit artifact-type sentence: "The
  artifact is a benchmark (data, protocol, and automated enforcement), not
  a data collection alone; … this simulation is a measurement instrument
  of the benchmark, not a standalone simulation study." DONE.
- **G1-T6** (`introduction.tex`) — roadmap paragraph added at the end of
  the Introduction (Sections 2–11). Also fixed the vague "(Section on
  methods)" to "(Section~5)". DONE.
- Incidental (supports G4 later): conclusion's em-dash pair converted to
  parentheses; stale "The corrected evidence supports" phrasing (internal
  revision jargon a reviewer cannot parse) replaced by hierarchy phrasing.

**GATE 1 evidence:** compile clean (10 pp, page 10 at 36/109 lines ≈ 9.30
effective; 0 overfull; 0 undefined refs); guards 37/37; protected wording
greps pass (identity sentence, request-equivalent, no "neutral objective",
"removes most of the non-identification gap", fairness-guarantee caveat);
fresh-read coherence panel: **3/3 independent fresh-read judges PASS**
(lenses: hierarchy-consistency, competing-questions, promise-vs-delivery;
zero contradictions reported; all three inferred the identical hierarchy
unprompted). Two minor non-blocking observations recorded: (a) the RQ is
grammatically compound (both clauses are answered, VII(b) and VII(d)); (b)
the abstract's opening coordinates two verbs but the explicit labels two
sentences later resolve primacy.

**GATE 1: PASS** (compile clean, guards 37/37, protected items intact,
coherence panel 3/3).

## Group 2 — Problem Formulation & Technical Exposition

- **G2-T1** (`formulation.tex`) — section rewritten for a non-OR reader:
  new "Data in brief" opener; plain-language walk-through added after the
  carryover align block ("In words: each day's workload $w$ is new
  requests plus carried stock; …"); no definition, equation, or audited
  number changed (verified by the per-equation audit below). DONE.
- **G2-T2** — per-equation verification log (independent agents, each
  checking manuscript vs implementation, all verdicts CORRECT):
  | Equation / statement | Verdict | Key evidence |
  |---|---|---|
  | Carryover recursion w=b+y; resolved=min(w,κx); u=w−resolved; b′=(1−α)u; b₀=0; α=0 primary | correct | allocation.py:129,133,135–137,142; SimConfig α default 0.0 |
  | Decision loss L_c=ΣΣω_s·u; k-day request counts k times; ω_s=1 primary | correct | allocation.py:135–139,148; loss on u before abandonment |
  | Budget B_c=max(round(f·d̄_c/κ),\|S_c\|), f∈{0.7,0.9,1.1}, train-only mean, frozen pre-selection | correct | run_decision.py:79,84–91,122–125; decision.yml:7,10,13–15; frozen_budgets.json matches 119/153/187, 29/38/46, 26/33/41, 8/11/13; budgets independently recomputed from stored means |
  | Greedy exactly maximizes Σω·E[min(D,κx)]; concavity; ascending-index tie key | correct | allocation.py:94–114 (heap tuple gives index tie-break); brute-force optimality test test_core.py:100–115 |
  | Quantile-interpolated distribution: 99-pt grid [0.01,0.99], linear interp, clamped tails, implied mean = grid mean, median arm = .50 | correct | allocation.py:73,79,87–88; models.py:20; run_decision.py:148–156,211–213 |
  | Proportional = largest-remainder of ŷ+b; uniform forecast-free; full budget always | correct | allocation.py:51–62,170–175; runtime assert alloc.sum()==units |
  | Protocol constants: 70/15/15; val-MAE selection + train+val refit; 28d/2000/seed 20260609 (14/56 sens.); κ=50; non-crossing cummax; 5 folds | correct | protocol.py:16,31; run_forecasting.py:138,142,271–287; decision.yml:59–62; models.py:90–93 |
  Rendering: visual inspection of pages 2–5 at high zoom — **clean, zero
  defects** (align block, eq. (2), the budget expression
  max{round(f·d̄/κ),\|S_c\|}, greedy objective, quantile superscripts;
  gutters ink-free, right edge exact, no overfull).
  NOTE (tracker "UNRESOLVED" field): the reviewer-clarification answer on
  whether Fatimah meant math/rendering/exposition is still pending; per
  the tracker instruction the rendering was checked regardless, and both
  math-vs-code and exposition were covered.
- **G2-T3** — "Data in brief" paragraph opens Section III, before the
  prediction task (reordering-free preview; Section IV not duplicated).
  DONE.
- **G2-T4** — input → output → goal opener applied to all five
  formulation subsections that define the pipeline (prediction task,
  allocation, policies, uncertainty contrast — plus the data preview),
  all five methods subsections, and the three main data paragraphs
  (12 openers total). Results/robustness sections are findings, not
  pipeline definitions; pattern not applied there (recorded scope
  decision). DONE.
- **G2-T5** — "Why a simulated allocation layer" motivation paragraph
  now precedes the mechanism ("Simulated allocation"), framing the
  simulation as a scientific instrument consistent with the Group-1
  hierarchy. DONE.

**GATE 2: PASS** — recompile clean (10 pp, 0 overfull, 0 undefined);
Sections III–IV visually inspected (self + independent inspector, zero
defects); every formula logged (table above); no audited number changed;
guards 37/37; forbidden scan clean; I/O/G pattern present (12 openers).

## Group 5 — Decisions (recorded here as the tracker's decision log)

*(filled in when Group 5 executes)*
