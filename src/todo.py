"""
Simple in-memory todo application
"""
from typing import List, Optional, Dict, Any
from datetime import datetime


class Todo:
    """Simple todo item"""
    def __init__(self, id: int, title: str, description: str = "", completed: bool = False):
        self.id = id
        self.title = title
        self.description = description
        self.completed = completed
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def __repr__(self):
        status = "✓" if self.completed else "○"
        return f"Todo(id={self.id}, title='{self.title}', completed={self.completed})"


class TodoApp:
    """Simple in-memory todo application"""
    def __init__(self):
        self.todos: List[Todo] = []
        self.next_id = 1

    def add_todo(self, title: str, description: str = "") -> Todo:
        """Add a new todo"""
        if not title.strip():
            raise ValueError("Title cannot be empty")

        todo = Todo(self.next_id, title, description)
        self.todos.append(todo)
        self.next_id += 1
        return todo

    def get_todo(self, todo_id: int) -> Optional[Todo]:
        """Get a todo by ID"""
        for todo in self.todos:
            if todo.id == todo_id:
                return todo
        return None

    def list_todos(self, completed: Optional[bool] = None) -> List[Todo]:
        """List all todos, optionally filtered by completion status"""
        if completed is None:
            return self.todos[:]
        return [todo for todo in self.todos if todo.completed == completed]

    def update_todo(self, todo_id: int, title: Optional[str] = None, description: Optional[str] = None) -> bool:
        """Update a todo"""
        todo = self.get_todo(todo_id)
        if not todo:
            return False

        if title is not None:
            if not title.strip():
                raise ValueError("Title cannot be empty")
            todo.title = title
        if description is not None:
            todo.description = description
        todo.updated_at = datetime.now()
        return True

    def complete_todo(self, todo_id: int) -> bool:
        """Mark a todo as completed"""
        todo = self.get_todo(todo_id)
        if todo:
            todo.completed = True
            todo.updated_at = datetime.now()
            return True
        return False

    def delete_todo(self, todo_id: int) -> bool:
        """Delete a todo"""
        for i, todo in enumerate(self.todos):
            if todo.id == todo_id:
                del self.todos[i]
                return True
        return False