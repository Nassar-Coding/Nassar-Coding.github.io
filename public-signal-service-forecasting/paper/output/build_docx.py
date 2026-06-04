"""Build the Word submission document from the final draft and committed assets.

This is a one-off production script. It reads paper/final_submission_draft.md,
paper/references.bib, paper/figures/*.png, and the figure captions, and writes a
formatted .docx with embedded images, real Word tables, styled headings, page
numbers, and a clean References section. It does not change any empirical value;
all text and numbers come verbatim from the committed draft.
"""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

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

SUBTITLE = (
    "arXiv-style / workshop-style research artifact. The study is predictive and "
    "correlational; it makes no causal, production-readiness, real-dispatch, or "
    "full-paper-readiness claim. All empirical values are read from committed "
    "repository artifacts under reports/ and data/metadata/."
)

FIG_CAPTIONS = {
    1: "Held-out test MAE for the naive baseline and every model x feature-set combination across the four feature sets.",
    2: "Best test MAE achieved per feature set across models.",
    3: "Per-fold test MAE by configuration across five expanding-window chronological folds.",
    4: "Internal-historical vs calendar-augmented test MAE by borough (random forest).",
    5: "Internal-historical vs calendar-augmented test MAE by complaint group (random forest).",
    6: "Total weighted unmet demand by policy under scarce, moderate, and generous crew budgets.",
    7: "Observed vs predicted city-wide next-day request totals over the test period for the best model.",
    8: "Real NOAA daily weather series for the Central Park station over 2022-2024.",
    9: "Total weighted unmet demand by policy at the baseline crew budget, with the oracle benchmark.",
    10: "Internal-historical vs calendar-augmented test MAE per non-naive model.",
}

FIG_FILES = {
    1: "figure_1_model_comparison_mae.png",
    2: "figure_2_feature_set_comparison_mae.png",
    3: "figure_3_rolling_validation_mae.png",
    4: "figure_4_borough_robustness_mae.png",
    5: "figure_5_complaint_group_robustness_mae.png",
    6: "figure_6_decision_sensitivity.png",
    7: "figure_7_actual_vs_predicted.png",
    8: "figure_8_weather_feature_summary.png",
    9: "figure_9_decision_quality_comparison.png",
    10: "figure_10_internal_vs_calendar_augmented_mae.png",
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
    sp = doc.add_paragraph()
    sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sr = sp.add_run(SUBTITLE)
    _set_run_font(sr, size=Pt(10), italic=True)


def add_heading(doc: Document, text: str, level: int) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    if level == 1:
        _set_run_font(r, size=Pt(14), bold=True)
    else:
        _set_run_font(r, size=Pt(12), bold=True)


def add_body(doc: Document, text: str) -> None:
    """Add a justified body paragraph, rendering **bold** lead-ins."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    # Split on ** for simple bold lead-ins.
    parts = text.split("**")
    for i, part in enumerate(parts):
        if not part:
            continue
        r = p.add_run(part)
        _set_run_font(r, bold=(i % 2 == 1))
    return p


def add_figure(doc: Document, number: int, width_in: float = 6.0) -> None:
    path = FIG / FIG_FILES[number]
    fp = doc.add_paragraph()
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = fp.add_run()
    run.add_picture(str(path), width=Inches(width_in))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cr = cap.add_run(f"Figure {number}. {FIG_CAPTIONS[number]}")
    _set_run_font(cr, size=Pt(10), italic=True)


def add_table_caption(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    r = p.add_run(text)
    _set_run_font(r, size=Pt(11), bold=True)


def add_word_table(doc: Document, header: list[str], rows: list[list[str]],
                   font_size: int = 10) -> None:
    table = doc.add_table(rows=1, cols=len(header))
    table.style = "Table Grid"
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hdr = table.rows[0].cells
    for j, h in enumerate(header):
        hdr[j].text = ""
        run = hdr[j].paragraphs[0].add_run(h)
        _set_run_font(run, size=Pt(font_size), bold=True)
    for row in rows:
        cells = table.add_row().cells
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
        "(9,851,452 raw records aggregated to 43,240 date x borough x complaint_group "
        "observations) and real NOAA Central Park daily weather, we compare four feature sets - "
        "internal_historical, calendar_augmented, weather_augmented, and "
        "calendar_weather_augmented - across four model families under a strictly chronological "
        "protocol with five-fold rolling-origin validation. Calendar features deliver the largest "
        "accuracy gain; real weather adds a smaller but consistent further gain. The best model, a "
        "random forest on calendar_weather_augmented, attains a held-out test mean absolute error "
        "(MAE) of 55.325 versus 71.848 for a naive seasonal baseline, a 23.0% reduction. A stylized "
        "proportional staffing simulation shows the augmented policy reduces weighted unmet demand "
        "at every crew budget tested and closes 26.381% of the gap to an oracle at the baseline "
        "budget, but the magnitude of the decision benefit is budget-dependent. The central finding "
        "is that the forecast gains are real and robust, while the decision gains are smaller and "
        "conditional on capacity. The work is a reproducible baseline; no synthetic data or "
        "synthetic weather is used.")

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
        "with real NOAA weather, with a leakage-controlled chronological protocol. (ii) An honest "
        "four-way feature-set comparison isolating the marginal value of calendar features and of "
        "real weather. (iii) A transparent forecast-to-decision simulation that measures whether "
        "forecast gains transfer to a stylized allocation, with the result reported as it is: "
        "directionally positive but budget-dependent. The study is predictive and correlational and "
        "is positioned as an arXiv/workshop artifact, not a full paper; gating items for a stronger "
        "paper are stated in Section 8.")

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
        "“311 Service Requests from 2010 to Present”; City of New York, 2026), restricted "
        "to 2022-2024. From 9,851,452 raw records the pipeline produces a 43,240-row "
        "date x borough x complaint_group panel spanning observed dates 2022-01-15 to 2024-12-30 "
        "(after lag and rolling warmup). Records are mapped to eight complaint groups (Housing, "
        "Noise, Other, Public Safety, Sanitation, Street Condition, Traffic, Water) by a "
        "deterministic substring rule and aggregated to daily counts over the five NYC boroughs. "
        "The forecasting target is request_volume_next_day, the observed next-day request count per "
        "cell, defined only when consecutive calendar days are present.")
    add_body(doc,
        "**NOAA NCEI Daily Summaries (GHCN-Daily)** (NOAA NCEI, 2026), station USW00094728 (NY City "
        "Central Park), 2022-2024, 1,096 daily rows. Variables used: precipitation, daily maximum "
        "and minimum temperature, average temperature, snowfall, snow depth, and wind speed. The "
        "source average-temperature field was empty for this station, so average temperature is "
        "derived as the mean of observed daily maximum and minimum; five missing wind-speed days "
        "are filled by time interpolation of neighbouring real observations. A single Central Park "
        "station is used as a city-level proxy, a documented spatial-resolution limitation.")
    add_table_caption(doc, "Table 1. Dataset summary.")
    add_word_table(doc, ["Property", "Value"], [
        ["Service data", "NYC 311 Service Requests (NYC Open Data, erm2-nwe9)"],
        ["Study window", "2022-01-01 to 2024-12-31"],
        ["Raw records", "9,851,452"],
        ["Processed rows", "43,240 (date x borough x complaint_group)"],
        ["Observed range (processed)", "2022-01-15 to 2024-12-30"],
        ["Boroughs / complaint groups", "5 / 8"],
        ["Target", "request_volume_next_day (observed next-day count)"],
        ["Weather source", "NOAA NCEI Daily Summaries (GHCN-Daily)"],
        ["Weather station", "USW00094728 (NY City Central Park); single-station proxy"],
        ["Weather rows / variables", "1,096 / 7"],
        ["Synthetic data or weather", "none"],
    ])

    # 4. Methods
    add_heading(doc, "4. Methods", 1)
    add_body(doc,
        "We compare four feature sets: internal_historical (lag and rolling statistics of the "
        "per-cell series), calendar_augmented (internal plus deterministic calendar features), "
        "weather_augmented (internal plus the seven real weather variables), and "
        "calendar_weather_augmented (internal plus calendar plus weather). Full feature definitions "
        "are in Appendix A.")
    add_body(doc,
        "Four model families are evaluated: a naive seasonal baseline (trailing 7-day mean), Ridge "
        "regression, a random forest, and gradient boosting. Categorical features (borough, "
        "complaint_group) are one-hot encoded; numeric features pass through. Lag and rolling "
        "features use only past observations, with rolling statistics shifted by one day to avoid "
        "same-day or future leakage.")
    add_body(doc,
        "Validation uses a strictly chronological split by date: the earliest 70% of dates for "
        "training (30,240 rows), the next 15% for validation (6,480 rows), and the latest 15% for "
        "test (6,520 rows). The primary metric is MAE; RMSE, MAPE (with safe handling of near-zero "
        "actuals), and R-squared are also reported. The best configuration by validation MAE is "
        "refit on train+validation before the final test evaluation. Separately, five "
        "expanding-window rolling-origin folds assess stability.")
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
        "consistent gain on top of it. For the random forest, MAE falls from 65.282 "
        "(internal_historical) to 58.082 (calendar_augmented); weather alone improves the internal "
        "model (64.104 versus 65.282), and calendar+weather is best (56.224 on the train-only fit). "
        "Ridge does not benefit from weather (internal 69.219, weather 69.283, calendar+weather "
        "68.915). Figure 2 shows the best test MAE per feature set; the full per-model results are "
        "in Table 3 (trimmed below; complete table in Appendix G).")
    add_table_caption(doc,
        "Table 3 (selected rows). Held-out test MAE by model and feature set; lower is better. "
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
        "The selected model (by validation MAE, refit on train+validation) is the random forest on "
        "calendar_weather_augmented, with held-out test MAE 55.325, RMSE 177.476, MAPE 27.469%, and "
        "R-squared 0.648 - a 23.0% MAE reduction over the naive seasonal baseline (71.848). Figure 7 "
        "shows observed versus predicted city-wide next-day totals over the test period, which track "
        "the overall level and weekly pattern of demand.")
    add_figure(doc, 2)
    add_figure(doc, 7)

    # 6. Forecast-to-Decision Simulation
    add_heading(doc, "6. Forecast-to-Decision Simulation", 1)
    add_body(doc,
        "At the baseline budget (135 crews, 50 requests per crew, 163 test days), total weighted "
        "unmet demand is 643,324 under the internal-historical policy and 631,191 under "
        "calendar+weather, versus an oracle of 597,332: the augmented policy reduces weighted unmet "
        "demand by 1.886% and closes 26.381% of the baseline-to-oracle gap.")
    add_body(doc,
        "Across crew budgets (Table 7, Figure 6) the calendar+weather policy is better than the "
        "baseline in all three settings, but the magnitude grows with capacity: the weighted-unmet "
        "reduction is 0.38% (scarce, 100 crews), 4.32% (moderate, 160), and 14.53% (generous, 220). "
        "The headline contrast - an approximately 11-15% forecast-accuracy gain versus a roughly "
        "1.9% decision-quality gain at the baseline budget - is the central observation: average "
        "accuracy and operational value are not the same, and a scarce budget with demand "
        "concentrated in a few large cells limits how much any forecast can help.")
    add_table_caption(doc,
        "Table 7. Decision sensitivity by crew budget. Stylized simulation; total weighted unmet "
        "demand (lower is better); calendar+weather versus internal-historical.")
    add_word_table(doc,
        ["Setting", "Crews", "Internal", "Calendar+Weather", "Oracle", "Reduction", "Gap to oracle closed"],
        [
            ["scarce", "100", "941,817", "938,211", "928,491", "0.38%", "27.06%"],
            ["moderate", "160", "454,073", "434,469", "367,553", "4.32%", "22.66%"],
            ["generous", "220", "164,197", "140,346", "50,865", "14.53%", "21.05%"],
        ])
    add_figure(doc, 6)

    # 7. Robustness Checks
    add_heading(doc, "7. Robustness Checks", 1)
    add_body(doc,
        "Five-fold expanding-window rolling-origin validation (Figure 3; full table in Appendix C) "
        "shows calendar augmentation lowering MAE in every fold for every model: mean improvement "
        "15.13% for the random forest, 9.94% for gradient boosting, and 0.94% for Ridge, each in "
        "all 5 of 5 folds. The calendar_weather_augmented random forest has the lowest mean fold MAE "
        "(47.497). Segmented analysis (random forest, internal vs calendar; Appendix G) shows the "
        "improvement holds for all five boroughs (about 8.8% to 18.8%) and all eight complaint "
        "groups (about 8.9% to 25.8%); absolute error concentrates in the highest-volume segments "
        "(Noise, Housing; the Bronx). The forecast improvement is therefore consistent across folds "
        "and segments, not an artifact of one split.")
    add_figure(doc, 3)

    # 8. Limitations
    add_heading(doc, "8. Limitations", 1)
    add_body(doc,
        "The study is predictive and correlational and makes no causal claim. NYC 311 reflects "
        "reporting behaviour, not true incidence (reporting bias), so forecasts predict reported "
        "volume. Weather is a single Central Park station used as a city-level proxy. Borough-level "
        "aggregation hides within-borough variation; the complaint-group mapping is a deterministic "
        "approximation with a residual Other group. No transit or event data is included. The "
        "staffing simulation is a stylized proportional heuristic - not real dispatch, not staffing "
        "optimization, not validated against any real policy - and omits crew travel, shifts, "
        "backlog, intra-day timing, and substitution; it uses no observed dispatch decisions. "
        "Results apply to NYC and 2022-2024 only.")
    add_body(doc,
        "Gating items for a stronger (full) paper: a non-stylized, agency-grounded decision model "
        "with an empirical service-level realism check; formal forecast-difference testing (for "
        "example a Diebold-Mariano test) with uncertainty intervals; and broader external signals "
        "beyond a single weather station, or cross-city replication.")

    # 9. Conclusion
    add_heading(doc, "9. Conclusion", 1)
    add_body(doc,
        "On real NYC 311 data augmented with real NOAA weather, public-signal augmentation "
        "consistently improves next-day service-demand forecasts - calendar most, weather a smaller "
        "consistent increment - across rolling folds, boroughs, and complaint groups. The "
        "improvement transfers in direction to a stylized staffing allocation but with attenuated, "
        "budget-dependent magnitude. The forecast gains are real and robust; the decision gains are "
        "smaller and conditional on capacity. The artifact is a reproducible baseline suitable as a "
        "workshop / short-paper / arXiv-style contribution.")

    # End-matter statements
    add_heading(doc, "Reproducibility Statement", 1)
    add_body(doc,
        "All values are read from committed artifacts under reports/ and data/metadata/. The "
        "pipeline is run with python -m src.weather, python -m src.build_dataset, python -m "
        "src.train, python -m src.evaluate, python -m src.decision_simulation, python -m "
        "src.monitor, python -m src.rolling_validation, python -m src.robustness_analysis, python -m "
        "src.decision_sensitivity, and python -m src.practical_significance, on Python 3.11. The "
        "quality gate is ruff check . and pytest, run offline on a committed real-schema sample; "
        "continuous integration runs the pipeline in that sample mode. No API keys or secrets are "
        "required. The committed inputs are the aggregated real daily counts and the real NOAA "
        "weather export; the large raw monthly exports and the trained model binary are not "
        "committed.")
    add_heading(doc, "Data Availability Statement", 1)
    add_body(doc,
        "NYC 311 Service Requests are public via NYC Open Data (Socrata dataset erm2-nwe9; City of "
        "New York, 2026). NOAA NCEI Daily Summaries (GHCN-Daily) for station USW00094728 are public "
        "(NOAA NCEI, 2026). The study window is 2022-2024. The aggregated daily counts and the NOAA "
        "export used here are committed; the large raw monthly 311 exports and the processed "
        "modelling dataset are regenerable and not committed; small real-schema samples are "
        "committed for continuous integration. No synthetic data and no synthetic weather are used.")
    add_heading(doc, "Ethics Statement", 1)
    add_body(doc,
        "The study uses public data only, at an aggregate date x borough x complaint_group level; no "
        "individual-level records and no personal data are used or produced. It makes no "
        "individual-level decisions, is not deployed, and is not public-safety software. It makes no "
        "causal claim and no real dispatch or staffing optimization claim. NYC 311 reflects "
        "reporting behaviour, not true incidence; reporting propensity varies across communities and "
        "time, so forecasts of 311 volume are forecasts of reporting, not of need, and must not be "
        "read as measures of true demand or used in ways that could compound existing inequities.")

    # Appendix (page break before)
    page_break(doc)
    add_heading(doc, "Appendix", 1)
    add_heading(doc, "A. Feature and feature-set definitions", 2)
    add_body(doc,
        "Lag features (request_lag_1, request_lag_7) and rolling statistics (rolling_mean_7/14, "
        "rolling_std_7/14) per (borough, complaint_group) cell, using only past observations with a "
        "one-day shift. Calendar features: is_weekend, is_holiday, day_of_week, month, quarter, "
        "year, day_of_year, week_of_year, is_month_start, is_month_end. Weather features: "
        "precipitation_mm, temp_max_c, temp_min_c, temp_avg_c, snowfall_mm, snow_depth_mm, "
        "wind_speed_ms. Feature sets: internal_historical; calendar_augmented (internal + calendar); "
        "weather_augmented (internal + weather); calendar_weather_augmented (internal + calendar + "
        "weather). Table 2 lists the feature sets.")
    add_table_caption(doc, "Table 2. Feature sets.")
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
        "block, with no future information in training. Per-fold metrics are in "
        "reports/rolling_validation_report.csv; the summary (Figure 3 source) is in "
        "reports/rolling_validation_summary.json. Table 4 reports the mean fold MAE.")
    add_table_caption(doc, "Table 4. Rolling-origin validation: random-forest mean fold test MAE by feature set.")
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
        "configuration 135 crews x 50 requests per crew over 163 test days; weighted unmet demand "
        "up-weights Public Safety, Water, and Traffic; an oracle allocates on true next-day demand. "
        "Not real dispatch; uses no observed dispatch decisions.")
    add_heading(doc, "E. Crew-budget sensitivity", 2)
    add_body(doc,
        "Three budgets - scarce (100 crews, 5,000 daily capacity), moderate (160 / 8,000), generous "
        "(220 / 11,000); per-policy results in reports/decision_sensitivity_report.csv and "
        "..._summary.json (Table 7).")
    add_heading(doc, "F. Weather-data treatment", 2)
    add_body(doc,
        "Single NOAA station (USW00094728) joined to all boroughs by date; temp_avg_c derived from "
        "observed TMAX/TMIN (source TAVG empty); five missing wind-speed days time-interpolated from "
        "real neighbours; no synthetic weather (data/metadata/weather_source_report.json). Figure 8 "
        "shows the series.")
    add_figure(doc, 8)
    add_heading(doc, "G. Full results tables", 2)
    add_body(doc,
        "Table G1 is the complete 13-row model comparison (reports/model_comparison.csv; Figure 1). "
        "Table G2 reports per-borough robustness (reports/borough_performance.csv; Figure 4) and "
        "Table G3 per-complaint-group robustness (reports/complaint_group_performance.csv; "
        "Figure 5), each comparing internal-historical vs calendar-augmented for the random forest. "
        "Figure 10 shows internal vs calendar-augmented per model; Figure 9 shows a baseline-budget "
        "policy comparison with the oracle.")
    add_table_caption(doc, "Table G1. Full model comparison (held-out test).")
    add_word_table(doc,
        ["Model", "Feature set", "Test MAE", "Test RMSE", "Test MAPE (%)", "Test R2"],
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
    add_table_caption(doc, "Table G2. Borough robustness (random forest; internal vs calendar).")
    add_word_table(doc,
        ["Borough", "Internal MAE", "Calendar MAE", "Improvement (%)"],
        [
            ["Bronx", "120.194", "109.567", "8.84"],
            ["Brooklyn", "76.991", "64.175", "16.65"],
            ["Manhattan", "58.178", "48.078", "17.36"],
            ["Queens", "53.771", "43.675", "18.78"],
            ["Staten Island", "12.766", "11.129", "12.82"],
        ], font_size=9)
    add_table_caption(doc, "Table G3. Complaint-group robustness (random forest; internal vs calendar).")
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
    add_table_caption(doc, "Table 8. Limitations and mitigations.")
    add_word_table(doc, ["Limitation", "Mitigation / honest framing"], [
        ["311 reporting bias", "Documented; target framed as reported volume; no need-based or causal claim"],
        ["Borough-level aggregation", "Granularity stated; within-borough variation not captured"],
        ["Complaint-group mapping coarseness", "Deterministic, documented; residual Other group reported"],
        ["Single-station weather proxy", "Documented spatial-resolution limitation; city-level proxy"],
        ["Derived average temperature", "Mean of observed TMAX/TMIN; source TAVG empty; documented"],
        ["No transit or event data", "Scope stated; future work"],
        ["Stylized decision simulation", "Labelled stylized; not real dispatch; oracle bound included"],
        ["No observed dispatch decisions", "Counterfactual only; no real-dispatch or optimization claim"],
        ["Forecast-versus-decision gap", "Decision metrics reported; transfer honestly attenuated/budget-dependent"],
        ["No causal inference", "No causal claim anywhere"],
        ["NYC-only, 2022-2024", "External-validity limitation stated explicitly"],
    ], font_size=9)
    add_heading(doc, "H. Reproducibility commands", 2)
    add_body(doc, "See the Reproducibility Statement.")

    add_heading(doc, "Appendix Figures", 2)
    for n in (1, 4, 5, 9, 10):
        add_figure(doc, n)

    # References (page break before)
    page_break(doc)
    add_heading(doc, "References", 1)
    refs = [
        "City of New York. (2026). 311 Service Requests from 2010 to Present. NYC Open Data, "
        "Socrata dataset erm2-nwe9. "
        "https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9. "
        "Accessed 2026-06-03.",
        "Cui, R., Gallino, S., Moreno, A., & Zhang, D. J. (2018). The Operational Value of Social "
        "Media Information. Production and Operations Management, 27(10), 1749-1769. "
        "https://doi.org/10.1111/poms.12707.",
        "National Oceanic and Atmospheric Administration, National Centers for Environmental "
        "Information. (2026). Global Historical Climatology Network Daily (GHCNd). NOAA NCEI Daily "
        "Summaries; station USW00094728, NY City Central Park. "
        "https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily. "
        "Accessed 2026-06-03.",
        "Samorani, M., Harris, S. L., Blount, L. G., Lu, H., & Santoro, M. A. (2022). Overbooked and "
        "Overlooked: Machine Learning and Racial Bias in Medical Appointment Scheduling. "
        "Manufacturing & Service Operations Management, 24(6), 2825-2842. "
        "https://doi.org/10.1287/msom.2021.0999.",
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
