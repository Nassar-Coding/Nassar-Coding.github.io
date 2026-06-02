# Table 4: Rolling-Origin Validation (5 expanding-window folds)

Source: `reports/rolling_validation_summary.json` and
`reports/rolling_validation_report.csv`.

## Random-forest mean fold test MAE by feature set

| Configuration | Mean MAE | Std |
|---------------|---------:|----:|
| naive_seasonal | 61.701 | 9.673 |
| random_forest internal_historical | 57.027 | 8.046 |
| random_forest weather_augmented | 56.222 | 7.561 |
| random_forest calendar_augmented | 48.690 | 9.590 |
| random_forest calendar_weather_augmented | 47.497 | 8.746 |

## Calendar-augmentation consistency across folds

For each model, the mean MAE improvement of calendar_augmented over
internal_historical, and the number of folds (of 5) in which calendar
augmentation was better.

| Model | Mean improvement (%) | Folds better |
|-------|---------------------:|-------------:|
| random_forest | 15.13 | 5 / 5 |
| gradient_boosting | 9.94 | 5 / 5 |
| ridge | 0.94 | 5 / 5 |

Across all five folds, calendar augmentation lowers MAE for every model, and the
calendar_weather_augmented random forest has the lowest mean fold MAE. The
ordering is stable across folds rather than an artifact of one split.
