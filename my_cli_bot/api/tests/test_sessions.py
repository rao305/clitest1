#!/usr/bin/env python3
"""
Test Session Management API Endpoints
TDD approach: Write tests first, then implement endpoints
"""

import pytest
import json
import time
from unittest.mock import patch
from fastapi import status


class TestSessionCreation:
    """Test session creation endpoint"""
    
    def test_create_session_success(self, test_client):
        """Test successful session creation"""
        # ARRANGE
        request_data = {
            "student_id": "test_student_123",
            "initial_context": {
                "current_year": "sophomore",
                "gpa": 3.2,
                "completed_courses": ["CS 18000", "CS 18200"]
            }
        }
        
        # ACT
        response = test_client.post("/api/v1/sessions", json=request_data)
        
        # ASSERT
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["success"] is True
        assert "session_id" in data
        assert data["session_id"].startswith("session_")
        assert "expires_at" in data
        assert "context" in data
        assert data["context"]["current_year"] == "sophomore"
        assert "processing_time_ms" in data
        assert data["processing_time_ms"] > 0
    
    def test_create_session_minimal_data(self, test_client):
        """Test session creation with minimal data"""
        # ARRANGE
        request_data = {}
        
        # ACT
        response = test_client.post("/api/v1/sessions", json=request_data)
        
        # ASSERT
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["success"] is True
        assert "session_id" in data
        assert data["context"] is not None
    
    def test_create_session_invalid_context(self, test_client):
        """Test session creation with invalid context data"""
        # ARRANGE
        request_data = {
            "student_id": "test_student",
            "initial_context": {
                "current_year": "invalid_year",  # Invalid year
                "gpa": 5.5,  # Invalid GPA
                "completed_courses": "not_a_list"  # Invalid type
            }
        }
        
        # ACT
        response = test_client.post("/api/v1/sessions", json=request_data)
        
        # ASSERT
        # Should still create session but sanitize context
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["success"] is True
        # Invalid fields should be filtered out or corrected
        context = data["context"]
        assert context.get("current_year") != "invalid_year"
    
    def test_create_session_performance(self, test_client):
        """Test session creation performance"""
        # ARRANGE
        request_data = {"student_id": "perf_test"}
        
        # ACT
        start_time = time.time()
        response = test_client.post("/api/v1/sessions", json=request_data)
        end_time = time.time()
        
        # ASSERT
        response_time = end_time - start_time
        assert response_time < 1.0  # Should complete in under 1 second
        
        data = response.json()
        assert data["processing_time_ms"] < 1000  # Reported time should also be under 1s


class TestSessionRetrieval:
    """Test session retrieval endpoint"""
    
    def test_get_session_success(self, test_client):
        """Test successful session retrieval"""
        # ARRANGE - Create a session first
        create_response = test_client.post("/api/v1/sessions", json={"student_id": "test_student"})
        session_id = create_response.json()["session_id"]
        
        # ACT
        response = test_client.get(f"/api/v1/sessions/{session_id}")
        
        # ASSERT
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["success"] is True
        assert data["session_id"] == session_id
        assert "context" in data
        assert "expires_at" in data
    
    def test_get_session_not_found(self, test_client):
        """Test retrieving non-existent session"""
        # ARRANGE
        invalid_session_id = "non_existent_session"
        
        # ACT
        response = test_client.get(f"/api/v1/sessions/{invalid_session_id}")
        
        # ASSERT
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "SESSION_NOT_FOUND"
        assert "not found" in data["error_message"].lower()
    
    def test_get_session_expired(self, test_client):
        """Test retrieving expired session"""
        # ARRANGE - Create session and simulate expiration
        create_response = test_client.post("/api/v1/sessions", json={"student_id": "test_student"})
        session_id = create_response.json()["session_id"]
        
        # Mock session as expired
        with patch('api.services.session_service.is_session_expired', return_value=True):
            # ACT
            response = test_client.get(f"/api/v1/sessions/{session_id}")
            
            # ASSERT
            assert response.status_code == status.HTTP_410_GONE
            
            data = response.json()
            assert data["success"] is False
            assert data["error_code"] == "SESSION_EXPIRED"


class TestSessionUpdate:
    """Test session update endpoint"""
    
    def test_update_session_context(self, test_client):
        """Test updating session context"""
        # ARRANGE - Create a session first
        create_response = test_client.post("/api/v1/sessions", json={"student_id": "test_student"})
        session_id = create_response.json()["session_id"]
        
        update_data = {
            "context_updates": {
                "current_year": "junior",
                "gpa": 3.5,
                "completed_courses": ["CS 18000", "CS 18200", "CS 25100"]
            }
        }
        
        # ACT
        response = test_client.patch(f"/api/v1/sessions/{session_id}", json=update_data)
        
        # ASSERT
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["success"] is True
        assert data["context"]["current_year"] == "junior"
        assert data["context"]["gpa"] == 3.5
        assert "CS 25100" in data["context"]["completed_courses"]
    
    def test_update_session_invalid_data(self, test_client):
        """Test updating session with invalid data"""
        # ARRANGE
        create_response = test_client.post("/api/v1/sessions", json={"student_id": "test_student"})
        session_id = create_response.json()["session_id"]
        
        update_data = {
            "context_updates": {
                "gpa": "invalid_gpa",  # Invalid type
                "completed_courses": None  # Invalid value
            }
        }
        
        # ACT
        response = test_client.patch(f"/api/v1/sessions/{session_id}", json=update_data)
        
        # ASSERT
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "VALIDATION_ERROR"


class TestSessionDeletion:
    """Test session deletion endpoint"""
    
    def test_delete_session_success(self, test_client):
        """Test successful session deletion"""
        # ARRANGE
        create_response = test_client.post("/api/v1/sessions", json={"student_id": "test_student"})
        session_id = create_response.json()["session_id"]
        
        # ACT
        response = test_client.delete(f"/api/v1/sessions/{session_id}")
        
        # ASSERT
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify session is deleted
        get_response = test_client.get(f"/api/v1/sessions/{session_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_session_not_found(self, test_client):
        """Test deleting non-existent session"""
        # ARRANGE
        invalid_session_id = "non_existent_session"
        
        # ACT
        response = test_client.delete(f"/api/v1/sessions/{invalid_session_id}")
        
        # ASSERT
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "SESSION_NOT_FOUND"


class TestSessionConcurrency:
    """Test session handling under concurrent access"""
    
    def test_concurrent_session_creation(self, test_client):
        """Test creating multiple sessions concurrently"""
        import threading
        import queue
        
        # ARRANGE
        results = queue.Queue()
        thread_count = 10
        
        def create_session(student_id):
            response = test_client.post("/api/v1/sessions", json={"student_id": f"student_{student_id}"})
            results.put((student_id, response.status_code, response.json()))
        
        # ACT
        threads = []
        for i in range(thread_count):
            thread = threading.Thread(target=create_session, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # ASSERT
        session_ids = set()
        while not results.empty():
            student_id, status_code, data = results.get()
            assert status_code == status.HTTP_201_CREATED
            assert data["success"] is True
            session_ids.add(data["session_id"])
        
        # All sessions should have unique IDs
        assert len(session_ids) == thread_count
    
    def test_concurrent_session_updates(self, test_client):
        """Test concurrent updates to same session"""
        # ARRANGE
        create_response = test_client.post("/api/v1/sessions", json={"student_id": "test_student"})
        session_id = create_response.json()["session_id"]
        
        import threading
        import queue
        
        results = queue.Queue()
        
        def update_session(update_value):
            update_data = {
                "context_updates": {
                    "test_field": f"value_{update_value}"
                }
            }
            response = test_client.patch(f"/api/v1/sessions/{session_id}", json=update_data)
            results.put((update_value, response.status_code, response.json()))
        
        # ACT
        threads = []
        for i in range(5):
            thread = threading.Thread(target=update_session, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # ASSERT
        successful_updates = 0
        while not results.empty():
            update_value, status_code, data = results.get()
            if status_code == status.HTTP_200_OK:
                successful_updates += 1
        
        assert successful_updates >= 1  # At least one update should succeed


class TestSessionSecurity:
    """Test session security aspects"""
    
    def test_session_id_unpredictability(self, test_client):
        """Test that session IDs are unpredictable"""
        # ARRANGE & ACT
        session_ids = []
        for i in range(10):
            response = test_client.post("/api/v1/sessions", json={"student_id": f"student_{i}"})
            session_id = response.json()["session_id"]
            session_ids.append(session_id)
        
        # ASSERT
        # All session IDs should be unique
        assert len(set(session_ids)) == 10
        
        # Session IDs should not follow predictable pattern
        # Check that they don't increment sequentially
        ids_without_prefix = [sid.replace("session_", "") for sid in session_ids]
        for i in range(1, len(ids_without_prefix)):
            assert ids_without_prefix[i] != str(int(ids_without_prefix[i-1]) + 1)
    
    def test_session_isolation(self, test_client):
        """Test that sessions are properly isolated"""
        # ARRANGE
        response1 = test_client.post("/api/v1/sessions", json={"student_id": "student1"})
        session_id1 = response1.json()["session_id"]
        
        response2 = test_client.post("/api/v1/sessions", json={"student_id": "student2"})
        session_id2 = response2.json()["session_id"]
        
        # Update session 1
        update_data = {"context_updates": {"secret_data": "confidential"}}
        test_client.patch(f"/api/v1/sessions/{session_id1}", json=update_data)
        
        # ACT - Get session 2
        response = test_client.get(f"/api/v1/sessions/{session_id2}")
        
        # ASSERT
        data = response.json()
        assert "secret_data" not in data["context"]
        assert data["context"].get("student_id") == "student2"
    
    def test_unauthorized_session_access(self, test_client):
        """Test unauthorized access to sessions"""
        # This test would be more meaningful with actual authentication
        # For now, we test basic access patterns
        
        # ARRANGE
        create_response = test_client.post("/api/v1/sessions", json={"student_id": "private_student"})
        session_id = create_response.json()["session_id"]
        
        # ACT - Try to access with malformed session ID
        malformed_ids = [
            session_id + "_hacked",
            session_id.replace("session_", "admin_"),
            "../../../etc/passwd",
            "'; DROP TABLE sessions; --"
        ]
        
        # ASSERT
        for malformed_id in malformed_ids:
            response = test_client.get(f"/api/v1/sessions/{malformed_id}")
            assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]
            
            data = response.json()
            assert data["success"] is False


@pytest.mark.performance
class TestSessionPerformance:
    """Performance tests for session endpoints"""
    
    def test_session_creation_performance_benchmark(self, test_client, performance_test_config):
        """Benchmark session creation performance"""
        # ARRANGE
        session_count = 100
        max_response_time = performance_test_config["response_time_threshold"]
        
        # ACT
        response_times = []
        for i in range(session_count):
            start_time = time.time()
            response = test_client.post("/api/v1/sessions", json={"student_id": f"benchmark_user_{i}"})
            end_time = time.time()
            
            response_times.append(end_time - start_time)
            assert response.status_code == status.HTTP_201_CREATED
        
        # ASSERT
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time_actual = max(response_times)
        
        assert avg_response_time < max_response_time / 2  # Average should be well under threshold
        assert max_response_time_actual < max_response_time  # No response should exceed threshold
        
        print(f"Session creation performance:")
        print(f"  Average: {avg_response_time:.3f}s")
        print(f"  Maximum: {max_response_time_actual:.3f}s")
        print(f"  Minimum: {min(response_times):.3f}s")
    
    def test_session_retrieval_performance(self, test_client):
        """Test session retrieval performance"""
        # ARRANGE - Create multiple sessions
        session_ids = []
        for i in range(50):
            response = test_client.post("/api/v1/sessions", json={"student_id": f"perf_user_{i}"})
            session_ids.append(response.json()["session_id"])
        
        # ACT & ASSERT
        for session_id in session_ids:
            start_time = time.time()
            response = test_client.get(f"/api/v1/sessions/{session_id}")
            end_time = time.time()
            
            assert response.status_code == status.HTTP_200_OK
            assert (end_time - start_time) < 0.5  # Should be very fast for retrieval