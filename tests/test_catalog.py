import pytest

from src.catalog import Catalog
from src.errors import DuplicateIDError, ItemNotFoundError
from src.models import Book


def make_book(item_id: str, name: str, category: str) -> Book:
    """Create a valid book with the specified ID, name and category."""
    return Book(
        item_id=item_id,
        name=name,
        category=category,
        year=2000,
        author="Test Author",
        pages=300,
    )


def test_add_and_get():
    """Check that a book can be added and retrieved by ID"""
    catalog = Catalog()

    book = Book(
        item_id="book-1",
        name="War and Peace",
        category="Novel",
        year=1869,
        author="Leo Tolstoy",
        pages=1225,
    )

    catalog.add(book)

    assert catalog.get("book-1") == book
    assert len(catalog) == 1


def test_duplicate_id():
    """Check that adding a duplicate ID raises an error"""
    catalog = Catalog()

    book = Book(
        item_id="book-1",
        name="War and Peace",
        category="Novel",
        year=1869,
        author="Leo Tolstoy",
        pages=1225,
    )

    catalog.add(book)

    with pytest.raises(DuplicateIDError):
        catalog.add(book)


def test_remove():
    """Check that removing a book updates the catalog"""
    catalog = Catalog()

    book = Book(
        item_id="book-1",
        name="War and Peace",
        category="Novel",
        year=1869,
        author="Leo Tolstoy",
        pages=1225,
    )

    catalog.add(book)
    catalog.remove("book-1")

    assert len(catalog) == 0
    assert "book-1" not in catalog


def test_remove_missing_id():
    """Check that removing a missing book raises an error"""
    catalog = Catalog()

    with pytest.raises(ItemNotFoundError):
        catalog.remove("book-999")


def test_find_by_category():
    """Check case-insensitive category search."""
    catalog = Catalog()

    book1 = make_book("book-1", "Book A", "Novel")
    book2 = make_book("book-2", "Book B", "Fantasy")

    catalog.add(book1)
    catalog.add(book2)

    assert catalog.find_by_category("NOVEL") == [book1]
    assert catalog.find_by_category("Unknown") == []


def test_find_by_name():
    """Check case-insensitive substring search by book name."""
    catalog = Catalog()

    book = make_book("book-1", "War and Peace", "Novel")
    catalog.add(book)

    assert catalog.find_by_name("WAR") == [book]
    assert catalog.find_by_name("peace") == [book]
    assert catalog.find_by_name("Unknown") == []
    assert catalog.find_by_name("") == []


def test_iteration_order():
    """Check that books are iterated in insertion order."""
    catalog = Catalog()

    book1 = make_book("book-1", "Book A", "Novel")
    book2 = make_book("book-2", "Book B", "Fantasy")

    catalog.add(book1)
    catalog.add(book2)

    assert list(catalog) == [book1, book2]


def test_contains():
    """Check membership by book ID."""
    catalog = Catalog()

    book = make_book("book-1", "Book A", "Novel")
    catalog.add(book)

    assert "book-1" in catalog
    assert "book-999" not in catalog


def test_search_returns_independent_list():
    """Check that modifying search results does not change the catalog."""
    catalog = Catalog()

    book = make_book("book-1", "Book A", "Novel")
    catalog.add(book)

    results = catalog.find_by_category("Novel")
    results.clear()

    assert len(catalog) == 1
    assert catalog.get("book-1") == book


def test_get_missing_id():
    """Check that requesting a missing book raises an error."""
    catalog = Catalog()

    with pytest.raises(ItemNotFoundError):
        catalog.get("book-999")


def test_category_index_after_add():
    """Check that added books appear in the category index."""
    catalog = Catalog()

    book1 = make_book("book-1", "Book A", "Novel")
    book2 = make_book("book-2", "Book B", "Novel")

    catalog.add(book1)
    catalog.add(book2)

    assert catalog.find_by_category("NOVEL") == [book1, book2]


def test_category_index_after_remove():
    """Check that removed books disappear from the category index."""
    catalog = Catalog()

    book1 = make_book("book-1", "Book A", "Novel")
    book2 = make_book("book-2", "Book B", "Novel")

    catalog.add(book1)
    catalog.add(book2)

    catalog.remove("book-1")

    assert catalog.find_by_category("Novel") == [book2]

    catalog.remove("book-2")

    assert catalog.find_by_category("Novel") == []


def test_category_index_after_duplicate():
    """Check that duplicate insertion does not change the index."""
    catalog = Catalog()

    book = make_book("book-1", "Book A", "Novel")
    catalog.add(book)

    with pytest.raises(DuplicateIDError):
        catalog.add(book)

    assert catalog.find_by_category("Novel") == [book]
    assert len(catalog) == 1
