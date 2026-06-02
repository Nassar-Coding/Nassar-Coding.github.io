# Table 8: Limitations and Mitigations

Source: `docs/limitations.md` and `research_artifacts/reviewer_risk_register.md`.

| Limitation | Why it matters | Current mitigation / honest framing |
|------------|----------------|-------------------------------------|
| 311 reporting bias | 311 records reporting behaviour, not true incidence; forecasts predict reported volume, not need | Documented; the target is framed as reported volume and no need-based or causal claim is made |
| Borough-level aggregation | Borough x complaint_group x day cells hide within-borough variation | Stated explicitly; granularity is documented |
| Complaint-group mapping coarseness | A deterministic substring mapping into eight groups (plus Other) groups heterogeneous types | Mapping is deterministic and documented; a residual Other group is reported |
| Single-station weather proxy | One Central Park station is joined to every borough by date, so within-city spatial weather variation is not captured | Documented as a spatial-resolution limitation; framed as a city-level proxy |
| Derived average temperature | temp_avg_c is computed from observed TMAX/TMIN because the source TAVG was empty | Documented in the weather source report; no synthetic weather |
| No transit or event data | Only weather is added as an external signal in this version | Scope stated explicitly; framed as future work |
| Stylized decision simulation | Proportional allocation omits crew travel, shifts, backlog, intra-day arrivals, and substitution | Labelled stylized; not real dispatch; oracle bound included |
| No observed dispatch decisions | The decision layer is a counterfactual, not real agency behaviour | Stated; no real-dispatch or real-optimization claim |
| Forecast-versus-decision gap | Accuracy gains do not translate one-to-one into decision value | Decision metrics reported alongside accuracy; transfer is honestly reported as attenuated and budget-dependent |
| No causal inference | The study is correlational and predictive | No causal claim anywhere |
| NYC-only, 2022-2024 | Results are specific to one city and window | External-validity limitation stated explicitly |
| Single chronological split for headline | One split is a point estimate | Mitigated by five-fold rolling-origin validation; formal forecast-difference tests remain future work |
