"""
Main file for the project
set up the database and run the app
"""
from crypt import methods

from flask import Flask, jsonify

from book import Book
from books_blueprint import book_blueprint
from user_blueprint import user_blueprint
from book_dao import BookDao, BOOK_DB_NAME
from user_dao import UserDao, USER_DB_NAME
from user import User

app = Flask(__name__)
app.secret_key = 'supersecret'
app.register_blueprint(book_blueprint)
app.register_blueprint(user_blueprint)


@app.route('/', methods=['GET'])
def greet():
    return jsonify("Hello")


def generate_data():
    """
    This method generates data for the database.
    """
    book_dao = BookDao(BOOK_DB_NAME)
    book_dao.create_table()
    book_dao.add_book(Book('1234', 'Book1', 'Author1'))
    book_dao.add_book(Book('5678', 'Book2', 'Author2'))
    book_dao.add_book(Book('91011', 'Book3', 'Author3'))
    book_dao.close()

    user_dao = UserDao(USER_DB_NAME)
    user_dao.create_table()  # Ensure the table is created
    user_dao.add_user(User(1, 'admin', 'admin'))
    user_dao.add_user(User(2, 'user', 'user'))
    user_dao.close()


if __name__ == '__main__':
    generate_data()
    app.run(debug=True)
