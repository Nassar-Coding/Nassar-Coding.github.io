"""Locate and validate the real NYC 311 input data for the study window.

This module does not generate synthetic data. In this environment the modelling
input is the pre-aggregated real daily-counts file (produced locally from the
monthly NYC 311 exports with scripts/aggregate_nyc_311_local.py) or a manually
placed record-level export. This command verifies that a valid real input is
present and reports what was found; it fails clearly if none is available.

Direct programmatic download from NYC Open Data is intentionally not performed
here because the full export is very large and, in restricted environments,
outbound access may be blocked. See the README "How to download/build data"
section for the supported real-data acquisition paths.
"""
from __future__ import annotations

from pathlib import Path

from . import config
from .utils import ensure_directories, get_logger

LOGGER = get_logger(__name__)


def locate_real_input() -> tuple[str, Path]:
    """Return (data_mode, path) for the first valid real input, else raise."""
    if config.use_sample_data():
        if config.SAMPLE_DAILY_COUNTS_FILE.exists():
            return config.DATA_MODE_SAMPLE, config.SAMPLE_DAILY_COUNTS_FILE
        raise FileNotFoundError(
            f"Sample mode requested but committed sample is missing: "
            f"{config.SAMPLE_DAILY_COUNTS_FILE}"
        )

    if config.DAILY_COUNTS_FILE.exists():
        return config.DATA_MODE_REAL, config.DAILY_COUNTS_FILE
    if config.MANUAL_RAW_FILE.exists():
        return config.DATA_MODE_REAL, config.MANUAL_RAW_FILE

    raise FileNotFoundError(
        "No real NYC 311 data found. Provide one of the following, then re-run:\n"
        f"  1. Pre-aggregated daily counts at\n     {config.DAILY_COUNTS_FILE}\n"
        "     Produce it locally by running, over the 36 monthly exports:\n"
        "       python scripts/aggregate_nyc_311_local.py --input-dir <folder>\n"
        f"  2. A record-level NYC 311 export at\n     {config.MANUAL_RAW_FILE}\n"
        f"     with columns {config.RAW_REQUIRED_COLUMNS}.\n"
        "Synthetic data is intentionally not generated."
    )


def main() -> None:
    ensure_directories()
    data_mode, path = locate_real_input()
    LOGGER.info(
        "Real NYC 311 input located. data_mode=%s, file=%s",
        data_mode,
        path.relative_to(config.PROJECT_ROOT),
    )
    LOGGER.info(
        "Run `python -m src.build_dataset` to construct the processed dataset."
    )


if __name__ == "__main__":
    main()
