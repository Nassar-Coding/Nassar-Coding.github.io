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

## Group 5 — Decisions (recorded here as the tracker's decision log)

*(filled in when Group 5 executes)*
