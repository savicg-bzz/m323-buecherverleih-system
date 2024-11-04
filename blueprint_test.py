"""
Test all Blueprint classes
"""
# pylint: disable=[line-too-long,redefined-outer-name,duplicate-code]
import pytest
from flask import Flask

from book import Book
from book_dao import BookDao
from books_blueprint import book_blueprint
from rent_book import RentedBook
from rent_book_blueprint import rent_book_blueprint
from rent_book_dao import RentedBookDao
from user import User
from user_blueprint import user_blueprint
from user_dao import UserDao

import tempfile


@pytest.fixture
def app():
    """
    Create a Flask app with all blueprints registered
    :return:
    """
    app = Flask(__name__)
    app.secret_key = 'supersecret'
    app.register_blueprint(user_blueprint)
    app.register_blueprint(book_blueprint)
    app.register_blueprint(rent_book_blueprint)
    yield app


@pytest.fixture
def user_dao():
    """
    Create a UserDao with an in-memory database and initialize the table
    :return:
    """
    # Create UserDao with an in-memory database and initialize the table
    dao = UserDao(":memory:")
    dao.create_table()
    yield dao
    dao.close()


@pytest.fixture
def book_dao():
    """
    Create a BookDao with an in-memory database and initialize the table
    :return:
    """
    # Create BookDao with an in-memory database and initialize the table
    dao = BookDao(":memory:")
    dao.create_table()
    yield dao
    dao.close()


@pytest.fixture
def rented_book_dao():
    """Create a RentedBookDao with a temporary SQLite database."""
    with tempfile.NamedTemporaryFile(suffix='.db') as temp_db:
        db_path = temp_db.name

        # Initialize DAOs with the file-based database path
        rented_book_dao_user_dao = UserDao(db_path)
        rented_book_dao_book_dao = BookDao(db_path)

        rented_book_dao_user_dao.create_table()
        rented_book_dao_book_dao.create_table()

        dao = RentedBookDao(db_path)
        dao.create_table()

        yield dao  # Provide the DAO for testing

        # Clean up resources by closing DAO connections
        rented_book_dao_user_dao.close()
        rented_book_dao_book_dao.close()
        dao.close()


def test_add_user(app):
    """
    Test the add_user route
    """
    with app.test_client() as client:
        response = client.post('/add_user', json={'user_id': 1,
                                                  'username': 'admin', 'password': 'admin'})
        assert response.status_code == 201
        assert response.json == {'message': 'User created'}


def test_get_all_users(app):
    """
    Test the get_all_users route
    """
    with app.test_client() as client:
        response = client.get('/users')
        assert response.status_code == 200
        assert response.json == [] or response.json >= []


def test_get_user(app, user_dao):
    """
    Test the get_user route
    """
    list_of_users = user_dao.get_all_users()
    with app.test_client() as client:
        response = client.get(f'/user_by_id/{len(list_of_users) + 100000}')
        assert response.status_code == 404
        assert response.json == {'message': 'User not found'}

        user_dao.add_user(User(1, 'admin', 'admin'))
        list_of_users = user_dao.get_all_users()
        user_id = len(list_of_users) + 1
        client.get('/add_user', json={'user_id': user_id, 'username': 'user', 'password': 'user'})
        response = client.get(f'/user_by_id/{user_id}')
        assert response.status_code == 200
        print(response.json)
        assert response.json == {'user_id': 2, 'username': 'user', 'password': 'user'}


def test_get_user_by_username(app):
    """
    Test the get_user_by_username route
    """
    with app.test_client() as client:
        response = client.get('/user_by_username/1')
        assert response.status_code == 404
        assert response.json == {'message': 'User not found'}

        json_string = {'user_id': 2, 'username': 'user', 'password': 'user'}
        client.get('/add_user', json=json_string)
        response = client.get(f'/user_by_username/{json_string["username"]}')
        assert response.status_code == 200
        assert response.json == json_string


def test_update_user(app, user_dao):
    """
    Test the update_user route
    """
    with app.test_client() as client:
        user_dao.add_user(User(1, 'admin', 'admin'))
        response = client.put('/update',
                              json={'user_id': 1, 'username': 'admin', 'password': 'admin'})
        assert response.status_code == 200
        assert response.json == {'message': 'User updated'}


def test_add_book(app):
    """
    Test the add_book route
    """
    with app.test_client() as client:
        book = Book(1, '123', 'Test Book', 'Author')
        json_string = book.__dict__
        response = client.post('/add_book', json=json_string)
        assert response.status_code == 201
        assert response.json == {'message': 'Book created'}


def test_get_all_books(app):
    """
    Test the get_all_books route
    """
    with app.test_client() as client:
        response = client.get('/books')
        assert response.status_code == 200
        assert response.json == [] or response.json >= []


def test_get_book_by_isbn(app, book_dao):
    """
    Test the get_book_by_isbn route
    :param app:
    :param book_dao:
    :return:
    """
    list_of_books = book_dao.get_all_books()
    with app.test_client() as client:
        response = client.get(f'/books/{len(list_of_books) + 100000}')
        assert response.status_code == 404
        assert response.json == {'message': 'Book not found'}

        book_dao.add_book(Book(1, '123', 'Test Book', 'Author'))
        response = client.get('/books/1')
        assert response.status_code == 200
        assert response.json == {'id': 1, 'isbn': '123', 'title': 'Test Book', 'author': 'Author'}


def test_update_book(app, book_dao):
    """
    Test the update_book route
    """
    with app.test_client() as client:
        book_dao.add_book(Book(1, '123', 'Test Book', 'Author'))
        client.post('/add_book',
                    json={'id': 1, 'isbn': '123', 'title': 'Test Book', 'author': 'Author'})
        response = client.put('/updateBook',
                              json={'id': 1, 'isbn': '123', 'title': 'Test Book', 'author': 'Author'})
        assert response.status_code == 200
        assert response.json == {'message': 'Book updated'}


def test_add_rented_book(app):
    """
    Test the add_rent route
    """
    with app.test_client() as client:
        user = User(1, 'admin', 'admin')
        book = Book(1, '123', 'Test Book', 'Author')
        rented_book = RentedBook(1, user, book, True)
        json_string = rented_book.__dict__
        response = client.post('/create_rent', json=json_string)
        assert response.status_code == 201
        assert response.json == {'message': 'Rent created'}


def test_get_rented_book_by_id(app, rented_book_dao, book_dao):
    """
    Test the get_rented_book_by_id route
    """
    list_of_rented_books = rented_book_dao.get_all_rented_books()
    with app.test_client() as client:
        response = client.get(f'/rented_books/{len(list_of_rented_books) + 100000}')
        assert response.status_code == 404
        assert response.json == {'message': 'Rented book not found'}

        user = User(1, 'admin', 'admin')
        book = Book(1, '123', 'Test Book', 'Author')
        rented_book = RentedBook(1, user, book, True)
        rented_book_dao.add_rented_book(rented_book)
        book_dao.add_book(book)
        client.post('/add_book', json={'id': 1, 'isbn': '123', 'title': 'Test Book', 'author': 'Author'})
        response = client.get('/rented_books/1')
        assert response.status_code == 200
        assert response.json == {'id': 1, 'user': {'user_id': 1, 'username': 'admin',
                                                   'password': 'admin'},
                                 'book': {'id': 1, 'isbn': '123', 'title': 'Test Book', 'author': 'Author'},
                                 'rented': True}


def test_get_rented_books_by_user_id(app, rented_book_dao):
    """
    Test the get_rented_books_by_user_id route
    """
    with app.test_client() as client:
        list_rented_books = rented_book_dao.get_all_rented_books()
        response = client.get(f'/rented_books_by_user_id/{len(list_rented_books) + 1000000}')
        assert response.status_code == 404
        assert response.json == {'message': 'Rented book not found'}

        user = User(1, 'admin', 'admin')
        book = Book(1, '123', 'Test Book', 'Author')
        rented_book = RentedBook(1, user, book, True)
        rented_book_dao.add_rented_book(rented_book)
        response = client.get(f'/rented_books_by_user_id/{user.user_id}')
        assert response.status_code == 200
        response_json = response.get_json()
        assert any(rented_book['user']['user_id'] == user.user_id for rented_book in response_json)


def test_get_all_rented_books(app):
    """
    Test the get_all_rented_books route
    """
    with app.test_client() as client:
        response = client.get('/rented_books')
        assert response.status_code == 200
        assert response.json == [] or response.json >= []


def test_update_rent(app, rented_book_dao):
    """
    Test the update_rent route
    """
    with app.test_client() as client:
        user = User(1, 'admin', 'admin')
        book = Book(1, '123', 'Test Book', 'Author')
        rented_book = RentedBook(1, user, book, True)
        rented_book_dao.add_rented_book(rented_book)
        response = client.get('/rented_books')
        new_id = len(response.json) + 50
        print(new_id)
        client.post('/create_rent',
                    json={'id': new_id, 'user': {'user_id': 1, 'username': 'admin', 'password': 'admin'},
                          'book': {'id': 1, 'isbn': '123', 'title': 'Test Book', 'author': 'Author'},
                          'rented': True})

        response = client.put('/update_rent',
                              json={'id': 1, 'user': {'user_id': new_id, 'username': 'admin', 'password': 'admin'},
                                    'book': {'id': 1, 'isbn': '123', 'title': 'Test Book', 'author': 'Author'},
                                    'rented': False})
        assert response.status_code == 200
        assert response.json == {'message': 'Rent updated'}


def test_delete_rented_books_by_user_id(app, rented_book_dao):
    """
    Test the delete_rented_books_by_user_id route
    """
    with app.test_client() as client:
        list_rented_books = rented_book_dao.get_all_rented_books()
        response = client.delete(f'/delete_rented_books_by_user_id/{len(list_rented_books) + 1000000}')
        assert response.status_code == 404
        assert response.json == {'message': 'Rented books not found or not deleted'}

        user = User(1, 'admin', 'admin')
        book = Book(1, '123', 'Test Book', 'Author')
        rented_book = RentedBook(1, user, book, True)
        rented_book_dao.add_rented_book(rented_book)
        response = client.delete(f'/delete_rented_books_by_user_id/{user.user_id}')
        assert response.status_code == 200
        assert response.json == {'message': 'Rented books deleted'}


def test_delete_rent(app, rented_book_dao):
    """
    Test the delete_rent route
    """
    with app.test_client() as client:
        list_rented_books = rented_book_dao.get_all_rented_books()
        response = client.delete(f'/delete_rent/{len(list_rented_books) + 1000000}')
        assert response.status_code == 404
        assert response.json == {'message': 'Rent not found or not deleted'}

        user = User(1, 'admin', 'admin')
        book = Book(1, '123', 'Test Book', 'Author')
        rented_book = RentedBook(1, user, book, True)
        rented_book_dao.add_rented_book(rented_book)
        response = client.get('/rented_books')
        last_object = response.json[-1]
        response = client.delete(f'/delete_rent/{last_object["id"]}')
        assert response.status_code == 200
        assert response.json == {'message': 'Rent deleted'}


def test_delete_user(app, user_dao):
    """
    Test the delete_user route
    """
    with app.test_client() as client:
        list_of_users = user_dao.get_all_users()
        response = client.delete(f'/delete_user/{len(list_of_users) + 100000}')
        assert response.status_code == 404
        assert response.json == {'message': 'User not found or not deleted'}

        json_string = {'user_id': 2, 'username': 'user', 'password': 'user'}
        client.get('/add_user', json=json_string)
        response = client.delete(f'/delete_user/{json_string["user_id"]}')
        assert response.status_code == 200
        assert response.json == {'message': 'User deleted'}


def test_delete_book(app, book_dao):
    """
    Test the delete_book route
    """
    with app.test_client() as client:
        list_of_books = book_dao.get_all_books()
        response = client.delete(f'/deleteBook/{len(list_of_books) + 100000}')
        assert response.status_code == 404
        assert response.json == {'message': 'Book not found'}

        book_dao.add_book(Book(1, '123', 'Test Book', 'Author'))
        client.post('/add_book',
                    json={'id': len(list_of_books) + 100, 'isbn': '123', 'title': 'Test Book', 'author': 'Author'})
        response = client.get('/books')
        print(response.json)
        last_object = response.json[-1]
        response = client.delete(f'/deleteBook/{last_object["id"]}')
        assert response.status_code == 200
        assert response.json == {'message': 'Book deleted'}


def test_close(book_dao, user_dao, rented_book_dao):
    """
    Close all DAOs to properly close database connections
    :param book_dao:
    :param user_dao:
    :param rented_book_dao:
    :return:
    """
    book_dao.close()
    user_dao.close()
    rented_book_dao.close()


if __name__ == '__main__':
    pytest.main(['-vv'])
