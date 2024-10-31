from flask import Blueprint, request, jsonify

from rent_book_dao import RentedBookDao, RENTED_BOOK_DB_NAME

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
    :return list of rented books in json format:
    """
    rented_books = rent_book_dao.get_rented_books_by_user_id(user_id)
    return jsonify([rented_book.__dict__ for rented_book in rented_books]), 200


@rent_book_blueprint.route('/create_rent/<int:user_id>,<int:book_id>', methods=['POST'])
def add_rent(user_id, book_id):
    """
    This method adds a rent to the database.
    :return message:
    """
    rent_book_dao.add_rented_book(user_id, book_id)
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


@rent_book_blueprint.route('/update_rent/<int:rent_id>', methods=['PUT'])
def update_rent(rent_id):
    """
    This method updates a rent.
    :param rent_id:
    :return message:
    """
    data = request.get_json()
    updated_rent = rent_book_dao.update_rented_book(rent_id, data['user_id'], data['isbn'], data['rented'])
    if updated_rent:
        return jsonify({'message': 'Rent updated'}), 200
    else:
        return jsonify({'message': 'Rent not found or not updated'}), 404
