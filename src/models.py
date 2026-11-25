from dataclasses import dataclass
from datetime import date

from .errors import InvalidItemError


@dataclass(frozen=True)
class Book:
    item_id: str
    name: str
    category: str
    year: int
    author: str
    pages: int

    def __post_init__(self):
        """Validate book fields after initialization."""
        for field in ("item_id", "name", "category", "author"):
            value = getattr(self, field)

            if not isinstance(value, str):
                raise InvalidItemError(f"Поле {field} должно быть строкой")

            if not value.strip():
                raise InvalidItemError(f"Поле {field} не может быть пустой строкой")

        if type(self.year) is not int:
            raise InvalidItemError("Год должен быть целым числом")

        if not 1 <= self.year <= date.today().year:
            raise InvalidItemError("Некорректный год публикации книги")

        if type(self.pages) is not int or self.pages <= 0:
            raise InvalidItemError("Число страниц должно быть натуральным")
