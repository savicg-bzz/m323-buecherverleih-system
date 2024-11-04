"""
This file is used to define fixtures that can be used in the tests.
"""
from main import generate_data


def pytest_sessionstart():
    """
    This method is called when the session starts.
    :return:
    """
    generate_data()
