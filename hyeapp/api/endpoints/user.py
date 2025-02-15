"""
User-related endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import (
    UserCreate,
    UserProfile,
    UsernameCheckResponse,
    UserEmailCheckResponse,
    GetFriendListResponse,
    GetFriendRequestListResponse,
    SendFriendRequestResponse,
    AcceptFriendRequestResponse,
)
import dbcrud.user as dbcruduser
from db.session import get_db_session
import logging
from dataclasses import asdict
from api.auth import verify_token

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/signup", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def signup(
    user: UserCreate,
    token_payload: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session),
):
    new_user = await dbcruduser.create_user(
        db,
        user={
            "email": user.email,
            "username": user.username,
            "id": token_payload["sub"],
        },
    )
    logging.info(f"New user created: {new_user}")
    return UserProfile(**(asdict(new_user)))


@router.get("/checkUsername", response_model=UsernameCheckResponse)
async def check_username_availability(
    username: str,
    token_payload: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session),
):
    logging.info(f"Checking availability of username: {username}")
    available = await dbcruduser.check_username_availability(username, db)
    logging.info(f"Username {username} availability: {available}")
    return UsernameCheckResponse(available=available)


@router.get("/checkUserEmailExistence", response_model=UserEmailCheckResponse)
async def check_user_email_existence(
    userEmail: str,
    token_payload: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session),
):
    logging.info(f"Checking if user email exists: {userEmail}")
    exists = await dbcruduser.check_user_email_existence(userEmail, db)
    logging.info(f"User id {userEmail} existence: {exists}")
    return UserEmailCheckResponse(exists=exists)


@router.get("/getFriendList", response_model=GetFriendListResponse)
async def get_friend_list(
    userId: str,
    token_payload: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session),
):
    logging.info(f"Getting friend list for user: {userId}")
    friends = await dbcruduser.get_friend_list(userId, db)
    logging.info(f"Friend list for user {userId}: {friends}")
    return GetFriendListResponse(friends=friends)


@router.get("/getFriendRequestList", response_model=GetFriendRequestListResponse)
async def get_friend_request_list(
    userId: str,
    token_payload: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session),
):
    logging.info(f"Getting friend request list for user: {userId}")
    sent, received = await dbcruduser.get_friend_request_list(userId, db)
    logging.info(
        f"Friend request list for user {userId}: sent: {sent}, received: {received}"
    )
    return GetFriendRequestListResponse(requests_sent=sent, requests_received=received)


@router.post("/sendFriendRequest", response_model=SendFriendRequestResponse)
async def send_friend_request(
    userId: str,
    friendUsername: str,
    token_payload: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session),
):
    logging.info(f"Sending friend request to user: {friendUsername}")
    sent, already_exist = await dbcruduser.send_friend_request(
        user_id=userId, friend_username=friendUsername, db=db
    )
    logging.info(f"Friend request sent to user {friendUsername}: {sent}")
    return SendFriendRequestResponse(
        friend_request_sent=sent, friend_request_already_exist=already_exist
    )


@router.post("/acceptFriendRequest", response_model=AcceptFriendRequestResponse)
async def accept_friend_request(
    userId: str,
    friendUsername: str,
    token_payload: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session),
):
    logging.info(f"Accepting friend request from user: {friendUsername}")
    accepted = await dbcruduser.accept_friend_request(
        user_id=userId, friend_username=friendUsername, db=db
    )
    logging.info(f"Friend request from user {friendUsername} accepted: {accepted}")
    return AcceptFriendRequestResponse(accepted=accepted)
