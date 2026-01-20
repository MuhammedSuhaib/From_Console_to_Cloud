import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
from models import Task
from database import get_session
import json

# Create an in-memory SQLite database for testing
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


class TestMCPTaskTools:
    """Unit tests for MCP task tools"""

    def test_add_task_tool(self, session: Session):
        """Test the add_task MCP tool"""
        from mcp_server.mcp_server import add_task

        # Test adding a task
        user_id = "test_user_123"
        title = "Test Task"
        description = "Test Description"

        result = add_task(user_id, title, description)

        # Verify the task was created in the database
        created_task = session.exec(
            select(Task).where(Task.user_id == user_id)
        ).first()

        assert created_task is not None
        assert created_task.title == title
        assert created_task.description == description
        assert created_task.user_id == user_id
        assert created_task.completed is False  # Default value

    def test_add_task_without_description(self, session: Session):
        """Test the add_task MCP tool without description"""
        from mcp_server.mcp_server import add_task

        user_id = "test_user_456"
        title = "Task Without Description"

        result = add_task(user_id, title)

        # Verify the task was created in the database
        created_task = session.exec(
            select(Task).where(Task.user_id == user_id)
        ).first()

        assert created_task is not None
        assert created_task.title == title
        assert created_task.description is None
        assert created_task.user_id == user_id

    def test_list_tasks_tool_all(self, session: Session):
        """Test the list_tasks MCP tool with all status"""
        from mcp_server.mcp_server import list_tasks

        # Create test tasks
        user_id = "test_user_789"

        # Add a few tasks for the user
        task1 = Task(user_id=user_id, title="Task 1", description="Desc 1")
        task2 = Task(user_id=user_id, title="Task 2", description="Desc 2", completed=True)
        task3 = Task(user_id=user_id, title="Task 3", description="Desc 3")

        session.add(task1)
        session.add(task2)
        session.add(task3)
        session.commit()

        # Test listing all tasks
        result = list_tasks(user_id, "all")

        # The result should contain all tasks in a text format
        assert "Task 1" in result
        assert "Task 2" in result
        assert "Task 3" in result
        assert "✅" in result or "⏳" in result  # Check for completion status indicators

    def test_list_tasks_tool_pending(self, session: Session):
        """Test the list_tasks MCP tool with pending status"""
        from mcp_server.mcp_server import list_tasks

        # Create test tasks
        user_id = "test_user_000"

        # Add a mix of pending and completed tasks
        task1 = Task(user_id=user_id, title="Pending Task 1", completed=False)
        task2 = Task(user_id=user_id, title="Completed Task", completed=True)
        task3 = Task(user_id=user_id, title="Pending Task 2", completed=False)

        session.add(task1)
        session.add(task2)
        session.add(task3)
        session.commit()

        # Test listing only pending tasks
        result = list_tasks(user_id, "pending")

        # The result should contain only pending tasks
        assert "Pending Task 1" in result
        assert "Pending Task 2" in result
        assert "Completed Task" not in result
        # Should have 2 task entries (pending ones)
        assert result.count("⏳") == 2  # Check for pending status indicators

    def test_list_tasks_tool_completed(self, session: Session):
        """Test the list_tasks MCP tool with completed status"""
        from mcp_server.mcp_server import list_tasks

        # Create test tasks
        user_id = "test_user_111"

        # Add a mix of pending and completed tasks
        task1 = Task(user_id=user_id, title="Pending Task", completed=False)
        task2 = Task(user_id=user_id, title="Completed Task 1", completed=True)
        task3 = Task(user_id=user_id, title="Completed Task 2", completed=True)

        session.add(task1)
        session.add(task2)
        session.add(task3)
        session.commit()

        # Test listing only completed tasks
        result = list_tasks(user_id, "completed")

        # The result should contain only completed tasks
        assert "Completed Task 1" in result
        assert "Completed Task 2" in result
        assert "Pending Task" not in result
        # Should have 2 task entries (completed ones)
        assert result.count("✅") == 2  # Check for completed status indicators

    def test_complete_task_tool(self, session: Session):
        """Test the complete_task MCP tool"""
        from mcp_server.mcp_server import complete_task

        # Create a test task
        user_id = "test_user_222"
        task = Task(user_id=user_id, title="Incomplete Task", completed=False)
        session.add(task)
        session.commit()

        # Verify task is initially not completed
        assert task.completed is False

        # Complete the task
        result = complete_task(user_id, task.id)

        # Verify the task is now completed
        updated_task = session.get(Task, task.id)
        assert updated_task is not None
        assert updated_task.completed is True

    def test_delete_task_tool(self, session: Session):
        """Test the delete_task MCP tool"""
        from mcp_server.mcp_server import delete_task

        # Create a test task
        user_id = "test_user_333"
        task = Task(user_id=user_id, title="Task to Delete", description="Will be deleted")
        session.add(task)
        session.commit()

        # Verify task exists
        existing_task = session.get(Task, task.id)
        assert existing_task is not None

        # Delete the task
        result = delete_task(user_id, task.id)

        # Verify the task is deleted
        deleted_task = session.get(Task, task.id)
        assert deleted_task is None

    def test_update_task_tool(self, session: Session):
        """Test the update_task MCP tool"""
        from mcp_server.mcp_server import update_task

        # Create a test task
        user_id = "test_user_444"
        task = Task(user_id=user_id, title="Original Title", description="Original Description", completed=False)
        session.add(task)
        session.commit()

        # Update the task
        new_title = "Updated Title"
        new_description = "Updated Description"

        result = update_task(user_id, task.id, title=new_title, description=new_description)

        # Verify the task is updated
        updated_task = session.get(Task, task.id)
        assert updated_task is not None
        assert updated_task.title == new_title
        assert updated_task.description == new_description

    def test_update_task_partial(self, session: Session):
        """Test the update_task MCP tool with partial updates"""
        from mcp_server.mcp_server import update_task

        # Create a test task
        user_id = "test_user_555"
        task = Task(user_id=user_id, title="Original Title", description="Original Description", completed=False)
        session.add(task)
        session.commit()

        # Update only the title
        new_title = "Updated Title Only"

        result = update_task(user_id, task.id, title=new_title)

        # Verify only the title is updated and result indicates success
        updated_task = session.get(Task, task.id)
        assert updated_task is not None
        assert updated_task.title == new_title
        assert updated_task.description == "Original Description"  # Should remain unchanged
        assert updated_task.completed is False  # Should remain unchanged
        assert "Success" in result  # Result should indicate success

    def test_user_isolation_for_add_task(self, session: Session):
        """Test that users can only access their own tasks when adding"""
        from mcp_server.mcp_server import add_task, list_tasks

        # Create tasks for different users
        user1_id = "user_1"
        user2_id = "user_2"

        # Add task for user 1
        add_task(user1_id, "User 1 Task", "Task for user 1")

        # Add task for user 2
        add_task(user2_id, "User 2 Task", "Task for user 2")

        # Verify user 1 only sees their own tasks
        user1_tasks = list_tasks(user1_id, "all")
        assert "User 1 Task" in user1_tasks
        assert "User 2 Task" not in user1_tasks

        # Verify user 2 only sees their own tasks
        user2_tasks = list_tasks(user2_id, "all")
        assert "User 2 Task" in user2_tasks
        assert "User 1 Task" not in user2_tasks

    def test_user_isolation_for_list_tasks(self, session: Session):
        """Test that users can only access their own tasks when listing"""
        from mcp_server.mcp_server import add_task, list_tasks

        # Create tasks for different users
        user1_id = "user_3"
        user2_id = "user_4"

        # Add multiple tasks for each user
        add_task(user1_id, "User 1 Task 1", "Task 1 for user 1")
        add_task(user1_id, "User 1 Task 2", "Task 2 for user 1")
        add_task(user2_id, "User 2 Task 1", "Task 1 for user 2")
        add_task(user2_id, "User 2 Task 2", "Task 2 for user 2")

        # Verify user 1 only sees their own tasks
        user1_tasks = list_tasks(user1_id, "all")
        assert "User 1 Task 1" in user1_tasks
        assert "User 1 Task 2" in user1_tasks
        assert "User 2 Task 1" not in user1_tasks
        assert "User 2 Task 2" not in user1_tasks

        # Verify user 2 only sees their own tasks
        user2_tasks = list_tasks(user2_id, "all")
        assert "User 2 Task 1" in user2_tasks
        assert "User 2 Task 2" in user2_tasks
        assert "User 1 Task 1" not in user2_tasks
        assert "User 1 Task 2" not in user2_tasks

    def test_user_isolation_for_complete_task(self, session: Session):
        """Test that users can only complete their own tasks"""
        from mcp_server.mcp_server import add_task, complete_task

        # Create tasks for different users
        user1_id = "user_5"
        user2_id = "user_6"

        # Add tasks for each user
        result1 = add_task(user1_id, "User 1 Task", "Task for user 1")
        result2 = add_task(user2_id, "User 2 Task", "Task for user 2")

        # Get the tasks from the database to get their IDs
        task1 = session.exec(select(Task).where(Task.user_id == user1_id).where(Task.title == "User 1 Task")).first()
        task2 = session.exec(select(Task).where(Task.user_id == user2_id).where(Task.title == "User 2 Task")).first()

        assert task1 is not None
        assert task2 is not None

        # Initially both tasks should be incomplete
        assert task1.completed is False
        assert task2.completed is False

        # User 1 should be able to complete their own task
        result = complete_task(user1_id, task1.id)
        assert "Success" in result

        # Refresh the task from the database
        session.refresh(task1)
        assert task1.completed is True  # Task 1 should now be completed

        # User 1 should NOT be able to complete user 2's task (but in our implementation it will just say task not found)
        result = complete_task(user1_id, task2.id)
        assert "not found" in result or "Error" in result  # Should return error message

    def test_parameter_validation_for_add_task(self, session: Session):
        """Test parameter validation for add_task tool"""
        from mcp_server.mcp_server import add_task

        # Test with empty title (should return error)
        result = add_task("test_user", "", "Description")
        # Result should indicate an error for empty title
        assert "Error" in result or "error" in result.lower() or "invalid" in result.lower()

        # Test with None user_id (should return error)
        result = add_task(None, "Valid Title", "Valid Description")
        # Result should indicate an error for invalid user_id
        assert "Error" in result or "error" in result.lower() or "invalid" in result.lower()

    def test_error_handling_for_nonexistent_task(self, session: Session):
        """Test error handling when operating on non-existent tasks"""
        from mcp_server.mcp_server import complete_task, delete_task, update_task

        user_id = "test_user_777"
        nonexistent_task_id = 99999  # Definitely doesn't exist

        # Test completing non-existent task
        result = complete_task(user_id, nonexistent_task_id)
        # Result should indicate error or task not found
        assert "not found" in result.lower() or "error" in result.lower() or "Error" in result

        # Test deleting non-existent task
        result = delete_task(user_id, nonexistent_task_id)
        # Result should indicate error or task not found
        assert "not found" in result.lower() or "error" in result.lower() or "Error" in result

        # Test updating non-existent task
        result = update_task(user_id, nonexistent_task_id, title="New Title")
        # Result should indicate error or task not found
        assert "not found" in result.lower() or "error" in result.lower() or "Error" in result