"""Construct the leakage-controlled supervised learning table.

One row per (city, family, day t) with target y = n[t+1].

Feature sets (matched to Paper 1's four-way design, extended cross-city):
  internal : lags and rolling statistics of the target series through day t
  calendar : internal + deterministic calendar features of target day t+1
  weather  : internal + weather for target day t+1 (realized GHCN values as
             a stand-in for a day-ahead forecast; assumption A3) + lagged
             weather through day t
  calendar_weather : union of the above

Leakage controls:
  - every lag/rolling feature is computed from n[t], n[t-1], ... only
    (rolling windows are shifted so day t+1 is never included);
  - calendar features of t+1 are deterministic, hence known at decision time;
  - the only stochastic t+1 information is weather (assumption A3), and a
    sensitivity variant `weather_lagged_only` removes it.

Output: data/processed/features.parquet + feature group registry JSON.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.runtime import DATA_INTERIM, DATA_PROCESSED, us_federal_holidays, write_json  # noqa: E402

LAGS = [1, 2, 3, 7, 14, 28]
ROLL_WINDOWS = [7, 28]
WEATHER_VARS = ["PRCP", "TMAX", "TMIN", "SNOW", "SNWD", "TAVG_DERIVED"]


def add_internal_features(grp: pd.DataFrame) -> pd.DataFrame:
    g = grp.sort_values("day").copy()
    s = g["n"].astype(float)
    for lag in LAGS:
        g[f"lag_{lag}"] = s.shift(lag - 1)        # lag_1 = n[t], lag_7 = n[t-6]
    for w in ROLL_WINDOWS:
        g[f"roll_mean_{w}"] = s.rolling(w).mean()  # window ends at day t
        g[f"roll_std_{w}"] = s.rolling(w).std()
    g["target"] = s.shift(-1)                      # y = n[t+1]
    return g


def calendar_frame(days: pd.Series) -> pd.DataFrame:
    """Deterministic calendar features for the TARGET day (t+1)."""
    target_day = days + pd.Timedelta(days=1)
    years = range(target_day.dt.year.min(), target_day.dt.year.max() + 1)
    holidays = set()
    for y in years:
        holidays |= us_federal_holidays(y)
    doy = target_day.dt.dayofyear
    return pd.DataFrame({
        "cal_dow": target_day.dt.dayofweek,
        "cal_month": target_day.dt.month,
        "cal_is_weekend": (target_day.dt.dayofweek >= 5).astype(int),
        "cal_is_holiday": target_day.dt.date.isin(holidays).astype(int),
        "cal_doy_sin": np.sin(2 * np.pi * doy / 365.25),
        "cal_doy_cos": np.cos(2 * np.pi * doy / 365.25),
    }, index=days.index)


def main() -> int:
    panel = pd.read_parquet(DATA_INTERIM / "panel_311.parquet")
    weather = pd.read_parquet(DATA_INTERIM / "weather_daily.parquet")

    # iterate groups explicitly: pandas 3 excludes grouping columns from
    # frames passed to GroupBy.apply, which would drop city/family here
    feats = pd.concat([add_internal_features(g)
                       for _, g in panel.groupby(["city", "family"], sort=False)],
                      ignore_index=True)
    feats = pd.concat([feats, calendar_frame(feats["day"])], axis=1)

    # Weather for the target day t+1 ...
    w_target = weather.rename(columns={c: f"wx_t1_{c}" for c in WEATHER_VARS}).copy()
    w_target["day"] = w_target["day"] - pd.Timedelta(days=1)   # joins onto decision day t
    feats = feats.merge(w_target, on=["city", "day"], how="left")
    # ... and lagged weather (day t), known at the cutoff with certainty.
    w_lag = weather.rename(columns={c: f"wx_t0_{c}" for c in WEATHER_VARS})
    feats = feats.merge(w_lag, on=["city", "day"], how="left")

    internal_cols = [f"lag_{l}" for l in LAGS] + \
                    [f"roll_{s}_{w}" for w in ROLL_WINDOWS for s in ("mean", "std")]
    calendar_cols = [c for c in feats.columns if c.startswith("cal_")]
    weather_cols = [c for c in feats.columns if c.startswith("wx_")]
    weather_lagged_cols = [c for c in feats.columns if c.startswith("wx_t0_")]

    before = len(feats)
    feats = feats.dropna(subset=internal_cols + ["target"]).reset_index(drop=True)
    feats = feats.dropna(subset=weather_cols).reset_index(drop=True)

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    feats.to_parquet(DATA_PROCESSED / "features.parquet", index=False)
    registry = {
        "rows": len(feats),
        "rows_dropped_warmup_or_missing": before - len(feats),
        "feature_sets": {
            "internal": internal_cols,
            "calendar": internal_cols + calendar_cols,
            "weather": internal_cols + weather_cols,
            "calendar_weather": internal_cols + calendar_cols + weather_cols,
            "calendar_weather_lagged_only": internal_cols + calendar_cols + weather_lagged_cols,
        },
        "id_cols": ["city", "family", "day"],
        "target": "n[t+1]",
        "leakage_note": "rolling windows end at day t; target-day weather is assumption A3",
    }
    write_json(DATA_PROCESSED / "feature_registry.json", registry)
    print(f"features: {len(feats)} rows, {len(feats.columns)} cols")
    return 0


if __name__ == "__main__":
    sys.exit(main())
