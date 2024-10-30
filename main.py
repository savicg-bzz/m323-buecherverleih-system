"""
Main file for the project
set up the database and run the app
"""
from flask import Flask

from book import Book
from books_blueprint import book_blueprint
from book_dao import BookDao, BOOK_DB_NAME

app = Flask(__name__)
app.secret_key = 'supersecret'
app.register_blueprint(book_blueprint)


def generate_data():
    """
    This method generates data for the database.
    :return:
    """
    book_dao = BookDao(BOOK_DB_NAME)
    book_dao.create_table()
    book_dao.add_book(Book('1234', 'Book1', 'Author1'))
    book_dao.add_book(Book('5678', 'Book2', 'Author2'))
    book_dao.add_book(Book('91011', 'Book3', 'Author3'))
    book_dao.close()


if __name__ == '__main__':
    generate_data()
    app.run(debug=True)
