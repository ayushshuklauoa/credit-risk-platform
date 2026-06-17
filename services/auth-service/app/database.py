"""Auth Service Database Configuration"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv(
    "AUTH_DATABASE_URL",
    "postgresql://auth_user:auth_password@postgres-auth:5432/auth_db"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "False").lower() == "true",
    pool_size=50,
    max_overflow=100,
    pool_timeout=30,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    from app.models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Auth Service database initialized")


def drop_db():
    """Drop all tables (for development/testing)"""
    from app.models import Base
    Base.metadata.drop_all(bind=engine)
    logger.info("❌ Auth Service database dropped")
