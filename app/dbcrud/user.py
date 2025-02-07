from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import NicknameUpdate


async def get_user_by_username(db: AsyncSession, username: str) -> User:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def update_user_nickname(
    db: AsyncSession, username: str, nickname_update: NicknameUpdate
) -> User:
    user = await get_user_by_username(db, username)
    if not user:
        return None
    user.nickname = nickname_update.nickname
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
