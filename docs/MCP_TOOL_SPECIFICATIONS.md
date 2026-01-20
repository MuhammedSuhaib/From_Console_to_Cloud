# MCP Tool Specifications

This document provides comprehensive specifications for the Model Context Protocol (MCP) tools used in the AI Chatbot system. These tools allow the AI agent to interact with the backend to perform task management operations.

## Overview

The MCP tools provide a standardized interface for the AI agent to perform CRUD operations on tasks. Each tool follows MCP specifications and includes proper validation and error handling.

## Available Tools

### 1. add_task

Adds a new task to the user's task list.

**Function Signature:**
```python
def add_task(user_id: str, title: str, description: Optional[str] = None) -> str
```

**Parameters:**
- `user_id` (string): The ID of the user creating the task (required)
- `title` (string): The title of the task (required)
- `description` (string, optional): Detailed description of the task

**Returns:**
- Success message with task ID on success
- Error message if validation fails or operation fails

**Example Usage:**
```json
{
  "name": "add_task",
  "arguments": {
    "user_id": "user123",
    "title": "Buy groceries",
    "description": "Milk, bread, eggs"
  }
}
```

**Example Response:**
```json
{
  "result": "Success: Task 'Buy groceries' added with ID 456"
}
```

### 2. list_tasks

Retrieves a list of tasks for the specified user with optional filtering.

**Function Signature:**
```python
def list_tasks(user_id: str, status: Optional[str] = "all") -> str
```

**Parameters:**
- `user_id` (string): The ID of the user whose tasks to retrieve (required)
- `status` (string, optional): Filter by task status ("all", "pending", "completed") - defaults to "all"

**Returns:**
- Formatted string containing the list of tasks with their status indicators
- Error message if validation fails or operation fails

**Example Usage:**
```json
{
  "name": "list_tasks",
  "arguments": {
    "user_id": "user123",
    "status": "pending"
  }
}
```

**Example Response:**
```
Here are your pending tasks:
⏳ Task 1: Buy groceries - Milk, bread, eggs
⏳ Task 2: Finish report - Complete quarterly analysis
```

### 3. complete_task

Marks a specific task as completed.

**Function Signature:**
```python
def complete_task(user_id: str, task_id: int) -> str
```

**Parameters:**
- `user_id` (string): The ID of the user (required)
- `task_id` (integer): The ID of the task to mark as completed (required)

**Returns:**
- Success message if task was completed
- Error message if task not found or validation fails

**Example Usage:**
```json
{
  "name": "complete_task",
  "arguments": {
    "user_id": "user123",
    "task_id": 456
  }
}
```

**Example Response:**
```json
{
  "result": "Success: Task 'Buy groceries' marked as completed"
}
```

### 4. delete_task

Removes a specific task from the user's task list.

**Function Signature:**
```python
def delete_task(user_id: str, task_id: int) -> str
```

**Parameters:**
- `user_id` (string): The ID of the user (required)
- `task_id` (integer): The ID of the task to delete (required)

**Returns:**
- Success message if task was deleted
- Error message if task not found or validation fails

**Example Usage:**
```json
{
  "name": "delete_task",
  "arguments": {
    "user_id": "user123",
    "task_id": 456
  }
}
```

**Example Response:**
```json
{
  "result": "Success: Task 'Buy groceries' deleted"
}
```

### 5. update_task

Updates properties of an existing task.

**Function Signature:**
```python
def update_task(user_id: str, task_id: int, title: Optional[str] = None, description: Optional[str] = None, completed: Optional[bool] = None) -> str
```

**Parameters:**
- `user_id` (string): The ID of the user (required)
- `task_id` (integer): The ID of the task to update (required)
- `title` (string, optional): New title for the task
- `description` (string, optional): New description for the task
- `completed` (boolean, optional): New completion status for the task

**Returns:**
- Success message if task was updated
- Error message if task not found or validation fails

**Example Usage:**
```json
{
  "name": "update_task",
  "arguments": {
    "user_id": "user123",
    "task_id": 456,
    "title": "Buy weekly groceries",
    "description": "Milk, bread, eggs, fruits, vegetables"
  }
}
```

**Example Response:**
```json
{
  "result": "Success: Task updated successfully"
}
```

## Security Features

### User Isolation
- Each tool validates that the requesting user has permission to perform the operation on the specified task
- Users can only access, modify, or delete their own tasks
- Cross-user data access is prevented

### Input Validation
- All string parameters are validated for minimum length requirements
- Numeric parameters are validated for appropriate ranges
- Malicious input is sanitized to prevent injection attacks

### Error Handling
- Tools return appropriate error messages without exposing sensitive information
- Failed operations are logged for security monitoring
- Graceful degradation when database operations fail

## Implementation Details

### Backend Location
- Main MCP server: `backend/mcp_server/mcp_server.py`
- Database integration: Uses SQLModel ORM with Neon PostgreSQL
- Authentication: Integrated with JWT token validation

### Error Responses
All tools return descriptive error messages for:
- Invalid user IDs
- Non-existent tasks
- Insufficient permissions
- Database connection issues
- Validation failures

## Usage Examples

### Natural Language to Tool Mapping
The AI agent automatically maps natural language requests to appropriate tools:

- "Add a task to buy groceries" → `add_task`
- "Show me my tasks" → `list_tasks`
- "Mark task #1 as done" → `complete_task`
- "Delete my task about buying groceries" → `delete_task`
- "Update my grocery task to include milk" → `update_task`

### Tool Chaining
The AI agent can chain multiple tools in sequence to accomplish complex operations, such as listing tasks before completing one or adding a task and then updating it.