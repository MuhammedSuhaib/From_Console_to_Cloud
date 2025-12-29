"""
Simple tests for the todo application
"""
import pytest
from src.todo import TodoApp, Todo


class TestTodo:
    def test_todo_creation(self):
        """Test creating a todo"""
        todo = Todo(1, "Test title", "Test description")

        assert todo.id == 1
        assert todo.title == "Test title"
        assert todo.description == "Test description"
        assert todo.completed is False

    def test_todo_repr(self):
        """Test todo string representation"""
        todo = Todo(1, "Test title")
        repr_str = repr(todo)

        assert "Todo(id=1, title='Test title', completed=False)" in repr_str


class TestTodoApp:
    def setup_method(self):
        self.app = TodoApp()

    def test_add_todo(self):
        """Test adding a todo"""
        todo = self.app.add_todo("Test todo")

        assert len(self.app.todos) == 1
        assert todo.id == 1
        assert todo.title == "Test todo"
        assert todo.completed is False

    def test_add_todo_with_description(self):
        """Test adding a todo with description"""
        todo = self.app.add_todo("Test todo", "Test description")

        assert todo.title == "Test todo"
        assert todo.description == "Test description"

    def test_add_todo_empty_title(self):
        """Test adding a todo with empty title raises error"""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            self.app.add_todo("")

    def test_get_todo(self):
        """Test getting a todo by ID"""
        todo = self.app.add_todo("Test todo")
        retrieved = self.app.get_todo(1)

        assert retrieved is not None
        assert retrieved.id == 1
        assert retrieved.title == "Test todo"

    def test_get_todo_not_found(self):
        """Test getting a non-existent todo returns None"""
        result = self.app.get_todo(999)

        assert result is None

    def test_list_todos(self):
        """Test listing all todos"""
        self.app.add_todo("Todo 1")
        self.app.add_todo("Todo 2")

        todos = self.app.list_todos()

        assert len(todos) == 2

    def test_list_todos_filtered_completed(self):
        """Test listing todos with completed filter"""
        todo1 = self.app.add_todo("Todo 1")
        todo2 = self.app.add_todo("Todo 2")

        self.app.complete_todo(2)

        completed_todos = self.app.list_todos(completed=True)
        pending_todos = self.app.list_todos(completed=False)

        assert len(completed_todos) == 1
        assert completed_todos[0].id == 2

        assert len(pending_todos) == 1
        assert pending_todos[0].id == 1

    def test_update_todo(self):
        """Test updating a todo"""
        todo = self.app.add_todo("Original title", "Original description")

        success = self.app.update_todo(1, "New title", "New description")

        assert success is True
        assert todo.title == "New title"
        assert todo.description == "New description"

    def test_update_todo_not_found(self):
        """Test updating a non-existent todo"""
        success = self.app.update_todo(999, "New title")

        assert success is False

    def test_complete_todo(self):
        """Test completing a todo"""
        todo = self.app.add_todo("Test todo")

        success = self.app.complete_todo(1)

        assert success is True
        assert todo.completed is True

    def test_complete_todo_not_found(self):
        """Test completing a non-existent todo"""
        success = self.app.complete_todo(999)

        assert success is False

    def test_delete_todo(self):
        """Test deleting a todo"""
        self.app.add_todo("Test todo")

        success = self.app.delete_todo(1)

        assert success is True
        assert len(self.app.todos) == 0

    def test_delete_todo_not_found(self):
        """Test deleting a non-existent todo"""
        success = self.app.delete_todo(999)

        assert success is False