import pytest

from src.errors import InvalidItemError
from src.models import Book


def test_valid_book():
    """Check that a valid book can be created"""
    book = Book(
        item_id="item-7319",
        name="War and Peace",
        category="Novel",
        year=1869,
        author="Leo Tolstoy",
        pages=1225,
    )

    assert book.item_id == "item-7319"
    assert book.pages == 1225


def test_empty_name():
    """Check that an empty book name is rejected"""
    with pytest.raises(InvalidItemError):
        Book(
            item_id="book-2",
            name="",
            category="Novel",
            year=1869,
            author="Leo Tolstoy",
            pages=1225,
        )


def test_invalid_year():
    """Check that a negative publication year is rejected"""
    with pytest.raises(InvalidItemError):
        Book(
            item_id="book-3",
            name="War and Peace",
            category="Novel",
            year=-100,
            author="Leo Tolstoy",
            pages=1225,
        )


def test_invalid_pages_type():
    """Check that the page count must be an integer"""
    with pytest.raises(InvalidItemError):
        Book(
            item_id="book-4",
            name="War and Peace",
            category="Novel",
            year=1869,
            author="Leo Tolstoy",
            pages="1225",
        )
