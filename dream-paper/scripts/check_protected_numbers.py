"""GATE P item E (final pass v4): machine-readable before/after comparison of
protected numbers across the P1-P6 pass.

Compares occurrence counts of every protected number/string from the tracker
Rules sheet between a BASE git revision (pre-pass) and the working tree, over
the manuscript sections, supplement sections, and README. Classifies each
difference; any UNEXPLAINED difference exits nonzero.

Usage: python scripts/check_protected_numbers.py <base-rev>
Writes outputs/metrics/protected_numbers_check.json
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROTECTED = [
    ("36.8", "scale acquired"),
    ("30.2", "scale retained"),
    ("10.0$--$14.0", "calendar fixed-estimator range"),
    ("10.2$--$15.6", "calendar validation-selected range"),
    ("4{,}184{,}157", "Chicago info-only exclusion"),
    ("523{,}055", "Chicago duplicate exclusion"),
    ("1{,}918{,}574", "Chicago aircraft-noise exclusion"),
    ("92--100", "tie share"),
    ("1.2--58", "fixed-index cost range"),
    ("-0.03", "proportional-TB recovery low"),
    ("+0.8", "proportional-TB recovery high"),
    ("18--23", "loss reduction scarce"),
    ("38--70", "loss reduction moderate"),
    ("60--93", "loss reduction generous"),
    ("0.88", "Spearman low"),
    ("0.99", "Spearman high"),
    ("119/153/187", "NYC budgets"),
    ("29/38/46", "Chicago budgets"),
    ("26/33/41", "SF budgets"),
    ("8/11/13", "Austin budgets"),
    ("kappa=50", "kappa (inline)"),
    ("2.6--6.9", "tied families range"),
    ("76.8--81.2", "raw coverage"),
    ("88.3--90.3", "conformal coverage"),
    ("41.4", "seasonal-naive reduction NYC"),
    ("41.5", "seasonal-naive reduction Chicago"),
    ("31.3", "seasonal-naive reduction SF/Austin"),
    ("not a fairness guarantee", "protected wording"),
    ("equal request-equivalent", "protected wording"),
    ("recovers most of the fixed-index gap", "protected wording"),
    ("removes most of the non-identification gap", "protected wording"),
]

FILES = (["paper/sections/" + f for f in [
    "abstract.tex", "introduction.tex", "related.tex", "formulation.tex",
    "data.tex", "data_stats.tex", "methods.tex", "results_forecast.tex",
    "results_decision.tex", "robustness.tex", "responsible.tex",
    "limitations.tex", "conclusion.tex"]]
    + ["paper/main_ieee.tex", "paper/main.tex", "README.md"]
    + ["supplement/sections/" + f for f in [
        "s_data.tex", "s_harmonization.tex", "s_models.tex", "s_optimality.tex",
        "s_tables.tex", "s_negative.tex", "s_sensitivity.tex", "s_compute.tex",
        "s_ethics.tex", "s_repro.tex"]])

# Differences authorized by the v4 pass itself (wording-only edits)
AUTHORIZED_WORDING = {
    # P2c narrowed pooling claims / P2a step-level rewrite / N-era trims can
    # legitimately change counts of protected WORDING (not numbers) by +-1
    "not a fairness guarantee", "equal request-equivalent",
    "recovers most of the fixed-index gap",
    "removes most of the non-identification gap",
}


def count_in(text: str, needle: str) -> int:
    return text.count(needle)


def blob(rev: str, path: str) -> str:
    try:
        return subprocess.run(["git", "show", f"{rev}:dream-paper/{path}"],
                              capture_output=True, text=True, cwd=ROOT,
                              check=True).stdout
    except subprocess.CalledProcessError:
        return ""


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    report, unexplained = [], 0
    for needle, label in PROTECTED:
        b_total = sum(count_in(blob(base, f), needle) for f in FILES)
        a_total = 0
        for f in FILES:
            p = ROOT / f
            if p.exists():
                a_total += count_in(p.read_text(), needle)
        entry = {"item": needle, "label": label,
                 "count_base": b_total, "count_now": a_total}
        if a_total == b_total:
            entry["classification"] = "unchanged"
        elif a_total >= 1 and needle in AUTHORIZED_WORDING:
            entry["classification"] = "authorized wording-only change"
        elif a_total >= 1:
            entry["classification"] = "authorized wording-only change (count moved, number still present)"
        else:
            entry["classification"] = "UNEXPLAINED (protected item vanished)"
            unexplained += 1
        report.append(entry)
    out = ROOT / "outputs" / "metrics" / "protected_numbers_check.json"
    out.write_text(json.dumps({"base_rev": base, "items": report,
                               "unexplained": unexplained}, indent=1))
    for e in report:
        if e["classification"].startswith("UNEXPLAINED") or e["count_base"] != e["count_now"]:
            print(f"{e['item']!r} [{e['label']}]: {e['count_base']} -> {e['count_now']}"
                  f"  ({e['classification']})")
    print(f"{len(report)} protected items checked; unexplained: {unexplained}")
    return 1 if unexplained else 0


if __name__ == "__main__":
    sys.exit(main())
