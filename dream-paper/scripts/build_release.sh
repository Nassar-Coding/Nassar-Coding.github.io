#!/usr/bin/env bash
# P6 (final pass v4): build the clean public release tree on an orphan branch.
#
# The development branch carries internal review files (reviewer logs,
# stage trackers, audit prompts) and a research history whose commit
# messages reference the review process. The public release is therefore an
# ORPHAN branch containing ONLY the allowlisted tree below at its root,
# with a single clean initial commit; the research history is retained
# privately by the author. This is the "clean initial history" option of
# the v4 P6c specification.
#
# Usage: scripts/build_release.sh <release-branch-name>
set -euo pipefail
BRANCH="${1:-release-v1}"
ROOT="$(git rev-parse --show-toplevel)"
SRC="$ROOT/dream-paper"
STAGE="$(mktemp -d)"

# ---- allowlist -----------------------------------------------------------
ALLOW=(
  Makefile requirements.txt LICENSE CITATION.cff CORRECTIONS.md
  configs src scripts tests
  data/raw
  outputs/metrics outputs/tables outputs/figures
  reproducibility
  audit
  paper supplement
)
mkdir -p "$STAGE"
for item in "${ALLOW[@]}"; do
  if [ -e "$SRC/$item" ]; then
    mkdir -p "$STAGE/$(dirname "$item")"
    cp -r "$SRC/$item" "$STAGE/$item"
  fi
done
# release README replaces the development README
cp "$SRC/release/README.md" "$STAGE/README.md"
cp "$SRC/release/DATA_LICENSES.md" "$STAGE/DATA_LICENSES.md"
# the release builder itself is a development tool and does not ship
rm -f "$STAGE/scripts/build_release.sh"
# strip development-only build byproducts and caches
find "$STAGE" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
find "$STAGE" \( -name '*.aux' -o -name '*.log' -o -name '*.out' -o \
      -name '*.blg' -o -name '*.toc' \) -delete
# keep .bbl files: they are required to compile without rerunning bibtex? (bibtex reruns fine; keep anyway)
# final PDF hashes
( cd "$STAGE" && sha256sum paper/main_ieee.pdf supplement/supplement.pdf > PDF_SHA256SUMS.txt )

echo "Staged release tree at: $STAGE"
echo "Files: $(find "$STAGE" -type f | wc -l)"
echo
echo "To create the orphan branch:"
echo "  git checkout --orphan $BRANCH && git rm -rf --cached . && rm -rf ./* && cp -r $STAGE/. . && git add -A && git commit -m 'Public archival release'"
