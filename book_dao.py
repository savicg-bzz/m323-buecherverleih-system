"""
This module contains the BookDAO class which is responsible for handling all the database
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

    def create_table(self):
        """
        creates the table if it does not exist
        :return:
        """
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    isbn TEXT PRIMARY KEY,
                    title TEXT,
                    author TEXT
                )
            ''')
            self.conn.commit()
        except sqlite3.OperationalError:
            print('Table already exists')

    def add_book(self, book):
        """
        This method adds a book to the database.
        :param book:
        """
        try:
            self.cursor.execute('INSERT INTO books (isbn, title, author) VALUES (?, ?, ?)',
                                (book.isbn, book.title, book.author))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print('Book already exists')

    def get_all_books(self):
        """
        This method returns all the books from the database.
        :return:
        """
        self.cursor.execute('SELECT * FROM books')
        rows = self.cursor.fetchall()
        books = [Book(row[0], row[1], row[2]) for row in rows]
        return books

    def get_book_by_isbn(self, isbn):
        """
        This method returns a book by its isbn.
        :param isbn:
        :return book or None:
        """
        self.cursor.execute('SELECT * FROM books WHERE isbn = ?', isbn)
        row = self.cursor.fetchone()
        if row:
            return Book(row[0], row[1], row[2])
        return None

    def delete_book(self, isbn):
        """
        This method deletes a book by its isbn.
        :param isbn:
        :return Boolean:
        """
        self.cursor.execute('DELETE FROM books WHERE isbn = ?', isbn)
        if self.cursor.rowcount > 0:
            self.conn.commit()
            return True
        return False

    def update_book(self, updated_book):
        """
        This method updates a book.
        :param updated_book:
        :return Boolean:
        """
        self.cursor.execute('UPDATE books SET title = ?, author = ? WHERE isbn = ?',
                            (updated_book.title, updated_book.author, updated_book.isbn))
        if self.cursor.rowcount > 0:
            self.conn.commit()
            return True
        return False

    def close(self):
        """
        This method closes the connection to the database.
        :return:
        """
        self.conn.close()
