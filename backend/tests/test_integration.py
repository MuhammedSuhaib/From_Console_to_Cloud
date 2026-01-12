import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock
import json


client = TestClient(app)

# Mock JWT token for testing
MOCK_JWT_TOKEN = "mock_jwt_token_for_testing"


def test_authenticated_task_operations():
    """Test complete task management flow with authentication"""
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = "test_user_123"
        
        # Test creating a task
        response = client.post(
            "/api/tasks",
            headers={"Authorization": f"Bearer {MOCK_JWT_TOKEN}"},
            json={
                "title": "Integration Test Task",
                "description": "Testing the complete task flow",
                "priority": "medium",
                "category": "integration-test",
                "tags": ["test", "integration"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["title"] == "Integration Test Task"
        assert data["data"]["user_id"] == "test_user_123"
        
        # Capture the task ID for later tests
        task_id = data["data"]["id"]
        
        # Test getting all tasks
        response = client.get(
            "/api/tasks",
            headers={"Authorization": f"Bearer {MOCK_JWT_TOKEN}"}
        )
        assert response.status_code == 200
        tasks = response.json()["data"]
        assert len(tasks) >= 1
        task_titles = [task["title"] for task in tasks]
        assert "Integration Test Task" in [t["title"] for t in tasks]
        
        # Test updating a task
        response = client.put(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {MOCK_JWT_TOKEN}"},
            json={
                "title": "Updated Integration Test Task",
                "completed": True
            }
        )
        assert response.status_code == 200
        updated_task = response.json()["data"]
        assert updated_task["title"] == "Updated Integration Test Task"
        assert updated_task["completed"] is True
        
        # Test toggling completion
        response = client.patch(
            f"/api/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer {MOCK_JWT_TOKEN}"}
        )
        assert response.status_code == 200
        toggled_task = response.json()["data"]
        assert toggled_task["completed"] is False  # Toggled back to False
        
        # Test deleting a task
        response = client.delete(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {MOCK_JWT_TOKEN}"}
        )
        assert response.status_code == 200
        assert response.json()["data"]["ok"] is True


def test_user_isolation():
    """Test that one user can't access another user's data"""
    # Mock user 1
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = "user_1"
        
        # Create a task for user 1
        response = client.post(
            "/api/tasks",
            headers={"Authorization": f"Bearer {MOCK_JWT_TOKEN}"},
            json={"title": "User 1 Task", "description": "Task for user 1"}
        )
        assert response.status_code == 200
        user1_task = response.json()["data"]
        task_id = user1_task["id"]
        assert user1_task["user_id"] == "user_1"
    
    # Mock user 2 and check they can't access user 1's task
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = "user_2"
        
        # User 2 tries to update user 1's task (should fail with 404)
        response = client.put(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {MOCK_JWT_TOKEN}"},
            json={"title": "User 2 trying to update user 1's task"}
        )
        # Either 404 (not found) or 422 (validation error) depending on implementation
        # The important thing is user 2 can't modify user 1's task
        assert response.status_code in [404, 422]

def test_unauthorized_access():
    """Test that unauthorized requests are properly rejected"""
    # Try to access tasks without authorization
    response = client.get("/api/tasks")
    assert response.status_code == 401
    
    # Try to create a task without authorization
    response = client.post(
        "/api/tasks",
        json={"title": "Unauthorized Task", "description": "Should not be created"}
    )
    assert response.status_code == 401
    
    # Try to access a specific task without authorization
    response = client.get("/api/tasks/1")
    assert response.status_code == 401