import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs.config import model_config
from agents import Agent, RunContextWrapper, function_tool
from models import UserContext
from mcp_tools import add_task_tool, list_tasks_tool, complete_task_tool, delete_task_tool

def dynamic_instructions(context: RunContextWrapper[UserContext], agent: Agent[UserContext]) -> str:
    user_info = context.context
    return f"""
    You are the AI Todo Assistant for {user_info.name}.
    Use tools to manage tasks. Commands:
    - Add task [title]
    - List tasks [all/pending/completed]
    - Complete task [id]
    - Delete task [id]
    Be concise. Do not mention tools. Confirm actions.
    """

@function_tool
def get_user_info(ctx: RunContextWrapper[UserContext]) -> str:
    return f"User: {ctx.context.name}, UID: {ctx.context.uid}"

@function_tool
def add_new_task(ctx: RunContextWrapper[UserContext], title: str, description: str = None) -> str:
    return str(add_task_tool(ctx.context.uid, title, description))

@function_tool
def list_my_tasks(ctx: RunContextWrapper[UserContext], status: str = "all") -> str:
    return str(list_tasks_tool(ctx.context.uid, status))

@function_tool
def finish_task(ctx: RunContextWrapper[UserContext], task_id: int) -> str:
    return str(complete_task_tool(ctx.context.uid, task_id))

Todo_Agent = Agent[UserContext](
    name="AI Todo Assistant",
    instructions=dynamic_instructions,
    tools=[get_user_info, add_new_task, list_my_tasks, finish_task],
    model=model_config,
)