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


# Base = declarative_base()


# class Users(Base):
#     """Base model for user profile"""

#     __tablename__ = "users"

#     id = Column(String, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True, nullable=False)
#     email = Column(String, unique=True, index=True, nullable=False)
#     created_at = Column(TIMESTAMP, nullable=False)
