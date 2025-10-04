"""Basic unit tests for health API router using shared test_client fixture."""

import time
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from ace_python.data_access.db.service import get_db as real_get_db


def test_health_check_basic(test_client) -> None:
    """Test basic health check endpoint."""
    r = test_client.get("/api/v1/health/")

    assert r.status_code == 200
    data = r.json()

    # Check required fields
    assert "status" in data
    assert "timestamp" in data
    assert "service" in data
    assert "version" in data

    # Check values
    assert data["status"] == "ok"
    assert data["service"] == "ace-api"
    assert data["version"] == "1.0.0"

    # Check timestamp format (ISO format)
    try:
        datetime.fromisoformat(data["timestamp"])
    except ValueError:
        pytest.fail("Timestamp is not in valid ISO format")


def test_health_check_db_success(test_client) -> None:
    """Test database health check endpoint with successful connection."""
    r = test_client.get("/api/v1/health/db")

    assert r.status_code == 200
    data = r.json()

    # Check required fields
    assert "status" in data
    assert "database" in data
    assert "response_time_ms" in data
    assert "timestamp" in data

    # Check values
    assert data["status"] == "ok"
    assert data["database"] == "postgresql"
    assert isinstance(data["response_time_ms"], int | float)
    assert data["response_time_ms"] >= 0

    # Check timestamp format
    try:
        datetime.fromisoformat(data["timestamp"])
    except ValueError:
        pytest.fail("Timestamp is not in valid ISO format")


def test_health_check_db_failure(test_client) -> None:
    """Test database health check endpoint with database failure."""
    # Create a mock session that raises an exception when execute is called
    mock_session = MagicMock()
    mock_session.execute.side_effect = Exception("Database connection failed")

    def mock_get_db():
        yield mock_session

    # Temporarily override the dependency
    test_client.app.dependency_overrides[real_get_db] = mock_get_db

    try:
        r = test_client.get("/api/v1/health/db")

        assert r.status_code == 503
        data = r.json()
        assert "detail" in data
        assert "Database health check failed" in data["detail"]
    finally:
        # Clean up the override
        if real_get_db in test_client.app.dependency_overrides:
            del test_client.app.dependency_overrides[real_get_db]


def test_health_check_system_success(test_client) -> None:
    """Test system health check endpoint with successful system info retrieval."""
    r = test_client.get("/api/v1/health/system")

    assert r.status_code == 200
    data = r.json()

    # Check required fields
    assert "status" in data
    assert "system" in data
    assert "timestamp" in data

    # Check system info structure
    system_info = data["system"]
    assert "platform" in system_info
    assert "platform_version" in system_info
    assert "cpu_usage_percent" in system_info
    assert "memory_usage_percent" in system_info
    assert "disk_usage_percent" in system_info
    assert "python_version" in system_info

    # Check values
    assert data["status"] == "ok"
    assert isinstance(system_info["cpu_usage_percent"], int | float)
    assert isinstance(system_info["memory_usage_percent"], int | float)
    assert isinstance(system_info["disk_usage_percent"], int | float)
    assert 0 <= system_info["cpu_usage_percent"] <= 100
    assert 0 <= system_info["memory_usage_percent"] <= 100
    assert 0 <= system_info["disk_usage_percent"] <= 100

    # Check timestamp format
    try:
        datetime.fromisoformat(data["timestamp"])
    except ValueError:
        pytest.fail("Timestamp is not in valid ISO format")


def test_health_check_system_failure(test_client) -> None:
    """Test system health check endpoint with system info failure."""
    with patch("ace_python.entrypoints.web.api.v1.routers.health.psutil.cpu_percent") as mock_cpu:
        mock_cpu.side_effect = Exception("System info retrieval failed")

        r = test_client.get("/api/v1/health/system")

        assert r.status_code == 503
        data = r.json()
        assert "detail" in data
        assert "System health check failed" in data["detail"]


def test_health_check_ping(test_client) -> None:
    """Test simple ping endpoint."""
    r = test_client.get("/api/v1/health/ping")

    assert r.status_code == 200
    data = r.json()

    # Check response structure
    assert "ping" in data
    assert data["ping"] == "pong"


def test_health_endpoints_consistency(test_client) -> None:
    """Test that all health endpoints return consistent timestamp formats."""
    endpoints = [
        "/api/v1/health/",
        "/api/v1/health/db",
        "/api/v1/health/system",
    ]

    for endpoint in endpoints:
        r = test_client.get(endpoint)
        assert r.status_code == 200
        data = r.json()

        # All health endpoints should have timestamp
        assert "timestamp" in data

        # Timestamp should be valid ISO format
        try:
            datetime.fromisoformat(data["timestamp"])
        except ValueError:
            pytest.fail(f"Endpoint {endpoint} has invalid timestamp format")


def test_health_endpoints_response_times(test_client) -> None:
    """Test that health endpoints respond within reasonable time."""
    endpoints = [
        "/api/v1/health/",
        "/api/v1/health/db",
        "/api/v1/health/system",
        "/api/v1/health/ping",
    ]

    for endpoint in endpoints:
        start_time = time.time()
        r = test_client.get(endpoint)
        response_time = time.time() - start_time

        assert r.status_code == 200
        # Health endpoints should respond quickly (within 5 seconds)
        assert response_time < 5.0, f"Endpoint {endpoint} took too long: {response_time:.2f}s"


def test_health_check_db_response_time_accuracy(test_client) -> None:
    """Test that database health check reports accurate response time."""
    r = test_client.get("/api/v1/health/db")

    assert r.status_code == 200
    data = r.json()

    # Response time should be reasonable for a simple SELECT 1 query
    response_time_ms = data["response_time_ms"]
    assert response_time_ms >= 0
    assert response_time_ms < 1000  # Should be less than 1 second for simple query


def test_health_check_system_platform_info(test_client) -> None:
    """Test that system health check provides valid platform information."""
    r = test_client.get("/api/v1/health/system")

    assert r.status_code == 200
    data = r.json()
    system_info = data["system"]

    # Platform should be a non-empty string
    assert isinstance(system_info["platform"], str)
    assert len(system_info["platform"]) > 0

    # Platform version should be a non-empty string
    assert isinstance(system_info["platform_version"], str)
    assert len(system_info["platform_version"]) > 0

    # Python version should be a valid version string
    assert isinstance(system_info["python_version"], str)
    assert len(system_info["python_version"]) > 0
    # Python version should contain dots (e.g., "3.10.0")
    assert "." in system_info["python_version"]


def test_health_endpoints_http_methods(test_client) -> None:
    """Test that health endpoints only accept GET requests."""
    endpoints = [
        "/api/v1/health/",
        "/api/v1/health/db",
        "/api/v1/health/system",
        "/api/v1/health/ping",
    ]

    for endpoint in endpoints:
        # GET should work
        r = test_client.get(endpoint)
        assert r.status_code == 200

        # POST should not be allowed
        r = test_client.post(endpoint)
        assert r.status_code == 405  # Method Not Allowed

        # PUT should not be allowed
        r = test_client.put(endpoint)
        assert r.status_code == 405  # Method Not Allowed

        # DELETE should not be allowed
        r = test_client.delete(endpoint)
        assert r.status_code == 405  # Method Not Allowed
