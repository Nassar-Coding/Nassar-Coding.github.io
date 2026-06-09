"""Acquire GHCN-Daily station weather from NOAA's official AWS Open Data mirror.

Source: https://registry.opendata.aws/noaa-ghcn/ (bucket noaa-ghcn-pds,
maintained by NOAA NCEI). For each configured station the full per-station
history file csv/by_station/<ID>.csv is downloaded, filtered to the study
window and the configured elements, and written to
data/raw/weather/<city>_<station>.csv.gz with a JSON manifest
(URL, retrieval time, SHA-256, row counts).

GHCN-Daily units (as distributed): PRCP tenths of mm; TMAX/TMIN tenths of
deg C; SNOW/SNWD mm; AWND tenths of m/s. Unit conversion happens in
preprocessing, never here; this layer stays as close to the source as
possible while remaining small enough to version.

Run:  python src/acquisition/fetch_weather.py --config configs/data_sources.yml \
          --out data/raw/weather
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
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

RETRY_ATTEMPTS = 5
RETRY_BASE_SLEEP = 5.0
USER_AGENT = "dream-paper-research-acquisition/1.0 (academic research; contact: NassarAlsharif0@gmail.com)"


def http_get(url: str, timeout: int = 300) -> bytes:
    last_err: Exception | None = None
    for attempt in range(RETRY_ATTEMPTS):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as err:  # noqa: BLE001
            last_err = err
            sleep = RETRY_BASE_SLEEP * (2 ** attempt)
            print(f"  retry {attempt + 1}/{RETRY_ATTEMPTS} after error: {err} (sleep {sleep}s)", flush=True)
            time.sleep(sleep)
    raise RuntimeError(f"GET failed after {RETRY_ATTEMPTS} attempts: {url}") from last_err


def fetch_station(station: dict, cfg: dict, window: dict, out_dir: Path) -> dict:
    city = station["city"]
    sid = station["station_id"]
    url = f"{cfg['base_url']}/csv/by_station/{sid}.csv"
    print(f"=== {city}: {sid} ({station['station_name']}) ===", flush=True)
    raw = http_get(url)
    print(f"  downloaded {len(raw)} bytes", flush=True)

    elements = set(cfg["elements"])
    start = window["start"].replace("-", "")
    end = window["end"].replace("-", "")

    reader = csv.DictReader(io.StringIO(raw.decode("utf-8")))
    kept: list[dict] = []
    for row in reader:
        date = row["DATE"]
        if row["ELEMENT"] in elements and start <= date < end:
            kept.append({
                "station": row["ID"],
                "date": date,
                "element": row["ELEMENT"],
                "value": row["DATA_VALUE"],
                "m_flag": row["M_FLAG"],
                "q_flag": row["Q_FLAG"],
                "s_flag": row["S_FLAG"],
            })

    fieldnames = ["station", "date", "element", "value", "m_flag", "q_flag", "s_flag"]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(kept)
    data_bytes = buf.getvalue().encode("utf-8")

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{city}_{sid}.csv.gz"
    with open(out_path, "wb") as fh:
        with gzip.GzipFile(fileobj=fh, mode="wb", mtime=0) as gz:
            gz.write(data_bytes)

    manifest = {
        "city": city,
        "station_id": sid,
        "station_name": station["station_name"],
        "source": "NOAA GHCN-Daily via AWS Open Data Program (bucket noaa-ghcn-pds)",
        "registry": "https://registry.opendata.aws/noaa-ghcn/",
        "url": url,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "study_window": dict(window),
        "elements": sorted(elements),
        "source_bytes": len(raw),
        "sha256_source_file": hashlib.sha256(raw).hexdigest(),
        "rows_kept": len(kept),
        "output_file": str(out_path),
        "sha256_uncompressed": hashlib.sha256(data_bytes).hexdigest(),
        "units_note": "GHCN-Daily native units (tenths of mm / tenths of degC / mm / tenths of m/s); converted in preprocessing only",
    }
    (out_dir / f"{city}_{sid}_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"  wrote {out_path} ({len(kept)} rows)", flush=True)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text())
    cfg = config["ghcn_daily"]
    window = config["study_window"]
    out_dir = Path(args.out)

    failures: dict[str, str] = {}
    for station in cfg["stations"]:
        try:
            fetch_station(station, cfg, window, out_dir)
        except Exception as err:  # noqa: BLE001
            failures[station["city"]] = str(err)
            print(f"!! {station['city']} FAILED: {err}", flush=True)

    if failures:
        (out_dir / "_failures.json").write_text(json.dumps(failures, indent=2))
        return 1
    print("All stations acquired successfully.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
