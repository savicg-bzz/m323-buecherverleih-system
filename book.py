"""Book class definition"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Book:
    """
    This class represents a book.
    """
    isbn: str
    title: str
    author: str
