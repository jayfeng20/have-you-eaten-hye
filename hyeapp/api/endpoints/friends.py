"""
Friend-related endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.friends import (
    GetFriendListResponse,
    GetFriendRequestListResponse,
    FriendRequestPostContent,
    SendFriendRequestResponse,
    AcceptFriendRequestResponse,
    RemoveFriendResponse,
)
import dbcrud.friends as dbcrudfriends
from db.session import get_db_session
import logging
from dataclasses import asdict
from api.auth import verify_token

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/getFriendList", response_model=GetFriendListResponse)
async def get_friend_list(
    # userId: str,
    token_payload: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session),
):
    userId = token_payload["sub"]
    logging.info(f"Getting friend list for user: {userId}")
    friends = await dbcrudfriends.get_friend_list(userId, db)
    logging.info(f"Friend list for user {userId}: {friends}")
    return GetFriendListResponse(friends=friends)


@router.get("/getFriendRequestList", response_model=GetFriendRequestListResponse)
async def get_friend_request_list(
    # userId: str,
    token_payload: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session),
):
    userId = token_payload["sub"]
    logging.info(f"Getting friend request list for user: {userId}")
    sent, received = await dbcrudfriends.get_friend_request_list(userId, db)
    logging.info(
        f"Friend request list for user {userId}: sent: {sent}, received: {received}"
    )
    return GetFriendRequestListResponse(requests_sent=sent, requests_received=received)


@router.post("/sendFriendRequest", response_model=SendFriendRequestResponse)
async def send_friend_request(
    # senderId: str,
    content: FriendRequestPostContent,
    token_payload: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session),
):
    senderId = token_payload["sub"]
    logging.info(f"Sending friend request to user: {content.recipientUsername}")
    sent, already_exist = await dbcrudfriends.send_friend_request(
        sender_id=senderId, recipient_username=content.recipientUsername, db=db
    )
    logging.info(f"Friend request sent to user {content.recipientUsername}: {sent}")
    return SendFriendRequestResponse(
        friend_request_sent=sent, friend_request_already_exist=already_exist
    )


@router.post("/acceptFriendRequest", response_model=AcceptFriendRequestResponse)
async def accept_friend_request(
    content: FriendRequestPostContent,
    token_payload: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session),
):
    senderId = token_payload["sub"]
    logging.info(f"Resolving friend request from user: {content.recipientUsername}")
    accepted = await dbcrudfriends.accept_friend_request(
        recipient_id=senderId,
        sender_username=content.recipientUsername,
        accept=content.accept,
        db=db,
    )
    logging.info(
        f"Friend request from user {content.recipientUsername} status: {accepted}"
    )
    return AcceptFriendRequestResponse(friend_request_accepted=accepted)


@router.post("/removeFriend", response_model=RemoveFriendResponse)
async def remove_friend(
    content: FriendRequestPostContent,
    token_payload: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session),
):
    senderId = token_payload["sub"]
    logging.info(f"Removing friend: {content.recipientUsername}")
    removed = await dbcrudfriends.remove_friend(
        sender_id=senderId, recipient_username=content.recipientUsername, db=db
    )
    logging.info(f"Friend {content.recipientUsername} removed: {removed}")
    return RemoveFriendResponse(friend_removed=removed)
