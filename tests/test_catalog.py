
import pytest

from src.catalog import Catalog
from src.models import Book
from src.errors import (
    CatalogError,
    DuplicateIDError,
    ItemNotFoundError,
)


def make_book(item_id: str, name: str, category: str) -> Book:
    """Create a valid book for catalog tests."""
    return Book(
        item_id=item_id,
        name=name,
        category=category,
        year=2000,
        author="Test Author",
        pages=300
    )


def test_add_and_get():
    """Check that a book can be added and retrieved by ID."""
    catalog = Catalog()
    book = make_book("book-1", "War and Peace", "Novel")

    catalog.add(book)

    assert catalog.get("book-1") == book
    assert len(catalog) == 1


def test_duplicate_id():
    """Check that adding a duplicate ID raises an error."""
    catalog = Catalog()
    book = make_book("book-1", "War and Peace", "Novel")

    catalog.add(book)

    with pytest.raises(DuplicateIDError):
        catalog.add(book)


def test_remove():
    """Check that removing a book updates the catalog."""
    catalog = Catalog()
    book = make_book("book-1", "War and Peace", "Novel")

    catalog.add(book)
    catalog.remove("book-1")

    assert len(catalog) == 0
    assert "book-1" not in catalog


def test_remove_missing_id():
    """Check that removing a missing book raises an error."""
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
    """Check that search results cannot modify the catalog."""
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


def test_undo_add():
    """Check that undo removes the last added book."""
    catalog = Catalog()
    book = make_book("book-1", "Book A", "Novel")

    catalog.add(book)
    catalog.undo()

    assert len(catalog) == 0
    assert "book-1" not in catalog
    assert catalog.find_by_category("Novel") == []


def test_undo_remove():
    """Check that undo restores a removed book and its position."""
    catalog = Catalog()

    book1 = make_book("book-1", "Book A", "Novel")
    book2 = make_book("book-2", "Book B", "Novel")
    book3 = make_book("book-3", "Book C", "Fantasy")

    catalog.add(book1)
    catalog.add(book2)
    catalog.add(book3)

    catalog.remove("book-1")
    catalog.undo()

    assert list(catalog) == [book1, book2, book3]
    assert catalog.find_by_category("Novel") == [book1, book2]


def test_undo_after_failed_add():
    """Check that a failed insertion is not recorded in undo history."""
    catalog = Catalog()
    book = make_book("book-1", "Book A", "Novel")

    catalog.add(book)

    with pytest.raises(DuplicateIDError):
        catalog.add(book)

    catalog.undo()

    assert len(catalog) == 0


def test_undo_empty_history():
    """Check that undo raises an error when history is empty."""
    catalog = Catalog()

    with pytest.raises(CatalogError):
        catalog.undo()


def test_read_only_view():
    """Check that the view provides read-only catalog operations."""
    catalog = Catalog()
    book = make_book("book-1", "Book A", "Novel")

    catalog.add(book)
    view = catalog.read_only_view()

    assert len(view) == 1
    assert view.get("book-1") == book
    assert view.find_by_category("Novel") == [book]
    assert view.find_by_name("BOOK") == [book]
    assert "book-1" in view
    assert list(view) == [book]

    assert not hasattr(view, "add")
    assert not hasattr(view, "remove")
    assert not hasattr(view, "undo")


def test_read_only_view_updates():
    """Check that the view reflects catalog modifications."""
    catalog = Catalog()
    view = catalog.read_only_view()

    book = make_book("book-1", "Book A", "Novel")
    catalog.add(book)

    assert len(view) == 1
    assert view.get("book-1") == book

    catalog.remove("book-1")

    assert len(view) == 0
    assert "book-1" not in view
    assert view.find_by_category("Novel") == []

    catalog.undo()

    assert len(view) == 1
    assert view.get("book-1") == book


def test_transaction_commit():
    """Check that successful transactions preserve all changes."""
    catalog = Catalog()

    book1 = make_book("book-1", "Book A", "Novel")
    book2 = make_book("book-2", "Book B", "Fantasy")

    with catalog.transaction():
        catalog.add(book1)
        catalog.add(book2)

    assert len(catalog) == 2
    assert list(catalog) == [book1, book2]


def test_transaction_rollback():
    """Check that failed transactions restore the catalog."""
    catalog = Catalog()

    original = make_book("book-1", "Original", "Novel")
    new_book = make_book("book-2", "New Book", "Fantasy")

    catalog.add(original)

    with pytest.raises(DuplicateIDError):
        with catalog.transaction():
            catalog.remove("book-1")
            catalog.add(new_book)
            catalog.add(new_book)

    assert list(catalog) == [original]
    assert catalog.find_by_category("Novel") == [original]
    assert catalog.find_by_category("Fantasy") == []


def test_transaction_preserves_undo_history():
    """Check that rollback preserves previous undo operations."""
    catalog = Catalog()

    book1 = make_book("book-1", "Book A", "Novel")
    book2 = make_book("book-2", "Book B", "Novel")

    catalog.add(book1)

    with pytest.raises(RuntimeError):
        with catalog.transaction():
            catalog.add(book2)
            raise RuntimeError("Test failure")

    assert list(catalog) == [book1]

    catalog.undo()

    assert len(catalog) == 0


def test_undo_inside_transaction():
    """Check that manual undo is prohibited during a transaction."""
    catalog = Catalog()
    book = make_book("book-1", "Book A", "Novel")

    with pytest.raises(CatalogError):
        with catalog.transaction():
            catalog.add(book)
            catalog.undo()

    assert len(catalog) == 0


def test_nested_transactions():
    """Check that nested transactions are rejected."""
    catalog = Catalog()
    book = make_book("book-1", "Book A", "Novel")

    with pytest.raises(CatalogError):
        with catalog.transaction():
            catalog.add(book)

            with catalog.transaction():
                pass

    assert len(catalog) == 0
