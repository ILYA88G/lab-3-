import json
from dataclasses import asdict
from pathlib import Path

from .catalog import Catalog


FORMAT_VERSION = 1


def save_catalog(catalog: Catalog, path: str | Path) -> None:
    """Saves catalog books to a JSON file"""

    data = {
        "format_version": FORMAT_VERSION,
        "books": [asdict(book) for book in catalog]
    }
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)