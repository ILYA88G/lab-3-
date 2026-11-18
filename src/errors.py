class CatalogError(Exception):
    """Basic catalog error"""

class InvalidItemError(CatalogError):
    """Incorrect book data"""

class DuplicateIDError(CatalogError):
    """The existance of book with the same ID"""

class ItemNotFoundError(CatalogError):
    """Specified book wasn't found"""

class UndupportedFormatVersionError(CatalogError):
    """Unsupported JSON file version"""

class CorruptedFileError(CatalogError):
    """Corrupted catalog file"""