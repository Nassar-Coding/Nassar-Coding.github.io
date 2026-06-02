# Table 5: Robustness by Borough (best model family, held-out test)

Source: `reports/borough_performance.csv`. Comparison of internal_historical vs
calendar_augmented test MAE for the random forest, per borough.

| Borough | Test rows | Mean next-day | Internal MAE | Calendar MAE | Improvement (%) | Augmented better |
|---------|----------:|--------------:|-------------:|-------------:|----------------:|:----------------:|
| Bronx | 1,304 | 283.023 | 120.194 | 109.567 | 8.84 | yes |
| Brooklyn | 1,304 | 363.699 | 76.991 | 64.175 | 16.65 | yes |
| Manhattan | 1,304 | 255.515 | 58.178 | 48.078 | 17.36 | yes |
| Queens | 1,304 | 284.544 | 53.771 | 43.675 | 18.78 | yes |
| Staten Island | 1,304 | 41.581 | 12.766 | 11.129 | 12.82 | yes |

Calendar augmentation improves MAE for all five boroughs (range about 8.8% to
18.8%). Absolute error scales with borough volume (largest for the Bronx,
smallest for Staten Island).
