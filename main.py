"""
Main file for the project
set up the database and run the app
"""
from flask import Flask, jsonify

# blueprints
from books_blueprint import book_blueprint
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


def generate_data():
    """
    This method generates data for the database.
    """
    # create books
    book_dao = BookDao(BOOK_DB_NAME)
    book_dao.create_table()
    book_dao.add_book(Book(1,'1234', 'Book1', 'Author1'))
    book_dao.add_book(Book(2,'5678', 'Book2', 'Author2'))
    book_dao.add_book(Book(3,'91011', 'Book3', 'Author3'))
    book_dao.close()

    # create users
    user_dao = UserDao(USER_DB_NAME)
    user_dao.create_table()
    user_dao.add_user(User(1, 'admin', 'admin'))
    user_dao.add_user(User(2, 'user', 'user'))
    user_dao.close()

    # create rented books
    rented_book_dao = RentedBookDao(RENTED_BOOK_DB_NAME)
    rented_book_dao.create_table()
    rented_book_dao.add_rented_book(1, '1234')
    rented_book_dao.add_rented_book(2, '5678')
    rented_book_dao.add_rented_book(1, '91011')
    rented_book_dao.close()


if __name__ == '__main__':
    generate_data()
    app.run(debug=True)
