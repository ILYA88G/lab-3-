import json
from dataclasses import asdict
from pathlib import Path

from .catalog import Catalog
from .errors import (
    CorruptedFileError,
    DuplicateIDError,
    InvalidItemError,
    UnsupportedFormatVersionError,
)
from .models import Book

FORMAT_VERSION = 2
LEGACY_FORMAT_VERSION = 1


def save_catalog(catalog: Catalog, path: str | Path) -> None:
    """Save catalog books to a JSON file using format version 2."""
    data = {
        "format_version": FORMAT_VERSION,
        "catalog": {"books": [asdict(book) for book in catalog]},
    }

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def migrate_v1_to_v2(data: dict) -> dict:
    """Convert a version 1 document to the version 2 structure."""
    books_data = data.get("books")

    if not isinstance(books_data, list):
        raise CorruptedFileError("Поле books должно содержать список")

    return {
        "format_version": FORMAT_VERSION,
        "catalog": {"books": books_data},
    }


def load_catalog(path: str | Path) -> Catalog:
    """Load a catalog, migrating version 1 data when necessary."""
    # Read the JSON file.
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

    except (json.JSONDecodeError, UnicodeError) as error:
        raise CorruptedFileError("Не удалось прочитать содержимое JSON") from error

    # Validate the root document.
    if not isinstance(data, dict):
        raise CorruptedFileError("Корневой элемент JSON должен быть словарём")

    version = data.get("format_version")

    if type(version) is not int:
        raise CorruptedFileError("Отсутствует или некорректна версия формата")

    # Reject unsupported versions.
    if version not in (LEGACY_FORMAT_VERSION, FORMAT_VERSION):
        raise UnsupportedFormatVersionError(
            f"Версия формата {version} не поддерживается"
        )

    # Migrate the old document structure.
    if version == LEGACY_FORMAT_VERSION:
        data = migrate_v1_to_v2(data)

    # Validate the version 2 structure.
    catalog_data = data.get("catalog")

    if not isinstance(catalog_data, dict):
        raise CorruptedFileError("Поле catalog должно быть словарём")

    books_data = catalog_data.get("books")

    if not isinstance(books_data, list):
        raise CorruptedFileError("Поле books должно содержать список")

    # Build a new catalog without changing existing data.
    catalog = Catalog()

    for index, book_data in enumerate(books_data):
        if not isinstance(book_data, dict):
            raise CorruptedFileError(f"Книга с индексом {index} должна быть словарём")

        try:
            book = Book(**book_data)
            catalog.add(book)

        except (
            TypeError,
            InvalidItemError,
            DuplicateIDError,
        ) as error:
            raise CorruptedFileError(
                f"Некорректные данные книги с индексом {index}: {error}"
            ) from error

    return catalog
