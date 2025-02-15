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


class UsernameCheckResponse(BaseModel):
    """Outgoing response model for /checkUsername endpoint"""

    available: bool


class UserEmailCheckResponse(BaseModel):
    """Outgoing response model for /checkUserEmailExistence endpoint"""

    exists: bool


class GetFriendListResponse(BaseModel):
    """Outgoing response model for /getFriendList endpoint"""

    friends: list[str]


class GetFriendRequestListResponse(BaseModel):
    """Outgoing response model for /getFriendRequestList endpoint"""

    requests_sent: list[str]
    requests_received: list[str]


class SendFriendRequestResponse(BaseModel):
    """
    Outgoing response model for /sendFriendRequest endpoint
    True, False if friend request sent successfully.
    False, True if friend request already exists.
    False, False if friend username does not exist.
    """

    friend_request_sent: bool
    friend_request_already_exist: bool


class AcceptFriendRequestResponse(BaseModel):
    """
    Outgoing response model for /acceptFriendRequest endpoint
    """

    friend_request_accepted: bool
