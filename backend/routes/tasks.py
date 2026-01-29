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


@router.get("/tasks/search")
def search_tasks(
    keyword: str,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
):
    logger.info(f"Searching tasks for user_id: {user_id} with keyword: {keyword}")
    try:
        from sqlmodel import or_, and_
        from sqlalchemy import func

        # Case-insensitive search in both title and description
        search_term = f"%{keyword.lower()}%"

        # Build query using LIKE for case-insensitive search
        condition = or_(
            func.lower(Task.title).like(search_term),
            and_(
                Task.description.is_not(None),
                func.lower(Task.description).like(search_term)
            )
        )

        tasks = session.exec(
            select(Task).where(
                Task.user_id == user_id,
                condition
            )
        ).all()

        logger.info(f"Found {len(tasks)} tasks matching keyword '{keyword}' for user_id: {user_id}")
        return {"data": tasks}
    except Exception as e:
        logger.error(f"Error searching tasks for user_id {user_id} with keyword {keyword}: {str(e)}")
        raise


@router.get("/tasks/filter-sort")
def filter_sort_tasks(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
    status: str = None,
    priority: str = None,
    category: str = None,
    tags: str = None,
    sort_by: str = None,
    sort_order: str = "asc",
):
    logger.info(f"Filtering and sorting tasks for user_id: {user_id}")
    try:
        from sqlmodel import select, and_
        from sqlalchemy import asc, desc, text

        # Start with base query for user's tasks
        query = select(Task).where(Task.user_id == user_id)

        # Apply filters
        conditions = []

        # Filter by status
        if status and status != "all":
            if status == "pending":
                conditions.append(Task.completed == False)
            elif status == "completed":
                conditions.append(Task.completed == True)

        # Filter by priority
        if priority:
            conditions.append(Task.priority == priority)

        # Filter by category
        if category:
            conditions.append(Task.category == category)

        # Filter by tags (if provided)
        if tags:
            # Split tags by comma and check if any of them match
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
            if tag_list:
                from sqlalchemy import or_, text
                tag_conditions = []
                for tag in tag_list:
                    # Use raw SQL for checking if tag exists in the tags array
                    tag_conditions.append(text(f"'{tag}' = ANY(tags)"))
                if tag_conditions:
                    conditions.append(or_(*tag_conditions))

        # Apply all conditions if any exist
        if conditions:
            query = query.where(and_(*conditions))

        # Apply sorting
        if sort_by:
            if sort_by == "priority":
                if sort_order == "desc":
                    query = query.order_by(desc(Task.priority))
                else:
                    query = query.order_by(asc(Task.priority))
            elif sort_by == "due_date":
                if sort_order == "desc":
                    query = query.order_by(desc(Task.due_date))
                else:
                    query = query.order_by(asc(Task.due_date))
            elif sort_by == "created_at":
                if sort_order == "desc":
                    query = query.order_by(desc(Task.created_at))
                else:
                    query = query.order_by(asc(Task.created_at))
            elif sort_by == "updated_at":
                if sort_order == "desc":
                    query = query.order_by(desc(Task.updated_at))
                else:
                    query = query.order_by(asc(Task.updated_at))
        else:
            # Default sorting by updated_at descending if no sort_by specified
            if sort_order == "desc":
                query = query.order_by(desc(Task.updated_at))
            else:
                query = query.order_by(asc(Task.updated_at))

        tasks = session.exec(query).all()

        logger.info(f"Found {len(tasks)} tasks after filtering and sorting for user_id: {user_id}")
        return {"data": tasks}
    except Exception as e:
        logger.error(f"Error filtering and sorting tasks for user_id {user_id}: {str(e)}")
        raise


@router.patch("/tasks/{task_id}/mark-reminder-sent")
def mark_reminder_sent(
    task_id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
):
    logger.info(f"Marking reminder as sent for task {task_id} for user_id: {user_id}")
    try:
        task = session.get(Task, task_id)
        if not task or task.user_id != user_id:
            logger.warning(f"Task {task_id} not found or user_id mismatch for user_id: {user_id}")
            raise HTTPException(status_code=404)

        task.reminder_sent = True
        task.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(task)
        logger.info(f"Marked reminder as sent for task {task_id}")
        return {"data": task}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking reminder as sent for task {task_id} for user_id {user_id}: {str(e)}")
        raise