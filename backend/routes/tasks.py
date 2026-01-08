from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime
from models import Task
from schemas.tasks import TaskCreate, TaskUpdate, TaskResponse
from database import get_session
from auth.jwt import get_current_user_id

router = APIRouter(prefix="/api", tags=["tasks"])


@router.get("/tasks")
def list_tasks(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
):
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()
    return {"data": tasks}


@router.post("/tasks")
def create_task(
    task: TaskCreate,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
):
    db_task = Task(**task.dict(), user_id=user_id)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return {"data": db_task}


@router.put("/tasks/{task_id}")
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
    return {"data": task}


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
    return {"data": {"ok": True}}


@router.patch("/tasks/{task_id}/complete")
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
    return {"data": task}