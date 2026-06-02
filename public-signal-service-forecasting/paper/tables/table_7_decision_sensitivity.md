# Table 7: Forecast-to-Decision Sensitivity by Crew Budget

Source: `reports/decision_sensitivity_report.csv` and
`reports/decision_sensitivity_summary.json`. Stylized staffing-allocation
simulation; total weighted unmet demand (lower is better). The headline
augmented policy is calendar_weather_augmented; the baseline is
internal_historical; the oracle allocates on true next-day demand and is an
upper bound only.

## Total weighted unmet demand by policy and crew budget

| Setting | Crews | Daily capacity | Internal | Calendar | Weather | Calendar+Weather | Oracle |
|---------|------:|---------------:|---------:|---------:|--------:|-----------------:|-------:|
| scarce | 100 | 5,000 | 941,817 | 939,884 | 941,022 | 938,211 | 928,491 |
| moderate | 160 | 8,000 | 454,073 | 439,579 | 450,346 | 434,469 | 367,553 |
| generous | 220 | 11,000 | 164,197 | 144,408 | 158,545 | 140,346 | 50,865 |

## Calendar+weather policy vs internal-historical baseline

| Setting | Crews | Weighted-unmet reduction (%) | Gap to oracle closed (%) |
|---------|------:|-----------------------------:|-------------------------:|
| scarce | 100 | 0.38 | 27.06 |
| moderate | 160 | 4.32 | 22.66 |
| generous | 220 | 14.53 | 21.05 |

At the baseline configuration reported separately
(`reports/decision_simulation_report.json`; 135 crews, 50 requests per crew,
163 test days), the calendar+weather policy reduces weighted unmet demand by
1.886% and closes 26.381% of the baseline-to-oracle gap (internal 643,324;
calendar+weather 631,191; oracle 597,332).

The augmented policy is better than the baseline in all three budget settings,
but the magnitude grows with capacity: the decision benefit is directionally
consistent but budget-dependent.
