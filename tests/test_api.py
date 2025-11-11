"""
Integration tests for the FastAPI application
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from insecurity_refactoring_py.api import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_endpoint_with_connection(client):
    """Test health endpoint with successful connection"""
    with patch('insecurity_refactoring_py.api.Neo4jDB') as mock_db_class:
        mock_db = Mock()
        mock_db.connect.return_value = True
        mock_db_class.return_value = mock_db
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["neo4j_connected"] is True


def test_health_endpoint_without_connection(client):
    """Test health endpoint with failed connection"""
    with patch('insecurity_refactoring_py.api.Neo4jDB') as mock_db_class:
        mock_db = Mock()
        mock_db.connect.return_value = False
        mock_db_class.return_value = mock_db
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["neo4j_connected"] is False


def test_list_patterns_empty(client):
    """Test listing patterns when folder doesn't exist"""
    response = client.get("/patterns")
    assert response.status_code == 200
    # Should return empty list if folder doesn't exist
    assert isinstance(response.json(), list)
