# Snake Game API Specification

This directory contains the OpenAPI specification for the Snake Game backend API.

## Files

- `openapi.yaml` - Complete OpenAPI 3.0.3 specification

## API Overview

The Snake Game API provides the following functionality:

### Authentication
- **POST /auth/login** - User login with email and password
- **POST /auth/signup** - User registration
- **POST /auth/logout** - User logout
- **GET /auth/me** - Get current authenticated user

### Leaderboard
- **GET /leaderboard** - Get top scores (with optional limit and mode filter)
- **POST /scores** - Submit a new game score (requires authentication)

### Players (Future Features)
- **GET /players/active** - Get list of active players
- **GET /players/{playerId}/watch** - Watch a specific player's game

## Authentication

The API uses JWT Bearer token authentication. After successful login, the client should:
1. Store the JWT token
2. Include it in the `Authorization` header for protected endpoints: `Authorization: Bearer <token>`

## Data Models

### User
```json
{
  "id": 1,
  "username": "player1",
  "email": "player1@example.com"
}
```

### Score
```json
{
  "id": 1,
  "userId": 1,
  "username": "player1",
  "score": 150,
  "mode": "wall",
  "timestamp": 1704067200000,
  "rank": 1
}
```

### Game Modes
- `wall` - Game ends when snake hits walls
- `pass` - Snake wraps around edges

## Response Format

All API responses follow a consistent format:

**Success:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error:**
```json
{
  "success": false,
  "error": "Error message"
}
```

## Status Codes

- `200` - Success
- `201` - Created (for POST requests that create resources)
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `409` - Conflict (e.g., email/username already exists)
- `500` - Internal Server Error

## Viewing the API Documentation

You can view and interact with the API documentation using:

1. **Swagger UI**: Import the `openapi.yaml` file into [Swagger Editor](https://editor.swagger.io/)
2. **Postman**: Import the OpenAPI spec into Postman
3. **Redoc**: Generate documentation using [Redoc](https://redocly.com/)

## Example Usage

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "player1@example.com",
    "password": "password123"
  }'
```

### Submit Score (with authentication)
```bash
curl -X POST http://localhost:8000/api/v1/scores \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "score": 150,
    "mode": "wall"
  }'
```

### Get Leaderboard
```bash
curl -X GET "http://localhost:8000/api/v1/leaderboard?limit=10&mode=wall"
```

## Implementation Notes

When implementing the backend:

1. **JWT Tokens**: Use a secure JWT library (e.g., `jsonwebtoken` for Node.js)
2. **Password Hashing**: Use bcrypt or similar for password storage
3. **Database**: Consider using PostgreSQL or MongoDB for persistence
4. **Validation**: Validate all input data according to the schema
5. **Error Handling**: Return appropriate HTTP status codes and error messages
6. **CORS**: Configure CORS to allow requests from the frontend
7. **Rate Limiting**: Consider implementing rate limiting for authentication endpoints

## Future Enhancements

- WebSocket support for real-time game watching
- Pagination for leaderboard
- User profiles and statistics
- Game replay functionality
- Multiplayer game sessions

