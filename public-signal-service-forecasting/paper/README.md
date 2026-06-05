# Paper

This folder contains the final paper artifacts for **"From Forecast Accuracy to
Operational Value: Public Signal Augmentation for NYC 311 Service Demand."**

## Final documents

- `output/public_signal_service_forecasting_final_submission.pdf` — final PDF.
- `output/public_signal_service_forecasting_final_submission.docx` — final Word document.

## Source files

- `output/content.py` — the shared content source of record (text, tables,
  figures, and references); both generators render from it so the PDF and Word
  documents are identical in content.
- `output/build_pdf.py` — renders the PDF (ReportLab).
- `output/build_docx.py` — renders the Word document (python-docx).
- `references.bib` — bibliography; every entry is cited in the paper.
- `number_audit.md` — every numeric claim traced to a committed output.
- `figures/` — the figures used in the paper.

## Rebuild

```bash
cd paper/output
python build_pdf.py
python build_docx.py
```

All reported values come from the committed outputs under `../../reports/` and
`../../data/metadata/`; no empirical result is recomputed here.
