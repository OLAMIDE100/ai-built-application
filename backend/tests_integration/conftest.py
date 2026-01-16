"""
Shared fixtures for integration tests
Uses a real SQLite database (in-memory) for testing
"""
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.db_models import Base
from app.main import app
from app.database import Database
from app import database as database_module
from app import db_config


@pytest.fixture(scope="function")
def test_db():
    """
    Create an in-memory SQLite database for each test.
    This ensures complete isolation between tests.
    """
    # Create in-memory SQLite database
    test_db_url = "sqlite:///:memory:"
    
    # Create engine for test database
    test_engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Save original engine and session
    original_engine = db_config.engine
    original_session = db_config.SessionLocal
    
    # Replace with test engine
    db_config.engine = test_engine
    db_config.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    # Create new database instance (it will use the test engine via db_config)
    test_database = Database(initialize_test_data=False)
    
    # Replace the global db instance
    original_db = database_module.db
    database_module.db = test_database
    
    yield test_database
    
    # Cleanup: drop all tables
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    
    # Restore original database configuration
    db_config.engine = original_engine
    db_config.SessionLocal = original_session
    database_module.db = original_db


@pytest.fixture
def client(test_db):
    """Create a test client with the test database"""
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    """Create a test user and return auth token"""
    # Create a test user
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    return data["token"]


@pytest.fixture
def auth_user(client):
    """Create a test user and return user info and token"""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    return {
        "id": data["user"]["id"],
        "username": data["user"]["username"],
        "email": data["user"]["email"],
        "token": data["token"]
    }

