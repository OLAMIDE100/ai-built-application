from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, leaderboard, players

app = FastAPI(
    title="Snake Game API",
    description="RESTful API for the Snake Game multiplayer application",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5176",  # Vite default port
        "http://localhost:3000",     # Alternative frontend port
        "http://127.0.0.1:5173",    # Alternative localhost format
        "http://127.0.0.1:3000",
        "https://snake-game.nabuminds-test.app"    # Alternative localhost format
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(leaderboard.router, prefix="/api/v1", tags=["Leaderboard"])
app.include_router(players.router, prefix="/api/v1/players", tags=["Players"])


@app.get("/")
async def root():
    return {"message": "Snake Game API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

