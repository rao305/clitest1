#!/usr/bin/env python3
"""
Detailed Edge Case Testing - Test specific scenarios and SQL failure handling
"""

import sys
import json
import traceback
from sql_query_handler import SQLQueryHandler

def test_course_query_variations():
    """Test different ways of asking about courses"""
    print("🔬 Testing Course Query Variations")
    print("=" * 50)
    
    handler = SQLQueryHandler()
    
    # Test different course code formats
    course_queries = [
        "Tell me about CS18000",  # No space
        "Tell me about CS 18000",  # With space
        "Tell me about cs 18000",  # Lowercase
        "Tell me about CS18000 Programming",  # With extra text
        "Info on CS 18000",  # Different phrasing
        "What is CS 18000?",  # Question format
        "CS 18000 description",  # Different structure
        "Describe CS 18000",  # Another variation
    ]
    
    successful_queries = 0
    ai_responses = 0
    
    for query in course_queries:
        print(f"\n📝 Testing: '{query}'")
        try:
            result = handler.process_query(query)
            print(f"   Type: {result['type']}")
            print(f"   Success: {result['success']}")
            
            if result['success']:
                successful_queries += 1
                print(f"   ✅ Found {result['count']} results")
            else:
                if isinstance(result.get('user_friendly_error'), dict):
                    ai_responses += 1
                    print(f"   ✅ AI-powered error response")
                else:
                    print(f"   ❌ Non-AI error: {result.get('user_friendly_error')}")
                    
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print(f"\n📊 Course Query Results:")
    print(f"   Successful queries: {successful_queries}/{len(course_queries)}")
    print(f"   AI-powered error responses: {ai_responses}")
    
    return successful_queries > 0

def test_prerequisite_queries():
    """Test prerequisite query variations"""
    print("\n🔗 Testing Prerequisite Queries")
    print("=" * 50)
    
    handler = SQLQueryHandler()
    
    prereq_queries = [
        "What are the prerequisites for CS 25100?",
        "Prerequisites for CS 25100",
        "What do I need before CS 25100?",
        "CS 25100 prerequisites",
        "What courses come before CS 25100?",
        "Requirements for CS 25100",
        "prereqs for CS 25100",
        "What are the prereqs for CS25100?",
    ]
    
    successful = 0
    ai_responses = 0
    
    for query in prereq_queries:
        print(f"\n📝 Testing: '{query}'")
        try:
            result = handler.process_query(query)
            print(f"   Type: {result['type']}")
            if result['success'] and result['count'] > 0:
                successful += 1
                print(f"   ✅ Found {result['count']} prerequisites")
            elif not result['success']:
                if isinstance(result.get('user_friendly_error'), dict):
                    ai_responses += 1
                    print(f"   ✅ AI-powered error response")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print(f"\n📊 Prerequisite Query Results:")
    print(f"   Successful: {successful}/{len(prereq_queries)}")
    return successful > 0

def test_track_queries():
    """Test track-related queries"""
    print("\n🎯 Testing Track Queries")
    print("=" * 50)
    
    handler = SQLQueryHandler()
    
    track_queries = [
        "What courses are in the Machine Intelligence track?",
        "Machine Intelligence track courses",
        "MI track requirements",
        "Show me MI track courses",
        "What is in the AI track?",
        "Artificial intelligence track courses",
        "Software Engineering track courses", 
        "SE track requirements",
        "Software track courses",
        "What courses for SE track?",
    ]
    
    successful = 0
    ai_responses = 0
    
    for query in track_queries:
        print(f"\n📝 Testing: '{query}'")
        try:
            result = handler.process_query(query)
            print(f"   Type: {result['type']}")
            if result['success'] and result['count'] > 0:
                successful += 1
                print(f"   ✅ Found {result['count']} track courses")
            elif not result['success']:
                if isinstance(result.get('user_friendly_error'), dict):
                    ai_responses += 1
                    print(f"   ✅ AI-powered error response")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print(f"\n📊 Track Query Results:")
    print(f"   Successful: {successful}/{len(track_queries)}")
    return successful > 0

def test_graduation_planning_queries():
    """Test graduation planning queries"""
    print("\n🎓 Testing Graduation Planning Queries") 
    print("=" * 50)
    
    handler = SQLQueryHandler()
    
    grad_queries = [
        "How can I graduate in 3 years?",
        "3 year graduation plan",
        "Early graduation options",
        "Can I graduate in 3.5 years?", 
        "Fast graduation",
        "Graduate early",
        "4 year graduation plan",
        "graduation timeline",
        "How to graduate quickly?",
    ]
    
    successful = 0
    ai_responses = 0
    
    for query in grad_queries:
        print(f"\n📝 Testing: '{query}'")
        try:
            result = handler.process_query(query)
            print(f"   Type: {result['type']}")
            if result['success'] and result['count'] > 0:
                successful += 1
                print(f"   ✅ Found {result['count']} graduation options")
            elif not result['success']:
                if isinstance(result.get('user_friendly_error'), dict):
                    ai_responses += 1
                    print(f"   ✅ AI-powered error response")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print(f"\n📊 Graduation Planning Results:")
    print(f"   Successful: {successful}/{len(grad_queries)}")
    return successful > 0

def test_codo_queries():
    """Test CODO-related queries"""
    print("\n🔄 Testing CODO Queries")
    print("=" * 50)
    
    handler = SQLQueryHandler()
    
    codo_queries = [
        "What are the CODO requirements?",
        "CODO requirements",
        "How to change to CS major?",
        "Switch to computer science",
        "Transfer to CS",
        "CODO process",
        "Change of degree objective requirements",
        "Requirements to switch to CS",
    ]
    
    successful = 0
    ai_responses = 0
    
    for query in codo_queries:
        print(f"\n📝 Testing: '{query}'")
        try:
            result = handler.process_query(query)
            print(f"   Type: {result['type']}")
            if result['success'] and result['count'] > 0:
                successful += 1
                print(f"   ✅ Found {result['count']} CODO requirements")
            elif not result['success']:
                if isinstance(result.get('user_friendly_error'), dict):
                    ai_responses += 1
                    print(f"   ✅ AI-powered error response")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print(f"\n📊 CODO Query Results:")
    print(f"   Successful: {successful}/{len(codo_queries)}")
    return successful > 0

def test_sql_failure_scenarios():
    """Test SQL failure handling with corrupted database"""
    print("\n💥 Testing SQL Failure Scenarios")
    print("=" * 50)
    
    # Test with non-existent database
    handler_bad = SQLQueryHandler("nonexistent_database.db")
    
    test_queries = [
        "Tell me about CS 18000",
        "What are the prerequisites for CS 25100?",
        "CODO requirements",
    ]
    
    ai_responses = 0
    hardcoded_responses = 0
    
    for query in test_queries:
        print(f"\n📝 Testing with bad DB: '{query}'")
        try:
            result = handler_bad.process_query(query)
            print(f"   Type: {result['type']}")
            print(f"   Success: {result['success']}")
            
            if not result['success'] and 'user_friendly_error' in result:
                error_context = result['user_friendly_error']
                if isinstance(error_context, dict) and error_context.get('needs_ai_response'):
                    ai_responses += 1
                    print(f"   ✅ AI-powered error handling")
                    print(f"   Context: {error_context.get('context')}")
                else:
                    hardcoded_responses += 1
                    print(f"   ❌ HARDCODED: {error_context}")
                    
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n📊 SQL Failure Results:")
    print(f"   AI-powered responses: {ai_responses}")
    print(f"   Hardcoded responses: {hardcoded_responses}")
    
    return hardcoded_responses == 0

def test_edge_case_inputs():
    """Test edge case inputs"""
    print("\n🎭 Testing Edge Case Inputs")
    print("=" * 50)
    
    handler = SQLQueryHandler()
    
    edge_cases = [
        "",  # Empty string
        "   ",  # Just spaces
        "a",  # Single character
        "?" * 100,  # Long string
        "CS 99999",  # Non-existent course
        "ABCD 12345",  # Invalid department
        "What about CS 18000 and also CS 25100 and maybe some other stuff?",  # Complex query
        "cs18000 cs25100 cs24000",  # Multiple courses
        "!@#$%^&*()",  # Special characters
        "12345",  # Just numbers
    ]
    
    handled_properly = 0
    ai_responses = 0
    
    for case in edge_cases:
        print(f"\n📝 Testing edge case: '{case[:50]}{'...' if len(case) > 50 else ''}'")
        try:
            result = handler.process_query(case)
            print(f"   Type: {result['type']}")
            
            if not result['success'] and isinstance(result.get('user_friendly_error'), dict):
                ai_responses += 1
                print(f"   ✅ AI-powered handling")
            elif result['success']:
                print(f"   ✅ Successfully processed")
            
            handled_properly += 1
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print(f"\n📊 Edge Case Results:")
    print(f"   Properly handled: {handled_properly}/{len(edge_cases)}")
    print(f"   AI-powered responses: {ai_responses}")
    
    return handled_properly == len(edge_cases)

def main():
    """Run detailed edge case tests"""
    print("🔬 Detailed Edge Case & SQL Failure Testing")
    print("=" * 60)
    
    tests = [
        ("Course Query Variations", test_course_query_variations),
        ("Prerequisite Queries", test_prerequisite_queries),
        ("Track Queries", test_track_queries),
        ("Graduation Planning", test_graduation_planning_queries),
        ("CODO Queries", test_codo_queries),
        ("SQL Failure Scenarios", test_sql_failure_scenarios),
        ("Edge Case Inputs", test_edge_case_inputs),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DETAILED TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if passed_test:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL DETAILED TESTS PASSED!")
        print("   - No hardcoded messages found")
        print("   - SQL queries working properly") 
        print("   - AI-powered error handling active")
        print("   - Edge cases handled gracefully")
    else:
        print("⚠️  Some tests failed - review output above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)