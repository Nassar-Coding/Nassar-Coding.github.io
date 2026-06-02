# Table 6: Robustness by Complaint Group (best model family, held-out test)

Source: `reports/complaint_group_performance.csv`. Comparison of
internal_historical vs calendar_augmented test MAE for the random forest, per
complaint group.

| Complaint group | Test rows | Mean next-day | Internal MAE | Calendar MAE | Improvement (%) | Augmented better |
|-----------------|----------:|--------------:|-------------:|-------------:|----------------:|:----------------:|
| Noise | 815 | 466.355 | 194.882 | 168.272 | 13.65 | yes |
| Housing | 815 | 414.310 | 121.762 | 106.839 | 12.26 | yes |
| Other | 815 | 251.470 | 54.794 | 44.474 | 18.83 | yes |
| Traffic | 815 | 436.574 | 45.000 | 40.990 | 8.91 | yes |
| Sanitation | 815 | 117.409 | 24.957 | 22.078 | 11.54 | yes |
| Public Safety | 815 | 101.827 | 24.449 | 21.496 | 12.08 | yes |
| Water | 815 | 74.476 | 25.111 | 20.585 | 18.02 | yes |
| Street Condition | 815 | 102.958 | 24.084 | 17.865 | 25.82 | yes |

Calendar augmentation improves MAE for all eight complaint groups (range about
8.9% to 25.8%). Absolute error is largest for the high-volume Noise and Housing
groups.
