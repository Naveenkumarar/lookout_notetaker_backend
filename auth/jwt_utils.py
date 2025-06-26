# utils.py
from jose import jwt, JWTError,ExpiredSignatureError
from datetime import datetime, timedelta
from fastapi import HTTPException
import time

SECRET_KEY = "lookout_notetaker"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



MAX_ATTEMPTS = 5
BLOCK_DURATION = 60  # seconds

from db_client import DatabaseConnection
db_conn=DatabaseConnection()


def is_user_blocked(username: str) -> bool:
    """
    Checks if the given user is currently blocked due to too many failed login attempts.

    Args:
        username (str): The username to check.

    Returns:
        bool: True if the user is blocked, False otherwise.
    """
    record = db_conn.blocked_users.find_one({"username": username})
    now = datetime.utcnow()

    if record:
        blocked_until = record.get("blocked_until")
        if blocked_until and blocked_until > now:
            return True
        elif record.get("failed_attempts", 0) >= MAX_ATTEMPTS:
            # Reset block if time is over
            db_conn.blocked_users.update_one(
                {"username": username},
                {"$set": {"failed_attempts": 0, "blocked_until": None}}
            )
    return False

def register_failed_attempt(username: str):
    """
    Registers a failed login attempt for the given user and updates block status if necessary.

    Args:
        username (str): The username for which to register the failed attempt.
    """
    user = db_conn.blocked_users.find_one({"username": username})
    now = datetime.utcnow()

    if not user:
        db_conn.blocked_users.insert_one({
            "username": username,
            "failed_attempts": 1,
            "blocked_until": None
        })
    else:
        attempts = user.get("failed_attempts", 0) + 1
        blocked_until = None

        if attempts >= MAX_ATTEMPTS:
            blocked_until = now + timedelta(seconds=BLOCK_DURATION)

        db_conn.blocked_users.update_one(
            {"username": username},
            {"$set": {
                "failed_attempts": attempts,
                "blocked_until": blocked_until
            }}
        )

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Creates a JWT access token with an optional expiration.

    Args:
        data (dict): The payload to encode in the token.
        expires_delta (timedelta, optional): Custom expiration duration.

    Returns:
        str: Encoded JWT token as a string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    """
    Decodes and validates a JWT token.

    Args:
        token (str): The JWT token to decode.

    Raises:
        HTTPException: If the token is expired or invalid.

    Returns:
        dict: The decoded JWT payload.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
