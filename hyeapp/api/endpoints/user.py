"""
User-related endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import (
    UserCreate,
    UserProfile,
    UsernameCheckResponse,
    UserIdCheckResponse,
)
from dbcrud.user import (
    create_user,
    get_user_by_email,
    check_username,
    check_user_id_existence,
)
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
    new_user = await create_user(
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
    available = await check_username(username, db)
    logging.info(f"Username {username} availability: {available}")
    return UsernameCheckResponse(available=available is not None)


@router.get("/checkUserIdExistence", response_model=UserIdCheckResponse)
async def check_user_id_existence(
    user_id: str,
    token_payload: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db_session),
):
    logging.info(f"Checking if user_id exists: {user_id}")
    exists = await check_user_id_existence(user_id, db)
    logging.info(f"User id {user_id} existence: {exists}")
    return UserIdCheckResponse(exists=exists is not None)
