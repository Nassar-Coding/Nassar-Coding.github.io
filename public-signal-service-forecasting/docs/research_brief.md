# Research Brief

## Research question

Do public external signals such as weather, calendar features, holidays, and
operational context improve service-request volume forecasts, and do those
forecast improvements translate into better staffing allocation decisions?

## Motivation from operations management

Municipal and service organizations must allocate finite crews and resources
against demand that is uncertain and time-varying. Forecasting daily
service-request volume is a classic operations-management problem at the
intersection of demand forecasting and capacity allocation. A central question
in technology-and-operations-management and information-systems research is
whether *external* data signals (here, public weather, calendar, and event-like
proxies) add value beyond an organization's own internal operational history.

Two distinct questions follow:

1. **Predictive question.** Do public signals reduce forecast error relative to
   an internal-only baseline that uses only the organization's own lagged
   request history and calendar structure?
2. **Decision question.** If forecasts improve, does that improvement propagate
   into measurably better operational decisions, such as staffing or dispatch
   allocation?

These questions are related but not identical. A reduction in forecast error
does not automatically imply better decisions, because decision quality depends
on the loss structure of the allocation problem, not only on average accuracy.
This distinction motivates pairing the forecasting study with an explicit
decision simulation.

## Baseline vs augmented comparison

The study compares two feature sets under identical models and an identical
chronological validation protocol:

- **Internal-only baseline:** borough, complaint group, calendar features, and
  lag/rolling features derived from past request volume.
- **Public-signal augmented:** all internal features plus weather-like signals
  (temperature, precipitation, wind, severe-weather indicator) and an
  event-intensity proxy.

Each feature set is trained with a naive seasonal baseline, Ridge regression, a
random forest, and gradient boosting. The primary selection metric is mean
absolute error (MAE) on a held-out, chronologically later test set.

## Decision-link logic

The decision extension is a stylized staffing-allocation simulation. Each day a
fixed crew budget is distributed across borough x complaint-group cells in
proportion to forecasted next-day demand. Three policies are compared:

- a **baseline policy** driven by the internal-only forecast,
- an **augmented policy** driven by the public-signal forecast,
- an **oracle policy** driven by true next-day demand, used only as an upper
  reference bound.

Decision quality is measured with weighted unmet demand (weighting higher-stakes
complaint groups more heavily), average service shortfall, high-demand coverage
rate, and allocation efficiency. The percent reduction in weighted unmet demand
from baseline to augmented policy is the headline decision metric, while the
oracle bound indicates how much room for improvement exists in principle.

## What this repository can and cannot show

It **can**:

- quantify whether augmenting with public signals reduces forecast error under a
  leakage-controlled chronological protocol,
- demonstrate a transparent, reproducible link from forecast quality to a stylized
  operational decision metric,
- provide a clean, testable baseline implementation for further study.

It **cannot**:

- prove a causal effect of public signals on real service demand,
- represent real agency dispatch, real crew logistics, or real operational value,
- generalize beyond the modelled one-city, daily, borough x complaint-group scope,
- substitute for a validated, peer-reviewed study. When run with the synthetic
  fallback, results characterize the modelled data-generating process rather than
  real-world demand.

## How this could evolve into a paper

Natural extensions include: replacing the synthetic fallback with a fully
documented real-data ingestion and join pipeline; adding probabilistic and
hierarchical forecasting; formalizing the allocation problem as a constrained
optimization with service-level constraints; conducting ablations over signal
groups; and adding statistical tests for forecast-accuracy differences (for
example, Diebold-Mariano) and for decision-quality differences across policies.
