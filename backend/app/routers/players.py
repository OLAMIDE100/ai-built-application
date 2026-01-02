from fastapi import APIRouter, status
from app.models import ActivePlayersResponse, ActivePlayer, GameMode
from app.database import db

router = APIRouter()


@router.get("/active", response_model=ActivePlayersResponse, status_code=status.HTTP_200_OK)
async def get_active_players():
    """
    Get list of currently active players.
    Note: This is a mock implementation. In a real system, this would track
    players who are currently in an active game session.
    """
    # Mock active players - in a real system, this would query active game sessions
    # For now, return top 3 players from recent scores
    recent_scores = db.get_scores(limit=3)
    
    players = [
        ActivePlayer(
            id=score["userId"],
            username=score["username"],
            score=score["score"],
            mode=GameMode(score["mode"])
        )
        for score in recent_scores
    ]
    
    return ActivePlayersResponse(success=True, players=players)

