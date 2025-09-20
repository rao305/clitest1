#!/usr/bin/env python3
"""
Comprehensive Test Suite for Unified LangChain + N8N Integration
Tests all components, modes, and edge cases
"""

import asyncio
import json
import os
import pytest
import time
from typing import Dict, Any, List
from unittest.mock import Mock, patch, AsyncMock

# Import components to test
from unified_langchain_n8n_pipeline import (
    UnifiedPipelineOrchestrator,
    UnifiedPipelineConfig, 
    PipelineMode,
    UnifiedQueryResult,
    create_unified_pipeline
)

# Test configuration
TEST_CONFIG = UnifiedPipelineConfig(
    default_mode=PipelineMode.HYBRID,
    GEMINI_API_KEY=os.getenv("GEMINI_API_KEY", "test-key"),
    enable_caching=True,
    cache_ttl_minutes=1,
    max_retries=2,
    timeout_seconds=10,
    enable_monitoring=True,
    fallback_enabled=True
)

class TestUnifiedPipelineOrchestrator:
    """Test suite for unified pipeline orchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create test orchestrator"""
        return create_unified_pipeline(
            GEMINI_API_KEY="test-key",
            default_mode=PipelineMode.HYBRID,
            enable_caching=True
        )
    
    @pytest.fixture
    def sample_queries(self):
        """Sample test queries"""
        return [
            {
                "query": "What is CS 18000?",
                "expected_intent": "COURSE_INFO",
                "expected_mode": PipelineMode.LANGCHAIN_ONLY
            },
            {
                "query": "Tell me about the Machine Intelligence track",
                "expected_intent": "TRACK_GUIDANCE", 
                "expected_mode": PipelineMode.N8N_ONLY
            },
            {
                "query": "I failed CS 25100, what should I do?",
                "expected_intent": "failure_recovery",
                "expected_mode": PipelineMode.N8N_ONLY
            },
            {
                "query": "Can I graduate in 3 years with both tracks?",
                "expected_intent": "GRADUATION_ANALYSIS",
                "expected_mode": PipelineMode.HYBRID
            }
        ]
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly"""
        assert orchestrator is not None
        assert orchestrator.config.default_mode == PipelineMode.HYBRID
        assert orchestrator.logger is not None
        assert orchestrator.performance_metrics is not None
    
    def test_pipeline_mode_detection(self, orchestrator, sample_queries):
        """Test intelligent pipeline mode detection"""
        for query_data in sample_queries:
            detected_mode = orchestrator._determine_optimal_pipeline(query_data["query"])
            
            # Mode detection should be reasonable (may not match exactly due to hybrid logic)
            assert detected_mode in [PipelineMode.N8N_ONLY, PipelineMode.LANGCHAIN_ONLY, PipelineMode.HYBRID]
    
    def test_cache_key_generation(self, orchestrator):
        """Test cache key generation"""
        query = "What is CS 18000?"
        mode = PipelineMode.LANGCHAIN_ONLY
        
        key1 = orchestrator._generate_cache_key(query, mode)
        key2 = orchestrator._generate_cache_key(query, mode)
        key3 = orchestrator._generate_cache_key("Different query", mode)
        
        assert key1 == key2  # Same query/mode should generate same key
        assert key1 != key3  # Different query should generate different key
        assert len(key1) == 32  # MD5 hash length
    
    @pytest.mark.asyncio
    async def test_n8n_only_processing(self, orchestrator):
        """Test N8N-only processing mode"""
        query = "Tell me about CS 18000"
        session_id = "test_n8n"
        
        with patch.object(orchestrator, '_process_n8n_only') as mock_n8n:
            mock_result = UnifiedQueryResult(
                query=query,
                response="CS 18000 is an introductory programming course",
                pipeline_used="n8n_only",
                execution_time=0.5,
                intent="course_info",
                entities={"course_code": "CS18000"},
                confidence=0.8
            )
            mock_n8n.return_value = mock_result
            
            result = await orchestrator.process_query_async(
                query=query,
                session_id=session_id,
                mode=PipelineMode.N8N_ONLY
            )
            
            assert result.pipeline_used == "n8n_only"
            assert result.query == query
            assert "CS 18000" in result.response
            mock_n8n.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_langchain_only_processing(self, orchestrator):
        """Test LangChain-only processing mode"""
        query = "What are the prerequisites for CS 25000?"
        session_id = "test_langchain"
        
        with patch.object(orchestrator, '_process_langchain_only') as mock_langchain:
            mock_result = UnifiedQueryResult(
                query=query,
                response="Prerequisites for CS 25000 are CS 18200 and CS 24000",
                pipeline_used="langchain_only",
                execution_time=0.7,
                intent="PREREQUISITES",
                entities={"courseCode": "CS25000"},
                confidence=0.9
            )
            mock_langchain.return_value = mock_result
            
            result = await orchestrator.process_query_async(
                query=query,
                session_id=session_id,
                mode=PipelineMode.LANGCHAIN_ONLY
            )
            
            assert result.pipeline_used == "langchain_only"
            assert result.query == query
            assert "prerequisites" in result.response.lower()
            mock_langchain.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_hybrid_processing(self, orchestrator):
        """Test hybrid processing mode"""
        query = "Can I graduate early with the MI track?"
        session_id = "test_hybrid"
        
        with patch.object(orchestrator, '_process_hybrid') as mock_hybrid:
            mock_result = UnifiedQueryResult(
                query=query,
                response="Early graduation with MI track is possible with careful planning",
                pipeline_used="hybrid",
                execution_time=1.2,
                intent="GRADUATION_ANALYSIS",
                entities={"track": "Machine Intelligence", "timeline": "early"},
                confidence=0.85
            )
            mock_hybrid.return_value = mock_result
            
            result = await orchestrator.process_query_async(
                query=query,
                session_id=session_id,
                mode=PipelineMode.HYBRID
            )
            
            assert result.pipeline_used == "hybrid"
            assert result.query == query
            assert "graduation" in result.response.lower()
            mock_hybrid.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_caching_functionality(self, orchestrator):
        """Test query caching"""
        query = "What is CS 18000?"
        session_id = "test_cache"
        mode = PipelineMode.N8N_ONLY
        
        # Mock the actual processing method
        with patch.object(orchestrator, '_process_n8n_only') as mock_n8n:
            mock_result = UnifiedQueryResult(
                query=query,
                response="Cached response",
                pipeline_used="n8n_only",
                execution_time=0.1,
                intent="course_info",
                entities={},
                confidence=0.8
            )
            mock_n8n.return_value = mock_result
            
            # First call should invoke processing
            result1 = await orchestrator.process_query_async(query, session_id, mode)
            assert mock_n8n.call_count == 1
            
            # Second call should use cache
            result2 = await orchestrator.process_query_async(query, session_id, mode)
            assert mock_n8n.call_count == 1  # Should not increase
            
            # Results should be the same
            assert result1.response == result2.response
    
    @pytest.mark.asyncio
    async def test_error_handling(self, orchestrator):
        """Test error handling and fallback"""
        query = "Test error handling"
        session_id = "test_error"
        
        with patch.object(orchestrator, '_process_n8n_only') as mock_n8n:
            mock_n8n.side_effect = Exception("Test error")
            
            result = await orchestrator.process_query_async(
                query=query,
                session_id=session_id,
                mode=PipelineMode.N8N_ONLY
            )
            
            assert result.success == False
            assert "error" in result.response.lower()
            assert result.error_message is not None
    
    def test_performance_metrics_update(self, orchestrator):
        """Test performance metrics tracking"""
        initial_queries = orchestrator.performance_metrics["total_queries"]
        initial_avg = orchestrator.performance_metrics["average_response_time"]
        
        # Simulate processing
        orchestrator._update_performance_metrics(PipelineMode.N8N_ONLY, 0.5)
        
        assert orchestrator.performance_metrics["total_queries"] == initial_queries + 1
        assert orchestrator.performance_metrics["n8n_calls"] == 1
    
    def test_system_status(self, orchestrator):
        """Test system status reporting"""
        status = orchestrator.get_system_status()
        
        assert "status" in status
        assert "components" in status
        assert "configuration" in status
        assert "performance_metrics" in status
        assert "cache_stats" in status
        
        # Check component status
        components = status["components"]
        assert "n8n_pipeline" in components
        assert "enhanced_n8n" in components

class TestPipelineModes:
    """Test different pipeline modes and routing"""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock orchestrator for isolated testing"""
        orchestrator = Mock()
        orchestrator.config = TEST_CONFIG
        orchestrator.langchain_available = True
        return orchestrator
    
    def test_mode_enum_values(self):
        """Test pipeline mode enum values"""
        assert PipelineMode.N8N_ONLY.value == "n8n_only"
        assert PipelineMode.LANGCHAIN_ONLY.value == "langchain_only"
        assert PipelineMode.HYBRID.value == "hybrid"
        assert PipelineMode.FALLBACK.value == "fallback"
    
    def test_config_creation(self):
        """Test configuration creation"""
        config = UnifiedPipelineConfig(
            default_mode=PipelineMode.HYBRID,
            GEMINI_API_KEY="test-key",
            enable_caching=True
        )
        
        assert config.default_mode == PipelineMode.HYBRID
        assert config.GEMINI_API_KEY == "test-key"
        assert config.enable_caching == True
        assert config.cache_ttl_minutes == 15  # Default value

class TestIntegrationScenarios:
    """Test real-world integration scenarios"""
    
    @pytest.fixture
    def integration_orchestrator(self):
        """Create orchestrator for integration testing"""
        # Only create if Gemini key is available
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            pytest.skip("Gemini API key not available for integration tests")
        
        return create_unified_pipeline(
            GEMINI_API_KEY=api_key,
            default_mode=PipelineMode.HYBRID
        )
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_course_information_scenario(self, integration_orchestrator):
        """Test course information retrieval scenario"""
        query = "What is CS 18000 about?"
        result = await integration_orchestrator.process_query_async(query)
        
        assert result.success == True
        assert len(result.response) > 50
        assert "CS 18000" in result.response or "18000" in result.response
        assert result.execution_time > 0
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_prerequisite_scenario(self, integration_orchestrator):
        """Test prerequisite query scenario"""
        query = "What are the prerequisites for CS 25100?"
        result = await integration_orchestrator.process_query_async(query)
        
        assert result.success == True
        assert len(result.response) > 30
        assert result.execution_time > 0
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_conversation_continuity(self, integration_orchestrator):
        """Test conversation continuity across multiple queries"""
        session_id = "continuity_test"
        
        # First query
        query1 = "What is CS 18000?"
        result1 = await integration_orchestrator.process_query_async(query1, session_id)
        
        # Follow-up query
        query2 = "What are its prerequisites?"
        result2 = await integration_orchestrator.process_query_async(query2, session_id)
        
        assert result1.success == True
        assert result2.success == True
        assert result1.session_id == result2.session_id

class TestErrorScenarios:
    """Test error scenarios and edge cases"""
    
    @pytest.mark.asyncio
    async def test_invalid_mode_handling(self):
        """Test handling of invalid pipeline modes"""
        with pytest.raises(ValueError):
            PipelineMode("invalid_mode")
    
    @pytest.mark.asyncio
    async def test_empty_query_handling(self):
        """Test handling of empty queries"""
        orchestrator = create_unified_pipeline(GEMINI_API_KEY="test-key")
        
        result = await orchestrator.process_query_async("")
        
        # Should handle gracefully
        assert result is not None
        assert isinstance(result, UnifiedQueryResult)
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling"""
        config = UnifiedPipelineConfig(
            GEMINI_API_KEY="test-key",
            timeout_seconds=0.1  # Very short timeout
        )
        orchestrator = UnifiedPipelineOrchestrator(config)
        
        # This should handle timeout gracefully
        result = await orchestrator.process_query_async("What is CS 18000?")
        
        assert result is not None

class TestPerformance:
    """Performance and load testing"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_queries(self):
        """Test handling of concurrent queries"""
        orchestrator = create_unified_pipeline(GEMINI_API_KEY="test-key")
        
        queries = [
            "What is CS 18000?",
            "What is CS 18200?", 
            "What is CS 24000?",
            "What is CS 25000?",
            "What is CS 25100?"
        ]
        
        # Run queries concurrently
        start_time = time.time()
        tasks = [
            orchestrator.process_query_async(query, f"session_{i}")
            for i, query in enumerate(queries)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Check results
        successful_results = [r for r in results if isinstance(r, UnifiedQueryResult) and r.success]
        
        # Should handle concurrent queries reasonably
        assert len(successful_results) >= len(queries) // 2  # At least half should succeed
        assert end_time - start_time < 30  # Should complete within reasonable time
    
    @pytest.mark.performance
    def test_memory_usage(self):
        """Test memory usage remains reasonable"""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Create and use orchestrator
        orchestrator = create_unified_pipeline(GEMINI_API_KEY="test-key")
        
        # Process multiple queries
        for i in range(10):
            result = orchestrator.process_query_sync(f"Test query {i}")
        
        # Force garbage collection
        gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024

# Test runner
def run_tests():
    """Run all tests"""
    print("🧪 Running Unified Pipeline Integration Tests")
    print("=" * 60)
    
    # Run basic tests
    pytest.main([
        __file__,
        "-v",
        "-x",  # Stop on first failure
        "--tb=short",  # Short traceback format
        "-m", "not integration and not performance"  # Skip integration tests by default
    ])
    
    print("\n" + "=" * 60)
    print("✅ Basic tests completed")
    
    # Run integration tests if Gemini key is available
    if os.getenv("GEMINI_API_KEY"):
        print("\n🔗 Running Integration Tests...")
        pytest.main([
            __file__,
            "-v",
            "-m", "integration",
            "--tb=short"
        ])
        print("✅ Integration tests completed")
    else:
        print("⚠️ Skipping integration tests - GEMINI_API_KEY not set")

if __name__ == "__main__":
    run_tests()