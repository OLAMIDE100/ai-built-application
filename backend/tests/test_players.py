import pytest
from tests.conftest import clean_db, client


def test_get_active_players(client, clean_db):
    """Test getting active players"""
    response = client.get("/api/v1/players/active")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "players" in data
    assert isinstance(data["players"], list)

