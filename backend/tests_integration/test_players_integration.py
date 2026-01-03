"""
Integration tests for players endpoints
Tests the full flow: API -> Database -> Response
"""
import pytest
import time
from fastapi import status


def test_get_active_players_returns_empty_when_no_scores(client, test_db):
    """Test that active players endpoint returns empty when no scores exist"""
    response = client.get("/api/v1/players/active")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert len(data["players"]) == 0


def test_get_active_players_returns_recent_scores(client, auth_user, test_db):
    """Test that active players returns recent scores from database"""
    # Submit a score
    response = client.post(
        "/api/v1/scores",
        headers={"Authorization": f"Bearer {auth_user['token']}"},
        json={
            "score": 150,
            "mode": "wall"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    
    # Get active players
    response = client.get("/api/v1/players/active")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert len(data["players"]) >= 1
    
    # Check that the player data is correct
    player = data["players"][0]
    assert player["username"] == auth_user["username"]
    assert player["score"] == 150
    assert player["mode"] == "wall"
    assert "id" in player


def test_active_players_includes_multiple_users(client, test_db):
    """Test active players with multiple users"""
    # Create and submit score for user 1
    user1_response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "active1",
            "email": "active1@example.com",
            "password": "password123"
        }
    )
    user1_token = user1_response.json()["token"]
    
    client.post(
        "/api/v1/scores",
        headers={"Authorization": f"Bearer {user1_token}"},
        json={"score": 200, "mode": "wall"}
    )
    
    # Create and submit score for user 2
    user2_response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "active2",
            "email": "active2@example.com",
            "password": "password123"
        }
    )
    user2_token = user2_response.json()["token"]
    
    client.post(
        "/api/v1/scores",
        headers={"Authorization": f"Bearer {user2_token}"},
        json={"score": 180, "mode": "pass"}
    )
    
    # Get active players
    response = client.get("/api/v1/players/active")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["players"]) >= 2
    
    # Check usernames
    usernames = [player["username"] for player in data["players"]]
    assert "active1" in usernames
    assert "active2" in usernames

