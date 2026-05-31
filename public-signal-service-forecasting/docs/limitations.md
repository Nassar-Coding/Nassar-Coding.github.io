# Limitations

This real-data baseline is intentionally scoped. The limitations below should be
read alongside every reported result.

## NYC 311 reporting bias

311 records reflect reporting behaviour, not true incidence. Reporting
propensity varies across communities, complaint types, channels, and time.
Forecasts of 311 volume are forecasts of reporting, not of underlying need, and
must not be read as measures of true demand.

## Missing or inconsistent fields

Raw records with unparseable dates or invalid/unspecified boroughs are dropped
during aggregation and counted in the aggregation metadata. Borough and
complaint_type values can be inconsistent across time; the pipeline normalises
boroughs and maps complaint types deterministically but cannot correct
underlying data-entry inconsistencies.

## Complaint-type mapping limitations

The complaint_type to complaint_group mapping is a deterministic, order-
sensitive approximation. It groups heterogeneous complaint types, and a residual
"Other" group absorbs unmatched types. Different reasonable mappings would shift
group-level counts.

## Borough-level aggregation limitations

Aggregating to the borough x complaint_group x day level discards finer
geography (for example community district or ZIP), intra-day timing, and
request-level attributes. Conclusions are limited to this granularity.

## Forecast-versus-decision gap

Improvements in average forecast accuracy do not translate one-to-one into
operational value. The decision simulation is a stylized heuristic and ignores
crew travel, shift constraints, backlog carryover, intra-day arrivals, and
substitution. Decision-quality results describe the simulation, not real
operations.

## No causal inference

The project is correlational and predictive, not causal. It does not identify or
estimate the causal effect of calendar factors, weather, events, or any variable
on service demand. Improvements in forecast or decision metrics must not be
interpreted as causal evidence.

## External validity beyond the study window

Findings are specific to New York City, daily granularity, five boroughs, the
mapped complaint groups, and calendar years 2022-2024. They do not necessarily
generalize to other cities, periods, granularities, or service types.
