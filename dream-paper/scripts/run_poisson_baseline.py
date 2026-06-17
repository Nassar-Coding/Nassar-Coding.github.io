"""Poisson GLM count-data baseline (professor #65/#66).

311 targets are non-negative counts, so a Poisson regression is a natural
benchmark a reviewer expects. We add it as a REPORTED baseline only: it does not
enter the pre-registered eleven-configuration decision grid or the within-scope
headline selection (which would change frozen artifacts); it is fit per city and
feature set on train+validation, evaluated once on the untouched test window,
and compared to the validation-selected model and the naive trailing-mean.
Writes outputs/metrics/poisson_baseline.csv.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import PoissonRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from common.runtime import DATA_PROCESSED, OUTPUTS, GLOBAL_SEED, set_seed  # noqa: E402
from evaluation.protocol import chrono_split, split_masks, mae  # noqa: E402

FSETS = ["internal", "calendar", "calendar_weather"]


def design(df, cols, fams):
    parts = [df[cols].to_numpy(dtype=float)]
    fam = pd.get_dummies(pd.Categorical(df["family"], categories=fams), prefix="fam")
    parts.append(fam.to_numpy(dtype=float))
    return np.hstack(parts)


def run() -> None:
    set_seed()
    feats = pd.read_parquet(DATA_PROCESSED / "features.parquet")
    registry = pd.read_json(DATA_PROCESSED / "feature_registry.json", typ="series")
    fsets = registry["feature_sets"]
    cities = sorted(feats["city"].unique())
    fams = sorted(feats["family"].unique())
    vs = pd.read_csv(OUTPUTS / "metrics" / "validation_selection.csv")
    fm = pd.read_csv(OUTPUTS / "metrics" / "forecast_metrics.csv")
    test = fm[fm.split == "test"]

    rows = []
    for city in cities:
        df = feats[feats.city == city]
        t_end, v_end = chrono_split(df["day"])
        m_tr, m_va, m_te = split_masks(df["day"], t_end, v_end)
        fit = (m_tr | m_va).to_numpy(); te = m_te.to_numpy()
        y = df["target"].to_numpy(dtype=float)
        for fset in FSETS:
            X = design(df, fsets[fset], fams)
            pois = Pipeline([("s", StandardScaler()),
                             ("p", PoissonRegressor(alpha=1.0, max_iter=2000))])
            pois.fit(X[fit], np.maximum(y[fit], 0.0))
            p = np.maximum(pois.predict(X[te]), 0.0)
            pois_mae = mae(y[te], p)
            sel = vs[(vs.scope == "local") & (vs.city == city) & (vs.feature_set == fset)]
            sel_mae = float(sel["test_mae"].iloc[0]) if not sel.empty else np.nan
            sel_model = sel["selected_model"].iloc[0] if not sel.empty else ""
            naive = test[(test.scope == "local") & (test.city == city) &
                         (test.feature_set == "internal") &
                         (test.model == "naive_trailing7")]["mae"]
            naive_mae = float(naive.iloc[0]) if len(naive) else np.nan
            rows.append({"city": city, "feature_set": fset,
                         "poisson_glm_mae": round(pois_mae, 3),
                         "selected_model": sel_model,
                         "selected_mae": round(sel_mae, 3),
                         "naive_mae": round(naive_mae, 3),
                         "poisson_beats_selected": bool(pois_mae < sel_mae),
                         "poisson_beats_naive": bool(pois_mae < naive_mae)})
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "metrics" / "poisson_baseline.csv", index=False)
    print(out.to_string(index=False))
    print(f"\nPoisson beats the validation-selected model in "
          f"{int(out.poisson_beats_selected.sum())}/{len(out)} (city,feature-set) cells; "
          f"beats naive in {int(out.poisson_beats_naive.sum())}/{len(out)}.")


if __name__ == "__main__":
    run()
