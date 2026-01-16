from pydantic import BaseModel, Field, validator
from typing import Optional
from fastapi import HTTPException
import re


# Input validation models
class AddTaskInput(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100, description="User identifier")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")

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

    @validator('title')
    def validate_title(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip() if v else v


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


def validate_add_task_input(user_id: str, title: str, description: Optional[str] = None) -> AddTaskInput:
    """Validate add_task input parameters"""
    try:
        validated = AddTaskInput(
            user_id=user_id,
            title=title,
            description=description
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


def validate_update_task_input(user_id: str, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> UpdateTaskInput:
    """Validate update_task input parameters"""
    try:
        validated = UpdateTaskInput(
            user_id=user_id,
            task_id=task_id,
            title=title,
            description=description
        )
        return validated
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input for update_task: {str(e)}")


def validate_output_format(result: str, operation: str) -> str:
    """Validate that the output format meets expected standards"""
    # Basic validation - ensure result is a string and not empty
    if not isinstance(result, str):
        raise HTTPException(status_code=500, detail=f"Invalid output format for {operation}: expected string")
    
    if not result.strip():
        raise HTTPException(status_code=500, detail=f"Empty output for {operation}")
    
    return result