from fastapi import Request
from datetime import datetime
import json
import logging
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Audit logging middleware for sensitive operations"""
    
    async def dispatch(self, request: Request, call_next):
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Define sensitive endpoints that require audit logging
        sensitive_operations = [
            "/auth/login",
            "/accounts",
            "/credit/summary",
            "/fraud/alerts",
            "/documents/upload"
        ]
        
        should_audit = any(
            request.url.path.startswith(path) 
            for path in sensitive_operations
        )
        
        if should_audit and request.method in ["POST", "PUT", "DELETE"]:
            try:
                client_ip = request.client.host if request.client else "unknown"
                
                audit_entry = {
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "method": request.method,
                    "path": request.url.path,
                    "client_ip": client_ip,
                    "user_agent": request.headers.get("User-Agent", "unknown"),
                }
                
                logger.info(f"AUDIT: {json.dumps(audit_entry)}")
            except Exception as e:
                logger.error(f"Audit logging error: {str(e)}")
        
        response = await call_next(request)
        return response
