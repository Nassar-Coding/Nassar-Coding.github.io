"""Build the harmonized (city, family, day) demand panel and daily weather table.

Inputs  (read-only): data/raw/311/<city>_daily_by_category.csv.gz
                     data/raw/weather/<city>_<station>.csv.gz
Outputs: data/interim/panel_311.parquet        (city, family, day, n)
         data/interim/weather_daily.parquet    (city, day, weather variables)
         outputs/tables/family_composition_<city>.csv
         data/interim/panel_manifest.json

Harmonization is a deterministic, ordered, case-insensitive substring rule
set (configs/service_families.yml). Exclusions of non-service-request
categories are applied here with documented reasons; everything else,
including unmatched categories, is retained (unmatched -> "other").
Chicago rows flagged duplicate=true by the source system are dropped and
counted in the manifest.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.runtime import DATA_INTERIM, DATA_RAW, OUTPUTS, load_config, write_json  # noqa: E402

GHCN_UNIT_DIVISORS = {"PRCP": 10.0, "TMAX": 10.0, "TMIN": 10.0, "SNOW": 1.0,
                      "SNWD": 1.0, "AWND": 10.0}


def compile_rules(cfg: dict):
    rules = []
    for fam in cfg["families"]:
        for pat in fam["patterns"]:
            rules.append((pat.lower(), fam["name"]))
    return rules


def map_category(category: str, rules) -> str:
    c = (category or "").lower()
    for pat, fam in rules:
        if pat in c:
            return fam
    return "other"


def build_city_panel(city: str, fam_cfg: dict, rules, notes: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    path = DATA_RAW / "311" / f"{city}_daily_by_category.csv.gz"
    df = pd.read_csv(path)
    df["day"] = pd.to_datetime(df["day"]).dt.normalize()
    df["category"] = df["category"].fillna("(missing)").astype(str)
    raw_total = int(df["n"].sum())

    if "duplicate" in df.columns:
        dup_mask = df["duplicate"].astype(str).str.lower().isin(["true", "1", "1.0"])
        notes[f"{city}_duplicate_requests_dropped"] = int(df.loc[dup_mask, "n"].sum())
        df = df.loc[~dup_mask].drop(columns=["duplicate"])

    excl_patterns = [e["pattern"].lower() for e in fam_cfg["exclusions"].get(city, [])]
    if excl_patterns:
        cat_lower = df["category"].str.lower()
        excl_mask = np.zeros(len(df), dtype=bool)
        for pat in excl_patterns:
            excl_mask |= cat_lower.str.contains(pat, regex=False)
        notes[f"{city}_excluded_requests"] = int(df.loc[excl_mask, "n"].sum())
        df = df.loc[~excl_mask]

    df["family"] = [map_category(c, rules) for c in df["category"]]

    composition = (df.groupby(["family", "category"], as_index=False)["n"].sum()
                     .sort_values(["family", "n"], ascending=[True, False]))
    composition.insert(0, "city", city)

    panel = df.groupby(["day", "family"], as_index=False)["n"].sum()
    panel.insert(0, "city", city)
    notes[f"{city}_raw_request_total"] = raw_total
    notes[f"{city}_kept_request_total"] = int(panel["n"].sum())
    notes[f"{city}_native_categories"] = int(df["category"].nunique())
    return panel, composition


def densify(panel: pd.DataFrame) -> pd.DataFrame:
    """Complete the (city, family, day) grid with explicit zeros.

    A missing (day, family) combination inside a city's observed date range
    means zero requests of that family were created that day; the SODA
    aggregation simply emits no row for it.
    """
    out = []
    for city, grp in panel.groupby("city"):
        days = pd.date_range(grp["day"].min(), grp["day"].max(), freq="D")
        fams = sorted(grp["family"].unique())
        full = pd.MultiIndex.from_product([days, fams], names=["day", "family"]).to_frame(index=False)
        merged = full.merge(grp.drop(columns=["city"]), on=["day", "family"], how="left")
        merged["n"] = merged["n"].fillna(0).astype(int)
        merged.insert(0, "city", city)
        out.append(merged)
    return pd.concat(out, ignore_index=True)


def build_weather(sources: dict) -> pd.DataFrame:
    frames = []
    for st in sources["ghcn_daily"]["stations"]:
        city, sid = st["city"], st["station_id"]
        path = DATA_RAW / "weather" / f"{city}_{sid}.csv.gz"
        df = pd.read_csv(path, dtype={"date": str})
        df = df[df["q_flag"].isna() | (df["q_flag"].astype(str).str.strip() == "")]
        df["day"] = pd.to_datetime(df["date"], format="%Y%m%d")
        df["value"] = df["value"].astype(float) / df["element"].map(GHCN_UNIT_DIVISORS)
        wide = df.pivot_table(index="day", columns="element", values="value", aggfunc="first")
        wide = wide.reindex(pd.date_range(wide.index.min(), wide.index.max(), freq="D"))
        wide.index.name = "day"
        # SNOW/SNWD missing almost always means none recorded; temperatures
        # are interpolated over short gaps only (limit 7 days), and the
        # remaining missingness is reported in the manifest.
        for col in ("SNOW", "SNWD"):
            if col in wide.columns:
                wide[col] = wide[col].fillna(0.0)
            else:
                wide[col] = 0.0
        for col in ("TMAX", "TMIN", "PRCP"):
            if col not in wide.columns:
                wide[col] = np.nan
        # AWND is dropped: SF Downtown reports no wind and Central Park has
        # multi-month gaps; keeping it would silently delete those days (D15)
        if "AWND" in wide.columns:
            wide = wide.drop(columns=["AWND"])
        wide[["TMAX", "TMIN"]] = wide[["TMAX", "TMIN"]].interpolate(limit=7)
        wide["PRCP"] = wide["PRCP"].fillna(0.0)
        wide["TAVG_DERIVED"] = (wide["TMAX"] + wide["TMIN"]) / 2.0
        wide = wide.reset_index()
        wide.insert(0, "city", city)
        frames.append(wide)
    return pd.concat(frames, ignore_index=True)


def main() -> int:
    fam_cfg = load_config("service_families.yml")
    sources = load_config("data_sources.yml")
    rules = compile_rules(fam_cfg)

    notes: dict = {"built_at_utc": datetime.now(timezone.utc).isoformat()}
    panels, compositions = [], []
    for src in sources["socrata_311"]:
        city = src["city"]
        if not (DATA_RAW / "311" / f"{city}_daily_by_category.csv.gz").exists():
            notes[f"{city}_status"] = "raw file missing; city skipped"
            continue
        panel, comp = build_city_panel(city, fam_cfg, rules, notes)
        panels.append(panel)
        compositions.append(comp)

    if not panels:
        raise SystemExit("No raw 311 data found under data/raw/311; run acquisition first.")

    panel = densify(pd.concat(panels, ignore_index=True))
    weather = build_weather(sources)

    DATA_INTERIM.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(DATA_INTERIM / "panel_311.parquet", index=False)
    weather.to_parquet(DATA_INTERIM / "weather_daily.parquet", index=False)

    tables = OUTPUTS / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    for comp in compositions:
        comp.to_csv(tables / f"family_composition_{comp['city'].iloc[0]}.csv", index=False)

    for city, grp in weather.groupby("city"):
        notes[f"{city}_weather_missing_after_fill"] = {
            c: int(grp[c].isna().sum()) for c in ("TMAX", "TMIN", "PRCP")
        }
    # Authoritative per-city active-family manifest (redesign C10).
    # A family is ACTIVE in a city iff the city's source taxonomy maps any
    # request volume to it over the study window. Structural absence
    # (e.g., Chicago noise) is recorded here and is NOT encoded as zeros:
    # densify() only completes the grid over each city's active set.
    all_families = [f["name"] for f in fam_cfg["families"]]
    active = {}
    for city, grp in panel.groupby("city"):
        present = sorted(grp.loc[grp["n"] > 0, "family"].unique())
        active[city] = {
            "active_families": present,
            "structurally_absent": sorted(set(all_families) - set(present)),
        }
    write_json(DATA_INTERIM / "active_families.json", active)

    notes["panel_rows"] = len(panel)
    notes["panel_cities"] = sorted(panel["city"].unique())
    notes["panel_date_range"] = [str(panel["day"].min().date()), str(panel["day"].max().date())]
    write_json(DATA_INTERIM / "panel_manifest.json", notes)
    print(json.dumps(notes, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
