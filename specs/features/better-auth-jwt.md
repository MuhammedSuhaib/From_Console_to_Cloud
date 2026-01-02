# Authentication Implementation: Better Auth + JWT

## Overview
This document details the implementation of authentication for the Phase II Todo application using Better Auth with JWT tokens. This approach enables secure user sessions in the Next.js frontend while allowing the FastAPI backend to independently verify user identity.

## Architecture

### The Challenge
Better Auth is a JavaScript/TypeScript authentication library that runs on the **Next.js frontend**. However, the **FastAPI backend** is a separate Python service that needs to verify which user is making API requests.

### The Solution: JWT Tokens
Better Auth can be configured to issue **JWT (JSON Web Token)** tokens when users log in. These tokens are self-contained credentials that include user information and can be verified by any service that knows the secret key.

## How It Works

### 1. Authentication Flow
1. User logs in on Frontend → Better Auth creates a session and issues a JWT token
2. Frontend makes API call → Includes the JWT token in the Authorization: Bearer <token> header
3. Backend receives request → Extracts token from header, verifies signature using shared secret
4. Backend identifies user → Decodes token to get user ID, email, etc. and matches it with the user ID in the URL
5. Backend filters data → Returns only tasks belonging to that user

### 2. Component Changes Required

#### Better Auth Configuration
- Enable JWT plugin to issue tokens
- Configure token expiration times
- Set the shared secret (BETTER_AUTH_SECRET)

#### Frontend API Client
- Attach JWT token to every API request header
- Handle token refresh when expired
- Manage secure token storage

#### FastAPI Backend
- Add middleware to verify JWT and extract user
- Validate that the user ID in the token matches the user ID in the URL
- Handle token expiration and invalid token scenarios

#### API Routes
- Filter all queries by the authenticated user's ID
- Return 403 Forbidden for requests with mismatched user IDs

## Configuration Details

### The Shared Secret
Both frontend (Better Auth) and backend (FastAPI) must use the **same secret key** for JWT signing and verification. This is typically set via environment variable `BETTER_AUTH_SECRET` in both services.

### Environment Variables
```env
# Shared secret for JWT signing/verification
BETTER_AUTH_SECRET=your-super-secret-key-here

# API configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Security Benefits

### User Isolation
- Each user only sees their own tasks
- Database queries filtered by authenticated user ID
- API endpoints validate user ownership of resources

### Stateless Authentication
- Backend doesn't need to call frontend to verify users
- Fast, independent token verification
- Scalable authentication without session storage

### Token Expiry
- JWTs expire automatically (e.g., after 7 days)
- Automatic refresh mechanisms
- Enhanced security through limited token lifetime

### Independent Verification
- Frontend and backend can verify auth independently
- No shared database session required
- Resilient to service outages

## API Behavior with Authentication

### Before Auth (Phase I - CLI)
- No authentication required
- All operations performed directly

### After Auth (Phase II - Web)
- All endpoints require valid JWT token
- Requests without token receive 401 Unauthorized
- Each user only sees/modifies their own tasks
- Task ownership is enforced on every operation

## Implementation Requirements

### Frontend Requirements
- Better Auth configured with JWT plugin
- Secure token storage and retrieval
- Automatic token attachment to API calls
- Proper error handling for auth failures

### Backend Requirements
- JWT verification middleware
- User ID validation against URL parameters
- Proper HTTP status codes (401, 403)
- Consistent error response format

### Database Requirements
- User ID foreign key in all protected resources
- Queries filtered by authenticated user
- Proper indexing on user_id fields