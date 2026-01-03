# Docker Setup Guide

This project uses Docker Compose to run the entire application stack with PostgreSQL, FastAPI backend, and React frontend served by Nginx.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Quick Start

1. **Copy the environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** (required - no defaults in docker-compose.yml):
   ```bash
   # Update these values - especially for production
   POSTGRES_PASSWORD=your-secure-password
   SECRET_KEY=your-secret-key-use-a-long-random-string
   ```
   
   **Important:** The `.env` file is required. All environment variables must be set as there are no default values in `docker-compose.yml`.

3. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost:8001
   - API Docs: http://localhost:8001/docs

## Services

### PostgreSQL Database (`db`)
- **Port:** 5432 (default)
- **Database:** `snake_game` (default)
- **User:** `snakegame` (default)
- **Password:** Set in `.env` file
- **Data Persistence:** Data is stored in a Docker volume `postgres_data`

### Backend API (`backend`)
- **Port:** 8001 (default)
- **Framework:** FastAPI
- **Database:** Connects to PostgreSQL
- **Health Check:** http://localhost:8001/health
- **API Documentation:** http://localhost:8001/docs

### Frontend (`frontend`)
- **Port:** 80 (default)
- **Server:** Nginx
- **Framework:** React (Vite)
- **API Proxy:** API calls are proxied through Nginx to the backend

## Docker Compose Commands

### Start services in detached mode:
```bash
docker-compose up -d
```

### View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Stop services:
```bash
docker-compose down
```

### Stop and remove volumes (⚠️ deletes database data):
```bash
docker-compose down -v
```

### Rebuild specific service:
```bash
docker-compose build backend
docker-compose up -d backend
```

### Execute commands in containers:
```bash
# Backend shell
docker-compose exec backend bash

# Database shell
docker-compose exec db psql -U snakegame -d snake_game

# Frontend shell (nginx)
docker-compose exec frontend sh
```

## Environment Variables

Create a `.env` file in the root directory. You can copy from `.env.example`:

```bash
cp .env.example .env
```

Then edit `.env` with your values:

```env
# PostgreSQL Configuration
POSTGRES_USER=snakegame
POSTGRES_PASSWORD=snakegame123
POSTGRES_DB=snake_game
POSTGRES_PORT=5432

# Backend Configuration
BACKEND_PORT=8001
SECRET_KEY=your-secret-key-change-in-production-use-a-long-random-string
ALGORITHM=HS256

# Frontend Configuration
FRONTEND_PORT=80
VITE_API_BASE_URL=/api/v1
```

**Note:** All environment variables are required. There are no default values in `docker-compose.yml`, so the `.env` file must exist and contain all variables.

## Database Management

### Initialize Database
The database is automatically initialized when the backend starts. Tables are created via `init_db.py`.

### Access Database
```bash
# Using psql
docker-compose exec db psql -U snakegame -d snake_game

# Or connect from host (if port is exposed)
psql -h localhost -p 5432 -U snakegame -d snake_game
```

### Backup Database
```bash
docker-compose exec db pg_dump -U snakegame snake_game > backup.sql
```

### Restore Database
```bash
docker-compose exec -T db psql -U snakegame snake_game < backup.sql
```

## Development

### Hot Reload
For development with hot reload, you can mount volumes:

```yaml
# Already configured in docker-compose.yml
volumes:
  - ./backend:/app
```

Changes to backend code will require a container restart:
```bash
docker-compose restart backend
```

### Frontend Development
For frontend development, it's recommended to run the Vite dev server locally:
```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:5173 and will connect to the Docker backend.

## Troubleshooting

### Port Already in Use
If ports 80, 8001, or 5432 are already in use, update the `.env` file:
```env
FRONTEND_PORT=8080
BACKEND_PORT=8002
POSTGRES_PORT=5433
```

### Database Connection Issues
1. Check if the database is healthy:
   ```bash
   docker-compose ps
   ```

2. Check database logs:
   ```bash
   docker-compose logs db
   ```

3. Wait for database to be ready (backend automatically waits):
   ```bash
   docker-compose logs backend
   ```

### Frontend Not Loading
1. Check if frontend container is running:
   ```bash
   docker-compose ps frontend
   ```

2. Check nginx logs:
   ```bash
   docker-compose logs frontend
   ```

3. Rebuild frontend:
   ```bash
   docker-compose build frontend
   docker-compose up -d frontend
   ```

### Backend Not Starting
1. Check backend logs:
   ```bash
   docker-compose logs backend
   ```

2. Verify database is ready:
   ```bash
   docker-compose exec db pg_isready -U snakegame
   ```

3. Check environment variables:
   ```bash
   docker-compose exec backend env | grep DATABASE
   ```

## Production Considerations

For production deployment:

1. **Change default passwords** in `.env`
2. **Use strong SECRET_KEY** for JWT tokens
3. **Enable SSL/TLS** (use reverse proxy like Traefik or Nginx with Let's Encrypt)
4. **Set up database backups**
5. **Use environment-specific configurations**
6. **Monitor logs and health checks**
7. **Consider using Docker secrets** for sensitive data
8. **Set resource limits** in docker-compose.yml

## Network Architecture

```
Browser
  │
  ├─→ Frontend (Nginx) :80
  │     │
  │     ├─→ Serves static files
  │     │
  │     └─→ Proxies /api/* → Backend:8001
  │
  └─→ Backend (FastAPI) :8001
        │
        └─→ PostgreSQL :5432
```

All services communicate through the `snake_game_network` Docker network.

