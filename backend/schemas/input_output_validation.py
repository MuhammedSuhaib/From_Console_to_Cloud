from pydantic import BaseModel, Field, validator
from typing import Optional, List
from fastapi import HTTPException
import re


# Input validation models
class AddTaskInput(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100, description="User identifier")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    priority: Optional[str] = Field("medium", pattern=r"^(low|medium|high)$", description="Priority level: low, medium, or high")
    tags: Optional[List[str]] = Field([], description="List of tags for the task")
    due_date: Optional[str] = Field(None, description="Due date as ISO string (YYYY-MM-DDTHH:MM:SS) or natural language")
    is_recurring: Optional[bool] = Field(False, description="Whether the task is recurring")
    recurrence_pattern: Optional[str] = Field(None, max_length=255, description="Recurrence pattern (e.g., daily, weekly)")

    @validator('user_id')
    def validate_user_id(cls, v):
        if not v.strip():
            raise ValueError('User ID cannot be empty or whitespace')
        return v.strip()

    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

    @validator('recurrence_pattern')
    def validate_recurrence_pattern(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Recurrence pattern cannot be empty or whitespace')
        return v.strip() if v else v

    @validator('priority')
    def validate_priority(cls, v):
        if v not in ['low', 'medium', 'high']:
            raise ValueError('Priority must be one of: low, medium, high')
        return v


class ListTasksInput(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100, description="User identifier")
    status: str = Field("all", pattern=r"^(all|pending|completed)$", description="Filter status")

    @validator('user_id')
    def validate_user_id(cls, v):
        if not v.strip():
            raise ValueError('User ID cannot be empty or whitespace')
        return v.strip()


class CompleteTaskInput(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100, description="User identifier")
    task_id: int = Field(..., gt=0, description="Task identifier")


class DeleteTaskInput(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100, description="User identifier")
    task_id: int = Field(..., gt=0, description="Task identifier")


class UpdateTaskInput(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100, description="User identifier")
    task_id: int = Field(..., gt=0, description="Task identifier")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="New task title")
    description: Optional[str] = Field(None, max_length=1000, description="New task description")
    priority: Optional[str] = Field(None, pattern=r"^(low|medium|high)?$", description="Priority level: low, medium, or high")
    tags: Optional[List[str]] = Field(None, description="List of tags for the task")
    due_date: Optional[str] = Field(None, description="Due date as ISO string (YYYY-MM-DDTHH:MM:SS) or natural language")
    is_recurring: Optional[bool] = Field(None, description="Whether the task is recurring")
    recurrence_pattern: Optional[str] = Field(None, max_length=255, description="Recurrence pattern (e.g., daily, weekly)")

    @validator('title')
    def validate_title(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip() if v else v

    @validator('recurrence_pattern')
    def validate_recurrence_pattern(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Recurrence pattern cannot be empty or whitespace')
        return v.strip() if v else v

    @validator('priority')
    def validate_priority(cls, v):
        if v is not None and v not in ['low', 'medium', 'high']:
            raise ValueError('Priority must be one of: low, medium, high')
        return v


class SearchTasksInput(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100, description="User identifier")
    keyword: str = Field(..., min_length=1, max_length=200, description="Keyword to search in task titles or descriptions")

    @validator('user_id')
    def validate_user_id(cls, v):
        if not v.strip():
            raise ValueError('User ID cannot be empty or whitespace')
        return v.strip()

    @validator('keyword')
    def validate_keyword(cls, v):
        if not v.strip():
            raise ValueError('Keyword cannot be empty or whitespace')
        return v.strip()


class FilterSortTasksInput(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100, description="User identifier")
    status: Optional[str] = Field(None, pattern=r"^(all|pending|completed)?$", description="Filter by status: all, pending, or completed")
    priority: Optional[str] = Field(None, pattern=r"^(low|medium|high)?$", description="Filter by priority: low, medium, high")
    tags: Optional[List[str]] = Field(None, description="Filter by tags (any of these tags)")
    sort_by: Optional[str] = Field(None, pattern=r"^(priority|due_date|created_at|updated_at)?$", description="Sort by: priority, due_date, created_at, updated_at")
    sort_order: str = Field("asc", pattern=r"^(asc|desc)$", description="Sort order: asc or desc")
    category: Optional[str] = Field(None, description="Filter by category")

    @validator('user_id')
    def validate_user_id(cls, v):
        if not v.strip():
            raise ValueError('User ID cannot be empty or whitespace')
        return v.strip()


# Output validation models
class TaskOutput(BaseModel):
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    category: Optional[str]
    tags: list
    created_at: str
    updated_at: str


class AddTaskOutput(BaseModel):
    status: str
    message: str
    task_id: Optional[int] = None
    title: Optional[str] = None


class ListTasksOutput(BaseModel):
    status: str
    tasks: list
    count: int


class GenericTaskOutput(BaseModel):
    status: str
    message: str
    task_id: Optional[int] = None
    title: Optional[str] = None


def validate_add_task_input(user_id: str, title: str, description: Optional[str] = None, priority: Optional[str] = None, tags: Optional[List[str]] = None, due_date: Optional[str] = None, is_recurring: Optional[bool] = None, recurrence_pattern: Optional[str] = None) -> AddTaskInput:
    """Validate add_task input parameters"""
    try:
        validated = AddTaskInput(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority if priority else "medium",  # Default to medium if not provided
            tags=tags if tags is not None else [],  # Default to empty list if not provided
            due_date=due_date,
            is_recurring=is_recurring,
            recurrence_pattern=recurrence_pattern
        )
        return validated
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input for add_task: {str(e)}")


def validate_list_tasks_input(user_id: str, status: str = "all") -> ListTasksInput:
    """Validate list_tasks input parameters"""
    try:
        validated = ListTasksInput(
            user_id=user_id,
            status=status
        )
        return validated
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input for list_tasks: {str(e)}")


def validate_complete_task_input(user_id: str, task_id: int) -> CompleteTaskInput:
    """Validate complete_task input parameters"""
    try:
        validated = CompleteTaskInput(
            user_id=user_id,
            task_id=task_id
        )
        return validated
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input for complete_task: {str(e)}")


def validate_delete_task_input(user_id: str, task_id: int) -> DeleteTaskInput:
    """Validate delete_task input parameters"""
    try:
        validated = DeleteTaskInput(
            user_id=user_id,
            task_id=task_id
        )
        return validated
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input for delete_task: {str(e)}")


def validate_update_task_input(user_id: str, task_id: int, title: Optional[str] = None, description: Optional[str] = None, priority: Optional[str] = None, tags: Optional[List[str]] = None, due_date: Optional[str] = None, is_recurring: Optional[bool] = None, recurrence_pattern: Optional[str] = None) -> UpdateTaskInput:
    """Validate update_task input parameters"""
    try:
        validated = UpdateTaskInput(
            user_id=user_id,
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            due_date=due_date,
            is_recurring=is_recurring,
            recurrence_pattern=recurrence_pattern
        )
        return validated
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input for update_task: {str(e)}")


def validate_search_tasks_input(user_id: str, keyword: str) -> SearchTasksInput:
    """Validate search_tasks input parameters"""
    try:
        validated = SearchTasksInput(
            user_id=user_id,
            keyword=keyword
        )
        return validated
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input for search_tasks: {str(e)}")


def validate_filter_sort_tasks_input(user_id: str, status: str = None, priority: str = None, tags: list = None, sort_by: str = None, sort_order: str = "asc", category: str = None) -> FilterSortTasksInput:
    """Validate filter_sort_tasks input parameters"""
    try:
        validated = FilterSortTasksInput(
            user_id=user_id,
            status=status,
            priority=priority,
            tags=tags,
            sort_by=sort_by,
            sort_order=sort_order,
            category=category
        )
        return validated
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input for filter_sort_tasks: {str(e)}")


class PushSubscriptionInput(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100, description="User identifier")
    endpoint: str = Field(..., min_length=1, max_length=500, description="Push subscription endpoint")
    p256dh: str = Field(..., min_length=1, max_length=255, description="P256DH key")
    auth: str = Field(..., min_length=1, max_length=255, description="Auth secret")


def validate_push_subscription_input(user_id: str, endpoint: str, p256dh: str, auth: str) -> PushSubscriptionInput:
    """Validate push subscription input parameters"""
    try:
        validated = PushSubscriptionInput(
            user_id=user_id,
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth
        )
        return validated
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input for push subscription: {str(e)}")


def validate_output_format(result: str, operation: str) -> str:
    """Validate that the output format meets expected standards"""
    # Basic validation - ensure result is a string and not empty
    if not isinstance(result, str):
        raise HTTPException(status_code=500, detail=f"Invalid output format for {operation}: expected string")

    if not result.strip():
        raise HTTPException(status_code=500, detail=f"Empty output for {operation}")

    return result