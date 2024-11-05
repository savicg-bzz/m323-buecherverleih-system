"""
This module contains the data access object for rented books.
"""
# pylint: disable=line-too-long,no-else-return
import sqlite3
from functools import reduce

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

    def query_executor(self):
        """
        Closure to handle SQL query execution with error handling.
        """

        def execute_query(query, params=(), fetch_all=True, expect_change=False):
            try:
                self.cursor.execute(query, params)
                self.conn.commit()
                if expect_change:
                    # Return True if rows were affected, False otherwise
                    return self.cursor.rowcount > 0
                elif fetch_all:
                    return self.cursor.fetchall()
                else:
                    return self.cursor.fetchone()
            except sqlite3.Error as e:
                print(f"Database error: {e}")
                self.conn.rollback()
                return None

        return execute_query

    def create_table(self):
        """
        This method creates the table if it does not exist.
        """
        execute_query = self.query_executor()
        try:
            execute_query('DROP TABLE IF EXISTS rented_books', fetch_all=False)
            execute_query('''
                CREATE TABLE IF NOT EXISTS rented_books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                book_id INTEGER,
                rented BOOLEAN,
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(book_id) REFERENCES books(id)
            )
            ''', fetch_all=False)
        except sqlite3.OperationalError as e:
            print(f'Error creating table: {e}')

    def add_rented_book(self, rented_book):
        """
        This method adds a rented book to the database.
        """
        execute_query = self.query_executor()
        result = execute_query('''
            INSERT INTO rented_books (user_id, book_id, rented) VALUES (?, ?, ?)
        ''', (rented_book.user.user_id, rented_book.book.id, rented_book.rented), fetch_all=False, expect_change=True)
        return result is not None

    def get_all_rented_books(self):
        """
        This method returns all rented books.
        """
        execute_query = self.query_executor()
        rows = execute_query('SELECT * FROM rented_books')
        rented_books = []
        for row in rows:
            user = self.user_dao.get_one_user(row[1])
            book = self.book_dao.get_book_by_id(row[2])
            rented_books.append(RentedBook(id=row[0], user=user, book=book, rented=row[3]))
        return rented_books

    def get_rent_by_id(self, rent_id):
        """
        This method returns a rented book by its id.
        """
        execute_query = self.query_executor()
        row = execute_query('SELECT * FROM rented_books WHERE id = ?', (rent_id,), fetch_all=False)
        if row:
            user = self.user_dao.get_one_user(row[1])
            book = self.book_dao.get_book_by_id(row[2])
            return RentedBook(id=row[0], user=user, book=book, rented=bool(row[3]))
        return None

    def get_rented_books_by_user_id(self, user_id):
        """
        This method returns all the rented books by a user.
        """
        execute_query = self.query_executor()
        rows = execute_query('SELECT * FROM rented_books WHERE user_id = ?', (user_id,))
        return [
            RentedBook(row[0], self.user_dao.get_one_user(row[1]), self.book_dao.get_book_by_id(row[2]), bool(row[3]))
            for row in rows
        ]

    def delete_rented_book(self, rent_id):
        """
        This method deletes a rented book by its id.
        """
        execute_query = self.query_executor()
        return execute_query('DELETE FROM rented_books WHERE id = ?', (rent_id,), fetch_all=False, expect_change=True)

    def delete_rented_book_by_user_id(self, user_id):
        """
        This method deletes a rented book by its user id.
        """
        execute_query = self.query_executor()
        return execute_query('DELETE FROM rented_books WHERE user_id = ?', (user_id,), fetch_all=False,
                             expect_change=True)

    def update_rented_book(self, rented_book):
        """
        This method updates a rented book.
        """
        execute_query = self.query_executor()
        return execute_query('''
            UPDATE rented_books SET rented = ? WHERE id = ?
        ''', (rented_book.rented, rented_book.id), fetch_all=False, expect_change=True)

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
        execute_query = self.query_executor()
        execute_query('DROP TABLE IF EXISTS rented_books', fetch_all=False)

    def count_rented_books_by_user(self):
        """
        This method returns the count of rented books by user.
        :return:
        """
        # Retrieve all rented books
        rented_books = self.get_all_rented_books()

        # Map: Extract user IDs from rented books
        user_ids = list(map(lambda rb: rb.user.user_id, rented_books))

        # Filter: Keep only IDs of users with rented books
        active_rentals = list(filter(lambda uid: uid is not None, user_ids))

        # Reduce: Count occurrences of each user ID (number of rented books per user)
        rental_count_by_user = reduce(lambda acc, uid: {**acc, uid: acc.get(uid, 0) + 1}, active_rentals, {})

        return rental_count_by_user
