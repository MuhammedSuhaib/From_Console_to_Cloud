import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs.config import model_config
from agents import Agent, RunContextWrapper, function_tool
from models import UserContext

# Removed manual mcp_tools import, now using official mcp_server tools
from mcp_server.mcp_server import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
    search_tasks,
    filter_sort_tasks,
    get_task,
    mark_reminder_sent
)


def dynamic_instructions(
    context: RunContextWrapper[UserContext], agent: Agent[UserContext]
) -> str:
    user_info = context.context
    return f"""
You are the AI Todo Assistant for {user_info.name}.

Role:
- You MUST use tools for EVERY task operation. Never pretend an action was done.
- You know the user's name is {user_info.name}. Use it.

Micro-task policy (2-minute rule):
- Detect large, vague, or incomprehensible goals ("giant mountain").
- DO NOT automatically break them down.
- When a giant mountain is detected, ASK the user if they want it broken into 2-minute micro-tasks.
- ONLY create micro-tasks when:
  1) The user explicitly agrees after being asked, OR
  2) The user explicitly asks to create micro-tasks.
- If micro-tasks are approved:
  - Break the goal into many small, specific, actionable steps.
  - Ensure the FIRST task is doable in ~2 minutes (open file, write one line, create folder).
  - Focus on urgency if multiple tasks exist.

Task rules:
- Description is OPTIONAL. If not provided, create the task with title only. Do NOT ask for a description.
- To act on a task by name, you MUST first call `list_my_tasks` to find the ID.
- Use only numeric IDs returned by tools.

Text & language:
- Default language is English. Use Urdu only if requested.
- Treat Unicode/emojis as normal text.

Behavior:
- Be concise. Do not mention tool names.
- Confirm actions only after tool success.

Commands:
- List tasks [all/pending/completed]
- Add task [title] (Description is optional, do not ask for it)
- Complete task [id]
- Update task [id] [new title/description]
- Delete task [id]
- Acknowledge/snooze reminder for [id] (Use when user indicates they've seen or acknowledged a reminder)

If title is provided, ALWAYS create the task.
NEVER ask for description.
If missing, pass empty string.

If multiple commands are given:
Execute them ONE BY ONE.
Before update/complete/delete by name:
ALWAYS call list_my_tasks again.
Never ask user to retry.
Never ask confirmation unless destructive.

If a user asks to snooze or acknowledge a reminder, use the acknowledge_reminder tool to silence further alerts for that task.
"""


@function_tool
def get_user_info(ctx: RunContextWrapper[UserContext]) -> str:
    """Get the info of the user from the context."""
    user_info = ctx.context
    return f"User: {user_info.name}, UID: {user_info.uid or 'N/A'}, Personalization: {user_info.personalization_data or 'None'}"


@function_tool
def add_new_task(
    ctx: RunContextWrapper[UserContext],
    title: str,
    description: str = None,
    priority: str = "medium",
    tags: list = None,
    due_date: str = None,
    is_recurring: bool = False,
    recurrence_pattern: str = None
) -> str:
    """
    Add a new task with advanced Phase V features.
    Args:
        priority: 'low', 'medium', or 'high'
        tags: List of strings for categorization
        due_date: ISO format string
        recurrence_pattern: 'daily', 'weekly', etc.
    """
    return str(add_task(
        user_id=ctx.context.uid,
        title=title,
        description=description,
        priority=priority,
        tags=tags or [],
        due_date=due_date,
        is_recurring=is_recurring,
        recurrence_pattern=recurrence_pattern
    ))


@function_tool
def list_my_tasks(ctx: RunContextWrapper[UserContext], status: str = "all") -> str:
    """List tasks."""
    # Bridging to the official MCP server tool
    return str(list_tasks(user_id=ctx.context.uid, status=status))


@function_tool
def finish_task(ctx: RunContextWrapper[UserContext], task_id: int) -> str:
    """Complete a task."""
    # Bridging to the official MCP server tool
    return str(complete_task(user_id=ctx.context.uid, task_id=task_id))


@function_tool
def remove_task(ctx: RunContextWrapper[UserContext], task_id: int) -> str:
    """Delete a task."""
    # Bridging to the official MCP server tool
    return str(delete_task(user_id=ctx.context.uid, task_id=task_id))


@function_tool
def modify_task(
    ctx: RunContextWrapper[UserContext],
    task_id: int,
    title: str = None,
    description: str = None,
    priority: str = None,
    tags: list = None,
    due_date: str = None,
    is_recurring: bool = None,
    recurrence_pattern: str = None
) -> str:
    """Update any attribute of an existing task including Phase V features."""
    return str(
        update_task(
            user_id=ctx.context.uid,
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            due_date=due_date,
            is_recurring=is_recurring,
            recurrence_pattern=recurrence_pattern
        )
    )


@function_tool
def find_tasks(ctx: RunContextWrapper[UserContext], keyword: str) -> str:
    """Search for tasks containing a specific keyword."""
    return str(search_tasks(user_id=ctx.context.uid, keyword=keyword))


@function_tool
def organize_tasks(
    ctx: RunContextWrapper[UserContext],
    status: str = None,
    priority: str = None,
    sort_by: str = "created_at"
) -> str:
    """Filter and sort tasks based on criteria."""
    return str(filter_sort_tasks(
        user_id=ctx.context.uid,
        status=status,
        priority=priority,
        sort_by=sort_by
    ))


@function_tool
def get_task_details(ctx: RunContextWrapper[UserContext], task_id: int) -> str:
    """Get detailed information about a specific task."""
    return str(get_task(user_id=ctx.context.uid, task_id=task_id))


@function_tool
def acknowledge_reminder(ctx: RunContextWrapper[UserContext], task_id: int) -> str:
    """Mark a reminder as sent/acknowledged to stop further alerts for a task."""
    return str(mark_reminder_sent(user_id=ctx.context.uid, task_id=task_id))


Todo_Agent = Agent[UserContext](
    name="AI Todo Assistant",
    instructions=dynamic_instructions,
    tools=[
        get_user_info,
        add_new_task,
        list_my_tasks,
        finish_task,
        remove_task,
        modify_task,
        find_tasks,
        organize_tasks,
        get_task_details,
        acknowledge_reminder,
    ],
    model=model_config,
)
