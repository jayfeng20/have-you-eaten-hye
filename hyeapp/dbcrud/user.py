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
from typing import Tuple

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


async def check_username_availability(username: str, db: AsyncSession) -> bool:
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


async def check_user_email_existence(user_email: str, db: AsyncSession) -> bool:
    """Check if the user with given user_id already exists in the database"""
    select_sql = text(
        """
        SELECT COUNT(1) as cnt FROM users WHERE email = :email
    """
    )

    try:
        result = await db.execute(select_sql, {"email": user_email})
        exists = result.fetchone()._mapping["cnt"] == 1
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=400, detail="user_email existence request failed."
        )

    return exists


async def get_friend_list(user_id: str, db: AsyncSession) -> list[str]:
    """Get the list of friends for a given user"""

    fetch_friends = text(
        """
        SELECT friend_id FROM friends WHERE user_id = :user_id
    """
    )

    try:
        result = await db.execute(fetch_friends, {"user_id": user_id})
        friends = [row[0] for row in result.fetchall()]
    except SQLAlchemyError as e:
        logger.error("Failed to get friend list for user: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get friend list.")

    return friends


async def get_friend_request_list(user_id: str, db: AsyncSession) -> list[dict]:
    """Get the list of friend requests received and sent by a given user that have not been accepted nor rejected"""

    fetch_requests_sent = text(
        """
        SELECT u.username AS friend_name FROM friends f
        JOIN users u ON u.id = friends.friend_id
        WHERE f.user_id = :user_id AND f.status = 'pending'
    """
    )

    fetch_requests_received = text(
        """
        SELECT u.username AS friend_name FROM friends f
        JOIN users u ON u.id = f.user_id
        WHERE friend_id = :user_id AND status = 'pending'
    """
    )

    try:
        result = await db.execute(fetch_requests_sent, {"user_id": user_id})
        sent = [row[0] for row in result.fetchall()]
    except SQLAlchemyError as e:
        logger.error(
            "Failed to get friend requests sent by the user: %s", e, exc_info=True
        )
        raise HTTPException(
            status_code=400, detail="Failed to get friend request list."
        )

    try:
        result = await db.execute(fetch_requests_received, {"user_id": user_id})
        received = [row[0] for row in result.fetchall()]
    except SQLAlchemyError as e:
        logger.error(
            "Failed to get friend requests received by the user: %s", e, exc_info=True
        )
        raise HTTPException(
            status_code=400, detail="Failed to get friend request list."
        )

    return sent, received


async def send_friend_request(
    user_id: str, friend_username: str, db: AsyncSession
) -> Tuple[bool, bool]:
    """Send a friend request from one user to its friend"""

    check_friend_username = text(
        """
        SELECT COUNT(1) as cnt FROM users WHERE username = :username
    """
    )

    try:
        result = await db.execute(check_friend_username, {"username": friend_username})
        friend_exists = result.fetchone()._mapping["cnt"] == 1
        if not friend_exists:
            logging.info("Friend username: {friend_username} does not exist.")
            return False, False
    except SQLAlchemyError as e:
        logger.error("Failed to check friend username: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to send friend request.")

    send_request = text(
        """
        INSERT INTO friends (user_id, friend_id, status)
        VALUES (:user_id, (SELECT id FROM users WHERE username = :friend_username), 'pending')
    """
    )

    try:
        await db.execute(
            send_request, {"user_id": user_id, "friend_username": friend_username}
        )
        await db.commit()
    except IntegrityError as ie:
        await db.rollback()
        logger.info(
            "Integrity error while sending friend request. It may already exists: %s",
            ie,
            exc_info=True,
        )
        return False, True
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            "Database error while sending friend request: %s", e, exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to send friend request. Please try again later.",
        )
    else:
        logging.info(f"Friend request sent to {friend_username}")
        return True, False


async def accept_friend_request(
    user_id: str, friend_username: str, db: AsyncSession
) -> bool:
    """Accept a friend request from a friend"""

    accept_request = text(
        """
        UPDATE friends SET status = 'accepted' WHERE user_id = :user_id AND friend_id = (SELECT id FROM users WHERE username = :friend_username)
    """
    )

    try:
        await db.execute(
            accept_request, {"user_id": user_id, "friend_username": friend_username}
        )
        await db.commit()
    except IntegrityError as ie:
        await db.rollback()
        logger.info(
            "Integrity error while accepting friend request. It may already exists: %s",
            ie,
            exc_info=True,
        )
        return False
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            "Database error while accepting friend request: %s", e, exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to accept friend request. Please try again later.",
        )
    else:
        logging.info(f"Friend request from {friend_username} accepted")
        return True
