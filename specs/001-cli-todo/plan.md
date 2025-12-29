# CLI Todo Application - Architecture Plan

## 1. Architecture Overview

### 1.1 System Context
The CLI Todo application is a single-process Python application that provides an interactive menu-driven interface for managing todo items. The system follows a simplified architecture with clear separation of concerns between domain logic and presentation layers, using questionary for interactive prompts and rich for formatted display.

### 1.2 Architecture Style
- **Simplified Architecture**: Minimal layers focusing on domain and presentation
- **Single Responsibility**: Each component has a single, well-defined purpose
- **Interactive-First Design**: User experience optimized for menu-driven interaction

## 2. Architecture Components

### 2.1 Domain Layer
**Purpose**: Contains business logic and domain entities

**Components**:
- `Todo` entity: Core domain model with validation
- `TodoApp` service: In-memory storage and business operations
- Domain services for business logic operations

**Key Classes**:
- `Todo`: Value object with id, title, description, completed, timestamps
- `TodoApp`: In-memory todo application service with CRUD operations

### 2.2 Presentation Layer
**Purpose**: Handles user interaction and display formatting

**Components**:
- `TodoCLI`: Interactive CLI interface using questionary for prompts
- `questionary`: Library for interactive command-line prompts and menus
- `rich`: Library for rich text and beautiful formatting in terminal

## 3. Component Design

### 3.1 Domain Model (`src/todo.py`)
```python
from typing import List, Optional
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
```

### 3.2 Interactive CLI Interface (`src/cli.py`)
```python
import questionary
from rich.console import Console
from rich.table import Table
from .todo import TodoApp


class TodoCLI:
    def __init__(self):
        self.app = TodoApp()
        self.console = Console()

    def run(self, args=None):
        """Run the interactive CLI."""
        # Only run interactive mode
        try:
            self._run_interactive_mode()
        except Exception as e:
            # If interactive mode fails (e.g., due to terminal issues), show error
            self.console.print(f"[red]Error starting interactive mode: {e}[/red]")
            self.console.print("[yellow]Please run in a terminal that supports interactive prompts.[/yellow]")

    def _run_interactive_mode(self):
        """Run the interactive menu system."""
        self.console.print("[bold cyan]Welcome to Todo CLI![/bold cyan]")

        while True:
            choice = questionary.select(
                "What would you like to do?",
                choices=[
                    "Add Todo",
                    "List Todos",
                    "Complete Todo",
                    "Edit Todo",
                    "Delete Todo",
                    "Exit",
                ],
            ).ask()

            if choice == "Add Todo":
                self._add_todo_interactive()
            elif choice == "List Todos":
                self._list_todos_interactive()
            elif choice == "Complete Todo":
                self._complete_todo_interactive()
            elif choice == "Edit Todo":
                self._edit_todo_interactive()
            elif choice == "Delete Todo":
                self._delete_todo_interactive()
            elif choice == "Exit" or choice is None:
                self.console.print("[bold cyan]Goodbye![/bold cyan]")
                break

    def _add_todo_interactive(self):
        """Add a todo interactively."""
        title = questionary.text("Enter todo title:").ask()
        if not title:
            self.console.print("[yellow]Todo title cannot be empty![/yellow]")
            return

        description = questionary.text("Enter todo description (optional):").ask() or ""

        try:
            todo = self.app.add_todo(title, description)
            self.console.print(f"[green]Added todo: {todo.title} (ID: {todo.id})[/green]")
        except ValueError as e:
            self.console.print(f"[red]Error: {e}[/red]")

    def _list_todos_interactive(self):
        """List todos interactively."""
        filter_choice = questionary.select(
            "Filter todos:",
            choices=[
                "All Todos",
                "Completed Only",
                "Pending Only",
            ],
        ).ask()

        completed = None
        if filter_choice == "Completed Only":
            completed = True
        elif filter_choice == "Pending Only":
            completed = False

        todos = self.app.list_todos(completed=completed)

        if todos:
            table = Table(title=f"{filter_choice}")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Status", style="magenta")
            table.add_column("Title", style="green")
            table.add_column("Description", style="yellow")

            for todo in todos:
                status = "✓" if todo.completed else "○"
                table.add_row(
                    str(todo.id),
                    status,
                    todo.title,
                    todo.description
                )

            self.console.print(table)
        else:
            self.console.print("[yellow]No todos found.[/yellow]")

    def _complete_todo_interactive(self):
        """Complete a todo interactively."""
        todos = self.app.list_todos(completed=False)

        if not todos:
            self.console.print("[yellow]No pending todos to complete.[/yellow]")
            return

        choices = [f"{todo.id}: {todo.title}" for todo in todos]
        choice = questionary.select("Select todo to complete:", choices=choices).ask()

        if choice:
            todo_id = int(choice.split(':')[0])
            try:
                self.app.complete_todo(todo_id)
                self.console.print(f"[green]Marked todo {todo_id} as completed![/green]")
            except ValueError as e:
                self.console.print(f"[red]Error: {e}[/red]")

    def _edit_todo_interactive(self):
        """Edit a todo interactively."""
        todos = self.app.list_todos()

        if not todos:
            self.console.print("[yellow]No todos to edit.[/yellow]")
            return

        choices = [f"{todo.id}: {todo.title}" for todo in todos]
        choice = questionary.select("Select todo to edit:", choices=choices).ask()

        if choice:
            todo_id = int(choice.split(':')[0])

            # Get current todo
            current_todo = self.app.get_todo(todo_id)

            # Ask for new values, keeping current ones as defaults
            new_title = questionary.text("Enter new title:", default=current_todo.title).ask()
            new_description = questionary.text("Enter new description:", default=current_todo.description).ask()

            try:
                self.app.update_todo(todo_id, new_title, new_description)
                self.console.print(f"[green]Updated todo {todo_id}![/green]")
            except ValueError as e:
                self.console.print(f"[red]Error: {e}[/red]")

    def _delete_todo_interactive(self):
        """Delete a todo interactively."""
        todos = self.app.list_todos()

        if not todos:
            self.console.print("[yellow]No todos to delete.[/yellow]")
            return

        choices = [f"{todo.id}: {todo.title}" for todo in todos]
        choice = questionary.select("Select todo to delete:", choices=choices).ask()

        if choice:
            todo_id = int(choice.split(':')[0])
            confirm = questionary.confirm(f"Are you sure you want to delete todo {todo_id}?").ask()

            if confirm:
                try:
                    self.app.delete_todo(todo_id)
                    self.console.print(f"[green]Deleted todo {todo_id}![/green]")
                except ValueError as e:
                    self.console.print(f"[red]Error: {e}[/red]")
```

### 3.3 Main Application Entry Point (`src/main.py`)
```python
import sys
from .cli import TodoCLI


def main():
    # Run in interactive mode
    cli = TodoCLI()
    cli.run()


if __name__ == "__main__":
    main()
```

## 4. File Structure

```
src/
├── todo.py          # Domain model and in-memory storage
├── cli.py           # Interactive CLI interface with questionary and rich
├── main.py          # Application entry point
└── __init__.py      # Package initialization
```

## 5. Technology Stack

### 5.1 Primary Technology
- **Python 3.10+**: Core programming language
- **questionary**: Library for interactive command-line prompts and menus
- **rich**: Library for rich text and beautiful formatting in terminal
- **Standard Library**: datetime for timestamps, typing for type hints

### 5.2 Architecture Patterns
- **Single Responsibility**: Each class has a single, well-defined purpose
- **Separation of Concerns**: Domain logic separate from presentation layer

## 6. Data Flow

### 6.1 Add Todo Flow
1. Interactive menu displays "Add Todo" option
2. User selects "Add Todo" option
3. questionary prompts user for title and optional description
4. TodoCLI calls `TodoApp.add_todo()` with user input
5. TodoApp creates new `Todo` entity with auto-incremented ID
6. TodoApp stores the todo in in-memory list
7. rich displays confirmation message

### 6.2 List Todos Flow
1. Interactive menu displays "List Todos" option
2. User selects "List Todos" option
3. questionary prompts user for filter (All, Completed Only, Pending Only)
4. TodoCLI calls `TodoApp.list_todos()` with filter parameter
5. TodoApp retrieves filtered todos from in-memory list
6. rich formats todos in a table with color coding
7. Table is displayed in terminal

### 6.3 Complete Todo Flow
1. Interactive menu displays "Complete Todo" option
2. User selects "Complete Todo" option
3. TodoCLI retrieves pending todos from TodoApp
4. questionary displays pending todos for selection
5. User selects a todo by ID
6. TodoCLI calls `TodoApp.complete_todo()` with selected ID
7. TodoApp marks the todo as completed in memory
8. rich displays confirmation message

## 7. Error Handling Strategy

### 7.1 Domain Layer
- Input validation in the `Todo` entity methods (e.g., non-empty title)
- Proper error propagation to presentation layer

### 7.2 Presentation Layer
- Business logic validation
- Proper error handling for non-existent todos
- Terminal compatibility error handling with user guidance
- Rich error messages using rich formatting

## 8. Performance Considerations

### 8.1 Memory Usage
- All todos stored in memory during session (acceptable for typical todo lists)
- Performance optimized for interactive response times (< 1 second)

### 8.2 Interactive Performance
- Menu navigation and operations respond within 1 second
- Rich table formatting optimized for typical todo list sizes

## 9. Testing Strategy

### 9.1 Unit Tests
- Test domain entity methods and validation
- Test TodoApp service logic (add, list, complete, edit, delete operations)
- Test edge cases and error conditions

### 9.2 Integration Tests
- Test end-to-end functionality
- Test interactive flow behavior
- Test integration between domain and presentation layers

### 9.3 Test Coverage
- 100% coverage for core domain logic
- High coverage for application services
- Integration tests for interactive CLI interface

## 10. Security Considerations

### 10.1 Input Validation
- Validate all user inputs in the domain layer (e.g., non-empty titles)
- No external data sources to validate
- In-memory only, no file system access

## 11. Deployment Strategy

### 11.1 Packaging
- Package as Python application with pyproject.toml
- Include all dependencies (questionary, rich) in configuration
- Provide installation instructions using uv

### 11.2 Execution
- Run directly with Python interpreter
- Console script available as `todo` command after installation
- Cross-platform compatibility

## 12. Maintenance and Evolution

### 12.1 Extension Points
- TodoApp service can be extended with new business logic
- Interactive CLI can be extended with new menu options
- Domain model can be extended with additional fields (per constitution)

### 12.2 Backward Compatibility
- Maintain same interactive menu structure
- Preserve core functionality across versions
- Follow semantic versioning for breaking changes