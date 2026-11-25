from dataclasses import FrozenInstanceError

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


def test_whitespace_item_id():
    """Check that an ID containing only spaces is rejected."""
    with pytest.raises(InvalidItemError):
        Book(
            item_id="   ",
            name="War and Peace",
            category="Novel",
            year=1869,
            author="Leo Tolstoy",
            pages=1225,
        )


def test_invalid_author_type():
    """Check that the author must be a non-empty string."""
    with pytest.raises(InvalidItemError):
        Book(
            item_id="book-5",
            name="War and Peace",
            category="Novel",
            year=1869,
            author=123,
            pages=1225,
        )


def test_boolean_year():
    """Check that boolean values are rejected as publication years."""
    with pytest.raises(InvalidItemError):
        Book(
            item_id="book-6",
            name="War and Peace",
            category="Novel",
            year=True,
            author="Leo Tolstoy",
            pages=1225,
        )


def test_zero_pages():
    """Check that the page count must be positive."""
    with pytest.raises(InvalidItemError):
        Book(
            item_id="book-7",
            name="War and Peace",
            category="Novel",
            year=1869,
            author="Leo Tolstoy",
            pages=0,
        )


def test_book_is_immutable():
    """Check that book fields cannot be changed after creation."""
    book = Book(
        item_id="book-8",
        name="War and Peace",
        category="Novel",
        year=1869,
        author="Leo Tolstoy",
        pages=1225,
    )

    with pytest.raises(FrozenInstanceError):
        book.name = "New Name"
