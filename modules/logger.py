from __future__ import annotations

import logging
from pathlib import Path


LOGGER_NAME = "smart_automation_bot"


def get_logger(
    log_file: str | Path = "logs/Activity.log",
    enable_console: bool = False,
) -> logging.Logger:
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

    if enable_console and not any(
        isinstance(handler, logging.StreamHandler)
        and not isinstance(handler, logging.FileHandler)
        for handler in logger.handlers
    ):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))
        logger.addHandler(console_handler)

    return logger


def log_task_start(logger: logging.Logger, task_name: str) -> None:
    logger.info("[%s] started", task_name)


def log_task_success(logger: logging.Logger, task_name: str, details: str) -> None:
    logger.info("[%s] completed | %s", task_name, details)


def log_task_error(logger: logging.Logger, task_name: str, error: Exception) -> None:
    logger.error("[%s] failed | %s", task_name, error)
