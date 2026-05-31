"""Local pre-aggregation for NYC 311 monthly CSV files (run on your machine).

This script is intended to be run LOCALLY by the data owner, not inside the
research container. It reduces the large monthly NYC 311 exports (one file per
month, named like ``jan_2022.csv`` ... ``dec_2024.csv``) into a single small
CSV of real observed daily counts, indexed by date x borough x complaint_group,
plus a metadata JSON describing the aggregation.

No synthetic data is generated. Every output row is an observed count of real
311 service requests. Rows that cannot be parsed or validated are dropped and
counted in the metadata, never replaced with fabricated values.

Usage
-----
    python aggregate_nyc_311_local.py --input-dir /path/to/monthly_csvs \\
        --output-csv nyc_311_daily_counts_2022_2024.csv \\
        --output-meta nyc_311_daily_counts_2022_2024.meta.json

Then upload BOTH output files (the CSV and the .meta.json) so the research
pipeline can continue.

Requirements: Python 3.9+ and pandas (``pip install pandas``).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Study window (inclusive start, inclusive end). 2022-2024 only.
# ---------------------------------------------------------------------------
STUDY_START = pd.Timestamp("2022-01-01")
STUDY_END = pd.Timestamp("2024-12-31")

# Required columns in each monthly raw file (case-insensitive match).
REQUIRED_COLUMNS = ["unique_key", "created_date", "borough", "complaint_type"]

# Canonical NYC boroughs. Raw values are upper-cased before matching.
VALID_BOROUGHS = {
    "MANHATTAN": "Manhattan",
    "BROOKLYN": "Brooklyn",
    "QUEENS": "Queens",
    "BRONX": "Bronx",
    "STATEN ISLAND": "Staten Island",
}

# Deterministic complaint_type -> complaint_group mapping.
# Matching is done on the upper-cased complaint_type using substring rules,
# evaluated in order; the first matching rule wins. Anything unmatched falls
# through to "Other". This mapping is documented in docs/data_card.md.
#
# Rule order matters. Housing is evaluated before Water so that heating
# complaints such as "HEAT/HOT WATER" are classified as Housing rather than
# being caught by the "WATER" substring under Water.
COMPLAINT_GROUP_RULES: list[tuple[str, list[str]]] = [
    ("Noise", ["NOISE", "LOUD"]),
    (
        "Housing",
        [
            "HEAT/HOT WATER",
            "HEAT",
            "HOT WATER",
            "PLUMBING",
            "PAINT",
            "PLASTER",
            "APPLIANCE",
            "DOOR",
            "WINDOW",
            "ELECTRIC",
            "FLOORING",
            "STAIRS",
            "ELEVATOR",
            "MOLD",
            "GENERAL CONSTRUCTION",
            "HOUSING",
            "APARTMENT",
            "UNSANITARY CONDITION",
            "OUTSIDE BUILDING",
        ],
    ),
    (
        "Sanitation",
        [
            "SANITATION",
            "DIRTY",
            "MISSED COLLECTION",
            "LITTER",
            "GARBAGE",
            "RECYCLING",
            "WASTE",
            "DUMPING",
            "GRAFFITI",
            "RODENT",
            "OVERFLOWING",
        ],
    ),
    (
        "Street Condition",
        [
            "STREET CONDITION",
            "STREET LIGHT",
            "POTHOLE",
            "SIDEWALK",
            "CURB",
            "ROAD",
            "STREET SIGN",
            "TRAFFIC SIGNAL",
            "HIGHWAY",
        ],
    ),
    (
        "Water",
        [
            "WATER",
            "SEWER",
            "HYDRANT",
            "LEAK",
            "FLOOD",
            "DRAINAGE",
            "CATCH BASIN",
        ],
    ),
    (
        "Traffic",
        [
            "ILLEGAL PARKING",
            "BLOCKED DRIVEWAY",
            "TRAFFIC",
            "PARKING",
            "ABANDONED VEHICLE",
            "DERELICT VEHICLE",
            "DRIVEWAY",
        ],
    ),
    (
        "Public Safety",
        [
            "ILLEGAL FIREWORKS",
            "DRUG",
            "WEAPON",
            "ASSAULT",
            "SAFETY",
            "EMERGENCY",
            "ENCAMPMENT",
            "HOMELESS",
            "ANIMAL ABUSE",
            "DISORDERLY",
            "URINATING",
            "PANHANDLING",
        ],
    ),
]


def map_complaint_group(complaint_type: str) -> str:
    """Map a raw complaint_type to a complaint_group deterministically."""
    if not isinstance(complaint_type, str):
        return "Other"
    text = complaint_type.strip().upper()
    if not text:
        return "Other"
    for group, keywords in COMPLAINT_GROUP_RULES:
        for keyword in keywords:
            if keyword in text:
                return group
    return "Other"


def _resolve_columns(frame: pd.DataFrame, path: Path) -> dict[str, str]:
    """Map required canonical names to the actual columns in the file."""
    lower_to_actual = {str(c).strip().lower(): c for c in frame.columns}
    resolved: dict[str, str] = {}
    missing: list[str] = []
    for required in REQUIRED_COLUMNS:
        if required in lower_to_actual:
            resolved[required] = lower_to_actual[required]
        else:
            missing.append(required)
    if missing:
        raise ValueError(
            f"File {path.name} is missing required column(s): {missing}. "
            f"Found columns: {list(frame.columns)}"
        )
    return resolved


def process_file(path: Path, stats: dict) -> pd.DataFrame:
    """Read one monthly CSV and return a tidy date/borough/group/count frame."""
    frame = pd.read_csv(path, dtype=str, low_memory=False)
    stats["raw_rows_read"] += len(frame)

    columns = _resolve_columns(frame, path)
    frame = frame.rename(columns={v: k for k, v in columns.items()})
    frame = frame[REQUIRED_COLUMNS].copy()

    # Parse created_date; drop rows whose date cannot be parsed.
    created = pd.to_datetime(frame["created_date"], errors="coerce")
    before = len(frame)
    frame = frame.loc[created.notna()].copy()
    frame["date"] = created.loc[created.notna()].dt.normalize()
    stats["dropped_unparseable_date"] += before - len(frame)

    # Filter to the study window (2022-01-01 .. 2024-12-31 inclusive).
    in_window = (frame["date"] >= STUDY_START) & (frame["date"] <= STUDY_END)
    stats["dropped_out_of_window"] += int((~in_window).sum())
    frame = frame.loc[in_window].copy()

    # Keep valid NYC boroughs only; normalise capitalisation.
    borough_upper = frame["borough"].astype(str).str.strip().str.upper()
    valid = borough_upper.isin(VALID_BOROUGHS)
    stats["dropped_invalid_borough"] += int((~valid).sum())
    frame = frame.loc[valid].copy()
    frame["borough"] = borough_upper.loc[valid].map(VALID_BOROUGHS)

    # Map complaint types to complaint groups (deterministic).
    frame["complaint_group"] = frame["complaint_type"].map(map_complaint_group)
    stats["rows_mapped_to_other"] += int((frame["complaint_group"] == "Other").sum())

    # Aggregate to observed daily counts per cell.
    counts = (
        frame.groupby(["date", "borough", "complaint_group"], observed=True)
        .size()
        .reset_index(name="request_volume")
    )
    stats["files_processed"].append(path.name)
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        required=True,
        type=Path,
        help="Folder containing the monthly NYC 311 CSV files.",
    )
    parser.add_argument(
        "--output-csv",
        default=Path("nyc_311_daily_counts_2022_2024.csv"),
        type=Path,
        help="Path for the aggregated daily-count CSV output.",
    )
    parser.add_argument(
        "--output-meta",
        default=Path("nyc_311_daily_counts_2022_2024.meta.json"),
        type=Path,
        help="Path for the aggregation metadata JSON output.",
    )
    parser.add_argument(
        "--glob",
        default="*.csv",
        help="Glob pattern for monthly files (default: *.csv).",
    )
    args = parser.parse_args()

    input_dir: Path = args.input_dir
    if not input_dir.is_dir():
        print(f"ERROR: input directory does not exist: {input_dir}", file=sys.stderr)
        return 2

    files = sorted(input_dir.glob(args.glob))
    if not files:
        print(f"ERROR: no CSV files found in {input_dir}", file=sys.stderr)
        return 2

    stats = {
        "raw_rows_read": 0,
        "dropped_unparseable_date": 0,
        "dropped_out_of_window": 0,
        "dropped_invalid_borough": 0,
        "rows_mapped_to_other": 0,
        "files_processed": [],
    }

    partials: list[pd.DataFrame] = []
    for path in files:
        print(f"Processing {path.name} ...")
        try:
            partials.append(process_file(path, stats))
        except Exception as error:  # noqa: BLE001
            print(f"ERROR while processing {path.name}: {error}", file=sys.stderr)
            return 3

    combined = pd.concat(partials, ignore_index=True)
    # Re-aggregate in case a calendar day is split across files.
    combined = (
        combined.groupby(["date", "borough", "complaint_group"], observed=True)[
            "request_volume"
        ]
        .sum()
        .reset_index()
        .sort_values(["date", "borough", "complaint_group"])
        .reset_index(drop=True)
    )

    combined["date"] = combined["date"].dt.strftime("%Y-%m-%d")
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(args.output_csv, index=False)

    metadata = {
        "data_mode": "real_nyc_311",
        "source_name": "NYC 311 Service Requests (NYC Open Data)",
        "study_start_date": STUDY_START.strftime("%Y-%m-%d"),
        "study_end_date": STUDY_END.strftime("%Y-%m-%d"),
        "aggregated_at": datetime.now(timezone.utc).isoformat(),
        "aggregation_level": "date x borough x complaint_group (observed daily counts)",
        "input_files_count": len(stats["files_processed"]),
        "input_files": stats["files_processed"],
        "raw_rows_read": stats["raw_rows_read"],
        "rows_dropped_unparseable_date": stats["dropped_unparseable_date"],
        "rows_dropped_out_of_window": stats["dropped_out_of_window"],
        "rows_dropped_invalid_borough": stats["dropped_invalid_borough"],
        "rows_mapped_to_other_group": stats["rows_mapped_to_other"],
        "aggregated_row_count": int(len(combined)),
        "total_requests_after_filtering": int(combined["request_volume"].sum()),
        "date_range_observed": [
            str(combined["date"].min()),
            str(combined["date"].max()),
        ],
        "boroughs_included": sorted(combined["borough"].unique().tolist()),
        "complaint_groups_included": sorted(
            combined["complaint_group"].unique().tolist()
        ),
        "no_synthetic_data": True,
        "notes": (
            "All counts are observed real NYC 311 requests. No synthetic or "
            "fabricated values were generated. Dropped rows are reported above "
            "and were never replaced."
        ),
    }
    args.output_meta.parent.mkdir(parents=True, exist_ok=True)
    with args.output_meta.open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)

    print("\nDone.")
    print(f"Wrote aggregated CSV : {args.output_csv}  ({len(combined):,} rows)")
    print(f"Wrote metadata JSON  : {args.output_meta}")
    print(f"Total observed requests after filtering: {metadata['total_requests_after_filtering']:,}")
    print(f"Date range: {metadata['date_range_observed'][0]} .. {metadata['date_range_observed'][1]}")
    print(f"Boroughs: {metadata['boroughs_included']}")
    print(f"Complaint groups: {metadata['complaint_groups_included']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
