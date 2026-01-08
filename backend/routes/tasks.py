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