# Backend Guidelines (FastAPI Application)

## Stack
- FastAPI
- SQLModel (ORM)
- Pydantic (data validation)
- JWT (authentication)
- Neon PostgreSQL

## Project Structure
- `main.py` - FastAPI app entry point
- `models.py` - SQLModel database models
- `schemas/` - Pydantic models for request/response validation
- `routes/` - API route handlers
- `auth/` - Authentication and JWT middleware
- `database/` - Database connection and session management
- `dependencies/` - FastAPI dependencies

## API Conventions
- All routes under `/api/{user_id}/` for user context
- Return JSON responses using Pydantic models
- Handle errors with HTTPException
- Use proper HTTP status codes (200, 201, 400, 401, 403, 404, 500)
- Include JWT authentication on all protected endpoints

## Database
- Use SQLModel for all database operations
- Connection string from environment variable: DATABASE_URL
- Implement proper indexing for performance
- Use database sessions via dependency injection

## Authentication
- Implement JWT token verification middleware
- Validate that user_id in URL matches authenticated user
- Return 401 for invalid tokens
- Return 403 for unauthorized access attempts
- Store user_id in token for authorization

## Running
- Development: `uvicorn main:app --reload --port 8000`
- Production: `uvicorn main:app --host 0.0.0.0 --port 8000`

## Security
- Validate user_id matches authenticated user on all endpoints
- Implement proper input validation with Pydantic
- Use parameterized queries to prevent SQL injection
- Implement rate limiting if needed