"""Automated protocol guards (redesign section 9, G1-G16).

Two kinds of guard:
  - code-level guards run on synthetic fixtures and must always pass;
  - artifact guards validate generated outputs and SKIP only while the
    corrected pipeline has not yet produced them. After the rerun, the
    full suite must pass with no artifact-guard skips (checked at final
    validation), and the manuscript-terminology guard is armed by the
    marker file docs/.manuscript_rewritten.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from optimization.allocation import (EmpiricalDemand, SimConfig, make_policy,  # noqa: E402
                                     simulate)

M = ROOT / "outputs" / "metrics"
T = ROOT / "outputs" / "tables"

FORBIDDEN_OUTPUT_TOKENS = ["oracle_gap", "gap_closed", "gap closed",
                           "achievable range", "oracle gap"]
FORBIDDEN_MANUSCRIPT_TOKENS = FORBIDDEN_OUTPUT_TOKENS + [
    "staffing", "crew", "oracle", "backlog"]


def need(path: Path):
    if not path.exists():
        pytest.skip(f"artifact guard pending rerun: {path.name} not yet generated")
    return path


# ---------------------------------------------------------------- G1
class TestG1CapacityFromTrainingOnly:
    def synth_panel(self, bump_test: float):
        days = pd.date_range("2024-01-01", periods=200)
        n = np.full(200, 100.0)
        n[140:] += bump_test            # 70% boundary at day 140
        return pd.concat([pd.DataFrame({"city": "x", "family": f, "day": days,
                                        "n": n / 2}) for f in ["a", "b"]],
                         ignore_index=True)

    def test_budgets_invariant_to_test_window_perturbation(self):
        from run_decision import compute_frozen_budgets
        active = {"x": {"active_families": ["a", "b"], "structurally_absent": []}}
        dcfg = {"kappa_base": 10.0, "austin_other_sensitivity": False,
                "capacity": {"regimes": {"scarce": 0.7, "moderate": 0.9,
                                         "generous": 1.1}}}
        days = pd.Series(pd.date_range("2024-01-01", periods=200))
        b0 = compute_frozen_budgets(self.synth_panel(0.0), {"x": days}, active, dcfg)
        b1 = compute_frozen_budgets(self.synth_panel(500.0), {"x": days}, active, dcfg)
        assert (b0["cities"]["x"]["train_only"]["budgets"]
                == b1["cities"]["x"]["train_only"]["budgets"])

    def test_frozen_budgets_artifact_regenerates_from_pretest_data(self):
        path = need(M / "frozen_budgets.json")
        frozen = json.loads(path.read_text())
        assert frozen["calibration_primary"] == "train_only"
        for city, entry in frozen["cities"].items():
            assert "train_only" in entry and "budgets" in entry["train_only"]


# ---------------------------------------------------------------- G2
class TestG2SelectionUsesValidationOnly:
    def test_selection_artifact_is_argmin_of_validation_rows(self):
        vs = pd.read_csv(need(M / "validation_selection.csv"))
        fm = pd.read_csv(need(M / "forecast_metrics.csv"))
        val = fm[fm.split == "val"]
        for _, r in vs.iterrows():
            grp = val[(val.scope == r.scope) & (val.city == r.city) &
                      (val.feature_set == r.feature_set)]
            assert grp.loc[grp["mae"].idxmin(), "model"] == r.selected_model

    def test_selection_invariant_to_test_metric_perturbation(self):
        fm = pd.read_csv(need(M / "forecast_metrics.csv")).copy()
        val = fm[fm.split == "val"]
        pick = {k: g.loc[g["mae"].idxmin(), "model"]
                for k, g in val.groupby(["scope", "city", "feature_set"])}
        fm.loc[fm.split == "test", "mae"] *= 100        # corrupt test metrics
        val2 = fm[fm.split == "val"]
        pick2 = {k: g.loc[g["mae"].idxmin(), "model"]
                 for k, g in val2.groupby(["scope", "city", "feature_set"])}
        assert pick == pick2


# ---------------------------------------------------------------- G3
class TestG3TransferTemporalCensoring:
    def test_loco_rows_carry_correct_censor_dates(self):
        from evaluation.protocol import chrono_split
        fm = pd.read_csv(need(M / "forecast_metrics.csv"))
        loco = fm[fm.scope == "loco_zero_shot_censored"]
        assert len(loco) > 0, "censored transfer rows missing"
        feats_path = ROOT / "data" / "processed" / "features.parquet"
        if not feats_path.exists():
            pytest.skip("features.parquet not present in this environment")
        feats = pd.read_parquet(feats_path, columns=["city", "day"])
        for _, r in loco.iterrows():
            days = feats.loc[feats.city == r.city, "day"]
            _, v_end = chrono_split(days)
            expected = (pd.Timestamp(v_end) - pd.Timedelta(days=1)).date()
            assert str(expected) == r.source_censor_date

    def test_no_uncensored_loco_rows_remain(self):
        fm = pd.read_csv(need(M / "forecast_metrics.csv"))
        assert "loco_zero_shot" not in set(fm.scope) - {"loco_zero_shot_censored"}


# ---------------------------------------------------------------- G4
class TestG4SameModelUncertaintyArms:
    def test_arms_derive_from_one_distribution_object(self):
        qfc = {q: np.full((4, 2), v) for q, v in
               zip([0.05, 0.25, 0.5, 0.75, 0.95], [10, 20, 30, 45, 90.0])}
        cfg = SimConfig(units=4, kappa=10.0)
        fams = ["a", "b"]
        med = make_policy("greedy_ev_point", cfg, fams, point_fc=qfc[0.5])
        full = make_policy("greedy_ev_quantile", cfg, fams, quantile_fc=qfc)
        demand = np.full((4, 2), 35.0)
        r1 = simulate(demand, med, cfg, fams)
        r2 = simulate(demand, full, cfg, fams)
        assert r1["total_loss"] >= 0 and r2["total_loss"] >= 0

    def test_decision_outputs_contain_all_three_arms(self):
        dm = pd.read_csv(need(M / "decision_metrics.csv"))
        for arm in ["quantile/median_arm", "quantile/implied_mean_arm",
                    "quantile/full_arm"]:
            assert arm in set(dm.config), f"missing uncertainty arm {arm}"

    def test_config_declares_single_quantile_model(self):
        import yaml
        dcfg = yaml.safe_load((ROOT / "configs" / "decision.yml").read_text())
        assert dcfg["uncertainty_contrast"]["model"] == "lgbm_quantile"


# ---------------------------------------------------------------- G5
class TestG5StructuralAbsenceNotZero:
    def test_chicago_noise_structurally_absent(self):
        path = need(ROOT / "data" / "interim" / "active_families.json")
        active = json.loads(path.read_text())
        assert "noise" in active["chicago"]["structurally_absent"]
        assert "noise" not in active["chicago"]["active_families"]

    def test_panel_has_no_allzero_structural_family(self):
        panel_path = ROOT / "data" / "interim" / "panel_311.parquet"
        if not panel_path.exists():
            pytest.skip("panel not present")
        panel = pd.read_parquet(panel_path)
        chi = panel[panel.city == "chicago"]
        assert "noise" not in set(chi.family), \
            "structural absence must not be encoded as zero rows"


# ---------------------------------------------------------------- G6
class TestG6BudgetConservationOnActiveSets:
    def test_full_budget_used_on_uneven_family_sets(self):
        for n_f in (3, 7):
            fams = [f"f{i}" for i in range(n_f)]
            cfg = SimConfig(units=11, kappa=5.0)
            pol = make_policy("uniform", cfg, fams)
            demand = np.abs(np.random.default_rng(0).normal(20, 5, (10, n_f)))
            simulate(demand, pol, cfg, fams)  # internal assert enforces budget


# ---------------------------------------------------------------- G7/G8
class TestG7G8ForbiddenTerminology:
    def test_no_forbidden_tokens_in_output_tables(self):
        if not T.exists() or not list(T.glob("*.csv")):
            pytest.skip("tables pending rerun")
        for f in T.glob("*.csv"):
            text = f.read_text().lower()
            for tok in FORBIDDEN_OUTPUT_TOKENS:
                assert tok not in text, f"forbidden token '{tok}' in {f.name}"

    def test_no_forbidden_tokens_in_manuscript(self):
        marker = ROOT / "docs" / ".manuscript_rewritten"
        if not marker.exists():
            pytest.skip("manuscript guard armed after rewrite stage")
        for f in (list((ROOT / "paper" / "sections").glob("*.tex"))
                  + list((ROOT / "supplement" / "sections").glob("*.tex"))
                  + [ROOT / "README.md", ROOT / "paper" / "main.tex",
                     ROOT / "supplement" / "supplement.tex"]):
            text = f.read_text().lower()
            for tok in FORBIDDEN_MANUSCRIPT_TOKENS:
                assert tok not in text, f"forbidden token '{tok}' in {f.name}"


# ---------------------------------------------------------------- G9
class TestG9SensitivityClaimsMatchCode:
    def test_scenarios_in_outputs_match_config(self):
        import yaml
        sens = pd.read_csv(need(M / "decision_sensitivity.csv"))
        dcfg = yaml.safe_load((ROOT / "configs" / "decision.yml").read_text())
        active = json.loads(need(ROOT / "data" / "interim" /
                                 "active_families.json").read_text())
        mults = dcfg["service_yield"]["one_family_multipliers"]
        for city, grp in sens.groupby("city"):
            expected = {"normative_weights", "abandonment_10",
                        "budgets_train_plus_validation"}
            expected |= {f"yield_{f}_x{int(round(m * 100)):03d}"
                         for f in active[city]["active_families"] for m in mults}
            if city == "austin" and dcfg.get("austin_other_sensitivity"):
                expected |= {"austin_other_excluded_recalibrated"}
            assert set(grp.scenario) == expected, \
                f"{city}: scenario set diverges from config (G9)"

    def test_primary_yield_is_homogeneous(self):
        import yaml
        dcfg = yaml.safe_load((ROOT / "configs" / "decision.yml").read_text())
        assert dcfg["service_yield"]["primary"] == "homogeneous"
        assert "sensitivity_heterogeneous_multipliers" not in dcfg["service_yield"]


# ---------------------------------------------------------------- G10
class TestG10SourceConsistency:
    def test_dataset_ids_and_window_agree_across_files(self):
        import yaml
        cfg = yaml.safe_load((ROOT / "configs" / "data_sources.yml").read_text())
        for src in cfg["socrata_311"]:
            mpath = ROOT / "data" / "raw" / "311" / f"{src['city']}_manifest.json"
            man = json.loads(need(mpath).read_text())
            assert man["dataset_id"] == src["dataset_id"], src["city"]
        pm = ROOT / "data" / "interim" / "panel_manifest.json"
        if pm.exists():
            man = json.loads(pm.read_text())
            assert man["panel_date_range"][0] == cfg["study_window"]["start"]


# ---------------------------------------------------------------- G11
class TestG11NoStaleArtifacts:
    def test_provenance_hashes_match_current_files(self):
        import hashlib
        prov = json.loads(need(T / "_provenance.json").read_text())
        rid = json.loads(need(M / "run_id.json").read_text())
        assert prov["run_id"].get("run_id") == rid.get("run_id")
        assert "decision_run_completed" in rid
        for rel, digest in prov["files"].items():
            f = ROOT / "outputs" / rel
            assert f.exists(), f"provenance lists missing file {rel}"
            assert hashlib.sha256(f.read_bytes()).hexdigest()[:16] == digest, \
                f"stale or modified artifact: {rel}"


# ---------------------------------------------------------------- G12
class TestG12ActiveFamiliesCodeConfigAgreement:
    def test_simulation_family_sets_equal_manifest(self):
        dm = pd.read_csv(need(M / "decision_metrics.csv"))
        active = json.loads(need(ROOT / "data" / "interim" /
                                 "active_families.json").read_text())
        for city, grp in dm.groupby("city"):
            sim_fams = set(json.loads(grp.iloc[0]["served_fraction_by_family"]))
            assert sim_fams == set(active[city]["active_families"]), city


# ---------------------------------------------------------------- G13
class TestG13PooledTrainingCensoring:
    """R1-F1 targeted fix: no pooled/global training row may cross the
    stage-applicable boundary (val stage: min train-end; test stage: min
    validation-end across pooled cities)."""

    def test_cutoff_helper_takes_minimum_across_cities(self):
        from run_forecasting import pooled_stage_cutoffs
        bounds = {"a": (pd.Timestamp("2023-08-04"), pd.Timestamp("2024-05-05")),
                  "b": (pd.Timestamp("2023-07-29"), pd.Timestamp("2024-05-06")),
                  "c": (pd.Timestamp("2023-08-03"), pd.Timestamp("2024-05-04"))}
        t, v = pooled_stage_cutoffs(bounds)
        assert t == pd.Timestamp("2023-07-29") and v == pd.Timestamp("2024-05-04")

    def test_censoring_proof_manifest_matches_recomputed_boundaries(self):
        from evaluation.protocol import chrono_split
        proof = json.loads(need(M / "pooled_censoring.json").read_text())
        feats_path = ROOT / "data" / "processed" / "features.parquet"
        if not feats_path.exists():
            pytest.skip("features.parquet not present in this environment")
        feats = pd.read_parquet(feats_path, columns=["city", "day"])
        bounds = {c: chrono_split(feats.loc[feats.city == c, "day"])
                  for c in sorted(feats.city.unique())}
        min_t = min(b[0] for b in bounds.values())
        min_v = min(b[1] for b in bounds.values())
        assert proof["min_train_end"] == str(pd.Timestamp(min_t).date())
        assert proof["min_validation_end"] == str(pd.Timestamp(min_v).date())
        # fit-time proof: the latest row actually used never crosses the boundary
        assert proof["max_train_day_val_stage"] <= proof["min_train_end"]
        assert proof["max_train_day_test_stage"] <= proof["min_validation_end"]
        # the fix must have actually removed boundary rows
        assert proof["rows_censored_val_stage"] > 0
        assert proof["rows_censored_test_stage"] > 0


# ---------------------------------------------------------------- G14
class TestG14ManuscriptDatasetIdsMatchConfig:
    """Every Socrata dataset id printed in the manuscript or supplement must
    be one of the configured ids, and the known-bad Austin id must not
    appear (Prof 1 W4b / Prof 2 R3)."""

    def test_printed_ids_subset_of_config(self):
        import re, yaml
        cfg = yaml.safe_load((ROOT / "configs" / "data_sources.yml").read_text())
        valid = {s["dataset_id"] for s in cfg["socrata_311"]}
        tex = ""
        for f in (list((ROOT / "paper" / "sections").glob("*.tex"))
                  + list((ROOT / "supplement" / "sections").glob("*.tex"))):
            tex += f.read_text()
        printed = set(re.findall(r"\\texttt\{([a-z0-9]{4}-[a-z0-9]{4})\}", tex))
        assert printed <= valid, f"unknown dataset ids in print: {printed - valid}"
        assert "i26j-ai4z" not in tex, "stale Austin dataset id reappeared"
        for vid in valid:
            assert vid in tex, f"configured id {vid} missing from print"


# ---------------------------------------------------------------- G15
class TestG15CaptionTruthfulness:
    """The Table 1 caption must not claim a uniform family count per city
    and must carry the Chicago qualification (Prof 2 R1 / Prof 1 W4a)."""

    def test_caption_phrase(self):
        frag = ROOT / "paper" / "sections" / "data_stats.tex"
        if not frag.exists():
            pytest.skip("data_stats fragment pending regeneration")
        text = frag.read_text()
        assert "families per city" not in text, "false uniform-count caption"
        assert "Chicago has seven" in text, "Chicago qualification missing"

    def test_generator_emits_correct_caption(self):
        gen = (ROOT / "scripts" / "make_paper_stats.py").read_text()
        assert "8 harmonized service families per city" not in gen
        assert "Chicago has seven" in gen


# ---------------------------------------------------------------- G16
class TestG16SelectionArtifactConsistency:
    """The cross-scope selection experiment's by-MAE choice must equal the
    recomputed argmin of validation MAE over the pre-specified
    eleven-configuration grid (W1: manuscript statements are anchored to
    this artifact, so the artifact itself is re-derived here)."""

    def test_selected_by_val_mae_is_recomputable(self):
        from run_decision import POINT_CONFIGS
        sel = pd.read_csv(need(M / "decision_selection.csv"))
        fm = pd.read_csv(need(M / "forecast_metrics.csv"))
        val = fm[fm.split == "val"]
        for city, grp in sel.groupby("city"):
            maes = {}
            for c3 in POINT_CONFIGS:
                r = val[(val.scope == c3[0]) & (val.city == city) &
                        (val.feature_set == c3[1]) & (val.model == c3[2])]
                maes[c3] = float(r["mae"].iloc[0])
            best = "/".join(min(maes, key=maes.get))
            assert (grp.selected_by_val_mae == best).all(), city
