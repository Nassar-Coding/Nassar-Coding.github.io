"""Acquire daily-aggregated 311 service-request counts from official Socrata APIs.

For each configured city this script:
  1. retrieves the dataset's official metadata (name, columns, rowsUpdatedAt)
     for provenance and validates that the configured fields exist;
  2. pages through a server-side daily aggregation query
     (count of requests per day x native category);
  3. writes the result to data/raw/311/<city>_daily_by_category.csv.gz
     together with a JSON manifest recording every query URL, retrieval
     timestamp, SHA-256 checksum, and row count.

No record-level data are downloaded or redistributed. The daily aggregate
is the rawest layer of the benchmark; it is never overwritten by later
pipeline stages (preprocessing reads it and writes to data/interim/).

Run:  python src/acquisition/fetch_311.py --config configs/data_sources.yml \
          --out data/raw/311
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
from datetime import datetime, timezone
from pathlib import Path

import yaml

PAGE_LIMIT = 50000
MAX_PAGES = 200          # hard safety cap; expected pages per city is < 30
RETRY_ATTEMPTS = 5
RETRY_BASE_SLEEP = 5.0   # seconds, doubled per attempt
USER_AGENT = "dream-paper-research-acquisition/1.0 (academic research; contact: NassarAlsharif0@gmail.com)"


def http_get(url: str, timeout: int = 180) -> bytes:
    last_err: Exception | None = None
    for attempt in range(RETRY_ATTEMPTS):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as err:  # noqa: BLE001 - log and retry any transport error
            last_err = err
            sleep = RETRY_BASE_SLEEP * (2 ** attempt)
            print(f"  retry {attempt + 1}/{RETRY_ATTEMPTS} after error: {err} (sleep {sleep}s)", flush=True)
            time.sleep(sleep)
    raise RuntimeError(f"GET failed after {RETRY_ATTEMPTS} attempts: {url}") from last_err


def fetch_dataset_metadata(domain: str, dataset_id: str) -> dict:
    url = f"https://{domain}/api/views/{dataset_id}.json"
    meta = json.loads(http_get(url))
    return {
        "metadata_url": url,
        "name": meta.get("name"),
        "id": meta.get("id"),
        "rowsUpdatedAt": meta.get("rowsUpdatedAt"),
        "license": (meta.get("license") or {}).get("name"),
        "attribution": meta.get("attribution"),
        "columns": [c.get("fieldName") for c in meta.get("columns", [])],
    }


def year_windows(window: dict):
    """Split the study window into calendar-year chunks.

    Smaller windows keep the server-side $group computation well inside the
    portal's query-time limits; results are identical to one large query
    because (day, category) groups never span calendar years.
    """
    start_y = int(window["start"][:4])
    end_y = int(window["end"][:4])
    chunks = []
    for y in range(start_y, end_y + 1):
        lo = f"{y}-01-01" if y > start_y else window["start"]
        hi = f"{y + 1}-01-01"
        if hi > window["end"]:
            hi = window["end"]
        if lo < hi:
            chunks.append({"start": lo, "end": hi})
    return chunks


def build_query_url(source: dict, window: dict, offset: int) -> str:
    date_field = source["date_field"]
    category_field = source["category_field"]
    extra = source.get("extra_group_fields") or []
    select_parts = [
        f"date_trunc_ymd({date_field}) AS day",
        f"{category_field} AS category",
        *extra,
        "count(*) AS n",
    ]
    group_parts = ["day", "category", *extra]
    params = {
        "$select": ", ".join(select_parts),
        "$group": ", ".join(group_parts),
        "$where": (
            f"{date_field} >= '{window['start']}T00:00:00' AND "
            f"{date_field} < '{window['end']}T00:00:00'"
        ),
        "$order": ", ".join(group_parts),
        "$limit": str(PAGE_LIMIT),
        "$offset": str(offset),
    }
    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    return f"https://{source['domain']}/resource/{source['dataset_id']}.json?{query}"


def fetch_city(source: dict, window: dict, out_dir: Path) -> dict:
    city = source["city"]
    print(f"=== {city}: {source['name']} ===", flush=True)
    manifest: dict = {
        "city": city,
        "source_name": source["name"],
        "domain": source["domain"],
        "dataset_id": source["dataset_id"],
        "dataset_page": f"https://{source['domain']}/d/{source['dataset_id']}",
        "license_note": source.get("license_note"),
        "aggregation": "server-side count per (day, native category) via SODA $group",
        "study_window": dict(window),
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "query_urls": [],
    }

    meta = fetch_dataset_metadata(source["domain"], source["dataset_id"])
    manifest["dataset_metadata"] = meta
    needed = [source["date_field"], source["category_field"], *(source.get("extra_group_fields") or [])]
    missing = [f for f in needed if f not in meta["columns"]]
    if missing:
        raise RuntimeError(
            f"{city}: configured fields {missing} not present in dataset columns: {meta['columns']}"
        )

    rows: list[dict] = []
    for chunk in year_windows(window):
        for page in range(MAX_PAGES):
            url = build_query_url(source, chunk, offset=page * PAGE_LIMIT)
            manifest["query_urls"].append(url)
            payload = json.loads(http_get(url))
            rows.extend(payload)
            print(f"  {chunk['start'][:4]} page {page}: {len(payload)} rows (total {len(rows)})", flush=True)
            if len(payload) < PAGE_LIMIT:
                break
        else:
            raise RuntimeError(f"{city}: exceeded MAX_PAGES={MAX_PAGES}; aborting rather than truncating silently")

    extra = source.get("extra_group_fields") or []
    fieldnames = ["day", "category", *extra, "n"]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    data_bytes = buf.getvalue().encode("utf-8")

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{city}_daily_by_category.csv.gz"
    # mtime=0 keeps the gzip output byte-stable so the checksum reflects content only.
    with open(out_path, "wb") as fh:
        with gzip.GzipFile(fileobj=fh, mode="wb", mtime=0) as gz:
            gz.write(data_bytes)

    manifest["output_file"] = str(out_path)
    manifest["row_count"] = len(rows)
    manifest["sha256_uncompressed"] = hashlib.sha256(data_bytes).hexdigest()
    manifest["sha256_gzip"] = hashlib.sha256(out_path.read_bytes()).hexdigest()

    manifest_path = out_dir / f"{city}_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"  wrote {out_path} ({len(rows)} rows) and {manifest_path}", flush=True)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--cities", nargs="*", default=None,
                        help="optional subset of city keys to fetch")
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text())
    window = config["study_window"]
    out_dir = Path(args.out)

    failures: dict[str, str] = {}
    for source in config["socrata_311"]:
        if args.cities and source["city"] not in args.cities:
            continue
        try:
            fetch_city(source, window, out_dir)
        except Exception as err:  # noqa: BLE001 - one city failing must not lose the others
            failures[source["city"]] = str(err)
            print(f"!! {source['city']} FAILED: {err}", flush=True)

    if failures:
        (out_dir / "_failures.json").write_text(json.dumps(failures, indent=2))
        print(f"Completed with failures: {failures}", flush=True)
        return 1
    print("All cities acquired successfully.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
