"""Fraud Detection Service - Real-time fraud detection and alert management"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

from .database import init_db
from .routes import router
from prometheus_client import make_asgi_app


# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Lifespan event handlers
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Fraud Detection Service starting up")
    init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Fraud Detection Service shutting down")

# Create FastAPI application
app = FastAPI(
    title="CRIP Fraud Detection Service",
    description="Real-time fraud detection, alert management, and anomaly detection",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus metrics endpoint
app.mount("/metrics", make_asgi_app())

# Include routes
app.include_router(router, prefix="/api/fraud", tags=["fraud-detection"])


# Health check endpoint
from datetime import datetime

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "fraud-detection-service",
        "timestamp": datetime.utcnow().isoformat()
    }
