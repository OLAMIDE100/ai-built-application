# Snake Game Backend

FastAPI backend implementation for the Snake Game multiplayer application.

## Features

- ✅ User authentication (JWT-based)
- ✅ User registration and login
- ✅ Leaderboard with filtering
- ✅ Score submission
- ✅ Active players tracking (mock)
- ✅ Player watching (mock)
- ✅ Comprehensive test coverage

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── database.py          # Mock database implementation
│   ├── auth.py              # JWT authentication utilities
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # Authentication endpoints
│       ├── leaderboard.py   # Leaderboard endpoints
│       └── players.py        # Players endpoints
├── tests/
│   ├── __init__.py
│   ├── test_auth.py         # Authentication tests
│   ├── test_leaderboard.py  # Leaderboard tests
│   └── test_players.py      # Players tests
├── requirements.txt
├── pytest.ini
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the Server

```bash
uvicorn app.main:app --reload --port 8001
```

Or use the run script:
```bash
python run.py
```

The API will be available at `http://localhost:8001`

### 3. API Documentation

Once the server is running, you can access:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=app --cov-report=html
```

## API Endpoints

### Authentication

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/signup` - User registration
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user (requires auth)

### Leaderboard

- `GET /api/v1/leaderboard?limit=10&mode=wall` - Get leaderboard
- `POST /api/v1/scores` - Submit score (requires auth)

### Players

- `GET /api/v1/players/active` - Get active players
- `GET /api/v1/players/{playerId}/watch` - Watch player game

## Authentication

The API uses JWT Bearer token authentication:

1. Login or signup to get a token
2. Include token in requests: `Authorization: Bearer <token>`
3. Token expires after 30 minutes

### Example

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "player1@example.com", "password": "password123"}'

# Use token
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <your-token>"
```

## Database

The application uses SQLAlchemy with support for both **SQLite** (default) and **PostgreSQL**.

### Database Setup

1. **SQLite (Default - No setup required)**
   - SQLite is used by default for development
   - Database file: `snake_game.db` in the backend directory
   - No additional configuration needed

2. **PostgreSQL (Production)**
   - Set the `DATABASE_URL` in the `.env` file (see Environment Variables section below)
   - Make sure PostgreSQL is installed and running
   - Create the database: `createdb snake_game`

### Initialize Database

Run the initialization script to create tables:

```bash
python init_db.py
```

### Database Models

- **User**: Stores user accounts (id, username, email, password_hash, created_at)
- **Score**: Stores game scores (id, user_id, score, mode, timestamp)

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///./snake_game.db  # SQLite
# DATABASE_URL=postgresql://user:password@localhost:5432/snake_game  # PostgreSQL

# JWT Secret Key (change in production!)
SECRET_KEY=your-secret-key-here-change-in-production
```

## Next Steps

1. **Database Integration**: Replace mock database with PostgreSQL/MongoDB
2. **Environment Configuration**: Use environment variables for secrets
3. **WebSocket Support**: Add real-time game watching
4. **Rate Limiting**: Implement rate limiting for API endpoints
5. **Logging**: Add structured logging
6. **Monitoring**: Add health checks and metrics

## Development

### Code Style

The project follows PEP 8 style guidelines. Consider using:
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

### Adding New Endpoints

1. Create model in `app/models.py`
2. Add route in appropriate router file
3. Update database methods if needed
4. Add tests in `tests/`

## License

Part of the AI Dev Zoomcamp course.

