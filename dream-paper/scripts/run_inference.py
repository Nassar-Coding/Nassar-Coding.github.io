"""Dependence-aware inference for forecast-accuracy contrasts (redesign U2).

All contrasts use the paired moving-block bootstrap (block and resample
counts from configs/decision.yml, register resolution: moving-block
everywhere) applied to the DAILY MEAN absolute-error differential between
two configurations, computed on the untouched test window. CIs replace the
earlier day-resampling p-values, which under-modeled serial dependence.

Output: outputs/metrics/significance_tests.csv
        (city, comparison, mean daily |err| diff, 95% block-bootstrap CI)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from common.runtime import DATA_PROCESSED, OUTPUTS, load_config  # noqa: E402
from optimization.allocation import moving_block_bootstrap_ci  # noqa: E402

COMPARISONS = [
    ("calendar vs internal (lgbm)",
     ("local", "calendar", "lgbm_point"), ("local", "internal", "lgbm_point")),
    ("cal_weather vs calendar (lgbm)",
     ("local", "calendar_weather", "lgbm_point"), ("local", "calendar", "lgbm_point")),
    ("cal_weather lgbm vs seasonal_naive",
     ("local", "calendar_weather", "lgbm_point"), ("local", "internal", "seasonal_naive7")),
    ("global vs local (cal_weather lgbm)",
     ("global", "calendar_weather", "lgbm_point"), ("local", "calendar_weather", "lgbm_point")),
    ("lagged-weather vs target-day weather (lgbm)",
     ("local", "calendar_weather_lagged_only", "lgbm_point"),
     ("local", "calendar_weather", "lgbm_point")),
]


def daily_mean_abs_err(df: pd.DataFrame) -> pd.Series:
    err = (df["target"] - df["pred"]).abs()
    return err.groupby(df["day"]).mean().sort_index()


def main() -> None:
    inf = load_config("decision.yml")["inference"]
    preds = pd.read_parquet(DATA_PROCESSED / "test_predictions.parquet")
    rows = []
    for city in sorted(preds["city"].unique()):
        cp = preds[preds.city == city]
        for name, a, b in COMPARISONS:
            A = cp[(cp.scope == a[0]) & (cp.feature_set == a[1]) & (cp.model == a[2])]
            B = cp[(cp.scope == b[0]) & (cp.feature_set == b[1]) & (cp.model == b[2])]
            if A.empty or B.empty:
                continue
            da, db = daily_mean_abs_err(A), daily_mean_abs_err(B)
            assert (da.index == db.index).all(), "day misalignment in contrast"
            diff = (da - db).to_numpy()
            mean, lo, hi = moving_block_bootstrap_ci(
                diff, block=inf["block_length_days"],
                n_boot=inf["n_resamples"], seed=inf["seed"])
            rows.append({"city": city, "comparison": name,
                         "mean_daily_abs_err_diff": round(mean, 3),
                         "ci95_lo": round(lo, 3), "ci95_hi": round(hi, 3),
                         "ci_excludes_zero": bool(hi < 0 or lo > 0),
                         "n_days": len(diff),
                         "block_length": inf["block_length_days"]})
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUTS / "metrics" / "significance_tests.csv", index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
