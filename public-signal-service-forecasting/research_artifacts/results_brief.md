# Results Brief

A concise, technical summary of the verified results for the real NYC 311
baseline. All values are read from the committed artifacts under `reports/` and
`data/metadata/`.

## Dataset summary

| Property | Value |
|----------|-------|
| Source | NYC 311 Service Requests (NYC Open Data, `erm2-nwe9`) |
| Data mode | `real_nyc_311` (no synthetic data; no synthetic fallback) |
| Study window | 2022-01-01 to 2024-12-31 |
| Monthly input files | 36 |
| Raw records read | 9,851,452 |
| Requests after filtering | 9,838,988 |
| Rows dropped (invalid borough) | 12,464 |
| Rows dropped (unparseable/out-of-window date) | 0 |
| Aggregated daily-count rows | 43,840 |
| Processed modelling rows | 43,240 |
| Observed date range (processed) | 2022-01-15 to 2024-12-30 |
| Boroughs | Bronx, Brooklyn, Manhattan, Queens, Staten Island |
| Complaint groups | Housing, Noise, Other, Public Safety, Sanitation, Street Condition, Traffic, Water |
| Unit of analysis | date x borough x complaint_group |
| Target | `request_volume_next_day` (observed next-day count) |

## Validation split (chronological by date)

| Partition | Rows | Fraction of dates |
|-----------|------|-------------------|
| Train | 30,240 | 0.70 |
| Validation | 6,480 | 0.15 |
| Test | 6,520 | 0.15 |

## Model comparison (test partition)

| Model | Feature set | Test MAE | Test RMSE | Test MAPE (%) | Test R2 |
|-------|-------------|----------|-----------|---------------|---------|
| naive_seasonal | naive_seasonal | 71.848 | 197.743 | 34.689 | 0.563 |
| ridge | internal_historical | 69.219 | 187.753 | 36.073 | 0.606 |
| random_forest | internal_historical | 65.282 | 184.787 | 34.259 | 0.618 |
| gradient_boosting | internal_historical | 67.493 | 187.734 | 38.378 | 0.606 |
| ridge | calendar_augmented | 68.758 | 187.757 | 35.729 | 0.606 |
| random_forest | calendar_augmented | 58.082 | 181.135 | 29.026 | 0.633 |
| gradient_boosting | calendar_augmented | 61.710 | 183.886 | 34.152 | 0.622 |

## Best model

| Property | Value |
|----------|-------|
| Model | random_forest |
| Feature set | calendar_augmented |
| Selection metric | validation MAE |
| Test MAE | 57.263 |
| Test RMSE | 182.210 |
| Test MAPE (%) | 28.055 |
| Test R2 | 0.629 |

Note: the best-model test metrics are computed in the evaluation step after
refitting on train+validation, so they differ slightly from the
calendar_augmented random_forest row in the comparison table (which is fit on
train only).

### Best-model test MAE by borough

| Borough | Test MAE |
|---------|----------|
| Bronx | 114.529 |
| Brooklyn | 66.040 |
| Manhattan | 49.214 |
| Queens | 45.287 |
| Staten Island | 11.246 |

### Best-model test MAE by complaint group

| Complaint group | Test MAE |
|-----------------|----------|
| Noise | 174.195 |
| Housing | 114.740 |
| Other | 45.589 |
| Traffic | 40.439 |
| Water | 21.949 |
| Sanitation | 21.788 |
| Public Safety | 21.512 |
| Street Condition | 17.894 |

## Internal historical vs calendar augmented (test MAE)

| Model | Internal historical | Calendar augmented | Improvement |
|-------|---------------------|--------------------|-------------|
| random_forest | 65.282 | 58.082 | 11.03% |
| gradient_boosting | 67.493 | 61.710 | 8.57% |
| ridge | 69.219 | 68.758 | 0.67% |

Calendar augmentation improves every model; the gain is largest for the tree
ensembles.

## Decision simulation (163 test days)

Assumptions: 135 crews, 50 requests per crew per day, proportional
largest-remainder allocation, weighted unmet demand with higher weight on Public
Safety (2.0), Water (1.5), and Traffic (1.5).

| Policy | Weighted unmet | Total unmet | Avg shortfall | High-demand coverage | Allocation efficiency |
|--------|----------------|-------------|---------------|----------------------|-----------------------|
| Baseline (internal historical) | 643,324.5 | 551,381 | 84.568 | 0.0861 | 0.9547 |
| Calendar augmented | 634,613.5 | 543,322 | 83.332 | 0.0739 | 0.9620 |
| Oracle (true demand) | 597,332.0 | 506,347 | 77.661 | 0.0110 | 0.9956 |

| Decision metric | Value |
|-----------------|-------|
| Weighted-unmet reduction (augmented vs baseline) | 1.354% |
| Gap to oracle closed | 18.94% |
| Augmented better than baseline | true |

## Monitoring status

| Property | Value |
|----------|-------|
| Best-model test MAE | 57.2632 |
| Naive baseline test MAE | 71.848 |
| Improvement over baseline | 20.3% |
| Improvement threshold | 5.0% |
| Status | healthy |

## Robustness package (closure pass)

### Rolling-origin validation (5 expanding-window chronological folds)

Calendar-augmentation MAE improvement, by model, across folds
(`reports/rolling_validation_summary.json`):

| Model | Mean improvement | Folds augmented better |
|-------|------------------|------------------------|
| random_forest | 15.13% | 5 / 5 |
| gradient_boosting | 9.94% | 5 / 5 |
| ridge | 0.94% | 5 / 5 |

Random-forest mean fold test MAE: internal_historical 57.03 (std 8.05) vs
calendar_augmented 48.69 (std 9.59).

### Robustness by borough (best model, held-out test)

Calendar augmentation improved MAE for all 5 boroughs (4.7% to 15.8%); largest
absolute error in the Bronx, smallest in Staten Island
(`reports/borough_performance.csv`).

### Robustness by complaint group (best model, held-out test)

Calendar augmentation improved MAE for all 8 complaint groups (5.8% to 25.7%);
largest absolute error in Noise and Housing
(`reports/complaint_group_performance.csv`).

### Decision sensitivity by crew budget

| Setting | Crews | Weighted-unmet reduction | Gap to oracle closed |
|---------|-------|--------------------------|----------------------|
| Scarce | 100 | 0.21% | 14.50% |
| Moderate | 160 | 3.19% | 16.75% |
| Generous | 220 | 12.05% | 17.46% |

The calendar-augmented policy is better in all three budgets, but the effect size
is budget-dependent (`reports/decision_sensitivity_summary.json`).

### Practical-significance summary

`reports/practical_significance_summary.json`: forecasting evidence strong
(consistent across folds, boroughs, and complaint groups); decision evidence
directionally consistent but budget-dependent; not strong enough for full-paper
drafting.

## Key takeaways

- Calendar augmentation reduces next-day forecast error for every model and most
  for the best (random forest) model, under a leakage-controlled chronological
  protocol on real NYC 311 data.
- The forecast improvement transfers to the stylized decision metric in the same
  direction but with much smaller magnitude (about 11% accuracy gain to about
  1.35% weighted-unmet reduction), closing roughly a fifth of the oracle gap.
- Error and the achievable decision benefit are dominated by high-volume cells
  and a deliberately scarce capacity budget.

## Limitations

- 311 reflects reporting behaviour, not true incidence (reporting bias).
- Borough-level aggregation hides within-borough heterogeneity; complaint-group
  mapping is a deterministic approximation with a residual Other group.
- Calendar features may proxy seasonality rather than specific operational
  drivers.
- The decision simulation is a single stylized heuristic; results characterize the
  simulation, not real operations.
- Correlational only; no causal identification; no external validity beyond NYC
  and the 2022-2024 window.
