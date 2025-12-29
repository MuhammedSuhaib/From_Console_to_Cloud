# CLI Todo Application - Architecture Plan

## 1. Architecture Overview

### 1.1 System Context
The CLI Todo application is a single-process Python application that provides command-line interface for managing todo items. The system follows a layered architecture with clear separation of concerns between domain logic, application logic, and infrastructure/persistence.

### 1.2 Architecture Style
- **Layered Architecture**: Separation of domain, application, and infrastructure layers
- **Single Responsibility**: Each component has a single, well-defined purpose
- **Dependency Inversion**: High-level modules don't depend on low-level modules

## 2. Architecture Layers

### 2.1 Domain Layer
**Purpose**: Contains business logic and domain entities

**Components**:
- `Todo` entity: Core domain model with validation
- `TodoRepository` interface: Abstract persistence contract
- Domain services for business logic operations

**Key Classes**:
- `Todo`: Value object with id, title, description, completed, timestamps
- `TodoRepository`: Interface defining persistence operations

### 2.2 Application Layer
**Purpose**: Orchestrates domain logic and coordinates with infrastructure

**Components**:
- `TodoService`: Main application service coordinating operations
- `TodoCommandHandler`: Handles CLI commands and delegates to services
- `TodoQueryHandler`: Handles read operations and queries

### 2.3 Infrastructure Layer
**Purpose**: Provides external services like file persistence, CLI parsing

**Components**:
- `FileTodoRepository`: File-based implementation of TodoRepository
- `CLIParser`: Command-line argument parser
- `Serializer`: JSON serialization for persistence

## 3. Component Design

### 3.1 Domain Model (`src/core/domain/todo.py`)
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Todo:
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("Title cannot be empty")
        if self.created_at is None:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def complete(self):
        self.completed = True
        self.updated_at = datetime.now()

    def update(self, title: Optional[str] = None, description: Optional[str] = None):
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        self.updated_at = datetime.now()
```

### 3.2 Repository Interface (`src/core/ports/todo_repository.py`)
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.domain.todo import Todo

class TodoRepository(ABC):
    @abstractmethod
    def add(self, todo: Todo) -> Todo:
        pass

    @abstractmethod
    def get_by_id(self, todo_id: int) -> Optional[Todo]:
        pass

    @abstractmethod
    def get_all(self) -> List[Todo]:
        pass

    @abstractmethod
    def update(self, todo: Todo) -> Optional[Todo]:
        pass

    @abstractmethod
    def delete(self, todo_id: int) -> bool:
        pass
```

### 3.3 Application Service (`src/core/application/todo_service.py`)
```python
from typing import List, Optional
from src.core.domain.todo import Todo
from src.core.ports.todo_repository import TodoRepository

class TodoService:
    def __init__(self, repository: TodoRepository):
        self.repository = repository
        self._next_id = self._get_next_id()

    def _get_next_id(self) -> int:
        todos = self.repository.get_all()
        if not todos:
            return 1
        return max(todo.id for todo in todos) + 1

    def create_todo(self, title: str, description: Optional[str] = None) -> Todo:
        todo = Todo(
            id=self._next_id,
            title=title,
            description=description
        )
        self._next_id += 1
        return self.repository.add(todo)

    def get_todo(self, todo_id: int) -> Optional[Todo]:
        return self.repository.get_by_id(todo_id)

    def get_all_todos(self, completed: Optional[bool] = None, sort_by: str = "created") -> List[Todo]:
        todos = self.repository.get_all()

        # Filter by completion status if specified
        if completed is not None:
            todos = [todo for todo in todos if todo.completed == completed]

        # Sort by specified criteria
        if sort_by == "created":
            todos = sorted(todos, key=lambda t: t.created_at)
        elif sort_by == "completed":
            todos = sorted(todos, key=lambda t: (not t.completed, t.created_at))
        elif sort_by == "updated":
            todos = sorted(todos, key=lambda t: t.updated_at or t.created_at)

        return todos

    def complete_todo(self, todo_id: int) -> bool:
        todo = self.repository.get_by_id(todo_id)
        if todo:
            todo.complete()
            self.repository.update(todo)
            return True
        return False

    def update_todo(self, todo_id: int, title: Optional[str] = None, description: Optional[str] = None) -> bool:
        todo = self.repository.get_by_id(todo_id)
        if todo:
            todo.update(title, description)
            self.repository.update(todo)
            return True
        return False

    def delete_todo(self, todo_id: int) -> bool:
        return self.repository.delete(todo_id)
```

### 3.4 In-Memory Repository Implementation (`src/infrastructure/repositories/in_memory_todo_repository.py`)
```python
from typing import List, Optional
from src.core.domain.todo import Todo
from src.core.ports.todo_repository import TodoRepository

class InMemoryTodoRepository(TodoRepository):
    def __init__(self):
        self._todos: List[Todo] = []
        self._next_id = 1

    def add(self, todo: Todo) -> Todo:
        # Set the ID if not already set
        if todo.id == 0:  # Assuming 0 means not set
            todo.id = self._next_id
            self._next_id += 1
        self._todos.append(todo)
        return todo

    def get_by_id(self, todo_id: int) -> Optional[Todo]:
        for todo in self._todos:
            if todo.id == todo_id:
                return todo
        return None

    def get_all(self) -> List[Todo]:
        return self._todos.copy()  # Return a copy to prevent external modification

    def update(self, todo: Todo) -> Optional[Todo]:
        for i, existing_todo in enumerate(self._todos):
            if existing_todo.id == todo.id:
                self._todos[i] = todo
                return todo
        return None

    def delete(self, todo_id: int) -> bool:
        for i, todo in enumerate(self._todos):
            if todo.id == todo_id:
                self._todos.pop(i)
                return True
        return False
```

### 3.5 CLI Interface (`src/interfaces/cli.py`)
```python
import argparse
import sys
from typing import Optional
from src.core.application.todo_service import TodoService

class CLIInterface:
    def __init__(self, todo_service: TodoService):
        self.todo_service = todo_service

    def run(self, args: Optional[list] = None):
        parser = argparse.ArgumentParser(description='Todo CLI Application')
        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # Add command
        add_parser = subparsers.add_parser('add', help='Add a new todo')
        add_parser.add_argument('title', help='Title of the todo')
        add_parser.add_argument('--description', '-d', help='Description of the todo')

        # List command
        list_parser = subparsers.add_parser('list', help='List all todos')
        list_parser.add_argument('--completed', action='store_true', help='Show only completed todos')
        list_parser.add_argument('--pending', action='store_true', help='Show only pending todos')
        list_parser.add_argument('--sort', choices=['created', 'completed', 'updated'],
                                default='created', help='Sort order for todos')

        # Complete command
        complete_parser = subparsers.add_parser('complete', help='Mark a todo as completed')
        complete_parser.add_argument('id', type=int, help='ID of the todo to complete')

        # Edit command
        edit_parser = subparsers.add_parser('edit', help='Edit a todo')
        edit_parser.add_argument('id', type=int, help='ID of the todo to edit')
        edit_parser.add_argument('--title', help='New title')
        edit_parser.add_argument('--description', '-d', help='New description')

        # Delete command
        delete_parser = subparsers.add_parser('delete', help='Delete a todo')
        delete_parser.add_argument('id', type=int, help='ID of the todo to delete')

        # Parse arguments
        parsed_args = parser.parse_args(args)

        if parsed_args.command == 'add':
            self._handle_add(parsed_args)
        elif parsed_args.command == 'list':
            self._handle_list(parsed_args)
        elif parsed_args.command == 'complete':
            self._handle_complete(parsed_args)
        elif parsed_args.command == 'edit':
            self._handle_edit(parsed_args)
        elif parsed_args.command == 'delete':
            self._handle_delete(parsed_args)
        elif parsed_args.command is None:
            parser.print_help()
            sys.exit(1)
        else:
            parser.print_help()
            sys.exit(1)

    def _handle_add(self, args):
        todo = self.todo_service.create_todo(args.title, args.description)
        print(f"Added todo: {todo.title} (ID: {todo.id})")

    def _handle_list(self, args):
        # Determine filter for completion status
        completed_filter = None
        if args.completed:
            completed_filter = True
        elif args.pending:
            completed_filter = False

        todos = self.todo_service.get_all_todos(
            completed=completed_filter,
            sort_by=args.sort
        )

        if not todos:
            print("No todos found.")
            return

        for todo in todos:
            status = "✓" if todo.completed else "○"
            print(f"[{status}] {todo.id}: {todo.title}")
            if todo.description:
                print(f"      Description: {todo.description}")
            if todo.created_at:
                print(f"      Created: {todo.created_at.strftime('%Y-%m-%d %H:%M')}")

    def _handle_complete(self, args):
        success = self.todo_service.complete_todo(args.id)
        if success:
            print(f"Todo {args.id} marked as completed")
        else:
            print(f"Error: Todo with ID {args.id} not found")
            sys.exit(1)

    def _handle_edit(self, args):
        success = self.todo_service.update_todo(args.id, args.title, args.description)
        if success:
            print(f"Todo {args.id} updated successfully")
        else:
            print(f"Error: Todo with ID {args.id} not found")
            sys.exit(1)

    def _handle_delete(self, args):
        success = self.todo_service.delete_todo(args.id)
        if success:
            print(f"Todo {args.id} deleted successfully")
        else:
            print(f"Error: Todo with ID {args.id} not found")
            sys.exit(1)
```

### 3.6 Main Application Entry Point (`src/main.py`)
```python
from src.core.application.todo_service import TodoService
from src.infrastructure.repositories.in_memory_todo_repository import InMemoryTodoRepository
from src.interfaces.cli import CLIInterface

def main():
    # Initialize the repository
    repository = InMemoryTodoRepository()

    # Initialize the service
    todo_service = TodoService(repository)

    # Initialize the CLI interface
    cli = CLIInterface(todo_service)

    # Run the application
    cli.run()

if __name__ == "__main__":
    main()
```

## 4. File Structure

```
src/
├── core/
│   ├── domain/
│   │   ├── __init__.py
│   │   └── todo.py
│   ├── ports/
│   │   ├── __init__.py
│   │   └── todo_repository.py
│   └── application/
│       ├── __init__.py
│       └── todo_service.py
├── infrastructure/
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── in_memory_todo_repository.py
│   └── __init__.py
├── interfaces/
│   ├── __init__.py
│   └── cli.py
├── __init__.py
└── main.py
```

## 5. Technology Stack

### 5.1 Primary Technology
- **Python 3.10+**: Core programming language
- **Standard Library**: argparse for CLI parsing, json for serialization, os for file operations

### 5.2 Architecture Patterns
- **Dependency Inversion**: Using abstract interfaces for repository pattern
- **Single Responsibility**: Each class has a single, well-defined purpose
- **Separation of Concerns**: Domain, application, and infrastructure layers

## 6. Data Flow

### 6.1 Add Todo Flow
1. CLI receives `todo add "Title"` command
2. CLI parser extracts command and arguments
3. CLI interface calls `TodoService.create_todo()`
4. Service creates new `Todo` entity
5. Service calls `FileTodoRepository.add()` to persist
6. Repository serializes and saves to JSON file

### 6.2 List Todos Flow
1. CLI receives `todo list` command with optional filters
2. CLI parser extracts command and options
3. CLI interface calls `TodoService.get_all_todos()`
4. Service retrieves all todos from repository
5. Service applies filters and sorting
6. CLI interface formats and displays results

### 6.3 Complete Todo Flow
1. CLI receives `todo complete <id>` command
2. CLI parser extracts command and ID
3. CLI interface calls `TodoService.complete_todo()`
4. Service retrieves todo from repository
5. Service marks todo as completed and updates timestamp
6. Service calls repository to update the todo
7. Repository persists the updated todo to JSON file

## 7. Error Handling Strategy

### 7.1 Domain Layer
- Input validation in the `Todo` entity constructor
- Proper error propagation to higher layers

### 7.2 Application Layer
- Business logic validation
- Proper error handling for non-existent todos

### 7.3 Infrastructure Layer
- File I/O error handling
- JSON serialization/deserialization error handling
- Graceful degradation when persistence fails

## 8. Performance Considerations

### 8.1 File I/O Optimization
- Read entire file once per operation
- Write entire file once per operation
- For large todo lists, consider memory-mapped files

### 8.2 Memory Usage
- Load all todos into memory at once (acceptable for small datasets)
- Consider lazy loading for very large todo lists

## 9. Testing Strategy

### 9.1 Unit Tests
- Test domain entity methods and validation
- Test application service logic
- Test repository interface implementations

### 9.2 Integration Tests
- Test CLI command flows
- Test end-to-end functionality
- Test file persistence behavior

### 9.3 Test Coverage
- 100% coverage for core domain logic
- High coverage for application services
- Integration tests for CLI interface

## 10. Security Considerations

### 10.1 Input Validation
- Validate all user inputs in the domain layer
- Prevent injection attacks through proper serialization

### 10.2 File Security
- Validate file paths to prevent directory traversal
- Handle file permissions appropriately

## 11. Deployment Strategy

### 11.1 Packaging
- Package as Python application with setup.py
- Include all dependencies in requirements.txt
- Provide installation instructions

### 11.2 Execution
- Run directly with Python interpreter
- Create command-line executable script
- Cross-platform compatibility

## 12. Maintenance and Evolution

### 12.1 Extension Points
- Repository interface allows for different persistence strategies
- Service layer can be extended with new business logic
- CLI interface can be extended with new commands

### 12.2 Backward Compatibility
- Maintain same command-line interface
- Preserve data format compatibility
- Follow semantic versioning for breaking changes