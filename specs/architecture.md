# System Architecture: Phase II Todo Application

## Overview
The Phase II Todo application is a full-stack web application built with a Next.js frontend and FastAPI backend. It features secure user authentication with Better Auth and JWT tokens, persistent data storage with Neon PostgreSQL, and a responsive user interface.

## Architecture Layers

### Presentation Layer (Frontend)
- **Technology**: Next.js 16+ with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth client integration
- **API Communication**: Custom API client handling JWT tokens

Components:
- Authentication management (sign-in, sign-up, session)
- Task management UI (list, create, edit, delete)
- Responsive layout components
- Form handling and validation

### Application Layer (Backend)
- **Framework**: FastAPI
- **Language**: Python 3.10+
- **Database ORM**: SQLModel
- **Authentication**: JWT middleware
- **API Format**: REST with JSON

Components:
- Authentication service (JWT validation)
- Task management service (CRUD operations)
- User authorization service (user isolation)
- API route handlers

### Data Layer
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel
- **Authentication**: Managed by Better Auth

Components:
- Task data model
- User data model (via Better Auth)
- Connection pooling
- Database migrations

## Technology Stack Alignment

### Frontend Stack
- Next.js 16+ with App Router ✓
- TypeScript for type safety ✓
- Tailwind CSS for styling ✓
- Better Auth for authentication ✓
- JWT token handling ✓

### Backend Stack
- FastAPI framework ✓
- SQLModel ORM ✓
- Pydantic for data validation ✓
- JWT for authentication ✓
- Python 3.10+ ✓

### Database Stack
- Neon Serverless PostgreSQL ✓
- SQLModel for database operations ✓

### Authentication Stack
- Better Auth for user management ✓
- JWT tokens for API authentication ✓
- Shared secret for token validation ✓

## Data Flow Architecture

### Authentication Flow
1. User registers/signs in via Better Auth
2. Better Auth issues JWT token to frontend
3. Frontend stores token securely
4. Frontend includes token in Authorization header for API requests
5. Backend validates token and extracts user identity
6. Backend authorizes user actions based on extracted identity

### Task Management Flow
1. Frontend retrieves JWT token from session
2. Frontend makes authenticated API request
3. Backend validates JWT and user authorization
4. Backend performs database operation filtered by user_id
5. Backend returns result to frontend
6. Frontend updates UI with new data

## Security Architecture

### Authentication Security
- JWT tokens with proper expiration
- Shared secret (BETTER_AUTH_SECRET) for token validation
- Secure token storage and transmission
- Automatic session validation

### Authorization Security
- User isolation at API level (user_id validation)
- User isolation at database level (query filtering)
- Proper authorization checks on all endpoints
- Secure data access patterns

## API Architecture
- RESTful design principles
- Standard HTTP methods and status codes
- JWT-based authentication for all endpoints
- User-specific endpoints using user_id parameter
- Consistent error response format

## Deployment Architecture
- Frontend and backend deployed separately
- Database hosted separately on Neon
- Environment variable configuration
- CORS configuration for API communication
- SSL/TLS for secure communication