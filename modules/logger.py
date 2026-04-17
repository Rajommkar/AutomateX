from __future__ import annotations

import logging
from pathlib import Path


LOGGER_NAME = "smart_automation_bot"


def get_logger(log_file: str | Path = "logs/Activity.log") -> logging.Logger:
    """Create or reuse the project logger with a file handler."""
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    resolved_log = log_path.resolve()
    has_file_handler = any(
        isinstance(handler, logging.FileHandler)
        and Path(handler.baseFilename).resolve() == resolved_log
        for handler in logger.handlers
    )

    if not has_file_handler:
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        )
        logger.addHandler(handler)

    return logger
