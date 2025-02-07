from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import db_session
from app.schemas.user import UserProfile, NicknameUpdate
from app.dbcrud.user import get_user_by_username, update_user_nickname

router = APIRouter()


# Endpoint to get user profile.
@router.get("/{username}", response_model=UserProfile)
async def read_user_profile(username: str, db: AsyncSession = Depends(db_session)):
    user = await get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


# Endpoint to update user nickname.
@router.put("/{username}/nickname", response_model=UserProfile)
async def set_nickname(
    username: str,
    nickname_update: NicknameUpdate,
    db: AsyncSession = Depends(db_session),
):
    user = await update_user_nickname(db, username, nickname_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
