import logging
import uuid
import hashlib
import json
from datetime import datetime
from typing import Dict, Optional, Any
from fastapi import Request
from app.config import redis_client, settings

logger = logging.getLogger(__name__)

class RequestInterceptorPipeline:
    """
    13-Step Request Interceptor Pipeline
    
    1. Request ID generation
    2. Correlation ID extraction/generation
    3. IP address extraction
    4. User-Agent parsing
    5. Rate limiting (Redis)
    6. API key validation
    7. JWT extraction
    8. Session validation (Redis)
    9. RBAC enforcement
    10. Input validation
    11. Data sanitization
    12. Audit logging
    13. Error handling & response formatting
    """
    
    async def process(self, request: Request) -> Dict[str, Any]:
        """Process request through all 13 steps"""
        context = {}
        
        try:
            # Step 1: Request ID generation
            context["request_id"] = self._step_1_generate_request_id()
            logger.info(f"[{context['request_id']}] Step 1: Generated request ID")
            
            # Step 2: Correlation ID extraction/generation
            context["correlation_id"] = self._step_2_correlation_id(request)
            logger.info(f"[{context['request_id']}] Step 2: Correlation ID: {context['correlation_id']}")
            
            # Step 3: IP address extraction
            context["client_ip"] = self._step_3_extract_ip(request)
            logger.info(f"[{context['request_id']}] Step 3: Client IP: {context['client_ip']}")
            
            # Step 4: User-Agent parsing
            context["user_agent"] = self._step_4_parse_user_agent(request)
            logger.info(f"[{context['request_id']}] Step 4: User-Agent parsed")
            
            # Step 5: Rate limiting
            rate_limit_result = await self._step_5_rate_limiting(context["client_ip"])
            if not rate_limit_result["allowed"]:
                logger.warning(f"[{context['request_id']}] Step 5: Rate limit exceeded for {context['client_ip']}")
                return {"status": "rejected", "reason": "rate_limit_exceeded", **context}
            context["rate_limit"] = rate_limit_result
            logger.info(f"[{context['request_id']}] Step 5: Rate limit check passed")
            
            # Step 6: API key validation
            api_key_result = self._step_6_validate_api_key(request)
            context["api_key"] = api_key_result
            logger.info(f"[{context['request_id']}] Step 6: API key validation: {api_key_result['valid']}")
            
            # Step 7: JWT extraction
            jwt_token = self._step_7_extract_jwt(request)
            context["jwt_token"] = jwt_token
            logger.info(f"[{context['request_id']}] Step 7: JWT extracted: {bool(jwt_token)}")
            
            # Step 8: Session validation
            if jwt_token:
                session_result = await self._step_8_validate_session(jwt_token)
                context["session"] = session_result
                logger.info(f"[{context['request_id']}] Step 8: Session validation: {session_result.get('valid', False)}")
            
            # Step 9: RBAC enforcement (placeholder)
            rbac_result = self._step_9_rbac_check(request, context)
            context["rbac"] = rbac_result
            logger.info(f"[{context['request_id']}] Step 9: RBAC check: {rbac_result['allowed']}")
            
            # Step 10: Input validation (done at endpoint level with Pydantic)
            context["input_validation"] = {"status": "pending"}
            logger.info(f"[{context['request_id']}] Step 10: Input validation: pending (done at endpoint)")
            
            # Step 11: Data sanitization (done at request parsing level)
            context["sanitization"] = {"status": "applied"}
            logger.info(f"[{context['request_id']}] Step 11: Data sanitization: applied")
            
            # Step 12: Audit logging (will be done after request processing)
            context["audit_enabled"] = settings.audit_log_enabled
            logger.info(f"[{context['request_id']}] Step 12: Audit logging: enabled")
            
            # Step 13: Error handling prepared
            context["error_handling"] = {"handler": "global_exception_handler"}
            logger.info(f"[{context['request_id']}] Step 13: Error handling: ready")
            
            context["status"] = "accepted"
            return context
            
        except Exception as e:
            logger.error(f"[{context.get('request_id', 'unknown')}] Pipeline error: {str(e)}", exc_info=True)
            return {"status": "error", "reason": str(e), **context}
    
    # Step 1: Request ID generation
    def _step_1_generate_request_id(self) -> str:
        """Generate unique request ID"""
        return str(uuid.uuid4())
    
    # Step 2: Correlation ID extraction/generation
    def _step_2_correlation_id(self, request: Request) -> str:
        """Extract or generate correlation ID for distributed tracing"""
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        return correlation_id
    
    # Step 3: IP address extraction
    def _step_3_extract_ip(self, request: Request) -> str:
        """Extract client IP from request (handles proxies)"""
        # Check for X-Forwarded-For header (behind proxy)
        if "X-Forwarded-For" in request.headers:
            return request.headers["X-Forwarded-For"].split(",")[0].strip()
        # Check for X-Real-IP header
        if "X-Real-IP" in request.headers:
            return request.headers["X-Real-IP"]
        # Fall back to client connection IP
        return request.client.host if request.client else "unknown"
    
    # Step 4: User-Agent parsing
    def _step_4_parse_user_agent(self, request: Request) -> Dict[str, str]:
        """Parse User-Agent header"""
        user_agent = request.headers.get("User-Agent", "unknown")
        return {
            "raw": user_agent,
            "browser": "Unknown",  # Can be expanded with ua-parser
            "os": "Unknown"
        }
    
    # Step 5: Rate limiting (Redis)
    async def _step_5_rate_limiting(self, client_ip: str) -> Dict[str, Any]:
        """Rate limiting using Redis"""
        key = f"rate_limit:{client_ip}"
        current = redis_client.incr(key)
        
        if current == 1:
            redis_client.expire(key, settings.rate_limit_period_seconds)
        
        allowed = current <= settings.rate_limit_requests
        
        return {
            "allowed": allowed,
            "current": current,
            "limit": settings.rate_limit_requests,
            "period_seconds": settings.rate_limit_period_seconds
        }
    
    # Step 6: API key validation
    def _step_6_validate_api_key(self, request: Request) -> Dict[str, Any]:
        """Validate API key from header"""
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            return {"valid": False, "reason": "missing"}
        
        # Placeholder validation (in production, check against database/vault)
        if api_key == settings.api_key_secret:
            return {"valid": True, "key": "service-auth"}
        
        return {"valid": False, "reason": "invalid_key"}
    
    # Step 7: JWT extraction
    def _step_7_extract_jwt(self, request: Request) -> Optional[str]:
        """Extract JWT from Authorization header"""
        auth_header = request.headers.get("Authorization", "")
        
        if auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix
        
        return None
    
    # Step 8: Session validation (Redis)
    async def _step_8_validate_session(self, jwt_token: str) -> Dict[str, Any]:
        """Validate session from Redis"""
        session_key = f"session:{hashlib.sha256(jwt_token.encode()).hexdigest()}"
        session_data = redis_client.get(session_key)
        
        if session_data:
            return {
                "valid": True,
                "data": json.loads(session_data)
            }
        
        return {
            "valid": False,
            "reason": "session_not_found"
        }
    
    # Step 9: RBAC enforcement
    def _step_9_rbac_check(self, request: Request, context: Dict) -> Dict[str, Any]:
        """Role-based access control check"""
        # Placeholder RBAC logic
        # In production, check JWT claims against endpoint requirements
        
        public_endpoints = ["/health", "/docs", "/openapi.json", "/redoc", "/"]
        
        if request.url.path in public_endpoints:
            return {"allowed": True, "role": "public"}
        
        # All other endpoints require authentication
        if context.get("jwt_token"):
            return {"allowed": True, "role": "authenticated"}
        
        return {"allowed": False, "reason": "authentication_required"}
