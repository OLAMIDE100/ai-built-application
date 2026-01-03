import pytest
import uuid
from app.models import GameMode
from tests.conftest import safe_password, clean_db, client


@pytest.fixture
def auth_token(client, clean_db):
    """Create a user and return auth token and username"""
    # Generate unique username and email for each test to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    username = f"testplayer_{unique_id}"
    email = f"testplayer_{unique_id}@example.com"
    
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": username,
            "email": email,
            "password": safe_password("password123")
        }
    )
    assert response.status_code == 201, f"Signup failed with status {response.status_code}: {response.json()}"
    data = response.json()
    assert "token" in data, f"Token not found in response: {data}"
    # Return both token and username for tests that need the username
    return {"token": data["token"], "username": username}


def test_get_leaderboard(client, clean_db):
    """Test getting leaderboard"""
    response = client.get("/api/v1/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "leaderboard" in data
    assert isinstance(data["leaderboard"], list)


def test_get_leaderboard_with_limit(client, clean_db):
    """Test getting leaderboard with limit"""
    response = client.get("/api/v1/leaderboard?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["leaderboard"]) <= 5


def test_get_leaderboard_with_mode_filter(client, clean_db):
    """Test getting leaderboard filtered by mode"""
    response = client.get("/api/v1/leaderboard?mode=wall")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # All scores should be wall mode
    for score in data["leaderboard"]:
        assert score["mode"] == "wall"


def test_submit_score(client, clean_db, auth_token):
    """Test submitting a score"""
    response = client.post(
        "/api/v1/scores",
        json={
            "score": 250,
            "mode": "wall"
        },
        headers={"Authorization": f"Bearer {auth_token['token']}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["score"]["score"] == 250
    assert data["score"]["mode"] == "wall"
    assert data["score"]["username"] == auth_token["username"]


def test_submit_score_no_auth(client, clean_db):
    """Test submitting score without authentication"""
    response = client.post(
        "/api/v1/scores",
        json={
            "score": 100,
            "mode": "wall"
        }
    )
    assert response.status_code == 403  # FastAPI returns 403 for missing auth


def test_submit_score_negative(client, clean_db, auth_token):
    """Test submitting negative score (should fail validation)"""
    response = client.post(
        "/api/v1/scores",
        json={
            "score": -10,
            "mode": "wall"
        },
        headers={"Authorization": f"Bearer {auth_token['token']}"}
    )
    assert response.status_code == 422  # Validation error


def test_leaderboard_ordering(client, clean_db, auth_token):
    """Test that leaderboard is ordered by score descending"""
    # Submit multiple scores
    client.post(
        "/api/v1/scores",
        json={"score": 100, "mode": "wall"},
        headers={"Authorization": f"Bearer {auth_token['token']}"}
    )
    client.post(
        "/api/v1/scores",
        json={"score": 300, "mode": "wall"},
        headers={"Authorization": f"Bearer {auth_token['token']}"}
    )
    client.post(
        "/api/v1/scores",
        json={"score": 200, "mode": "wall"},
        headers={"Authorization": f"Bearer {auth_token['token']}"}
    )
    
    response = client.get("/api/v1/leaderboard?limit=10")
    assert response.status_code == 200
    scores = response.json()["leaderboard"]
    
    # Check that scores are in descending order
    for i in range(len(scores) - 1):
        assert scores[i]["score"] >= scores[i + 1]["score"]


def test_leaderboard_ranks(client, clean_db):
    """Test that leaderboard includes rank numbers"""
    response = client.get("/api/v1/leaderboard")
    assert response.status_code == 200
    scores = response.json()["leaderboard"]
    
    # Check that ranks are sequential starting from 1
    for i, score in enumerate(scores, start=1):
        assert score["rank"] == i

