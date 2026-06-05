"""Single source of record for the submission document content.

This module holds the full text, tables, figures, and references of the paper
via ``emit(renderer)``; the final PDF and Word documents were produced from it,
so the two deliverables carry identical content. No empirical value is defined
anywhere else; all numbers here come verbatim from the verified results.
"""
from __future__ import annotations

TITLE = (
    "From Forecast Accuracy to Operational Value: "
    "Public Signal Augmentation for NYC 311 Service Demand"
)

# Author metadata.
AUTHOR = "Nassar Naif Alsharif"
AFFILIATION = "Independent researcher"
EMAIL = "NassarAlsharif0@gmail.com"

# label -> (filename, caption). Numbering follows order of first appearance:
# main-body figures 1-4, appendix figures A1-A6.
FIGS = {
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

REFS = [
    "Bertsimas, D., & Kallus, N. (2020). From Predictive to Prescriptive Analytics. Management "
    "Science, 66(3), 1025-1044. https://doi.org/10.1287/mnsc.2018.3253",
    "City of New York. (2026). 311 Service Requests from 2020 to Present [data set]. "
    "NYC Open Data, Socrata dataset erm2-nwe9. Retrieved 2026-06-03 from "
    "https://data.cityofnewyork.us/Social-Services/"
    "311-Service-Requests-from-2020-to-Present/erm2-nwe9",
    "Cui, R., Gallino, S., Moreno, A., & Zhang, D. J. (2018). The Operational Value of Social "
    "Media Information. Production and Operations Management, 27(10), 1749-1769. "
    "https://doi.org/10.1111/poms.12707",
    "Elmachtoub, A. N., & Grigas, P. (2022). Smart “Predict, then Optimize”. Management Science, "
    "68(1), 9-26. https://doi.org/10.1287/mnsc.2020.3922",
    "Green, L. V., Kolesar, P. J., & Whitt, W. (2007). Coping with Time-Varying Demand When "
    "Setting Staffing Requirements for a Service System. Production and Operations Management, "
    "16(1), 13-39. https://doi.org/10.1111/j.1937-5956.2007.tb00164.x",
    "Kontokosta, C. E., & Hong, B. (2021). Bias in smart city governance: How socio-spatial "
    "disparities in 311 complaint behavior impact the fairness of data-driven decisions. "
    "Sustainable Cities and Society, 64, 102503. https://doi.org/10.1016/j.scs.2020.102503",
    "National Oceanic and Atmospheric Administration, National Centers for Environmental "
    "Information. (2026). Global Historical Climatology Network Daily (GHCNd) [data set]. "
    "NOAA NCEI Daily Summaries; station USW00094728, NY City Central Park. Retrieved "
    "2026-06-03 from https://www.ncei.noaa.gov/products/land-based-station/"
    "global-historical-climatology-network-daily",
    "Samorani, M., Harris, S. L., Blount, L. G., Lu, H., & Santoro, M. A. (2022). Overbooked "
    "and Overlooked: Machine Learning and Racial Bias in Medical Appointment Scheduling. "
    "Manufacturing & Service Operations Management, 24(6), 2825-2842. "
    "https://doi.org/10.1287/msom.2021.0999",
    "Steinker, S., Hoberg, K., & Thonemann, U. W. (2017). The Value of Weather Information for "
    "E-Commerce Operations. Production and Operations Management, 26(10), 1854-1874. "
    "https://doi.org/10.1111/poms.12721",
]


def _fig(r, label):
    filename, caption = FIGS[label]
    r.figure(label, filename, caption)


def emit(r) -> None:
    """Drive a renderer to produce the full document in order."""
    r.title(TITLE, AUTHOR, AFFILIATION, EMAIL)

    # Abstract
    r.h1("Abstract")
    r.body(
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
        "Calendar features deliver the largest accuracy gain across models; adding real weather "
        "further improves the selected random-forest model. The best model, a random forest on the "
        "calendar + weather "
        "feature set, attains a held-out test mean absolute error (MAE) of 55.325 versus 71.848 "
        "for a naive seasonal baseline, a 23.0% reduction. A stylized proportional staffing "
        "simulation shows the augmented policy reduces weighted unmet demand at all three tested "
        "crew budgets and closes 26.381% of the gap to an oracle at the baseline budget, but the "
        "magnitude of the decision benefit is budget-dependent. The central finding is that the "
        "calendar-augmentation gains are observed consistently across the evaluated splits, folds, "
        "boroughs, and complaint groups, while the decision gains are smaller and conditional on "
        "capacity. "
        "This study "
        "provides a reproducible evaluation of public-signal augmentation "
        "for municipal service-demand forecasting; no synthetic data or synthetic weather is used.")

    # 1. Introduction
    r.h1("1. Introduction")
    r.body(
        "Municipal service operations plan finite crews against demand that varies by day of week, "
        "season, and location. Short-horizon (next-day) volume forecasts are a standard planning "
        "input. Two questions follow. First, a predictive question: does augmenting an "
        "internal-history forecasting model with public external signals reduce next-day forecast "
        "error? Second, a decision question: does any such forecast improvement actually improve "
        "the quality of a capacity allocation built on top of the forecast?")
    r.body(
        "These questions are related but distinct. Mean absolute error weights all errors equally "
        "across cells and days. A capacity allocation does not: under a fixed, scarce budget, an "
        "error on a high-volume or high-priority cell is more consequential than an error on a "
        "quiet one, and a proportional allocation maps forecasts to capacity non-linearly. A study "
        "reporting only forecast metrics can therefore misstate operational relevance.")
    r.body(
        "We make three contributions. (i) A reproducible, real-data baseline on NYC 311 augmented "
        "with real NOAA weather, with a leakage-controlled chronological protocol. (ii) A "
        "controlled four-way feature-set comparison isolating the marginal value of calendar "
        "features and of real weather. (iii) A transparent forecast-to-decision simulation that "
        "measures whether forecast gains transfer to a stylized allocation, showing directionally "
        "positive but budget-dependent decision benefits. The study is predictive "
        "and correlational; Section 8 states the scope of the analysis and the natural directions "
        "for extending it.")

    # 2. Related Work
    r.h1("2. Related Work")
    r.body(
        "The methodological template is the demonstration that publicly available signals can "
        "improve operational forecasts. Cui et al. (2018) show, in a retail setting, that public "
        "social-media information improves daily sales forecasts across multiple machine-learning "
        "methods, with tree-based methods extracting more value from heterogeneous public signals "
        "than linear methods, and they frame the contribution as feature value rather than method "
        "novelty. Our work is in this lineage but moves from retail to municipal service "
        "operations, uses public weather rather than social media, and adds an explicit "
        "forecast-to-decision layer rather than stopping at forecast accuracy.")
    r.body(
        "A second line argues that predictive accuracy and decision quality are distinct "
        "objectives. Elmachtoub and Grigas (2022) develop a “predict, then optimize” framework in "
        "which models are trained with respect to the downstream optimization objective rather than "
        "prediction error alone, and Bertsimas and Kallus (2020) show how predictive models can be "
        "turned into prescriptions for decision problems. Our forecast-to-decision simulation is "
        "motivated by the same distinction, although we keep the allocation deliberately stylized "
        "and evaluate the decision objective rather than re-training the forecaster for it.")
    r.body(
        "Within operations, public weather data has been shown to improve demand forecasts: "
        "Steinker, Hoberg, and Thonemann (2017) quantify the value of weather information for "
        "e-commerce order forecasting, which parallels our use of NOAA weather as a public signal. "
        "Planning capacity against time-varying demand is a long-standing service-operations "
        "problem; Green, Kolesar, and Whitt (2007) study staffing requirements when demand varies "
        "over time, motivating our crew-budget sensitivity analysis.")
    r.body(
        "Prediction-driven prioritization in service and scheduling settings has been studied from "
        "an equity and efficiency angle (Samorani et al., 2022). We make no equity or causal claim; "
        "we cite this line only to situate the general point that the objective placed on top of a "
        "predictive model, not the model alone, shapes outcomes—which motivates our separate "
        "evaluation of the decision layer. Relatedly, our use of 311 data inherits a documented "
        "reporting bias: Kontokosta and Hong (2021) show that socio-spatial disparities in 311 "
        "complaint behaviour can make data-driven decisions unfair, which is why we frame the "
        "forecasting target as reported request volume rather than underlying need.")

    # 3. Data
    r.h1("3. Data")
    r.body(
        "Two real public sources are used; no synthetic data and no synthetic weather are used "
        "anywhere. Table 1 summarizes both.")
    r.body(
        "**NYC 311 Service Requests** (NYC Open Data, Socrata dataset erm2-nwe9, "
        "“311 Service Requests from 2020 to Present”; City of New York, accessed 2026), "
        "restricted to 2022-2024. From 9,851,452 raw records the preprocessing procedure yields a "
        "43,240-row date × borough × complaint-group panel spanning observed dates "
        "2022-01-15 to 2024-12-30 (after lag and rolling warmup). Records are mapped to eight "
        "complaint groups (Housing, Noise, Other, Public Safety, Sanitation, Street Condition, "
        "Traffic, Water) by a deterministic substring rule and aggregated to daily counts over the "
        "five NYC boroughs. The forecasting target is the observed next-day request count per cell, "
        "defined only when consecutive calendar days are present.")
    r.body(
        "**NOAA NCEI Daily Summaries (GHCN-Daily)** (NOAA NCEI, accessed 2026), station "
        "USW00094728 (NY City Central Park), 2022-2024, 1,096 daily rows. Variables used: "
        "precipitation, daily maximum and minimum temperature, average temperature, snowfall, snow "
        "depth, and wind speed. The source average-temperature field was empty for this station, so "
        "average temperature is derived as the mean of observed daily maximum and minimum; five "
        "missing wind-speed days are filled by time interpolation of neighbouring real "
        "observations. A single Central Park station is used as a city-level proxy, a documented "
        "spatial-resolution limitation.")
    r.table_caption("Table 1. Dataset summary.")
    r.table(["Property", "Value"], [
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
    r.h1("4. Methods")
    r.body(
        "We compare four feature sets: internal history (lag and rolling statistics of the "
        "per-cell series), calendar (internal plus deterministic calendar features), weather "
        "(internal plus the seven real weather variables), and calendar + weather (internal plus "
        "calendar plus weather). The corresponding configuration identifiers used in the results "
        "tables are internal_historical, calendar_augmented, weather_augmented, and "
        "calendar_weather_augmented. Full feature definitions are in Appendix A.")
    r.body(
        "Four model families are evaluated: a naive seasonal baseline (trailing 7-day mean), Ridge "
        "regression, a random forest, and gradient boosting. Categorical features (borough, "
        "complaint group) are one-hot encoded; numeric features pass through. Lag and rolling "
        "features use only past observations, with rolling statistics shifted by one day to avoid "
        "same-day or future leakage. Model hyperparameters are listed in Appendix I.")
    r.body(
        "Validation uses a strictly chronological split by date: the earliest 70% of dates for "
        "training (30,240 rows), the next 15% for validation (6,480 rows), and the latest 15% for "
        "test (6,520 rows). The primary metric is MAE; RMSE, MAPE (computed with the denominator "
        "floored at one request, so that near-zero actual counts do not inflate the percentage "
        "error), and R² are also reported. The best configuration by validation MAE is refit "
        "on train + validation before the final test evaluation. Separately, five expanding-window "
        "rolling-origin folds assess stability.")
    r.body(
        "The decision layer is a stylized staffing-allocation simulation. Each day a fixed crew "
        "budget is distributed across cells in proportion to the forecast using a largest-remainder "
        "rule. Each crew handles a fixed number of requests; unmet demand in a cell is the positive "
        "part of actual demand minus allocated capacity; weighted unmet demand assigns higher "
        "weight to Public Safety, Water, and Traffic. Policies driven by each feature set are "
        "compared against an oracle that allocates on the observed (realized) next-day request "
        "volume, which provides an upper bound only. Full assumptions are in Appendix D.")

    # 5. Forecasting Results
    r.h1("5. Forecasting Results")
    r.body(
        "Calendar augmentation improves test MAE for every model. Adding real weather on top of "
        "calendar features further lowers error for the random forest, the selected model family; "
        "for Ridge and gradient boosting it does not improve on calendar alone (Table A3). For the "
        "random forest, MAE falls from 65.282 (internal "
        "history) to 58.082 (calendar); weather alone improves the internal-history model (64.104 "
        "versus 65.282), and calendar + weather is best, at 56.224 for the single-split model fit "
        "on the training set only. Ridge does not benefit from weather (internal 69.219, weather "
        "69.283, calendar + weather 68.915). Figure 1 shows the best test MAE per feature set; the "
        "full per-model results are in Table 2 (selected rows are reported below; the complete "
        "table is in Appendix G).")
    r.table_caption(
        "Table 2 (selected rows). Held-out test MAE by model and feature set; lower is better. "
        "Full 13-row table in Appendix G.")
    r.table(["Model", "Feature set", "Test MAE"], [
        ["naive_seasonal", "naive_seasonal", "71.848"],
        ["random_forest", "internal_historical", "65.282"],
        ["random_forest", "calendar_augmented", "58.082"],
        ["random_forest", "weather_augmented", "64.104"],
        ["random_forest", "calendar_weather_augmented", "56.224"],
        ["gradient_boosting", "calendar_weather_augmented", "61.878"],
        ["ridge", "calendar_weather_augmented", "68.915"],
    ])
    r.body(
        "The selected configuration by validation MAE is the random forest on calendar + weather. "
        "Refit on train + validation and evaluated once on the held-out test set, it attains test "
        "MAE 55.325, RMSE 177.476, MAPE 27.469%, and R² 0.648 - a 23.0% MAE reduction over the "
        "naive seasonal baseline (71.848). The selected-model test MAE of 55.325 (refit on train + "
        "validation) is therefore slightly lower than the 56.224 obtained from the train-only fit "
        "on the single split. Figure 2 shows observed versus predicted city-wide next-day totals "
        "over the test period, which track the overall level and weekly pattern of demand.")
    _fig(r, "1")
    _fig(r, "2")

    # 6. Forecast-to-Decision Simulation
    r.h1("6. Forecast-to-Decision Simulation")
    r.body(
        "At the baseline budget (135 crews, 50 requests per crew, 163 test days), total weighted "
        "unmet demand is 643,324 under the internal-history policy and 631,191 under calendar + "
        "weather, versus an oracle of 597,332: the augmented policy reduces weighted unmet demand "
        "by 1.886% and closes 26.381% of the baseline-to-oracle gap.")
    r.body(
        "Across crew budgets (Table 3, Figure 3) the calendar + weather policy is better than the "
        "baseline in all three settings, but the magnitude grows with capacity: the weighted-unmet "
        "reduction is 0.38% (scarce, 100 crews), 4.32% (moderate, 160), and 14.53% (generous, 220). "
        "The headline contrast - an approximately 11-15% forecast-accuracy gain versus a roughly "
        "1.9% decision-quality gain at the baseline budget - is the central observation: average "
        "accuracy and operational value are not the same, and a scarce budget with demand "
        "concentrated in a few large cells limits how much any forecast can help.")
    r.table_caption(
        "Table 3. Decision sensitivity by crew budget. Stylized simulation; total weighted unmet "
        "demand (lower is better); calendar + weather versus internal history.")
    r.table(
        ["Setting", "Crews", "Internal", "Calendar+Weather", "Oracle", "Reduction", "Oracle gap closed"],
        [
            ["scarce", "100", "941,817", "938,211", "928,491", "0.38%", "27.06%"],
            ["moderate", "160", "454,073", "434,469", "367,553", "4.32%", "22.66%"],
            ["generous", "220", "164,197", "140,346", "50,865", "14.53%", "21.05%"],
        ])
    _fig(r, "3")

    # 7. Robustness Checks
    r.h1("7. Robustness Checks")
    r.body(
        "Five-fold expanding-window rolling-origin validation (Figure 4; full table in Appendix C) "
        "shows calendar augmentation lowering MAE in every fold for every model: mean improvement "
        "15.13% for the random forest, 9.94% for gradient boosting, and 0.94% for Ridge, each in "
        "all 5 of 5 folds. The calendar + weather random forest has the lowest mean fold MAE "
        "(47.497). Segmented analysis (random forest, internal history versus calendar; Appendix G) "
        "shows the improvement holds for all five boroughs (about 8.8% to 18.8%) and all eight "
        "complaint groups (about 8.9% to 25.8%); absolute error concentrates in the highest-volume "
        "segments (Noise, Housing; the Bronx). The calendar improvement is therefore observed "
        "consistently across folds and segments, and is not driven by any single split.")
    _fig(r, "4")

    # 8. Limitations
    r.h1("8. Limitations")
    r.body(
        "The study is predictive and correlational and makes no causal claim. NYC 311 reflects "
        "reporting behaviour, not true incidence (reporting bias), so forecasts predict reported "
        "volume. Weather is a single Central Park station used as a city-level proxy. Borough-level "
        "aggregation hides within-borough variation; the complaint-group mapping is a deterministic "
        "approximation with a residual Other group. No transit or event data is included. The "
        "staffing simulation is a stylized proportional heuristic - it omits crew travel, shifts, "
        "backlog, intra-day timing, and substitution, and it uses no observed dispatch decisions. "
        "Results apply to NYC and 2022-2024 only.")
    r.body(
        "Natural extensions of this work: a non-stylized, agency-grounded decision model with an "
        "empirical service-level realism check; formal forecast-difference testing (for example a "
        "Diebold-Mariano test) with uncertainty intervals; and broader external signals beyond a "
        "single weather station, or cross-city replication.")

    # 9. Conclusion
    r.h1("9. Conclusion")
    r.body(
        "On real NYC 311 data augmented with real NOAA weather, public-signal augmentation improves "
        "next-day service-demand forecasts—calendar features most, across rolling folds, boroughs, "
        "and complaint groups, with real weather adding a further gain for the selected "
        "random-forest model. The "
        "improvement transfers in direction to a stylized staffing allocation but with attenuated, "
        "budget-dependent magnitude. The calendar-augmentation gains are observed consistently "
        "across the evaluated splits, folds, and segments; the decision gains are smaller and "
        "conditional on capacity. This "
        "provides a reproducible evaluation framework for "
        "forecast-to-decision analysis in municipal service operations.")

    # End-matter statements
    r.h1("Reproducibility Statement")
    r.body(
        "All reported values derive from the analysis described in Sections 3-7, implemented in "
        "Python 3.11 with fixed random seeds. The full procedure—weather ingestion, dataset "
        "construction, model training and evaluation, the decision simulation, rolling-origin "
        "validation, per-segment robustness analysis, and the crew-budget sensitivity analysis—is "
        "deterministic and reproducible from the two public data sources described in the "
        "references.")
    r.h1("Data Availability Statement")
    r.body(
        "NYC 311 Service Requests are publicly available through NYC Open Data (Socrata dataset "
        "erm2-nwe9), and NOAA NCEI Daily Summaries (GHCN-Daily) for station USW00094728 are "
        "publicly available through NOAA NCEI; full identifiers and retrieval dates are given in the "
        "references. The study window is 2022-2024. The aggregated daily counts and the derived "
        "weather series used in the analysis are obtained from these public sources following the "
        "procedure described above, and the full modelling dataset is reproducible from them. No "
        "synthetic data are used.")
    r.h1("Code and Materials Availability")
    r.body(
        "The analysis code, the derived summary outputs, and the figures reproduced here are "
        "available in the project repository at "
        "https://github.com/Nassar-Coding/Nassar-Coding.github.io (the "
        "public-signal-service-forecasting directory).")
    r.h1("Ethics Statement")
    r.body(
        "The study uses only public data at an aggregate date × borough × complaint-group level; no "
        "individual-level or personal data are used or produced, the analysis makes no "
        "individual-level decisions, and it is not deployed. Because NYC 311 reflects reporting "
        "behaviour rather than true incidence, and reporting propensity varies across communities "
        "and over time, forecasts of 311 volume describe reported demand rather than underlying "
        "need and should be interpreted accordingly.")

    # Appendix
    r.page_break()
    r.h1("Appendix")
    r.h2("A. Feature and feature-set definitions")
    r.body(
        "Lag features (request_lag_1, request_lag_7) and rolling statistics (rolling_mean_7/14, "
        "rolling_std_7/14) per (borough, complaint group) cell, using only past observations with a "
        "one-day shift. Calendar features: is_weekend, is_holiday, day_of_week, month, quarter, "
        "year, day_of_year, week_of_year, is_month_start, is_month_end. Weather features: "
        "precipitation_mm, temp_max_c, temp_min_c, temp_avg_c, snowfall_mm, snow_depth_mm, "
        "wind_speed_ms. The four feature sets - internal history (internal_historical), calendar "
        "(calendar_augmented), weather (weather_augmented), and calendar + weather "
        "(calendar_weather_augmented) - are listed in Table A1.")
    r.table_caption("Table A1. Feature sets.")
    r.table(["Feature set", "Features"], [
        ["internal_historical", "borough, complaint_group, request_lag_1, request_lag_7, rolling_mean_7, rolling_mean_14, rolling_std_7, rolling_std_14"],
        ["calendar_augmented", "internal_historical + is_weekend, is_holiday, day_of_week, month, quarter, year, day_of_year, week_of_year, is_month_start, is_month_end"],
        ["weather_augmented", "internal_historical + precipitation_mm, temp_max_c, temp_min_c, temp_avg_c, snowfall_mm, snow_depth_mm, wind_speed_ms"],
        ["calendar_weather_augmented", "internal_historical + calendar features + weather features"],
    ])
    r.h2("B. Complaint-group mapping")
    r.body(
        "Raw complaint types are upper-cased and matched against an ordered list of substring "
        "rules; the first matching group wins, and any record matching none is assigned the "
        "residual Other group. The order places Housing before Water so that, for example, "
        "“HEAT/HOT WATER” is classified as Housing rather than Water. The matched substrings per "
        "group are as follows.")
    r.body(
        "**Noise:** NOISE, LOUD. "
        "**Housing:** HEAT/HOT WATER, HEAT, HOT WATER, PLUMBING, PAINT, PLASTER, APPLIANCE, DOOR, "
        "WINDOW, ELECTRIC, FLOORING, STAIRS, ELEVATOR, MOLD, GENERAL CONSTRUCTION, HOUSING, "
        "APARTMENT, UNSANITARY CONDITION, OUTSIDE BUILDING. "
        "**Sanitation:** SANITATION, DIRTY, MISSED COLLECTION, LITTER, GARBAGE, RECYCLING, WASTE, "
        "DUMPING, GRAFFITI, RODENT, OVERFLOWING. "
        "**Street Condition:** STREET CONDITION, STREET LIGHT, POTHOLE, SIDEWALK, CURB, ROAD, "
        "STREET SIGN, TRAFFIC SIGNAL, HIGHWAY. "
        "**Water:** WATER, SEWER, HYDRANT, LEAK, FLOOD, DRAINAGE, CATCH BASIN. "
        "**Traffic:** ILLEGAL PARKING, BLOCKED DRIVEWAY, TRAFFIC, PARKING, ABANDONED VEHICLE, "
        "DERELICT VEHICLE, DRIVEWAY. "
        "**Public Safety:** ILLEGAL FIREWORKS, DRUG, WEAPON, ASSAULT, SAFETY, EMERGENCY, "
        "ENCAMPMENT, HOMELESS, ANIMAL ABUSE, DISORDERLY, URINATING, PANHANDLING.")
    r.h2("C. Chronological split and rolling-origin setup")
    r.body(
        "Chronological 70/15/15 split by date (30,240 / 6,480 / 6,520 rows). Five expanding-window "
        "rolling-origin folds; each fold trains on all dates up to a cut point and tests on the next "
        "block, with no future information in training. Table A2 reports the mean fold MAE that "
        "underlies Figure 4.")
    r.table_caption("Table A2. Rolling-origin validation: random-forest mean fold test MAE by feature set.")
    r.table(["Configuration", "Mean MAE", "Std"], [
        ["naive_seasonal", "61.701", "9.673"],
        ["random_forest internal_historical", "57.027", "8.046"],
        ["random_forest weather_augmented", "56.222", "7.561"],
        ["random_forest calendar_augmented", "48.690", "9.590"],
        ["random_forest calendar_weather_augmented", "47.497", "8.746"],
    ])
    r.h2("D. Decision-simulation assumptions")
    r.body(
        "Each day, a fixed crew budget is allocated across the 40 (borough × complaint-group) cells "
        "in proportion to each cell's forecast, rounded by a largest-remainder rule with a minimum "
        "of zero crews per cell. Each crew serves 50 requests per day, so a cell's allocated "
        "capacity is 50 times its crew count. Unmet demand in a cell is max(0, actual next-day "
        "requests − allocated capacity). Weighted unmet demand multiplies each cell's unmet demand "
        "by a complaint-group weight—Public Safety 2.0, Water 1.5, Traffic 1.5, and 1.0 for Noise, "
        "Sanitation, Street Condition, Housing, and Other—and is summed over cells and test days. "
        "The baseline-budget configuration uses 135 crews over 163 test days. The oracle allocates "
        "using the observed (realized) next-day request volume and provides an upper bound on "
        "achievable performance within this stylized simulation; it is not a forecast. The "
        "simulation uses no observed dispatch decisions.")
    r.h2("E. Crew-budget sensitivity")
    r.body(
        "Three budgets - scarce (100 crews, 5,000 daily capacity), moderate (160 / 8,000), and "
        "generous (220 / 11,000); per-policy results are reported in Table 3.")
    r.h2("F. Weather-data treatment")
    r.body(
        "Single NOAA station (USW00094728) joined to all boroughs by date; temp_avg_c derived from "
        "observed daily maximum and minimum (source average-temperature field empty); five missing "
        "wind-speed days time-interpolated from real neighbours; no synthetic weather. Figure A1 "
        "shows the series.")
    _fig(r, "A1")
    r.h2("G. Full results tables")
    r.body(
        "Table A3 is the complete 13-row model comparison (Figure A2). Table A4 reports per-borough "
        "robustness (Figure A3) and Table A5 per-complaint-group robustness (Figure A4), each "
        "comparing internal history with calendar for the random forest. Figure A6 shows internal "
        "history versus calendar per model; Figure A5 shows a baseline-budget policy comparison "
        "with the oracle.")
    r.table_caption("Table A3. Full model comparison (held-out test).")
    r.table(
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
    r.table_caption("Table A4. Borough robustness (random forest; internal history versus calendar).")
    r.table(
        ["Borough", "Internal MAE", "Calendar MAE", "Improvement (%)"],
        [
            ["Bronx", "120.194", "109.567", "8.84"],
            ["Brooklyn", "76.991", "64.175", "16.65"],
            ["Manhattan", "58.178", "48.078", "17.36"],
            ["Queens", "53.771", "43.675", "18.78"],
            ["Staten Island", "12.766", "11.129", "12.82"],
        ], font_size=9)
    r.table_caption("Table A5. Complaint-group robustness (random forest; internal history versus calendar).")
    r.table(
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
    r.table_caption("Table A6. Limitations and mitigations.")
    r.table(["Limitation", "Mitigation / Scope statement"], [
        ["311 reporting bias", "Documented; target framed as reported volume; no need-based or causal claim"],
        ["Borough-level aggregation", "Granularity stated; within-borough variation not captured"],
        ["Complaint-group mapping coarseness", "Deterministic, documented; residual Other group reported"],
        ["Single-station weather proxy", "Documented spatial-resolution limitation; city-level proxy"],
        ["Derived average temperature", "Mean of observed daily max/min; source field empty; documented"],
        ["No transit or event data", "Scope stated; future work"],
        ["Stylized decision simulation", "Labelled stylized; oracle bound included for context"],
        ["No observed dispatch decisions", "Counterfactual only; no real-dispatch or optimization claim"],
        ["Forecast-versus-decision gap", "Decision metrics reported; transfer attenuated and budget-dependent"],
        ["No causal inference", "No causal claim anywhere"],
        ["NYC-only, 2022-2024", "External-validity limitation stated explicitly"],
    ], font_size=9)
    r.h2("H. Reproducibility")
    r.body(
        "The full analysis is reproducible from the public data sources following the protocol "
        "described in Sections 3-7; see the Reproducibility Statement.")

    r.h2("I. Model configurations")
    r.body(
        "All models are scikit-learn estimators trained with random seed 42. The naive seasonal "
        "baseline predicts the trailing 7-day mean. Ridge regression uses alpha = 1.0. The random "
        "forest uses 200 trees, maximum depth 14, and a minimum of two samples per leaf. Gradient "
        "boosting uses 200 stages, maximum depth 3, and learning rate 0.05. All other "
        "hyperparameters take their scikit-learn defaults; no additional hyperparameter tuning was "
        "performed, and model selection chooses among feature sets by validation MAE.")

    r.h2("Appendix Figures")
    for label in ("A2", "A3", "A4", "A5", "A6"):
        _fig(r, label)

    # References (continue after the appendix figures to avoid a near-empty page)
    r.h1("References")
    r.references(REFS)
