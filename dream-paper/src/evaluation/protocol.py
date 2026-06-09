"""Chronological evaluation protocol shared by all experiments.

Within each city: the earliest 70% of distinct days form TRAIN, the next
15% VALIDATION, and the final 15% an untouched TEST window evaluated once.
Five expanding-window rolling-origin folds are carved out of TRAIN+VAL for
stability analysis. Splits are by calendar day, never by row, so no
(city, family) cell ever straddles a boundary on the same day.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def chrono_split(days: pd.Series, train_frac: float = 0.70, val_frac: float = 0.15):
    uniq = np.array(sorted(pd.unique(days)))
    n = len(uniq)
    t_end = uniq[int(n * train_frac) - 1]
    v_end = uniq[int(n * (train_frac + val_frac)) - 1]
    return t_end, v_end


def split_masks(days: pd.Series, t_end, v_end):
    train = days <= t_end
    val = (days > t_end) & (days <= v_end)
    test = days > v_end
    return train, val, test


def rolling_origin_folds(days: pd.Series, n_folds: int = 5, test_frac: float = 0.15):
    """Expanding-window folds over the pre-test period.

    Yields (train_mask, eval_mask) tuples. Fold k trains on the first
    (k+1)/(n_folds+1) share of pre-test days and evaluates on the next block.
    """
    uniq = np.array(sorted(pd.unique(days)))
    n = len(uniq)
    pre = uniq[: int(n * (1 - test_frac))]
    m = len(pre)
    block = m // (n_folds + 1)
    folds = []
    for k in range(1, n_folds + 1):
        train_end = pre[k * block - 1]
        eval_end = pre[min((k + 1) * block, m) - 1]
        folds.append(((days <= train_end),
                      (days > train_end) & (days <= eval_end)))
    return folds


def mae(y, p):
    return float(np.mean(np.abs(np.asarray(y) - np.asarray(p))))


def rmse(y, p):
    return float(np.sqrt(np.mean((np.asarray(y) - np.asarray(p)) ** 2)))


def mape_floored(y, p, floor: float = 1.0):
    y = np.asarray(y, dtype=float)
    return float(np.mean(np.abs(y - np.asarray(p)) / np.maximum(y, floor)) * 100)


def pinball(y, q_preds: dict):
    y = np.asarray(y, dtype=float)
    losses = []
    for q, p in q_preds.items():
        d = y - np.asarray(p)
        losses.append(np.mean(np.maximum(q * d, (q - 1) * d)))
    return float(np.mean(losses))


def coverage(y, lo, hi):
    y = np.asarray(y, dtype=float)
    return float(np.mean((y >= np.asarray(lo)) & (y <= np.asarray(hi))))


def paired_block_bootstrap_pvalue(err_a, err_b, days: pd.Series, n_boot: int = 2000,
                                  seed: int = 0):
    """Two-sided p-value for H0: mean(|err_a|) == mean(|err_b|).

    Resamples whole days (block bootstrap over the daily mean error
    differential) to respect cross-sectional correlation within a day.
    """
    df = pd.DataFrame({"d": np.abs(np.asarray(err_a)) - np.abs(np.asarray(err_b)),
                       "day": np.asarray(days)})
    daily = df.groupby("day")["d"].mean().to_numpy()
    rng = np.random.default_rng(seed)
    n = len(daily)
    boots = np.array([daily[rng.integers(0, n, n)].mean() for _ in range(n_boot)])
    obs = daily.mean()
    # shift bootstrap distribution to the null
    p = float(np.mean(np.abs(boots - obs) >= np.abs(obs)))
    return obs, max(p, 1.0 / n_boot)
