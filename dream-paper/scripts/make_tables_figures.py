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
    fig, axes = plt.subplots(len(cities), 1, figsize=(7.0, 1.33 * len(cities)),
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
    ax.set_ylabel("% test-MAE reduction vs trailing\n7-day-mean baseline\n(validation-selected model)")
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
    fig, axes = plt.subplots(1, len(cities), figsize=(2.4 * len(cities), 2.2),
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


def table_tiebreak() -> None:
    """Tie-break / objective non-identification evidence (review B). Main-text
    compact view + full supplement grid. pct_vs_proportional: positive = better
    than proportional, negative = worse."""
    d = pd.read_csv(M / "tiebreak_sensitivity.csv")
    tf = pd.read_csv(M / "tie_frequency.csv")[["city", "regime", "tie_share_steps",
                                               "mean_tied_families"]]
    piv = d.pivot_table(index=["city", "regime"], columns="policy",
                        values="pct_vs_proportional")
    main = piv.reset_index()[["city", "regime"]].copy()
    main = main.merge(tf, on=["city", "regime"])
    main["tie_pct"] = (main["tie_share_steps"] * 100).round(1)
    colmap = {"point_greedy/fixed_index": "fixed_tb",
              "point_greedy/random_max": "random_worst",
              "point_greedy/random_min": "random_best",
              "point_greedy/proportional_unmet": "proportional_tb",
              "quantile_full": "full_distribution"}
    for src, dst in colmap.items():
        main[dst] = piv[src].round(2).values
    main = main[["city", "regime", "tie_pct", "fixed_tb", "random_worst",
                 "random_best", "proportional_tb", "full_distribution"]]
    main["city"] = main["city"].map({"austin": "Austin", "chicago": "Chicago",
                                     "nyc": "NYC", "sf": "SF"})
    main.columns = ["City", "Regime", "Tie %", "Fixed", "Rand. worst",
                    "Rand. best", "Prop. TB", "Full dist."]
    save_table(main, "tab11_tiebreak_main", float_fmt="%.2f")
    save_table(d.round(2), "tab12_tiebreak_full")


def table_kappa_sweep() -> None:
    """P4 (final pass v4): global kappa-granularity sweep magnitudes.

    Emitted only when the sweep artifact exists; the sweep itself runs via
    `make kappa` (scripts/run_kappa_sweep.py) and is not part of `make all`."""
    path = M / "kappa_sweep_summary.csv"
    if not path.exists():
        return
    ks = pd.read_csv(path)
    save_table(ks, "tab23_kappa_summary", float_fmt="%.3f")   # machine-readable (all columns)
    full = pd.read_csv(M / "kappa_sweep.csv")
    save_table(full.round(3), "tab24_kappa_full", float_fmt="%.3f")
    # compact rendered view: fixed-index gap (% vs proportional) by kappa
    comp = ks.pivot_table(index=["city", "regime"], columns="kappa",
                          values="fixed_index_gap_pct").reset_index()
    comp.columns = ["City", "Regime"] + [f"kappa={int(k)}" for k in sorted(ks["kappa"].unique())]
    save_table(comp.round(1), "tab23c_kappa_fixedindex", float_fmt="%.1f")
    tie = ks.pivot_table(index=["city", "regime"], columns="kappa",
                         values="tie_share_steps").reset_index()
    tie.columns = ["City", "Regime"] + [f"kappa={int(k)}" for k in sorted(ks["kappa"].unique())]
    save_table((tie.assign(**{c: (tie[c]*100) for c in tie.columns[2:]})).round(1),
               "tab23d_kappa_tieshare", float_fmt="%.1f")


def table_conformal() -> None:
    """Conformal recalibration: coverage/width before-after, and the calibrated
    vs uncalibrated full-arm decision (review G)."""
    cal = pd.read_csv(M / "conformal_calibration.csv")
    save_table(cal, "tab13_conformal_calibration")
    dec = pd.read_csv(M / "conformal_decision.csv")
    save_table(dec, "tab13b_conformal_decision")


def table_logpool() -> None:
    """Normalized/log-scale pooling vs local (review F #75-#79)."""
    lp = pd.read_csv(M / "logpool_sensitivity.csv")
    wide = lp.pivot_table(index="city", columns="normalization",
                          values="pct_vs_local").reset_index()
    wide = wide.rename(columns={c: f"pooled_{c}_pct_vs_local"
                                for c in ["raw", "log1p", "per_city_z"]})
    save_table(wide.round(2), "tab14_logpool")


def table_horizon() -> None:
    """Policy ranking by evaluation horizon (review D #49, #190)."""
    h = pd.read_csv(M / "horizon_sensitivity.csv")
    save_table(h[["city", "regime", "horizon", "best_policy", "worst_policy",
                  "ranking"]], "tab15_horizon")


def table_perfamily_unserved() -> None:
    """Per-family served fraction by policy so systematic deprioritization is
    visible rather than hidden in aggregate loss (review L #22/#140/#191).
    Moderate regime; forecast-free uniform vs the full-distribution arm."""
    dm = pd.read_csv(M / "decision_metrics.csv")
    rows = []
    for city, grp in dm.groupby("city"):
        for policy, config in [("uniform", "uniform"),
                               ("greedy_ev_quantile", "quantile/full_arm")]:
            r = grp[(grp.regime == "moderate") & (grp.policy == policy) &
                    (grp.config == config)]
            if r.empty:
                continue
            sf = json.loads(r.iloc[0]["served_fraction_by_family"])
            for fam, frac in sf.items():
                rows.append({"city": city, "policy": config, "family": fam,
                             "served_fraction": round(float(frac), 4)})
    wide = pd.DataFrame(rows).pivot_table(
        index=["city", "family"], columns="policy", values="served_fraction").reset_index()
    save_table(wide, "tab16_perfamily_served")


def table_dataset_audit() -> None:
    """Acquired / excluded / retained records and native-category counts per
    city, from the build manifests (review H #93/#179)."""
    pm = json.loads((DATA_INTERIM / "panel_manifest.json").read_text())
    raw = ROOT_RAW = OUTPUTS.parent / "data" / "raw" / "311"
    rows = []
    for c, lbl in [("nyc", "New York"), ("chicago", "Chicago"),
                   ("sf", "San Francisco"), ("austin", "Austin")]:
        man = json.loads((raw / f"{c}_manifest.json").read_text())
        acquired = pm[f"{c}_raw_request_total"]
        kept = pm[f"{c}_kept_request_total"]
        rows.append({"City": lbl, "Dataset id": man["dataset_id"],
                     "Retrieved": man["retrieved_at_utc"][:10],
                     "Native cats": pm[f"{c}_native_categories"],
                     "Acquired": acquired, "Excluded": acquired - kept,
                     "Retained": kept})
    tot = {"City": "Total", "Dataset id": "", "Retrieved": "",
           "Native cats": sum(r["Native cats"] for r in rows),
           "Acquired": sum(r["Acquired"] for r in rows),
           "Excluded": sum(r["Excluded"] for r in rows),
           "Retained": sum(r["Retained"] for r in rows)}
    save_table(pd.DataFrame(rows + [tot]), "tab17_dataset_audit", float_fmt="%.0f")


def table_split_dates() -> None:
    """Exact per-city chronological train/validation/test boundaries (review J
    #116/#180)."""
    from evaluation.protocol import chrono_split
    feats = pd.read_parquet(OUTPUTS.parent / "data" / "processed" / "features.parquet",
                            columns=["city", "day"])
    rows = []
    labels = {"nyc": "New York", "chicago": "Chicago", "sf": "San Francisco",
              "austin": "Austin"}
    for c in cities_present():
        days = feats.loc[feats.city == c, "day"]
        t_end, v_end = chrono_split(days)
        d = pd.to_datetime(days)
        rows.append({"City": labels[c],
                     "Train": f"{d.min().date()} .. {pd.Timestamp(t_end).date()}",
                     "Validation": f"{(pd.Timestamp(t_end)+pd.Timedelta(days=1)).date()} .. {pd.Timestamp(v_end).date()}",
                     "Test": f"{(pd.Timestamp(v_end)+pd.Timedelta(days=1)).date()} .. {d.max().date()}"})
    save_table(pd.DataFrame(rows), "tab18_split_dates")


def table_guards() -> None:
    """The protocol guard suite: what each guard checks and against which
    artifact (review M #152/#192)."""
    g = [("G1", "Budgets from training window only; invariant to test perturbation", "frozen_budgets.json"),
         ("G2", "Model selection uses validation MAE only; invariant to corrupted test metrics", "validation_selection.csv"),
         ("G3", "Leave-one-city-out transfer rows carry recomputed censor dates", "forecast_metrics.csv"),
         ("G4", "All three uncertainty arms derive from one fitted quantile model", "decision_metrics.csv"),
         ("G5", "Structural absence (Chicago noise) never encoded as zero rows", "active_families.json"),
         ("G6", "Allocation conserves the full budget on uneven family sets", "allocation.py"),
         ("G7/G8", "No forbidden terminology in output tables or manuscript", "tables / *.tex"),
         ("G9", "Every sensitivity scenario in outputs matches the config grid", "decision_sensitivity.csv"),
         ("G10", "Dataset ids and study window agree across config and manifests", "data_sources.yml / manifests"),
         ("G11", "Provenance SHA-256 hashes bind every table/figure to the run", "_provenance.json"),
         ("G12", "Simulated family sets equal the active-family manifest", "decision_metrics.csv"),
         ("G13", "Pooled training is stage-censored (fit-time proof manifest)", "pooled_censoring.json"),
         ("G14", "Printed dataset ids are a subset of the configured ids", "*.tex"),
         ("G15", "Table-1 caption carries the Chicago seven-family qualification", "data_stats.tex"),
         ("G16", "Cross-scope by-MAE selection equals the recomputed argmin", "decision_selection.csv")]
    save_table(pd.DataFrame(g, columns=["Guard", "Checks", "Artifact"]), "tab19_guards")


def table_backlog() -> None:
    """Initial-backlog (b0) sensitivity: mean policy rank (1=best) under each
    initial-carryover condition, showing the ordering is stable (review D
    #30/#50)."""
    b = pd.read_csv(M / "b0_sensitivity.csv")
    piv = b.pivot_table(index="policy", columns="b0_condition", values="rank",
                        aggfunc="mean").round(2).reset_index()
    cols = ["policy"] + [c for c in ["zero", "warmup", "train_avg"] if c in piv.columns]
    save_table(piv[cols], "tab22_b0")


def table_poisson() -> None:
    """Poisson GLM count baseline vs the validation-selected model and naive
    (review F #65/#66)."""
    p = pd.read_csv(M / "poisson_baseline.csv")
    keep = p[["city", "feature_set", "naive_mae", "poisson_glm_mae",
              "selected_model", "selected_mae"]]
    save_table(keep, "tab21_poisson")


def table_weather_missing() -> None:
    """Weather missingness after quality-flag drop and gap fill, per city
    (review E #59)."""
    pm = json.loads((DATA_INTERIM / "panel_manifest.json").read_text())
    labels = {"nyc": "New York", "chicago": "Chicago", "sf": "San Francisco",
              "austin": "Austin"}
    rows = []
    for c, lbl in labels.items():
        mm = pm[f"{c}_weather_missing_after_fill"]
        rows.append({"City": lbl, "TMAX missing": mm.get("TMAX", 0),
                     "TMIN missing": mm.get("TMIN", 0), "PRCP missing": mm.get("PRCP", 0)})
    save_table(pd.DataFrame(rows), "tab20_weather_missing", float_fmt="%.0f")


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

    # review-revision validity tables (tie-break, conformal, pooling, horizon,
    # per-family); each guarded by presence of its sensitivity metrics file
    for fn in (table_tiebreak, table_kappa_sweep, table_conformal, table_logpool, table_horizon,
               table_perfamily_unserved, table_dataset_audit, table_split_dates,
               table_guards, table_weather_missing, table_poisson, table_backlog):
        try:
            fn()
        except FileNotFoundError:
            pass

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
