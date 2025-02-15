"""
Data models for tables in the database.
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


@dataclass
class Friends:
    """Data model for the Friends table"""

    user_id: str
    friend_id: str
    created_at: datetime
    updated_at: datetime
    status: str
