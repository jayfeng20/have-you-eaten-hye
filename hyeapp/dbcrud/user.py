"""
Database operations for user management.
"""

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from models.user import Users
from schemas.user import UserCreate
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


async def create_user(db: AsyncSession, user: dict) -> Users:
    """
    Create a new user record in the database.

    This function attempts to insert a new user into the database using the provided
    UserCreate data. If the commit is successful, the new user is returned; otherwise,
    the transaction is rolled back and an appropriate HTTP error is raised.

    Args:
        db (AsyncSession): The asynchronous database session.
        user (UserCreate): The validated user data from the request.

    Returns:
        Users: The ORM user instance representing the newly created user.
    """

    insert_sql = text(
        """
        INSERT INTO users (email, username, id)
        VALUES (:email, :username, :id)
    """
    )
    select_sql = text(
        """
        SELECT * FROM users WHERE id = :id
    """
    )

    try:
        await db.execute(
            insert_sql,
            {"email": user["email"], "username": user["username"], "id": user["id"]},
        )
        await db.commit()
        result = await db.execute(select_sql, {"id": user["id"]})
        user_profile = dict(result.fetchone()._mapping)

        if user_profile is None:
            raise HTTPException(
                status_code=500, detail="Failed to retrieve inserted user."
            )
    except IntegrityError as ie:
        # Roll back the session in case of integrity issues (e.g., duplicate user)
        await db.rollback()
        logger.error("Integrity error while creating user: %s", ie, exc_info=True)
        raise HTTPException(status_code=400, detail="User already exists.")
    except SQLAlchemyError as e:
        # Roll back the session for any other database-related error
        await db.rollback()
        logger.error("Database error while creating user: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to create user. Please try again later."
        )
    else:
        logger.info(f"User created successfully: {user_profile}")
    return Users(**user_profile)


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(text(f"SELECT * FROM users WHERE email = {email}"))
    return result.scalar_one_or_none()


async def check_username(username: str, db: AsyncSession) -> bool:
    """Check if the username is already taken in the database"""
    select_sql = text(
        """
        SELECT COUNT(1) as cnt FROM users WHERE username ILIKE :username
    """
    )
    try:
        result = await db.execute(select_sql, {"username": username})
        available = result.fetchone()._mapping["cnt"] == 0
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="username check failed.")

    return available
