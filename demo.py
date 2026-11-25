
from pathlib import Path
from tempfile import TemporaryDirectory

from src.models import Book
from src.catalog import Catalog
from src.storage import save_catalog, load_catalog
from src.errors import DuplicateIDError, ItemNotFoundError


def main() -> None:
    """Demonstrate book catalog operations, JSON storage and transactions."""

    # Create an empty catalog
    catalog = Catalog()

    # Create book objects
    book1 = Book(
        item_id="item-7319",
        name="Война и мир",
        category="Роман",
        year=1869,
        author="Лев Толстой",
        pages=1225
    )

    book2 = Book(
        item_id="book-2",
        name="1984",
        category="Антиутопия",
        year=1949,
        author="Джордж Оруэлл",
        pages=328
    )

    book3 = Book(
        item_id="book-3",
        name="Мастер и Маргарита",
        category="Роман",
        year=1967,
        author="Михаил Булгаков",
        pages=480
    )

    # Add books to the catalog
    catalog.add(book1)
    catalog.add(book2)
    catalog.add(book3)

    print("=== БИБЛИОТЕЧНЫЙ КАТАЛОГ ===")
    print("Количество книг:", len(catalog))

    # Iterate over catalog books
    print("\nВсе книги:")
    for book in catalog:
        print(f"{book.item_id}: {book.name}")

    # Search by unique ID
    print("\nПоиск по ID:")
    found_book = catalog.get("item-7319")
    print(found_book.name)

    # Search by category
    print("\nПоиск по категории 'РОМАН':")
    books = catalog.find_by_category("РОМАН")

    if not books:
        print("Книги данной категории отсутствуют")
    else:
        for book in books:
            print(book.name)

    # Search by name
    print("\nПоиск по названию 'война':")
    for book in catalog.find_by_name("война"):
        print(book.name)

    # Check book membership
    print("\nПроверка наличия книги:")

    if "book-2" in catalog:
        print("Книга с ID book-2 присутствует в каталоге")
    else:
        print("Книга с ID book-2 отсутствует в каталоге")

    # Handle duplicate book IDs
    print("\nПопытка добавить дубликат:")
    try:
        catalog.add(book1)
    except DuplicateIDError as error:
        print("Ошибка:", error)

    # Handle missing book IDs
    print("\nПоиск отсутствующей книги:")
    try:
        catalog.get("unknown-id")
    except ItemNotFoundError as error:
        print("Ошибка:", error)

    # Save and load catalog data
    print("\nСохранение и загрузка JSON:")

    with TemporaryDirectory() as directory:
        path = Path(directory) / "catalog.json"

        save_catalog(catalog, path)
        print("Каталог сохранён")

        loaded_catalog = load_catalog(path)
        print("Каталог загружен")
        print("Загружено книг:", len(loaded_catalog))

    # Remove a book
    print("\nУдаление книги:")
    catalog.remove("book-2")
    print("Количество книг после удаления:", len(catalog))

    # Demonstrate transaction rollback
    print("\n=== ДЕМОНСТРАЦИЯ ТРАНЗАКЦИИ ===")
    print("Количество книг до транзакции:", len(catalog))

    try:
        with catalog.transaction():
            catalog.add(book2)
            print("Внутри транзакции добавлена книга:", book2.name)

            # Trigger a duplicate ID error
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
