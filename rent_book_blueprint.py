"""
This module contains the blueprint for the rent book API.
"""
import logging

# pylint: disable=no-else-return,broad-exception-caught,logging-fstring-interpolation
from flask import Blueprint, request, jsonify

from book import Book
from rent_book import RentedBook
from rent_book_dao import RentedBookDao, RENTED_BOOK_DB_NAME
from user import User

rent_book_blueprint = Blueprint('rent_book_blueprint', __name__)
rent_book_dao = RentedBookDao(db_file=RENTED_BOOK_DB_NAME)


def serialize_data(data):
    """Convert data recursively to JSON-compatible format."""
    if isinstance(data, dict):
        return {key: serialize_data(value) for key, value in data.items()}
    if isinstance(data, list):
        return [serialize_data(item) for item in data]
    return handle_bytes_and_custom_objects(data)


def handle_bytes_and_custom_objects(data):
    """Helper function for handling bytes and custom objects in data serialization."""
    if isinstance(data, bytes):
        return data.decode('utf-8')
    if hasattr(data, "__dict__"):
        return serialize_data(data.__dict__)
    return data


@rent_book_blueprint.route('/rented_books', methods=['GET'])
def get_all_rented_books():
    """
    This method returns all the rented books from the database.
    :return:
    """
    rented_books = rent_book_dao.get_all_rented_books()
    try:
        rented_books_dict = [serialize_data(book) for book in rented_books]
        return jsonify(rented_books_dict), 200
    except TypeError as e:
        print(f"Serialization error: {e}")  # Log the error to locate problematic data
        return jsonify({"error": "Data serialization issue"}), 500


@rent_book_blueprint.route('/rented_books/<int:rent_id>', methods=['GET'])
def get_rented_book_by_id(rent_id):
    """
    This method returns a rented book by its id.
    :param rent_id:
    :return rented book json format:
    """
    rented_book = rent_book_dao.get_rent_by_id(rent_id)
    if rented_book:
        return jsonify(rented_book.__dict__), 200
    else:
        return jsonify({'message': 'Rented book not found'}), 404


@rent_book_blueprint.route('/rented_books_by_user_id/<int:user_id>', methods=['GET'])
def get_rented_books_by_user_id(user_id):
    """
    This method returns all the rented books by user id.
    :param user_id:
    :return:
    """
    try:
        rented_books = rent_book_dao.get_rented_books_by_user_id(user_id)
        if not rented_books:
            return jsonify({'message': 'Rented book not found'}), 404
        return jsonify([rented_book.__dict__ for rented_book in rented_books]), 200
    except Exception as e:
        logging.error(f"Error fetching rented books for user_id {user_id}: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500


@rent_book_blueprint.route('/create_rent', methods=['POST'])
def add_rent():
    """
    Adds a rent to the database.
    :return message:
    """
    data = request.get_json()

    # Extract user and book data
    user_data = data.get('user')
    book_data = data.get('book')
    rent_id = data.get('id')
    rented_date = data.get('rented')

    # Initialize user and book objects separately
    user = create_user(user_data)
    book = create_book(book_data)

    # Create RentedBook object and add to database
    rented_book = create_rented_book(rent_id, user, book, rented_date)
    rent_book_dao.add_rented_book(rented_book)

    return jsonify({'message': 'Rent created'}), 201


def create_user(user_data):
    """Creates a User object from provided data."""
    return User(**user_data)


def create_book(book_data):
    """Creates a Book object from provided data."""
    return Book(**book_data)


def create_rented_book(rent_id, user, book, rented):
    """Creates a RentedBook object from provided data."""
    return RentedBook(id=rent_id, user=user, book=book, rented=rented)


@rent_book_blueprint.route('/delete_rent/<int:rent_id>', methods=['DELETE'])
def delete_rent(rent_id):
    """
    This method deletes a rent by its id.
    :param rent_id:
    :return message:
    """
    if rent_book_dao.delete_rented_book(rent_id):
        return jsonify({'message': 'Rent deleted'}), 200
    else:
        return jsonify({'message': 'Rent not found or not deleted'}), 404


@rent_book_blueprint.route('/delete_rented_books_by_user_id/<int:user_id>', methods=['DELETE'])
def delete_rented_books_by_user_id(user_id):
    """
    This method deletes all the rented books by user id.
    :param user_id:
    :return message:
    """
    if rent_book_dao.delete_rented_book_by_user_id(user_id):
        return jsonify({'message': 'Rented books deleted'}), 200
    else:
        return jsonify({'message': 'Rented books not found or not deleted'}), 404


@rent_book_blueprint.route('/update_rent', methods=['PUT'])
def update_rent():
    """
    This method updates a rent.
    :return:
    """
    data = request.get_json()
    updated_rent = rent_book_dao.update_rented_book(
        RentedBook(data['id'], data['user'], data['book'], data['rented']))
    if updated_rent:
        return jsonify({'message': 'Rent updated'}), 200
    else:
        return jsonify({'message': 'Rent not found or not updated'}), 404


@rent_book_blueprint.route('/rented_books/count_by_user', methods=['GET'])
def count_rented_books_by_user_route():
    """
    This method returns the count of rented books by user.
    :return:
    """
    # Count rented books by user
    rental_count_by_user = rent_book_dao.count_rented_books_by_user()
    return jsonify(rental_count_by_user)
