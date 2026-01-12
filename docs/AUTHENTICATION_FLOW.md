# Authentication Flow Documentation

This document describes the authentication system implemented in the Full-Stack Todo Application, including the technology stack, flow diagrams, and implementation details.

## Overview

The application uses **Better Auth** for authentication with **JWT tokens** for secure communication between the frontend and backend. The system ensures user data isolation where each user can only access their own data.

## Technology Stack

- **Frontend**: Next.js 16+, TypeScript, Better Auth client
- **Backend**: FastAPI, SQLModel, JWT token verification
- **Authentication Provider**: Better Auth with custom JWT handling
- **Database**: Neon Serverless PostgreSQL
- **Token Storage**: localStorage (frontend), session table (backend)

## Authentication Architecture

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────┐
│   User      │    │   Frontend      │    │   Backend   │
│             │    │   (Next.js)     │    │  (FastAPI)  │
└──────┬──────┘    └──────┬──────────┘    └──────┬──────┘
       │                  │                      │
       │ 1. Login/Signup  │                      │
       │─────────────────▶│                      │
       │                  │                      │
       │                  │ 2. JWT Token         │
       │                  │◀─────────────────────│
       │                  │                      │
       │                  │ 3. Store in localStorage
       │                  │─────────────────────▶│
       │                  │                      │
       │ 4. API Request   │                      │
       │─────────────────▶│ 5. Verify JWT Token  │
       │                  │─────────────────────▶│
       │                  │                      │
       │                  │ 6. Validate User     │
       │                  │    Access Rights     │
       │                  │◀─────────────────────│
       │                  │                      │
       │                  │ 7. Return Data       │
       │                  │◀─────────────────────│
       │                  │                      │
       │ 8. Display Data  │                      │
       │◀─────────────────│                      │
```

## Authentication Flow Details

### 1. User Registration Flow

1. User navigates to `/auth/signup` page
2. User enters email, password, and name
3. Frontend validates input fields
4. Frontend calls Better Auth registration endpoint
5. Better Auth creates user record and session
6. Better Auth generates JWT token
7. JWT token is returned to frontend
8. Frontend stores JWT token in localStorage
9. User is redirected to dashboard

### 2. User Login Flow

1. User navigates to `/auth/signin` page
2. User enters email and password
3. Frontend validates input fields
4. Frontend calls Better Auth login endpoint
5. Better Auth verifies credentials
6. Better Auth generates new JWT token
7. JWT token is returned to frontend
8. Frontend stores JWT token in localStorage
9. User is redirected to dashboard

### 3. API Request Flow

1. Frontend prepares API request
2. Frontend retrieves JWT token from localStorage
3. Frontend adds token to Authorization header: `Authorization: Bearer <token>`
4. Frontend sends API request to backend
5. Backend receives request and extracts JWT token
6. Backend verifies token signature and validity
7. Backend decodes user information from token
8. Backend validates user has access to requested resource
9. Backend processes request and returns data
10. Frontend receives and displays data

### 4. Token Validation Flow

1. Request reaches authentication middleware
2. Middleware extracts JWT token from Authorization header
3. Middleware verifies token signature using secret key
4. Middleware checks token expiration
5. Middleware decodes user ID from token
6. Middleware queries user record to ensure account is active
7. If valid, request proceeds to route handler
8. If invalid, returns 401 Unauthorized response

## JWT Token Structure

The JWT tokens contain the following claims:

```json
{
  "sub": "user-id",
  "email": "user@example.com",
  "name": "User Name",
  "iat": 1704067200,
  "exp": 1704153600,
  "jti": "unique-token-id"
}
```

## Frontend Implementation

### API Client Authentication

The frontend API client automatically includes the JWT token in all requests:

```typescript
// lib/api.ts
const getAuthHeaders = () => {
  const token = localStorage.getItem('better-auth-token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
};

// All API calls include authentication headers
export const api = {
  getTasks: () => request('/api/tasks', { headers: getAuthHeaders() }),
  createTask: (data: any) => request('/api/tasks', {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data)
  }),
  // ... other authenticated endpoints
};
```

### Authentication State Management

The application manages authentication state using React Context:

```typescript
// context/AuthContext.tsx
interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (email: string, password: string, name: string) => Promise<void>;
  isAuthenticated: boolean;
}
```

## Backend Implementation

### Authentication Middleware

The backend uses middleware to protect routes and verify tokens:

```python
# backend/auth/middleware.py
def verify_token(token: str = Security(HTTPBearer())):
    try:
        # Decode and verify JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### User Data Isolation

All data access is filtered by the authenticated user's ID:

```python
# backend/routes/tasks.py
@app.get("/api/tasks")
def get_user_tasks(current_user: dict = Security(verify_token)):
    user_id = current_user["sub"]
    # Only return tasks belonging to authenticated user
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()
    return tasks
```

## Security Measures

### Token Security
- JWT tokens expire after 24 hours by default
- Tokens are signed with a strong secret key
- Tokens are transmitted over HTTPS only
- Tokens are stored securely in localStorage

### Session Management
- Sessions are tracked in the database
- Invalid sessions are immediately rejected
- Session cleanup occurs automatically
- Multiple device support with separate tokens

### Data Isolation
- Each user can only access their own data
- Database queries are filtered by user ID
- API responses only include authorized data
- Cross-user data access is prevented

## Error Handling

### Authentication Errors

- **401 Unauthorized**: Invalid or expired token
- **403 Forbidden**: Insufficient permissions
- **422 Validation Error**: Invalid request format

### Token Refresh

Currently, the system doesn't implement automatic token refresh. When a token expires:
1. API returns 401 Unauthorized
2. Frontend detects expired token
3. User is redirected to login page
4. User must log in again to continue

## Testing Authentication

### Unit Tests

Authentication functionality is covered by unit tests in `backend/tests/`:
- Authentication middleware validation
- Token verification and expiration
- User data isolation enforcement
- Error handling for invalid credentials

### Integration Tests

Integration tests verify the complete authentication flow:
- End-to-end registration and login
- API requests with valid/invalid tokens
- Data isolation between different users
- Session management functionality

## Performance Considerations

- JWT token verification is efficient and doesn't require database lookups
- Authentication middleware has minimal overhead
- Token validation happens in O(1) time complexity
- Caching can be implemented for frequently accessed user data