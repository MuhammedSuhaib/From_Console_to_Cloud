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

If title is provided, ALWAYS create the task.
NEVER ask for description.
If missing, pass empty string.

If multiple commands are given:
Execute them ONE BY ONE.
Before update/complete/delete by name:
ALWAYS call list_my_tasks again.
Never ask user to retry.
Never ask confirmation unless destructive.

"""


@function_tool
def get_user_info(ctx: RunContextWrapper[UserContext]) -> str:
    """Get the info of the user from the context."""
    user_info = ctx.context
    return f"User: {user_info.name}, UID: {user_info.uid or 'N/A'}, Personalization: {user_info.personalization_data or 'None'}"


@function_tool
def add_new_task(
    ctx: RunContextWrapper[UserContext], title: str, description: str = None
) -> str:
    """Add a new task."""
    # Bridging to the official MCP server tool
    return str(add_task(user_id=ctx.context.uid, title=title, description=description))


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
) -> str:
    """Update a task."""
    # Bridging to the official MCP server tool
    return str(
        update_task(
            user_id=ctx.context.uid,
            task_id=task_id,
            title=title,
            description=description,
        )
    )


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
    ],
    model=model_config,
)
