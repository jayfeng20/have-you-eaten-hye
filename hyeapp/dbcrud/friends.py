"""
Database operations for friend management.
"""

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


async def get_friend_list(user_id: str, db: AsyncSession) -> list[str]:
    """Get the list of friends for a given user"""

    fetch_friends1 = text(
        """
        SELECT u.username AS recipient_username FROM friends f
        JOIN users u ON u.id = f.recipient_id
        WHERE sender_id = :user_id AND status = 'accepted'
    """
    )

    fetch_friends2 = text(
        """
        SELECT u.username AS sender_username FROM friends f
        JOIN users u ON u.id = f.sender_id
        WHERE recipient_id = :user_id AND status = 'accepted'
    """
    )

    try:
        result = await db.execute(fetch_friends1, {"user_id": user_id})
        friends = [row[0] for row in result.fetchall()]

        result = await db.execute(fetch_friends2, {"user_id": user_id})
        friends += [row[0] for row in result.fetchall()]
    except SQLAlchemyError as e:
        logger.error("Failed to get friend list for user: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get friend list.")

    return friends


async def get_friend_request_list(user_id: str, db: AsyncSession) -> list[dict]:
    """Get the list of friend requests received and sent by a given user that have not been accepted nor rejected"""

    fetch_requests_sent = text(
        """
        SELECT u.username AS recipient_username FROM friends f
        JOIN users u ON u.id = f.recipient_id
        WHERE f.sender_id = :user_id AND f.status = 'pending'
    """
    )

    fetch_requests_received = text(
        """
        SELECT u.username AS sender_username FROM friends f
        JOIN users u ON u.id = f.sender_id
        WHERE recipient_id = :user_id AND status = 'pending'
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
    sender_id: str, recipient_username: str, db: AsyncSession
) -> Tuple[bool, bool]:
    """Send a friend request from one user to a target user"""

    # Check if the target username exists at all
    check_friend_username = text(
        """
        SELECT COUNT(1) as cnt FROM users WHERE username = :username
    """
    )

    try:
        result = await db.execute(
            check_friend_username, {"username": recipient_username}
        )
        friend_exists = result.fetchone()._mapping["cnt"] == 1
        if not friend_exists:
            logging.info("Friend username: {friend_username} does not exist.")
            return False, False
    except SQLAlchemyError as e:
        logger.error("Failed to check friend username: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to send friend request.")

    # Check if the user and target are already friends
    check_if_already_friends = text(
        """
        WITH TargetId AS (
            SELECT id FROM users WHERE username = :recipient_username
        )
        SELECT COUNT(1) as cnt 
        FROM friends 
        WHERE (sender_id = :sender_id 
            AND recipient_id = (SELECT t.id FROM TargetId t) 
            AND status = 'accepted')
        OR (recipient_id = :sender_id 
            AND sender_id = (SELECT t.id FROM TargetId t) 
            AND status = 'accepted')
        """
    )

    try:
        result = await db.execute(
            check_if_already_friends,
            {"sender_id": sender_id, "recipient_username": recipient_username},
        )
        already_friends = result.fetchone()._mapping["cnt"] == 1
        if already_friends:
            logging.info(f"{sender_id} and {recipient_username} are already friends.")
            return True, True
    except SQLAlchemyError as e:
        logger.error(
            "Failed to check if friend request already exists: %s", e, exc_info=True
        )
        raise HTTPException(status_code=400, detail="Failed to send friend request.")

    # Check if the user has already sent a friend request to `recipient` or having one sent by `recipient`. E.g. pending status
    check_if_already_sent = text(
        """
        WITH TargetId AS (
            SELECT id FROM users WHERE username = :recipient_username
        )
        SELECT COUNT(1) as cnt 
        FROM friends 
        WHERE (sender_id = :sender_id 
            AND recipient_id = (SELECT t.id FROM TargetId t) 
            AND status = 'pending')
        OR (recipient_id = :sender_id 
            AND sender_id = (SELECT t.id FROM TargetId t) 
            AND status = 'pending')
        """
    )

    try:
        result = await db.execute(
            check_if_already_sent,
            {"sender_id": sender_id, "recipient_username": recipient_username},
        )
        already_sent = result.fetchone()._mapping["cnt"] == 1
        if already_sent:
            logging.info(
                f"{sender_id} has already sent a friend request to {recipient_username}."
            )
            return False, True
    except SQLAlchemyError as e:
        logger.error(
            "Failed to check if friend request already exists: %s", e, exc_info=True
        )
        raise HTTPException(status_code=400, detail="Failed to send friend request.")

    # Send the friend request
    send_request = text(
        """
        INSERT INTO friends (sender_id, recipient_id, status)
        VALUES (:sender_id, (SELECT id FROM users WHERE username = :recipient_username), 'pending')
    """
    )

    try:
        await db.execute(
            send_request,
            {"sender_id": sender_id, "recipient_username": recipient_username},
        )
        await db.commit()
    except IntegrityError as ie:
        await db.rollback()
        logger.info(
            "Integrity error while sending friend request: %s",
            ie,
            exc_info=True,
        )
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
        logging.info(f"Friend request sent to {recipient_username}")
        return True, False


async def accept_friend_request(
    recipient_id: str, sender_username: str, accept: bool, db: AsyncSession
) -> bool:
    """Accept a friend request from a user"""

    resolve_request = (
        text(
            """
        UPDATE friends SET status = 'accepted' WHERE recipient_id = :recipient_id AND sender_id = (SELECT id FROM users WHERE username = :sender_username)
    """
        )
        if accept
        else text(
            """
        DELETE FROM friends WHERE recipient_id = :recipient_id AND sender_id = (SELECT id FROM users WHERE username = :sender_username)
    """
        )
    )

    try:
        await db.execute(
            resolve_request,
            {"recipient_id": recipient_id, "sender_username": sender_username},
        )
        await db.commit()
    except IntegrityError as ie:
        await db.rollback()
        logger.info(
            "Integrity error while resolving friend request. %s",
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
        logging.info(f"Friend request from {sender_username} accepted")
        return True


async def remove_friend(
    sender_id: str, recipient_username: str, db: AsyncSession
) -> bool:
    """Remove a friend from the user's friend list"""

    remove_friend = text(
        """
        DELETE FROM friends 
        WHERE (sender_id = :sender_id AND recipient_id = (SELECT id FROM users WHERE username = :recipient_username) AND status = 'accepted')
        OR
        (recipient_id = :sender_id AND sender_id = (SELECT id FROM users WHERE username = :recipient_username) AND status = 'accepted')
    """
    )

    try:
        deleted = await db.execute(
            remove_friend,
            {"sender_id": sender_id, "recipient_username": recipient_username},
        )
        await db.commit()
    except IntegrityError as ie:
        await db.rollback()
        logger.info(
            "Integrity error while removing friend: %s",
            ie,
            exc_info=True,
        )
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error("Database error while removing friend: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to remove friend. Please try again later.",
        )
    else:
        logging.info(f"Friend {recipient_username} removed")
        return deleted.rowcount == 1
