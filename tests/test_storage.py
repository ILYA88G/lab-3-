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
    """Check that catalog data is saved in format version 2."""
    catalog = Catalog()
    book = make_book()
    catalog.add(book)

    path = tmp_path / "catalog.json"
    save_catalog(catalog, path)

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    assert data["format_version"] == 2
    assert len(data["catalog"]["books"]) == 1

    saved_book = data["catalog"]["books"][0]

    assert saved_book["item_id"] == "item-7319"
    assert saved_book["name"] == "Война и мир"
    assert saved_book["pages"] == 1225


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

    path.write_text(
        '{"format_version": 1, "books": [',
        encoding="utf-8",
    )

    with pytest.raises(CorruptedFileError):
        load_catalog(path)


def test_unsupported_version(tmp_path):
    """Check that unsupported JSON versions are rejected."""
    path = tmp_path / "catalog.json"

    path.write_text(
        '{"format_version": 99, "books": []}',
        encoding="utf-8",
    )

    with pytest.raises(UnsupportedFormatVersionError):
        load_catalog(path)


def test_missing_format_version(tmp_path):
    """Check that a missing format version is rejected."""
    path = tmp_path / "catalog.json"

    path.write_text(
        '{"books": []}',
        encoding="utf-8",
    )

    with pytest.raises(CorruptedFileError):
        load_catalog(path)


def test_invalid_books_structure(tmp_path):
    """Check that books must be stored as a list."""
    path = tmp_path / "catalog.json"

    path.write_text(
        '{"format_version": 1, "books": "invalid"}',
        encoding="utf-8",
    )

    with pytest.raises(CorruptedFileError):
        load_catalog(path)


def test_invalid_book_data(tmp_path):
    """Check that invalid book fields are rejected."""
    path = tmp_path / "catalog.json"

    book_data = asdict(make_book())
    book_data["pages"] = -100

    data = {
        "format_version": 1,
        "books": [book_data],
    }

    path.write_text(
        json.dumps(data, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(CorruptedFileError):
        load_catalog(path)


def test_duplicate_ids_in_json(tmp_path):
    """Check that duplicate book IDs are rejected during loading."""
    path = tmp_path / "catalog.json"

    book_data = asdict(make_book())

    data = {
        "format_version": 1,
        "books": [book_data, book_data],
    }

    path.write_text(
        json.dumps(data, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(CorruptedFileError):
        load_catalog(path)


def test_no_partial_modification(tmp_path):
    """Check that failed loading does not modify an existing catalog."""
    existing_catalog = Catalog()

    original_book = make_book("original-1")
    existing_catalog.add(original_book)

    valid_book = asdict(make_book("book-1"))
    invalid_book = asdict(make_book("book-2"))
    invalid_book["pages"] = -50

    data = {
        "format_version": 1,
        "books": [valid_book, invalid_book],
    }

    path = tmp_path / "catalog.json"

    path.write_text(
        json.dumps(data, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(CorruptedFileError, match="индексом 1"):
        load_catalog(path)

    assert len(existing_catalog) == 1
    assert list(existing_catalog) == [original_book]
    assert existing_catalog.get("original-1") == original_book
    assert "book-1" not in existing_catalog
    assert "book-2" not in existing_catalog


def test_migrate_v1_to_v2(tmp_path):
    """Check that version 1 data can be loaded and saved as version 2."""
    old_path = tmp_path / "old_catalog.json"
    new_path = tmp_path / "new_catalog.json"

    book = make_book("book-1")

    old_data = {
        "format_version": 1,
        "books": [asdict(book)],
    }

    old_path.write_text(
        json.dumps(old_data, ensure_ascii=False),
        encoding="utf-8",
    )

    loaded_catalog = load_catalog(old_path)

    assert loaded_catalog.get("book-1") == book

    save_catalog(loaded_catalog, new_path)

    with open(new_path, "r", encoding="utf-8") as file:
        new_data = json.load(file)

    assert new_data["format_version"] == 2
    assert new_data["catalog"]["books"] == [asdict(book)]


def test_invalid_v2_structure(tmp_path):
    """Check that an invalid version 2 document is rejected."""
    path = tmp_path / "invalid_v2.json"

    data = {
        "format_version": 2,
        "catalog": {
            "books": "invalid",
        },
    }

    path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )

    with pytest.raises(CorruptedFileError):
        load_catalog(path)


def test_invalid_root_type(tmp_path):
    """Check that the JSON root must be an object."""
    path = tmp_path / "invalid_root.json"

    path.write_text(
        "[]",
        encoding="utf-8",
    )

    with pytest.raises(CorruptedFileError):
        load_catalog(path)


def test_boolean_format_version(tmp_path):
    """Check that a boolean is rejected as a format version."""
    path = tmp_path / "boolean_version.json"

    data = {
        "format_version": True,
        "books": [],
    }

    path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )

    with pytest.raises(CorruptedFileError):
        load_catalog(path)
