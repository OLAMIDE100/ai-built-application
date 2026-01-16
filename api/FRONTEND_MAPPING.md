# Frontend to Backend API Mapping

This document maps the frontend API service calls to the backend OpenAPI endpoints.

## Frontend API Service (`src/services/api.js`)

### Authentication

| Frontend Method | Backend Endpoint | Method | Description |
|----------------|------------------|--------|-------------|
| `api.login(email, password)` | `/auth/login` | POST | User authentication |
| `api.signup(username, email, password)` | `/auth/signup` | POST | User registration |
| `api.logout()` | `/auth/logout` | POST | User logout |
| `api.getCurrentUser()` | `/auth/me` | GET | Get current user |

### Leaderboard

| Frontend Method | Backend Endpoint | Method | Description |
|----------------|------------------|--------|-------------|
| `api.getLeaderboard(limit)` | `/leaderboard?limit={limit}` | GET | Get top scores |
| `api.submitScore(score, mode)` | `/scores` | POST | Submit game score |

### Players (Future/Removed from UI)

| Frontend Method | Backend Endpoint | Method | Description |
|----------------|------------------|--------|-------------|
| `api.getActivePlayers()` | `/players/active` | GET | Get active players |
| `api.watchPlayer(playerId)` | `/players/{playerId}/watch` | GET | Watch player game |

## Request/Response Mappings

### Login

**Frontend Call:**
```javascript
api.login('player1@example.com', 'password123')
```

**Backend Request:**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "player1@example.com",
  "password": "password123"
}
```

**Backend Response:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "player1",
    "email": "player1@example.com"
  }
}
```

**Note:** Backend should also return a JWT token (not in current mock). Consider adding:
```json
{
  "success": true,
  "user": { ... },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Signup

**Frontend Call:**
```javascript
api.signup('newplayer', 'newplayer@example.com', 'password123')
```

**Backend Request:**
```http
POST /api/v1/auth/signup
Content-Type: application/json

{
  "username": "newplayer",
  "email": "newplayer@example.com",
  "password": "password123"
}
```

**Backend Response:**
```json
{
  "success": true,
  "user": {
    "id": 3,
    "username": "newplayer",
    "email": "newplayer@example.com"
  }
}
```

### Get Leaderboard

**Frontend Call:**
```javascript
api.getLeaderboard(10)
```

**Backend Request:**
```http
GET /api/v1/leaderboard?limit=10
```

**Backend Response:**
```json
{
  "success": true,
  "leaderboard": [
    {
      "id": 3,
      "userId": 1,
      "username": "player1",
      "score": 200,
      "mode": "wall",
      "timestamp": 1704067200000,
      "rank": 1
    },
    ...
  ]
}
```

### Submit Score

**Frontend Call:**
```javascript
api.submitScore(150, 'wall')
```

**Backend Request:**
```http
POST /api/v1/scores
Authorization: Bearer <token>
Content-Type: application/json

{
  "score": 150,
  "mode": "wall"
}
```

**Backend Response:**
```json
{
  "success": true,
  "score": {
    "id": 4,
    "userId": 1,
    "username": "player1",
    "score": 150,
    "mode": "wall",
    "timestamp": 1704067200000
  }
}
```

## Authentication Flow

### Current Frontend Implementation (Mock)
- Uses in-memory `currentUser` variable
- No token storage

### Recommended Backend Implementation
1. **Login/Signup** → Returns JWT token
2. **Frontend** → Store token in localStorage/sessionStorage
3. **All authenticated requests** → Include `Authorization: Bearer <token>` header
4. **Backend** → Validate token on protected endpoints
5. **Logout** → Clear token from storage

### Frontend Changes Needed

Update `src/services/api.js` to:
1. Store JWT token after login/signup
2. Include token in Authorization header for authenticated requests
3. Handle token expiration/refresh
4. Clear token on logout

Example:
```javascript
// Store token
localStorage.setItem('authToken', token);

// Include in requests
headers: {
  'Authorization': `Bearer ${localStorage.getItem('authToken')}`
}
```

## Error Handling

Frontend expects error responses in format:
```json
{
  "success": false,
  "error": "Error message"
}
```

Backend should return appropriate HTTP status codes:
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid credentials, missing/invalid token)
- `409` - Conflict (email/username already exists)
- `500` - Internal Server Error

## Data Validation

### Frontend Validation (Client-side)
- Email format
- Password minimum length (6 characters)
- Username format (alphanumeric + underscore)

### Backend Validation (Server-side)
- All frontend validations should be re-checked
- Additional security checks
- SQL injection prevention
- XSS prevention
- Rate limiting

## Notes

1. **Game Mode**: Currently supports `'wall'` and `'pass'` - enum in OpenAPI spec
2. **Timestamps**: Unix timestamps in milliseconds (JavaScript Date.now() format)
3. **Score Ranking**: Backend should calculate rank when returning leaderboard
4. **User ID**: Backend should extract from JWT token for authenticated requests
5. **Username**: Can be included in score response for convenience (denormalized)

