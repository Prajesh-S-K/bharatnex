"""Structured application logging for the Full Stack prototype (Module 5/15).

Configured once at import time in main.py, before the FastAPI app is built, so
it is active even when apps.api.main is imported directly by tests.
"""

from __future__ import annotations

import logging
import os


def configure_logging() -> None:
    level_name = os.getenv("SMART_MINE_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    # force=True: basicConfig() otherwise no-ops once the root logger already has
    # a handler (e.g. a prior call from an earlier test or apps.api.main's own
    # import-time call), which would make configure_logging() uncallable-again.
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=True,
    )
