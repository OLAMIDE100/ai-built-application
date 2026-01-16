"""
Database initialization script
Run this to create database tables
"""
from app.db_config import init_db, DATABASE_URL, IS_SQLITE

def main():
    """Initialize database"""
    print(f"Initializing database: {DATABASE_URL}")
    print(f"Database type: {'SQLite' if IS_SQLITE else 'PostgreSQL'}")
    
    # Create tables
    init_db()
    print("✓ Database tables created")

if __name__ == "__main__":
    main()

