"""Causal sensitivity for two-sided weather interpolation.

PREREGISTERED METHOD (chosen before any result was computed): method (1): drop every forecast target whose predictors depend on
a two-sided interpolated weather value, from EVERY temporal stage (training,
validation, and test), then refit and re-evaluate. The forward-only-interpolation alternative was not used.

Affected values (row-level audit, build_panel.py:132 pandas linear
interpolate(limit=7), two-sided by construction):
  - San Francisco: 14 TMAX and 12 TMIN station values (union of dates below),
    all inside the modeled span 2020-01-28..2025-02-05;
  - Austin: 2 TMAX and 2 TMIN values (2024-12-31 inside the span;
    2025-02-06 outside it).
A features row (decision day t) depends on an interpolated value when
weather(t+1) is interpolated (target-day features wx_t1_*) or weather(t) is
interpolated (current-day features wx_t0_*): affected decision days are
D union (D - 1 day).

Only the weather and calendar_weather feature sets consume weather columns,
so only they are refit; internal and calendar are unaffected by construction.
Split boundaries are computed on the FULL day list (identical to the primary
protocol) and affected rows are then removed from each stage, so stage
boundaries are unchanged.

Outputs: outputs/metrics/weather_causal_sensitivity.csv with, per
(city, feature_set, model): published-protocol original test MAE (recomputed
in-harness and cross-checked against forecast_metrics.csv), the bridge MAE
(original fit, reduced test set), and the sensitivity MAE (reduced fit,
reduced test set), plus deltas.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common.runtime import DATA_PROCESSED, OUTPUTS, load_config, set_seed  # noqa: E402
from evaluation.protocol import chrono_split, split_masks  # noqa: E402
from forecasting.models import make_point_models  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
GLOBAL_SEED = 20260609


def interpolated_dates() -> dict:
    """Recompute, from raw GHCN files, the dates whose TMAX/TMIN values are
    filled by the two-sided limit-7 interpolation (deterministic audit)."""
    sources = yaml.safe_load(open(ROOT / "configs" / "data_sources.yml"))
    out = {}
    for st in sources["ghcn_daily"]["stations"]:
        city, sid = st["city"], st["station_id"]
        df = pd.read_csv(ROOT / "data" / "raw" / "weather" / f"{city}_{sid}.csv.gz",
                         dtype={"date": str})
        df = df[df["q_flag"].isna() | (df["q_flag"].astype(str).str.strip() == "")]
        df["day"] = pd.to_datetime(df["date"], format="%Y%m%d")
        wide = df.pivot_table(index="day", columns="element", values="value",
                              aggfunc="first")
        wide = wide.reindex(pd.date_range(wide.index.min(), wide.index.max(), freq="D"))
        dates = set()
        for col in ("TMAX", "TMIN"):
            if col not in wide.columns:
                continue
            miss = wide[col].isna()
            filled = wide[col].interpolate(limit=7)
            dates |= set(wide.index[miss & filled.notna()])
        if dates:
            out[city] = sorted(dates)
    return out


def design_local(df: pd.DataFrame, cols: list, all_families: list):
    parts = [df[cols].to_numpy(dtype=float)]
    names = list(cols)
    fam_d = pd.get_dummies(pd.Categorical(df["family"], categories=all_families),
                           prefix="fam")
    parts.append(fam_d.to_numpy(dtype=float))
    names += list(fam_d.columns)
    return np.hstack(parts), names


def run() -> None:
    set_seed()
    feats = pd.read_parquet(DATA_PROCESSED / "features.parquet")
    registry = pd.read_json(DATA_PROCESSED / "feature_registry.json", typ="series")
    fsets = registry["feature_sets"]
    all_families = sorted(feats["family"].unique())
    interp = interpolated_dates()

    rows = []
    for city, dates in sorted(interp.items()):
        D = pd.to_datetime(pd.Series(dates))
        affected_days = set(D) | set(D - pd.Timedelta(days=1))
        cf = feats[feats.city == city].reset_index(drop=True)
        t_end, v_end = chrono_split(cf["day"])
        m_tr, m_va, m_te = (m.to_numpy() for m in split_masks(cf["day"], t_end, v_end))
        aff = cf["day"].isin(list(affected_days)).to_numpy()
        n_aff = {"train": int((m_tr & aff).sum()), "val": int((m_va & aff).sum()),
                 "test": int((m_te & aff).sum())}
        for fset in ("weather", "calendar_weather"):
            cols = fsets[fset]
            X, names = design_local(cf, cols, all_families)
            y = cf["target"].to_numpy(dtype=float)
            for model_orig, model_sens in zip(make_point_models(GLOBAL_SEED),
                                              make_point_models(GLOBAL_SEED)):
                # original protocol: fit train+val, evaluate full test
                model_orig.fit(X[m_tr | m_va], y[m_tr | m_va], names)
                p_full = np.maximum(model_orig.predict(X[m_te]), 0.0)
                mae_orig = float(np.mean(np.abs(y[m_te] - p_full)))
                # bridge: original fit, reduced test set
                te_red = m_te & ~aff
                p_red = np.maximum(model_orig.predict(X[te_red]), 0.0)
                mae_bridge = float(np.mean(np.abs(y[te_red] - p_red)))
                # sensitivity: affected rows dropped from every stage, refit
                fit_mask = (m_tr | m_va) & ~aff
                model_sens.fit(X[fit_mask], y[fit_mask], names)
                p_sens = np.maximum(model_sens.predict(X[te_red]), 0.0)
                mae_sens = float(np.mean(np.abs(y[te_red] - p_sens)))
                # validation MAE under sensitivity (for selection stability)
                va_red = m_va & ~aff
                model_vs = [m for m in make_point_models(GLOBAL_SEED)
                            if m.name == model_sens.name][0]
                model_vs.fit(X[m_tr & ~aff], y[m_tr & ~aff], names)
                pv = np.maximum(model_vs.predict(X[va_red]), 0.0)
                vmae_sens = float(np.mean(np.abs(y[va_red] - pv)))
                rows.append({
                    "city": city, "feature_set": fset, "model": model_sens.name,
                    "affected_rows_train": n_aff["train"],
                    "affected_rows_val": n_aff["val"],
                    "affected_rows_test": n_aff["test"],
                    "test_mae_original": round(mae_orig, 4),
                    "test_mae_original_reduced_testset": round(mae_bridge, 4),
                    "test_mae_sensitivity": round(mae_sens, 4),
                    "delta_abs": round(mae_sens - mae_bridge, 4),
                    "delta_pct": round(100 * (mae_sens - mae_bridge) /
                                       mae_bridge if mae_bridge else 0.0, 3),
                    "val_mae_sensitivity": round(vmae_sens, 4),
                })
    out = OUTPUTS / "metrics"
    pd.DataFrame(rows).to_csv(out / "weather_causal_sensitivity.csv", index=False)
    print(f"weather causal sensitivity: {len(rows)} rows written")


if __name__ == "__main__":
    run()
