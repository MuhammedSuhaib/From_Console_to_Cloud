import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock
from sqlmodel import Session, select
import json


client = TestClient(app)

def test_user_data_isolation():
    """Test that users can only access their own data"""
    
    # Mock user 1
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = "user_1"
        
        # Create a task for user 1
        response = client.post(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token_for_user1"},
            json={
                "title": "User 1 Task",
                "description": "This belongs to user 1",
                "priority": "medium"
            }
        )
        assert response.status_code == 200
        user1_task = response.json()["data"]
        assert user1_task["user_id"] == "user_1"
        task_id = user1_task["id"]
    
    # Now mock user 2 and try to access/modify user 1's task
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = "user_2"
        
        # Try to get user 1's task as user 2 (should return 404 or some indication that user 2 can't see it)
        response = client.get(
            f"/api/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token_for_user2"}
        )
        
        # This depends on the implementation - it might return 404 or 403
        # The key is that user 2 should not be able to access user 1's task
        assert response.status_code in [404, 403]  # Should not be able to access another user's task
        
        # Try to update user 1's task as user 2
        response = client.put(
            f"/api/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token_for_user2"},
            json={
                "title": "User 2 trying to update user 1's task"
            }
        )
        assert response.status_code in [404, 403]  # Should not be able to modify another user's task
        
        # Try to delete user 1's task as user 2
        response = client.delete(
            f"/api/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token_for_user2"}
        )
        assert response.status_code in [404, 403]  # Should not be able to delete another user's task
        
        # Try to toggle completion of user 1's task as user 2
        response = client.patch(
            f"/api/tasks/{task_id}/complete",
            headers={"Authorization": "Bearer valid_token_for_user2"}
        )
        assert response.status_code in [404, 403]  # Should not be able to modify another user's task


def test_user_can_access_own_data():
    """Test that users can access their own data"""
    
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = "user_3"
        
        # Create a task for user 3
        response = client.post(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token_for_user3"},
            json={
                "title": "User 3 Task",
                "description": "This belongs to user 3",
                "priority": "high"
            }
        )
        assert response.status_code == 200
        user3_task = response.json()["data"]
        assert user3_task["user_id"] == "user_3"
        task_id = user3_task["id"]
        
        # User 3 should be able to get their own task
        response = client.get(
            f"/api/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token_for_user3"}
        )
        assert response.status_code == 200
        returned_task = response.json()["data"]
        assert returned_task["id"] == task_id
        assert returned_task["user_id"] == "user_3"
        
        # User 3 should be able to update their own task
        response = client.put(
            f"/api/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token_for_user3"},
            json={
                "title": "User 3 Updated Task",
                "priority": "low"
            }
        )
        assert response.status_code == 200
        updated_task = response.json()["data"]
        assert updated_task["title"] == "User 3 Updated Task"
        assert updated_task["priority"] == "low"
        
        # User 3 should be able to delete their own task
        response = client.delete(
            f"/api/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token_for_user3"}
        )
        assert response.status_code == 200  # Should be able to delete their own task


def test_user_sees_only_own_tasks():
    """Test that when getting all tasks, users only see their own"""
    
    # Create tasks for different users in a realistic scenario
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = "user_a"
        
        # Create multiple tasks for user A
        response = client.post(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token_for_user_a"},
            json={"title": "User A Task 1", "priority": "medium"}
        )
        assert response.status_code == 200
        task_a1_id = response.json()["data"]["id"]

        response = client.post(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token_for_user_a"},
            json={"title": "User A Task 2", "priority": "high"}
        )
        assert response.status_code == 200
        task_a2_id = response.json()["data"]["id"]

    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = "user_b"

        # Create multiple tasks for user B
        response = client.post(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token_for_user_b"},
            json={"title": "User B Task 1", "priority": "low"}
        )
        assert response.status_code == 200
        task_b1_id = response.json()["data"]["id"]

        response = client.post(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token_for_user_b"},
            json={"title": "User B Task 2", "priority": "high"}
        )
        assert response.status_code == 200
        task_b2_id = response.json()["data"]["id"]
    
    # Now test that each user only sees their own tasks
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = "user_a"
        
        response = client.get(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token_for_user_a"}
        )
        assert response.status_code == 200
        user_a_tasks = response.json()["data"]
        
        # Check that user A only sees their own tasks
        user_a_task_ids = [task["id"] for task in user_a_tasks]
        assert task_a1_id in user_a_task_ids
        assert task_a2_id in user_a_task_ids
        assert task_b1_id not in user_a_task_ids  # User A should not see User B's tasks
        assert task_b2_id not in user_a_task_ids  # User A should not see User B's tasks
    
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = "user_b"
        
        response = client.get(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token_for_user_b"}
        )
        assert response.status_code == 200
        user_b_tasks = response.json()["data"]
        
        # Check that user B only sees their own tasks
        user_b_task_ids = [task["id"] for task in user_b_tasks]
        assert task_b1_id in user_b_task_ids
        assert task_b2_id in user_b_task_ids
        assert task_a1_id not in user_b_task_ids  # User B should not see User A's tasks
        assert task_a2_id not in user_b_task_ids  # User B should not see User A's tasks