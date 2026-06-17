"""Auth Service - JWT and Password Utilities"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import jwt
import os
import asyncio
import bcrypt
import logging

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
ALGORITHM = "HS256"


async def hash_password(password: str) -> str:
    """Hash a password in a separate thread to avoid blocking the event loop."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = await asyncio.to_thread(bcrypt.hashpw, pwd_bytes, salt)
    return hashed_bytes.decode('utf-8')


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash in a separate thread."""
    pwd_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return await asyncio.to_thread(bcrypt.checkpw, pwd_bytes, hash_bytes)


def create_access_token(user_id: str, email: str, roles: List[Dict], expires_delta: timedelta = None) -> Tuple[str, int]:
    """Create JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    
    # Build permissions list from roles
    permissions = []
    for role in roles:
        if hasattr(role, 'permissions'):
            for perm in role.permissions:
                permissions.append((perm.resource, perm.action))
    
    payload = {
        "user_id": user_id,
        "email": email,
        "roles": [role.name if hasattr(role, 'name') else role['name'] for role in roles],
        "permissions": permissions,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    expires_in = int(expires_delta.total_seconds())
    
    return encoded_jwt, expires_in


def create_refresh_token(user_id: str, email: str) -> Tuple[str, int]:
    """Create JWT refresh token"""
    expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.utcnow() + expires_delta
    
    payload = {
        "user_id": user_id,
        "email": email,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    expires_in = int(expires_delta.total_seconds())
    
    return encoded_jwt, expires_in


def decode_token(token: str) -> Dict:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise ValueError("Invalid token")


def decode_refresh_token(token: str) -> Dict:
    """Decode and validate refresh token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Refresh token expired")
        raise ValueError("Refresh token has expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid refresh token: {e}")
        raise ValueError("Invalid refresh token")
