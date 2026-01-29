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
    validate_search_tasks_input,
    validate_filter_sort_tasks_input,
    validate_output_format
)

# Initialize the official FastMCP server
mcp = FastMCP("Focus Task Manager")

@mcp.tool()
def add_task(user_id: str, title: str, description: Optional[str] = None, priority: Optional[str] = "medium", tags: Optional[List[str]] = None, due_date: Optional[str] = None, is_recurring: Optional[bool] = None, recurrence_pattern: Optional[str] = None) -> str:
    """
    Create a new task in the database.

    Args:
        user_id: The unique identifier of the user.
        title: The title of the todo item.
        description: Optional detailed notes for the task.
        priority: Priority level ('low', 'medium', 'high'). Default is 'medium'.
        tags: Optional list of tags for the task.
        due_date: Optional due date for the task (ISO string format).
        is_recurring: Whether the task should recur (default: False).
        recurrence_pattern: Pattern for recurring tasks (e.g., "daily", "weekly").
    """
    # Validate input parameters
    validated_inputs = validate_add_task_input(user_id, title, description, priority, tags, due_date, is_recurring, recurrence_pattern)
    session_gen = get_session()
    session = next(session_gen)
    try:
        # Parse due_date if provided
        parsed_due_date = None
        if validated_inputs.due_date:
            try:
                # Try to parse as ISO format first
                from datetime import datetime
                parsed_due_date = datetime.fromisoformat(validated_inputs.due_date.replace('Z', '+00:00'))
            except ValueError:
                # If not ISO format, leave as None for now (could be natural language that needs further processing)
                parsed_due_date = None

        new_task = Task(
            user_id=validated_inputs.user_id,
            title=validated_inputs.title,
            description=validated_inputs.description,
            priority=TaskPriority(validated_inputs.priority),
            tags=validated_inputs.tags,
            due_date=parsed_due_date,
            is_recurring=validated_inputs.is_recurring if validated_inputs.is_recurring is not None else False,
            recurrence_pattern=validated_inputs.recurrence_pattern,
            reminder_sent=False  # New tasks don't have reminders sent yet
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
def update_task(user_id: str, task_id: int, title: Optional[str] = None, description: Optional[str] = None, priority: Optional[str] = None, tags: Optional[List[str]] = None, due_date: Optional[str] = None, is_recurring: Optional[bool] = None, recurrence_pattern: Optional[str] = None) -> str:
    """
    Modify the title, description, priority, tags or other attributes of an existing task.

    Args:
        user_id: The unique identifier of the user.
        task_id: The numeric ID of the task to update.
        title: The new title for the task.
        description: The new description for the task.
        priority: New priority level ('low', 'medium', 'high').
        tags: New list of tags for the task.
        due_date: Optional due date for the task (ISO string format).
        is_recurring: Whether the task should recur.
        recurrence_pattern: Pattern for recurring tasks (e.g., "daily", "weekly").
    """
    # Validate input parameters
    validated_inputs = validate_update_task_input(user_id, task_id, title, description, priority, tags, due_date, is_recurring, recurrence_pattern)

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
            if validated_inputs.priority:
                task.priority = TaskPriority(validated_inputs.priority)
            if validated_inputs.tags is not None:
                task.tags = validated_inputs.tags
            if validated_inputs.due_date is not None:
                try:
                    # Try to parse as ISO format first
                    from datetime import datetime
                    parsed_due_date = datetime.fromisoformat(validated_inputs.due_date.replace('Z', '+00:00'))
                    task.due_date = parsed_due_date
                except ValueError:
                    # If not ISO format, leave as None for now (could be natural language that needs further processing)
                    task.due_date = None
            if validated_inputs.is_recurring is not None:
                task.is_recurring = validated_inputs.is_recurring
            if validated_inputs.recurrence_pattern is not None:
                task.recurrence_pattern = validated_inputs.recurrence_pattern
            task.updated_at = datetime.utcnow()

            session.add(task)
            session.commit()
            result = f"Success: Task {validated_inputs.task_id} updated."

        return validate_output_format(result, "update_task")
    finally:
        session.close()
        next(session_gen, None)


@mcp.tool()
def search_tasks(user_id: str, keyword: str) -> str:
    """
    Search tasks by keyword in title or description.

    Args:
        user_id: The unique identifier of the user.
        keyword: The keyword to search for in task titles or descriptions.
    """
    # Validate input parameters
    validated_inputs = validate_search_tasks_input(user_id, keyword)
    session_gen = get_session()
    session = next(session_gen)
    try:
        # Search for tasks that match the keyword in title or description
        from sqlmodel import or_, and_
        from sqlalchemy import func

        # Case-insensitive search in both title and description
        # Create the search term for reuse
        search_term = f"%{validated_inputs.keyword.lower()}%"

        # Build query using LIKE for case-insensitive search
        # Search in title always, and in description if it's not None
        condition = or_(
            func.lower(Task.title).like(search_term),
            and_(
                Task.description.is_not(None),
                func.lower(Task.description).like(search_term)
            )
        )

        tasks = session.exec(
            select(Task).where(
                Task.user_id == validated_inputs.user_id,
                condition
            )
        ).all()

        if not tasks:
            result = f"No tasks found containing '{validated_inputs.keyword}'."
        else:
            result_lines = [f"Found {len(tasks)} task(s) containing '{validated_inputs.keyword}':"]
            for task in tasks:
                status_icon = '✅' if task.completed else '⏳'
                due_info = f" (Due: {task.due_date.strftime('%Y-%m-%d')})" if task.due_date else ""
                result_lines.append(f"[{task.id}] {status_icon} {task.title}{due_info}")
            result = "\n".join(result_lines)

        return validate_output_format(result, "search_tasks")
    finally:
        session.close()
        next(session_gen, None)


@mcp.tool()
def get_task(user_id: str, task_id: int) -> str:
    """
    Retrieve details of a specific task.

    Args:
        user_id: The unique identifier of the user.
        task_id: The numeric ID of the task to retrieve.
    """
    session_gen = get_session()
    session = next(session_gen)
    try:
        task = session.get(Task, task_id)
        if not task or task.user_id != user_id:
            result = f"Error: Task with ID {task_id} not found."
        else:
            # Format the task details
            status_icon = '✅' if task.completed else '⏳'
            priority_str = task.priority.value if hasattr(task.priority, 'value') else str(task.priority)

            due_info = f"Due: {task.due_date.strftime('%Y-%m-%d %H:%M:%S')}" if task.due_date else "No due date"
            recurring_info = f"Recurring: {task.recurrence_pattern}" if task.is_recurring else "Not recurring"
            reminder_info = f"Reminder sent: {'Yes' if task.reminder_sent else 'No'}"
            tags_info = f"Tags: {', '.join(task.tags) if task.tags else 'None'}"
            category_info = f"Category: {task.category if task.category else 'None'}"

            result = f"""Task Details:
ID: {task.id}
Status: {status_icon} {task.title}
Priority: {priority_str}
Description: {task.description if task.description else 'None'}
{due_info}
{recurring_info}
{reminder_info}
{category_info}
{tags_info}
Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}
Updated: {task.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"""

        return validate_output_format(result, "get_task")
    finally:
        session.close()
        next(session_gen, None)


@mcp.tool()
def mark_reminder_sent(user_id: str, task_id: int) -> str:
    """
    Mark that a reminder has been sent for a specific task.

    Args:
        user_id: The unique identifier of the user.
        task_id: The numeric ID of the task to mark reminder as sent.
    """
    session_gen = get_session()
    session = next(session_gen)
    try:
        task = session.get(Task, task_id)
        if not task or task.user_id != user_id:
            result = f"Error: Task with ID {task_id} not found."
        else:
            task.reminder_sent = True
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()

            result = f"Success: Marked reminder as sent for task {task_id}."

        return validate_output_format(result, "mark_reminder_sent")
    finally:
        session.close()
        next(session_gen, None)


@mcp.tool()
def filter_sort_tasks(user_id: str, status: Optional[str] = None, priority: Optional[str] = None, tags: Optional[List[str]] = None, sort_by: Optional[str] = None, sort_order: str = "asc", category: Optional[str] = None) -> str:
    """
    Filter and sort tasks based on various criteria.

    Args:
        user_id: The unique identifier of the user.
        status: Filter by status ('all', 'pending', 'completed'). Default is 'all'.
        priority: Filter by priority ('low', 'medium', 'high').
        tags: Filter by tags (tasks containing any of these tags).
        sort_by: Sort by 'priority', 'due_date', 'created_at', 'updated_at'.
        sort_order: Sort order 'asc' or 'desc'. Default is 'asc'.
        category: Filter by category.
    """
    # Validate input parameters
    validated_inputs = validate_filter_sort_tasks_input(user_id, status, priority, tags, sort_by, sort_order, category)

    session_gen = get_session()
    session = next(session_gen)
    try:
        from sqlmodel import select, and_, or_
        from sqlalchemy import asc, desc

        # Start with a base query for the user's tasks
        query = select(Task).where(Task.user_id == validated_inputs.user_id)

        # Apply filters
        conditions = []

        # Filter by status
        if validated_inputs.status and validated_inputs.status != "all":
            if validated_inputs.status == "pending":
                conditions.append(Task.completed == False)
            elif validated_inputs.status == "completed":
                conditions.append(Task.completed == True)

        # Filter by priority
        if validated_inputs.priority:
            conditions.append(Task.priority == validated_inputs.priority)

        # Filter by tags (if provided)
        if validated_inputs.tags:
            # For tags, we need to check if any of the provided tags are in the task's tags list
            # Using SQL to check if any of the tags in the list are contained in the task's tags
            from sqlalchemy import text
            for tag in validated_inputs.tags:
                conditions.append(text(f"'{tag}' = ANY(tags)"))

        # Filter by category
        if validated_inputs.category:
            conditions.append(Task.category == validated_inputs.category)

        # Apply all conditions if any exist
        if conditions:
            query = query.where(and_(*conditions))

        # Apply sorting
        if validated_inputs.sort_by:
            if validated_inputs.sort_by == "priority":
                if validated_inputs.sort_order == "desc":
                    query = query.order_by(desc(Task.priority))
                else:
                    query = query.order_by(asc(Task.priority))
            elif validated_inputs.sort_by == "due_date":
                if validated_inputs.sort_order == "desc":
                    query = query.order_by(desc(Task.due_date))
                else:
                    query = query.order_by(asc(Task.due_date))
            elif validated_inputs.sort_by == "created_at":
                if validated_inputs.sort_order == "desc":
                    query = query.order_by(desc(Task.created_at))
                else:
                    query = query.order_by(asc(Task.created_at))
            elif validated_inputs.sort_by == "updated_at":
                if validated_inputs.sort_order == "desc":
                    query = query.order_by(desc(Task.updated_at))
                else:
                    query = query.order_by(asc(Task.updated_at))
        else:
            # Default sorting by updated_at descending if no sort_by specified
            if validated_inputs.sort_order == "desc":
                query = query.order_by(desc(Task.updated_at))
            else:
                query = query.order_by(asc(Task.updated_at))

        tasks = session.exec(query).all()

        if not tasks:
            result = f"No tasks found matching the specified criteria."
        else:
            result_lines = [f"Found {len(tasks)} task(s) matching the criteria:"]
            for task in tasks:
                status_icon = '✅' if task.completed else '⏳'
                priority_str = task.priority.value if hasattr(task.priority, 'value') else str(task.priority)

                # Format due date if it exists
                due_info = ""
                if task.due_date:
                    due_info = f" (Due: {task.due_date.strftime('%Y-%m-%d')})"

                # Show tags if they exist
                tags_info = ""
                if task.tags:
                    tags_info = f" [Tags: {', '.join(task.tags)}]"

                # Show category if it exists
                category_info = ""
                if task.category:
                    category_info = f" [Category: {task.category}]"

                result_lines.append(f"[{task.id}] {status_icon} P:{priority_str} {task.title}{due_info}{tags_info}{category_info}")

            result = "\n".join(result_lines)

        return validate_output_format(result, "filter_sort_tasks")
    finally:
        session.close()
        next(session_gen, None)