from __future__ import annotations

import json
from pathlib import Path


REQUIRED_PATH_KEYS = {
    "source_folder",
    "reports_folder",
    "log_file",
    "state_file",
}


def load_settings(config_path: str | Path) -> dict:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Settings file not found: {path}")

    with path.open(encoding="utf-8") as file:
        settings = json.load(file)

    _validate_settings(settings)
    return settings


def resolve_paths(base_dir: str | Path, settings: dict) -> dict[str, Path]:
    base_path = Path(base_dir)
    path_settings = settings["paths"]

    resolved_paths = {
        key: base_path / value
        for key, value in path_settings.items()
    }

    _ensure_runtime_directories(resolved_paths)
    return resolved_paths


def _validate_settings(settings: dict) -> None:
    if "paths" not in settings:
        raise ValueError("Missing 'paths' section in settings.json")

    missing_keys = REQUIRED_PATH_KEYS - set(settings["paths"])
    if missing_keys:
        joined_keys = ", ".join(sorted(missing_keys))
        raise ValueError(f"Missing required path settings: {joined_keys}")

    settings.setdefault("app", {})
    settings["app"].setdefault("project_name", "Smart Automation Bot")
    settings["app"].setdefault("report_log_lines", 10)
    settings["app"].setdefault("history_limit", 20)
    settings["app"].setdefault("console_logging", False)
    settings["app"].setdefault("default_email_dry_run", False)

    settings.setdefault("organization", {})
    settings["organization"].setdefault("categories", {})
    settings.setdefault("email", {})


def _ensure_runtime_directories(resolved_paths: dict[str, Path]) -> None:
    resolved_paths["source_folder"].mkdir(parents=True, exist_ok=True)
    resolved_paths["reports_folder"].mkdir(parents=True, exist_ok=True)
    resolved_paths["log_file"].parent.mkdir(parents=True, exist_ok=True)
    resolved_paths["state_file"].parent.mkdir(parents=True, exist_ok=True)
