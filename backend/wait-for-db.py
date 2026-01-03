#!/usr/bin/env python3
"""
Wait for PostgreSQL database to be ready
"""
import sys
import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_db(host, port, user, password, database, max_retries=30, delay=2):
    """Wait for database to be ready"""
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            conn.close()
            print("Database is ready!")
            return True
        except OperationalError:
            print(f"Waiting for database... (attempt {i+1}/{max_retries})")
            time.sleep(delay)
    
    print("Database is not ready after maximum retries")
    return False

if __name__ == "__main__":
    import os
    
    # Get database connection details from environment
    db_url = os.getenv("DATABASE_URL", "postgresql://snakegame:snakegame123@db:5432/snake_game")
    
    # Parse DATABASE_URL
    # Format: postgresql://user:password@host:port/database
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "")
    
    parts = db_url.split("@")
    if len(parts) != 2:
        print("Invalid DATABASE_URL format")
        sys.exit(1)
    
    user_pass = parts[0].split(":")
    host_db = parts[1].split("/")
    
    if len(user_pass) != 2 or len(host_db) != 2:
        print("Invalid DATABASE_URL format")
        sys.exit(1)
    
    user = user_pass[0]
    password = user_pass[1]
    host_port = host_db[0].split(":")
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 5432
    database = host_db[1]
    
    if not wait_for_db(host, port, user, password, database):
        sys.exit(1)

