# Phase 2 — Novelty Verification and Literature Audit

All entries below were verified against primary sources (publisher pages,
arXiv, DBLP, Semantic Scholar) during this project on 2026-06-09. Citation
metadata recorded here is what goes into `paper/references.bib`; nothing is
cited from memory alone.

## Anchor literature (verified)

| Work | Venue (verified) | Role here |
|---|---|---|
| Cui, Gallino, Moreno & Zhang (2018), *The Operational Value of Social Media Information* | Production and Operations Management 27(10): 1749–1769 | template: public-signal value for operational forecasts |
| Bertsimas & Kallus (2020), *From Predictive to Prescriptive Analytics* | Management Science 66(3): 1025–1044 | prediction vs prescription distinction |
| Elmachtoub & Grigas (2022), *Smart "Predict, then Optimize"* | Management Science 68(1): 9–26 | decision-aware loss; SPO framework |
| Donti, Amos & Kolter (2017), *Task-based End-to-End Model Learning in Stochastic Optimization* | NeurIPS 2017: 5484–5494 | end-to-end task-based learning |
| Mandi, Kotary, Berden, Mulamba, Bucarey, Guns & Fioretto (2024), *Decision-Focused Learning: Foundations, State of the Art, Benchmark and Future Opportunities* | JAIR 80: 1623–1701, DOI 10.1613/jair.1.15320 | DFL state of the art; benchmark framing |
| Green, Kolesar & Whitt (2007), *Coping with Time-Varying Demand When Setting Staffing Requirements for a Service System* | Production and Operations Management 16(1): 13–39 | staffing under time-varying demand |
| Steinker, Hoberg & Thonemann (2017), *The Value of Weather Information for E-Commerce Operations* | Production and Operations Management 26(10) | weather as a public operational signal |
| Kontokosta & Hong (2021), *Bias in Smart City Governance: How Socio-Spatial Disparities in 311 Complaint Behavior Impact the Fairness of Data-Driven Decisions* | Sustainable Cities and Society 64: 102503 | reporting bias; demand ≠ need |
| Zheng, Capra, Wolfson & Yang (2014), *Urban Computing: Concepts, Methodologies, and Applications* | ACM TIST 5(3), Article 38 | urban computing framing |
| Wang, Geng, Ma, Liu & Zhang (2019), *Cross-City Transfer Learning for Deep Spatio-Temporal Prediction* | IJCAI 2019 (arXiv:1802.00386) | cross-city transfer precedent |
| Salinas, Flunkert, Gasthaus & Januschowski (2020), *DeepAR: Probabilistic Forecasting with Autoregressive Recurrent Networks* | International Journal of Forecasting 36(3): 1181–1191 | global/pooled probabilistic forecasting |
| Gneiting, Balabdaoui & Raftery (2007), *Probabilistic Forecasts, Calibration and Sharpness* | JRSS-B 69(2): 243–268 | calibration/sharpness evaluation |
| Cheng (2022), machine-learning analysis of 311 requests in Miami-Dade County | Growth and Change (Wiley), 2022 | closest 311-volume ML study |

## Closest prior work and the distinct contribution

**Closest clusters found:**

1. *Single-city 311 prediction studies* (e.g., Cheng 2022 Miami-Dade;
   assorted municipal-analytics reports): predict request volumes or
   hotspots in one city; stop at predictive metrics. None couple forecasts
   to an explicit capacity-allocation loss, none compare cities under one
   protocol.
2. *311 equity literature* (Kontokosta & Hong 2021; Kontokosta, Hong &
   Korsberg 2017, arXiv:1710.02452): documents reporting bias; does not do
   forecasting or decision evaluation.
3. *Decision-focused learning / predict-then-optimize* (Elmachtoub &
   Grigas 2022; Donti et al. 2017; Mandi et al. 2024): general methodology
   on synthetic or single-domain benchmarks (energy, inventory, routing).
   The JAIR 2024 benchmark contains no municipal-service-demand task and no
   cross-city replication dimension.
4. *Cross-city transfer in urban computing* (Wang et al. 2019; subsequent
   traffic-transfer literature): transfers representations for prediction
   tasks (traffic, crowd flow); decision quality downstream of the forecast
   is not evaluated.
5. *Paper 1 (Alsharif, 2026, submitted)*: single city (NYC), point
   forecasts only, no backlog dynamics, three crew budgets, proportional
   allocation only.

**Adversarial check.** We searched for any paper that (a) benchmarks
forecast-accuracy-to-decision-value transfer (b) on public 311/municipal
service-request data (c) across multiple cities (d) with uncertainty-aware
allocation. No such paper was found in the forecasting, OR, urban-computing,
or data-mining literature we could access. We did NOT conclude novelty from
the absence of an identical title; the clusters above are each adjacent on
two of the four axes, and the related-work section positions the paper
against each cluster explicitly.

**Remaining distinct contribution.** A reproducible four-city benchmark and
empirical analysis of *when* forecast-accuracy improvements in municipal
service demand convert into capacity-allocation improvements — quantifying
the dependence on capacity regime, backlog dynamics, and uncertainty use,
and testing whether accuracy-based and decision-based model selection agree
across cities. This survives comparison with every cluster above.

## Phase 2 gate

A distinct, falsifiable contribution remains after comparison with the
closest prior work. PASS — with the caveat, recorded honestly, that
literature search coverage was performed through a web-search proxy
(full-text access to some paywalled venues was not available); the
supplement's extended related work lists every search query used.
