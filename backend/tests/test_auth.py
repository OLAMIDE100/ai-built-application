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
    # Truncate to 72 bytes safely
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


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_signup_success(clean_db):
    """Test successful user registration"""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": safe_password("password123")
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["user"]["username"] == "testuser"
    assert data["user"]["email"] == "testuser@example.com"
    assert "token" in data
    assert data["token"] is not None


def test_signup_duplicate_email(clean_db):
    """Test signup with duplicate email"""
    # First signup
    client.post(
        "/api/v1/auth/signup",
        json={
            "username": "user1",
            "email": "duplicate@example.com",
            "password": safe_password("password123")
        }
    )
    
    # Try to signup with same email
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "user2",
            "email": "duplicate@example.com",
            "password": safe_password("password123")
        }
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


def test_signup_duplicate_username(clean_db):
    """Test signup with duplicate username"""
    # First signup
    client.post(
        "/api/v1/auth/signup",
        json={
            "username": "duplicate",
            "email": "user1@example.com",
            "password": safe_password("password123")
        }
    )
    
    # Try to signup with same username
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "duplicate",
            "email": "user2@example.com",
            "password": safe_password("password123")
        }
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


def test_login_success(clean_db):
    """Test successful login"""
    # First create a user
    client.post(
        "/api/v1/auth/signup",
        json={
            "username": "loginuser",
            "email": "loginuser@example.com",
            "password": safe_password("password123")
        }
    )
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": safe_password("password123")
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["user"]["email"] == "loginuser@example.com"
    assert "token" in data
    assert data["token"] is not None


def test_login_invalid_credentials(clean_db):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": safe_password("wrongpassword")
        }
    )
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_login_wrong_password(clean_db):
    """Test login with wrong password"""
    # Create user
    client.post(
        "/api/v1/auth/signup",
        json={
            "username": "wrongpass",
            "email": "wrongpass@example.com",
            "password": safe_password("correctpassword")
        }
    )
    
    # Try login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": safe_password("wrongpassword")
        }
    )
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_get_current_user(clean_db):
    """Test getting current user with valid token"""
    # Signup and get token
    signup_response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "currentuser",
            "email": "currentuser@example.com",
            "password": safe_password("password123")
        }
    )
    assert signup_response.status_code == 201, f"Signup failed: {signup_response.json()}"
    signup_data = signup_response.json()
    assert "token" in signup_data, f"Token not found in response: {signup_data}"
    token = signup_data["token"]
    
    # Get current user
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "currentuser"
    assert data["email"] == "currentuser@example.com"


def test_get_current_user_no_token(clean_db):
    """Test getting current user without token"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403  # FastAPI returns 403 for missing auth


def test_logout(clean_db):
    """Test logout endpoint"""
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"success": True}

