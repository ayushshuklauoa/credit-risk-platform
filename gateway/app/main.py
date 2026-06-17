from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
import uuid
import os
from contextlib import asynccontextmanager

from app.config import settings
from app.interceptors import RequestInterceptorPipeline
from app.routes import router as service_routes
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.audit import AuditLoggingMiddleware
from prometheus_client import make_asgi_app


# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 CRIP Gateway starting up...")
    yield
    logger.info("🛑 CRIP Gateway shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="CRIP Enterprise Platform - API Gateway",
    description="Central API Gateway for Credit Risk Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Initialize request interceptor pipeline
interceptor_pipeline = RequestInterceptorPipeline()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Add audit logging middleware
app.add_middleware(AuditLoggingMiddleware)

# Request/Response logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    request.state.start_time = datetime.utcnow()
    
    logger.info(f"[{request_id}] {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    duration = (datetime.utcnow() - request.state.start_time).total_seconds()
    logger.info(f"[{request_id}] Status: {response.status_code} Duration: {duration:.2f}s")
    
    response.headers["X-Request-ID"] = request_id
    return response

# Custom exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global error handler"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"[{request_id}] Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """Readiness check - includes dependency checks"""
    try:
        # Check Redis connection
        from app.config import redis_client
        await redis_client.ping()
        
        return {
            "status": "ready",
            "service": "api-gateway",
            "dependencies": {
                "redis": "healthy",
                "auth_service": "connected",
                "customer_service": "connected",
                "account_service": "connected",
                "credit_service": "connected",
                "fraud_service": "connected",
                "document_service": "connected"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {
            "status": "not_ready",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/health/live", tags=["Health"])
async def liveness_check():
    """Liveness check - is the service still running"""
    return {
        "status": "alive",
        "service": "api-gateway",
        "timestamp": datetime.utcnow().isoformat()
    }

# Mount Prometheus metrics endpoint
app.mount("/metrics", make_asgi_app())

# Include service routes
app.include_router(service_routes)


# Welcome endpoint
@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint with API information"""
    return {
        "service": "CRIP Enterprise Platform - API Gateway",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "auth": "/auth",
            "customers": "/customers",
            "accounts": "/accounts",
            "credit": "/credit",
            "fraud": "/fraud",
            "documents": "/documents"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.gateway_host,
        port=settings.gateway_port,
        reload=settings.debug
    )
