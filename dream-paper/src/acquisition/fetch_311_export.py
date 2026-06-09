"""Fallback acquisition path: column-projected CSV export + client-side aggregation.

Server-side $group queries on very large Socrata datasets (NYC's erm2-nwe9,
~40M rows) can exceed the portal's query-time limits. This fallback streams
a two-column CSV export (created date, category) per calendar year — a
plain filtered scan with column projection, which the portal serves much
faster than a GROUP BY — and aggregates client-side to exactly the same
(day, category, n) layer produced by fetch_311.py, with the same manifest
format (plus a note recording which path produced the file).

Run:  python src/acquisition/fetch_311_export.py --config configs/data_sources.yml \
          --out data/raw/311 --cities nyc
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import yaml

from fetch_311 import fetch_dataset_metadata, year_windows  # same provenance helpers

RETRY_ATTEMPTS = 4
RETRY_BASE_SLEEP = 10.0
USER_AGENT = "dream-paper-research-acquisition/1.0 (academic research; contact: NassarAlsharif0@gmail.com)"
EXPORT_LIMIT = 10_000_000   # far above any single year's request count


def stream_year(source: dict, chunk: dict, counts: Counter, manifest: dict) -> int:
    date_field = source["date_field"]
    category_field = source["category_field"]
    params = {
        "$select": f"{date_field}, {category_field}",
        "$where": (f"{date_field} >= '{chunk['start']}T00:00:00' AND "
                   f"{date_field} < '{chunk['end']}T00:00:00'"),
        "$limit": str(EXPORT_LIMIT),
    }
    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    url = f"https://{source['domain']}/resource/{source['dataset_id']}.csv?{query}"
    manifest["query_urls"].append(url)

    last_err = None
    for attempt in range(RETRY_ATTEMPTS):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            n_rows = 0
            # accumulate into a per-attempt counter and merge only on success,
            # so a stream that dies mid-year and is retried cannot double-count
            attempt_counts: Counter = Counter()
            with urllib.request.urlopen(req, timeout=1800) as resp:
                text = io.TextIOWrapper(resp, encoding="utf-8", newline="")
                reader = csv.reader(text)
                header = next(reader, None)
                if header is None:
                    return 0
                for row in reader:
                    if len(row) < 2:
                        continue
                    day = row[0][:10]
                    attempt_counts[(day, row[1])] += 1
                    n_rows += 1
            counts.update(attempt_counts)
            return n_rows
        except Exception as err:  # noqa: BLE001
            last_err = err
            sleep = RETRY_BASE_SLEEP * (2 ** attempt)
            print(f"  retry {attempt + 1}/{RETRY_ATTEMPTS} after error: {err} (sleep {sleep}s)",
                  flush=True)
            time.sleep(sleep)
    raise RuntimeError(f"export failed after {RETRY_ATTEMPTS} attempts: {url}") from last_err


def fetch_city_export(source: dict, window: dict, out_dir: Path) -> None:
    city = source["city"]
    print(f"=== {city} (export path): {source['name']} ===", flush=True)
    manifest = {
        "city": city,
        "source_name": source["name"],
        "domain": source["domain"],
        "dataset_id": source["dataset_id"],
        "dataset_page": f"https://{source['domain']}/d/{source['dataset_id']}",
        "license_note": source.get("license_note"),
        "aggregation": ("client-side count per (day, native category) from a "
                        "column-projected CSV export; equivalent layer to the "
                        "server-side $group path in fetch_311.py"),
        "study_window": dict(window),
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "query_urls": [],
    }
    manifest["dataset_metadata"] = fetch_dataset_metadata(source["domain"], source["dataset_id"])

    counts: Counter = Counter()
    total = 0
    for chunk in year_windows(window):
        n = stream_year(source, chunk, counts, manifest)
        total += n
        print(f"  {chunk['start'][:4]}: {n} records (running total {total})", flush=True)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["day", "category", "n"])
    for (day, category), n in sorted(counts.items()):
        writer.writerow([day, category, n])
    data_bytes = buf.getvalue().encode("utf-8")

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{city}_daily_by_category.csv.gz"
    with open(out_path, "wb") as fh:
        with gzip.GzipFile(fileobj=fh, mode="wb", mtime=0) as gz:
            gz.write(data_bytes)

    manifest["source_records_scanned"] = total
    manifest["output_file"] = str(out_path)
    manifest["row_count"] = len(counts)
    manifest["sha256_uncompressed"] = hashlib.sha256(data_bytes).hexdigest()
    manifest["sha256_gzip"] = hashlib.sha256(out_path.read_bytes()).hexdigest()
    (out_dir / f"{city}_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"  wrote {out_path} ({len(counts)} aggregated rows from {total} records)", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--cities", nargs="*", required=True)
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text())
    window = config["study_window"]
    failures = {}
    for source in config["socrata_311"]:
        if source["city"] not in args.cities:
            continue
        try:
            fetch_city_export(source, window, Path(args.out))
        except Exception as err:  # noqa: BLE001
            failures[source["city"]] = str(err)
            print(f"!! {source['city']} FAILED: {err}", flush=True)
    if failures:
        Path(args.out, "_export_failures.json").write_text(json.dumps(failures, indent=2))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
