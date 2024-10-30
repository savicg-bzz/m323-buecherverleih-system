""" This module contains the User class. """
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """
    This class represents a user.
    """
    user_id: int
    username: str
    password: str
