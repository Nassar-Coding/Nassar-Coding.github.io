"""Shared runtime utilities: project paths, config loading, deterministic seeding."""

from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "configs"
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_INTERIM = PROJECT_ROOT / "data" / "interim"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
OUTPUTS = PROJECT_ROOT / "outputs"

GLOBAL_SEED = 20260609


def set_seed(seed: int = GLOBAL_SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)


def load_config(name: str) -> dict:
    return yaml.safe_load((CONFIG_DIR / name).read_text())


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str))


def us_federal_holidays(year: int) -> set:
    """Observed U.S. federal holidays, computed deterministically (no lookup service).

    Includes the observed-day shift rule: Saturday holidays observed Friday,
    Sunday holidays observed Monday. Juneteenth included from 2021.
    """
    import datetime as dt

    def nth_weekday(month: int, weekday: int, n: int) -> dt.date:
        d = dt.date(year, month, 1)
        offset = (weekday - d.weekday()) % 7
        return d + dt.timedelta(days=offset + 7 * (n - 1))

    def last_weekday(month: int, weekday: int) -> dt.date:
        if month == 12:
            d = dt.date(year, 12, 31)
        else:
            d = dt.date(year, month + 1, 1) - dt.timedelta(days=1)
        return d - dt.timedelta(days=(d.weekday() - weekday) % 7)

    def observed(d: dt.date) -> dt.date:
        if d.weekday() == 5:
            return d - dt.timedelta(days=1)
        if d.weekday() == 6:
            return d + dt.timedelta(days=1)
        return d

    fixed = [dt.date(year, 1, 1), dt.date(year, 7, 4), dt.date(year, 11, 11),
             dt.date(year, 12, 25)]
    if year >= 2021:
        fixed.append(dt.date(year, 6, 19))
    floating = [
        nth_weekday(1, 0, 3),    # MLK Day
        nth_weekday(2, 0, 3),    # Presidents Day
        last_weekday(5, 0),      # Memorial Day
        nth_weekday(9, 0, 1),    # Labor Day
        nth_weekday(10, 0, 2),   # Columbus Day
        nth_weekday(11, 3, 4),   # Thanksgiving
    ]
    return {observed(d) for d in fixed} | set(floating)
