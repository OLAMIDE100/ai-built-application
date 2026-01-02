from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from app.models import (
    ScoreSubmission, ScoreResponse, LeaderboardResponse, Score, GameMode
)
from app.database import db
from app.auth import get_current_user_id

router = APIRouter()


@router.get("/leaderboard", response_model=LeaderboardResponse, status_code=status.HTTP_200_OK)
async def get_leaderboard(
    limit: Optional[int] = Query(default=10, ge=1, le=100),
    mode: Optional[GameMode] = None
):
    """Get leaderboard with optional limit and mode filter"""
    scores_data = db.get_scores(limit=limit, mode=mode)
    
    scores = [
        Score(
            id=s["id"],
            userId=s["userId"],
            username=s["username"],
            score=s["score"],
            mode=GameMode(s["mode"]),
            timestamp=s["timestamp"],
            rank=s.get("rank")
        )
        for s in scores_data
    ]
    
    return LeaderboardResponse(success=True, leaderboard=scores)


@router.post("/scores", response_model=ScoreResponse, status_code=status.HTTP_201_CREATED)
async def submit_score(
    score_submission: ScoreSubmission,
    user_id: int = Depends(get_current_user_id)
):
    """Submit a new game score"""
    # Create score entry
    score_id = db.create_score(
        user_id=user_id,
        score=score_submission.score,
        mode=score_submission.mode
    )
    
    # Get the created score
    user = db.get_user_by_id(user_id)
    score_data = {
        "id": score_id,
        "userId": user_id,
        "username": user["username"],
        "score": score_submission.score,
        "mode": score_submission.mode.value,
        "timestamp": db.scores[score_id]["timestamp"]
    }
    
    score = Score(
        id=score_data["id"],
        userId=score_data["userId"],
        username=score_data["username"],
        score=score_data["score"],
        mode=GameMode(score_data["mode"]),
        timestamp=score_data["timestamp"]
    )
    
    return ScoreResponse(success=True, score=score)

