"""
Blueprint for user operations.
"""
# pylint: disable=no-else-return
from flask import Blueprint, request, jsonify
from user_dao import UserDao, USER_DB_NAME
from user import User

user_blueprint = Blueprint('user_blueprint', __name__)
user_dao = UserDao(db_file=USER_DB_NAME)


@user_blueprint.route('/users', methods=['GET'])
def get_all_users():
    """
    This method returns all the users from the database.
    :return list of users in json format:
    """
    users = user_dao.get_all_users()
    users_dict = []
    for user in users:
        user_dict = user.__dict__
        if isinstance(user_dict.get('password'), bytes):
            user_dict['password'] = user_dict['password'].decode('utf-8')
        users_dict.append(user_dict)
    return jsonify(users_dict), 200


@user_blueprint.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    This method returns a user by its id.
    :param user_id:
    :return user json format:
    """
    user = user_dao.get_one_user(user_id)

    if user:
        return jsonify(user.__dict__), 200
    else:
        return jsonify({'message': 'User not found'}), 404


@user_blueprint.route('/user_by_id_and_password/<int:user_id>', methods=['GET'])
def get_user_by_id_and_password(user_id):
    """
    This method returns a user by its id and password.
    :param user_id:
    :return user json format:
    """
    user = user_dao.get_user_by_username(user_id)
    if user:
        return jsonify(user.__dict__), 200
    else:
        return jsonify({'message': 'User not found'}), 404


@user_blueprint.route('/createUser', methods=['POST'])
def add_user():
    """
    This method adds a user to the database.
    :return message:
    """
    data = request.get_json()
    user = User(data['user_id'], data['username'], data['password'])
    user_dao.add_user(user)
    return jsonify({'message': 'User created'}), 201


@user_blueprint.route('/deleteUser/<int:user_id>', methods=['DELETE'])
def delete_user_by_id_and_password(user_id):
    """
    This method deletes a user by its id and password.
    :param user_id:
    :return message:
    """
    if user_dao.delete_user_by_id(user_id):
        return jsonify({'message': 'User deleted'}), 200
    else:
        return jsonify({'message': 'User not found or not deleted'}), 404


@user_blueprint.route('/update', methods=['PUT'])
def update_user():
    """
    This method updates a user.
    :return message:
    """
    data = request.get_json()
    updated_user = User(data['user_id'], data['username'], data['password'])

    if user_dao.update_user(updated_user):
        return jsonify({'message': 'User updated'}), 200
    else:
        return jsonify({'message': 'User not found or not updated'}), 404
