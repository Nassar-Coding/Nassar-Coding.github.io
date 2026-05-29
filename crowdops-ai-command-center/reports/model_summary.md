# CrowdOps Risk Model -- Training Summary

_Generated: 2026-05-29T21:55:53_

## Selected Model

- **Winning model:** `LogisticRegression` (selected by macro F1).
- **Accuracy:** 0.8680
- **Precision (macro):** 0.8437
- **Recall (macro):** 0.8382
- **F1 (macro):** 0.8405

## Dataset

- Total rows: 2,500
- Training rows: 2,000
- Test rows: 500

## Model Comparison

| Model | Accuracy | Precision (macro) | Recall (macro) | F1 (macro) |
| --- | --- | --- | --- | --- |
| LogisticRegression **(selected)** | 0.8680 | 0.8437 | 0.8382 | 0.8405 |
| RandomForest | 0.8440 | 0.8144 | 0.8110 | 0.8123 |

## Notes

- The target (`risk_level`) is derived from synthetic, local-only data.
- Controlled noise is added during data generation so accuracy is
  realistic rather than perfect.
- The persisted artifact is a full scikit-learn `Pipeline`, so the same
  preprocessing is applied automatically at inference time.
