import json
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory

from src.catalog import Catalog
from src.errors import DuplicateIDError, ItemNotFoundError
from src.models import Book
from src.storage import load_catalog, save_catalog


def main() -> None:
    """Demonstrate catalog operations, JSON migration, undo and transactions."""
    # Create an empty catalog.
    catalog = Catalog()

    # Create book objects.
    book1 = Book(
        item_id="item-7319",
        name="Война и мир",
        category="Роман",
        year=1869,
        author="Лев Толстой",
        pages=1225,
    )

    book2 = Book(
        item_id="book-2",
        name="1984",
        category="Антиутопия",
        year=1949,
        author="Джордж Оруэлл",
        pages=328,
    )

    book3 = Book(
        item_id="book-3",
        name="Мастер и Маргарита",
        category="Роман",
        year=1967,
        author="Михаил Булгаков",
        pages=480,
    )

    # Add books to the catalog.
    catalog.add(book1)
    catalog.add(book2)
    catalog.add(book3)

    print("=== БИБЛИОТЕЧНЫЙ КАТАЛОГ ===")
    print("Количество книг:", len(catalog))

    # Iterate over catalog books.
    print("\nВсе книги:")
    for book in catalog:
        print(f"{book.item_id}: {book.name}")

    # Search by unique ID.
    print("\nПоиск по ID:")
    found_book = catalog.get("item-7319")
    print(found_book.name)

    # Search by category using the category index.
    print("\nПоиск по категории 'РОМАН':")
    books = catalog.find_by_category("РОМАН")

    if not books:
        print("Книги данной категории отсутствуют")
    else:
        for book in books:
            print(book.name)

    # Search by a case-insensitive name substring.
    print("\nПоиск по названию 'война':")
    for book in catalog.find_by_name("война"):
        print(book.name)

    # Check book membership.
    print("\nПроверка наличия книги:")

    if "book-2" in catalog:
        print("Книга с ID book-2 присутствует в каталоге")
    else:
        print("Книга с ID book-2 отсутствует в каталоге")

    # Handle duplicate book IDs.
    print("\nПопытка добавить дубликат:")
    try:
        catalog.add(book1)
    except DuplicateIDError as error:
        print("Ошибка:", error)

    # Handle missing book IDs.
    print("\nПоиск отсутствующей книги:")
    try:
        catalog.get("unknown-id")
    except ItemNotFoundError as error:
        print("Ошибка:", error)

    # Save and load catalog data.
    print("\n=== СОХРАНЕНИЕ И ЗАГРУЗКА JSON ===")

    with TemporaryDirectory() as directory:
        path = Path(directory) / "catalog.json"

        save_catalog(catalog, path)
        print("Каталог сохранён в формате JSON версии 2")

        loaded_catalog = load_catalog(path)
        print("Каталог загружен")
        print("Загружено книг:", len(loaded_catalog))

        # Demonstrate migration from JSON format version 1.
        print("\nМиграция JSON версии 1 в версию 2:")

        legacy_path = Path(directory) / "catalog_v1.json"

        legacy_data = {
            "format_version": 1,
            "books": [asdict(book1)],
        }

        with open(legacy_path, "w", encoding="utf-8") as file:
            json.dump(
                legacy_data,
                file,
                ensure_ascii=False,
                indent=4,
            )

        migrated_catalog = load_catalog(legacy_path)

        print("Каталог версии 1 успешно загружен")
        print("Количество книг:", len(migrated_catalog))
        print("Название книги:", migrated_catalog.get("item-7319").name)

    # Demonstrate a read-only catalog view.
    print("\n=== ПРЕДСТАВЛЕНИЕ ТОЛЬКО ДЛЯ ЧТЕНИЯ ===")

    view = catalog.read_only_view()

    print("Количество книг в представлении:", len(view))
    print("Книги в представлении:")

    for book in view:
        print(f"{book.item_id}: {book.name}")

    # Remove a book and show that the view reflects the change.
    print("\nУдаление книги:")
    catalog.remove("book-2")

    print("Количество книг после удаления:", len(catalog))
    print("Количество книг в представлении:", len(view))

    # Demonstrate undo by restoring a removed book.
    print("\n=== ОТМЕНА ОПЕРАЦИИ UNDO ===")

    catalog.remove("book-3")
    print("Количество книг после удаления:", len(catalog))

    catalog.undo()
    print("Количество книг после undo:", len(catalog))
    print("Восстановленная книга:", catalog.get("book-3").name)

    # Demonstrate automatic transaction rollback.
    print("\n=== ДЕМОНСТРАЦИЯ ТРАНЗАКЦИИ ===")
    print("Количество книг до транзакции:", len(catalog))

    try:
        with catalog.transaction():
            catalog.add(book2)
            print("Внутри транзакции добавлена книга:", book2.name)

            # Trigger a duplicate ID error to roll back the transaction.
            catalog.add(book1)

    except DuplicateIDError as error:
        print("Ошибка транзакции:", error)
        print("Все изменения транзакции отменены")

    print("Количество книг после отката:", len(catalog))

    if "book-2" in catalog:
        print("Книга с ID book-2 присутствует в каталоге")
    else:
        print("Книга с ID book-2 отсутствует в каталоге")


if __name__ == "__main__":
    main()
