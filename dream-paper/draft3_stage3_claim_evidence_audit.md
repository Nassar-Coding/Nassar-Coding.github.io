# Draft 3 — Stage 3 Claim–Evidence Audit

**INTERNAL DOCUMENT — never include on the public release branch.**
Branch `draft_3`, post-Stage-3 edits. Two-direction audit; all numbers are the
Stage-1/2B audited values (no re-run).

## Direction 1 — claim → evidence

| Claim | Where | Evidence artifact | Status |
|---|---|---|---|
| Reproducible multi-city benchmark, 4 cities, 36.8M acquired / 30.2M retained | abstract, intro (1), data | `panel_manifest.json`, `tab17` | Supported |
| Calendar reduces next-day error 10.0–14.0% (fixed-estimator), intervals exclude zero | abstract, results_forecast | `forecast_metrics.csv`, `tab9` | Supported (fixed-estimator; 10.2–15.6% labeled separately as validation-selected) |
| Weather helps 3 cities, null in Austin | abstract, results_forecast | `tab9`, `forecast_metrics.csv` | Supported |
| Pooling raises error in 3/4 cities, robust to log/standardized normalization | abstract, results_forecast | `tab14`, `forecast_metrics.csv` | Supported |
| Poisson beats naive 11/12, dominated by selected 12/12 | results_forecast | `poisson_baseline.csv`, `tab21` | Supported |
| Point forecast non-identifies the objective; 92–100% of steps tied | abstract, results_decision | `tie_frequency.csv`, `tab11` | Supported |
| Fixed-index default loses to proportional in all 12 (1.2–58%) | results_decision | `tab11`, `tiebreak_sensitivity.csv` | Supported; framed as cost of the **naive default**, recoverable |
| Proportional secondary rule recovers proportional (−0.03..+0.8%) | results_decision | `tab11` | Supported |
| Quantile-interpolated distribution recovers **most of** the gap | abstract, results_decision, conclusion | `tab11` (full_distribution col) | Supported; **not** stated as equal to proportional |
| Bounded principle: representation + tie-break are first-class design choices | abstract, results_decision | mechanism + `tab11` | Supported, explicitly bounded to objective/regimes/sim |
| Aggregate loss reductions are not fairness guarantees; water/sewer ≈0 served, SF public safety ≈0 | abstract, results_decision, responsible | `tab16` | Supported |
| b₀ / horizon / conformal robustness | robustness, results_forecast | `tab22_b0`, `tab15`, `tab13` | Supported |
| Modeled span ends 2025-02-05 (frozen weather-joined window); 311 to 2025-12-31 | data, data_stats, s_tables | `features.parquet`, `weather_daily.parquet`, manifests | Supported (Stage 2B framing) |
| Prior single-city NYC 311 work by the author; delta = 4 cities/pooling-transfer/decision-coupling/non-identification/repro | related | prose (citation pending; under review) | Supported as a defensible delta; no overstated novelty |
| BigData fit via Volume/Variety/Veracity/Value (Velocity out of scope); modeling on daily panels | intro 5V | manifests, guards | Supported; no raw-row training claim |

No claim found **overstated** after Stage 3. No **unsupported** claims. The
"representation matters as much as accuracy" vague phrasing was removed and
replaced by the bounded principle.

## Direction 2 — evidence → claim (no over/under-claim)

- Calendar 10.0–14.0% (fixed) / 10.2–15.6% (selected): both ranges present and
  correctly labeled as distinct comparisons; not conflated.
- Pooling/transfer: stated as "mostly hurt / 3 of 4," not "always"; normalization
  robustness stated without claiming reversal.
- Poisson: stated as dominated baseline (no algorithmic-novelty claim).
- Conformal: "removes most of the gap"/coverage 88–90%; decision essentially
  unchanged — not overclaimed as changing conclusions.
- Non-identification: presented as pervasive empirical characterization with the
  obviousness caveat ("ties are not surprising; the question is pervasiveness");
  cost attributed to the naive default, recoverable.
- Full distribution vs proportional: "recovers most of the gap" / "a second
  route" — **not** equal performance (the 0/12 full-vs-arms-under-proportional
  finding is in the supplement, not overclaimed in main).
- Family served fractions: exact 0.0000/0.0025 disclosed; framed as tradeoff,
  not a fairness analysis or social-need claim.
- A2 window: frozen pinned-layer wording; no general-NOAA-unavailability claim.
- Reproducibility/guards: 37-test suite / 16 guards; provenance hashes — stated
  factually.

## Stage-3 overstatement check (explicit)

- **Non-identification cost:** every statement of the 1.2–58% figure is tied to
  the *fixed-index default* and immediately paired with the recovering remedies.
  No statement presents it as an inherent, non-recoverable cost of point
  forecasts. ✓
- **Distribution ≠ proportional:** abstract, results_decision, and conclusion
  all say the distribution "recovers most of the gap" / "a second route," never
  that it equals proportional performance. ✓
- **No new operational/deployment/staffing/causal/social-need/city-validation
  claim** introduced (forbidden-token scan clean). ✓
- **Identity/benchmark claim** is asserted but bounded; no broad algorithmic
  novelty claim. ✓

**Audit result: PASS** — claims and evidence are aligned in both directions; no
Stage-3 enthusiasm overstatement detected.
