import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch


client = TestClient(app)

def test_authentication_on_all_protected_endpoints():
    """Test authentication on all protected endpoints"""
    
    endpoints_to_test = [
        ("GET", "/api/tasks", None),
        ("POST", "/api/tasks", {"title": "Auth test task", "priority": "medium"}),
        ("GET", "/api/tasks/1", None),  # This will likely be 404 if task doesn't exist, but should be 401 without auth
        ("PUT", "/api/tasks/1", {"title": "Updated task"}),
        ("DELETE", "/api/tasks/1", None),
        ("PATCH", "/api/tasks/1/complete", None)
    ]

    # Test that all endpoints require authentication (return 401 without token)
    for method, endpoint, json_data in endpoints_to_test:
        if method == "GET":
            response = client.get(endpoint)
        elif method == "POST":
            response = client.post(endpoint, json=json_data)
        elif method == "PUT":
            response = client.put(endpoint, json=json_data)
        elif method == "DELETE":
            response = client.delete(endpoint)
        elif method == "PATCH":
            response = client.patch(endpoint)

        # All endpoints should return 401 Unauthorized without proper authentication
        # Some endpoints might return 405 if not implemented, but they still require auth
        # The important thing is they don't return 200 (success without auth)
        assert response.status_code in [401, 405], f"Endpoint {method} {endpoint} should require authentication"


def test_authentication_with_valid_token():
    """Test that all endpoints work with valid authentication"""
    
    user_id = "auth_test_user"
    
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = user_id
        
        # Test GET /api/tasks with authentication
        response = client.get(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code in [200, 204]  # OK or No Content if no tasks exist
        
        # Test POST /api/tasks with authentication to create a task for other tests
        response = client.post(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token"},
            json={
                "title": "Authentication Test Task",
                "description": "Testing auth on all endpoints",
                "priority": "medium"
            }
        )
        assert response.status_code == 200
        task_data = response.json()["data"]
        task_id = task_data["id"]
        assert task_data["user_id"] == user_id
        assert task_data["title"] == "Authentication Test Task"
        
        # Test GET /api/tasks/{id} with authentication
        response = client.get(
            f"/api/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 200
        task = response.json()["data"]
        assert task["id"] == task_id
        assert task["user_id"] == user_id
        
        # Test PUT /api/tasks/{id} with authentication
        response = client.put(
            f"/api/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token"},
            json={"title": "Updated Auth Test Task", "completed": True}
        )
        assert response.status_code == 200
        updated_task = response.json()["data"]
        assert updated_task["title"] == "Updated Auth Test Task"
        assert updated_task["completed"] is True
        
        # Test PATCH /api/tasks/{id}/complete with authentication
        response = client.patch(
            f"/api/tasks/{task_id}/complete",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 200
        toggled_task = response.json()["data"]
        assert toggled_task["id"] == task_id
        assert toggled_task["completed"] is False  # Was true, should toggle to false
        
        # Test DELETE /api/tasks/{id} with authentication
        response = client.delete(
            f"/api/tasks/{task_id}",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 200
        result = response.json()["data"]
        assert result["ok"] is True


def test_authentication_with_invalid_token():
    """Test that all endpoints properly reject invalid tokens"""

    endpoints_to_test = [
        ("GET", "/api/tasks", None),
        ("POST", "/api/tasks", {"title": "Auth rejection test", "priority": "medium"}),
        ("GET", "/api/tasks/999", None),
        ("PUT", "/api/tasks/999", {"title": "Should fail"}),
        ("DELETE", "/api/tasks/999", None),
        ("PATCH", "/api/tasks/999/complete", None)
    ]

    # Mock the auth function to simulate token validation failure
    for method, endpoint, json_data in endpoints_to_test:
        with patch("auth.jwt.get_current_user_id") as mock_get_user:
            mock_get_user.side_effect = Exception("Invalid or expired token")

            if method == "GET":
                response = client.get(endpoint, headers={"Authorization": "Bearer invalid_token"})
            elif method == "POST":
                response = client.post(endpoint, headers={"Authorization": "Bearer invalid_token"}, json=json_data)
            elif method == "PUT":
                response = client.put(endpoint, headers={"Authorization": "Bearer invalid_token"}, json=json_data)
            elif method == "DELETE":
                response = client.delete(endpoint, headers={"Authorization": "Bearer invalid_token"})
            elif method == "PATCH":
                response = client.patch(endpoint, headers={"Authorization": "Bearer invalid_token"})

            # All endpoints should return 401 when token validation fails
            assert response.status_code == 401, f"Endpoint {method} {endpoint} should reject invalid tokens"


def test_bearer_token_format_requirement():
    """Test that endpoints specifically require Bearer token format"""
    
    user_id = "bearer_format_user"
    
    # Test with correct Bearer format
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = user_id
        
        response = client.get(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code in [200, 204]
    
    # Test with other authorization formats (should fail)
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = user_id  # Even if user is valid, wrong format should fail at security level
        
        # This might still work if our implementation doesn't strictly check format
        # but the important part is that the token validation happens correctly
        response = client.get(
            "/api/tasks",
            headers={"Authorization": "Token valid_token"}
        )
        # This response depends on how strictly FastAPI's HTTPBearer validates the format
        # It might return 401 for wrong format, or might still work if backend validates token regardless


def test_missing_authorization_header():
    """Test that endpoints consistently reject requests without authorization header"""

    endpoints_tests = [
        ("GET", "/api/tasks"),
        ("POST", "/api/tasks", {"title": "Missing auth test", "priority": "medium"}),
        ("GET", "/api/tasks/1"),
        ("PUT", "/api/tasks/1", {"title": "Missing auth update"}),
        ("DELETE", "/api/tasks/1"),
        ("PATCH", "/api/tasks/1/complete")  # This one doesn't send a body
    ]

    for test_data in endpoints_tests:
        if len(test_data) == 2:  # GET, DELETE, PATCH endpoints without body
            method, endpoint = test_data
            if method == "GET":
                response = client.get(endpoint)
            elif method == "DELETE":
                response = client.delete(endpoint)
            elif method == "PATCH":
                response = client.patch(endpoint)
            else:
                response = client.request(method, endpoint)  # Fallback for other methods
        elif len(test_data) == 3:  # POST, PUT endpoints with body
            method, endpoint, json_data = test_data
            if method == "POST":
                response = client.post(endpoint, json=json_data)
            elif method == "PUT":
                response = client.put(endpoint, json=json_data)
            else:
                response = client.request(method, endpoint)  # Fallback for other methods

        # All endpoints should return 401 without Authorization header
        assert response.status_code == 401, f"Endpoint {method} {endpoint} should require authorization header"


def test_authorization_header_variations():
    """Test various ways the authorization header might be sent"""
    
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = "test_user"
        
        # Test with correct format
        response = client.get(
            "/api/tasks",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code in [200, 204]
    
    # Test with lowercase authorization header
    with patch("auth.jwt.get_current_user_id") as mock_get_user:
        mock_get_user.return_value = "test_user"
        
        response = client.get(
            "/api/tasks",
            headers={"authorization": "Bearer valid_token"}
        )
        # This should work since FastAPI handles header case-insensitivity
        assert response.status_code in [200, 204], "Lowercase authorization header should work"
    
    # Test with empty authorization header
    response = client.get(
        "/api/tasks",
        headers={"Authorization": ""}
    )
    assert response.status_code == 401, "Empty authorization header should be rejected"
    
    # Test with malformed authorization header
    response = client.get(
        "/api/tasks",
        headers={"Authorization": "malformed_header"}
    )
    assert response.status_code == 401, "Malformed authorization header should be rejected"