"""
This module contains the BookDao class which is responsible for handling all the database
operations related to the book entity.
"""
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

    def get_all_books(self):
        """
        Returns all books from the database.
        :return: list of Book instances
        """
        self.cursor.execute('SELECT * FROM books')
        rows = self.cursor.fetchall()
        return [Book(row[0], row[1], row[2], row[3]) for row in rows]

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
