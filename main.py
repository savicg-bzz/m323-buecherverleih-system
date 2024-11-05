"""
Main file for the project
set up the database and run the app
"""

from flask import Flask, jsonify

# blueprints
from books_blueprint import book_blueprint
from rent_book import RentedBook
from user_blueprint import user_blueprint
from rent_book_blueprint import rent_book_blueprint
# dao
from book_dao import BookDao, BOOK_DB_NAME
from user_dao import UserDao, USER_DB_NAME
from rent_book_dao import RentedBookDao, RENTED_BOOK_DB_NAME
# models
from book import Book
from user import User

app = Flask(__name__)
app.secret_key = 'supersecret'
app.register_blueprint(book_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(rent_book_blueprint)


@app.route('/', methods=['GET'])
def greet():
    """
    This method returns a greeting message.
    :return:
    """
    return jsonify("Hello", "myfriend")


def setup_books(book_dao):
    book_dao.create_table()
    books = [
        Book(1, '1234', 'Book1', 'Author1'),
        Book(2, '5678', 'Book2', 'Author2')
    ]
    for book in books:
        book_dao.add_book(book)
    book_dao.close()


def setup_users(user_dao):
    user_dao.create_table()
    users = [
        User(1, 'admin', 'admin'),
        User(2, 'user', 'user')
    ]
    for user in users:
        user_dao.add_user(user)
    user_dao.close()


def setup_rented_books(rented_book_dao):
    rented_book_dao.create_table()
    rented_books = [
        RentedBook(1, User(1, 'admin', 'admin'), Book(1, '1234', 'Book1', 'Author1'), True),
        RentedBook(2, User(2, 'user', 'user'), Book(2, '5678', 'Book2', 'Author2'), False)
    ]
    for rented_book in rented_books:
        rented_book_dao.add_rented_book(rented_book)
    rented_book_dao.close()


def generate_data():
    setup_books(BookDao(BOOK_DB_NAME))
    setup_users(UserDao(USER_DB_NAME))
    setup_rented_books(RentedBookDao(RENTED_BOOK_DB_NAME))


if __name__ == '__main__':
    generate_data()
    app.run(debug=True)
