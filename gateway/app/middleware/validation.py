"""
Input validation middleware and sanitization utilities
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
import re
import logging

logger = logging.getLogger(__name__)

class ValidationMiddleware(BaseHTTPMiddleware):
    """Input validation middleware"""
    
    async def dispatch(self, request: Request, call_next):
        # Pydantic automatically validates request bodies
        # Additional validation can be done here
        response = await call_next(request)
        return response

class SanitizationUtils:
    """Data sanitization utilities"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input to prevent XSS"""
        if not isinstance(value, str):
            return value
        
        # Truncate if too long
        value = value[:max_length]
        
        # Remove potentially dangerous characters
        value = re.sub(r'[<>\"\'&]', '', value)
        
        return value.strip()
    
    @staticmethod
    def sanitize_dict(data: dict) -> dict:
        """Recursively sanitize dictionary"""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = SanitizationUtils.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = SanitizationUtils.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    SanitizationUtils.sanitize_string(v) if isinstance(v, str) else v
                    for v in value
                ]
            else:
                sanitized[key] = value
        return sanitized
