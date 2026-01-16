"""
Integration tests for authentication endpoints
Tests the full flow: API -> Database -> Response
"""
import pytest
from fastapi import status


def test_signup_creates_user_in_database(client, test_db):
    """Test that signup creates a user in the database"""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["success"] is True
    assert data["user"]["username"] == "newuser"
    assert data["user"]["email"] == "newuser@example.com"
    assert "token" in data
    
    # Verify user exists in database
    user = test_db.get_user_by_email("newuser@example.com")
    assert user is not None
    assert user["username"] == "newuser"
    assert user["email"] == "newuser@example.com"
    assert "password_hash" in user


def test_login_authenticates_existing_user(client, test_db):
    """Test that login works with a user in the database"""
    # First create a user
    signup_response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "loginuser",
            "email": "loginuser@example.com",
            "password": "password123"
        }
    )
    assert signup_response.status_code == status.HTTP_201_CREATED
    
    # Now login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "password123"
        }
    )
    
    assert login_response.status_code == status.HTTP_200_OK
    data = login_response.json()
    assert data["success"] is True
    assert data["user"]["email"] == "loginuser@example.com"
    assert "token" in data
    assert data["token"] is not None


def test_login_fails_with_wrong_password(client, test_db):
    """Test that login fails with incorrect password"""
    # Create user
    client.post(
        "/api/v1/auth/signup",
        json={
            "username": "wrongpass",
            "email": "wrongpass@example.com",
            "password": "correctpassword"
        }
    )
    
    # Try login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid" in response.json()["detail"].lower()


def test_get_current_user_returns_database_user(client, auth_token):
    """Test that /me endpoint returns the user from database"""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert "id" in data


def test_duplicate_email_signup_fails(client, test_db):
    """Test that signup with duplicate email fails and doesn't create duplicate"""
    # First signup
    response1 = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "user1",
            "email": "duplicate@example.com",
            "password": "password123"
        }
    )
    assert response1.status_code == status.HTTP_201_CREATED
    
    # Try to signup with same email
    response2 = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "user2",
            "email": "duplicate@example.com",
            "password": "password123"
        }
    )
    
    assert response2.status_code == status.HTTP_409_CONFLICT
    
    # Verify only one user exists with that email
    user = test_db.get_user_by_email("duplicate@example.com")
    assert user is not None
    assert user["username"] == "user1"  # First user, not second


def test_duplicate_username_signup_fails(client, test_db):
    """Test that signup with duplicate username fails"""
    # First signup
    response1 = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "duplicate",
            "email": "user1@example.com",
            "password": "password123"
        }
    )
    assert response1.status_code == status.HTTP_201_CREATED
    
    # Try to signup with same username
    response2 = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "duplicate",
            "email": "user2@example.com",
            "password": "password123"
        }
    )
    
    assert response2.status_code == status.HTTP_409_CONFLICT


def test_password_is_hashed_in_database(client, test_db):
    """Test that passwords are stored as hashes, not plaintext"""
    password = "password123"
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "hashtest",
            "email": "hashtest@example.com",
            "password": password
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    
    # Get user from database
    user = test_db.get_user_by_email("hashtest@example.com")
    assert user is not None
    assert "password_hash" in user
    # Password should be hashed, not plaintext
    assert user["password_hash"] != password
    assert len(user["password_hash"]) > len(password)  # Hash is longer
    
    # But we should be able to verify it
    assert test_db.verify_password(password, user["password_hash"])


def test_logout_endpoint(client):
    """Test logout endpoint"""
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"success": True}

