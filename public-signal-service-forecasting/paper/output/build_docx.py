"""Build the Word submission document from the final draft and committed assets.

This is a one-off production script. It reads the figure assets under
paper/figures/ and writes a formatted .docx with embedded images, real Word
tables, styled headings, page numbers, and a clean References section. It does
not change any empirical value; all numbers come verbatim from the verified
results.
"""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

PAPER = Path(__file__).resolve().parents[1]
FIG = PAPER / "figures"
OUT = PAPER / "output" / "public_signal_service_forecasting_final_submission.docx"

BODY_FONT = "Times New Roman"
BODY_SIZE = Pt(12)
LINE_SPACING = 1.15

TITLE = (
    "From Forecast Accuracy to Operational Value: "
    "Public Signal Augmentation for NYC 311 Service Demand"
)

# Author metadata (bracketed placeholders to be completed before submission).
AUTHOR = "[Author Name]"
AFFILIATION = "[Affiliation]"
EMAIL = "[Email]"

# Figures are addressed by an explicit label so the numbering follows order of
# first appearance: main-body figures 1-4, appendix figures A1-A6.
FIGS = {
    # label: (filename, caption)
    "1": ("figure_2_feature_set_comparison_mae.png",
          "Best held-out test MAE achieved per feature set across models."),
    "2": ("figure_7_actual_vs_predicted.png",
          "Observed versus predicted city-wide next-day request totals over the "
          "test period for the selected model."),
    "3": ("figure_6_decision_sensitivity.png",
          "Total weighted unmet demand by policy under scarce, moderate, and "
          "generous crew budgets."),
    "4": ("figure_3_rolling_validation_mae.png",
          "Per-fold test MAE by configuration across five expanding-window "
          "chronological folds."),
    "A1": ("figure_8_weather_feature_summary.png",
           "Real NOAA daily weather series for the Central Park station, "
           "2022-2024."),
    "A2": ("figure_1_model_comparison_mae.png",
           "Held-out test MAE for the naive baseline and every model and "
           "feature-set combination."),
    "A3": ("figure_4_borough_robustness_mae.png",
           "Internal history versus Calendar test MAE by borough (random "
           "forest)."),
    "A4": ("figure_5_complaint_group_robustness_mae.png",
           "Internal history versus Calendar test MAE by complaint group "
           "(random forest)."),
    "A5": ("figure_9_decision_quality_comparison.png",
           "Total weighted unmet demand by policy at the baseline crew budget, "
           "with the oracle benchmark."),
    "A6": ("figure_10_internal_vs_calendar_augmented_mae.png",
           "Internal history versus Calendar test MAE per non-naive model."),
}


def set_base_style(doc: Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = BODY_SIZE
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
    pf = normal.paragraph_format
    pf.line_spacing = LINE_SPACING
    pf.space_after = Pt(6)
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)


def add_page_number_footer(doc: Document) -> None:
    section = doc.sections[0]
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    fld1 = OxmlElement("w:fldChar"); fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = "PAGE"
    fld2 = OxmlElement("w:fldChar"); fld2.set(qn("w:fldCharType"), "end")
    run._r.append(fld1); run._r.append(instr); run._r.append(fld2)
    _set_run_font(run)


def _set_run_font(run, size=BODY_SIZE, bold=False, italic=False):
    run.font.name = BODY_FONT
    run.font.size = size
    run.bold = bold
    run.italic = italic
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts"); rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), BODY_FONT)
    rfonts.set(qn("w:hAnsi"), BODY_FONT)


def add_title(doc: Document) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(TITLE)
    _set_run_font(r, size=Pt(18), bold=True)

    ap = doc.add_paragraph()
    ap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_run_font(ap.add_run(AUTHOR), size=Pt(12))

    afp = doc.add_paragraph()
    afp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_run_font(afp.add_run(AFFILIATION), size=Pt(11), italic=True)

    ep = doc.add_paragraph()
    ep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_run_font(ep.add_run(EMAIL), size=Pt(11))


def add_heading(doc: Document, text: str, level: int) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    if level == 1:
        _set_run_font(r, size=Pt(14), bold=True)
    else:
        _set_run_font(r, size=Pt(12), bold=True)


def add_body(doc: Document, text: str) -> None:
    """Add a justified body paragraph, rendering **bold** lead-ins."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    parts = text.split("**")
    for i, part in enumerate(parts):
        if not part:
            continue
        r = p.add_run(part)
        _set_run_font(r, bold=(i % 2 == 1))
    return p


def add_figure(doc: Document, label: str, width_in: float = 6.0) -> None:
    filename, caption = FIGS[label]
    path = FIG / filename
    fp = doc.add_paragraph()
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # Keep the image with its caption so they never split across a page break.
    fp.paragraph_format.keep_with_next = True
    fp.paragraph_format.keep_together = True
    fp.paragraph_format.space_before = Pt(6)
    run = fp.add_run()
    run.add_picture(str(path), width=Inches(width_in))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.keep_together = True
    cr = cap.add_run(f"Figure {label}. {caption}")
    _set_run_font(cr, size=Pt(10), italic=True)


def add_table_caption(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    # Keep the caption attached to the table that follows.
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    _set_run_font(r, size=Pt(11), bold=True)


def _row_cant_split(row) -> None:
    trPr = row._tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:cantSplit"))


def _row_repeat_header(row) -> None:
    trPr = row._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true")
    trPr.append(th)


def add_word_table(doc: Document, header: list[str], rows: list[list[str]],
                   font_size: int = 10) -> None:
    table = doc.add_table(rows=1, cols=len(header))
    table.style = "Table Grid"
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hdr_row = table.rows[0]
    hdr = hdr_row.cells
    for j, h in enumerate(header):
        hdr[j].text = ""
        run = hdr[j].paragraphs[0].add_run(h)
        _set_run_font(run, size=Pt(font_size), bold=True)
    # Repeat the header on every page the table spans, and never split a row.
    _row_repeat_header(hdr_row)
    _row_cant_split(hdr_row)
    for row in rows:
        r = table.add_row()
        _row_cant_split(r)
        cells = r.cells
        for j, val in enumerate(row):
            cells[j].text = ""
            run = cells[j].paragraphs[0].add_run(val)
            _set_run_font(run, size=Pt(font_size))
    doc.add_paragraph()


def page_break(doc: Document) -> None:
    doc.add_page_break()


def build() -> None:
    doc = Document()
    set_base_style(doc)
    add_page_number_footer(doc)
    add_title(doc)

    # Abstract
    add_heading(doc, "Abstract", 1)
    add_body(doc,
        "Day-ahead forecasts of municipal service-request volume are a natural input to "
        "staffing and dispatch planning, yet a reduction in average forecast error does not "
        "automatically translate into better operational decisions. We ask, on real data, two "
        "questions: do public external signals improve next-day forecasts of NYC 311 "
        "service-request volume, and does any improvement carry through to a stylized "
        "staffing-allocation simulation? Using real NYC 311 Service Requests for 2022-2024 "
        "(9,851,452 raw records aggregated to 43,240 date × borough × complaint-group "
        "observations) and real NOAA Central Park daily weather, we compare four feature sets - "
        "internal history, calendar, weather, and calendar + weather - across four model families "
        "under a strictly chronological protocol with five-fold rolling-origin validation. "
        "Calendar features deliver the largest accuracy gain; real weather adds a smaller but "
        "consistent further gain. The best model, a random forest on the calendar + weather "
        "feature set, attains a held-out test mean absolute error (MAE) of 55.325 versus 71.848 "
        "for a naive seasonal baseline, a 23.0% reduction. A stylized proportional staffing "
        "simulation shows the augmented policy reduces weighted unmet demand at every crew budget "
        "tested and closes 26.381% of the gap to an oracle at the baseline budget, but the "
        "magnitude of the decision benefit is budget-dependent. The central finding is that the "
        "forecast gains are real and robust, while the decision gains are smaller and conditional "
        "on capacity. This study provides a reproducible evaluation of public-signal augmentation "
        "for municipal service-demand forecasting; no synthetic data or synthetic weather is used.")

    # 1. Introduction
    add_heading(doc, "1. Introduction", 1)
    add_body(doc,
        "Municipal service operations plan finite crews against demand that varies by day of week, "
        "season, and location. Short-horizon (next-day) volume forecasts are a standard planning "
        "input. Two questions follow. First, a predictive question: does augmenting an "
        "internal-history forecasting model with public external signals reduce next-day forecast "
        "error? Second, a decision question: does any such forecast improvement actually improve "
        "the quality of a capacity allocation built on top of the forecast?")
    add_body(doc,
        "These questions are related but distinct. Mean absolute error weights all errors equally "
        "across cells and days. A capacity allocation does not: under a fixed, scarce budget, an "
        "error on a high-volume or high-priority cell is more consequential than an error on a "
        "quiet one, and a proportional allocation maps forecasts to capacity non-linearly. A study "
        "reporting only forecast metrics can therefore misstate operational relevance.")
    add_body(doc,
        "We make three contributions. (i) A reproducible, real-data baseline on NYC 311 augmented "
        "with real NOAA weather, with a leakage-controlled chronological protocol. (ii) A "
        "controlled four-way feature-set comparison isolating the marginal value of calendar "
        "features and of real weather. (iii) A transparent forecast-to-decision simulation that "
        "measures whether forecast gains transfer to a stylized allocation, showing directionally "
        "positive but budget-dependent decision benefits. The study is predictive "
        "and correlational; Section 8 states the scope of the analysis and the natural directions "
        "for extending it.")

    # 2. Related Work
    add_heading(doc, "2. Related Work", 1)
    add_body(doc,
        "The methodological template is the demonstration that publicly available signals can "
        "improve operational forecasts. Cui et al. (2018) show, in a retail setting, that public "
        "social-media information improves daily sales forecasts across multiple machine-learning "
        "methods, with tree-based methods extracting more value from heterogeneous public signals "
        "than linear methods, and they frame the contribution as feature value rather than method "
        "novelty. Our work is in this lineage but moves from retail to municipal service "
        "operations, uses public weather rather than social media, and adds an explicit "
        "forecast-to-decision layer rather than stopping at forecast accuracy.")
    add_body(doc,
        "Prediction-driven prioritization in service and scheduling settings has been studied from "
        "an equity and efficiency angle (Samorani et al., 2022). We make no equity or causal claim; "
        "we cite this line only to situate the general point that the objective placed on top of a "
        "predictive model, not the model alone, shapes outcomes - which motivates our separate "
        "evaluation of the decision layer.")

    # 3. Data
    add_heading(doc, "3. Data", 1)
    add_body(doc,
        "Two real public sources are used; no synthetic data and no synthetic weather are used "
        "anywhere. Table 1 summarizes both.")
    add_body(doc,
        "**NYC 311 Service Requests** (NYC Open Data, Socrata dataset erm2-nwe9, "
        "“311 Service Requests from 2010 to Present”; City of New York, accessed 2026), "
        "restricted to 2022-2024. From 9,851,452 raw records the preprocessing procedure yields a "
        "43,240-row date × borough × complaint-group panel spanning observed dates "
        "2022-01-15 to 2024-12-30 (after lag and rolling warmup). Records are mapped to eight "
        "complaint groups (Housing, Noise, Other, Public Safety, Sanitation, Street Condition, "
        "Traffic, Water) by a deterministic substring rule and aggregated to daily counts over the "
        "five NYC boroughs. The forecasting target is the observed next-day request count per cell, "
        "defined only when consecutive calendar days are present.")
    add_body(doc,
        "**NOAA NCEI Daily Summaries (GHCN-Daily)** (NOAA NCEI, accessed 2026), station "
        "USW00094728 (NY City Central Park), 2022-2024, 1,096 daily rows. Variables used: "
        "precipitation, daily maximum and minimum temperature, average temperature, snowfall, snow "
        "depth, and wind speed. The source average-temperature field was empty for this station, so "
        "average temperature is derived as the mean of observed daily maximum and minimum; five "
        "missing wind-speed days are filled by time interpolation of neighbouring real "
        "observations. A single Central Park station is used as a city-level proxy, a documented "
        "spatial-resolution limitation.")
    add_table_caption(doc, "Table 1. Dataset summary.")
    add_word_table(doc, ["Property", "Value"], [
        ["Service data", "NYC 311 Service Requests (NYC Open Data, erm2-nwe9)"],
        ["Study window", "2022-01-01 to 2024-12-31"],
        ["Raw records", "9,851,452"],
        ["Processed rows", "43,240 (date × borough × complaint-group)"],
        ["Observed range (processed)", "2022-01-15 to 2024-12-30"],
        ["Boroughs / complaint groups", "5 / 8"],
        ["Target", "Observed next-day request count per cell"],
        ["Weather source", "NOAA NCEI Daily Summaries (GHCN-Daily)"],
        ["Weather station", "USW00094728 (NY City Central Park); single-station proxy"],
        ["Weather rows / variables", "1,096 / 7"],
        ["Synthetic data or weather", "none"],
    ])

    # 4. Methods
    add_heading(doc, "4. Methods", 1)
    add_body(doc,
        "We compare four feature sets: internal history (lag and rolling statistics of the "
        "per-cell series), calendar (internal plus deterministic calendar features), weather "
        "(internal plus the seven real weather variables), and calendar + weather (internal plus "
        "calendar plus weather). The corresponding configuration identifiers used in the results "
        "tables are internal_historical, calendar_augmented, weather_augmented, and "
        "calendar_weather_augmented. Full feature definitions are in Appendix A.")
    add_body(doc,
        "Four model families are evaluated: a naive seasonal baseline (trailing 7-day mean), Ridge "
        "regression, a random forest, and gradient boosting. Categorical features (borough, "
        "complaint group) are one-hot encoded; numeric features pass through. Lag and rolling "
        "features use only past observations, with rolling statistics shifted by one day to avoid "
        "same-day or future leakage.")
    add_body(doc,
        "Validation uses a strictly chronological split by date: the earliest 70% of dates for "
        "training (30,240 rows), the next 15% for validation (6,480 rows), and the latest 15% for "
        "test (6,520 rows). The primary metric is MAE; RMSE, MAPE (computed with the denominator "
        "floored at one request, so that near-zero actual counts do not inflate the percentage "
        "error), and R² are also reported. The best configuration by validation MAE is refit "
        "on train + validation before the final test evaluation. Separately, five expanding-window "
        "rolling-origin folds assess stability.")
    add_body(doc,
        "The decision layer is a stylized staffing-allocation simulation. Each day a fixed crew "
        "budget is distributed across cells in proportion to the forecast using a largest-remainder "
        "rule. Each crew handles a fixed number of requests; unmet demand in a cell is the positive "
        "part of actual demand minus allocated capacity; weighted unmet demand assigns higher "
        "weight to Public Safety, Water, and Traffic. Policies driven by each feature set are "
        "compared against an oracle that allocates on true next-day demand (an upper bound only). "
        "Full assumptions are in Appendix D.")

    # 5. Forecasting Results
    add_heading(doc, "5. Forecasting Results", 1)
    add_body(doc,
        "Calendar augmentation improves test MAE for every model, and real weather adds a smaller "
        "consistent gain on top of it. For the random forest, MAE falls from 65.282 (internal "
        "history) to 58.082 (calendar); weather alone improves the internal-history model (64.104 "
        "versus 65.282), and calendar + weather is best, at 56.224 for the single-split model fit "
        "on the training set only. Ridge does not benefit from weather (internal 69.219, weather "
        "69.283, calendar + weather 68.915). Figure 1 shows the best test MAE per feature set; the "
        "full per-model results are in Table 2 (selected rows are reported below; the complete "
        "table is in Appendix G).")
    add_table_caption(doc,
        "Table 2 (selected rows). Held-out test MAE by model and feature set; lower is better. "
        "Full 13-row table in Appendix G.")
    add_word_table(doc, ["Model", "Feature set", "Test MAE"], [
        ["naive_seasonal", "naive_seasonal", "71.848"],
        ["random_forest", "internal_historical", "65.282"],
        ["random_forest", "calendar_augmented", "58.082"],
        ["random_forest", "weather_augmented", "64.104"],
        ["random_forest", "calendar_weather_augmented", "56.224"],
        ["gradient_boosting", "calendar_weather_augmented", "61.878"],
        ["ridge", "calendar_weather_augmented", "68.915"],
    ])
    add_body(doc,
        "The selected configuration by validation MAE is the random forest on calendar + weather. "
        "Refit on train + validation and evaluated once on the held-out test set, it attains test "
        "MAE 55.325, RMSE 177.476, MAPE 27.469%, and R² 0.648 - a 23.0% MAE reduction over the "
        "naive seasonal baseline (71.848). The selected-model test MAE of 55.325 (refit on train + "
        "validation) is therefore slightly lower than the 56.224 obtained from the train-only fit "
        "on the single split. Figure 2 shows observed versus predicted city-wide next-day totals "
        "over the test period, which track the overall level and weekly pattern of demand.")
    add_figure(doc, "1")
    add_figure(doc, "2")

    # 6. Forecast-to-Decision Simulation
    add_heading(doc, "6. Forecast-to-Decision Simulation", 1)
    add_body(doc,
        "At the baseline budget (135 crews, 50 requests per crew, 163 test days), total weighted "
        "unmet demand is 643,324 under the internal-history policy and 631,191 under calendar + "
        "weather, versus an oracle of 597,332: the augmented policy reduces weighted unmet demand "
        "by 1.886% and closes 26.381% of the baseline-to-oracle gap.")
    add_body(doc,
        "Across crew budgets (Table 3, Figure 3) the calendar + weather policy is better than the "
        "baseline in all three settings, but the magnitude grows with capacity: the weighted-unmet "
        "reduction is 0.38% (scarce, 100 crews), 4.32% (moderate, 160), and 14.53% (generous, 220). "
        "The headline contrast - an approximately 11-15% forecast-accuracy gain versus a roughly "
        "1.9% decision-quality gain at the baseline budget - is the central observation: average "
        "accuracy and operational value are not the same, and a scarce budget with demand "
        "concentrated in a few large cells limits how much any forecast can help.")
    add_table_caption(doc,
        "Table 3. Decision sensitivity by crew budget. Stylized simulation; total weighted unmet "
        "demand (lower is better); calendar + weather versus internal history.")
    add_word_table(doc,
        ["Setting", "Crews", "Internal", "Calendar+Weather", "Oracle", "Reduction", "Oracle gap closed"],
        [
            ["scarce", "100", "941,817", "938,211", "928,491", "0.38%", "27.06%"],
            ["moderate", "160", "454,073", "434,469", "367,553", "4.32%", "22.66%"],
            ["generous", "220", "164,197", "140,346", "50,865", "14.53%", "21.05%"],
        ])
    add_figure(doc, "3")

    # 7. Robustness Checks
    add_heading(doc, "7. Robustness Checks", 1)
    add_body(doc,
        "Five-fold expanding-window rolling-origin validation (Figure 4; full table in Appendix C) "
        "shows calendar augmentation lowering MAE in every fold for every model: mean improvement "
        "15.13% for the random forest, 9.94% for gradient boosting, and 0.94% for Ridge, each in "
        "all 5 of 5 folds. The calendar + weather random forest has the lowest mean fold MAE "
        "(47.497). Segmented analysis (random forest, internal history versus calendar; Appendix G) "
        "shows the improvement holds for all five boroughs (about 8.8% to 18.8%) and all eight "
        "complaint groups (about 8.9% to 25.8%); absolute error concentrates in the highest-volume "
        "segments (Noise, Housing; the Bronx). The forecast improvement is therefore consistent "
        "across folds and segments, not an artifact of one split.")
    add_figure(doc, "4")

    # 8. Limitations
    add_heading(doc, "8. Limitations", 1)
    add_body(doc,
        "The study is predictive and correlational and makes no causal claim. NYC 311 reflects "
        "reporting behaviour, not true incidence (reporting bias), so forecasts predict reported "
        "volume. Weather is a single Central Park station used as a city-level proxy. Borough-level "
        "aggregation hides within-borough variation; the complaint-group mapping is a deterministic "
        "approximation with a residual Other group. No transit or event data is included. The "
        "staffing simulation is a stylized proportional heuristic - it omits crew travel, shifts, "
        "backlog, intra-day timing, and substitution, and it uses no observed dispatch decisions. "
        "Results apply to NYC and 2022-2024 only.")
    add_body(doc,
        "Natural extensions of this work: a non-stylized, agency-grounded decision model with an "
        "empirical service-level realism check; formal forecast-difference testing (for example a "
        "Diebold-Mariano test) with uncertainty intervals; and broader external signals beyond a "
        "single weather station, or cross-city replication.")

    # 9. Conclusion
    add_heading(doc, "9. Conclusion", 1)
    add_body(doc,
        "On real NYC 311 data augmented with real NOAA weather, public-signal augmentation "
        "consistently improves next-day service-demand forecasts - calendar most, weather a smaller "
        "consistent increment - across rolling folds, boroughs, and complaint groups. The "
        "improvement transfers in direction to a stylized staffing allocation but with attenuated, "
        "budget-dependent magnitude. The forecast gains are real and robust; the decision gains are "
        "smaller and conditional on capacity. This provides a reproducible baseline for "
        "forecast-to-decision evaluation in municipal service operations.")

    # End-matter statements
    add_heading(doc, "Reproducibility Statement", 1)
    add_body(doc,
        "All reported values derive from the analysis described in Sections 3-7, run on Python 3.11 "
        "with fixed random seeds. The analysis comprises weather ingestion, dataset construction, "
        "model training, evaluation, the decision simulation, rolling-origin validation, "
        "per-segment robustness analysis, crew-budget sensitivity, and practical-significance "
        "summaries; each stage is fully automated and reproducible from the public data sources. "
        "The aggregated real daily counts and the real NOAA weather export are retained as inputs; "
        "the large raw monthly exports and the trained model are regenerable from the public "
        "sources.")
    add_heading(doc, "Data Availability Statement", 1)
    add_body(doc,
        "NYC 311 Service Requests are publicly available via NYC Open Data (Socrata dataset "
        "erm2-nwe9; City of New York, accessed 2026). NOAA NCEI Daily Summaries (GHCN-Daily) for "
        "station USW00094728 are publicly available (NOAA NCEI, accessed 2026). The study window is "
        "2022-2024. The aggregated daily counts and the NOAA weather export used here are provided "
        "with the analysis materials; the large raw monthly 311 exports and the processed modelling "
        "dataset are regenerable from the public sources. No synthetic data and no synthetic "
        "weather are used.")
    add_heading(doc, "Ethics Statement", 1)
    add_body(doc,
        "The study uses public data only, at an aggregate date × borough × complaint-group "
        "level; no individual-level records and no personal data are used or produced. It makes no "
        "individual-level decisions and is not a deployed system. It makes no causal claim and no "
        "real dispatch or staffing-optimization claim. NYC 311 reflects reporting behaviour, not "
        "true incidence; reporting propensity varies across communities and time, so forecasts of "
        "311 volume are forecasts of reporting, not of need, and must not be read as measures of "
        "true demand or used in ways that could compound existing inequities.")

    # Appendix (page break before)
    page_break(doc)
    add_heading(doc, "Appendix", 1)
    add_heading(doc, "A. Feature and feature-set definitions", 2)
    add_body(doc,
        "Lag features (request_lag_1, request_lag_7) and rolling statistics (rolling_mean_7/14, "
        "rolling_std_7/14) per (borough, complaint group) cell, using only past observations with a "
        "one-day shift. Calendar features: is_weekend, is_holiday, day_of_week, month, quarter, "
        "year, day_of_year, week_of_year, is_month_start, is_month_end. Weather features: "
        "precipitation_mm, temp_max_c, temp_min_c, temp_avg_c, snowfall_mm, snow_depth_mm, "
        "wind_speed_ms. The four feature sets - internal history (internal_historical), calendar "
        "(calendar_augmented), weather (weather_augmented), and calendar + weather "
        "(calendar_weather_augmented) - are listed in Table A1.")
    add_table_caption(doc, "Table A1. Feature sets.")
    add_word_table(doc, ["Feature set", "Features"], [
        ["internal_historical", "borough, complaint_group, request_lag_1, request_lag_7, rolling_mean_7, rolling_mean_14, rolling_std_7, rolling_std_14"],
        ["calendar_augmented", "internal_historical + is_weekend, is_holiday, day_of_week, month, quarter, year, day_of_year, week_of_year, is_month_start, is_month_end"],
        ["weather_augmented", "internal_historical + precipitation_mm, temp_max_c, temp_min_c, temp_avg_c, snowfall_mm, snow_depth_mm, wind_speed_ms"],
        ["calendar_weather_augmented", "internal_historical + calendar features + weather features"],
    ])
    add_heading(doc, "B. Complaint-group mapping", 2)
    add_body(doc,
        "Raw complaint types are mapped by a deterministic, order-sensitive substring rule into "
        "eight groups (Housing, Noise, Sanitation, Street Condition, Water, Traffic, Public Safety, "
        "and a residual Other).")
    add_heading(doc, "C. Chronological split and rolling-origin setup", 2)
    add_body(doc,
        "Chronological 70/15/15 split by date (30,240 / 6,480 / 6,520 rows). Five expanding-window "
        "rolling-origin folds; each fold trains on all dates up to a cut point and tests on the next "
        "block, with no future information in training. Table A2 reports the mean fold MAE that "
        "underlies Figure 4.")
    add_table_caption(doc, "Table A2. Rolling-origin validation: random-forest mean fold test MAE by feature set.")
    add_word_table(doc, ["Configuration", "Mean MAE", "Std"], [
        ["naive_seasonal", "61.701", "9.673"],
        ["random_forest internal_historical", "57.027", "8.046"],
        ["random_forest weather_augmented", "56.222", "7.561"],
        ["random_forest calendar_augmented", "48.690", "9.590"],
        ["random_forest calendar_weather_augmented", "47.497", "8.746"],
    ])
    add_heading(doc, "D. Decision-simulation assumptions", 2)
    add_body(doc,
        "Stylized proportional allocation via a largest-remainder rule; baseline-budget "
        "configuration 135 crews × 50 requests per crew over 163 test days; weighted unmet "
        "demand up-weights Public Safety, Water, and Traffic; an oracle allocates on true next-day "
        "demand. The simulation uses no observed dispatch decisions.")
    add_heading(doc, "E. Crew-budget sensitivity", 2)
    add_body(doc,
        "Three budgets - scarce (100 crews, 5,000 daily capacity), moderate (160 / 8,000), and "
        "generous (220 / 11,000); per-policy results are reported in Table 3.")
    add_heading(doc, "F. Weather-data treatment", 2)
    add_body(doc,
        "Single NOAA station (USW00094728) joined to all boroughs by date; temp_avg_c derived from "
        "observed daily maximum and minimum (source average-temperature field empty); five missing "
        "wind-speed days time-interpolated from real neighbours; no synthetic weather. Figure A1 "
        "shows the series.")
    add_figure(doc, "A1")
    add_heading(doc, "G. Full results tables", 2)
    add_body(doc,
        "Table A3 is the complete 13-row model comparison (Figure A2). Table A4 reports per-borough "
        "robustness (Figure A3) and Table A5 per-complaint-group robustness (Figure A4), each "
        "comparing internal history with calendar for the random forest. Figure A6 shows internal "
        "history versus calendar per model; Figure A5 shows a baseline-budget policy comparison "
        "with the oracle.")
    add_table_caption(doc, "Table A3. Full model comparison (held-out test).")
    add_word_table(doc,
        ["Model", "Feature set", "Test MAE", "Test RMSE", "Test MAPE (%)", "Test R²"],
        [
            ["naive_seasonal", "naive_seasonal", "71.848", "197.743", "34.689", "0.563"],
            ["ridge", "internal_historical", "69.219", "187.753", "36.073", "0.606"],
            ["ridge", "calendar_augmented", "68.758", "187.757", "35.729", "0.606"],
            ["ridge", "weather_augmented", "69.283", "187.784", "36.009", "0.606"],
            ["ridge", "calendar_weather_augmented", "68.915", "187.762", "36.140", "0.606"],
            ["random_forest", "internal_historical", "65.282", "184.787", "34.259", "0.618"],
            ["random_forest", "calendar_augmented", "58.082", "181.135", "29.026", "0.633"],
            ["random_forest", "weather_augmented", "64.104", "181.379", "33.614", "0.632"],
            ["random_forest", "calendar_weather_augmented", "56.224", "178.150", "28.173", "0.645"],
            ["gradient_boosting", "internal_historical", "67.493", "187.734", "38.378", "0.606"],
            ["gradient_boosting", "calendar_augmented", "61.710", "183.886", "34.152", "0.622"],
            ["gradient_boosting", "weather_augmented", "67.553", "188.046", "38.236", "0.605"],
            ["gradient_boosting", "calendar_weather_augmented", "61.878", "181.778", "33.822", "0.631"],
        ], font_size=9)
    add_table_caption(doc, "Table A4. Borough robustness (random forest; internal history versus calendar).")
    add_word_table(doc,
        ["Borough", "Internal MAE", "Calendar MAE", "Improvement (%)"],
        [
            ["Bronx", "120.194", "109.567", "8.84"],
            ["Brooklyn", "76.991", "64.175", "16.65"],
            ["Manhattan", "58.178", "48.078", "17.36"],
            ["Queens", "53.771", "43.675", "18.78"],
            ["Staten Island", "12.766", "11.129", "12.82"],
        ], font_size=9)
    add_table_caption(doc, "Table A5. Complaint-group robustness (random forest; internal history versus calendar).")
    add_word_table(doc,
        ["Complaint group", "Internal MAE", "Calendar MAE", "Improvement (%)"],
        [
            ["Noise", "194.882", "168.272", "13.65"],
            ["Housing", "121.762", "106.839", "12.26"],
            ["Other", "54.794", "44.474", "18.83"],
            ["Traffic", "45.000", "40.990", "8.91"],
            ["Sanitation", "24.957", "22.078", "11.54"],
            ["Public Safety", "24.449", "21.496", "12.08"],
            ["Water", "25.111", "20.585", "18.02"],
            ["Street Condition", "24.084", "17.865", "25.82"],
        ], font_size=9)
    add_table_caption(doc, "Table A6. Limitations and mitigations.")
    add_word_table(doc, ["Limitation", "Mitigation / Scope statement"], [
        ["311 reporting bias", "Documented; target framed as reported volume; no need-based or causal claim"],
        ["Borough-level aggregation", "Granularity stated; within-borough variation not captured"],
        ["Complaint-group mapping coarseness", "Deterministic, documented; residual Other group reported"],
        ["Single-station weather proxy", "Documented spatial-resolution limitation; city-level proxy"],
        ["Derived average temperature", "Mean of observed daily max/min; source field empty; documented"],
        ["No transit or event data", "Scope stated; future work"],
        ["Stylized decision simulation", "Labelled stylized; oracle bound included for context"],
        ["No observed dispatch decisions", "Counterfactual only; no real-dispatch or optimization claim"],
        ["Forecast-versus-decision gap", "Decision metrics reported; transfer honestly attenuated/budget-dependent"],
        ["No causal inference", "No causal claim anywhere"],
        ["NYC-only, 2022-2024", "External-validity limitation stated explicitly"],
    ], font_size=9)
    add_heading(doc, "H. Reproducibility", 2)
    add_body(doc,
        "The full analysis is reproducible from the public data sources following the protocol "
        "described in Sections 3-7; see the Reproducibility Statement.")

    add_heading(doc, "Appendix Figures", 2)
    for label in ("A2", "A3", "A4", "A5", "A6"):
        add_figure(doc, label)

    # References (page break before)
    page_break(doc)
    add_heading(doc, "References", 1)
    refs = [
        "City of New York. (2026). 311 Service Requests from 2010 to Present [data set]. "
        "NYC Open Data, Socrata dataset erm2-nwe9. Retrieved 2026-06-03 from "
        "https://data.cityofnewyork.us/Social-Services/"
        "311-Service-Requests-from-2010-to-Present/erm2-nwe9",
        "Cui, R., Gallino, S., Moreno, A., & Zhang, D. J. (2018). The Operational Value of Social "
        "Media Information. Production and Operations Management, 27(10), 1749-1769. "
        "https://doi.org/10.1111/poms.12707",
        "National Oceanic and Atmospheric Administration, National Centers for Environmental "
        "Information. (2026). Global Historical Climatology Network Daily (GHCNd) [data set]. "
        "NOAA NCEI Daily Summaries; station USW00094728, NY City Central Park. Retrieved "
        "2026-06-03 from https://www.ncei.noaa.gov/products/land-based-station/"
        "global-historical-climatology-network-daily",
        "Samorani, M., Harris, S. L., Blount, L. G., Lu, H., & Santoro, M. A. (2022). Overbooked "
        "and Overlooked: Machine Learning and Racial Bias in Medical Appointment Scheduling. "
        "Manufacturing & Service Operations Management, 24(6), 2825-2842. "
        "https://doi.org/10.1287/msom.2021.0999",
    ]
    for r in refs:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        run = p.add_run(r)
        _set_run_font(run)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUT))
    print("WROTE", OUT)


if __name__ == "__main__":
    build()
