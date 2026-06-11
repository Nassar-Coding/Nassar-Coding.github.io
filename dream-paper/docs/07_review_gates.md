# Review Gates (post-rerun, pre-manuscript)

Three independent structured reviews of the corrected package
(run id `20260609-20260610T213950`, freeze commit `9dd97c2`,
rerun commit `02b1b6e`). Every check below was executed against the
actual artifacts; commands and outputs are reproducible from §16 of
`paper_redesign_implementation_report.md`.

---

## Gate 1 — Forecasting–Statistics–Optimization Methodologist review

### Checks performed and evidence

| Check | Evidence | Result |
|---|---|---|
| Leakage controls in features (lags/rolling end at t; deterministic calendar; A3 weather documented) | unit tests `TestLeakage` (4 tests pass) | OK |
| Validation-only selection; refit train+val; single test evaluation | G2 (artifact equals val-argmin; invariant to corrupted test metrics) | OK |
| Rolling-origin folds confined to pre-test data | unit test `test_rolling_folds_never_train_on_future` | OK |
| LOCO temporal censoring | G3: recomputed censor date equals artifact for every row | OK |
| U8 quantile fitting (train-only → val; train+val → test) | code path verified; val quantile rows present in val_predictions | OK |
| Same-model uncertainty arms | G4; arms differ only in distribution representation | OK |
| Greedy exactness for the per-day objective | brute-force equality test passes | OK |
| Moving-block bootstrap: circular MBB, percentile CIs, fixed seed, paired daily differentials | code review of `moving_block_bootstrap_ci`; block-length sensitivity 14/56 shows 0/48 conclusion flips | OK |
| Budget purity (train-only, perturbation-invariant) | G1 synthetic + artifact checks | OK |

### Findings

**F1 (minor, documented; new — found by this review).** Per-city 70/15/15
splits land on slightly different calendar dates (SF validation cutoff
2024-05-06; Austin 2024-05-05; Chicago/NYC 2024-05-04) because warmup and
weather-missingness drops differ by city. The pooled ("global") model's
train+validation data therefore include 1–2 calendar days of *other-city*
rows contemporaneous with the earliest Chicago/NYC test days (≤ ~48 rows,
≈0.1% of pooled training). Local models and the censored LOCO are
unaffected. Direction of bias favors the pooled model, so the
negative-transfer conclusion is conservative; the marginal SF
pooling-benefit estimate carries this caveat. Disposition (owner-directed, Amendment C11): DETECTED AND CORRECTED via
targeted pooled-model stage censoring — pooled validation-stage fits use
rows <= min train-end (2023-07-29), pooled test-stage fits use rows <=
min validation-end (2024-05-04); guard G13 added with a fit-time proof
manifest (123 / 24 rows censored); pooled/global outputs and all
downstream stages rerun. Post-fix: negative transfer significant in 3/4
cities (SF neutral); validation selection picks the LOCAL model in all
four cities for calendar+weather; the selection experiment shifted from
7/12 disagreements with 4 harms to 9/12 same-choice, 2 gains, 0 harms —
the earlier disagreement was substantially an artifact of the
contaminated pooled model's inflated validation scores.

**F2 (mechanism, explanatory — must appear in the manuscript).** Under
degenerate point-forecast distributions, once allocated capacity covers
point demand + carryover, every further unit has zero marginal expected
value, so placement of surplus units is deterministic but uninformative
(verified: budget-12/3-family example allocates surplus [6,3,3]). This is
the mechanism behind (a) the point-greedy policy's inferiority to
proportional allocation under equal weights and (b) the full
distribution's significant advantage within the greedy class (informative
tails break the ties). This is the consolidated-findings §6 mechanism,
now empirically confirmed rather than assumed.

**F3 (interpretation constraint).** The proportional-dominance result is
conditional on the equal-weights objective and the stylized carryover
dynamics; under the normative-weight sensitivity the ranking compresses.
The manuscript must state this conditionality wherever the result appears.

### Verdict: **PASS** — F1 detected and corrected (Amendment C11, G13);
F2 and F3 remain binding manuscript statements.

---

## Gate 2 — Data, Code, and Reproducibility audit

### Checks performed and evidence

| Check | Evidence | Result |
|---|---|---|
| Raw data integrity | SHA-256 manifests unchanged; NYC scanned==aggregated invariant; dual-path row-count cross-validation (D17) | OK |
| Source-ID / window consistency | G10 passes across data_sources.yml, raw manifests, panel manifest | OK |
| Determinism | rerun reproduced pre-redesign forecast values bit-exactly for unchanged configurations (e.g., NYC cal+weather LightGBM test MAE 165.416814 in both runs) | OK |
| Provenance / stale artifacts | G11: 22 artifact hashes match; run-id stamps for forecast and decision stages present; pre-redesign outputs isolated in `artifacts/stale_pre_redesign/` | OK |
| Environment pinning | reproducibility/pip-freeze.txt; Python 3.11.15 | OK |
| Run logs preserved | outputs/logs/rerun_{panel,features,forecasting,decision,inference,artifacts}.log committed | OK |
| Repository cleanliness | `git status --porcelain` empty at rerun commit `02b1b6e` | OK |
| Config-output agreement | G9 per-city scenario sets match config-derived expectation | OK |

### Findings

**F4 (minor, engineering).** `pd.Timestamp.utcnow()` emits FutureWarnings
under pandas 3.0.3 (functional; migration noted as post-gate maintenance,
not protocol-relevant). **F5 (note).** The full-history GHCN station files
are re-downloaded by `make acquire-weather`; NOAA may append data after
the manifest date — manifests pin what this study used; re-acquisition
drift is documented in the README.

### Verdict: **PASS** (F4/F5 are maintenance notes, not validity issues).

---

## Gate 3 — Responsible-AI and Public-Systems review

### Checks performed and evidence

| Check | Evidence | Result |
|---|---|---|
| No individual-level data anywhere | acquisition is server-side daily aggregation; raw layers contain (day, category, count) only | OK |
| Reported demand ≠ social need maintained | problem definition, claims registers; no needs language in outputs | OK |
| Neutral primary objective | equal weights primary (config); normative weights labeled illustrative sensitivity | OK |
| Family-level distributional visibility | served_fraction_by_family, loss_share_other in decision outputs | OK |
| Forbidden operational terminology in outputs | G7 passes over all tables | OK |
| Simulation-not-deployment enforced | spec, configs, code docstrings; manuscript guard (G8) armed for rewrite phase | OK |
| Austin `other` equity of treatment | dual treatment (retained-with-reporting primary; excluded-recalibrated sensitivity); ordering identical in both — Austin claims need not be narrowed | OK |

### Findings

**F6 (manuscript condition).** The proportional-dominance result is at
risk of being read as operational advice ("cities should just allocate
proportionally"). The manuscript must frame it strictly as a property of
the simulated environment under stated assumptions, never as municipal
guidance. **F7 (manuscript condition).** The known socio-spatial
reporting-bias literature must remain central in the responsible-use
section; city-level aggregation contains but does not eliminate the
bias-amplification channel.

### Verdict: **PASS WITH CONDITIONS** — F6 and F7 are binding manuscript
constraints, enforced at the closure review.

---

## Gate summary

| Gate | Verdict | Open items |
|---|---|---|
| 1 Methodologist | PASS | R1-F1 corrected (C11/G13); F2/F3 manuscript statements |
| 2 Data/Code/Repro | PASS | none blocking |
| 3 Responsible-AI | PASS WITH CONDITIONS | F6/F7 manuscript statements |

All three gates have passed. Manuscript rewriting is UNBLOCKED; F2, F3,
F6, F7 transfer to the manuscript-closure checklist.
