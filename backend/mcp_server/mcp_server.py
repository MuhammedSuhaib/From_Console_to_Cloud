from mcp.server.fastmcp import FastMCP
from sqlmodel import select
from models import Task, TaskPriority
from database import get_session
from datetime import datetime
from typing import Optional, List
from schemas.input_output_validation import (
    validate_add_task_input,
    validate_list_tasks_input,
    validate_complete_task_input,
    validate_delete_task_input,
    validate_update_task_input,
    validate_output_format
)

# Initialize the official FastMCP server
mcp = FastMCP("Focus Task Manager")

@mcp.tool()
def add_task(user_id: str, title: str, description: Optional[str] = None) -> str:
    """
    Create a new task in the database.

    Args:
        user_id: The unique identifier of the user.
        title: The title of the todo item.
        description: Optional detailed notes for the task.
    """
    # Validate input parameters
    validated_inputs = validate_add_task_input(user_id, title, description)
    session_gen = get_session()
    session = next(session_gen)
    try:
        new_task = Task(
            user_id=validated_inputs.user_id,
            title=validated_inputs.title,
            description=validated_inputs.description,
            priority=TaskPriority.medium
        )
        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        result = f"Success: Created task '{new_task.title}' with ID {new_task.id}"
        return validate_output_format(result, "add_task")
    finally:
        session.close()
        next(session_gen, None)

@mcp.tool()
def list_tasks(user_id: str, status: str = "all") -> str:
    """
    Retrieve a list of tasks for the user.
    
    Args:
        user_id: The unique identifier of the user.
        status: Filter tasks by 'all', 'pending', or 'completed'.
    """
    # Validate input parameters
    validated_inputs = validate_list_tasks_input(user_id, status)

    session_gen = get_session()
    session = next(session_gen)
    try:
        statement = select(Task).where(Task.user_id == validated_inputs.user_id)
        if validated_inputs.status == "pending":
            statement = statement.where(Task.completed == False)
        elif validated_inputs.status == "completed":
            statement = statement.where(Task.completed == True)

        tasks = session.exec(statement).all()
        if not tasks:
            result = "No tasks found for the specified criteria."
        else:
            result = "\n".join([f"[{t.id}] {'✅' if t.completed else '⏳'} {t.title}" for t in tasks])

        return validate_output_format(result, "list_tasks")
    finally:
        session.close()
        next(session_gen, None)

@mcp.tool()
def complete_task(user_id: str, task_id: int) -> str:
    """
    Mark a specific task as completed.

    Args:
        user_id: The unique identifier of the user.
        task_id: The numeric ID of the task to complete.
    """
    # Validate input parameters
    validated_inputs = validate_complete_task_input(user_id, task_id)

    session_gen = get_session()
    session = next(session_gen)
    try:
        task = session.get(Task, validated_inputs.task_id)
        if not task or task.user_id != validated_inputs.user_id:
            result = f"Error: Task with ID {validated_inputs.task_id} not found."
        else:
            task.completed = True
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            result = f"Success: Task {validated_inputs.task_id} marked as completed."

        return validate_output_format(result, "complete_task")
    finally:
        session.close()
        next(session_gen, None)

@mcp.tool()
def delete_task(user_id: str, task_id: int) -> str:
    """
    Permanently remove a task from the database.

    Args:
        user_id: The unique identifier of the user.
        task_id: The numeric ID of the task to delete.
    """
    # Validate input parameters
    validated_inputs = validate_delete_task_input(user_id, task_id)

    session_gen = get_session()
    session = next(session_gen)
    try:
        task = session.get(Task, validated_inputs.task_id)
        if not task or task.user_id != validated_inputs.user_id:
            result = f"Error: Task with ID {validated_inputs.task_id} not found."
        else:
            session.delete(task)
            session.commit()
            result = f"Success: Task {validated_inputs.task_id} has been deleted."

        return validate_output_format(result, "delete_task")
    finally:
        session.close()
        next(session_gen, None)

@mcp.tool()
def update_task(user_id: str, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> str:
    """
    Modify the title or description of an existing task.

    Args:
        user_id: The unique identifier of the user.
        task_id: The numeric ID of the task to update.
        title: The new title for the task.
        description: The new description for the task.
    """
    # Validate input parameters
    validated_inputs = validate_update_task_input(user_id, task_id, title, description)

    session_gen = get_session()
    session = next(session_gen)
    try:
        task = session.get(Task, validated_inputs.task_id)
        if not task or task.user_id != validated_inputs.user_id:
            result = f"Error: Task with ID {validated_inputs.task_id} not found."
        else:
            if validated_inputs.title:
                task.title = validated_inputs.title
            if validated_inputs.description:
                task.description = validated_inputs.description
            task.updated_at = datetime.utcnow()

            session.add(task)
            session.commit()
            result = f"Success: Task {validated_inputs.task_id} updated."

        return validate_output_format(result, "update_task")
    finally:
        session.close()
        next(session_gen, None)