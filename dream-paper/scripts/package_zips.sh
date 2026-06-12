#!/usr/bin/env bash
# Build the two final deliverable archives from a clean checkout state.
set -euo pipefail
cd "$(dirname "$0")/.."   # dream-paper/

OUT=${1:-/tmp}

# ZIP 1: complete working repository (code, configs, tests, docs, raw data
# manifests and acquired aggregates, outputs, reproducibility records).
# NOTE: run logs and pytest logs are execution evidence and MUST ship;
# only LaTeX build byproducts are excluded (a blanket *.log exclusion
# previously stripped the run logs from delivered mirrors).
zip -qr "$OUT/dream_paper_complete_repository.zip" . \
  -x "data/interim/*" -x "data/processed/*" -x "**/__pycache__/*" \
  -x "*.aux" -x "*.blg" -x "*.out" -x "*.bbl" \
  -x "paper/*.log" -x "supplement/*.log"

# ZIP 2: manuscript + supplement (sources, compiled PDFs, figures, tables,
# bibliography, anonymized build, checklists, manifest).
zip -qr "$OUT/dream_paper_manuscript_and_supplements.zip" \
  paper supplement outputs/tables outputs/figures reproducibility \
  -x "**/__pycache__/*" -x "*.aux" -x "*.blg" -x "*.out" \
  -x "paper/*.log" -x "supplement/*.log"

ls -la "$OUT"/dream_paper_*.zip
