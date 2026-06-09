"""Generate LaTeX fragments whose numbers come straight from the data layers.

Writes:
  paper/sections/data_stats.tex            dataset summary table (Table 1)
  supplement/sections/s_harmonization_tables.tex
                                           top native categories per family/city

Run after build_panel.py. Keeping these numbers script-generated means the
manuscript cannot drift from the data (every number traceable).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from common.runtime import DATA_INTERIM, OUTPUTS  # noqa: E402

CITY_LABELS = {"nyc": "New York", "chicago": "Chicago", "sf": "San Francisco",
               "austin": "Austin"}


def latex_escape(s: str) -> str:
    for a, b in [("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_"),
                 ("$", r"\$")]:
        s = s.replace(a, b)
    return s


def data_stats() -> str:
    manifest = json.loads((DATA_INTERIM / "panel_manifest.json").read_text())
    panel = pd.read_parquet(DATA_INTERIM / "panel_311.parquet")
    rows = []
    for city in sorted(panel["city"].unique()):
        sub = panel[panel.city == city]
        rows.append({
            "City": CITY_LABELS[city],
            "Requests kept": f"{manifest[f'{city}_kept_request_total']:,}",
            "Native cat.": manifest[f"{city}_native_categories"],
            "Panel rows": f"{len(sub):,}",
            "Days": sub["day"].nunique(),
            "Mean/day": f"{sub.groupby('day')['n'].sum().mean():,.0f}",
        })
    df = pd.DataFrame(rows)
    body = " \\\\\n".join(" & ".join(str(v) for v in r) for r in df.values)
    return (
        "\\begin{table}[t]\\centering\n"
        "\\caption{Dataset summary after preprocessing (study window "
        f"{manifest['panel_date_range'][0]} to {manifest['panel_date_range'][1]}; "
        "8 harmonized service families per city; no synthetic data).}\n"
        "\\label{tab:data}\n"
        "\\small\\begin{tabular}{lrrrrr}\n\\toprule\n"
        + " & ".join(df.columns) + " \\\\\n\\midrule\n"
        + body + " \\\\\n\\bottomrule\n\\end{tabular}\n\\end{table}\n"
    )


def harmonization_tables() -> str:
    out = []
    for path in sorted((OUTPUTS / "tables").glob("family_composition_*.csv")):
        city = path.stem.replace("family_composition_", "")
        comp = pd.read_csv(path)
        total = comp["n"].sum()
        out.append(f"\\subsection*{{{CITY_LABELS.get(city, city)}}}\n")
        out.append("\\begin{itemize}\n")
        for fam, grp in comp.groupby("family"):
            share = grp["n"].sum() / total * 100
            top = grp.nlargest(3, "n")
            cats = "; ".join(f"{latex_escape(str(c))} ({n:,})"
                             for c, n in zip(top["category"], top["n"]))
            out.append(f"\\item \\textbf{{{fam.replace('_', ' ')}}} "
                       f"({share:.1f}\\%): {cats}\n")
        out.append("\\end{itemize}\n")
    return "".join(out)


if __name__ == "__main__":
    (ROOT / "paper/sections/data_stats.tex").write_text(data_stats())
    (ROOT / "supplement/sections/s_harmonization_tables.tex").write_text(
        harmonization_tables())
    print("wrote data_stats.tex and s_harmonization_tables.tex")
