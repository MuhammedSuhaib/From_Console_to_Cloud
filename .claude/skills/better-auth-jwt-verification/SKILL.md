---
name: "better-auth-jwt-verification"
description: "Expert skill for implementing Better Auth with JWT tokens for secure authentication between Next.js frontend and FastAPI backend. Handles JWT verification through session table lookup in shared database, secure API communication, and user isolation. Includes setup for database integration, session management, and JWT-only backend verification. Use when implementing authentication between frontend (Next.js) and backend (FastAPI) services with Better Auth JWT tokens and user isolation."
---

# Better Auth JWT Verification Implementation Skill

## When to Use This Skill

- User wants to implement Better Auth with JWT tokens for Next.js + FastAPI authentication
- Need to set up secure communication between frontend and backend services
- Want to implement user isolation with JWT token verification
- Need JWT token verification without custom auth logic on backend
- Looking for stateless authentication using shared database session verification

## How This Skill Works (Step-by-Step Execution)

1. **Better Auth Configuration**
   - Set up Better Auth with database connection (PostgreSQL recommended)
   - Enable email/password and social authentication
   - Configure session management and expiration

2. **Frontend Integration**
   - Implement Better Auth client for login/signup
   - Store JWT tokens from Better Auth in localStorage/session storage
   - Send JWT tokens in Authorization header for protected API calls

3. **Backend JWT Verification** (Database Lookup Approach)
   - Create middleware to verify JWT tokens using Better Auth's session table
   - Query the database directly to validate session tokens
   - Extract user ID from verified session records
   - Implement proper error handling for invalid/expired tokens

4. **Secure API Implementation**
   - Protect API routes with JWT verification
   - Implement user isolation (each request only accesses authorized user's data)
   - Add proper error handling for token issues
   - Configure environment variables for shared secrets

## Output You Will Receive

After activation, I will deliver:

- Complete Better Auth configuration with database integration
- Frontend implementation for Better Auth integration
- Backend JWT verification using database session lookup
- Protected API route examples with user isolation
- Environment variable setup for both services
- Error handling and security best practices
- Test suite for verification and validation

## Example Usage

**User says:**
"I have a Next.js application with Better Auth and need to secure my FastAPI backend."

**This Skill Instantly Activates → Delivers:**

- Better Auth configuration in Next.js
- Database session setup in Better Auth
- FastAPI JWT verification middleware using database lookup
- Protected route examples with user isolation
- Complete setup for secure frontend-backend communication

**User says:**
"Implement JWT verification between my Next.js and FastAPI application."

**This Skill Responds:**
→ Sets up Better Auth for JWT generation on frontend
→ Creates database-based verification in FastAPI backend
→ Implements user isolation for data access
→ Provides comprehensive security and testing

## Activate This Skill By Saying

- "Set up Better Auth with JWT verification"
- "Secure my FastAPI backend with Better Auth JWT tokens"
- "Implement JWT token verification between Next.js and FastAPI"
- "I need user isolation with JWT verification"
- "Verify Better Auth tokens in FastAPI backend"

## Core Implementation Steps

### 1. Better Auth Setup (Frontend)
```typescript
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET!,
  database: {
    uri: process.env.DATABASE_URL!,
  },
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },
  session: {
    expiresIn: 7 * 24 * 60 * 60,
  },
  cookies: {
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
  },
});
```

### 2. Better Auth API Route (Next.js App Router)
```typescript
// app/api/auth/[...betterauth]/route.ts
import { auth } from "../../../../lib/auth";
import { withCors } from "../../../../lib/auth";

const handler = auth.handleRequest;

export { handler as GET, handler as POST };
export const OPTIONS = withCors(async () => {
    return new Response(null, { status: 204 });
});
```

### 3. FastAPI JWT Verification (Database Lookup Approach)
```python
import logging
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlmodel import Session
from database import get_session
import sqlalchemy
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
security = HTTPBearer()

def get_current_user_id(
    creds = Depends(security),
    db: Session = Depends(get_session)
) -> str:
    token = creds.credentials

    try:
        # Query the session table directly - Better Auth stores tokens in the database
        # userId and expiresAt are standard Better Auth columns
        result = db.execute(
            sqlalchemy.text('SELECT "userId", "expiresAt" FROM "session" WHERE "token" = :t'),
            {"t": token}
        ).fetchone()

        if not result:
            logger.warning(f"Session not found for token: {token[:10]}...")
            raise Exception("Session invalid")

        user_id, expires_at = result

        # Convert expires_at to datetime if it's a string
        if isinstance(expires_at, str):
            from datetime import datetime
            expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))

        # Check if expired
        if expires_at < datetime.now():
            logger.warning("Session expired")
            raise Exception("Session expired")

        logger.info(f"Authenticated user: {user_id}")
        return str(user_id)

    except Exception as e:
        logger.error(f"Auth failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Not authenticated")
```

### 4. Protected Routes with User Isolation
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from models import Task
from auth.jwt import get_current_user_id
from database import get_session

router = APIRouter(prefix="/api", tags=["tasks"])

@router.get("/tasks")
def list_tasks(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),  # User ID from JWT verification
):
    # Only return tasks belonging to the authenticated user
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()
    return {"data": tasks}

@router.post("/tasks")
def create_task(
    task: TaskCreate,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),  # User ID from JWT verification
):
    # Assign task to authenticated user ID from JWT
    db_task = Task(**task.dict(), user_id=user_id)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return {"data": db_task}
```

### 5. Frontend API Client with JWT Token
```typescript
const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL!;

async function request<T>(path: string, options: RequestInit = {}) {
  const token = localStorage.getItem('auth_token'); // JWT token from Better Auth

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });

  if (res.status === 401) {
    // Token is invalid/expired, clear it and redirect to login
    localStorage.removeItem('auth_token');
    window.location.href = '/auth/signin';
    throw new Error('Unauthorized: Please login again');
  }

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'API error');
  }

  return res.json().data as T;
}
```

### 6. Environment Configuration
```
# Backend
DATABASE_URL=postgresql://user:password@host:port/database
BETTER_AUTH_SECRET=your_secret_key

# Frontend
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```
