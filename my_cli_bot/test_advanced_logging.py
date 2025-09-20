#!/usr/bin/env python3
"""
Test Advanced Logging System
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_ai_engine import SmartAIEngine

def test_advanced_logging():
    """Test the advanced logging system"""
    
    print("🔍 TESTING ADVANCED LOGGING SYSTEM")
    print("=" * 50)
    
    engine = SmartAIEngine()
    
    # Test queries to see detailed logging
    test_queries = [
        "How hard is CS 25100?",
        "What courses should I take as a freshman?",
        "I want to graduate with both machine intelligence and software engineering tracks"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing Query: {query}")
        print("-" * 40)
        
        try:
            response = engine.process_query(query)
            print(f"✅ Response generated: {len(response)} characters")
            print(f"📄 Response preview: {response[:100]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n{'='*50}")
    print("🏁 ADVANCED LOGGING TEST COMPLETED")
    print("\n📊 Check the log file 'boilerai_queries.log' for detailed analysis!")
    print("🔍 The log will show:")
    print("   • Every step of query processing")
    print("   • Knowledge nodes accessed")
    print("   • Graph traversal operations")
    print("   • NLP processing details")
    print("   • Whether templates were used")
    print("   • AI method effectiveness")

if __name__ == "__main__":
    test_advanced_logging() 