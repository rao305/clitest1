#!/usr/bin/env python3
"""
Test Data Science CS Electives System
Tests the system's ability to handle Data Science CS electives questions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from intelligent_conversation_manager import IntelligentConversationManager
import json

def test_data_science_electives():
    """Test Data Science CS electives guidance"""
    print("🧪 Testing Data Science CS Electives System")
    print("=" * 60)
    
    # Initialize conversation manager
    conversation_manager = IntelligentConversationManager()
    session_id = "test_ds_electives_session"
    
    # Test scenarios
    test_queries = [
        {
            "query": "I'm a Data Science major and need to choose CS electives. What are my options?",
            "context": "General electives inquiry"
        },
        {
            "query": "What CS electives should I take for Data Science if I want to focus on machine learning?",
            "context": "ML-focused electives"
        },
        {
            "query": "How many CS electives do Data Science majors need to take?",
            "context": "Credit requirements"
        },
        {
            "query": "I'm a DS major interested in data visualization. Which electives should I choose?",
            "context": "Data visualization focus"
        },
        {
            "query": "What's the difference between CS 34800 and CS 44800 for Data Science students?",
            "context": "Course comparison"
        },
        {
            "query": "Can I take CS 31100 and CS 41100 as my two CS electives for Data Science?",
            "context": "Competitive programming electives"
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {test['context']}")
        print("-" * 40)
        print(f"Query: {test['query']}")
        print("\nResponse:")
        
        try:
            # Process the query
            response = conversation_manager.process_query(session_id, test['query'])
            print(response['response'])
            
            # Check if response contains relevant information
            response_text = response['response'].lower()
            contains_electives = 'elective' in response_text
            contains_credits = 'credit' in response_text or '6-7' in response_text
            contains_courses = any(course in response_text for course in ['cs 47100', 'cs 43900', 'cs 38100', 'cs 31100'])
            
            results.append({
                'test': test['context'],
                'query': test['query'],
                'contains_electives': contains_electives,
                'contains_credits': contains_credits,
                'contains_courses': contains_courses,
                'response_length': len(response['response']),
                'success': contains_electives and (contains_credits or contains_courses)
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                'test': test['context'],
                'query': test['query'],
                'error': str(e),
                'success': False
            })
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    successful_tests = sum(1 for r in results if r.get('success', False))
    total_tests = len(results)
    
    for result in results:
        status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
        print(f"{status} - {result['test']}")
        if 'error' in result:
            print(f"    Error: {result['error']}")
        elif result.get('success', False):
            print(f"    ✓ Contains electives info: {result['contains_electives']}")
            print(f"    ✓ Contains credit info: {result['contains_credits']}")
            print(f"    ✓ Contains course info: {result['contains_courses']}")
        print()
    
    print(f"Overall Success Rate: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
    
    if successful_tests == total_tests:
        print("🎉 All tests passed! Data Science CS electives system is working correctly.")
    else:
        print("⚠️ Some tests failed. System may need additional configuration.")
    
    return successful_tests == total_tests

if __name__ == "__main__":
    success = test_data_science_electives()
    sys.exit(0 if success else 1)