import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import MockDatabase

client = TestClient(app)

# Helper to ensure passwords are safe for bcrypt (<= 72 bytes)
def safe_password(pwd: str) -> str:
    """Ensure password is <= 72 bytes for bcrypt"""
    pwd_bytes = pwd.encode('utf-8')
    if len(pwd_bytes) <= 72:
        return pwd
    # Truncate to 70 bytes safely
    truncated = pwd_bytes[:70]
    while truncated and (truncated[-1] & 0b11000000) == 0b10000000:
        truncated = truncated[:-1]
    return truncated.decode('utf-8', errors='ignore')


@pytest.fixture
def clean_db():
    """Create a fresh database instance for each test"""
    from app import database
    # Create database without test data initialization to avoid password issues
    database.db = MockDatabase(initialize_test_data=False)
    return database.db


def test_get_active_players(clean_db):
    """Test getting active players"""
    response = client.get("/api/v1/players/active")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "players" in data
    assert isinstance(data["players"], list)

