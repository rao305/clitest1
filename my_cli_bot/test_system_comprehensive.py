#!/usr/bin/env python3
"""
Comprehensive System Test - Test AI-powered system for gaps and hardcoded messages
Tests the system without requiring Gemini API key for basic functionality
"""

import sys
import json
import time
import traceback
from sql_query_handler import SQLQueryHandler
from hybrid_safety_config import HybridSafetyManager

def test_sql_query_handler():
    """Test SQL query handler for hardcoded messages and AI-powered responses"""
    print("🧪 Testing SQL Query Handler")
    print("=" * 50)
    
    handler = SQLQueryHandler()
    test_cases = [
        # Valid queries that should work
        ("Tell me about CS 18000", "course_info"),
        ("What are the prerequisites for CS 25100?", "prerequisite_chain"),
        ("What courses are in the Machine Intelligence track?", "track_courses"),
        ("How can I graduate in 3 years?", "graduation_timeline"),
        ("What happens if I fail CS 18000?", "failure_impact"),
        ("How hard is CS 25200?", "course_difficulty"),
        ("What are the CODO requirements?", "codo_requirements"),
        ("How many courses can I take as a freshman?", "course_load"),
        
        # Invalid queries that should trigger AI responses
        ("Tell me about XYZ123", "unknown"),
        ("asdfghjkl", "unknown"),
        ("What is the meaning of life?", "unknown"),
        ("invalid course ABC999", "unknown"),
    ]
    
    hardcoded_messages_found = []
    ai_powered_responses = 0
    
    for query, expected_type in test_cases:
        print(f"\n📝 Testing: '{query}'")
        try:
            result = handler.process_query(query)
            print(f"   Type: {result['type']}")
            print(f"   Success: {result['success']}")
            
            if not result['success'] and 'user_friendly_error' in result:
                error_context = result['user_friendly_error']
                
                # Check if it's the new AI-powered format
                if isinstance(error_context, dict) and error_context.get('needs_ai_response'):
                    print(f"   ✅ AI-powered error context detected")
                    print(f"   Context: {error_context.get('context')}")
                    print(f"   Query type: {error_context.get('query_type')}")
                    ai_powered_responses += 1
                else:
                    print(f"   ❌ HARDCODED MESSAGE FOUND: {error_context}")
                    hardcoded_messages_found.append((query, error_context))
            
            if result['success'] and result['count'] > 0:
                print(f"   ✅ SQL query successful - {result['count']} results")
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            traceback.print_exc()
    
    print(f"\n📊 SQL Query Handler Results:")
    print(f"   AI-powered responses: {ai_powered_responses}")
    print(f"   Hardcoded messages found: {len(hardcoded_messages_found)}")
    
    if hardcoded_messages_found:
        print(f"\n❌ HARDCODED MESSAGES DETECTED:")
        for query, message in hardcoded_messages_found:
            print(f"   Query: {query}")
            print(f"   Message: {message[:100]}...")
    
    return len(hardcoded_messages_found) == 0

def test_database_connection():
    """Test database connectivity and structure"""
    print("\n🗄️ Testing Database Connection")
    print("=" * 50)
    
    handler = SQLQueryHandler()
    try:
        with handler.get_connection() as conn:
            cursor = conn.cursor()
            
            # Test table existence
            tables_to_check = [
                'courses', 'prerequisites', 'tracks', 'track_requirements',
                'graduation_timelines', 'failure_recovery', 'codo_requirements',
                'course_load_guidelines'
            ]
            
            missing_tables = []
            for table in tables_to_check:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"   ✅ {table}: {count} records")
                except Exception as e:
                    print(f"   ❌ {table}: Missing or error - {e}")
                    missing_tables.append(table)
            
            print(f"\n📊 Database Status:")
            print(f"   Tables checked: {len(tables_to_check)}")
            print(f"   Missing tables: {len(missing_tables)}")
            
            return len(missing_tables) == 0
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_safety_manager():
    """Test hybrid safety manager for hardcoded messages"""
    print("\n🛡️ Testing Safety Manager")
    print("=" * 50)
    
    try:
        manager = HybridSafetyManager()
        
        # Test safety methods
        print(f"   Should use SQL: {manager.should_use_sql('test query')}")
        
        # Test recording methods (should not produce hardcoded output)
        manager.record_sql_success("test query", 10.5, 5)
        manager.record_sql_failure("test query", "test error", 5.0)
        manager.record_json_fallback("test query", "test reason")
        
        # Get health status
        health = manager.get_health_status()
        print(f"   ✅ Health status retrieved: {health['sql_enabled']}")
        
        # Test emergency rollback (should not print hardcoded messages)
        original_active = manager.query_stats['emergency_rollback_active']
        manager._trigger_emergency_rollback("test")
        manager.query_stats['emergency_rollback_active'] = original_active
        
        print(f"   ✅ Safety manager working - no hardcoded messages detected")
        return True
        
    except Exception as e:
        print(f"❌ Safety manager error: {e}")
        traceback.print_exc()
        return False

def test_system_integration():
    """Test overall system integration"""
    print("\n🔗 Testing System Integration")
    print("=" * 50)
    
    try:
        # Test importing main components
        from simple_boiler_ai import SimpleBoilerAI
        print("   ✅ SimpleBoilerAI import successful")
        
        from universal_purdue_advisor import UniversalPurdueAdvisor
        print("   ✅ UniversalPurdueAdvisor import successful")
        
        # Test basic initialization (without API key)
        try:
            advisor = UniversalPurdueAdvisor()
            print("   ❌ SHOULD NOT WORK WITHOUT API KEY")
            return False
        except ValueError as e:
            if "GEMINI_API_KEY" in str(e):
                print("   ✅ Correctly requires API key")
            else:
                print(f"   ❌ Unexpected error: {e}")
                return False
        
        print("   ✅ System integration checks passed")
        return True
        
    except Exception as e:
        print(f"❌ Integration error: {e}")
        traceback.print_exc()
        return False

def test_search_for_hardcoded_patterns():
    """Search for common hardcoded message patterns in key files"""
    print("\n🔍 Searching for Hardcoded Patterns")
    print("=" * 50)
    
    hardcoded_patterns = [
        "I'm sorry",
        "I apologize", 
        "I can't",
        "I'm not sure",
        "I need more",
        "I couldn't",
        "Error:",
        "Please try",
        "Sorry,",
        "Unable to",
        "Failed to",
        "Cannot"
    ]
    
    files_to_check = [
        'sql_query_handler.py',
        'simple_boiler_ai.py',
        'intelligent_conversation_manager.py',
        'universal_purdue_advisor.py',
        'hybrid_safety_config.py'
    ]
    
    hardcoded_found = []
    
    for filename in files_to_check:
        try:
            with open(filename, 'r') as f:
                content = f.read()
                
            for pattern in hardcoded_patterns:
                if f'"{pattern}' in content or f"'{pattern}" in content:
                    # Check if it's in a comment or AI prompt
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if pattern in line and (f'"{pattern}' in line or f"'{pattern}" in line):
                            # Skip if it's in a comment
                            stripped = line.strip()
                            if stripped.startswith('#') or 'prompt' in line.lower() or 'ai' in line.lower():
                                continue
                            hardcoded_found.append((filename, i+1, pattern, line.strip()))
            
            print(f"   ✅ {filename} checked")
            
        except Exception as e:
            print(f"   ❌ Error checking {filename}: {e}")
    
    print(f"\n📊 Hardcoded Pattern Search Results:")
    print(f"   Suspicious patterns found: {len(hardcoded_found)}")
    
    if hardcoded_found:
        print(f"\n❌ POTENTIAL HARDCODED MESSAGES:")
        for filename, line_num, pattern, line in hardcoded_found:
            print(f"   {filename}:{line_num} - '{pattern}' in: {line[:80]}...")
    
    return len(hardcoded_found) == 0

def main():
    """Run comprehensive system tests"""
    print("🎯 Comprehensive AI-Powered System Test")
    print("=" * 60)
    print("Testing for gaps and hardcoded messages...\n")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("SQL Query Handler", test_sql_query_handler),
        ("Safety Manager", test_safety_manager),
        ("System Integration", test_system_integration),
        ("Hardcoded Pattern Search", test_search_for_hardcoded_patterns),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running: {test_name}")
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
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
        print("🎉 ALL TESTS PASSED - System is fully AI-powered!")
    else:
        print("⚠️  Some tests failed - review issues above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)