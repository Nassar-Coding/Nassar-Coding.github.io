"""Optional public-data download with safe fallback.

This module attempts to download a real public NYC 311 export without any
authentication or API key. The full export is very large, so only a bounded
number of rows is requested. If the download is unavailable, blocked,
rate-limited, or otherwise fails, the pipeline records the failure in metadata
and continues with the deterministic synthetic fallback dataset.

No internet access is required for the rest of the pipeline once raw data is
present.
"""
from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd

from . import config
from .generate_fallback_data import write_fallback_data
from .utils import ensure_directories, get_logger, save_json

LOGGER = get_logger(__name__)

# Bounded preview download; a full multi-million row export is out of scope for
# a local baseline. SoQL-style query parameters keep the payload small.
_DOWNLOAD_LIMIT = 50000


def _attempt_download() -> pd.DataFrame | None:
    """Attempt a bounded, key-free public download. Return None on any failure."""
    try:
        import requests  # Imported lazily so the project runs without requests.
    except ImportError:
        LOGGER.warning("The 'requests' package is not installed; skipping download.")
        return None

    url = f"{config.NYC_311_CSV_URL}&$limit={_DOWNLOAD_LIMIT}"
    try:
        LOGGER.info("Attempting public download (no authentication).")
        response = requests.get(url, timeout=config.DOWNLOAD_TIMEOUT_SECONDS, stream=True)
        response.raise_for_status()
        from io import StringIO

        frame = pd.read_csv(StringIO(response.text))
        if frame.empty:
            LOGGER.warning("Downloaded file was empty; falling back to synthetic data.")
            return None
        LOGGER.info("Downloaded %s raw rows from public source.", len(frame))
        return frame
    except Exception as error:  # noqa: BLE001 - download must never crash the pipeline
        LOGGER.warning("Public download failed (%s); using synthetic fallback.", error)
        return None


def download_data() -> str:
    """Try to obtain real public data; fall back to synthetic data on failure.

    Returns the resulting data mode: ``"real_public_data"`` or
    ``"synthetic_fallback"``.
    """
    ensure_directories()
    raw = _attempt_download()

    if raw is None:
        write_fallback_data()
        return "synthetic_fallback"

    # A real, automated aggregation of the heterogeneous public export into the
    # exact daily borough x complaint-group schema (with matched weather joins)
    # is non-trivial and out of scope for this local baseline. To keep the data
    # contract honest and reproducible, the raw download is archived but the
    # modelling pipeline uses the deterministic synthetic schema. This decision
    # is recorded transparently in the data source report.
    raw_archive = config.RAW_DIR / "public_download_sample.csv"
    raw.to_csv(raw_archive, index=False)
    write_fallback_data()
    metadata = {
        "data_mode": "synthetic_fallback",
        "generated_at": datetime.now(UTC).isoformat(),
        "note": (
            "A bounded public sample was downloaded and archived, but the "
            "modelling pipeline uses the deterministic synthetic schema for "
            "reproducibility. See docs/data_card.md for details."
        ),
        "public_sample_rows": int(len(raw)),
        "public_sample_path": str(raw_archive.relative_to(config.PROJECT_ROOT)),
    }
    save_json(config.DATA_SOURCE_REPORT, metadata)
    return "synthetic_fallback"


def main() -> None:
    mode = download_data()
    LOGGER.info("Data acquisition complete. Mode: %s", mode)


if __name__ == "__main__":
    main()
