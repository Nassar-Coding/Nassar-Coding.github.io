"""Generate every table and figure used by the paper and supplement.

Reads only outputs/metrics/*.csv and data layers; writes
outputs/tables/*.csv (+ .tex) and outputs/figures/*.pdf/png.
Every artifact in the manuscript regenerates from this single script.
"""

from __future__ import annotations

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


def save_table(df: pd.DataFrame, name: str, float_fmt: str = "%.3f") -> None:
    T.mkdir(parents=True, exist_ok=True)
    df.to_csv(T / f"{name}.csv", index=False)
    try:
        df.to_latex(T / f"{name}.tex", index=False, float_format=float_fmt)
    except Exception:
        pass


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
    fig.savefig(F / "fig1_panel_overview.pdf"); fig.savefig(F / "fig1_panel_overview.png")
    plt.close(fig)


def table_forecast_main() -> pd.DataFrame:
    fm = pd.read_csv(M / "forecast_metrics.csv")
    test = fm[(fm.split == "test") & (fm.scope == "local") &
              (fm.feature_set.isin(["internal", "calendar", "weather", "calendar_weather"]))]
    main = (test.pivot_table(index=["city", "model"], columns="feature_set",
                             values="mae").round(3).reset_index())
    main = main[["city", "model", "internal", "calendar", "weather", "calendar_weather"]]
    save_table(main, "tab2_forecast_mae_main")
    return main


def fig_accuracy_gain() -> None:
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
            sub = test[(test.city == c) & (test.feature_set == fset)]
            naive = test[(test.city == c) & (test.model == "naive_trailing7") &
                         (test.feature_set == "internal")]["mae"].iloc[0]
            vals.append(100 * (1 - sub["mae"].min() / naive))
        ax.bar(np.arange(len(cities)) + (j - 1.5) * width, vals, width,
               label=fset, color=colors[j])
    ax.set_xticks(range(len(cities)), [CITY_LABELS[c] for c in cities])
    ax.set_ylabel("% test-MAE reduction vs naive")
    ax.legend(fontsize=7, ncol=4)
    fig.tight_layout()
    fig.savefig(F / "fig2_accuracy_gain.pdf"); fig.savefig(F / "fig2_accuracy_gain.png")
    plt.close(fig)


def table_decision_main() -> pd.DataFrame:
    dm = pd.read_csv(M / "decision_metrics.csv")
    rows = []
    for (city, regime), grp in dm.groupby(["city", "regime"]):
        uni = grp[grp.policy == "uniform"]["total_unmet_weighted"].iloc[0]
        ora = grp[grp.policy == "oracle"]["total_unmet_weighted"].iloc[0]
        for _, r in grp.iterrows():
            if r.policy in ("uniform", "oracle"):
                continue
            denom = uni - ora
            rows.append({
                "city": city, "regime": regime, "policy": r.policy,
                "config": r.config,
                "unmet_weighted": r.total_unmet_weighted,
                "red_vs_uniform_pct": 100 * (1 - r.total_unmet_weighted / uni),
                "oracle_gap_closed_pct": (100 * (uni - r.total_unmet_weighted) / denom
                                          if denom > 0 else np.nan),
            })
    out = pd.DataFrame(rows)
    save_table(out.round(3), "tab3_decision_all")
    return out


def fig_accuracy_vs_decision() -> None:
    """Core figure: forecast MAE vs decision loss, per city and regime."""
    fm = pd.read_csv(M / "forecast_metrics.csv")
    dm = pd.read_csv(M / "decision_metrics.csv")
    test = fm[(fm.split == "test")]
    dm = dm[dm.policy.isin(["greedy_ev_point"])]
    cities = cities_present()
    fig, axes = plt.subplots(len(cities), 3, figsize=(8.0, 2.3 * len(cities)),
                             squeeze=False)
    for i, city in enumerate(cities):
        for j, regime in enumerate(["scarce", "moderate", "generous"]):
            ax = axes[i, j]
            grp = dm[(dm.city == city) & (dm.regime == regime)]
            uni = pd.read_csv(M / "decision_metrics.csv")
            uni_v = uni[(uni.city == city) & (uni.regime == regime) &
                        (uni.policy == "uniform")]["total_unmet_weighted"].iloc[0]
            ora_v = uni[(uni.city == city) & (uni.regime == regime) &
                        (uni.policy == "oracle")]["total_unmet_weighted"].iloc[0]
            xs, ys = [], []
            for _, r in grp.iterrows():
                scope, fset, model = r["config"].split("/")
                mrow = test[(test.scope == scope) & (test.city == city) &
                            (test.feature_set == fset) & (test.model == model)]
                if mrow.empty:
                    continue
                xs.append(mrow["mae"].iloc[0])
                ys.append(100 * (uni_v - r.total_unmet_weighted) / (uni_v - ora_v)
                          if uni_v > ora_v else np.nan)
            ax.scatter(xs, ys, s=14, color="tab:blue")
            if i == 0:
                ax.set_title(regime, fontsize=9)
            if j == 0:
                ax.set_ylabel(f"{CITY_LABELS[city]}\noracle gap closed (%)", fontsize=7)
            if i == len(cities) - 1:
                ax.set_xlabel("test MAE", fontsize=8)
    fig.suptitle("Forecast accuracy vs decision value across capacity regimes")
    fig.tight_layout()
    fig.savefig(F / "fig3_accuracy_vs_decision.pdf")
    fig.savefig(F / "fig3_accuracy_vs_decision.png")
    plt.close(fig)


def table_rank_agreement() -> pd.DataFrame:
    from scipy.stats import spearmanr
    fm = pd.read_csv(M / "forecast_metrics.csv")
    dm = pd.read_csv(M / "decision_metrics.csv")
    test = fm[fm.split == "test"]
    rows = []
    for (city, regime), grp in dm[dm.policy == "greedy_ev_point"].groupby(["city", "regime"]):
        maes, losses = [], []
        for _, r in grp.iterrows():
            scope, fset, model = r["config"].split("/")
            mrow = test[(test.scope == scope) & (test.city == city) &
                        (test.feature_set == fset) & (test.model == model)]
            if mrow.empty:
                continue
            maes.append(mrow["mae"].iloc[0]); losses.append(r.total_unmet_weighted)
        rho, p = spearmanr(maes, losses)
        rows.append({"city": city, "regime": regime, "n_models": len(maes),
                     "spearman_rho": rho, "p_value": p})
    out = pd.DataFrame(rows).round(4)
    save_table(out, "tab4_rank_agreement")
    return out


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
    fig.savefig(F / "fig4_fold_stability.pdf"); fig.savefig(F / "fig4_fold_stability.png")
    plt.close(fig)


def main() -> None:
    F.mkdir(parents=True, exist_ok=True)
    fig_panel_overview()
    table_forecast_main()
    fig_accuracy_gain()
    table_decision_main()
    fig_accuracy_vs_decision()
    table_rank_agreement()
    fig_fold_stability()
    # passthrough tables
    for src, name in [("quantile_metrics.csv", "tab5_quantile"),
                      ("decision_selection.csv", "tab6_selection"),
                      ("decision_sensitivity.csv", "tab7_sensitivity")]:
        save_table(pd.read_csv(M / src).round(4), name)
    print("tables and figures written to outputs/")


if __name__ == "__main__":
    main()
