"""
Database configuration and session management
Supports both PostgreSQL and SQLite
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.db_models import Base
import os
from typing import Generator

# Get database URL from environment variable, default to SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./snake_game.db"  # Default to SQLite for development
)

# Determine if we're using SQLite
IS_SQLITE = DATABASE_URL.startswith("sqlite")

# Engine configuration
if IS_SQLITE:
    # SQLite-specific configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        poolclass=StaticPool,  # SQLite doesn't support connection pooling
        echo=False,  # Set to True for SQL query logging
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        echo=False,  # Set to True for SQL query logging
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Use this in FastAPI route dependencies.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get a database session directly (for use outside of FastAPI routes).
    Remember to close it when done: db.close()
    """
    return SessionLocal()

