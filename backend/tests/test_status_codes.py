import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock


client = TestClient(app)

def test_all_api_endpoints_return_proper_status_codes():
    """Verify all API endpoints return proper status codes"""
    
    user_id = "status_test_user"
    
    # Test GET /api/tasks - should return 200 when authenticated
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = user_id
        
        response = client.get(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token"}
        )
        # Should return 200 OK (might be 204 No Content if no tasks exist)
        assert response.status_code in [200, 204, 404]
        
        # Check the response structure
        if response.status_code == 200:
            data = response.json()
            assert "data" in data  # Should return proper response format
            assert isinstance(data["data"], list)  # Should return list of tasks
    
    # Test POST /api/tasks - should return 200 on success
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = user_id
        
        response = client.post(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token"},
            json={
                "title": "Status Code Test Task",
                "description": "Testing proper status codes",
                "priority": "medium"
            }
        )
        # Should return 200 OK on success
        assert response.status_code == 200

        # Check response structure
        data = response.json()
        assert "data" in data  # Should return proper response format
        task_data = data["data"]
        assert "id" in task_data
        assert task_data["user_id"] == user_id
        assert task_data["title"] == "Status Code Test Task"
        assert task_data["completed"] is False

        task_id = task_data["id"]
    
    # Test GET /api/tasks/{id} - should return 200 for existing task
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = user_id
        
        response = client.get(
            f"/api/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token"}
        )
        # Should return 200 for existing task
        assert response.status_code == 200
        
        # Check response structure
        data = response.json()
        assert "data" in data
        task_data = data["data"]
        assert task_data["id"] == task_id
        assert task_data["user_id"] == user_id
    
    # Test PUT /api/tasks/{id} - should return 200 on success
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = user_id
        
        response = client.put(
            f"/api/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token"},
            json={
                "title": "Updated Status Code Test Task",
                "description": "Updated description for status code test",
                "completed": True
            }
        )
        # Should return 200 OK on success
        assert response.status_code == 200
        
        # Check response structure
        data = response.json()
        assert "data" in data
        updated_task = data["data"]
        assert updated_task["id"] == task_id
        assert updated_task["title"] == "Updated Status Code Test Task"
        assert updated_task["completed"] is True
    
    # Test PATCH /api/tasks/{id}/complete - should return 200 on success
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = user_id
        
        response = client.patch(
            f"/api/tasks/{task_id}/complete",
            headers={"Authorization": "Bearer valid_token"}
        )
        # Should return 200 OK on success
        assert response.status_code == 200
        
        # Check response structure
        data = response.json()
        assert "data" in data
        toggled_task = data["data"]
        assert toggled_task["id"] == task_id
        assert toggled_task["completed"] is False  # Toggled back to False
    
    # Test DELETE /api/tasks/{id} - should return 200 on success
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = user_id
        
        response = client.delete(
            f"/api/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token"}
        )
        # Should return 200 OK on success
        assert response.status_code == 200
        
        # Check response structure
        data = response.json()
        assert "data" in data
        delete_result = data["data"]
        assert delete_result["ok"] is True


def test_error_status_codes():
    """Test that endpoints return proper error status codes"""
    
    # Test unauthenticated access - should return 401
    response = client.get("/api/tasks")
    assert response.status_code == 401
    
    response = client.post("/api/tasks", json={"title": "Unauthorized task"})
    assert response.status_code == 401
    
    response = client.put("/api/tasks/1", json={"title": "Unauthorized update"})
    assert response.status_code == 401
    
    response = client.delete("/api/tasks/1")
    assert response.status_code == 401
    
    response = client.patch("/api/tasks/1/complete")
    assert response.status_code == 401
    
    # Test authenticated access to non-existent task - should return 404
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = "test_user"
        
        response = client.get(
            "/api/tasks/999999",  # Non-existent task ID
            headers={"Authorization": "Bearer valid_token"}
        )
        # Should return 404 for non-existent resource
        assert response.status_code in [404, 422]  # 422 for validation errors
        
        # Test updating non-existent task
        response = client.put(
            "/api/tasks/999999",  # Non-existent task ID
            headers={"Authorization": "Bearer valid_token"},
            json={"title": "Updated non-existent task"}
        )
        # Should return 404 for non-existent resource
        assert response.status_code in [404, 422]
        
        # Test deleting non-existent task
        response = client.delete(
            "/api/tasks/999999",  # Non-existent task ID
            headers={"Authorization": "Bearer valid_token"}
        )
        # Should return 404 for non-existent resource
        assert response.status_code in [404, 422]
        
        # Test completing non-existent task
        response = client.patch(
            "/api/tasks/999999/complete",  # Non-existent task ID
            headers={"Authorization": "Bearer valid_token"}
        )
        # Should return 404 for non-existent resource
        assert response.status_code in [404, 422]


def test_api_endpoint_responses_structure():
    """Test that all API endpoints return consistent response structures"""
    
    user_id = "response_structure_user"
    
    # Test consistent response structure for POST /api/tasks
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = user_id
        
        response = client.post(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token"},
            json={
                "title": "Response Structure Test",
                "priority": "high"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data  # All successful responses should have data wrapper
        
        task = data["data"]
        required_fields = ["id", "user_id", "title", "description", "completed", "priority", "category", "tags", "created_at", "updated_at"]
        for field in required_fields:
            assert field in task  # All tasks should have required fields
    
    # Test consistent response structure for GET /api/tasks
    task_id = data["data"]["id"]
    
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = user_id
        
        response = client.get(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data  # All successful responses should have data wrapper
        assert isinstance(data["data"], list)  # Collection endpoints should return arrays
        # Check that each task in the list has the correct structure
        for task in data["data"]:
            required_fields = ["id", "user_id", "title", "description", "completed", "priority", "category", "tags", "created_at", "updated_at"]
            for field in required_fields:
                assert field in task  # All tasks should have required fields
    
    # Test consistent response structure for GET /api/tasks/{id}
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = user_id
        
        response = client.get(
            f"/api/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data  # All successful responses should have data wrapper
        
        task = data["data"]
        required_fields = ["id", "user_id", "title", "description", "completed", "priority", "category", "tags", "created_at", "updated_at"]
        for field in required_fields:
            assert field in task  # All tasks should have required fields
    
    # Test consistent response structure for PUT /api/tasks/{id}
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = user_id
        
        response = client.put(
            f"/api/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token"},
            json={"title": "Updated with Consistent Response Structure"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data  # All successful responses should have data wrapper
        
        task = data["data"]
        required_fields = ["id", "user_id", "title", "description", "completed", "priority", "category", "tags", "created_at", "updated_at"]
        for field in required_fields:
            assert field in task  # All tasks should have required fields
    
    # Test consistent response structure for PATCH /api/tasks/{id}/complete
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = user_id
        
        response = client.patch(
            f"/api/tasks/{task_id}/complete",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data  # All successful responses should have data wrapper
        
        task = data["data"]
        required_fields = ["id", "user_id", "title", "description", "completed", "priority", "category", "tags", "created_at", "updated_at"]
        for field in required_fields:
            assert field in task  # All tasks should have required fields
    
    # Test consistent response structure for DELETE /api/tasks/{id}
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = user_id
        
        response = client.delete(
            f"/api/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data  # All successful responses should have data wrapper
        
        result = data["data"]
        assert "ok" in result  # Delete should return ok status
        assert result["ok"] is True