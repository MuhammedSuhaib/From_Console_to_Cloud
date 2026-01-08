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