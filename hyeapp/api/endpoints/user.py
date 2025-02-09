"""
User-related endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import (
    UserCreate,
    UserProfile,
    UsernameCheckResponse,
)
from dbcrud.user import create_user, get_user_by_email, check_username
from db.session import get_db_session
import logging
from dataclasses import asdict

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/signup", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db_session)):
    new_user = await create_user(db, user)
    logging.info(f"New user created: {new_user}")
    return UserProfile(**(asdict(new_user)))


@router.get("/checkUsername", response_model=UsernameCheckResponse)
async def check_username_availability(
    username: str, db: AsyncSession = Depends(get_db_session)
):
    available = await check_username(username, db)
    return UsernameCheckResponse(available=available)
