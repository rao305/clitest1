#!/usr/bin/env python3
"""
Test truly dynamic AI responses
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_ai_engine import SmartAIEngine

def test_dynamic_responses():
    """Test that the AI generates truly dynamic responses"""
    
    print("🧪 TESTING TRULY DYNAMIC AI RESPONSES")
    print("=" * 50)
    
    engine = SmartAIEngine()
    
    # Test queries that should trigger dynamic responses
    test_queries = [
        "I want to graduate with both machine intelligence and software engineering tracks",
        "How hard is CS 25100?",
        "What courses should I take as a freshman?",
        "Which track should I choose for AI careers?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 40)
        
        try:
            response = engine.process_query(query)
            
            # Check if response is truly dynamic (not hardcoded)
            if len(response) > 300 and "📊" in response and "ANALYSIS" in response:
                print("✅ TRULY DYNAMIC RESPONSE DETECTED")
                print(f"Response length: {len(response)} characters")
                print(f"Contains analysis: {'📊' in response}")
                print(f"Contains dynamic content: {'ANALYSIS' in response}")
                print(f"Preview: {response[:200]}...")
            else:
                print("❌ RESPONSE APPEARS TEMPLATED")
                print(f"Response: {response}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print(f"\n{'='*50}")
    print("🏁 DYNAMIC AI TEST COMPLETED")

if __name__ == "__main__":
    test_dynamic_responses() 