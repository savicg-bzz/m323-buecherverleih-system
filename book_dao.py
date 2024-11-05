"""
This module contains the BookDao class which is responsible for handling all the database
operations related to the book entity.
"""
# pylint: disable=unnecessary-lambda-assignment
import sqlite3
from book import Book

BOOK_DB_NAME = "books.db"


class BookDao:
    """
    This class handles all the database operations related to the book entity.
    """

    def __init__(self, db_file=BOOK_DB_NAME):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """
        Creates the table if it does not exist.
        """
        self.cursor.execute('''DROP TABLE IF EXISTS books''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                isbn TEXT UNIQUE,
                title TEXT,
                author TEXT
            )
        ''')
        self.conn.commit()

    def add_book(self, book):
        """
        Adds a book to the database.
        :param book: Book instance
        :return: True if added, False if book exists
        """
        try:
            self.cursor.execute(
                'INSERT INTO books (id, isbn, title, author) VALUES (?,?, ?, ?)',
                (book.id, book.isbn, book.title, book.author)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print('Book already exists')
            return False

        # In book_dao.py

        # Existing methods...

    def get_all_books(self, sort_by_author=False, sort_by_title=True):
        """
        Retrieves all books from the database and optionally sorts them by author and/or title.
        :param sort_by_author: Sort books by author if True (optional).
        :param sort_by_title: Sort books by title if True (optional).
        :return: A sorted list of book objects.
        """
        # Retrieve all books from the database
        self.cursor.execute("SELECT id, isbn, title, author FROM books")
        books = [Book(*row) for row in self.cursor.fetchall()]

        # Define multi-var lambda for sorting
        sorting_key = lambda book: (
            book.author if sort_by_author else '',
            book.title if sort_by_title else ''
        )

        # Sort the books based on the sorting_key lambda
        books.sort(key=sorting_key)

        return books

    def get_book_by_id(self, book_id):
        """
        Returns a book by its isbn.
        :param book_id: int
        :return: Book instance or None
        """
        self.cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
        row = self.cursor.fetchone()
        return Book(*row) if row else None

    def delete_book_by_id(self, book_id):
        """
        Deletes a book by its isbn.
        :param book_id: str
        :return: True if deleted, False if not found
        """
        self.cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
        if self.cursor.rowcount > 0:
            self.conn.commit()
            return True
        return False

    # book_dao.py

    def update_book(self, updated_book):
        """
        Updates a book.
        :param updated_book: Book instance with updated data
        :return: True if updated, False if not found
        """
        self.cursor.execute(
            'UPDATE books SET title = ?, author = ?, isbn = ? WHERE id = ?',
            (updated_book.title, updated_book.author, updated_book.isbn, updated_book.id)
        )
        if self.cursor.rowcount > 0:
            self.conn.commit()
            return True
        return False

    def close(self):
        """
        Closes the connection to the database.
        """
        self.conn.close()

    def drop_table(self):
        """
        Drops the table.
        """
        self.cursor.execute('DROP TABLE IF EXISTS books')
        self.conn.commit()
