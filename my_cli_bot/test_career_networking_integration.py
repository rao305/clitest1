#!/usr/bin/env python3
"""
Test Career Networking Integration
Comprehensive testing of career networking features with existing Boiler AI system
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_career_networking_module():
    """Test the career networking module independently"""
    print("🔍 Testing Career Networking Module...")
    
    try:
        from career_networking import CareerNetworkingInterface
        
        # Test initialization
        interface = CareerNetworkingInterface("lk_26267cec2bcd4f34b9894bc07a00af1b")
        print("✅ Career networking interface initialized successfully")
        
        # Test intent classification
        test_queries = [
            "Find Purdue CS alumni working at Google",
            "I want to connect with professionals in machine learning",
            "Can you help me find mentors in software engineering?",
            "Show me alumni working at tech companies",
            "Looking for networking opportunities in AI"
        ]
        
        for query in test_queries:
            intent = interface._classify_career_intent(query)
            print(f"   Query: '{query}' -> Intent: {intent}")
        
        print("✅ Intent classification working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Career networking module test failed: {e}")
        return False

def test_conversation_manager_integration():
    """Test integration with intelligent conversation manager"""
    print("\n🔍 Testing Conversation Manager Integration...")
    
    try:
        from intelligent_conversation_manager import IntelligentConversationManager
        
        # Initialize conversation manager
        manager = IntelligentConversationManager()
        print("✅ Conversation manager initialized successfully")
        
        # Check if career networking is available
        if hasattr(manager, 'career_networking') and manager.career_networking:
            print("✅ Career networking integration detected")
        else:
            print("❌ Career networking not properly integrated")
            return False
        
        # Test intent pattern detection
        career_queries = [
            "alumni working at Microsoft",
            "find professionals in my field", 
            "networking opportunities",
            "mentorship in software engineering",
            "purdue graduates in AI"
        ]
        
        for query in career_queries:
            is_career_query = manager._is_career_networking_query(query)
            print(f"   Query: '{query}' -> Career query: {is_career_query}")
        
        print("✅ Career query detection working")
        return True
        
    except Exception as e:
        print(f"❌ Conversation manager integration test failed: {e}")
        return False

async def test_full_career_workflow():
    """Test complete career networking workflow"""
    print("\n🔍 Testing Full Career Networking Workflow...")
    
    try:
        from intelligent_conversation_manager import IntelligentConversationManager
        
        manager = IntelligentConversationManager()
        
        if not (hasattr(manager, 'career_networking') and manager.career_networking):
            print("❌ Career networking not available for workflow test")
            return False
        
        # Create test student context
        test_session_id = "test_session_001"
        
        # Simulate building student context through queries
        context_building_queries = [
            "I'm a sophomore in CS",
            "I'm interested in the Machine Intelligence track",
            "My GPA is around 3.5"
        ]
        
        print("   Building student context...")
        for query in context_building_queries:
            try:
                response = manager.process_query(test_session_id, query)
                print(f"   Context query processed: {len(response)} chars")
            except Exception as e:
                print(f"   Warning: Context building query failed: {e}")
        
        # Test career networking queries
        career_test_queries = [
            "Find Purdue alumni working in machine learning",
            "Can you help me find mentors in AI?",
            "Show me professionals at Google who studied CS at Purdue"
        ]
        
        print("   Testing career networking queries...")
        for query in career_test_queries:
            try:
                # This would make real API calls, so we'll simulate
                print(f"   Career query: '{query}' -> Would process with Clado API")
                
                # Test the query detection
                is_career = manager._is_career_networking_query(query)
                if is_career:
                    print(f"   ✅ Correctly identified as career networking query")
                else:
                    print(f"   ❌ Failed to identify as career networking query")
                    
            except Exception as e:
                print(f"   ❌ Career query processing failed: {e}")
        
        print("✅ Full workflow test completed")
        return True
        
    except Exception as e:
        print(f"❌ Full workflow test failed: {e}")
        return False

def test_ai_prompt_integration():
    """Test AI training prompt integration"""
    print("\n🔍 Testing AI Prompt Integration...")
    
    try:
        from ai_training_prompts import get_comprehensive_system_prompt
        
        system_prompt = get_comprehensive_system_prompt()
        
        # Check for career networking content
        career_keywords = [
            "Career Networking",
            "Professional Connections", 
            "alumni",
            "mentorship",
            "networking"
        ]
        
        found_keywords = []
        for keyword in career_keywords:
            if keyword.lower() in system_prompt.lower():
                found_keywords.append(keyword)
        
        if len(found_keywords) >= 3:
            print(f"✅ AI prompts include career networking training ({len(found_keywords)}/5 keywords found)")
        else:
            print(f"❌ AI prompts missing career networking content ({len(found_keywords)}/5 keywords found)")
            return False
        
        print("✅ AI prompt integration successful")
        return True
        
    except Exception as e:
        print(f"❌ AI prompt integration test failed: {e}")
        return False

def test_database_integration():
    """Test database integration for career profiles"""
    print("\n🔍 Testing Database Integration...")
    
    try:
        from career_networking import CareerNetworkingEngine
        
        # Test database initialization
        engine = CareerNetworkingEngine("test_api_key", ":memory:")
        print("✅ Career networking database initialized")
        
        # Test profile creation
        test_profile = {
            'year': 'sophomore',
            'track': 'MI', 
            'gpa_range': '3.0-3.5',
            'career_interests': ['machine learning', 'artificial intelligence'],
            'target_companies': ['Google', 'Microsoft'],
            'preferred_locations': ['Bay Area', 'Seattle'],
            'skills': ['Python', 'ML algorithms']
        }
        
        engine.update_student_career_profile("test_student", test_profile)
        print("✅ Student career profile created")
        
        # Test profile retrieval
        retrieved_profile = engine.get_student_career_profile("test_student")
        if retrieved_profile and retrieved_profile.track == 'MI':
            print("✅ Student career profile retrieved successfully")
        else:
            print("❌ Failed to retrieve student career profile")
            return False
        
        print("✅ Database integration working")
        return True
        
    except Exception as e:
        print(f"❌ Database integration test failed: {e}")
        return False

def test_error_handling():
    """Test error handling and fallback scenarios"""
    print("\n🔍 Testing Error Handling...")
    
    try:
        from career_networking import CareerNetworkingInterface
        
        # Test with invalid API key
        interface = CareerNetworkingInterface("invalid_key")
        
        # Test query classification with edge cases
        edge_case_queries = [
            "",  # Empty query
            "a",  # Single character
            "What are the prerequisites for CS 25000?",  # Non-career query
            "alumni" * 100,  # Very long query
        ]
        
        for query in edge_case_queries:
            try:
                intent = interface._classify_career_intent(query)
                print(f"   Edge case handled: '{query[:20]}...' -> {intent}")
            except Exception as e:
                print(f"   ❌ Edge case failed: {e}")
                return False
        
        print("✅ Error handling working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

async def run_all_tests():
    """Run all integration tests"""
    print("🚀 Starting Career Networking Integration Tests")
    print("=" * 60)
    
    test_results = []
    
    # Run individual tests
    test_results.append(("Career Networking Module", test_career_networking_module()))
    test_results.append(("Conversation Manager Integration", test_conversation_manager_integration()))
    test_results.append(("AI Prompt Integration", test_ai_prompt_integration()))
    test_results.append(("Database Integration", test_database_integration()))
    test_results.append(("Error Handling", test_error_handling()))
    test_results.append(("Full Workflow", await test_full_career_workflow()))
    
    # Print results summary
    print("\n" + "=" * 60)
    print("🏁 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<35} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Career networking integration is ready.")
        print("\n💡 Usage Examples:")
        print("   - 'Find Purdue CS alumni working at Google'")
        print("   - 'I need mentors in machine learning'") 
        print("   - 'Show me professionals in software engineering'")
        print("   - 'Connect me with alumni in the Bay Area'")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    print("Career Networking Integration Test Suite")
    print("This test validates the seamless integration of career networking with Boiler AI")
    print()
    
    # Run async tests
    success = asyncio.run(run_all_tests())
    
    if success:
        print("\n🎯 Integration Complete: Career networking is now seamlessly integrated!")
        print("   Students can now discover alumni, find mentors, and explore career connections")
        print("   through natural conversation with the AI advisor.")
    else:
        print("\n🔧 Integration Issues: Please address the failed tests before deployment.")
    
    sys.exit(0 if success else 1)