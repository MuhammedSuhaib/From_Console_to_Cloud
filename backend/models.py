from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional, List
from datetime import datetime
from enum import Enum
import os
import json
from sqlalchemy import JSON
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


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
    tags: List[str] = Field(default=[], sa_type=JSON, nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class User(SQLModel, table=True):
    id: str = Field(primary_key=True)  # Better Auth user ID
    email: str = Field(unique=True)
    name: Optional[str] = None
    hashed_password: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)


# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")  # Using SQLite for local development
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)