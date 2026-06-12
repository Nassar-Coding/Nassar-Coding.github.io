"""Generate every table and figure used by the paper and supplement.

Redesign-compliant (C3, C6, G11): headline aggregations use validation-only
selection; no gap-closure or oracle normalization exists; every artifact is
hashed into outputs/tables/_provenance.json together with the experiment
run id so stale artifacts are detectable by the guard suite.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from common.runtime import DATA_INTERIM, OUTPUTS  # noqa: E402

T = OUTPUTS / "tables"
F = OUTPUTS / "figures"
M = OUTPUTS / "metrics"
CITY_LABELS = {"nyc": "New York", "chicago": "Chicago", "sf": "San Francisco",
               "austin": "Austin"}
plt.rcParams.update({"figure.dpi": 150, "font.size": 9, "axes.grid": True,
                     "grid.alpha": 0.3})
GENERATED: list = []


def save_table(df: pd.DataFrame, name: str, float_fmt: str = "%.3f") -> None:
    T.mkdir(parents=True, exist_ok=True)
    df.to_csv(T / f"{name}.csv", index=False)
    GENERATED.append(T / f"{name}.csv")
    try:
        df.to_latex(T / f"{name}.tex", index=False, float_format=float_fmt, escape=True)
        GENERATED.append(T / f"{name}.tex")
    except Exception:
        pass


def save_fig(fig, name: str) -> None:
    for ext in ("pdf", "png"):
        fig.savefig(F / f"{name}.{ext}")
        GENERATED.append(F / f"{name}.{ext}")
    plt.close(fig)


def cities_present() -> list:
    panel = pd.read_parquet(DATA_INTERIM / "panel_311.parquet")
    return sorted(panel["city"].unique())


def fig_panel_overview() -> None:
    panel = pd.read_parquet(DATA_INTERIM / "panel_311.parquet")
    cities = cities_present()
    daily = panel.groupby(["city", "day"])["n"].sum().reset_index()
    fig, axes = plt.subplots(len(cities), 1, figsize=(7.0, 1.9 * len(cities)),
                             sharex=True, squeeze=False)
    for ax, city in zip(axes[:, 0], cities):
        d = daily[daily.city == city]
        ax.plot(d["day"], d["n"], lw=0.4, color="tab:blue")
        ax.plot(d["day"], d["n"].rolling(28, center=True).mean(), lw=1.2,
                color="tab:red")
        ax.set_ylabel(CITY_LABELS[city], fontsize=8)
    axes[-1, 0].set_xlabel("date")
    fig.suptitle("Daily 311 request totals (blue) with 28-day centred mean (red)")
    fig.tight_layout()
    save_fig(fig, "fig1_panel_overview")


def table_validation_selected() -> pd.DataFrame:
    """Headline: validation-selected model per (city, feature set), single
    test evaluation (C3)."""
    vs = pd.read_csv(M / "validation_selection.csv")
    local = vs[vs.scope == "local"].copy()
    out = local.pivot_table(index="city", columns="feature_set",
                            values="test_mae").round(3)
    fsets = ["internal", "calendar", "weather", "calendar_weather"]
    out = out[[c for c in fsets if c in out.columns]].reset_index()
    save_table(out, "tab1_valselected_test_mae")
    save_table(local[["city", "feature_set", "selected_model", "val_mae", "test_mae"]]
               .round(3), "tab1b_valselected_detail")
    return out


def table_forecast_exhaustive() -> None:
    """Supplement-only descriptive grid: every model x feature set."""
    fm = pd.read_csv(M / "forecast_metrics.csv")
    test = fm[(fm.split == "test") & (fm.scope == "local") &
              (fm.feature_set.isin(["internal", "calendar", "weather",
                                    "calendar_weather"]))]
    main = (test.pivot_table(index=["city", "model"], columns="feature_set",
                             values="mae").round(3).reset_index())
    main = main[["city", "model", "internal", "calendar", "weather",
                 "calendar_weather"]]
    save_table(main, "tab2_forecast_mae_exhaustive")


def fig_accuracy_gain() -> None:
    """Test-MAE reduction vs trailing-mean naive for the VALIDATION-selected
    model of each feature set (C3-compliant)."""
    vs = pd.read_csv(M / "validation_selection.csv")
    fm = pd.read_csv(M / "forecast_metrics.csv")
    test = fm[(fm.split == "test") & (fm.scope == "local")]
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    width = 0.18
    cities = cities_present()
    fsets = ["internal", "calendar", "weather", "calendar_weather"]
    colors = ["#888", "tab:orange", "tab:green", "tab:blue"]
    for j, fset in enumerate(fsets):
        vals = []
        for c in cities:
            sel = vs[(vs.scope == "local") & (vs.city == c) & (vs.feature_set == fset)]
            naive = test[(test.city == c) & (test.model == "naive_trailing7") &
                         (test.feature_set == "internal")]["mae"].iloc[0]
            vals.append(100 * (1 - sel["test_mae"].iloc[0] / naive))
        ax.bar(np.arange(len(cities)) + (j - 1.5) * width, vals, width,
               label=fset, color=colors[j])
    ax.set_xticks(range(len(cities)), [CITY_LABELS[c] for c in cities])
    ax.set_ylabel("% test-MAE reduction vs naive\n(validation-selected model)")
    ax.legend(fontsize=7, ncol=4)
    fig.tight_layout()
    save_fig(fig, "fig2_accuracy_gain")


def table_decision_main() -> None:
    dm = pd.read_csv(M / "decision_metrics.csv")
    keep = dm[["city", "regime", "units", "policy", "config", "total_loss",
               "pct_reduction_vs_uniform", "final_carryover",
               "served_fraction_other"]].round(3)
    save_table(keep, "tab3_decision_all")
    # compact main-text view: uniform / proportional+valbest implicit via
    # inference table; here per-policy best rows excluding the hindsight
    # reference (supplement-only by design decision U6)
    main = keep[keep.policy != "hindsight_myopic_reference"]
    save_table(main, "tab3b_decision_main")


def fig_accuracy_vs_decision() -> None:
    """Test MAE (x) vs % simulated-loss reduction relative to the uniform
    floor (y) for the fixed point-forecast grid under the greedy policy."""
    fm = pd.read_csv(M / "forecast_metrics.csv")
    dm = pd.read_csv(M / "decision_metrics.csv")
    test = fm[fm.split == "test"]
    g = dm[dm.policy == "greedy_ev_point"]
    g = g[~g.config.str.startswith("quantile/")]
    cities = cities_present()
    fig, axes = plt.subplots(len(cities), 3, figsize=(8.0, 2.3 * len(cities)),
                             squeeze=False)
    for i, city in enumerate(cities):
        for j, regime in enumerate(["scarce", "moderate", "generous"]):
            ax = axes[i, j]
            grp = g[(g.city == city) & (g.regime == regime)]
            xs, ys = [], []
            for _, r in grp.iterrows():
                scope, fset, model = r["config"].split("/")
                mrow = test[(test.scope == scope) & (test.city == city) &
                            (test.feature_set == fset) & (test.model == model)]
                if mrow.empty:
                    continue
                xs.append(mrow["mae"].iloc[0])
                ys.append(r["pct_reduction_vs_uniform"])
            ax.scatter(xs, ys, s=14, color="tab:blue")
            if i == 0:
                ax.set_title(regime, fontsize=9)
            if j == 0:
                ax.set_ylabel(f"{CITY_LABELS[city]}\n% loss reduction vs uniform",
                              fontsize=7)
            if i == len(cities) - 1:
                ax.set_xlabel("test MAE", fontsize=8)
    fig.suptitle("Forecast accuracy vs simulated decision value "
                 "(hypothetical service-pressure regimes)")
    fig.tight_layout()
    save_fig(fig, "fig3_accuracy_vs_decision")


def table_rank_agreement() -> None:
    from scipy.stats import spearmanr
    fm = pd.read_csv(M / "forecast_metrics.csv")
    dm = pd.read_csv(M / "decision_metrics.csv")
    test = fm[fm.split == "test"]
    g = dm[(dm.policy == "greedy_ev_point") &
           (~dm.config.str.startswith("quantile/"))]
    rows = []
    for (city, regime), grp in g.groupby(["city", "regime"]):
        maes, losses = [], []
        for _, r in grp.iterrows():
            scope, fset, model = r["config"].split("/")
            mrow = test[(test.scope == scope) & (test.city == city) &
                        (test.feature_set == fset) & (test.model == model)]
            if mrow.empty:
                continue
            maes.append(mrow["mae"].iloc[0])
            losses.append(r["total_loss"])
        rho, p = spearmanr(maes, losses)
        rows.append({"city": city, "regime": regime, "n_models": len(maes),
                     "spearman_rho": round(rho, 4)})
    save_table(pd.DataFrame(rows), "tab4_rank_agreement")


def fig_fold_stability() -> None:
    folds = pd.read_csv(M / "fold_metrics.csv")
    cities = cities_present()
    fig, axes = plt.subplots(1, len(cities), figsize=(2.4 * len(cities), 2.6),
                             sharey=False, squeeze=False)
    for ax, city in zip(axes[0], cities):
        sub = folds[(folds.city == city) & (folds.model == "lgbm_point")]
        for fset, color in [("internal", "#888"), ("calendar", "tab:orange"),
                            ("calendar_weather", "tab:blue")]:
            s = sub[sub.feature_set == fset].sort_values("fold")
            ax.plot(s["fold"], s["mae"], marker="o", ms=3, label=fset, color=color)
        ax.set_title(CITY_LABELS[city], fontsize=9)
        ax.set_xlabel("fold")
    axes[0, 0].set_ylabel("fold MAE (LightGBM)")
    axes[0, 0].legend(fontsize=6)
    fig.tight_layout()
    save_fig(fig, "fig4_fold_stability")


def main() -> None:
    F.mkdir(parents=True, exist_ok=True)
    fig_panel_overview()
    table_validation_selected()
    table_forecast_exhaustive()
    fig_accuracy_gain()
    table_decision_main()
    fig_accuracy_vs_decision()
    table_rank_agreement()
    fig_fold_stability()
    for src, name in [("quantile_metrics.csv", "tab5_quantile"),
                      ("decision_selection.csv", "tab6_selection"),
                      ("decision_sensitivity.csv", "tab7_sensitivity"),
                      ("decision_inference.csv", "tab8_inference"),
                      ("significance_tests.csv", "tab9_forecast_inference"),
                      ("trend_diagnostics.csv", "tab10_trend_diagnostics")]:
        save_table(pd.read_csv(M / src).round(4), name)

    # provenance manifest (stale-artifact guard G11)
    run_id = json.loads((M / "run_id.json").read_text())
    manifest = {"run_id": run_id,
                "files": {str(p.relative_to(OUTPUTS)):
                          hashlib.sha256(p.read_bytes()).hexdigest()[:16]
                          for p in GENERATED}}
    (T / "_provenance.json").write_text(json.dumps(manifest, indent=2))
    print(f"tables and figures written; {len(GENERATED)} artifacts in provenance manifest")


if __name__ == "__main__":
    main()
