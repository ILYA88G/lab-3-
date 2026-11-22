
import json

from src.catalog import Catalog
from src.models import Book
from src.storage import save_catalog


def test_save_catalog(tmp_path):
    """Check that catalog books are saved to a valid JSON file."""

    catalog = Catalog()

    book = Book(
        item_id="item-7319",
        name="Война и мир",
        category="Роман",
        year=1869,
        author="Лев Толстой",
        pages=1225
    )

    catalog.add(book)

    file_path = tmp_path / "catalog.json"

    save_catalog(catalog, file_path)

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    assert data["format_version"] == 1
    assert len(data["books"]) == 1
    assert data["books"][0]["item_id"] == "item-7319"
    assert data["books"][0]["name"] == "Война и мир"
    assert data["books"][0]["pages"] == 1225
