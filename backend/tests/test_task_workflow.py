import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock
import json


client = TestClient(app)

def test_complete_task_management_workflow():
    """Test the complete task management workflow: create, read, update, complete, delete"""
    
    user_id = "workflow_test_user"
    
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = user_id
        
        # 1. Test creating a task
        response = client.post(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token"},
            json={
                "title": "Workflow Test Task",
                "description": "Testing the complete workflow",
                "priority": "medium",
                "category": "test",
                "tags": ["workflow", "test"]
            }
        )
        assert response.status_code == 200
        created_task = response.json()["data"]
        assert created_task["title"] == "Workflow Test Task"
        assert created_task["description"] == "Testing the complete workflow"
        assert created_task["user_id"] == user_id
        assert created_task["priority"] == "medium"
        assert created_task["category"] == "test"
        assert "workflow" in created_task["tags"]
        assert "test" in created_task["tags"]
        assert created_task["completed"] is False

        task_id = created_task["id"]
        assert task_id is not None
        
        # 2. Test retrieving the created task
        response = client.get(
            f"/api/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 200
        retrieved_task = response.json()["data"]
        assert retrieved_task["id"] == task_id
        assert retrieved_task["title"] == "Workflow Test Task"
        
        # 3. Test retrieving all tasks for user
        response = client.get(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 200
        tasks_list = response.json()["data"]
        task_ids = [task["id"] for task in tasks_list]
        assert task_id in task_ids
        
        # 4. Test updating the task
        response = client.put(
            f"/api/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token"},
            json={
                "title": "Updated Workflow Test Task",
                "description": "Updated description for workflow test",
                "priority": "high",
                "category": "updated-test",
                "tags": ["updated", "workflow", "final-test"]
            }
        )
        assert response.status_code == 200
        updated_task = response.json()["data"]
        assert updated_task["id"] == task_id
        assert updated_task["title"] == "Updated Workflow Test Task"
        assert updated_task["description"] == "Updated description for workflow test"
        assert updated_task["priority"] == "high"
        assert updated_task["category"] == "updated-test"
        assert "updated" in updated_task["tags"]
        assert "workflow" in updated_task["tags"]
        assert "final-test" in updated_task["tags"]
        
        # 5. Test toggling completion status
        response = client.patch(
            f"/api/tasks/{task_id}/complete",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 200
        completed_task = response.json()["data"]
        assert completed_task["id"] == task_id
        assert completed_task["completed"] is True  # Should now be completed
        
        # 6. Test toggling completion status back
        response = client.patch(
            f"/api/tasks/{task_id}/complete",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 200
        uncompleted_task = response.json()["data"]
        assert uncompleted_task["id"] == task_id
        assert uncompleted_task["completed"] is False  # Should now be uncompleted again
        
        # 7. Test deleting the task
        response = client.delete(
            f"/api/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 200
        delete_result = response.json()["data"]
        assert delete_result["ok"] is True
        
        # 8. Verify the task is gone
        response = client.get(
            f"/api/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code in [404, 422]  # Should not be found after deletion


def test_multiple_tasks_workflow():
    """Test workflow with multiple tasks to ensure isolation and correctness"""
    
    user_id = "multi_task_user"
    
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = user_id
        
        # Create multiple tasks
        task_titles = ["Task 1", "Task 2", "Task 3"]
        created_tasks = []
        
        for i, title in enumerate(task_titles):
            response = client.post(
                "/api/tasks",
                headers={"Authorization": "Bearer valid_token"},
                json={
                    "title": title,
                    "description": f"Description for {title}",
                    "priority": "medium" if i % 2 == 0 else "high"
                }
            )
            assert response.status_code == 200
            task = response.json()["data"]
            assert task["user_id"] == user_id
            assert task["title"] == title
            created_tasks.append(task)
        
        # Verify all tasks were created with correct properties
        assert len(created_tasks) == 3
        for i, task in enumerate(created_tasks):
            assert task["title"] == task_titles[i]
            assert task["user_id"] == user_id
            expected_priority = "medium" if i % 2 == 0 else "high"
            assert task["priority"] == expected_priority
        
        # Get all tasks and verify they all belong to the same user
        response = client.get(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 200
        all_tasks = response.json()["data"]
        assert len(all_tasks) >= 3  # At least the 3 we created
        
        # Verify all returned tasks belong to the correct user
        for task in all_tasks:
            if task["id"] in [t["id"] for t in created_tasks]:
                # These are our created tasks - verify they have the right user_id
                assert task["user_id"] == user_id
        
        # Update one of the tasks
        task_id_to_update = created_tasks[0]["id"]
        response = client.put(
            f"/api/tasks/{task_id_to_update}",
            headers={"Authorization": "Bearer valid_token"},
            json={
                "title": "Updated Task 1",
                "completed": True
            }
        )
        assert response.status_code == 200
        updated_task = response.json()["data"]
        assert updated_task["id"] == task_id_to_update
        assert updated_task["title"] == "Updated Task 1"
        assert updated_task["completed"] is True
        
        # Toggle completion on another task
        task_id_to_toggle = created_tasks[1]["id"]
        response = client.patch(
            f"/api/tasks/{task_id_to_toggle}/complete",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 200
        toggled_task = response.json()["data"]
        assert toggled_task["id"] == task_id_to_toggle
        assert toggled_task["completed"] is True
        
        # Delete one task
        task_id_to_delete = created_tasks[2]["id"]
        response = client.delete(
            f"/api/tasks/{task_id_to_delete}",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 200
        
        # Verify only the deleted task is affected
        response = client.get(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 200
        remaining_tasks = response.json()["data"]
        
        # The deleted task should not appear in the list
        remaining_task_ids = [task["id"] for task in remaining_tasks]
        assert task_id_to_delete not in remaining_task_ids