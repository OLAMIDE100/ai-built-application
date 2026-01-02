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

## Mock Database

Currently uses an in-memory mock database (`app/database.py`). This will be replaced with a real database (PostgreSQL, MongoDB, etc.) later.

The mock database:
- Stores users and scores in memory
- Includes test data initialization
- Provides password hashing (bcrypt)
- Resets on server restart

## Environment Variables

For production, set these environment variables:

```bash
SECRET_KEY=your-secret-key-here  # Change from default!
DATABASE_URL=postgresql://...    # When implementing real DB
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

