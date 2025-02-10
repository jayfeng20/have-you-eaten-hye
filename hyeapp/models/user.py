"""
Data model for Users Table in the database.
"""

from datetime import datetime

# from sqlalchemy import Column, Integer, String, TIMESTAMP
# from sqlalchemy.ext.declarative import declarative_base
from dataclasses import dataclass


@dataclass
class Users:
    """Data model for the Users table"""

    id: str
    username: str
    email: str
    created_at: datetime
