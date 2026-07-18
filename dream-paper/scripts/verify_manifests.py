"""Verify the frozen raw-data layer against its committed provenance manifests.

Checks, for every 311 and weather manifest under data/raw/:
  - the referenced output file exists;
  - its gzip SHA-256 (when recorded) and/or uncompressed SHA-256 match the
    manifest exactly;
  - the recorded row count matches the file (311 layer).

Exit code 0 = every hash matches (the frozen inputs are intact);
nonzero = any mismatch, with a per-file report.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    failures = 0
    manifests = sorted((ROOT / "data" / "raw").glob("*/*_manifest.json"))
    if not manifests:
        print("no manifests found under data/raw/")
        return 1
    for mpath in manifests:
        man = json.loads(mpath.read_text())
        out = ROOT / man["output_file"]
        label = str(mpath.relative_to(ROOT))
        if not out.exists():
            print(f"FAIL {label}: missing {man['output_file']}")
            failures += 1
            continue
        raw = out.read_bytes()
        ok = True
        if "sha256_gzip" in man:
            if sha256_bytes(raw) != man["sha256_gzip"]:
                print(f"FAIL {label}: gzip sha256 mismatch")
                ok = False
        if "sha256_uncompressed" in man:
            if sha256_bytes(gzip.decompress(raw)) != man["sha256_uncompressed"]:
                print(f"FAIL {label}: uncompressed sha256 mismatch")
                ok = False
        if "row_count" in man:
            n = gzip.decompress(raw).count(b"\n") - 1
            if n != man["row_count"]:
                print(f"FAIL {label}: row count {n} != manifest {man['row_count']}")
                ok = False
        if ok:
            print(f"OK   {label}")
        else:
            failures += 1
    print(f"{len(manifests)} manifests checked, {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
