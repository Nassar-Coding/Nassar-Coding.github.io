"""C3 sensitivity: normalized / log-scale global pooling (professor #75-#79).

Tests whether the published "cross-city pooling hurts" conclusion is an artifact
of pooling RAW counts across cities whose daily volumes differ by an order of
magnitude (New York ~1.5k/day vs Austin ~150/day), which lets an absolute-error
objective be dominated by the largest city. We refit the pooled lgbm_point model
on calendar_weather under three target normalizations, stage-censored exactly as
the published pooled model (test-stage training rows dated <= the minimum
validation-end across cities, so no pooled training row is contemporaneous with
any city's test window), and evaluate per city on the untouched test window:

  raw        : published global pooling (absolute target)
  log1p      : multiplicative scale, predict expm1
  per_city_z : target standardized by each city's TRAIN-window mean/sd,
               de-standardized per evaluation city

Comparison is against the local lgbm_point test MAE from forecast_metrics.csv.
A reversal (any normalized pooling beating local in most cities) would overturn
a headline and trigger stop condition #3. Writes outputs/metrics/logpool_sensitivity.csv.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import lightgbm as lgb

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from common.runtime import DATA_PROCESSED, OUTPUTS, GLOBAL_SEED, set_seed  # noqa: E402
from evaluation.protocol import chrono_split, split_masks, mae  # noqa: E402

LGB_PARAMS = dict(objective="regression_l1", n_estimators=600, learning_rate=0.05,
                  num_leaves=63, min_child_samples=30, random_state=GLOBAL_SEED,
                  verbose=-1, n_jobs=-1)


def design(df, cols, all_families, all_cities, city_dummies):
    parts = [df[cols].to_numpy(dtype=float)]
    fam = pd.get_dummies(pd.Categorical(df["family"], categories=all_families), prefix="fam")
    parts.append(fam.to_numpy(dtype=float))
    if city_dummies:
        cd = pd.get_dummies(pd.Categorical(df["city"], categories=all_cities), prefix="city")
        parts.append(cd.to_numpy(dtype=float))
    return np.hstack(parts)


def run() -> None:
    set_seed()
    feats = pd.read_parquet(DATA_PROCESSED / "features.parquet")
    registry = pd.read_json(DATA_PROCESSED / "feature_registry.json", typ="series")
    cols = registry["feature_sets"]["calendar_weather"]
    cities = sorted(feats["city"].unique())
    fams = sorted(feats["family"].unique())
    bounds = {c: chrono_split(feats.loc[feats.city == c, "day"]) for c in cities}
    min_v_end = min(b[1] for b in bounds.values())

    fm = pd.read_csv(OUTPUTS / "metrics" / "forecast_metrics.csv")
    loc = fm[(fm.split == "test") & (fm.scope == "local") &
             (fm.feature_set == "calendar_weather") & (fm.model == "lgbm_point")]
    local_mae = {c: float(loc[loc.city == c]["mae"].iloc[0]) for c in cities}

    df = feats.copy()
    X = design(df, cols, fams, cities, city_dummies=True)
    y = df["target"].to_numpy(dtype=float)
    d_arr = df["day"].to_numpy()
    city_arr = df["city"].to_numpy()

    # masks
    tr = np.zeros(len(df), bool); va = tr.copy(); te = tr.copy()
    for c in cities:
        m_tr, m_va, m_te = split_masks(df["day"], *bounds[c])
        inc = (df["city"] == c).to_numpy()
        tr |= m_tr.to_numpy() & inc; va |= m_va.to_numpy() & inc; te |= m_te.to_numpy() & inc
    # test-stage pooled fit: train+val rows, censored at min validation end
    fit = (tr | va) & (d_arr <= np.datetime64(min_v_end))

    # per-city train-window standardization stats (pre-test, training rows only)
    mu = {c: float(y[tr & (city_arr == c)].mean()) for c in cities}
    sd = {c: float(y[tr & (city_arr == c)].std() + 1e-9) for c in cities}

    rows = []
    for norm in ["raw", "log1p", "per_city_z"]:
        if norm == "raw":
            yt = y.copy()
        elif norm == "log1p":
            yt = np.log1p(y)
        else:
            yt = np.array([(y[i] - mu[city_arr[i]]) / sd[city_arr[i]] for i in range(len(y))])
        m = lgb.LGBMRegressor(**LGB_PARAMS)
        m.fit(X[fit], yt[fit])
        pred = m.predict(X[te])
        for ci, c in enumerate(cities):
            sel = (city_arr[te] == c)
            if norm == "raw":
                pc = np.maximum(pred[sel], 0.0)
            elif norm == "log1p":
                pc = np.maximum(np.expm1(pred[sel]), 0.0)
            else:
                pc = np.maximum(pred[sel] * sd[c] + mu[c], 0.0)
            yc = y[te][sel]
            pooled = mae(yc, pc)
            rows.append({"normalization": norm, "city": c,
                         "pooled_mae": round(pooled, 3),
                         "local_mae": round(local_mae[c], 3),
                         "pct_vs_local": round(100 * (pooled - local_mae[c]) / local_mae[c], 2),
                         "pooled_beats_local": bool(pooled < local_mae[c])})
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "metrics" / "logpool_sensitivity.csv", index=False)
    print(out.to_string(index=False))
    print("\nPER-NORMALIZATION: cities where pooling beats local (out of 4):")
    for norm, g in out.groupby("normalization"):
        print(f"  {norm:11}: {int(g.pooled_beats_local.sum())}/4  "
              f"(median {g.pct_vs_local.median():+.1f}% vs local)")


if __name__ == "__main__":
    run()
