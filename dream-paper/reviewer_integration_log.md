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

## Group 3 — Related Work, Positioning & Prior-Paper Removal

- **G3-T1** — five recent references added, EVERY one verified against an
  authoritative source before entering `references.bib` (verification via
  publisher-domain-restricted searches after the subagent verification
  fan-out hit a session limit; the arXiv/DBLP/Crossref APIs are blocked by
  the sandbox proxy):
  | Key | Verified at | Facts confirmed |
  |---|---|---|
  | ning2023uukg | proceedings.neurips.cc + OpenReview (u2cXRGm95Y) | authors Ning/Liu/Wang/Zeng/Xiong; NeurIPS 2023 D&B; two cities NYC+Chicago; 5 USTP tasks incl. 311 prediction |
  | liu2023largest | proceedings.neurips.cc + neurips.cc poster 73480 | 10 authors match; NeurIPS 2023 D&B; 8,600 CA sensors, 5 years 2017–2021 |
  | tang2024pyepo | link.springer.com (10.1007/s12532-024-00255-x) | Tang & Khalil; Math. Prog. Computation 16:297–335 (2024); shortest-path/knapsack/TSP suites |
  | sadana2025survey | arXiv 2306.10374 + EJOR listing | 6 authors match; EJOR 320(2):271–289 (2025) |
  | rostamitabar2025hierarchical | journals.sagepub.com (10.1177/10946705241232169) + robjhyndman.com | JSR 28(2):278–295 (2025); ambulance demand, coherent point+probabilistic forecasts for deployment planning |
  Placement: PyEPO + Sadana in "From prediction to decisions" (synthetic-
  testbed positioning); LargeST + UUKG in "Cross-city learning and urban
  computing" (accuracy-only benchmark positioning); Rostami-Tabar &
  Hyndman in "Capacity planning" (recent public-sector forecasting).
  Deltas stated concretely in prose. DONE.
- **G3-T2** — comparison table added (`tab:positioning`, table*,
  scriptsize): rows Xu 2017 / Cheng 2022 / UUKG 2023 / LargeST 2023 /
  Mandi 2024 / this work; axes data scope, evaluation focus,
  forecast→allocation layer. Every row fact spot-checked against the
  verification evidence above or the already-verified existing prose
  (Xu "motivated, not evaluated" was verified in the Stage-1 audit;
  Cheng volumes+correlates from the bib entry; UUKG/LargeST accuracy-only
  from their verified abstracts; Mandi stylized/synthetic from the JAIR
  abstract and our existing verified prose). DONE.
- **G3-T3** — ALL prior-study mentions removed. related.tex II(a):
  positioning content retained at literature level, no self-attribution
  ("The present work brings this template to municipal reported demand at
  multi-city scale and extends it in kind: …"). data.tex IV(c): wind
  exclusion justified by data facts alone (SF station does not report
  wind; Central Park multi-month gap) + pointer to the repository's
  decision log (fact-checked: D15 in docs/04_decision_log.md documents
  exactly this). Grep for all six terms returns ZERO hits across
  manuscript + supplement + README. No factual claim left unsupported
  (the old "differs from" sentence was rewritten so its referent is the
  literature template, not the removed prior study). DONE.

**GATE 3: PASS** — all new bib entries verified real (table above);
citations resolve (0 undefined; 25 references); comparison-table claims
spot-checked; prior-study grep zero across manuscript+supplement; guards
37/37; protected wording intact.

**RED-pair carryover to G4-T4 (explicit):** after the Group 1–3
additions the compiled paper is 11 pages with a 34-line reference tail
on page 11 (~10.3 effective). Levers already applied: prose compression
(~12 lines: intro hierarchy/roadmap, data selection-criteria
parenthetical incl. removal of internal "decision D14" jargon,
formulation motivation), positioning table at scriptsize, IEEE BSTCTL
author truncation (et al. after 6 names — standard IEEE mechanism,
IEEEtranN supports it; 19 et-al entries in the bbl). Remaining levers
for G4: caption shortening (G4-T2), reproducibility-statement rewrite
(G4-T3), em-dash rewrites (G4-T1), small figure-width reductions if
needed (logged as an extra lever beyond the tracker's list — legibility
unaffected for vector PDFs). No claim-bearing evidence cut anywhere.

## Group 4 — Style, Length & Presentation

- **G4-T1 (em dashes)** — count logged: **50 (baseline) → 0**. Every
  prose `---` rewritten as parentheses, commas, colons, or semicolons
  with meaning unchanged; numeric en-dash ranges (`10.0--14.0`,
  `92--100\%`, etc.) untouched. DONE.
- **G4-T2 (captions)** — shortened: Fig. 1 (interpretive second sentence
  moved out; the observation lives in the body), Fig. 3 (6 lines → 4),
  Fig. 4 (minor), Table II/tiebreak caption (interpretive sentence
  removed; it duplicated protected body text which remains), and the
  generated Table `tab:data` caption shortened **in both**
  `sections/data_stats.tex` and its generator
  `scripts/make_paper_stats.py` (kept identical); G15-guarded strings
  preserved ("Chicago has seven" present in fragment+generator; no
  "families per city"). Grayscale legibility unaffected. DONE.
- **G4-T3 (reproducibility statement)** — rewritten in `main_ieee.tex`
  (and `main.tex` for consistency) to name THIS paper's concrete
  artifacts, fact-checked against the repo: one command = `make all`
  (verified Makefile target), acquisition scripts with exact query URLs,
  SHA-256 manifests, frozen-budget + pooled-censoring proof manifests,
  deterministic seeds, 16-guard/37-test suite. DONE.
- **G4-T4 (page budget)** — **final: 10 physical pages, hard venue limit
  ≤ 10.0 MET**; page 10's right column ends at reference [25] with about
  a quarter column of whitespace (verified visually), leaving room for
  the one line Group 5 adds. **Recorded buffer target: ≤ 9.75 was the
  recommendation; it was NOT reachable without cutting claim-bearing
  evidence** (the Group 1–3 additions — hierarchy, RQ, roadmap, data
  preview, I/O/G pattern, motivation, five verified references, and the
  positioning table — are all reviewer-mandated). Levers used, in order:
  prose compression across intro/data/formulation/methods/responsible/
  limitations/robustness (incl. removal of internal "decision D14"
  jargon), scriptsize positioning table, IEEE BSTCTL et-al author
  truncation (6 then 3 names — standard IEEE production practice),
  caption shortening, reproducibility-statement rewrite, and small
  figure-width reductions (0.95→0.84–0.86 linewidth, vector PDFs,
  legibility unaffected). **No claim-bearing evidence, protected
  wording, or audited number was cut.** DONE.

**GATE 4: PASS** — full recompile (10 pp; 0 overfull; 0 unresolved
refs/citations; numeric citations intact); page count at the enforced
hard limit with recorded buffer rationale; guards 37/37; forbidden-token
scan clean ("staffing" appearing only inside the verbatim Green–Kolesar–
Whitt reference title, which the guard correctly does not scan and which
must not be altered); em-dash/caption changes verified (visual render of
page 10 + G15); ALL protected items intact (identity sentence, Chicago
4,184,157, calendar 10.0–14.0%, no "neutral objective", "recovers most
of the fixed-index gap", fairness caveat, bounded principle,
frozen-window wording, zero prior-study hits).

## Group 5 — Decisions (recorded here as the tracker's decision log)

- **G5-T1 — Foundation time-series baseline (Amazon Chronos-2): DEFERRED
  to the journal version.** Rationale: the binary-baseline prior decision
  (one serious guarded baseline or none — the Poisson GLM fills that
  role), the Stage-3 scope lock (no new experiments in this pass), and
  the fact that adding any model to THIS submission would reopen every
  audited number and re-trigger the full guard/provenance chain days
  before the deadline; that trade is an author call, and the tracker
  itself classifies it as such. NOT silently dropped: one honest
  future-work sentence added to the conclusion naming foundation TS
  models ("… evaluating recent time-series foundation models (e.g.,
  Amazon's Chronos-2) as additional forecasting baselines in a journal
  extension"), +1 line, compiled (still 10 pages), guards 37/37.
  Chronos-2's existence verified (Amazon Science announcement;
  amazon/chronos-2 on Hugging Face) before naming it in print; no
  citation added (future-work mention, not a result claim; keeps the
  bibliography inside the page budget).
- **G5-T2 — Journal-version plan (post-submission): RECORDED.** Target
  venues per Khamis: Sustainable Cities and Society (Elsevier) and the
  International Journal of Forecasting (Elsevier). Required additions
  for the journal version: (a) clarified research objectives (largely
  addressed by Group 1; revisit against journal scope), (b) strengthened
  novelty discussion vs. recent literature (Group 3 baseline to build
  on), (c) expanded broader implications of the findings, (d) the
  foundation-TS baseline candidate (Chronos-2, per G5-T1) plus the
  previously deferred deep/hierarchical baselines, with the guard suite
  extended to cover any new model, and (e) consider the richer
  service-time modeling / spatial disaggregation continuations named in
  the conclusion. TIMING: all journal work starts AFTER the conference
  decision; none of it consumed conference-deadline time in this pass.

**GATE 5: PASS** — both Decide tasks have recorded outcomes + rationale
(nothing silently dropped); the one manuscript line added is compiled,
guarded (37/37), and within the page target (10 pages held); the final
commit references all Task IDs; the tracker Status column is fully
filled (see `Reviewer_Task_Tracker_v2_status.xlsx`).

---

## MICRO-PASS v3a (M1/M2/M3) — post-integration bounded fixes

- **M1 (Fig. 2 baseline consistency): DONE** (commit d3ddcfe). Code
  evidence: `scripts/make_tables_figures.py:117-118` — the % reduction
  denominator is `model == "naive_trailing7"` (internal feature set),
  i.e., the trailing 7-day mean; line 119 computes `100·(1 − sel/naive)`.
  Surfaces now naming it explicitly: y-axis label ("% test-MAE reduction
  vs trailing 7-day-mean baseline (validation-selected model)"), the
  Fig. 2 caption ("versus the trailing 7-day-mean baseline"), and the one
  body sentence naming this baseline (results_decision "Replacing the
  trailing 7-day-mean baseline…"). No body sentence cites
  `\ref{fig:gain}` (verified). Bare "naive" removed from the label. Bars
  unchanged: regeneration from frozen metrics left every table
  byte-identical (only figure re-renders + provenance hashes moved).
  Seasonal-naive 41.4/41.5/31.3/31.3 untouched.
- **M2 (IEEE cross-reference style): DONE** (commit 998d33a). All 22
  in-prose arabic section references converted to `\ref{sec:…}` against
  11 new labels in both `main_ieee.tex` and `main.tex` (shared sections
  render Roman in the IEEE build, arabic in the article build — each
  matching its own headings). Compiled IEEE text: `Section [0-9]` = 0
  hits; targets verified (V=Methods, VII=Decision ×6, VIII=Robustness
  ×4; ranges III–V, VI–VII, IX–XI). Supplement: two main-paper
  references hardcoded Roman (Sections VII–VIII; Section VII); its one
  self-reference uses `\ref{ssec:compute}` and stays arabic BY DESIGN —
  the supplement's own headings are arabic (article class), so Roman
  would mismatch headings, contradicting M2's stated purpose.
- **M3 (page-buffer via figure geometry): ATTEMPTED ONCE, FAILED,
  REVERTED CLEANLY.** Attempt: Fig. 1 panel height 1.9→1.45 in, Fig. 4
  height 2.6→2.1 in, `\textfloatsep`/`\floatsep` (+dbl) tightened to
  6pt. Result: page 10 fill 108→95 lines, references ending ~58% down
  the right column ≈ **9.79 effective pages** — recovery ≈ 0.09 page,
  short of both the ≥0.25-page aim and the ≤9.75 DoD. Per the
  one-attempt rule: **buffer unreachable via figure geometry**; all M3
  changes reverted (script, preamble, figures, provenance restored to
  the M2 state; rebuild verified 10 pages, byte-size identical build).

**GATE M: PASS** — 10 pages exactly (≤10.0); 0 overfull; 0 unresolved
citations/references; guards 37/37 after every task; forbidden scan
clean; frozen numbers all present and unchanged (36.8M/30.2M;
10.0–14.0% + 10.2–15.6% both labeled; Chicago 4,184,157; exclusion
components 523,055/4,184,157/1,918,574 — their 6,625,786 total was never
printed as a single number before or after this pass; 92–100%; 1.2–58%;
−0.03..+0.8%; 18–23/38–70/60–93%; Spearman 0.88–0.99; budgets
119/153/187, 29/38/46, 26/33/41, 8/11/13; κ=50); protected-wording
checklist fully intact; diff since pre-pass commit `edeae2b` touches
only M1/M2 surfaces (M3 net-zero).

---

## MICRO-PASS v3b (N1/N2/N3)

*(Executed in a fresh container after an environment reset: the clone
came up on the stale default branch; restored `draft_3` @ b8f8fca,
reinstalled the toolchain, rebuilt the regenerable `data/interim` /
`data/processed` layers deterministically from tracked raw data, and
verified a byte-identical baseline compile and guards 37/37 before any
edit.)*

- **N1 (Table III city labels): DONE** (2f3103f). Fixed at the generator
  source (`make_tables_figures.py`, `table_tiebreak`): display map
  austin→Austin, chicago→Chicago, nyc→NYC, sf→SF applied to the City
  column before emit; fragment + CSV regenerated (never hand-edited).
  Numeric grid verified identical (pandas equality on all non-City
  columns). Caption clause appended: "NYC = New York; SF = San
  Francisco." Rendered check: Table III fits, no wrap, 0 overfull.
- **N2 (orphan paragraph letter): DONE** (4ffd17a).
  `\paragraph{Reproducibility statement.}` → `\paragraph*{…}` in BOTH
  main files; the IEEE build renders the same italic run-in without the
  letter. Statement text verified character-identical (hash of the span
  heading→bibliography). Compiled text: "a) Reproducibility" = 0 hits;
  all other a)/b) run-ins untouched.
- **N3 (abstract trim): DONE** (904a790). 430 → **221 words** (target
  200–250). All five MUST items survive meaning-intact; per-signal
  forecasting detail compressed to one summary sentence. **Dropped from
  the abstract only (all remain in the body):** calendar 10.0–14.0% and
  the 28-day block-bootstrap qualifier; the weather/pooling per-city
  specifics beyond the summary sentence; "all 12 city-regime settings" /
  naive fixed-index default sentence; budget-freezing and
  validation-only-selection mechanics; the "first-class design choices"
  bounded-principle elaboration (still in Sections I, VII, and XI); the
  NOAA-join clause. No new numbers; no strengthened claims.

**GATE N: PASS** — both builds recompiled (IEEE: **10 pages**, page 10's
right column ends ≈68% down ≈ 9.84 effective, slack ≈ one-third column;
article: 19 pp); 0 overfull; 0 unresolved; guards 37/37 after every
task; forbidden scan clean; every tracker frozen number present in the
body (abstract omissions listed above); protected wording intact
(identity sentence, equal request-equivalent, qualified "removes most of
the non-identification gap", both fairness caveats, bounded principle in
body, zero prior-study hits, no "neutral objective"); diff since
pre-pass b8f8fca limited to N1 surfaces (generator, tab11 fragment+CSV,
provenance, figure re-renders from the same frozen metrics, Table III
caption), N2 surfaces (two main files), and N3 (abstract.tex) plus
rebuilt PDFs.
