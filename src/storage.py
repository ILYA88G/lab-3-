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

FORMAT_VERSION = 1


def save_catalog(catalog: Catalog, path: str | Path) -> None:
    """Save catalog books to a JSON file."""
    data = {
        "format_version": FORMAT_VERSION,
        "books": [asdict(book) for book in catalog],
    }

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_catalog(path: str | Path) -> Catalog:
    """Load and validate a catalog from a JSON file."""

    # Read the JSON file
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

    except (json.JSONDecodeError, UnicodeError) as error:
        raise CorruptedFileError("Не удалось прочитать содержимое JSON") from error

    # Validate the document structure
    if not isinstance(data, dict):
        raise CorruptedFileError("Корневой элемент JSON должен быть словарём")

    # Check the format version
    version = data.get("format_version")

    if type(version) is not int:
        raise CorruptedFileError("Отсутствует или некорректна версия формата")

    if version != FORMAT_VERSION:
        raise UnsupportedFormatVersionError(
            f"Версия формата {version} не поддерживается"
        )

    # Check the list of books
    books_data = data.get("books")

    if not isinstance(books_data, list):
        raise CorruptedFileError("Поле books должно содержать список")

    # Create a temporary catalog
    catalog = Catalog()

    for index, book_data in enumerate(books_data):
        if not isinstance(book_data, dict):
            raise CorruptedFileError(f"Книга с индексом {index} должна быть словарём")

        try:
            book = Book(**book_data)
            catalog.add(book)

        except (TypeError, InvalidItemError, DuplicateIDError) as error:
            raise CorruptedFileError(
                f"Некорректные данные книги с индексом {index}: {error}"
            ) from error

    return catalog
