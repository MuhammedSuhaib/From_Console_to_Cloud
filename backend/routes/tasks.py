from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime
from ..models import Task
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse
from ..database import get_session

router = APIRouter(prefix="/api", tags=["tasks"])

@router.get("/users/{user_id}/tasks", response_model=List[TaskResponse])
async def list_tasks(
    user_id: str,
    completed: Optional[bool] = None,
    session: Session = Depends(get_session)
):
    query = select(Task).where(Task.user_id == user_id)
    if completed is not None:
        query = query.where(Task.completed == completed)
    
    tasks = session.exec(query).all()
    return tasks

@router.post("/users/{user_id}/tasks", response_model=TaskResponse)
async def create_task(
    user_id: str,
    task: TaskCreate,
    session: Session = Depends(get_session)
):
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

@router.get("/users/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session)
):
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

@router.put("/users/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session)
):
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

@router.delete("/users/{user_id}/tasks/{task_id}")
async def delete_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session)
):
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

@router.patch("/users/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session)
):
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