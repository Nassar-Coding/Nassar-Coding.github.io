"""Model zoo: baselines, regularized linear, tree ensembles, quantile models.

Every model implements fit(X, y) / predict(X) on numeric matrices.
Categorical identifiers (city, family) are one-hot encoded upstream.

Baselines are first-class citizens and are never dropped from result
tables regardless of how they rank (research constitution).
"""

from __future__ import annotations

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import lightgbm as lgb

QUANTILES = [0.05, 0.25, 0.50, 0.75, 0.95]


class TrailingMeanBaseline:
    """Predicts the trailing 7-day mean (roll_mean_7), Paper 1's naive baseline."""

    name = "naive_trailing7"
    requires = ["roll_mean_7"]

    def fit(self, X, y, feature_names):  # noqa: ARG002 - baseline has no parameters
        self.idx = feature_names.index("roll_mean_7")
        return self

    def predict(self, X):
        return np.asarray(X)[:, self.idx]


class SeasonalNaiveBaseline:
    """Predicts the value observed 7 days before the target day (lag_7 of t+1 = n[t-6+7]=n[t+1-7]).

    With lag_k defined as n[t-k+1], the same weekday as target t+1 is n[t-6],
    i.e. feature lag_7.
    """

    name = "seasonal_naive7"
    requires = ["lag_7"]

    def fit(self, X, y, feature_names):  # noqa: ARG002
        self.idx = feature_names.index("lag_7")
        return self

    def predict(self, X):
        return np.asarray(X)[:, self.idx]


class SklearnModel:
    def __init__(self, name: str, estimator):
        self.name = name
        self.estimator = estimator

    def fit(self, X, y, feature_names):  # noqa: ARG002
        self.estimator.fit(X, y)
        return self

    def predict(self, X):
        return self.estimator.predict(X)


class LightGBMQuantile:
    """A set of monotonically-sorted quantile LightGBM models."""

    def __init__(self, name: str = "lgbm_quantile", quantiles=None, seed: int = 0,
                 n_estimators: int = 600, learning_rate: float = 0.05,
                 num_leaves: int = 63, min_child_samples: int = 30):
        self.name = name
        self.quantiles = quantiles or QUANTILES
        self.params = dict(n_estimators=n_estimators, learning_rate=learning_rate,
                           num_leaves=num_leaves, min_child_samples=min_child_samples,
                           random_state=seed, verbose=-1, n_jobs=-1)

    def fit(self, X, y, feature_names):  # noqa: ARG002
        self.models = {}
        for q in self.quantiles:
            m = lgb.LGBMRegressor(objective="quantile", alpha=q, **self.params)
            m.fit(X, y)
            self.models[q] = m
        return self

    def predict_quantiles(self, X) -> dict:
        preds = {q: self.models[q].predict(X) for q in self.quantiles}
        # enforce non-crossing by cumulative max across sorted quantile levels
        qs = sorted(preds)
        stacked = np.maximum.accumulate(np.vstack([preds[q] for q in qs]), axis=0)
        return {q: stacked[i] for i, q in enumerate(qs)}

    def predict(self, X):
        return self.predict_quantiles(X)[0.50]


def make_point_models(seed: int) -> list:
    return [
        TrailingMeanBaseline(),
        SeasonalNaiveBaseline(),
        SklearnModel("ridge", Pipeline([
            ("scale", StandardScaler()),
            ("ridge", Ridge(alpha=1.0, random_state=seed)),
        ])),
        SklearnModel("random_forest", RandomForestRegressor(
            n_estimators=300, min_samples_leaf=5, max_features=0.6,
            random_state=seed, n_jobs=-1)),
        SklearnModel("lgbm_point", lgb.LGBMRegressor(
            objective="regression_l1", n_estimators=600, learning_rate=0.05,
            num_leaves=63, min_child_samples=30, random_state=seed,
            verbose=-1, n_jobs=-1)),
    ]
