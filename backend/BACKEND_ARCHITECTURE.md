## Directory Structure
```
 Directory of D:\VScode\GitHub\From_Console_to_Cloud\backend

__pycache__/
auth/
database/
models/
routes/
schemas/
.env
.gitignore
Dockerfile
auth.db
deploy_hf.sh
main.py
models.py
requirements.txt
space.yaml
update_neon_schema.sql
```

# auth\jwt.py
```python
import logging
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlmodel import Session, select
from database import get_session
import sqlalchemy
from datetime import datetime

logger = logging.getLogger(__name__)

security = HTTPBearer()

def get_current_user_id(
    creds = Depends(security),
    db: Session = Depends(get_session)
) -> str:
    token = creds.credentials

    try:
        # Check the 'session' table that Better Auth created
        # Look for a session that matches the token and hasn't expired
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

# database\__init__.py
```python
import logging
from sqlmodel import Session, create_engine, SQLModel
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing")

logger.info(f"Connecting to database: {DATABASE_URL.replace('@', '[@]').replace(':', '[:]') if DATABASE_URL else 'None'}")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """Create database tables"""
    logger.info("Creating database tables...")
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

def get_session():
    logger.debug("Opening database session")
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Error in database session: {str(e)}")
            raise
        finally:
            logger.debug("Closing database session")
```

# main.py
```python
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import tasks
from database import create_db_and_tables
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(title="Todo API on Hugging Face")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://console-to-cloud.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)

@app.on_event("startup")
def startup():
    logger.info("Starting up the application...")
    try:
        create_db_and_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Todo API running on Hugging Face Spaces!"}

@app.get("/health")
def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}

# For Hugging Face Spaces
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))
```

# models.py
```python
from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlalchemy import JSON


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: TaskPriority = TaskPriority.medium
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list, sa_type=JSON)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

# models\user.py
```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

# routes\tasks.py
```python
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime
from models import Task
from schemas.tasks import TaskCreate, TaskUpdate, TaskResponse
from database import get_session
from auth.jwt import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["tasks"])


@router.get("/tasks")
def list_tasks(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
):
    logger.info(f"Fetching tasks for user_id: {user_id}")
    try:
        tasks = session.exec(
            select(Task).where(Task.user_id == user_id)
        ).all()
        logger.info(f"Found {len(tasks)} tasks for user_id: {user_id}")
        return {"data": tasks}
    except Exception as e:
        logger.error(f"Error fetching tasks for user_id {user_id}: {str(e)}")
        raise


@router.post("/tasks")
def create_task(
    task: TaskCreate,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
):
    logger.info(f"Creating task for user_id: {user_id}, task data: {task}")
    try:
        db_task = Task(**task.dict(), user_id=user_id)
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        logger.info(f"Created task with id: {db_task.id} for user_id: {user_id}")
        return {"data": db_task}
    except Exception as e:
        logger.error(f"Error creating task for user_id {user_id}: {str(e)}")
        raise


@router.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    updates: TaskUpdate,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
):
    logger.info(f"Updating task {task_id} for user_id: {user_id}, updates: {updates}")
    try:
        task = session.get(Task, task_id)
        if not task or task.user_id != user_id:
            logger.warning(f"Task {task_id} not found or user_id mismatch for user_id: {user_id}")
            raise HTTPException(status_code=404)

        for k, v in updates.dict(exclude_unset=True).items():
            setattr(task, k, v)

        task.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(task)
        logger.info(f"Updated task {task_id} successfully")
        return {"data": task}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id} for user_id {user_id}: {str(e)}")
        raise


@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
):
    logger.info(f"Deleting task {task_id} for user_id: {user_id}")
    try:
        task = session.get(Task, task_id)
        if not task or task.user_id != user_id:
            logger.warning(f"Task {task_id} not found or user_id mismatch for user_id: {user_id}")
            raise HTTPException(status_code=404)

        session.delete(task)
        session.commit()
        logger.info(f"Deleted task {task_id} successfully")
        return {"data": {"ok": True}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id} for user_id {user_id}: {str(e)}")
        raise


@router.patch("/tasks/{task_id}/complete")
def toggle_complete(
    task_id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
):
    logger.info(f"Toggling completion for task {task_id} for user_id: {user_id}")
    try:
        task = session.get(Task, task_id)
        if not task or task.user_id != user_id:
            logger.warning(f"Task {task_id} not found or user_id mismatch for user_id: {user_id}")
            raise HTTPException(status_code=404)

        task.completed = not task.completed
        task.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(task)
        logger.info(f"Toggled completion for task {task_id}, now completed: {task.completed}")
        return {"data": task}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling completion for task {task_id} for user_id {user_id}: {str(e)}")
        raise
```

# schemas\tasks.py
```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.medium
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    completed: Optional[bool] = None


class TaskResponse(TaskBase):
    id: int
    user_id: str
    completed: bool
    created_at: datetime
    updated_at: datetime
```

