import json
from dataclasses import asdict

import pytest

from src.catalog import Catalog
from src.errors import (
    CorruptedFileError,
    UnsupportedFormatVersionError,
)
from src.models import Book
from src.storage import load_catalog, save_catalog


def make_book(item_id: str = "item-7319") -> Book:
    """Create a valid book for storage tests."""
    return Book(
        item_id=item_id,
        name="Война и мир",
        category="Роман",
        year=1869,
        author="Лев Толстой",
        pages=1225,
    )


def test_save_catalog(tmp_path):
    """Check that catalog data is correctly saved to JSON."""
    catalog = Catalog()
    book = make_book()
    catalog.add(book)

    path = tmp_path / "catalog.json"
    save_catalog(catalog, path)

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    assert data["format_version"] == 1
    assert len(data["books"]) == 1
    assert data["books"][0]["item_id"] == "item-7319"
    assert data["books"][0]["name"] == "Война и мир"
    assert data["books"][0]["pages"] == 1225


def test_round_trip(tmp_path):
    """Check that saving and loading preserves all books."""
    catalog = Catalog()

    book1 = make_book("book-1")
    book2 = make_book("book-2")

    catalog.add(book1)
    catalog.add(book2)

    path = tmp_path / "catalog.json"

    save_catalog(catalog, path)
    loaded_catalog = load_catalog(path)

    assert len(loaded_catalog) == 2
    assert loaded_catalog.get("book-1") == book1
    assert loaded_catalog.get("book-2") == book2
    assert list(loaded_catalog) == list(catalog)


def test_corrupted_json(tmp_path):
    """Check that malformed JSON raises CorruptedFileError."""
    path = tmp_path / "broken.json"

    path.write_text('{"format_version": 1, "books": [', encoding="utf-8")

    with pytest.raises(CorruptedFileError):
        load_catalog(path)


def test_unsupported_version(tmp_path):
    """Check that unsupported JSON versions are rejected."""
    path = tmp_path / "catalog.json"

    path.write_text('{"format_version": 99, "books": []}', encoding="utf-8")

    with pytest.raises(UnsupportedFormatVersionError):
        load_catalog(path)


def test_missing_format_version(tmp_path):
    """Check that a missing format version is rejected."""
    path = tmp_path / "catalog.json"

    path.write_text('{"books": []}', encoding="utf-8")

    with pytest.raises(CorruptedFileError):
        load_catalog(path)


def test_invalid_books_structure(tmp_path):
    """Check that books must be stored as a list."""
    path = tmp_path / "catalog.json"

    path.write_text('{"format_version": 1, "books": "invalid"}', encoding="utf-8")

    with pytest.raises(CorruptedFileError):
        load_catalog(path)


def test_invalid_book_data(tmp_path):
    """Check that invalid book fields are rejected."""
    path = tmp_path / "catalog.json"

    book_data = asdict(make_book())
    book_data["pages"] = -100

    data = {"format_version": 1, "books": [book_data]}

    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(CorruptedFileError):
        load_catalog(path)


def test_duplicate_ids_in_json(tmp_path):
    """Check that duplicate book IDs are rejected during loading."""
    path = tmp_path / "catalog.json"

    book_data = asdict(make_book())

    data = {"format_version": 1, "books": [book_data, book_data]}

    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(CorruptedFileError):
        load_catalog(path)


def test_no_partial_modification(tmp_path):
    """Check that failed loading leaves an existing catalog unchanged."""
    existing_catalog = Catalog()

    original_book = make_book("original-1")
    existing_catalog.add(original_book)

    valid_book = asdict(make_book("book-1"))
    invalid_book = asdict(make_book("book-2"))
    invalid_book["pages"] = -50

    data = {"format_version": 1, "books": [valid_book, invalid_book]}

    path = tmp_path / "catalog.json"

    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(CorruptedFileError):
        load_catalog(path)

    assert len(existing_catalog) == 1
    assert existing_catalog.get("original-1") == original_book
    assert "book-1" not in existing_catalog
    assert "book-2" not in existing_catalog
