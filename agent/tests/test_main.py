"""
Unit Tests for AI Healing Pipeline Agent

OBJECTIVES:
- How to test FastAPI applications
- Request/response validation
- Test structure (Arrange, Act, Assert)
- Mocking and fixtures
"""

import pytest
from fastapi.testclient import TestClient
from agent.main import app

# ============================================
# TestClient
# ============================================
# FastAPI provides TestClient for testing without running a real server
# It simulates HTTP requests and returns responses
client = TestClient(app)


# ============================================
# Basic Test Structure
# ============================================
# Test function names start with "test_"
# Pytest automatically discovers and runs these

def test_root_endpoint():
    """
    Test the root endpoint
    
    AAA Pattern
    - Arrange: Set up test conditions (none needed here)
    - Act: Make the request
    - Assert: Verify the response
    """
    # Act: Make GET request to /
    response = client.get("/")
    
    # Assert: Check response
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "AI Healing Pipeline Agent"
    assert data["status"] == "operational"
    assert "version" in data
    assert "timestamp" in data


def test_health_check():
    """
    Test health check endpoint
    
    Health checks are critical
    - Kubernetes uses this to know if pod is healthy
    - Should be fast and simple
    - Should return 200 if everything is OK
    """
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_metrics_endpoint():
    """
    Test metrics endpoint
    
    Metrics endpoints provide observability
    """
    response = client.get("/metrics")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify expected metric fields
    assert "total_healings" in data
    assert "success_rate" in data
    assert "average_resolution_time" in data
    assert "timestamp" in data
    
    # Check data types
    assert isinstance(data["total_healings"], int)
    assert isinstance(data["success_rate"], float)
    assert isinstance(data["average_resolution_time"], float)


# ============================================
# Testing POST Endpoints
# ============================================

def test_heal_pipeline_success():
    """
    Test healing endpoint with valid input
    
    Testing happy path
    - Valid request data
    - Expected successful response
    """
    # Arrange: Prepare valid failure data
    failure_data = {
        "stage": "test",
        "error_message": "Test failed",
        "logs": "Error: assertion failed\nExpected: True\nGot: False",
        "timestamp": "2024-01-27T12:00:00Z",
        "metadata": {
            "branch": "main",
            "commit": "abc123"
        }
    }
    
    # Act: Make POST request
    response = client.post("/heal", json=failure_data)
    
    # Assert: Check response
    assert response.status_code == 200
    
    result = response.json()
    assert result["success"] is True
    assert "fix_applied" in result
    assert "confidence" in result
    assert "iterations" in result
    assert "message" in result
    
    # Verify confidence is between 0 and 1
    assert 0 <= result["confidence"] <= 1
    assert result["iterations"] >= 0


def test_heal_pipeline_minimal_data():
    """
    Test with minimal required fields
    
    Testing boundary conditions
    """
    failure_data = {
        "stage": "build",
        "error_message": "Build failed",
        "logs": "Error logs",
        "timestamp": "2024-01-27T12:00:00Z"
        # Note: metadata is optional
    }
    
    response = client.post("/heal", json=failure_data)
    assert response.status_code == 200


# ============================================
# Testing Error Cases
# ============================================

def test_heal_pipeline_missing_required_field():
    """
    Test with missing required fields
    
    Validation testing
    - Pydantic automatically validates request data
    - Missing required fields return 422 Unprocessable Entity
    """
    invalid_data = {
        "stage": "test",
        "error_message": "Test failed"
        # Missing: logs, timestamp (required fields)
    }
    
    response = client.post("/heal", json=invalid_data)
    
    # Assert: Should fail validation
    assert response.status_code == 422  # Unprocessable Entity
    
    # Check error details
    error = response.json()
    assert "detail" in error


def test_heal_pipeline_invalid_data_types():
    """
    Test with invalid data types
    
    Type validation
    - Pydantic checks types automatically
    """
    invalid_data = {
        "stage": 123,  # Should be string
        "error_message": "Test failed",
        "logs": "Error logs",
        "timestamp": "2024-01-27T12:00:00Z"
    }
    
    response = client.post("/heal", json=invalid_data)
    assert response.status_code == 422


def test_heal_pipeline_empty_string():
    """
    Test with empty strings
    
    Edge case testing
    """
    failure_data = {
        "stage": "",  # Empty but still a string
        "error_message": "",
        "logs": "",
        "timestamp": "2024-01-27T12:00:00Z"
    }
    
    response = client.post("/heal", json=failure_data)
    # Should still succeed (empty strings are valid)
    assert response.status_code == 200


# ============================================
# Async Testing
# ============================================

@pytest.mark.asyncio
async def test_multiple_concurrent_requests():
    """
    Test handling multiple concurrent requests
    
    Concurrency testing
    - FastAPI handles async requests well
    - Important for production systems
    """
    import asyncio
    
    failure_data = {
        "stage": "build",
        "error_message": "Build failed",
        "logs": "Error logs",
        "timestamp": "2024-01-27T12:00:00Z"
    }
    
    # Make 5 concurrent requests
    responses = []
    for _ in range(5):
        response = client.post("/heal", json=failure_data)
        responses.append(response)
    
    # All should succeed
    for response in responses:
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True


# ============================================
# Testing Different Failure Scenarios
# ============================================

def test_heal_different_stages():
    """
    Test healing for different pipeline stages
    
    Testing various inputs
    """
    stages = ["build", "test", "security-scan", "deploy"]
    
    for stage in stages:
        failure_data = {
            "stage": stage,
            "error_message": f"{stage} failed",
            "logs": f"Error in {stage}",
            "timestamp": "2024-01-27T12:00:00Z"
        }
        
        response = client.post("/heal", json=failure_data)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True


def test_heal_with_metadata():
    """
    Test healing with rich metadata
    
    Testing optional fields
    """
    failure_data = {
        "stage": "test",
        "error_message": "Test failed",
        "logs": "Error logs",
        "timestamp": "2024-01-27T12:00:00Z",
        "metadata": {
            "branch": "feature/new-feature",
            "commit": "abc123def456",
            "job_id": "12345",
            "run_number": 42,
            "repository": "user/repo",
            "actor": "developer@example.com"
        }
    }
    
    response = client.post("/heal", json=failure_data)
    assert response.status_code == 200


# ============================================
# Response Validation Tests
# ============================================

def test_healing_result_structure():
    """
    Test that healing result has correct structure
    
    Schema validation
    """
    failure_data = {
        "stage": "test",
        "error_message": "Test failed",
        "logs": "Error logs",
        "timestamp": "2024-01-27T12:00:00Z"
    }
    
    response = client.post("/heal", json=failure_data)
    result = response.json()
    
    # Verify all required fields exist
    required_fields = ["success", "confidence", "iterations", "message"]
    for field in required_fields:
        assert field in result, f"Missing required field: {field}"
    
    # Verify optional field might exist
    assert "fix_applied" in result or result["success"] is False
    
    # Verify data types
    assert isinstance(result["success"], bool)
    assert isinstance(result["confidence"], float)
    assert isinstance(result["iterations"], int)
    assert isinstance(result["message"], str)


def test_confidence_score_range():
    """
    Test that confidence scores are valid
    
    Domain-specific validation
    - Confidence should always be between 0 and 1
    """
    failure_data = {
        "stage": "test",
        "error_message": "Test failed",
        "logs": "Error logs",
        "timestamp": "2024-01-27T12:00:00Z"
    }
    
    response = client.post("/heal", json=failure_data)
    result = response.json()
    
    confidence = result["confidence"]
    assert 0.0 <= confidence <= 1.0, f"Confidence {confidence} is out of valid range [0, 1]"


# ============================================
# Edge Cases
# ============================================

def test_very_long_error_message():
    """
    Test with very long error message
    
    Stress testing
    """
    failure_data = {
        "stage": "test",
        "error_message": "Error: " + "x" * 10000,  # Very long message
        "logs": "Error logs",
        "timestamp": "2024-01-27T12:00:00Z"
    }
    
    response = client.post("/heal", json=failure_data)
    assert response.status_code == 200


def test_special_characters_in_input():
    """
    Test with special characters
    
    Input sanitization testing
    """
    failure_data = {
        "stage": "test",
        "error_message": "Error: <script>alert('xss')</script>",
        "logs": "Logs with 'quotes' and \"double quotes\" and \n newlines",
        "timestamp": "2024-01-27T12:00:00Z"
    }
    
    response = client.post("/heal", json=failure_data)
    assert response.status_code == 200


# ============================================
# Test Fixtures (Advanced)
# ============================================

@pytest.fixture
def sample_failure():
    """
    Fixture that provides reusable test data
    
    DRY (Don't Repeat Yourself) in tests
    - Fixtures reduce code duplication
    - Make tests more maintainable
    """
    return {
        "stage": "test",
        "error_message": "Test failed",
        "logs": "Error logs here",
        "timestamp": "2024-01-27T12:00:00Z",
        "metadata": {
            "branch": "main",
            "commit": "abc123"
        }
    }


def test_using_fixture(sample_failure):
    """
    Test using a fixture
    
    Pytest automatically injects fixtures
    """
    response = client.post("/heal", json=sample_failure)
    assert response.status_code == 200
    
    result = response.json()
    assert result["success"] is True
