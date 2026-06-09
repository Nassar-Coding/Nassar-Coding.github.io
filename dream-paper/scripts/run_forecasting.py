"""Experiment 1 — forecasting benchmark across cities, feature sets, models.

Protocol (docs/01_problem_definition.md):
  - per-city chronological 70/15/15 split by day;
  - model selection on validation MAE; selected configs refit on train+val
    and evaluated once on the untouched test window;
  - five expanding-window rolling-origin folds for stability;
  - pooled "global" variant trains one model on all cities with city
    indicators, evaluated per city on the same test windows;
  - leave-one-city-out zero-shot transfer for the pooled model;
  - LightGBM quantile model provides the predictive distribution used by
    the decision layer (pinball loss + interval coverage reported).

Outputs:
  outputs/metrics/forecast_metrics.csv     every (scope, city, fset, model) x split
  outputs/metrics/fold_metrics.csv         rolling-origin folds
  outputs/metrics/quantile_metrics.csv
  data/processed/test_predictions.parquet  per-row test predictions (decision layer input)
  data/processed/val_predictions.parquet   per-row validation predictions
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from common.runtime import DATA_PROCESSED, OUTPUTS, GLOBAL_SEED, set_seed  # noqa: E402
from evaluation.protocol import (chrono_split, split_masks, rolling_origin_folds,  # noqa: E402
                                 mae, rmse, mape_floored, pinball, coverage)
from forecasting.models import make_point_models, LightGBMQuantile, QUANTILES  # noqa: E402

FEATURE_SETS = ["internal", "calendar", "weather", "calendar_weather"]
SENSITIVITY_SETS = ["calendar_weather_lagged_only"]


ALL_FAMILIES: list = []
ALL_CITIES: list = []


def design_matrix(df: pd.DataFrame, cols: list, add_city_dummies: bool) -> tuple[np.ndarray, list]:
    """Build the numeric matrix with category lists pinned globally, so
    train/test column layouts are identical even when a subset of cities or
    families is present (pooled and leave-one-city-out settings)."""
    parts = [df[cols].to_numpy(dtype=float)]
    names = list(cols)
    fam_d = pd.get_dummies(pd.Categorical(df["family"], categories=ALL_FAMILIES),
                           prefix="fam")
    parts.append(fam_d.to_numpy(dtype=float))
    names += list(fam_d.columns)
    if add_city_dummies:
        city_d = pd.get_dummies(pd.Categorical(df["city"], categories=ALL_CITIES),
                                prefix="city")
        parts.append(city_d.to_numpy(dtype=float))
        names += list(city_d.columns)
    return np.hstack(parts), names


def eval_block(y, p, days):  # noqa: ANN001
    return {"mae": mae(y, p), "rmse": rmse(y, p), "mape_floored": mape_floored(y, p),
            "n_rows": int(len(y)), "n_days": int(pd.Series(days).nunique())}


def run() -> None:
    set_seed()
    feats = pd.read_parquet(DATA_PROCESSED / "features.parquet")
    registry = pd.read_json(DATA_PROCESSED / "feature_registry.json", typ="series")
    fsets = registry["feature_sets"]
    cities = sorted(feats["city"].unique())
    ALL_FAMILIES.extend(sorted(feats["family"].unique()))
    ALL_CITIES.extend(cities)

    # per-city split boundaries
    bounds = {c: chrono_split(feats.loc[feats.city == c, "day"]) for c in cities}

    metrics_rows, fold_rows, qrows = [], [], []
    test_pred_frames, val_pred_frames = [], []

    # ---------------- local (per-city) and global (pooled) point models ----
    for scope in ["local", "global"]:
        for fset_name in FEATURE_SETS + SENSITIVITY_SETS:
            cols = fsets[fset_name]
            scopes = cities if scope == "local" else ["__pooled__"]
            for unit in scopes:
                df = feats if unit == "__pooled__" else feats[feats.city == unit]
                X, names = design_matrix(df, cols, add_city_dummies=(unit == "__pooled__"))
                y = df["target"].to_numpy(dtype=float)
                days = df["day"]

                for model in make_point_models(GLOBAL_SEED):
                    t0 = time.time()
                    if unit == "__pooled__":
                        # masks are per-city boundaries applied row-wise
                        tr = np.zeros(len(df), dtype=bool); va = tr.copy(); te = tr.copy()
                        for c in cities:
                            m_tr, m_va, m_te = split_masks(df["day"], *bounds[c])
                            in_c = (df["city"] == c).to_numpy()
                            tr |= (m_tr.to_numpy() & in_c); va |= (m_va.to_numpy() & in_c)
                            te |= (m_te.to_numpy() & in_c)
                    else:
                        m_tr, m_va, m_te = split_masks(days, *bounds[unit])
                        tr, va, te = m_tr.to_numpy(), m_va.to_numpy(), m_te.to_numpy()

                    model.fit(X[tr], y[tr], names)
                    p_va = np.maximum(model.predict(X[va]), 0.0)
                    # refit on train+val for the final test evaluation
                    model.fit(X[tr | va], y[tr | va], names)
                    p_te = np.maximum(model.predict(X[te]), 0.0)

                    eval_units = cities if unit == "__pooled__" else [unit]
                    for ec in eval_units:
                        if unit == "__pooled__":
                            mva = va & (df["city"] == ec).to_numpy()
                            mte = te & (df["city"] == ec).to_numpy()
                            pva = p_va[(df.loc[va, "city"] == ec).to_numpy()]
                            pte = p_te[(df.loc[te, "city"] == ec).to_numpy()]
                        else:
                            mva, mte, pva, pte = va, te, p_va, p_te
                        for split, mask, preds in [("val", mva, pva), ("test", mte, pte)]:
                            res = eval_block(y[mask], preds, days[mask])
                            res.update(scope=scope, city=ec, feature_set=fset_name,
                                       model=model.name, split=split,
                                       fit_seconds=round(time.time() - t0, 2))
                            metrics_rows.append(res)
                            sub = df.loc[mask, ["city", "family", "day", "target"]].copy()
                            sub["pred"] = preds
                            sub["scope"], sub["feature_set"], sub["model"] = scope, fset_name, model.name
                            (test_pred_frames if split == "test" else val_pred_frames).append(sub)

    # ---------------- rolling-origin stability (local, key configs) --------
    for city in cities:
        df = feats[feats.city == city]
        days = df["day"]
        for fset_name in ["internal", "calendar", "calendar_weather"]:
            cols = fsets[fset_name]
            X, names = design_matrix(df, cols, add_city_dummies=False)
            y = df["target"].to_numpy(dtype=float)
            for k, (m_tr, m_ev) in enumerate(rolling_origin_folds(days)):
                tr, ev = m_tr.to_numpy(), m_ev.to_numpy()
                for model in make_point_models(GLOBAL_SEED):
                    model.fit(X[tr], y[tr], names)
                    p = np.maximum(model.predict(X[ev]), 0.0)
                    fold_rows.append({"city": city, "feature_set": fset_name,
                                      "model": model.name, "fold": k,
                                      "mae": mae(y[ev], p), "n_rows": int(ev.sum())})

    # ---------------- quantile models (local + pooled) ---------------------
    cols = fsets["calendar_weather"]
    for unit in cities + ["__pooled__"]:
        df = feats if unit == "__pooled__" else feats[feats.city == unit]
        X, names = design_matrix(df, cols, add_city_dummies=(unit == "__pooled__"))
        y = df["target"].to_numpy(dtype=float)
        if unit == "__pooled__":
            tr = np.zeros(len(df), dtype=bool); te = tr.copy()
            for c in cities:
                m_tr, m_va, m_te = split_masks(df["day"], *bounds[c])
                in_c = (df["city"] == c).to_numpy()
                tr |= ((m_tr | m_va).to_numpy() & in_c); te |= (m_te.to_numpy() & in_c)
        else:
            m_tr, m_va, m_te = split_masks(df["day"], *bounds[unit])
            tr, te = (m_tr | m_va).to_numpy(), m_te.to_numpy()
        qm = LightGBMQuantile(seed=GLOBAL_SEED)
        qm.fit(X[tr], y[tr], names)
        qp = qm.predict_quantiles(X[te])
        eval_units = cities if unit == "__pooled__" else [unit]
        for ec in eval_units:
            if unit == "__pooled__":
                sel = (df.loc[te, "city"] == ec).to_numpy()
                yy = y[te][sel]; qq = {q: qp[q][sel] for q in qp}
                mask_rows = df.loc[te].loc[sel]
            else:
                yy = y[te]; qq = qp; mask_rows = df.loc[te]
            qrows.append({"scope": "global" if unit == "__pooled__" else "local",
                          "city": ec, "model": "lgbm_quantile",
                          "pinball": pinball(yy, qq),
                          "coverage_90": coverage(yy, qq[0.05], qq[0.95]),
                          "coverage_50": coverage(yy, qq[0.25], qq[0.75]),
                          "mae_median": mae(yy, qq[0.50])})
            sub = mask_rows[["city", "family", "day", "target"]].copy()
            for q in qq:
                sub[f"q{int(q * 100):02d}"] = qq[q]
            sub["scope"] = "global" if unit == "__pooled__" else "local"
            sub["feature_set"] = "calendar_weather"; sub["model"] = "lgbm_quantile"
            sub["pred"] = sub["q50"]
            test_pred_frames.append(sub)

    # ---------------- leave-one-city-out zero-shot transfer ----------------
    for held in cities:
        df_tr = feats[feats.city != held]
        df_te = feats[feats.city == held]
        m_tr_, m_va_, m_te_ = split_masks(df_te["day"], *bounds[held])
        df_te_final = df_te[m_te_.to_numpy()]
        X_tr, names = design_matrix(df_tr, cols, add_city_dummies=False)
        X_te, _ = design_matrix(df_te_final, cols, add_city_dummies=False)
        import lightgbm as lgb
        m = lgb.LGBMRegressor(objective="regression_l1", n_estimators=600,
                              learning_rate=0.05, num_leaves=63, min_child_samples=30,
                              random_state=GLOBAL_SEED, verbose=-1, n_jobs=-1)
        m.fit(X_tr, df_tr["target"])
        p = np.maximum(m.predict(X_te), 0.0)
        metrics_rows.append({**eval_block(df_te_final["target"], p, df_te_final["day"]),
                             "scope": "loco_zero_shot", "city": held,
                             "feature_set": "calendar_weather", "model": "lgbm_point",
                             "split": "test", "fit_seconds": None})

    out_m = OUTPUTS / "metrics"; out_m.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(metrics_rows).to_csv(out_m / "forecast_metrics.csv", index=False)
    pd.DataFrame(fold_rows).to_csv(out_m / "fold_metrics.csv", index=False)
    pd.DataFrame(qrows).to_csv(out_m / "quantile_metrics.csv", index=False)
    pd.concat(test_pred_frames, ignore_index=True).to_parquet(
        DATA_PROCESSED / "test_predictions.parquet", index=False)
    pd.concat(val_pred_frames, ignore_index=True).to_parquet(
        DATA_PROCESSED / "val_predictions.parquet", index=False)
    print(f"forecast metrics: {len(metrics_rows)} rows; folds: {len(fold_rows)}; quantile: {len(qrows)}")


if __name__ == "__main__":
    run()
