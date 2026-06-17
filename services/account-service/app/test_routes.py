"""Unit tests for the Account Service routes."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.models import Base

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_account.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in the test database
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override the get_db dependency to use the test database."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Apply the override to the app
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db():
    """Fixture to create and drop tables for each test function."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_account_success():
    """Test creating a new account successfully."""
    response = client.post(
        "/accounts",
        json={
            "customer_id": "cust_test_123",
            "account_type": "checking",
            "initial_balance": 500.0,
            "interest_rate": 0.01,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == "cust_test_123"
    assert data["account_type"] == "checking"
    assert data["balance"] == 500.0
    assert "account_number" in data
    assert data["account_number"].startswith("ACC-")


def test_get_account_not_found():
    """Test that fetching a non-existent account returns a 404 error."""
    response = client.get("/accounts/some-random-uuid")
    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"


def test_create_account_with_negative_balance():
    """Test that creating an account with a negative initial balance fails."""
    response = client.post(
        "/accounts",
        json={"customer_id": "cust_test_456", "account_type": "savings", "initial_balance": -100.0},
    )
    # Pydantic validation should catch this and return a 422
    assert response.status_code == 422