class CatalogError(Exception):
    """Base exception for catalog errors."""


class InvalidItemError(CatalogError):
    """Raised when book data is invalid."""


class DuplicateIDError(CatalogError):
    """Raised when a book with the same ID already exists."""


class ItemNotFoundError(CatalogError):
    """Raised when a requested book is not found."""


class UnsupportedFormatVersionError(CatalogError):
    """Raised when the JSON format version is unsupported."""


class CorruptedFileError(CatalogError):
    """Raised when catalog file data is corrupted."""
