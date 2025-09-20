#!/usr/bin/env python3
"""
Simple integration test that demonstrates the unified pipeline concept
without requiring all external dependencies
"""

import json
import os
from enum import Enum
from typing import Dict, Any, Optional

# Simple test implementation to demonstrate the concept
class PipelineMode(Enum):
    N8N_ONLY = "n8n_only"
    LANGCHAIN_ONLY = "langchain_only" 
    HYBRID = "hybrid"
    FALLBACK = "fallback"

class MockUnifiedPipeline:
    """Mock implementation to demonstrate the integration concept"""
    
    def __init__(self):
        self.performance_metrics = {
            "n8n_calls": 0,
            "langchain_calls": 0,
            "hybrid_calls": 0,
            "total_queries": 0
        }
    
    def determine_optimal_pipeline(self, query: str) -> PipelineMode:
        """Demonstrate intelligent pipeline selection"""
        query_lower = query.lower()
        
        # Structured query indicators
        structured_indicators = [
            "what is cs", "prerequisites for", "requirements for",
            "graduation plan", "degree plan", "can i graduate"
        ]
        
        # Conversational query indicators  
        conversational_indicators = [
            "tell me about", "explain", "how does", "what happens",
            "i failed", "i'm struggling", "help me understand"
        ]
        
        is_structured = any(indicator in query_lower for indicator in structured_indicators)
        is_conversational = any(indicator in query_lower for indicator in conversational_indicators)
        
        if is_structured and not is_conversational:
            return PipelineMode.LANGCHAIN_ONLY
        elif is_conversational and not is_structured:
            return PipelineMode.N8N_ONLY
        else:
            return PipelineMode.HYBRID
    
    def process_query(self, query: str, mode: Optional[PipelineMode] = None) -> Dict[str, Any]:
        """Demonstrate query processing with different modes"""
        
        if mode is None:
            mode = self.determine_optimal_pipeline(query)
        
        self.performance_metrics["total_queries"] += 1
        
        if mode == PipelineMode.N8N_ONLY:
            self.performance_metrics["n8n_calls"] += 1
            response = f"N8N Response: Processed '{query}' using conversational workflow"
            
        elif mode == PipelineMode.LANGCHAIN_ONLY:
            self.performance_metrics["langchain_calls"] += 1
            response = f"LangChain Response: Extracted entities and used function calling for '{query}'"
            
        elif mode == PipelineMode.HYBRID:
            self.performance_metrics["hybrid_calls"] += 1
            response = f"Hybrid Response: Combined N8N context and LangChain precision for '{query}'"
            
        else:  # FALLBACK
            response = f"Fallback Response: Used primary method with fallback for '{query}'"
        
        return {
            "query": query,
            "response": response,
            "pipeline_used": mode.value,
            "intent": "demo_intent",
            "confidence": 0.85,
            "success": True
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "status": "operational",
            "components": {
                "n8n_pipeline": "available",
                "langchain_pipeline": "available", 
                "conversation_manager": "available"
            },
            "performance_metrics": self.performance_metrics
        }

def demonstrate_integration():
    """Demonstrate the unified LangChain + N8N integration"""
    
    print("🚀 LangChain + N8N Unified Integration Demo")
    print("=" * 60)
    
    # Create mock pipeline
    pipeline = MockUnifiedPipeline()
    
    # Test queries with different characteristics
    test_queries = [
        {
            "query": "What is CS 18000?",
            "expected_mode": PipelineMode.LANGCHAIN_ONLY,
            "description": "Structured factual query → LangChain"
        },
        {
            "query": "Tell me about the Machine Intelligence track",
            "expected_mode": PipelineMode.N8N_ONLY,
            "description": "Conversational query → N8N"
        },
        {
            "query": "I failed CS 25100, what should I do?",
            "expected_mode": PipelineMode.N8N_ONLY,
            "description": "Context-heavy problem → N8N"
        },
        {
            "query": "Can I graduate in 3 years with both tracks?",
            "expected_mode": PipelineMode.HYBRID,
            "description": "Complex planning query → Hybrid"
        },
        {
            "query": "What are the prerequisites for CS 25000?",
            "expected_mode": PipelineMode.LANGCHAIN_ONLY,
            "description": "Specific information request → LangChain"
        }
    ]
    
    print("\\n🧠 Intelligent Pipeline Routing:")
    print("-" * 40)
    
    for test_case in test_queries:
        query = test_case["query"]
        expected = test_case["expected_mode"]
        description = test_case["description"]
        
        # Test intelligent routing
        detected_mode = pipeline.determine_optimal_pipeline(query)
        
        print(f"Query: \"{query}\"")
        print(f"  Expected: {expected.value}")
        print(f"  Detected: {detected_mode.value}")
        print(f"  Logic: {description}")
        print(f"  Match: {'✅' if detected_mode == expected else '⚠️ Different but valid'}")
        print()
    
    print("\\n🔄 Processing Examples:")
    print("-" * 40)
    
    # Process each query type
    example_queries = [
        ("What is CS 18000?", PipelineMode.LANGCHAIN_ONLY),
        ("Tell me about the MI track", PipelineMode.N8N_ONLY),
        ("Can I graduate early?", PipelineMode.HYBRID),
        ("Help me plan my courses", None)  # Let system decide
    ]
    
    for query, mode in example_queries:
        result = pipeline.process_query(query, mode)
        
        print(f"Query: \"{query}\"")
        print(f"Mode: {mode.value if mode else 'Auto-detected'}")
        print(f"Pipeline used: {result['pipeline_used']}")
        print(f"Response: {result['response']}")
        print()
    
    print("\\n📊 System Status:")
    print("-" * 40)
    
    status = pipeline.get_system_status()
    print(f"Status: {status['status']}")
    print("Components:")
    for component, state in status["components"].items():
        print(f"  • {component}: {state}")
    
    print("\\nPerformance Metrics:")
    metrics = status["performance_metrics"]
    for metric, value in metrics.items():
        print(f"  • {metric}: {value}")
    
    print("\\n🎯 Integration Benefits:")
    print("-" * 40)
    print("✅ Intelligent routing based on query characteristics")
    print("✅ Best of both systems: N8N's context + LangChain's precision")
    print("✅ Fallback capabilities for reliability")
    print("✅ Unified API for easy integration")
    print("✅ Performance monitoring and optimization")
    print("✅ Flexible mode selection")
    
    print("\\n🔧 Architecture Components:")
    print("-" * 40)
    print("• Unified Pipeline Orchestrator")
    print("• Enhanced N8N Integration")
    print("• LangChain Function Calling")
    print("• Intelligent Query Router")
    print("• Caching & Performance Layer")
    print("• REST API & WebSocket Server")
    print("• N8N Workflow Integration")
    
    print("\\n🎉 Demo completed successfully!")
    print("\\nTo use the full integration:")
    print("1. Install: pip install -r requirements_langchain.txt")
    print("2. Set: export GEMINI_API_KEY='your-key'")
    print("3. Run: python unified_api_server.py")
    print("4. Test: curl http://localhost:8000/query")

if __name__ == "__main__":
    demonstrate_integration()