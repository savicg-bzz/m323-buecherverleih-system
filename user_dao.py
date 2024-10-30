"""
This module is responsible for handling user data.
"""
import sqlite3
from bcrypt import hashpw, gensalt, checkpw
from user import User

USER_DB_NAME = 'user.db'


class UserDao:
    """
    This class handles all the database operations related to the user entity.
    """

    def __init__(self, db_file=USER_DB_NAME):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()


    def create_table(self):
        """
            This method creates the table if it does not exist.
        """
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )
            ''')
            self.conn.commit()
        except sqlite3.OperationalError as e:
            print(f'Error creating table: {e}')

    def add_user(self, user):
        """
        This method adds a user to the database.
        """
        try:
            hashed_password = hashpw(user.password.encode('utf-8'), gensalt())
            self.cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                                (user.username, hashed_password))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print('User already exists')

    def get_all_users(self):
        """
        This method returns all the users from the database.
        """
        self.cursor.execute('SELECT * FROM users')
        rows = self.cursor.fetchall()
        users = [User(row[0], row[1], row[2]) for row in rows]
        return users

    def get_one_user(self, user_id):
        """
        This method returns a user from the database.
        """
        self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = self.cursor.fetchone()
        if row:
            return User(row[0], row[1], row[2])
        return None

    def get_user_by_username_and_password(self, username, password):
        """
        This method returns a user from the database.
        """
        self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = self.cursor.fetchone()
        if row and checkpw(password.encode('urf-8'), row[2]):
            return User(row[0], row[1], row[2])
        return None

    def delete_user_by_id_and_password(self, user_id, password):
        """
        This method deletes a user from the database.
        """
        # Fetch the user's hashed password from the database
        self.cursor.execute('SELECT password FROM users WHERE user_id = ?', (user_id,))
        row = self.cursor.fetchone()

        # Check if the user exists and the password is correct
        if row and checkpw(password.encode('utf-8'), row[0]):
            # Delete the user if the password is correct
            self.cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
            if self.cursor.rowcount > 0:
                self.conn.commit()
                return True
        return False

    def update_user(self, updated_user):
        """
        This method updates a user.
        """
        self.cursor.execute('UPDATE users SET username = ?, password = ? WHERE user_id = ?',
                            (updated_user.username, hashpw(updated_user.password, gensalt()),
                             updated_user.user_id))
        if self.cursor.rowcount > 0:
            self.conn.commit()
            return True
        return False

    def close(self):
        """
        This method closes the connection to the database.
        """
        self.conn.close()
