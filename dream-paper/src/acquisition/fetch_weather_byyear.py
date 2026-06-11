"""Supplement station weather from GHCN-Daily by_year files (gate finding D20).

The per-station GHCN files retrieved on 2026-06-09 end at 2025-02-05/06,
silently truncating the benchmark's final 11 months. The by_year files on
the same official NOAA AWS mirror are complete through 2025-12-31
(verified by range request before this script was approved). This script
streams the by_year file(s), keeps only the project's four stations and
configured elements within the missing window, and writes a SUPPLEMENTARY
raw layer with its own manifest. Existing raw files are never modified
(raw-preservation rule); build_panel merges both layers with
(station, date, element) de-duplication preferring the per-station layer.

Run:  python src/acquisition/fetch_weather_byyear.py \
          --config configs/data_sources.yml --out data/raw/weather \
          --years 2025 --from-date 2025-02-01
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

USER_AGENT = "dream-paper-research-acquisition/1.0 (academic research; contact: NassarAlsharif0@gmail.com)"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--years", nargs="+", type=int, required=True)
    parser.add_argument("--from-date", default=None,
                        help="keep only rows on/after this date (YYYY-MM-DD)")
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text())
    cfg = config["ghcn_daily"]
    stations = {s["station_id"]: s["city"] for s in cfg["stations"]}
    elements = set(cfg["elements"])
    window = config["study_window"]
    lo = max(window["start"].replace("-", ""),
             (args.from_date or window["start"]).replace("-", ""))
    hi = window["end"].replace("-", "")

    kept: list[dict] = []
    urls = []
    scanned = 0
    for year in args.years:
        url = f"{cfg['base_url']}/csv/by_year/{year}.csv"
        urls.append(url)
        print(f"streaming {url} ...", flush=True)
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=3600) as resp:
            text = io.TextIOWrapper(resp, encoding="utf-8", newline="")
            reader = csv.reader(text)
            header = next(reader)
            for row in reader:
                scanned += 1
                if row[0] in stations and row[2] in elements and lo <= row[1] < hi:
                    kept.append({"station": row[0], "date": row[1],
                                 "element": row[2], "value": row[3],
                                 "m_flag": row[4], "q_flag": row[5],
                                 "s_flag": row[6]})
                if scanned % 20_000_000 == 0:
                    print(f"  scanned {scanned:,} rows, kept {len(kept):,}", flush=True)
    print(f"scan complete: {scanned:,} rows scanned, {len(kept):,} kept", flush=True)

    fieldnames = ["station", "date", "element", "value", "m_flag", "q_flag", "s_flag"]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(sorted(kept, key=lambda r: (r["station"], r["date"], r["element"])))
    data_bytes = buf.getvalue().encode("utf-8")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "byyear_supplement.csv.gz"
    with open(out_path, "wb") as fh:
        with gzip.GzipFile(fileobj=fh, mode="wb", mtime=0) as gz:
            gz.write(data_bytes)

    manifest = {
        "purpose": ("supplementary weather layer closing the 2025-02-05..2025-12-31 "
                    "gap left by lagging per-station files (decision log D20)"),
        "source": "NOAA GHCN-Daily via AWS Open Data Program (bucket noaa-ghcn-pds)",
        "urls": urls,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "stations": stations,
        "elements": sorted(elements),
        "kept_window": [args.from_date or window["start"], window["end"]],
        "source_rows_scanned": scanned,
        "rows_kept": len(kept),
        "output_file": str(out_path),
        "sha256_uncompressed": hashlib.sha256(data_bytes).hexdigest(),
        "sha256_gzip": hashlib.sha256(out_path.read_bytes()).hexdigest(),
        "merge_rule": "(station,date,element) de-duplication; per-station layer wins on overlap",
    }
    (out_dir / "byyear_supplement_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"wrote {out_path} ({len(kept)} rows) + manifest", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
