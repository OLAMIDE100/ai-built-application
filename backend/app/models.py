from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from enum import Enum
from datetime import datetime


class GameMode(str, Enum):
    WALL = "wall"
    PASS = "pass"


# Authentication Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class SignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: EmailStr


class AuthResponse(BaseModel):
    success: bool
    user: User
    token: Optional[str] = None


# Leaderboard Models
class ScoreSubmission(BaseModel):
    score: int = Field(..., ge=0)
    mode: GameMode


class Score(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    userId: int
    username: str
    score: int
    mode: GameMode
    timestamp: int
    rank: Optional[int] = None


class LeaderboardResponse(BaseModel):
    success: bool
    leaderboard: List[Score]


class ScoreResponse(BaseModel):
    success: bool
    score: Score


# Players Models
class ActivePlayer(BaseModel):
    id: int
    username: str
    score: int
    mode: GameMode


class ActivePlayersResponse(BaseModel):
    success: bool
    players: List[ActivePlayer]


# Common Models
class SuccessResponse(BaseModel):
    success: bool


class ErrorResponse(BaseModel):
    success: bool = False
    error: str

