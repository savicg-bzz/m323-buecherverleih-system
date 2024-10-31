"""
This module contains the blueprint for the rent book API.
"""
import logging

# pylint: disable=no-else-return
from flask import Blueprint, request, jsonify

from book import Book
from rent_book import RentedBook
from rent_book_dao import RentedBookDao, RENTED_BOOK_DB_NAME
from user import User

rent_book_blueprint = Blueprint('rent_book_blueprint', __name__)
rent_book_dao = RentedBookDao(db_file=RENTED_BOOK_DB_NAME)


def serialize_data(data):
    """Recursively convert all data to JSON-compatible format, decoding bytes as needed."""
    if isinstance(data, dict):
        return {key: serialize_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_data(item) for item in data]
    elif isinstance(data, bytes):
        return data.decode('utf-8')
    elif hasattr(data, "__dict__"):  # For custom objects
        return serialize_data(data.__dict__)
    else:
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
    This method adds a rent to the database.
    :return message:
    """
    data = request.get_json()
    user = User(**data['user'])
    book = Book(**data['book'])
    rented_book = RentedBook(id=data['id'], user=user, book=book, rented=data['rented'])
    rent_book_dao.add_rented_book(rented_book)
    return jsonify({'message': 'Rent created'}), 201


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
    data = request.get_json()
    updated_rent = rent_book_dao.update_rented_book(
        RentedBook(data['id'], data['user'], data['book'], data['rented']))
    if updated_rent:
        return jsonify({'message': 'Rent updated'}), 200
    else:
        return jsonify({'message': 'Rent not found or not updated'}), 404
