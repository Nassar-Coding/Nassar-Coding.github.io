# Table 3: Model Comparison (held-out test partition)

Source: `reports/model_comparison.csv`. Test metrics from the single
chronological split (models fit on the training partition). Lower MAE, RMSE, and
MAPE are better; higher R-squared is better.

| Model | Feature set | Test MAE | Test RMSE | Test MAPE (%) | Test R2 |
|-------|-------------|---------:|----------:|--------------:|--------:|
| naive_seasonal | naive_seasonal | 71.848 | 197.743 | 34.689 | 0.563 |
| ridge | internal_historical | 69.219 | 187.753 | 36.073 | 0.606 |
| ridge | calendar_augmented | 68.758 | 187.757 | 35.729 | 0.606 |
| ridge | weather_augmented | 69.283 | 187.784 | 36.009 | 0.606 |
| ridge | calendar_weather_augmented | 68.915 | 187.762 | 36.140 | 0.606 |
| random_forest | internal_historical | 65.282 | 184.787 | 34.259 | 0.618 |
| random_forest | calendar_augmented | 58.082 | 181.135 | 29.026 | 0.633 |
| random_forest | weather_augmented | 64.104 | 181.379 | 33.614 | 0.632 |
| random_forest | calendar_weather_augmented | 56.224 | 178.150 | 28.173 | 0.645 |
| gradient_boosting | internal_historical | 67.493 | 187.734 | 38.378 | 0.606 |
| gradient_boosting | calendar_augmented | 61.710 | 183.886 | 34.152 | 0.622 |
| gradient_boosting | weather_augmented | 67.553 | 188.046 | 38.236 | 0.605 |
| gradient_boosting | calendar_weather_augmented | 61.878 | 181.778 | 33.822 | 0.631 |

Selected model (by validation MAE, then refit on train+validation and evaluated
on test; source `reports/evaluation_report.json`): random_forest on
calendar_weather_augmented, with test MAE 55.325, RMSE 177.476, MAPE 27.469%,
R-squared 0.648. This refit value differs slightly from the train-only row above
(56.224) because the selected model is refit on train+validation before the
final test evaluation.
