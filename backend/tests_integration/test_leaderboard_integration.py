"""
Integration tests for leaderboard endpoints
Tests the full flow: API -> Database -> Response
"""
import pytest
import time
from fastapi import status
from app.models import GameMode


def test_submit_score_creates_entry_in_database(client, auth_token, test_db):
    """Test that submitting a score creates an entry in the database"""
    response = client.post(
        "/api/v1/scores",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "score": 100,
            "mode": "wall"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["success"] is True
    assert data["score"]["score"] == 100
    assert data["score"]["mode"] == "wall"
    assert "timestamp" in data["score"]
    assert "id" in data["score"]
    
    # Verify score exists in database
    scores = test_db.get_scores(limit=10)
    assert len(scores) == 1
    assert scores[0]["score"] == 100
    assert scores[0]["mode"] == "wall"


def test_get_leaderboard_returns_scores_from_database(client, auth_user, test_db):
    """Test that leaderboard returns scores from database"""
    # Submit multiple scores
    scores_to_submit = [
        {"score": 150, "mode": "wall"},
        {"score": 200, "mode": "pass"},
        {"score": 100, "mode": "wall"},
    ]
    
    for score_data in scores_to_submit:
        response = client.post(
            "/api/v1/scores",
            headers={"Authorization": f"Bearer {auth_user['token']}"},
            json=score_data
        )
        assert response.status_code == status.HTTP_201_CREATED
        time.sleep(0.01)  # Small delay to ensure different timestamps
    
    # Get leaderboard
    response = client.get("/api/v1/leaderboard")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert len(data["leaderboard"]) == 3
    
    # Scores should be ordered by score descending
    scores = data["leaderboard"]
    assert scores[0]["score"] >= scores[1]["score"]
    assert scores[1]["score"] >= scores[2]["score"]


def test_leaderboard_respects_limit(client, auth_user, test_db):
    """Test that leaderboard limit parameter works"""
    # Submit 5 scores
    for i in range(5):
        response = client.post(
            "/api/v1/scores",
            headers={"Authorization": f"Bearer {auth_user['token']}"},
            json={"score": 100 + i * 10, "mode": "wall"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        time.sleep(0.01)
    
    # Get leaderboard with limit=3
    response = client.get("/api/v1/leaderboard?limit=3")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["leaderboard"]) == 3


def test_leaderboard_filters_by_mode(client, auth_user, test_db):
    """Test that leaderboard can filter by game mode"""
    # Submit scores for both modes
    wall_scores = [{"score": 150, "mode": "wall"}, {"score": 200, "mode": "wall"}]
    pass_scores = [{"score": 100, "mode": "pass"}, {"score": 120, "mode": "pass"}]
    
    for score_data in wall_scores + pass_scores:
        response = client.post(
            "/api/v1/scores",
            headers={"Authorization": f"Bearer {auth_user['token']}"},
            json=score_data
        )
        assert response.status_code == status.HTTP_201_CREATED
        time.sleep(0.01)
    
    # Get leaderboard filtered by wall mode
    response = client.get("/api/v1/leaderboard?mode=wall")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["leaderboard"]) == 2
    assert all(score["mode"] == "wall" for score in data["leaderboard"])
    
    # Get leaderboard filtered by pass mode
    response = client.get("/api/v1/leaderboard?mode=pass")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["leaderboard"]) == 2
    assert all(score["mode"] == "pass" for score in data["leaderboard"])


def test_submit_score_requires_authentication(client, test_db):
    """Test that submitting a score requires authentication"""
    response = client.post(
        "/api/v1/scores",
        json={
            "score": 100,
            "mode": "wall"
        }
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_submit_score_includes_username(client, auth_user, test_db):
    """Test that submitted score includes the username"""
    response = client.post(
        "/api/v1/scores",
        headers={"Authorization": f"Bearer {auth_user['token']}"},
        json={
            "score": 250,
            "mode": "pass"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["score"]["username"] == auth_user["username"]
    assert data["score"]["userId"] == auth_user["id"]


def test_multiple_users_leaderboard(client, test_db):
    """Test leaderboard with scores from multiple users"""
    # Create first user and submit score
    user1_response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "player1",
            "email": "player1@example.com",
            "password": "password123"
        }
    )
    user1_token = user1_response.json()["token"]
    
    client.post(
        "/api/v1/scores",
        headers={"Authorization": f"Bearer {user1_token}"},
        json={"score": 300, "mode": "wall"}
    )
    
    # Create second user and submit score
    user2_response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "player2",
            "email": "player2@example.com",
            "password": "password123"
        }
    )
    user2_token = user2_response.json()["token"]
    
    client.post(
        "/api/v1/scores",
        headers={"Authorization": f"Bearer {user2_token}"},
        json={"score": 250, "mode": "wall"}
    )
    
    # Get leaderboard
    response = client.get("/api/v1/leaderboard")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["leaderboard"]) == 2
    
    # Check usernames are correct
    usernames = [score["username"] for score in data["leaderboard"]]
    assert "player1" in usernames
    assert "player2" in usernames
    
    # Highest score should be first
    assert data["leaderboard"][0]["score"] == 300
    assert data["leaderboard"][0]["username"] == "player1"


def test_score_timestamp_is_set(client, auth_token, test_db):
    """Test that score timestamp is automatically set"""
    from datetime import datetime
    
    # Use UTC time to match database
    before_time = int(datetime.utcnow().timestamp() * 1000)
    
    response = client.post(
        "/api/v1/scores",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "score": 100,
            "mode": "wall"
        }
    )
    
    after_time = int(datetime.utcnow().timestamp() * 1000)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    timestamp = data["score"]["timestamp"]
    
    # Timestamp should be between before and after (with small margin for processing time)
    assert before_time <= timestamp <= after_time + 1000  # Allow 1 second margin
    assert timestamp > 0  # Ensure timestamp is set

