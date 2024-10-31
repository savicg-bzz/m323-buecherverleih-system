import pytest
from book_dao import BookDao
from user_dao import UserDao
from rent_book_dao import RentedBookDao
from book import Book
from user import User
from rent_book import RentedBooks


@pytest.fixture
def user_dao():
    # Create UserDao with an in-memory database and initialize the table
    dao = UserDao(":memory:")
    dao.create_table()  # Ensure the users table is created
    yield dao
    dao.close()


@pytest.fixture
def book_dao():
    # Create BookDao with an in-memory database and initialize the table
    dao = BookDao(":memory:")
    dao.create_table()  # Ensure the books table is created
    yield dao
    dao.close()


@pytest.fixture
def rented_book_dao():
    # Create RentedBookDao with an in-memory database and initialize all tables
    user_dao = UserDao(":memory:")
    book_dao = BookDao(":memory:")
    user_dao.create_table()
    book_dao.create_table()

    dao = RentedBookDao(":memory:")
    dao.create_table()  # Ensure the rented_books table is created

    # Inject dependencies into RentedBookDao for access to users and books tables
    dao.user_dao = user_dao
    dao.book_dao = book_dao
    yield dao

    # Close all DAOs to properly close database connections
    dao.close()
    user_dao.close()
    book_dao.close()


# Tests for BookDao

def test_add_book(book_dao):
    book = Book(id=1, isbn='123456789', title='Test Book', author='Author')
    result = book_dao.add_book(book)
    assert result is True

    # Attempt to add duplicate book
    result = book_dao.add_book(book)
    assert result is False


def test_get_all_books(book_dao):
    book1 = Book(id=1, isbn='111', title='Book1', author='Author1')
    book2 = Book(id=2, isbn='222', title='Book2', author='Author2')
    book_dao.add_book(book1)
    book_dao.add_book(book2)
    books = book_dao.get_all_books()
    assert len(books) == 2
    assert books[0].isbn == '111'
    assert books[1].isbn == '222'


def test_get_book_by_id(book_dao):
    book = Book(id=1, isbn='123', title='Single Book', author='Single Author')
    book_dao.add_book(book)
    fetched_book = book_dao.get_book_by_id(1)
    assert fetched_book is not None
    assert fetched_book.title == 'Single Book'
    assert fetched_book.author == 'Single Author'


def test_delete_book(book_dao):
    book = Book(id=1, isbn='123', title='Delete Book', author='Author')
    book_dao.add_book(book)
    result = book_dao.delete_book_by_id(1)
    assert result is True
    assert book_dao.get_book_by_id(1) is None


# Tests for UserDao

def test_add_user(user_dao):
    user = User(user_id=1, username='testuser', password='password')
    result = user_dao.add_user(user)
    assert result is True


def test_get_all_users(user_dao):
    user1 = User(user_id=1, username='user1', password='password1')
    user2 = User(user_id=2, username='user2', password='password2')
    user_dao.add_user(user1)
    user_dao.add_user(user2)
    users = user_dao.get_all_users()
    assert len(users) == 2
    assert users[0].username == 'user1'
    assert users[1].username == 'user2'


def test_get_one_user(user_dao):
    user = User(user_id=1, username='singleuser', password='password')
    user_dao.add_user(user)
    fetched_user = user_dao.get_one_user(1)
    assert fetched_user is not None
    assert fetched_user.username == 'singleuser'


def test_delete_user(user_dao):
    user = User(user_id=1, username='deleteuser', password='password')
    user_dao.add_user(user)
    result = user_dao.delete_user_by_id_and_password(1, 'password')
    assert result is True


# Tests for RentedBookDao

def test_add_rented_book(rented_book_dao):
    user = User(user_id=1, username='testuser', password='password')
    book = Book(id=1, isbn='123', title='Test Book', author='Author')
    rented_book = RentedBooks(id=1, user=user, book=book, rented=True)
    result = rented_book_dao.add_rented_book(rented_book)
    assert result is True


def test_get_all_rented_books(rented_book_dao, user_dao, book_dao):
    user = User(user_id=1, username='testuser', password='password')
    book = Book(id=1, isbn='123', title='Test Book', author='Author')
    user_dao.add_user(user)
    book_dao.add_book(book)
    rented_book = RentedBooks(id=1, user=user, book=book, rented=True)
    rented_book_dao.add_rented_book(rented_book)
    rented_books = rented_book_dao.get_all_rented_books()
    assert len(rented_books) == 1 or len(rented_books) >= 1


def test_get_rent_by_id(rented_book_dao, user_dao, book_dao):
    user = User(user_id=1, username='testuser2', password='password')
    book = Book(id=1, isbn='123', title='Test Book', author='Author')
    user_dao.add_user(user)
    book_dao.add_book(book)
    rented_book = RentedBooks(id=1, user=user, book=book, rented=True)
    rented_book_dao.add_rented_book(rented_book)
    fetched_rented_book = rented_book_dao.get_rent_by_id(1)
    assert fetched_rented_book is not None
    assert fetched_rented_book.id == 1


def test_get_rented_books_by_user_id(rented_book_dao, user_dao, book_dao):
    user = User(user_id=1, username='testuser3', password='password')
    book = Book(id=1, isbn='123', title='Test Book', author='Author')
    user_dao.add_user(user)
    book_dao.add_book(book)
    rented_book = RentedBooks(id=1, user=user, book=book, rented=True)
    rented_book_dao.add_rented_book(rented_book)
    rented_books = rented_book_dao.get_rented_books_by_user_id(1)
    assert len(rented_books) == 1 or len(rented_books) >= 1


def test_delete_rented_book(rented_book_dao, user_dao, book_dao):
    user = User(user_id=1, username='testuser4', password='password')
    book = Book(id=1, isbn='123', title='Test Book', author='Author')
    user_dao.add_user(user)
    book_dao.add_book(book)
    rented_book = RentedBooks(id=1, user=user, book=book, rented=True)
    rented_book_dao.add_rented_book(rented_book)
    result = rented_book_dao.delete_rented_book(1)
    assert result is True


def test_delete_rented_book_by_user_id(rented_book_dao, user_dao, book_dao):
    user = User(user_id=1, username='testuser5', password='password')
    book = Book(id=1, isbn='123', title='Test Book', author='Author')
    user_dao.add_user(user)
    book_dao.add_book(book)
    rented_book = RentedBooks(id=1, user=user, book=book, rented=True)
    rented_book_dao.add_rented_book(rented_book)
    result = rented_book_dao.delete_rented_book_by_user_id(1)
    assert result is True


def test_update_rented_book(rented_book_dao, user_dao, book_dao):
    user = User(user_id=1, username='testuser6', password='password')
    book = Book(id=1, isbn='123', title='Test Book', author='Author')
    user_dao.add_user(user)
    book_dao.add_book(book)
    rented_book = RentedBooks(id=1, user=user, book=book, rented=True)
    rented_book_dao.add_rented_book(rented_book)
    updated_rented_book = RentedBooks(id=1, user=user, book=book, rented=False)
    result = rented_book_dao.update_rented_book(updated_rented_book)
    assert result is True
    assert rented_book_dao.get_rent_by_id(1).rented is False
