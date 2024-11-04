"""
Blueprint for books
"""
import logging

# pylint: disable=no-else-return
from flask import Blueprint, jsonify, request
from book_dao import BookDao, BOOK_DB_NAME
from book import Book

book_blueprint = Blueprint('book_blueprint', __name__)
book_dao = BookDao(BOOK_DB_NAME)


# Higher-order function for executing an operation and handling responses
# Configure logging
logging.basicConfig(level=logging.DEBUG)

def execute_and_respond(operation):
    try:
        result, status_code = operation()
        return jsonify(result), status_code
    except Exception as e:
        logging.error("Error in operation: %s", e)
        return jsonify({'error': str(e)}), 500


@book_blueprint.route('/books', methods=['GET'])
def get_all_books():
    """This method returns all the books from the database."""
    return execute_and_respond(lambda: ([book.__dict__ for book in book_dao.get_all_books()], 200))



@book_blueprint.route('/books/<int:isbn>', methods=['GET'])
def get_book_by_isbn(isbn):
    """This method returns a book by its ISBN."""

    def operation():
        book = book_dao.get_book_by_id(isbn)
        if book is None:
            # Return 404 if the book is not found
            return {'message': 'Book not found'}, 404
        return book.__dict__, 200

    # Use execute_and_respond to handle the operation and response
    return execute_and_respond(operation)


@book_blueprint.route('/add_book', methods=['POST'])
def add_book():
    """This method adds a book to the database."""
    data = request.get_json()
    new_book = Book(data['id'], data['isbn'], data['title'], data['author'])
    existing_book = book_dao.get_book_by_id(data['id'])
    if existing_book:
        return jsonify({'message': 'Book already exists'}), 409
    # Ensure the lambda returns a tuple (result, status_code)
    return execute_and_respond(lambda: ({'message': 'Book created'}, 201) if book_dao.add_book(new_book) else ({'message': 'Book creation failed'}, 500))



@book_blueprint.route('/deleteBook/<int:isbn>', methods=['DELETE'])
def delete_book(isbn):
    """This method deletes a book by its ISBN."""
    if not book_dao.get_book_by_id(isbn):
        return jsonify({'message': 'Book not found'}), 404
    # Return a tuple (result, status_code) explicitly
    return execute_and_respond(lambda: ({'message': 'Book deleted'}, 200) if book_dao.delete_book_by_id(isbn) else ({'message': 'Deletion failed'}, 500))



@book_blueprint.route('/updateBook', methods=['PUT'])
def update_book():
    """This method updates a book."""
    data = request.get_json()
    updated_book = Book(data['id'], data['isbn'], data['title'], data['author'])
    if not book_dao.get_book_by_id(data['id']):
        return jsonify({'message': 'Book not found'}), 404
    # Return a tuple (result, status_code) explicitly
    return execute_and_respond(lambda: ({'message': 'Book updated'}, 200) if book_dao.update_book(updated_book) else ({'message': 'Update failed'}, 500))

