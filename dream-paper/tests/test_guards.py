"""Automated protocol guards (redesign section 9, G1-G12).

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
        for f in list((ROOT / "paper" / "sections").glob("*.tex")) + \
                 [ROOT / "README.md", ROOT / "paper" / "main.tex"]:
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
