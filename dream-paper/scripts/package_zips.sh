#!/usr/bin/env bash
# Build the two final deliverable archives from a clean checkout state.
set -euo pipefail
cd "$(dirname "$0")/.."   # dream-paper/

OUT=${1:-/tmp}

# ZIP 1: complete working repository (code, configs, tests, docs, raw data
# manifests and acquired aggregates, outputs, reproducibility records).
zip -qr "$OUT/dream_paper_complete_repository.zip" . \
  -x "data/interim/*" -x "data/processed/*" -x "**/__pycache__/*" \
  -x "*.aux" -x "*.log" -x "*.blg" -x "*.out" -x "*.bbl"

# ZIP 2: manuscript + supplement (sources, compiled PDFs, figures, tables,
# bibliography, anonymized build, checklists, manifest).
zip -qr "$OUT/dream_paper_manuscript_and_supplements.zip" \
  paper supplement outputs/tables outputs/figures reproducibility \
  -x "**/__pycache__/*" -x "*.aux" -x "*.log" -x "*.blg" -x "*.out"

ls -la "$OUT"/dream_paper_*.zip
