"""
Advanced API Tests - Real-world scenarios

LEARNING: These are tests that production teams actually write
"""

import pytest
import json
from fastapi.testclient import TestClient
from agent.main import app

client = TestClient(app)


# ============================================
# Performance Tests
# ============================================

def test_health_check_response_time():
    """
    Health checks must be fast (< 100ms)
    
    REAL-WORLD: Kubernetes restarts pods if health checks timeout
    """
    import time
    
    start = time.time()
    response = client.get("/health")
    duration = (time.time() - start) * 1000  # Convert to ms
    
    assert response.status_code == 200
    assert duration < 100, f"Health check too slow: {duration}ms"


def test_multiple_rapid_requests():
    """
    Test handling burst traffic
    
    REAL-WORLD: What happens during traffic spikes?
    """
    responses = []
    for _ in range(100):
        response = client.get("/health")
        responses.append(response)
    
    # All should succeed
    assert all(r.status_code == 200 for r in responses)


# ============================================
# Security Tests
# ============================================

def test_sql_injection_attempt():
    """
    Test SQL injection protection
    
    REAL-WORLD: Always validate input, never trust users
    """
    malicious_data = {
        "stage": "test'; DROP TABLE users; --",
        "error_message": "' OR '1'='1",
        "logs": "<script>alert('xss')</script>",
        "timestamp": "2024-01-27T12:00:00Z"
    }
    
    response = client.post("/heal", json=malicious_data)
    
    # Should handle gracefully, not crash
    assert response.status_code in [200, 400, 422]


def test_oversized_payload():
    """
    Test protection against huge payloads
    
    REAL-WORLD: Prevent DOS attacks
    """
    huge_logs = "ERROR " * 100000  # 600KB of text
    
    failure_data = {
        "stage": "test",
        "error_message": "Error",
        "logs": huge_logs,
        "timestamp": "2024-01-27T12:00:00Z"
    }
    
    response = client.post("/heal", json=failure_data)
    
    # Should either handle it or reject it, not crash
    assert response.status_code in [200, 413, 422]


def test_unicode_handling():
    """
    Test international character support
    
    REAL-WORLD: Apps are used globally
    """
    failure_data = {
        "stage": "test",
        "error_message": "テストが失敗しました",  # Japanese
        "logs": "Erreur: échec du test",  # French
        "timestamp": "2024-01-27T12:00:00Z",
        "metadata": {
            "user": "用户名",  # Chinese
            "location": "São Paulo"  # Portuguese
        }
    }
    
    response = client.post("/heal", json=failure_data)
    assert response.status_code == 200


# ============================================
# Error Recovery Tests
# ============================================

def test_malformed_json():
    """
    Test handling of malformed requests
    
    REAL-WORLD: Network issues, client bugs, etc.
    """
    response = client.post(
        "/heal",
        data="{ this is not valid json }",
        headers={"Content-Type": "application/json"}
    )
    
    # Should return 422 (Unprocessable Entity)
    assert response.status_code == 422


def test_missing_content_type():
    """
    Test request without Content-Type header
    
    REAL-WORLD: Client configuration errors
    """
    response = client.post(
        "/heal",
        data=json.dumps({
            "stage": "test",
            "error_message": "Error",
            "logs": "Logs",
            "timestamp": "2024-01-27T12:00:00Z"
        })
        # Note: No Content-Type header
    )
    
    # FastAPI should handle this
    assert response.status_code in [200, 422]


# ============================================
# Data Validation Tests
# ============================================

def test_timestamp_validation():
    """
    Test various timestamp formats
    
    REAL-WORLD: Different systems use different formats
    """
    valid_timestamps = [
        "2024-01-27T12:00:00Z",
        "2024-01-27T12:00:00.000Z",
        "2024-01-27T12:00:00+00:00",
    ]
    
    for timestamp in valid_timestamps:
        failure_data = {
            "stage": "test",
            "error_message": "Error",
            "logs": "Logs",
            "timestamp": timestamp
        }
        
        response = client.post("/heal", json=failure_data)
        assert response.status_code == 200, f"Failed for timestamp: {timestamp}"


def test_stage_values():
    """
    Test all expected pipeline stages
    
    REAL-WORLD: Document valid values through tests
    """
    valid_stages = [
        "checkout",
        "build",
        "test",
        "security-scan",
        "sbom",
        "deploy",
        "verify"
    ]
    
    for stage in valid_stages:
        failure_data = {
            "stage": stage,
            "error_message": f"{stage} failed",
            "logs": f"Error in {stage}",
            "timestamp": "2024-01-27T12:00:00Z"
        }
        
        response = client.post("/heal", json=failure_data)
        assert response.status_code == 200, f"Failed for stage: {stage}"


# ============================================
# Response Consistency Tests
# ============================================

def test_response_always_has_timestamp():
    """
    Ensure all responses include timestamp
    
    REAL-WORLD: Debugging requires knowing when things happened
    """
    endpoints = ["/", "/health", "/metrics"]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        data = response.json()
        
        assert "timestamp" in data, f"Missing timestamp in {endpoint}"


def test_confidence_always_valid_range():
    """
    Confidence scores must always be 0-1
    
    REAL-WORLD: Prevents confusion and downstream errors
    """
    for _ in range(10):  # Test multiple times
        failure_data = {
            "stage": "test",
            "error_message": "Error",
            "logs": "Logs",
            "timestamp": "2024-01-27T12:00:00Z"
        }
        
        response = client.post("/heal", json=failure_data)
        result = response.json()
        
        assert 0.0 <= result["confidence"] <= 1.0


# ============================================
# Idempotency Tests
# ============================================

def test_same_request_same_result():
    """
    Same input should give consistent output
    
    REAL-WORLD: Important for retry logic
    """
    failure_data = {
        "stage": "test",
        "error_message": "Specific error",
        "logs": "Specific logs",
        "timestamp": "2024-01-27T12:00:00Z"
    }
    
    # Make same request twice
    response1 = client.post("/heal", json=failure_data)
    response2 = client.post("/heal", json=failure_data)
    
    result1 = response1.json()
    result2 = response2.json()
    
    # Core fields should be consistent
    assert result1["success"] == result2["success"]
    assert result1["confidence"] == result2["confidence"]


# ============================================
# Documentation Tests
# ============================================

def test_openapi_schema_available():
    """
    Test that API documentation is accessible
    
    REAL-WORLD: Auto-generated docs are crucial for teams
    """
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    schema = response.json()
    assert "openapi" in schema
    assert "paths" in schema
    assert "/heal" in schema["paths"]


def test_docs_page_available():
    """
    Test Swagger UI is accessible
    
    REAL-WORLD: Interactive docs help developers
    """
    response = client.get("/docs")
    assert response.status_code == 200
    assert b"swagger" in response.content.lower()


# ============================================
# Regression Tests
# ============================================

def test_empty_metadata_doesnt_crash():
    """
    REGRESSION TEST: Previously crashed with empty metadata
    
    REAL-WORLD: Every bug gets a test to prevent it returning
    """
    failure_data = {
        "stage": "test",
        "error_message": "Error",
        "logs": "Logs",
        "timestamp": "2024-01-27T12:00:00Z",
        "metadata": {}  # Empty dict
    }
    
    response = client.post("/heal", json=failure_data)
    assert response.status_code == 200


def test_null_metadata_handled():
    """
    REGRESSION TEST: Null metadata should work
    
    REAL-WORLD: Different clients send different values
    """
    failure_data = {
        "stage": "test",
        "error_message": "Error",
        "logs": "Logs",
        "timestamp": "2024-01-27T12:00:00Z",
        "metadata": None
    }
    
    response = client.post("/heal", json=failure_data)
    assert response.status_code == 200