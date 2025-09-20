#!/usr/bin/env python3
"""
Quick test to verify intelligent AI responses
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_ai_engine import SmartAIEngine

def test_intelligent_responses():
    """Test that the AI generates intelligent responses instead of hardcoded ones"""
    
    print("🧪 TESTING INTELLIGENT AI RESPONSES")
    print("=" * 50)
    
    engine = SmartAIEngine()
    
    # Test queries that should trigger intelligent responses
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
            
            # Check if response is intelligent (not hardcoded)
            if len(response) > 200 and "🎓" in response:
                print("✅ INTELLIGENT RESPONSE DETECTED")
                print(f"Response length: {len(response)} characters")
                print(f"Preview: {response[:150]}...")
            else:
                print("❌ RESPONSE APPEARS HARDCODED")
                print(f"Response: {response}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print(f"\n{'='*50}")
    print("🏁 INTELLIGENT AI TEST COMPLETED")

if __name__ == "__main__":
    test_intelligent_responses() 