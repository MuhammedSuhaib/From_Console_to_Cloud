# Phase II: Full-Stack Web Application Todo - Architecture Plan

## 1. Architecture Overview

### 1.1 System Context
The Phase II Todo application is a full-stack web application with a Next.js frontend, FastAPI backend, and Neon PostgreSQL database. The architecture implements secure user authentication with Better Auth and JWT tokens, ensuring user data isolation and secure API communication.

### 1.2 Architecture Style
- **Separation of Concerns**: Clear separation between frontend and backend services
- **API-First Design**: Backend exposes REST API consumed by frontend
- **Authentication-Driven**: Security-first approach with JWT token validation
- **Database-Centric**: PostgreSQL as the single source of truth for todos

## 2. Architecture Components

### 2.1 Frontend Layer (Next.js)
**Purpose**: User interface and client-side logic

**Components**:
- Next.js 16+ with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- Better Auth for authentication management
- API client for backend communication

**Key Elements**:
- `/app/` - Pages and layouts using App Router
- `/components/` - Reusable React components
- `/lib/api.ts` - API client with JWT token handling
- `/lib/auth.ts` - Authentication utilities

### 2.2 Backend Layer (FastAPI)
**Purpose**: Business logic, data persistence, and authentication

**Components**:
- FastAPI for REST API endpoints
- SQLModel for database ORM
- JWT middleware for token verification
- Pydantic models for request/response validation

**Key Elements**:
- `main.py` - FastAPI application entry point
- `models.py` - SQLModel database models
- `routes/tasks.py` - Task management endpoints
- `auth/jwt.py` - JWT token validation middleware
- `dependencies/user.py` - User authentication dependencies
- `schemas/task.py` - Pydantic models for tasks

### 2.3 Database Layer (Neon PostgreSQL)
**Purpose**: Persistent data storage with user isolation

**Components**:
- Neon Serverless PostgreSQL database
- SQLModel-based schema
- User and Task tables with proper relationships

## 3. Component Design

### 3.1 Database Schema (`backend/models.py`)
```python
from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Foreign key to Better Auth user
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    priority: Optional[TaskPriority] = Field(default=TaskPriority.medium)
    category: Optional[str] = Field(default=None, max_length=50)
    tags: List[str] = Field(default=[])
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class User(SQLModel, table=True):
    id: str = Field(primary_key=True)  # Better Auth user ID
    email: str = Field(unique=True)
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
```

### 3.2 Frontend API Client (`frontend/lib/api.ts`)
```typescript
interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high';
  category?: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

class ApiClient {
  private baseUrl: string;
  
  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  }

  private async request(url: string, options: RequestInit = {}) {
    const token = this.getAuthToken();
    const headers = {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    };

    const response = await fetch(`${this.baseUrl}${url}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      // Handle unauthorized - maybe redirect to login
      window.location.href = '/auth/signin';
      return;
    }

    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }

    return response.json();
  }

  private getAuthToken(): string | null {
    // Get JWT token from Better Auth session
    // Implementation depends on Better Auth integration
    if (typeof window !== 'undefined') {
      return localStorage.getItem('better-auth-token');
    }
    return null;
  }

  async getTasks(userId: string): Promise<Task[]> {
    return this.request(`/api/${userId}/tasks`);
  }

  async createTask(userId: string, task: Omit<Task, 'id' | 'user_id' | 'created_at' | 'updated_at'>): Promise<Task> {
    return this.request(`/api/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(task),
    });
  }

  async updateTask(userId: string, taskId: number, updates: Partial<Task>): Promise<Task> {
    return this.request(`/api/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deleteTask(userId: string, taskId: number): Promise<void> {
    await this.request(`/api/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  async toggleTaskCompletion(userId: string, taskId: number): Promise<Task> {
    return this.request(`/api/${userId}/tasks/${taskId}/complete`, {
      method: 'PATCH',
    });
  }
}

export const api = new ApiClient();
```

### 3.3 FastAPI Routes (`backend/routes/tasks.py`)
```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime
from ..models import Task
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse
from ..auth.jwt import get_current_user_id
from ..database import get_session

router = APIRouter(prefix="/api/{user_id}", tags=["tasks"])

@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    user_id: str,
    completed: Optional[bool] = None,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id)
):
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these tasks"
        )
    
    query = select(Task).where(Task.user_id == user_id)
    if completed is not None:
        query = query.where(Task.completed == completed)
    
    tasks = session.exec(query).all()
    return tasks

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    user_id: str,
    task: TaskCreate,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id)
):
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's tasks"
        )
    
    db_task = Task(
        user_id=user_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        category=task.category,
        tags=task.tags
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id)
):
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these tasks"
        )
    
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )
    
    return task

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id)
):
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's tasks"
        )
    
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if db_task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )
    
    # Update task fields
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(db_task, field, value)
    
    db_task.updated_at = datetime.now()
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.delete("/tasks/{task_id}")
async def delete_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id)
):
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's tasks"
        )
    
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if db_task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )
    
    session.delete(db_task)
    session.commit()
    return {"message": "Task deleted successfully"}

@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id)
):
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's tasks"
        )
    
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if db_task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )
    
    db_task.completed = not db_task.completed
    db_task.updated_at = datetime.now()
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task
```

## 4. File Structure

```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── auth/
│   │   ├── signin/
│   │   │   └── page.tsx
│   │   └── signup/
│   │       └── page.tsx
│   ├── dashboard/
│   │   └── page.tsx
│   └── globals.css
├── components/
│   ├── TaskList.tsx
│   ├── TaskForm.tsx
│   ├── TaskItem.tsx
│   └── AuthGuard.tsx
├── lib/
│   ├── api.ts
│   └── auth.ts
├── styles/
│   └── globals.css
├── CLAUDE.md
├── package.json
├── tsconfig.json
└── next.config.js

backend/
├── main.py
├── models.py
├── schemas/
│   ├── task.py
│   └── user.py
├── routes/
│   ├── tasks.py
│   └── auth.py
├── auth/
│   └── jwt.py
├── database/
│   └── __init__.py
├── dependencies/
│   └── user.py
├── CLAUDE.md
├── requirements.txt
└── alembic/
    └── env.py

docker-compose.yml
.env.example
README.md
CLAUDE.md
```

## 5. Technology Stack

### 5.1 Frontend Technology
- **Next.js 16+**: React framework with App Router for page routing
- **TypeScript**: Type safety for frontend code
- **Tailwind CSS**: Utility-first CSS framework
- **Better Auth**: Authentication library with JWT token support
- **React Hooks**: State management and side effects

### 5.2 Backend Technology
- **FastAPI**: High-performance Python web framework
- **SQLModel**: SQL database modeling library with Pydantic integration
- **Pydantic**: Data validation and settings management
- **JWT**: JSON Web Tokens for authentication
- **Neon PostgreSQL**: Serverless PostgreSQL database

### 5.3 Architecture Patterns
- **API-First Design**: Backend provides REST API consumed by frontend
- **Authentication Middleware**: JWT token verification on all protected routes
- **User Isolation**: All data access filtered by authenticated user ID
- **Type Safety**: TypeScript and Pydantic for data validation

## 6. Data Flow

### 6.1 Create Task Flow
1. User authenticates via Better Auth in frontend
2. Better Auth issues JWT token to frontend
3. User fills task creation form in Next.js app
4. Frontend API client adds JWT token to Authorization header
5. Request sent to FastAPI backend: `POST /api/{user_id}/tasks`
6. JWT middleware verifies token and extracts user ID
7. Backend validates that request user_id matches authenticated user
8. Task created in Neon PostgreSQL database with user_id association
9. Backend returns created task data to frontend
10. Frontend updates UI with new task

### 6.2 List Tasks Flow
1. Frontend retrieves JWT token from Better Auth session
2. Frontend API client makes request: `GET /api/{user_id}/tasks`
3. JWT middleware verifies token and extracts user ID
4. Backend validates that request user_id matches authenticated user
5. SQLModel query retrieves only tasks belonging to authenticated user
6. Tasks returned as JSON to frontend
7. Frontend displays tasks in responsive UI

### 6.3 Authentication Flow
1. User visits frontend application
2. If not authenticated, redirected to login page
3. User enters credentials → Better Auth frontend handles authentication
4. Better Auth creates session and issues JWT token
5. JWT token stored securely in frontend
6. All subsequent API requests include JWT token in header
7. Backend verifies token signature using shared secret (BETTER_AUTH_SECRET)
8. Backend extracts user ID from token and uses for authorization

## 7. Error Handling Strategy

### 7.1 Backend Error Handling
- Input validation using Pydantic models
- Proper HTTP status codes (401, 403, 404, 500)
- JWT token validation with appropriate responses
- Database operation error handling
- Proper error response formatting

### 7.2 Frontend Error Handling
- Network error handling in API client
- Authorization error handling with redirect to login
- User-friendly error messages
- Loading states for API operations
- Form validation feedback

## 8. Performance Considerations

### 8.1 Backend Performance
- Database indexing on user_id for efficient queries
- Connection pooling for database operations
- JWT token validation optimized with caching
- Proper pagination for large result sets

### 8.2 Frontend Performance
- Next.js code splitting and lazy loading
- React.memo for expensive components
- Optimistic updates for UI responsiveness
- Efficient rendering of task lists

## 9. Testing Strategy

### 9.1 Unit Tests
- Test backend API endpoint logic
- Test JWT token validation functions
- Test database model methods
- Test frontend component logic

### 9.2 Integration Tests
- Test API endpoints with authenticated requests
- Test user isolation (one user can't access another's data)
- Test authentication flow end-to-end
- Test API client functionality

### 9.3 Test Coverage
- 90%+ coverage for backend business logic
- Frontend component testing with Jest and React Testing Library
- Authentication flow testing
- Database operation testing

## 10. Security Considerations

### 10.1 Authentication Security
- JWT tokens with proper expiration times
- Secure secret key management (BETTER_AUTH_SECRET)
- Token refresh mechanisms
- Secure session management

### 10.2 Data Security
- User data isolation enforced at both API and database levels
- Input validation and sanitization
- Parameterized queries to prevent SQL injection
- Proper authorization checks on all endpoints

## 11. Deployment Strategy

### 11.1 Frontend Deployment
- Next.js static export or Vercel deployment
- Environment variable configuration for API URLs
- CDN distribution for static assets

### 11.2 Backend Deployment
- Containerized deployment with Docker
- Environment variable configuration for database connection
- Load balancing for multiple instances
- Health checks and monitoring

### 11.3 Database Deployment
- Neon Serverless PostgreSQL for scalability
- Connection string configuration via environment variables
- Backup and recovery procedures
- Database migration management

## 12. Maintenance and Evolution

### 12.1 Extension Points
- Additional task properties (due_date, subtasks) for Phase III+
- Additional user preferences and settings
- Team/collaboration features
- API rate limiting and analytics

### 12.2 Backward Compatibility
- Maintain API endpoint contracts for Phase III+ development
- Ensure Phase I CLI can potentially access Phase II data
- Follow semantic versioning for API changes