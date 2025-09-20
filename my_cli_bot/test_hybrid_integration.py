#!/usr/bin/env python3
"""
Test script for Hybrid AI System integration with Universal Purdue Advisor
"""

import os
from universal_purdue_advisor import UniversalPurdueAdvisor

def test_hybrid_integration():
    """Test the integrated hybrid AI system"""
    
    # Set a test API key (will not be used for lookup/rule-based queries)
    os.environ["GEMINI_API_KEY"] = "test-key"
    
    try:
        # Initialize the advisor
        advisor = UniversalPurdueAdvisor()
        
        print("🧪 Testing Hybrid AI System Integration")
        print("=" * 60)
        
        # Test queries that should use different routing strategies
        test_queries = [
            ("What is CS 18000?", "Should use LOOKUP TABLE"),
            ("What are the track requirements for Machine Intelligence?", "Should use LOOKUP TABLE"),
            ("What are the CODO requirements?", "Should use LOOKUP TABLE"),
            ("What are the prerequisites for CS 25000?", "Should use RULE-BASED"),
            ("I failed CS 18000, what should I do?", "Should use RULE-BASED + LLM enhancement"),
            ("Tell me about CS 24000", "Should use LOOKUP TABLE"),
            ("What courses do I need before CS 25200?", "Should use RULE-BASED"),
        ]
        
        for query, expected_strategy in test_queries:
            print(f"\n🎓 Query: {query}")
            print(f"📋 Expected: {expected_strategy}")
            print("-" * 40)
            
            response = advisor.ask_question(query)
            print(f"💬 Response:\n{response}")
            print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_hybrid_integration()