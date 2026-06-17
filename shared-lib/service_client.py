"""
Inter-service communication utilities for microservices architecture
"""
import httpx
import logging
from typing import Any, Dict, Optional
from datetime import datetime
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)

# Service URLs configuration
SERVICE_URLS = {
    "auth": "http://auth-service:8001",
    "customer": "http://customer-service:8002",
    "account": "http://account-service:8003",
    "credit-scoring": "http://credit-scoring-service:8004",
    "fraud-detection": "http://fraud-detection-service:8005",
    "document-ai": "http://document-ai-service:8006",
}

class ServiceClient:
    """HTTP client for inter-service communication"""
    
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self.client = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def _make_request(self, method: str, service: str, path: str, 
                           **kwargs) -> Dict[str, Any]:
        """Make HTTP request to another service"""
        if service not in SERVICE_URLS:
            raise ValueError(f"Unknown service: {service}")
        
        url = f"{SERVICE_URLS[service]}{path}"
        
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            logger.error(f"Timeout calling {service} at {url}")
            raise ServiceTimeoutError(f"Service {service} timed out")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from {service}: {e.response.status_code}")
            raise ServiceError(f"Service {service} returned {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error calling {service}: {e}")
            raise ServiceError(f"Failed to call service {service}: {str(e)}")
    
    async def get(self, service: str, path: str, **kwargs) -> Dict[str, Any]:
        """GET request"""
        return await self._make_request("GET", service, path, **kwargs)
    
    async def post(self, service: str, path: str, **kwargs) -> Dict[str, Any]:
        """POST request"""
        return await self._make_request("POST", service, path, **kwargs)
    
    async def put(self, service: str, path: str, **kwargs) -> Dict[str, Any]:
        """PUT request"""
        return await self._make_request("PUT", service, path, **kwargs)
    
    async def delete(self, service: str, path: str, **kwargs) -> Dict[str, Any]:
        """DELETE request"""
        return await self._make_request("DELETE", service, path, **kwargs)


class CircuitBreaker:
    """Simple circuit breaker for fault tolerance"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func):
        """Decorator to wrap function with circuit breaker"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == "open":
                if (datetime.utcnow() - self.last_failure_time).total_seconds() > self.timeout:
                    self.state = "half-open"
                else:
                    raise CircuitBreakerOpen("Circuit breaker is open")
            
            try:
                result = await func(*args, **kwargs)
                self.on_success()
                return result
            except Exception as e:
                self.on_failure()
                raise
        
        return wrapper
    
    def on_success(self):
        """Reset failures on success"""
        self.failures = 0
        self.state = "closed"
    
    def on_failure(self):
        """Increment failures"""
        self.failures += 1
        self.last_failure_time = datetime.utcnow()
        if self.failures >= self.failure_threshold:
            self.state = "open"


# Service-specific client functions

async def get_customer_info(customer_id: str) -> Dict[str, Any]:
    """Get customer info from Customer Service"""
    async with ServiceClient() as client:
        return await client.get("customer", f"/customers/{customer_id}")


async def get_account_balance(account_id: str) -> Dict[str, Any]:
    """Get account balance from Account Service"""
    async with ServiceClient() as client:
        return await client.get("account", f"/accounts/{account_id}/balance")


async def get_credit_score(customer_id: str) -> Dict[str, Any]:
    """Get credit score from Credit Scoring Service"""
    async with ServiceClient() as client:
        return await client.get("credit-scoring", f"/score/{customer_id}")


async def assess_fraud_risk(
    customer_id: str,
    transaction_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Assess fraud risk from Fraud Detection Service"""
    async with ServiceClient() as client:
        return await client.post(
            "fraud-detection",
            "/assess-risk",
            json={
                "customer_id": customer_id,
                "transaction_data": transaction_data
            }
        )


async def validate_token(token: str) -> Dict[str, Any]:
    """Validate JWT token with Auth Service"""
    async with ServiceClient() as client:
        return await client.post("auth", "/validate-token", json={"token": token})


async def check_customer_kyc_status(customer_id: str) -> str:
    """Check if customer's KYC is verified"""
    try:
        customer_info = await get_customer_info(customer_id)
        return customer_info.get("kyc_status", "not_started")
    except Exception as e:
        logger.warning(f"Failed to check KYC status: {e}")
        return "unknown"


async def get_aggregate_risk_score(customer_id: str) -> float:
    """Get aggregate risk score from multiple services"""
    try:
        credit_score = await get_credit_score(customer_id)
        risk_score = credit_score.get("risk_score", 50.0)
        return risk_score
    except Exception as e:
        logger.warning(f"Failed to get aggregate risk score: {e}")
        return 50.0  # Default neutral score


class ServiceError(Exception):
    """Base exception for service communication errors"""
    pass


class ServiceTimeoutError(ServiceError):
    """Timeout error when calling another service"""
    pass


class CircuitBreakerOpen(ServiceError):
    """Circuit breaker is in open state"""
    pass
