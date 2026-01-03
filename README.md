# Snake Game - Multiplayer Application

A full-stack multiplayer Snake game application with authentication, leaderboards, and real-time features.

## Architecture

- **Frontend**: React 19 + Vite + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Containerization**: Docker Compose

## Quick Start with Docker

The easiest way to run the entire application:

```bash
# 1. Copy environment file (required - no defaults)
cp .env.example .env

# 2. Edit .env file with your values (especially SECRET_KEY and POSTGRES_PASSWORD)

# 3. Start all services
docker-compose up --build

# 4. Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8001
# API Docs: http://localhost:8001/docs
```

**Important:** The `.env` file is required. All environment variables must be set as there are no default values in `docker-compose.yml`.

See [DOCKER.md](./DOCKER.md) for detailed Docker documentation.

## Local Development

### Prerequisites

- Python 3.9+
- Node.js 20+
- PostgreSQL (optional, SQLite used by default)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Run server
python run.py
# Or: uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Backend will be available at http://localhost:8001

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at http://localhost:5173

### Environment Variables

#### Backend
Create a `.env` file in the `backend` directory:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/snake_game
# Or for SQLite (default):
# DATABASE_URL=sqlite:///./snake_game.db
SECRET_KEY=your-secret-key
```

#### Frontend
Create a `.env` file in the `frontend` directory:
```env
VITE_API_BASE_URL=http://localhost:8001/api/v1
```

## Testing

### Backend Tests

```bash
cd backend

# Unit tests
pytest tests/ -v

# Integration tests
pytest tests_integration/ -v

# All tests
pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run tests with UI
npm run test:ui
```

## Project Structure

```
Module_2_End_to_End_Application/
├── backend/              # FastAPI backend
│   ├── app/            # Application code
│   │   ├── routers/    # API routes
│   │   ├── models.py    # Pydantic models
│   │   ├── db_models.py # SQLAlchemy models
│   │   └── database.py  # Database operations
│   ├── tests/          # Unit tests
│   ├── tests_integration/ # Integration tests
│   └── Dockerfile      # Backend Docker image
├── frontend/           # React frontend
│   ├── src/
│   │   ├── components/ # React components
│   │   ├── services/   # API service
│   │   └── utils/      # Utilities
│   ├── nginx.conf      # Nginx configuration
│   └── Dockerfile      # Frontend Docker image
├── api/                # OpenAPI specifications
├── docker-compose.yml  # Docker Compose configuration
└── DOCKER.md          # Docker documentation
```

## Features

- ✅ User authentication (signup, login, logout)
- ✅ JWT token-based authentication
- ✅ Game modes (wall, pass-through)
- ✅ Score submission and leaderboard
- ✅ Real-time top 5 leaderboard on landing page
- ✅ Full leaderboard page
- ✅ Game pause/resume functionality
- ✅ PostgreSQL and SQLite support
- ✅ Docker Compose setup
- ✅ Comprehensive test coverage

## API Documentation

When the backend is running, visit:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

OpenAPI specification: [api/openapi.yaml](./api/openapi.yaml)

## License

MIT
