# Responsible AI

This project is a local-only research baseline. The notes below define its
boundaries and the conditions that would have to be met before any real use.

## Local-only scope

The repository runs entirely on a local machine. It uses no external APIs
requiring keys, no cloud services, no databases, no authentication, and no
geocoding. It is not deployed, not integrated with any city or agency system,
and not production-hardened.

## Public and synthetic data boundaries

The pipeline uses public-style data and, by default, a clearly labelled
deterministic synthetic fallback. The active data mode is always recorded in
`data/metadata/data_source_report.json`. Synthetic results characterize the
modelled data-generating process, not real-world demand, and must not be
presented as evidence about real operations.

## No personal data

No personal data, individual-level records, or personally identifiable
information are used or produced. All quantities are aggregate daily counts and
synthetic or public-style signals.

## No production dispatch use

The staffing simulation is a stylized, transparent model. It does not represent
real dispatch and must not be used to make real staffing, dispatch, or resource
decisions. It is intended only to study the link between forecast quality and a
simplified decision metric.

## Human oversight

Any future application in a real setting would require human oversight,
domain-expert review, and accountable decision-makers. The models here are
decision-support baselines at most, never autonomous decision-makers, and they do
not replace human judgement.

## Risk of over-interpreting synthetic results

Because the default mode is synthetic, there is a risk of over-interpreting the
numbers. Reported improvements reflect the assumed generating process and the
specific modelling choices. They are not estimates of real-world effect sizes and
do not establish causality.

## Requirements before real deployment

At minimum, real use would require: a fully documented real-data ingestion and
validation pipeline; bias, fairness, and equity analysis across boroughs and
complaint groups; robustness and drift monitoring on live data; formal
uncertainty quantification; security and privacy review; stakeholder and
community consultation; and independent validation. None of these are claimed to
be satisfied by this repository.
