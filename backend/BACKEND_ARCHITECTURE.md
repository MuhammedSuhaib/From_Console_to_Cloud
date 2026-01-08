## Directory Structure
```
 Directory of D:\VScode\GitHub\From_Console_to_Cloud\backend

Microsoft Windows [Version 10.0.19045.6466]
(c) Microsoft Corporation. All rights reserved.

D:\VScode\GitHub\From_Console_to_Cloud\backend>d:\VScode\GitHub\From_Console_to_Cloud\.venv\Scripts\activate.bat

(cli-todo) D:\VScode\GitHub\From_Console_to_Cloud\backend>dir /s
 Volume in drive D is New Volume
 Volume Serial Number is DC90-C5B0

 Directory of D:\VScode\GitHub\From_Console_to_Cloud\backend  

01/08/2026  02:16 PM    <DIR>          .
01/08/2026  02:16 PM    <DIR>          ..
01/07/2026  03:33 PM               518 .env
01/02/2026  11:53 PM               449 .env.example
01/03/2026  01:47 AM                38 .env.local
01/03/2026  02:08 AM               543 .gitignore
01/08/2026  01:47 PM               779 app.py
01/07/2026  03:07 PM    <DIR>          auth
01/08/2026  02:20 PM             7,519 BACKEND_ARCHITECTURE.md
01/03/2026  02:08 AM             1,611 CLAUDE.md
01/07/2026  03:20 PM    <DIR>          database
01/08/2026  01:48 PM             1,119 deploy_hf.sh
01/08/2026  01:52 PM               266 Dockerfile
01/08/2026  01:50 PM               910 main.py
01/07/2026  02:46 PM               735 models.py
01/08/2026  01:48 PM               667 README.md
01/03/2026  02:08 AM               181 requirements.txt      
01/07/2026  03:20 PM    <DIR>          routes
01/07/2026  03:20 PM    <DIR>          schemas
01/08/2026  01:52 PM                31 space.yaml
01/07/2026  03:28 PM               487 update_neon_schema.sql
01/07/2026  03:20 PM    <DIR>          __pycache__
              15 File(s)         15,853 bytes

 Directory of D:\VScode\GitHub\From_Console_to_Cloud\backend\auth

01/07/2026  03:07 PM    <DIR>          .
01/07/2026  03:07 PM    <DIR>          ..
01/07/2026  02:46 PM               800 jwt.py
               1 File(s)            800 bytes

 Directory of D:\VScode\GitHub\From_Console_to_Cloud\backend\database

01/07/2026  03:20 PM    <DIR>          .
01/07/2026  03:20 PM    <DIR>          ..
01/07/2026  02:10 PM               352 __init__.py
01/07/2026  03:20 PM    <DIR>          __pycache__
               1 File(s)            352 bytes

 Directory of D:\VScode\GitHub\From_Console_to_Cloud\backend\database\__pycache__

01/07/2026  03:20 PM    <DIR>          .
01/07/2026  03:20 PM    <DIR>          ..
01/07/2026  03:20 PM               906 __init__.cpython-313.pyc
               1 File(s)            906 bytes

 Directory of D:\VScode\GitHub\From_Console_to_Cloud\backend\routes

01/07/2026  03:20 PM    <DIR>          .
01/07/2026  03:20 PM    <DIR>          ..
01/07/2026  02:47 PM             2,314 tasks.py
01/07/2026  03:20 PM    <DIR>          __pycache__
               1 File(s)          2,314 bytes

 Directory of D:\VScode\GitHub\From_Console_to_Cloud\backend\routes\__pycache__

01/07/2026  03:20 PM    <DIR>          .
01/07/2026  03:20 PM    <DIR>          ..
01/07/2026  03:20 PM             4,008 tasks.cpython-313.pyc
               1 File(s)          4,008 bytes

 Directory of D:\VScode\GitHub\From_Console_to_Cloud\backend\schemas

01/07/2026  03:20 PM    <DIR>          .
01/07/2026  03:20 PM    <DIR>          ..
01/07/2026  03:23 PM               852 tasks.py
01/07/2026  03:24 PM    <DIR>          __pycache__
               1 File(s)            852 bytes

 Directory of D:\VScode\GitHub\From_Console_to_Cloud\backend\schemas\__pycache__

01/07/2026  03:24 PM    <DIR>          .
01/07/2026  03:24 PM    <DIR>          ..
01/07/2026  03:24 PM             2,164 tasks.cpython-313.pyc
               1 File(s)          2,164 bytes

 Directory of D:\VScode\GitHub\From_Console_to_Cloud\backend\__pycache__

01/07/2026  03:20 PM    <DIR>          .
01/07/2026  03:20 PM    <DIR>          ..
01/07/2026  03:20 PM               932 main.cpython-313.pyc
01/07/2026  03:20 PM             1,580 models.cpython-313.pyc
               2 File(s)          2,512 bytes

     Total Files Listed:
              24 File(s)         29,761 bytes
              26 Dir(s)  25,998,491,648 bytes free

(cli-todo) D:\VScode\GitHub\From_Console_to_Cloud\backend>
```

# app.py
```python
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import tasks
from database import create_db_and_tables
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Todo API on Hugging Face")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)

@app.on_event("startup")
def startup():
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"message": "Todo API running on Hugging Face Spaces!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

# auth\jwt.py
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os

security = HTTPBearer()

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"


def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise Exception()
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    return verify_token(credentials.credentials)
```

# database\__init__.py
```python
from sqlmodel import Session, create_engine, SQLModel
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

# main.py
```python
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import tasks
from database import create_db_and_tables
from dotenv import load_dotenv

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
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"message": "Todo API running on Hugging Face Spaces!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# For Hugging Face Spaces
if __name__ == "__main__":
    import uvicorn
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

# routes\tasks.py
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime
from models import Task
from schemas.tasks import TaskCreate, TaskUpdate, TaskResponse
from database import get_session
from auth.jwt import get_current_user_id

router = APIRouter(prefix="/api", tags=["tasks"])


@router.get("/tasks", response_model=list[TaskResponse])
def list_tasks(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
):
    return session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()


@router.post("/tasks", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
):
    db_task = Task(**task.dict(), user_id=user_id)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    updates: TaskUpdate,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
):
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404)

    for k, v in updates.dict(exclude_unset=True).items():
        setattr(task, k, v)

    task.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(task)
    return task


@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
):
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404)

    session.delete(task)
    session.commit()
    return {"ok": True}


@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
def toggle_complete(
    task_id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
):
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404)

    task.completed = not task.completed
    task.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(task)
    return task
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
