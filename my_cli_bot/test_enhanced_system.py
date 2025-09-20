#!/usr/bin/env python3
"""
Test the enhanced CLI chatbot system with intelligent prerequisite analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from intelligent_conversation_manager import IntelligentConversationManager

def test_calc_failure_query():
    """Test the exact user query about calc 1 failure"""
    manager = IntelligentConversationManager()
    
    # Test query from user
    query = "if i fail calc 1 would i still be able to take cs 182 or cs 240 after my freshman fall semester for spring semester"
    
    print(f"Query: {query}")
    print("=" * 100)
    
    # Process query
    session_id = "test_session_001"
    response = manager.process_query(session_id, query)
    
    print(f"Response:\n{response}")
    print("=" * 100)

def test_multiple_scenarios():
    """Test multiple complex prerequisite scenarios"""
    manager = IntelligentConversationManager()
    
    test_queries = [
        "if i fail calc 1 would i still be able to take cs 182 or cs 240 after my freshman fall semester for spring semester",
        "what happens if I fail CS 18200 in spring semester?",
        "Can I still take CS 240 if I haven't finished calc 1?",
        "I failed CS 180, how does this affect my graduation timeline?",
        "If I fail both CS 182 and calc 1, what should I do?",
        "Prerequisites for CS 25100 and impact of failing CS 18200",
        "CS 240 prerequisites if calc 1 not completed"
    ]
    
    for i, query in enumerate(test_queries):
        print(f"\n{'='*20} TEST CASE {i+1} {'='*20}")
        print(f"Query: {query}")
        print("-" * 80)
        
        session_id = f"test_session_{i+1:03d}"
        try:
            response = manager.process_query(session_id, query)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 80)

if __name__ == "__main__":
    print("🧪 Testing Enhanced CLI Chatbot System")
    print("=====================================")
    
    print("\n📋 Test 1: Original User Query")
    test_calc_failure_query()
    
    print("\n📋 Test 2: Multiple Complex Scenarios")
    test_multiple_scenarios()
    
    print("\n✅ Testing Complete!")