#!/usr/bin/env python3
"""
Test suite for Enhanced LangChain Academic Advisor Pipeline
Comprehensive testing of all components and integration points
"""

import pytest
import json
import os
import asyncio
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Import components to test
from langchain_advisor_pipeline import EnhancedLangChainPipeline, ToolDefinition
from fastapi_advisor_server import app

class TestEnhancedLangChainPipeline:
    """Test the core LangChain pipeline"""
    
    @pytest.fixture
    def mock_Gemini_key(self):
        """Mock Gemini API key for testing"""
        return "test-key-123"
    
    @pytest.fixture
    def pipeline(self, mock_Gemini_key):
        """Create a pipeline instance for testing"""
        with patch.dict(os.environ, {"GEMINI_API_KEY": mock_Gemini_key}):
            with patch("langchain_advisor_pipeline.Gemini"), \
                 patch("langchain_advisor_pipeline.GeminiEmbeddings"), \
                 patch("langchain_advisor_pipeline.FAISS"):
                pipeline = EnhancedLangChainPipeline(mock_Gemini_key)
                return pipeline
    
    def test_initialization(self, pipeline):
        """Test pipeline initialization"""
        assert pipeline is not None
        assert pipeline.GEMINI_API_KEY == "test-key-123"
        assert pipeline.conversation_manager is not None
        assert pipeline.smart_ai_engine is not None
        assert len(pipeline.tools) > 0
    
    def test_tool_definitions(self, pipeline):
        """Test tool definitions structure"""
        tool_defs = pipeline.get_tool_definitions()
        assert len(tool_defs) > 0
        
        # Check required tools are present
        tool_names = [tool["name"] for tool in tool_defs]
        expected_tools = ["getCourseInfo", "getPrerequisites", "getDegreePlan", "analyzeGraduationFeasibility"]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    def test_intent_classification(self, pipeline):
        """Test intent classification with various queries"""
        test_cases = [
            ("What is CS 18000?", "COURSE_INFO"),
            ("What are the prerequisites for CS 25000?", "PREREQUISITES"),
            ("Create a degree plan for me", "DEGREE_PLAN"),
            ("Can I graduate early?", "GRADUATION_ANALYSIS"),
            ("General question about computer science", "FALLBACK")
        ]
        
        for query, expected_intent in test_cases:
            with patch.object(pipeline.intent_chain, 'run', return_value=expected_intent):
                result = pipeline.process_query(query)
                assert result["intent"] == expected_intent
    
    def test_entity_extraction(self, pipeline):
        """Test entity extraction from queries"""
        # Mock intent and entity chains
        with patch.object(pipeline.intent_chain, 'run', return_value="COURSE_INFO"), \
             patch.object(pipeline.entity_chain, 'run', return_value='{"courseCode": "CS18000"}'):
            
            result = pipeline.process_query("What is CS 18000?")
            assert result["entities"]["courseCode"] == "CS18000"
    
    def test_course_info_function(self, pipeline):
        """Test course information retrieval"""
        # Mock the conversation manager response
        mock_response = {"response": "CS 18000 is Problem Solving and Object-Oriented Programming"}
        
        with patch.object(pipeline.conversation_manager, 'process_query', return_value=mock_response):
            result = pipeline._get_course_info("CS18000")
            assert "CS 18000" in result or "Problem Solving" in result
    
    def test_prerequisites_function(self, pipeline):
        """Test prerequisites retrieval"""
        # Mock knowledge base data
        mock_knowledge = {
            "courses": {
                "CS25000": {
                    "prerequisites": ["CS18000", "CS18200"]
                }
            }
        }
        
        with patch("builtins.open"), \
             patch("json.load", return_value=mock_knowledge):
            result = pipeline._get_prerequisites("CS25000")
            assert "CS18000" in result and "CS18200" in result
    
    def test_degree_plan_function(self, pipeline):
        """Test degree plan generation"""
        mock_planner = Mock()
        mock_planner.generate_comprehensive_plan.return_value = "Sample degree plan"
        pipeline.conversation_manager.graduation_planner = mock_planner
        
        result = pipeline._get_degree_plan("Computer Science", "Fall", 2024)
        assert "degree plan" in result.lower()
    
    def test_error_handling(self, pipeline):
        """Test error handling in query processing"""
        # Mock an exception in intent classification
        with patch.object(pipeline.intent_chain, 'run', side_effect=Exception("Test error")):
            result = pipeline.process_query("test query")
            assert result["intent"] == "ERROR"
            assert "error" in result["response"].lower()

class TestFastAPIServer:
    """Test the FastAPI server endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_pipeline(self):
        """Mock the global pipeline"""
        mock = Mock(spec=EnhancedLangChainPipeline)
        mock.process_query.return_value = {
            "intent": "COURSE_INFO",
            "entities": {"courseCode": "CS18000"},
            "response": "Test response",
            "method": "function_call"
        }
        mock.get_tool_definitions.return_value = [
            {
                "name": "getCourseInfo",
                "description": "Get course info",
                "parameters": {"type": "object"}
            }
        ]
        return mock
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        with patch("fastapi_advisor_server.pipeline", None):
            response = client.get("/health")
            # Should return 503 when pipeline not initialized
            assert response.status_code == 503
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
    
    def test_chat_endpoint(self, client, mock_pipeline):
        """Test chat endpoint"""
        with patch("fastapi_advisor_server.pipeline", mock_pipeline):
            response = client.post("/chat", json={
                "query": "What is CS 18000?",
                "session_id": "test-session"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["intent"] == "COURSE_INFO"
            assert data["response"] == "Test response"
            assert data["session_id"] == "test-session"
    
    def test_chat_endpoint_without_pipeline(self, client):
        """Test chat endpoint when pipeline not initialized"""
        with patch("fastapi_advisor_server.pipeline", None):
            response = client.post("/chat", json={
                "query": "Test query"
            })
            assert response.status_code == 503
    
    def test_tools_endpoint(self, client, mock_pipeline):
        """Test tools endpoint"""
        with patch("fastapi_advisor_server.pipeline", mock_pipeline):
            response = client.get("/tools")
            assert response.status_code == 200
            data = response.json()
            assert len(data) > 0
            assert data[0]["name"] == "getCourseInfo"
    
    def test_course_info_endpoint(self, client, mock_pipeline):
        """Test course info endpoint"""
        mock_pipeline._get_course_info.return_value = "Course information"
        
        with patch("fastapi_advisor_server.pipeline", mock_pipeline):
            response = client.get("/courses/CS18000")
            assert response.status_code == 200
            data = response.json()
            assert data["course_code"] == "CS18000"
            assert data["info"] == "Course information"
    
    def test_prerequisites_endpoint(self, client, mock_pipeline):
        """Test prerequisites endpoint"""
        mock_pipeline._get_prerequisites.return_value = "Prerequisites: CS18000"
        
        with patch("fastapi_advisor_server.pipeline", mock_pipeline):
            response = client.get("/courses/CS25000/prerequisites")
            assert response.status_code == 200
            data = response.json()
            assert data["course_code"] == "CS25000"
            assert "CS18000" in data["prerequisites"]
    
    def test_degree_plan_endpoint(self, client, mock_pipeline):
        """Test degree plan endpoint"""
        mock_pipeline._get_degree_plan.return_value = "Sample degree plan"
        
        with patch("fastapi_advisor_server.pipeline", mock_pipeline):
            response = client.post("/degree-plan", params={
                "major": "Computer Science",
                "entry_term": "Fall",
                "entry_year": 2024
            })
            assert response.status_code == 200
            data = response.json()
            assert data["major"] == "Computer Science"
            assert data["entry_term"] == "Fall"
            assert data["entry_year"] == 2024
    
    def test_search_endpoint(self, client, mock_pipeline):
        """Test search endpoint"""
        # Mock vector store
        mock_doc = Mock()
        mock_doc.page_content = "Sample content"
        mock_doc.metadata = {"source": "test"}
        
        mock_vector_store = Mock()
        mock_vector_store.similarity_search.return_value = [mock_doc]
        mock_pipeline.vector_store = mock_vector_store
        
        with patch("fastapi_advisor_server.pipeline", mock_pipeline):
            response = client.get("/search", params={"query": "CS courses"})
            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert len(data["results"]) > 0

class TestIntegration:
    """Integration tests combining multiple components"""
    
    def test_end_to_end_query_processing(self):
        """Test complete query processing pipeline"""
        # This would require actual Gemini API key and real data
        # For now, we'll test the structure
        
        # Mock all external dependencies
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}), \
             patch("langchain_advisor_pipeline.Gemini"), \
             patch("langchain_advisor_pipeline.GeminiEmbeddings"), \
             patch("langchain_advisor_pipeline.FAISS"):
            
            pipeline = EnhancedLangChainPipeline("test-key")
            
            # Mock the intent and entity chains
            with patch.object(pipeline.intent_chain, 'run', return_value="COURSE_INFO"), \
                 patch.object(pipeline.entity_chain, 'run', return_value='{"courseCode": "CS18000"}'), \
                 patch.object(pipeline.conversation_manager, 'process_query', 
                            return_value={"response": "CS 18000 is a programming course"}):
                
                result = pipeline.process_query("What is CS 18000?")
                
                assert result["intent"] == "COURSE_INFO"
                assert result["entities"]["courseCode"] == "CS18000"
                assert "programming course" in result["response"]
                assert result["method"] == "function_call"
    
    def test_fallback_to_rag(self):
        """Test fallback to RAG when entities can't be extracted"""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}), \
             patch("langchain_advisor_pipeline.Gemini"), \
             patch("langchain_advisor_pipeline.GeminiEmbeddings"), \
             patch("langchain_advisor_pipeline.FAISS"):
            
            pipeline = EnhancedLangChainPipeline("test-key")
            
            # Mock intent as FALLBACK
            with patch.object(pipeline.intent_chain, 'run', return_value="FALLBACK"), \
                 patch.object(pipeline.entity_chain, 'run', return_value='{"requires_clarification": true}'), \
                 patch.object(pipeline, '_search_knowledge_base', return_value="Context from search"), \
                 patch.object(pipeline.agent, 'run', return_value="Agent response"):
                
                result = pipeline.process_query("General question about computer science")
                
                assert result["intent"] == "FALLBACK"
                assert result["method"] == "rag_agent"
                assert "Context from search" in result["context"]

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])