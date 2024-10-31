from dataclasses import dataclass
from user import User
from book import Book


@dataclass(frozen=True)
class RentedBooks:
    """
    This class represents a rented book.
    """
    id: int
    user: User
    book: Book
    rented: bool = True
