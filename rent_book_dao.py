"""
This module contains the data access object for rented books.
"""
import sqlite3

from rent_book import RentedBook
from user_dao import UserDao, USER_DB_NAME
from book_dao import BookDao, BOOK_DB_NAME

RENTED_BOOK_DB_NAME = 'rented_books.db'


class RentedBookDao:
    """
    This class represents a data access object for rented books.
    """

    def __init__(self, db_file=RENTED_BOOK_DB_NAME):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.user_dao = UserDao(USER_DB_NAME)
        self.book_dao = BookDao(BOOK_DB_NAME)

    def create_table(self):
        """
        This method creates the table if it does not exist.
        """
        try:
            self.cursor.execute('''DROP TABLE IF EXISTS rented_books''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS rented_books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                book_id INTEGER,
                rented BOOLEAN,
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(book_id) REFERENCES books(id)
            )
            ''')
            self.conn.commit()
        except sqlite3.OperationalError as e:
            print(f'Error creating table: {e}')

    def add_rented_book(self, rented_book):
        """
        This method adds a rented book to the database.
        :param rented_book:
        :return:
        """
        try:
            self.cursor.execute('''
               INSERT INTO rented_books (user_id, book_id, rented) VALUES (?, ?, ?)
           ''', (rented_book.user.user_id, rented_book.book.id, rented_book.rented))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print('Book already rented')
            return False

    def get_all_rented_books(self):
        """
        This method returns all rented books.
        :return:
        """
        self.cursor.execute('SELECT * FROM rented_books')
        rows = self.cursor.fetchall()
        rented_books = []
        for row in rows:
            user = self.user_dao.get_one_user(row[1])
            book = self.book_dao.get_book_by_id(row[2])
            rented_books.append(RentedBook(id=row[0], user=user, book=book, rented=row[3]))
        return rented_books

    def get_rent_by_id(self, rent_id):
        """
        This method returns a rented book by its id.
        :param rent_id:
        :return:
        """
        self.cursor.execute('SELECT * FROM rented_books WHERE id = ?', (rent_id,))
        row = self.cursor.fetchone()
        if row:
            user = self.user_dao.get_one_user(row[1])  # Fetch User instance based on user_id
            book = self.book_dao.get_book_by_id(row[2])  # Fetch Book instance based on isbn
            return RentedBook(id=row[0], user=user, book=book, rented=bool(row[3]))
        return None

    def get_rented_books_by_user_id(self, user_id):
        """
        This method returns all the rented books by a user.
        """
        self.cursor.execute('SELECT * FROM rented_books WHERE user_id = ?', (user_id,))
        rows = self.cursor.fetchall()
        rented_books = [
            RentedBook(
                row[0],
                self.user_dao.get_one_user(row[1]),
                self.book_dao.get_book_by_id(row[2]),
                bool(row[3])
            ) for row in rows
        ]
        return rented_books

    def delete_rented_book(self, rent_id):
        """
        This method deletes a rented book by its id.
        """
        self.cursor.execute('DELETE FROM rented_books WHERE id = ?', (rent_id,))
        if self.cursor.rowcount > 0:
            self.conn.commit()
            return True
        return False

    def delete_rented_book_by_user_id(self, user_id):
        """
        This method deletes a rented book by its user id.
        """
        self.cursor.execute('DELETE FROM rented_books WHERE user_id = ?', (user_id,))
        if self.cursor.rowcount > 0:
            self.conn.commit()
            return True
        return False

    def update_rented_book(self, rented_book):
        """
        This method updates a rented book.
        :param rented_book:
        :return:
        """
        self.cursor.execute('''
               UPDATE rented_books SET rented = ? WHERE id = ?
           ''', (rented_book.rented, rented_book.id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def close(self):
        """
        This method closes the connection to the database.
        """
        self.conn.close()
        self.user_dao.close()
        self.book_dao.close()

    def drop_table(self):
        """
        This method drops the table.
        """
        self.cursor.execute('DROP TABLE IF EXISTS rented_books')
        self.conn.commit()
