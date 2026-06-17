"""
Shared library for token validation across services
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import logging

logger = logging.getLogger(__name__)

class TokenValidator:
    """Cross-service JWT token validation"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def validate_token(self, token: str) -> Optional[dict]:
        """
        Validate JWT token and return payload
        
        Internal method used by services to verify tokens
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except JWTError as e:
            logger.warning(f"Token validation failed: {str(e)}")
            return None
    
    def create_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a new JWT token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        return encoded_jwt
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create a refresh token"""
        expires = timedelta(days=7)
        return self.create_token(
            data={"user_id": user_id, "type": "refresh"},
            expires_delta=expires
        )
