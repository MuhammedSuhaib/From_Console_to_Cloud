from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlalchemy import JSON, Column, TEXT
from pydantic import BaseModel


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class UserContext(BaseModel):
    name: str
    uid: str
    personalization_data: Optional[str] = None


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: TaskPriority = TaskPriority.medium
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list, sa_type=JSON)
    due_date: Optional[datetime] = Field(default=None)
    is_recurring: bool = Field(default=False)
    recurrence_pattern: Optional[str] = Field(default=None) # e.g., "daily", "weekly"
    reminder_sent: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to messages
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class PushSubscription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    endpoint: str
    p256dh: str
    auth: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    user_id: str = Field(index=True)
    role: str  # 'user', 'assistant', or 'system'
    content: str = Field(sa_column=Column(TEXT))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship back to conversation
    conversation: Conversation = Relationship(back_populates="messages")