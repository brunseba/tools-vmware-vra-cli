"""Tests for REST API server."""

import pytest
from fastapi.testclient import TestClient
from vmware_vra_cli.app import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_endpoint():
    """Test the health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "healthy"
    assert "version" in data
    assert "uptime" in data


def test_auth_status_endpoint():
    """Test the auth status endpoint."""
    response = client.get("/auth/status")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "message" in data


def test_auth_logout_endpoint():
    """Test the auth logout endpoint."""
    response = client.post("/auth/logout")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_catalog_items_unauthorized():
    """Test catalog items endpoint without authentication."""
    # This should fail because we haven't authenticated
    response = client.get("/catalog/items")
    assert response.status_code == 401


def test_deployments_unauthorized():
    """Test deployments endpoint without authentication."""
    # This should fail because we haven't authenticated
    response = client.get("/deployments")
    assert response.status_code == 401
