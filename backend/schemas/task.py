from pydantic import BaseModel
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
    priority: Optional[TaskPriority] = TaskPriority.medium
    category: Optional[str] = None
    tags: List[str] = []


class TaskCreate(TaskBase):
    title: str  # Required field for creation


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


class UserBase(BaseModel):
    email: str
    name: Optional[str] = None


class UserResponse(UserBase):
    id: str
    created_at: datetime