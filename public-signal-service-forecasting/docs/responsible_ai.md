# Responsible AI

This project is a local-only research baseline built on real public NYC 311
data. The notes below define its boundaries and the conditions that would have
to be met before any real use.

## Public-data scope

The pipeline uses real public NYC 311 Service Requests aggregated to daily
counts by borough and complaint group for 2022-2024. It uses no external APIs
requiring keys, no cloud services, no databases, and no authentication. The
active data mode is recorded in `data/metadata/data_source_report.json`. CI and
tests use a small committed real-schema sample for speed, clearly labelled
`sample_real_schema`.

## No personal-level data or decision-making

All quantities are aggregate daily counts by borough and complaint group. No
personal data, individual-level records, or personally identifiable information
are used or produced. The project does not make or support decisions about
individuals.

## Aggregation

Working at the borough x complaint_group x day level is a deliberate choice that
avoids fine-grained geography and any re-identification risk, at the cost of
spatial resolution.

## No production dispatch use

The staffing simulation is a stylized, transparent model. It does not represent
real dispatch and must not be used to make real staffing, dispatch, or resource
decisions. It is intended only to study the link between forecast quality and a
simplified decision metric.

## Human oversight

Any future application in a real setting would require human oversight,
domain-expert review, and accountable decision-makers. The models here are
decision-support baselines at most, never autonomous decision-makers.

## Limitations of 311 reporting bias

NYC 311 records reflect who chooses to report and how requests are categorised,
not true underlying incidence. Reporting propensity varies across communities,
complaint types, and time, so counts can encode social and behavioural biases.
Forecasts of 311 volume are forecasts of reporting, not of need, and must not be
interpreted as measures of true demand or used in ways that could compound
existing inequities.

## Requirements before any real deployment

At minimum, real use would require: a fully documented and monitored real-data
ingestion pipeline; bias, fairness, and equity analysis across boroughs and
complaint groups; robustness and drift monitoring on live data; formal
uncertainty quantification; security and privacy review; stakeholder and
community consultation; and independent validation. None of these are claimed to
be satisfied by this repository.
