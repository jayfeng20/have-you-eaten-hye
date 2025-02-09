"""
This module defines Pydantic models used for validating and serializing incoming and outgoing
data related to the User domain.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserProfile(BaseModel):
    """Model for creating users including email, username, created_at and id"""

    id: str
    email: EmailStr
    username: Optional[str]
    created_at: Optional[datetime]


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    id: str


class UsernameCheckResponse(BaseModel):
    """Response model for /checkUsername endpoint"""

    available: bool
