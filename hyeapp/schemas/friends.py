"""
This module defines Pydantic models used for validating and serializing incoming and outgoing
data related to friend management.
"""

from pydantic import BaseModel
from typing import Optional


class GetFriendListResponse(BaseModel):
    """Outgoing response model for /getFriendList endpoint"""

    friends: list[str]


class GetFriendRequestListResponse(BaseModel):
    """
    Outgoing response model for /getFriendRequestList endpoint
    List of friend requests (friend usernames) sent and received by a user.
    """

    requests_sent: list[str]
    requests_received: list[str]


class FriendRequestPostContent(BaseModel):
    """
    Incoming request model for friend-related POST request endpoints
    senderId is Optional since it's only used in dev when there is no authentication.
    accept is Optional since it's only used in /acceptFriendRequest endpoint.
    """

    recipientUsername: str
    senderId: Optional[str] = None
    accept: Optional[bool] = None


class SendFriendRequestResponse(BaseModel):
    """
    Outgoing response model for /sendFriendRequest endpoint
    True, False if friend request sent successfully.
    False, True if friend request already exists.
    False, False if friend username does not exist.
    True, True if user and target are already friends.
    """

    friend_request_sent: bool
    friend_request_already_exist: bool


class AcceptFriendRequestResponse(BaseModel):
    """
    Outgoing response model for /acceptFriendRequest endpoint
    True, if friend request accepted successfully.
    False, if friend request rejected.
    """

    friend_request_accepted: bool


class RemoveFriendResponse(BaseModel):
    """
    Outgoing response model for /removeFriend endpoint
    True, if friend removed successfully.
    Will never be False.
    """

    friend_removed: bool
