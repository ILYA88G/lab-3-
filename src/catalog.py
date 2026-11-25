from collections.abc import Iterator

from .errors import (
    CatalogError,
    DuplicateIDError,
    InvalidItemError,
    ItemNotFoundError,
)
from .models import Book


class Catalog:
    def __init__(self):
        """Initialize the catalog, category index and undo history."""
        self._items: dict[str, Book] = {}
        self._category_index: dict[str, list[str]] = {}
        self._undo_stack: list[tuple[str, Book, int]] = []

    def add(self, item: Book) -> None:
        """Add a book, update the index and record the operation."""
        if not isinstance(item, Book):
            raise InvalidItemError("Объект должен быть книгой")

        if item.item_id in self._items:
            raise DuplicateIDError(f"Книга с ID {item.item_id} уже существует")

        self._items[item.item_id] = item

        category = item.category.strip().casefold()

        if category not in self._category_index:
            self._category_index[category] = []

        self._category_index[category].append(item.item_id)

        self._undo_stack.append(("add", item, -1))

    def get(self, item_id: str) -> Book:
        """Return a book by its unique ID."""
        if not isinstance(item_id, str) or not item_id.strip():
            raise InvalidItemError("ID должен быть непустой строкой")

        if item_id not in self._items:
            raise ItemNotFoundError(f"Книга с ID {item_id} не найдена")

        return self._items[item_id]

    def remove(self, item_id: str) -> None:
        """Remove a book and record the operation for undo."""
        book = self.get(item_id)

        position = list(self._items).index(item_id)
        category = book.category.strip().casefold()

        del self._items[item_id]

        self._category_index[category].remove(item_id)

        if not self._category_index[category]:
            del self._category_index[category]

        self._undo_stack.append(("remove", book, position))

    def find_by_category(self, category: str) -> list[Book]:
        """Find books using the case-insensitive category index."""
        if not isinstance(category, str):
            raise TypeError("Категория должна быть строкой")

        category = category.strip().casefold()
        book_ids = self._category_index.get(category, [])

        return [self._items[item_id] for item_id in book_ids]

    def find_by_name(self, query: str) -> list[Book]:
        """Find books by a case-insensitive name substring."""
        if not isinstance(query, str):
            raise TypeError("Запрос должен быть строкой")

        query = query.strip().casefold()

        if not query:
            return []

        return [book for book in self._items.values() if query in book.name.casefold()]

    def __len__(self) -> int:
        """Return the number of books in the catalog."""
        return len(self._items)

    def __iter__(self) -> Iterator[Book]:
        """Iterate over books in their insertion order."""
        return iter(self._items.values())

    def __contains__(self, item_id: str) -> bool:
        """Check whether a book with the given ID exists."""
        return isinstance(item_id, str) and item_id in self._items

    def _rebuild_category_index(self) -> None:
        """Rebuild the category index in catalog iteration order."""
        self._category_index.clear()

        for book in self._items.values():
            category = book.category.strip().casefold()

            if category not in self._category_index:
                self._category_index[category] = []

            self._category_index[category].append(book.item_id)

    def undo(self) -> None:
        """Undo the last successful catalog modification."""
        if not self._undo_stack:
            raise CatalogError("Нет операций для отмены")

        operation, book, position = self._undo_stack.pop()

        if operation == "add":
            del self._items[book.item_id]

        elif operation == "remove":
            items = list(self._items.items())
            items.insert(position, (book.item_id, book))
            self._items = dict(items)

        self._rebuild_category_index()

    def read_only_view(self) -> "CatalogReadOnlyView":
        """Return a read-only view of the catalog."""
        return CatalogReadOnlyView(self)


class CatalogReadOnlyView:
    def __init__(self, catalog: Catalog):
        """Create a read-only view of an existing catalog."""
        self.__catalog = catalog

    def get(self, item_id: str) -> Book:
        """Return a book by its unique ID."""
        return self.__catalog.get(item_id)

    def find_by_category(self, category: str) -> list[Book]:
        """Find books matching the specified category."""
        return self.__catalog.find_by_category(category)

    def find_by_name(self, query: str) -> list[Book]:
        """Find books matching the specified name query."""
        return self.__catalog.find_by_name(query)

    def __len__(self) -> int:
        """Return the number of books in the catalog."""
        return len(self.__catalog)

    def __iter__(self) -> Iterator[Book]:
        """Iterate over books in their insertion order."""
        return iter(self.__catalog)

    def __contains__(self, item_id: str) -> bool:
        """Check whether a book ID exists in the catalog."""
        return item_id in self.__catalog
