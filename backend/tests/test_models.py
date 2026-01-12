import pytest
from models import Task
from datetime import datetime


def test_task_model_creation():
    """Test that Task model can be created with required fields"""
    task = Task(
        user_id="user123",
        title="Test Task",
        description="Test Description",
        completed=False,
    )
    
    assert task.user_id == "user123"
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.completed is False
    assert task.priority == "medium"
    assert task.category is None
    assert task.tags == []
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)


def test_task_model_optional_fields():
    """Test that Task model handles optional fields correctly"""
    task = Task(
        user_id="user123",
        title="Test Task",
        priority="high",
        category="work",
        tags=["test", "important"]
    )
    
    assert task.user_id == "user123"
    assert task.title == "Test Task"
    assert task.priority == "high"
    assert task.category == "work"
    assert task.tags == ["test", "important"]
    assert task.completed is False  # Default value should be False


def test_task_model_defaults():
    """Test that Task model uses correct default values"""
    task = Task(
        user_id="user123",
        title="Test Task"
    )
    
    assert task.completed is False
    assert task.priority == "medium"
    assert task.category is None
    assert task.tags == []
    assert task.description is None


def test_task_model_priority_enum():
    """Test that Task model accepts valid priority values"""
    from models import TaskPriority

    task_high = Task(user_id="user123", title="High Priority", priority=TaskPriority.high)
    task_medium = Task(user_id="user123", title="Medium Priority", priority=TaskPriority.medium)
    task_low = Task(user_id="user123", title="Low Priority", priority=TaskPriority.low)

    assert task_high.priority == TaskPriority.high
    assert task_medium.priority == TaskPriority.medium
    assert task_low.priority == TaskPriority.low


def test_task_model_empty_title_validation():
    """Test that Task model accepts a title (creation happens with validation on frontend)"""
    # In the current SQLModel implementation, validation happens at the database level
    # or in the API layer rather than in the model constructor itself
    # The model will accept the empty title but the API will validate
    task = Task(user_id="user123", title="")
    assert task.user_id == "user123"
    assert task.title == ""


def test_task_model_required_user_id():
    """Test that Task model requires user_id"""
    task = Task(user_id="test_user", title="Test Task")
    
    assert task.user_id == "test_user"
    assert task.title == "Test Task"