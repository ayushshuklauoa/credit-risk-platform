from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware - delegates to interceptor"""
    
    async def dispatch(self, request: Request, call_next):
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Rate limit is already checked in interceptor
        # This is a placeholder for additional rate limit handling
        
        response = await call_next(request)
        return response
