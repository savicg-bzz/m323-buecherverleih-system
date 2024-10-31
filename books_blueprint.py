"""
Blueprint for books
"""
# pylint: disable=no-else-return
from flask import Blueprint, jsonify, request
from book_dao import BookDao, BOOK_DB_NAME
from book import Book

book_blueprint = Blueprint('book_blueprint', __name__)
book_dao = BookDao(BOOK_DB_NAME)


@book_blueprint.route('/books', methods=['GET'])
def get_all_books():
    """
    This method returns all the books from the database.
    :return list of books in json format:
    """
    books = book_dao.get_all_books()
    return jsonify([book.__dict__ for book in books]), 200


@book_blueprint.route('/books/<int:isbn>', methods=['GET'])
def get_book_by_isbn(isbn):
    """
    This method returns a book by its isbn.
    :param isbn:
    :return book json format:
    """
    book = book_dao.get_book_by_id(isbn)
    if book:
        return jsonify(book.__dict__), 200
    else:
        return jsonify({'message': 'Book not found'}), 404


@book_blueprint.route('/createBook', methods=['POST'])
def add_book():
    """
    This method adds a book to the database.
    :return message:
    """
    data = request.get_json()
    new_book = Book(data['id'],data['isbn'], data['title'], data['author'])
    book_dao.add_book(new_book)
    return jsonify({'message': 'Book created'}), 201


@book_blueprint.route('/deleteBook/<int:isbn>', methods=['DELETE'])
def delete_book(isbn):
    """
    This method deletes a book by its isbn.
    :param isbn:
    :return message:
    """
    if book_dao.delete_book_by_id(isbn):
        return jsonify({'message': 'Book deleted'}), 200
    else:
        return jsonify({'message': 'Book not found or not deleted'}), 404


@book_blueprint.route('/updateBook', methods=['PUT'])
def update_book():
    """
    This method updates a book.
    :return message:
    """
    data = request.get_json()
    updated_book = Book(data['id'],data['isbn'], data['title'], data['author'])
    if book_dao.update_book(updated_book):
        return jsonify({'message': 'Book updated'}), 200
    else:
        return jsonify({'message': 'Book not found or not updated'}), 404
