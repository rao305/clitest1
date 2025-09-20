#!/usr/bin/env python3
"""
Test Configuration and Fixtures
Comprehensive test setup for API testing with TDD approach
"""

import pytest
import asyncio
import os
import sys
import tempfile
import json
from typing import Dict, Any, Generator
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from api.main import app
from api.auth import get_current_user
from api.database import get_db_connection


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_Gemini():
    """Mock Gemini client for testing"""
    with patch('Gemini.Gemini') as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        # Mock chat completion response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.text = "Mock AI response for testing"
        mock_response.usage.total_tokens = 100
        
        mock_instance.chat.completions.create.return_value = mock_response
        yield mock_instance


@pytest.fixture
def test_db():
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    # Initialize test database
    import sqlite3
    conn = sqlite3.connect(db_path)
    
    # Create sessions table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            student_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            context_data TEXT,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Create conversation_history table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_query TEXT,
            ai_response TEXT,
            intent TEXT,
            confidence REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    os.unlink(db_path)


@pytest.fixture
def test_knowledge_base():
    """Create test knowledge base"""
    knowledge_data = {
        "courses": {
            "CS 18000": {
                "title": "Problem Solving And Object-Oriented Programming",
                "credits": 4,
                "description": "Problem solving and algorithms development using an object oriented programming language.",
                "prerequisites": [],
                "corequisites": [],
                "semesters_offered": ["Fall", "Spring", "Summer"],
                "difficulty_rating": 3.2,
                "typical_enrollment": 800
            },
            "CS 18200": {
                "title": "Foundations Of Computer Science",
                "credits": 3,
                "description": "Introduction to computational thinking and discrete mathematics.",
                "prerequisites": ["CS 18000"],
                "corequisites": [],
                "semesters_offered": ["Fall", "Spring"],
                "difficulty_rating": 3.8,
                "typical_enrollment": 600
            },
            "CS 25100": {
                "title": "Data Structures And Algorithms",
                "credits": 3,
                "description": "Introduction to data structures and algorithms.",
                "prerequisites": ["CS 18000", "CS 18200"],
                "corequisites": ["MA 26100"],
                "semesters_offered": ["Fall", "Spring"],
                "difficulty_rating": 4.2,
                "typical_enrollment": 500
            }
        },
        "tracks": {
            "Machine Intelligence": {
                "description": "Focus on AI, machine learning, and data science",
                "required_courses": ["CS 37300", "CS 47300", "CS 57300"],
                "elective_courses": ["CS 47100", "CS 57100", "STAT 51100"],
                "total_credits": 12,
                "career_paths": ["Data Scientist", "ML Engineer", "AI Researcher"]
            },
            "Software Engineering": {
                "description": "Focus on large-scale software development",
                "required_courses": ["CS 35200", "CS 40800", "CS 42600"],
                "elective_courses": ["CS 35300", "CS 30700", "CS 45200"],
                "total_credits": 12,
                "career_paths": ["Software Engineer", "DevOps Engineer", "Tech Lead"]
            }
        },
        "graduation_requirements": {
            "total_credits": 120,
            "cs_core_credits": 29,
            "track_credits": 12,
            "general_education_credits": 30,
            "free_electives": 49
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        json.dump(knowledge_data, tmp_file, indent=2)
        knowledge_file = tmp_file.name
    
    yield knowledge_file, knowledge_data
    
    # Cleanup
    os.unlink(knowledge_file)


@pytest.fixture
def mock_db_dependency(test_db):
    """Override database dependency for testing"""
    def get_test_db():
        import sqlite3
        return sqlite3.connect(test_db)
    
    return get_test_db


@pytest.fixture
def mock_auth_dependency():
    """Override auth dependency for testing"""
    def get_test_user():
        return {
            "user_id": "test_user",
            "username": "testuser",
            "email": "test@purdue.edu",
            "is_student": True,
            "permissions": ["read", "write"]
        }
    
    return get_test_user


@pytest.fixture
def test_client(mock_db_dependency, mock_auth_dependency, mock_Gemini, test_knowledge_base):
    """Create test client with mocked dependencies"""
    knowledge_file, knowledge_data = test_knowledge_base
    
    # Override dependencies
    app.dependency_overrides[get_db_connection] = mock_db_dependency
    app.dependency_overrides[get_current_user] = mock_auth_dependency
    
    # Set test environment variables
    os.environ['KNOWLEDGE_BASE_PATH'] = knowledge_file
    os.environ['TESTING'] = 'true'
    
    client = TestClient(app)
    yield client
    
    # Cleanup
    app.dependency_overrides.clear()
    if 'KNOWLEDGE_BASE_PATH' in os.environ:
        del os.environ['KNOWLEDGE_BASE_PATH']
    if 'TESTING' in os.environ:
        del os.environ['TESTING']


@pytest.fixture
async def async_test_client(mock_db_dependency, mock_auth_dependency, mock_Gemini, test_knowledge_base):
    """Create async test client"""
    knowledge_file, knowledge_data = test_knowledge_base
    
    # Override dependencies
    app.dependency_overrides[get_db_connection] = mock_db_dependency
    app.dependency_overrides[get_current_user] = mock_auth_dependency
    
    # Set test environment variables
    os.environ['KNOWLEDGE_BASE_PATH'] = knowledge_file
    os.environ['TESTING'] = 'true'
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Cleanup
    app.dependency_overrides.clear()
    if 'KNOWLEDGE_BASE_PATH' in os.environ:
        del os.environ['KNOWLEDGE_BASE_PATH']
    if 'TESTING' in os.environ:
        del os.environ['TESTING']


@pytest.fixture
def sample_student_profile():
    """Sample student profile for testing"""
    return {
        "current_year": "sophomore",
        "gpa": 3.2,
        "completed_courses": ["CS 18000", "CS 18200", "MA 16100", "MA 16200"],
        "failed_courses": [],
        "target_track": "Machine Intelligence",
        "graduation_goal": "Spring 2026"
    }


@pytest.fixture
def sample_session_context():
    """Sample session context for testing"""
    return {
        "session_id": "test_session_123",
        "student_profile": {
            "current_year": "sophomore",
            "gpa": 3.2,
            "completed_courses": ["CS 18000", "CS 18200"]
        },
        "conversation_history": [
            {"user": "Hi", "response": "Hello! How can I help you today?"},
            {"user": "What is CS 18000?", "response": "CS 18000 is Problem Solving..."}
        ],
        "extracted_context": {
            "mentioned_courses": ["CS 18000"],
            "current_topic": "course_info"
        }
    }


@pytest.fixture
def mock_performance_monitor():
    """Mock performance monitoring"""
    with patch('api.middleware.get_performance_monitor') as mock_monitor:
        monitor_instance = Mock()
        monitor_instance.start_request.return_value = "request_123"
        monitor_instance.end_request.return_value = None
        monitor_instance.get_performance_summary.return_value = {
            "current": {"cpu_percent": 25.5, "memory_percent": 45.2},
            "averages": {"response_time_ms": 150.0}
        }
        mock_monitor.return_value = monitor_instance
        yield monitor_instance


# Test data generators
def generate_test_queries():
    """Generate test queries for different intents"""
    return {
        "greeting": [
            "Hi", "Hello", "Hey there", "Good morning", "What's up"
        ],
        "course_info": [
            "What is CS 18000?",
            "Tell me about CS 25100",
            "CS 18200 prerequisites",
            "How hard is CS 25200?",
            "When is CS 37300 offered?"
        ],
        "graduation_planning": [
            "Can I graduate early?",
            "Plan my schedule for next semester",
            "How long will it take to graduate?",
            "What courses should I take next?",
            "I want to graduate in 3 years"
        ],
        "track_info": [
            "What's the difference between MI and SE tracks?",
            "Should I choose Machine Intelligence?",
            "Software Engineering track requirements",
            "Which track is better for AI careers?",
            "MI track electives"
        ],
        "failure_recovery": [
            "I failed CS 25100, what now?",
            "How does failing CS 18000 affect my timeline?",
            "Can I retake a course?",
            "Summer recovery options",
            "Failed multiple courses"
        ],
        "codo_advice": [
            "How do I CODO into CS?",
            "CODO requirements for Computer Science",
            "What GPA do I need for CODO?",
            "CODO application deadline",
            "Chances of getting into CS"
        ]
    }


@pytest.fixture
def test_queries():
    """Provide test queries fixture"""
    return generate_test_queries()


# Performance test helpers
@pytest.fixture
def performance_test_config():
    """Configuration for performance tests"""
    return {
        "concurrent_users": [1, 5, 10, 20],
        "load_duration": 30,  # seconds
        "response_time_threshold": 2.0,  # seconds
        "success_rate_threshold": 0.95,
        "memory_threshold_mb": 500
    }


# Security test helpers
@pytest.fixture
def security_test_payloads():
    """Malicious payloads for security testing"""
    return {
        "sql_injection": [
            "'; DROP TABLE sessions; --",
            "' OR '1'='1",
            "'; INSERT INTO sessions VALUES ('hacked'); --"
        ],
        "xss_payloads": [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>"
        ],
        "command_injection": [
            "; ls -la",
            "| cat /etc/passwd",
            "&& rm -rf /"
        ],
        "oversized_requests": {
            "long_query": "A" * 10000,
            "large_json": {"data": ["x"] * 10000}
        }
    }


# Utility functions for tests
def assert_api_response_structure(response_data: Dict[str, Any], expected_fields: list):
    """Assert API response has expected structure"""
    assert "success" in response_data
    assert "timestamp" in response_data
    
    for field in expected_fields:
        assert field in response_data, f"Missing field: {field}"


def assert_response_time(response_time: float, threshold: float = 2.0):
    """Assert response time is within acceptable limits"""
    assert response_time < threshold, f"Response time {response_time}s exceeds threshold {threshold}s"


def create_test_session_data(session_id: str = "test_session") -> Dict[str, Any]:
    """Create test session data"""
    return {
        "session_id": session_id,
        "student_id": "test_student",
        "created_at": "2024-12-01T14:30:00Z",
        "context_data": json.dumps({
            "current_year": "sophomore",
            "gpa": 3.2,
            "conversation_count": 0
        })
    }