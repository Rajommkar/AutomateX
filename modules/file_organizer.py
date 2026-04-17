from __future__ import annotations

import shutil
from pathlib import Path


def _resolve_category(file_path: Path, categories: dict[str, list[str]]) -> str:
    extension = file_path.suffix.lower()

    for category, extensions in categories.items():
        if extension in {item.lower() for item in extensions}:
            return category

    return "Others"


def _unique_destination(destination: Path) -> Path:
    if not destination.exists():
        return destination

    counter = 1
    while True:
        candidate = destination.with_name(
            f"{destination.stem}_{counter}{destination.suffix}"
        )
        if not candidate.exists():
            return candidate
        counter += 1


def organize_files(
    source_folder: str | Path,
    categories: dict[str, list[str]],
    logger=None,
) -> dict:
    source_path = Path(source_folder)
    source_path.mkdir(parents=True, exist_ok=True)

    moved_files: list[dict[str, str]] = []
    summary: dict[str, int] = {category: 0 for category in categories}
    summary.setdefault("Others", 0)

    for item in source_path.iterdir():
        if not item.is_file():
            continue

        category = _resolve_category(item, categories)
        target_folder = source_path / category
        target_folder.mkdir(parents=True, exist_ok=True)

        destination = _unique_destination(target_folder / item.name)
        shutil.move(str(item), str(destination))

        summary[category] = summary.get(category, 0) + 1
        moved_files.append(
            {
                "file_name": item.name,
                "category": category,
                "destination": str(destination),
            }
        )

        if logger:
            logger.info("Moved %s to %s", item.name, destination)

    result = {
        "source_folder": str(source_path),
        "total_files_moved": len(moved_files),
        "moved_files": moved_files,
        "summary": summary,
    }

    if logger:
        logger.info(
            "File organization completed for %s. Files moved: %s",
            source_path,
            len(moved_files),
        )

    return result
