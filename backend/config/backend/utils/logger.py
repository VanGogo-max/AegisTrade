"""
AegisTrade — Logger
"""
from __future__ import annotations
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    from backend.config.config import LOG_LEVEL, LOG_FILE

    effective_level = level or LOG_LEVEL
    log = logging.getLogger(name)

    if log.handlers:
        return log

    log.setLevel(effective_level)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    log.addHandler(ch)

    try:
        Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        fh = logging.handlers.RotatingFileHandler(
            LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3
        )
        fh.setFormatter(fmt)
        log.addHandler(fh)
    except Exception:
        pass

    log.propagate = False
    return log
