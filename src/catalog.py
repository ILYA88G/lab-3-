from collections.abc import Iterator

from .errors import DuplicateIDError, InvalidItemError, ItemNotFoundError
from .models import Book


class Catalog:
    def __init__(self):
        """Initialization of books' catalog"""
        self._items: dict[str, Book] = {}
        self._category_index: dict[str, list[str]] = {}

    def add(self, item: Book) -> None:
        """Adds book to catalog in case of unic ID"""
        if not isinstance(item, Book):
            raise InvalidItemError("Объект должен быть книгой")

        if item.item_id in self._items:
            raise DuplicateIDError(f"Книга с ID {item.item_id} уже существует")

        self._items[item.item_id] = item

        category = item.category.strip().casefold()

        if category not in self._category_index:
            self._category_index[category] = []

        self._category_index[category].append(item.item_id)

    def get(self, item_id: str) -> Book:
        """Returns a book by its unique ID"""
        if item_id not in self._items:
            raise ItemNotFoundError(f"Книга с ID {item_id} не найдена")
        return self._items[item_id]

    def remove(self, item_id: str) -> None:
        """Remove a book and update the category index"""
        if item_id not in self._items:
            raise ItemNotFoundError(f"Книга с ID {item_id} не найдена")

        book = self._items[item_id]
        category = book.category.strip().casefold()

        del self._items[item_id]

        self._category_index[category].remove(item_id)

        if not self._category_index[category]:
            del self._category_index[category]

    def find_by_category(self, category: str) -> list[Book]:
        """Finds books"""
        if not isinstance(category, str):
            raise TypeError("Категория должна быть строкой")

        category = category.strip().casefold()

        return [
            book
            for book in self._items.values()
            if book.category.strip().casefold() == category
        ]

    def find_by_name(self, query: str) -> list[Book]:
        """Finds books by a case-insensitive name subtring"""
        if not isinstance(query, str):
            raise TypeError("Запрос должен быть строкой")

        query = query.strip().casefold()

        if not query:
            return []

        return [book for book in self._items.values() if query in book.name.casefold()]

    def __len__(self) -> int:
        """Return the number of books in the catalog"""
        return len(self._items)

    def __iter__(self) -> Iterator[Book]:
        """Iterate over books in their insertion order"""
        return iter(self._items.values())

    def __contains__(self, item_id: str) -> bool:
        """Check whether a book with the given ID exists"""
        return isinstance(item_id, str) and item_id in self._items
