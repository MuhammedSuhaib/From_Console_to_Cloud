import pytest
from unittest.mock import patch, MagicMock
from auth.jwt import get_current_user_id
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends
from sqlmodel import Session
from datetime import datetime, timezone, timedelta
import sqlalchemy


def test_get_current_user_id_valid_token():
    """Test that a valid token returns the correct user ID"""
    from unittest.mock import Mock

    # Create a mock credentials object
    mock_creds = MagicMock()
    mock_creds.credentials = "valid_session_token"

    # Mock the database session
    mock_db_session = MagicMock()

    # Create a mock result that behaves like a SQLAlchemy result tuple
    mock_result = ("test_user_123", datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1))
    mock_db_session.execute.return_value.fetchone.return_value = mock_result

    # Test the function
    user_id = get_current_user_id(mock_creds, mock_db_session)

    assert user_id == "test_user_123"


def test_get_current_user_id_invalid_token():
    """Test that an invalid token raises HTTPException"""
    # Create a mock credentials object
    mock_creds = MagicMock()
    mock_creds.credentials = "invalid_token"

    # Mock the database session
    mock_db_session = MagicMock()
    mock_db_session.execute.return_value.fetchone.return_value = None  # No result found

    # Test that HTTPException is raised
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(mock_creds, mock_db_session)

    assert exc_info.value.status_code == 401
    assert "Invalid session" in exc_info.value.detail


def test_get_current_user_id_expired_token():
    """Test that an expired token raises HTTPException"""
    from datetime import timedelta

    # Create a mock credentials object
    mock_creds = MagicMock()
    mock_creds.credentials = "expired_token"

    # Mock the database session
    mock_db_session = MagicMock()

    # Mock the query result with an expired session (tuple format)
    mock_result = ("test_user_123", datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=1))  # Expired
    mock_db_session.execute.return_value.fetchone.return_value = mock_result

    # Test that HTTPException is raised
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(mock_creds, mock_db_session)

    assert exc_info.value.status_code == 401


def test_get_current_user_id_exception_handling():
    """Test that exceptions are handled properly"""
    # Create a mock credentials object
    mock_creds = MagicMock()
    mock_creds.credentials = "any_token"

    # Mock the database session to throw an exception
    mock_db_session = MagicMock()
    mock_db_session.execute.side_effect = Exception("Database error")

    # Test that HTTPException is raised
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(mock_creds, mock_db_session)

    assert exc_info.value.status_code == 401
    assert "Internal authentication failure" in exc_info.value.detail