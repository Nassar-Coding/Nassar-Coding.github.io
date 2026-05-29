"""Generate a reproducible synthetic CrowdOps dataset.

This script creates a realistic-but-synthetic operational dataset describing
crowd conditions across venue zones. It is intentionally *not* real client
data -- it is generated locally with a fixed random seed so that anyone can
reproduce the exact same file.

Run from the project root with:

    python -m src.generate_data

Output:
    data/crowd_ops.csv  (>= 2000 rows)
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from src import (
    DATA_PATH,
    EVENT_TYPES,
    RANDOM_SEED,
    REQUIRED_COLUMNS,
    ZONES,
)

# Number of rows to generate. The brief requires at least 2,000 rows; we
# generate a comfortable margin above that threshold.
N_ROWS = 2500

# Nominal capacity per zone (people). These are illustrative venue figures.
ZONE_CAPACITY = {
    "Gate A": 1000,
    "Gate B": 1000,
    "Main Hall": 4000,
    "Parking Area": 1500,
    "Emergency Exit": 600,
    "Food Court": 1200,
    "Service Corridor": 500,
    "Prayer Area": 800,
}

# Multipliers that nudge crowd dynamics depending on the operational context.
EVENT_INTENSITY = {
    "Normal Day": 0.45,
    "Peak Hour": 0.75,
    "Special Event": 0.92,
    "Maintenance Window": 0.35,
    "Weather Disruption": 0.70,
}


def _risk_score(
    density_ratio: float,
    avg_wait_time: float,
    entry_rate: float,
    exit_rate: float,
    event_type: str,
) -> float:
    """Compute a latent (hidden) risk score from operational drivers.

    The score blends the main risk drivers described in the project brief:
    density, waiting time, net inflow (entry vs exit) and event context.
    The score is later thresholded into Low / Medium / High with added noise
    so the classification problem stays realistic and not perfectly separable.
    """
    net_inflow = (entry_rate - exit_rate) / 100.0  # positive -> crowd growing

    score = (
        2.4 * density_ratio
        + 0.045 * avg_wait_time
        + 0.9 * max(net_inflow, 0.0)
    )

    # Higher-risk operational contexts add pressure to the latent score.
    if event_type in ("Special Event", "Weather Disruption"):
        score += 0.55
    elif event_type == "Peak Hour":
        score += 0.25
    elif event_type == "Maintenance Window":
        score += 0.10

    return score


def _score_to_risk(score: float, rng: np.random.Generator) -> str:
    """Convert a latent score into a Low/Medium/High label with noise.

    Controlled Gaussian noise is added before thresholding so the target is
    not a deterministic function of the features -- this keeps model accuracy
    realistic (high but not perfect).
    """
    noisy = score + rng.normal(0.0, 0.28)

    if noisy >= 2.70:
        return "High"
    if noisy >= 1.95:
        return "Medium"
    return "Low"


def generate_dataframe(n_rows: int = N_ROWS, seed: int = RANDOM_SEED) -> pd.DataFrame:
    """Build the synthetic CrowdOps DataFrame.

    Args:
        n_rows: Number of operational records to generate.
        seed: Random seed for full reproducibility.

    Returns:
        A pandas DataFrame matching the project schema (REQUIRED_COLUMNS).
    """
    rng = np.random.default_rng(seed)
    start_time = datetime(2025, 1, 1, 0, 0, 0)

    records: list[dict] = []
    for i in range(n_rows):
        zone = ZONES[rng.integers(0, len(ZONES))]
        event_type = EVENT_TYPES[rng.integers(0, len(EVENT_TYPES))]
        capacity = ZONE_CAPACITY[zone]

        # Timestamp marches forward in 10-minute operational ticks.
        timestamp = start_time + timedelta(minutes=10 * i)
        hour = timestamp.hour
        day_of_week = timestamp.weekday()  # 0 = Monday ... 6 = Sunday

        # Crowd count scales with venue capacity and event intensity, with a
        # diurnal bump around midday/evening operational peaks.
        intensity = EVENT_INTENSITY[event_type]
        diurnal = 0.5 + 0.5 * np.sin((hour - 6) / 24.0 * 2 * np.pi)
        base_fill = intensity * (0.6 + 0.6 * diurnal)
        fill_ratio = float(np.clip(rng.normal(base_fill, 0.12), 0.02, 1.25))
        crowd_count = int(np.clip(fill_ratio * capacity, 0, capacity * 1.3))

        density_ratio = round(crowd_count / capacity, 3)

        # Waiting time grows non-linearly once density climbs.
        avg_wait_time = round(
            float(np.clip(rng.normal(4 + 22 * density_ratio, 3.0), 0.0, 60.0)),
            1,
        )

        # Entry/exit flows (people per 10-min tick). Crowded, high-intensity
        # zones tend to have entry outpacing exit.
        entry_rate = int(np.clip(rng.normal(80 * intensity + 40 * density_ratio, 15), 0, 300))
        exit_bias = 0.85 if event_type in ("Special Event", "Peak Hour") else 1.05
        exit_rate = int(np.clip(rng.normal(entry_rate * exit_bias, 18), 0, 300))

        # Ambient temperature (Celsius) -- weather disruption skews hotter/colder.
        temp_center = 30 if event_type != "Weather Disruption" else 38
        temperature = round(float(np.clip(rng.normal(temp_center, 5.0), 5.0, 50.0)), 1)

        score = _risk_score(density_ratio, avg_wait_time, entry_rate, exit_rate, event_type)
        risk_level = _score_to_risk(score, rng)

        records.append(
            {
                "timestamp": timestamp.isoformat(sep=" "),
                "zone": zone,
                "crowd_count": crowd_count,
                "zone_capacity": capacity,
                "density_ratio": density_ratio,
                "avg_wait_time": avg_wait_time,
                "entry_rate": entry_rate,
                "exit_rate": exit_rate,
                "temperature": temperature,
                "hour": hour,
                "day_of_week": day_of_week,
                "event_type": event_type,
                "risk_level": risk_level,
            }
        )

    frame = pd.DataFrame.from_records(records, columns=REQUIRED_COLUMNS)
    return frame


def save_dataset(path: Path = DATA_PATH, n_rows: int = N_ROWS, seed: int = RANDOM_SEED) -> Path:
    """Generate the dataset and write it to CSV, creating folders as needed."""
    frame = generate_dataframe(n_rows=n_rows, seed=seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    return path


def main() -> None:
    """Entry point for `python -m src.generate_data`."""
    path = save_dataset()
    frame = pd.read_csv(path)
    print(f"[generate_data] Wrote {len(frame):,} rows to {path}")
    print("[generate_data] Risk level distribution:")
    print(frame["risk_level"].value_counts().to_string())


if __name__ == "__main__":
    main()
