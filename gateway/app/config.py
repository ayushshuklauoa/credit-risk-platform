from pydantic_settings import BaseSettings
import os
from typing import Optional
import redis

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Gateway
    gateway_host: str = os.getenv("GATEWAY_HOST", "0.0.0.0")
    gateway_port: int = int(os.getenv("GATEWAY_PORT", "8000"))
    debug: bool = os.getenv("GATEWAY_DEBUG", "False").lower() == "true"
    
    # Service URLs
    auth_service_url: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    customer_service_url: str = os.getenv("CUSTOMER_SERVICE_URL", "http://localhost:8002")
    account_service_url: str = os.getenv("ACCOUNT_SERVICE_URL", "http://localhost:8003")
    credit_service_url: str = os.getenv("CREDIT_SERVICE_URL", "http://localhost:8004")
    fraud_service_url: str = os.getenv("FRAUD_SERVICE_URL", "http://localhost:8005")
    document_service_url: str = os.getenv("DOCUMENT_SERVICE_URL", "http://localhost:8006")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Auth
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiration_hours: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    # API Keys
    api_key_secret: str = os.getenv("API_KEY_SECRET", "your-api-key-secret")
    
    # Rate Limiting
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_period_seconds: int = int(os.getenv("RATE_LIMIT_PERIOD_SECONDS", "60"))
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    audit_log_enabled: bool = os.getenv("AUDIT_LOG_ENABLED", "True").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# Redis client
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

# Hardcoded service registry (can be replaced with service discovery)
SERVICE_REGISTRY = {
    "auth": settings.auth_service_url,
    "customer": settings.customer_service_url,
    "account": settings.account_service_url,
    "credit": settings.credit_service_url,
    "fraud": settings.fraud_service_url,
    "document": settings.document_service_url,
}
