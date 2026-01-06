"""
Edge Cases and Stress Tests

The weird stuff that happens in production
"""

import pytest
from fastapi.testclient import TestClient
from agent.main import app

client = TestClient(app)


# ============================================
# Boundary Value Tests
# ============================================

def test_minimum_valid_input():
    """
    Test with absolute minimum data
    
    REAL-WORLD: What's the smallest valid request?
    """
    failure_data = {
        "stage": "a",  # Single character
        "error_message": "x",
        "logs": "y",
        "timestamp": "2024-01-27T12:00:00Z"
    }
    
    response = client.post("/heal", json=failure_data)
    assert response.status_code == 200


def test_maximum_reasonable_input():
    """
    Test with large but reasonable data
    
    REAL-WORLD: Stack traces can be huge
    """
    failure_data = {
        "stage": "test",
        "error_message": "Error: " + ("x" * 1000),
        "logs": "Stack trace:\n" + ("Line\n" * 5000),  # 5000 line stack trace
        "timestamp": "2024-01-27T12:00:00Z"
    }
    
    response = client.post("/heal", json=failure_data)
    assert response.status_code == 200


def test_all_whitespace_input():
    """
    Test with whitespace-only strings
    
    REAL-WORLD: Parsing errors, empty responses, etc.
    """
    failure_data = {
        "stage": "   ",
        "error_message": "\n\n\n",
        "logs": "\t\t\t",
        "timestamp": "2024-01-27T12:00:00Z"
    }
    
    response = client.post("/heal", json=failure_data)
    assert response.status_code == 200


# ============================================
# Concurrent Request Tests
# ============================================

import pytest
import asyncio
from httpx import AsyncClient
from agent.main import app

@pytest.mark.asyncio
async def test_concurrent_different_stages():
    stages = ["build", "test", "deploy", "security-scan"]
    async with AsyncClient(app=app, base_url="http://test") as ac:
        async def make_request(stage):
            failure_data = {
                "stage": stage,
                "error_message": f"{stage} failed",
                "logs": f"Error in {stage}",
                "timestamp": "2024-01-27T12:00:00Z"
            }
            response = await ac.post("/heal", json=failure_data)
            return response
        responses = await asyncio.gather(*[make_request(stage) for stage in stages])
        for response in responses:
            assert response.status_code == 200


# ============================================
# Fault Injection Tests
# ============================================

def test_invalid_http_method():
    """
    Test wrong HTTP method
    
    REAL-WORLD: Client misconfiguration
    """
    # Try GET on POST-only endpoint
    response = client.get("/heal")
    assert response.status_code == 405  # Method Not Allowed


def test_nonexistent_endpoint():
    """
    Test 404 handling
    
    REAL-WORLD: Typos, wrong URLs
    """
    response = client.get("/nonexistent")
    assert response.status_code == 404


def test_double_slash_in_path():
    """
    Test path normalization
    
    REAL-WORLD: URL construction bugs
    """
    response = client.get("//health")
    # Should either work or return 404, not crash
    assert response.status_code in [200, 404]


# ============================================
# Data Type Confusion Tests
# ============================================

def test_integer_as_string_stage():
    """
    Test type coercion
    
    REAL-WORLD: JSON parsing differences
    """
    failure_data = {
        "stage": "123",  # String that looks like number
        "error_message": "Error",
        "logs": "Logs",
        "timestamp": "2024-01-27T12:00:00Z"
    }
    
    response = client.post("/heal", json=failure_data)
    assert response.status_code == 200


def test_boolean_in_string_field():
    """
    Test unexpected types
    
    REAL-WORLD: Different languages handle types differently
    """
    failure_data = {
        "stage": "test",
        "error_message": "Error",
        "logs": "Logs",
        "timestamp": "2024-01-27T12:00:00Z",
        "metadata": {
            "success": "true"  # String "true", not boolean
        }
    }
    
    response = client.post("/heal", json=failure_data)
    assert response.status_code == 200


# ============================================
# Real Pipeline Failure Examples
# ============================================

def test_npm_install_failure():
    """
    Simulate real npm install failure
    
    REAL-WORLD: Actual error you'd see
    """
    failure_data = {
        "stage": "build",
        "error_message": "npm ERR! code ERESOLVE",
        "logs": """
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
npm ERR! Found: react@18.0.0
npm ERR! Could not resolve dependency:
npm ERR! peer react@"^17.0.0" from react-dom@17.0.2
        """,
        "timestamp": "2024-01-27T12:00:00Z",
        "metadata": {
            "package": "react",
            "version_conflict": "18.0.0 vs 17.0.0"
        }
    }
    
    response = client.post("/heal", json=failure_data)
    assert response.status_code == 200


def test_docker_build_failure():
    """
    Simulate Docker build failure
    
    REAL-WORLD: Common CI/CD error
    """
    failure_data = {
        "stage": "build",
        "error_message": "ERROR: failed to solve: python:3.9: not found",
        "logs": """
#4 [1/4] FROM docker.io/library/python:3.9
#4 ERROR: failed to solve: python:3.9: not found
------
 > [1/4] FROM docker.io/library/python:3.9:
------
ERROR: failed to solve: python:3.9: not found
        """,
        "timestamp": "2024-01-27T12:00:00Z"
    }
    
    response = client.post("/heal", json=failure_data)
    assert response.status_code == 200


def test_kubernetes_deployment_failure():
    """
    Simulate K8s deployment failure
    
    REAL-WORLD: Resource constraints
    """
    failure_data = {
        "stage": "deploy",
        "error_message": "Error from server (Forbidden): pods is forbidden",
        "logs": """
Error from server (Forbidden): pods is forbidden: 
User "system:serviceaccount:default:deployer" cannot list resource 
"pods" in API group "" in the namespace "production"
        """,
        "timestamp": "2024-01-27T12:00:00Z",
        "metadata": {
            "namespace": "production",
            "resource": "pods"
        }
    }
    
    response = client.post("/heal", json=failure_data)
    assert response.status_code == 200