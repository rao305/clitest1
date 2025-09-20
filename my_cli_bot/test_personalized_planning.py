#!/usr/bin/env python3
"""
Test script for personalized graduation planning functionality
Tests both CS and Data Science personalized planning with various scenarios
"""

import json
from intelligent_conversation_manager import IntelligentConversationManager

def test_personalized_planning():
    """Test personalized graduation planning with various scenarios"""
    
    print("🎓 Testing Personalized Graduation Planning System")
    print("=" * 60)
    
    # Initialize conversation manager
    manager = IntelligentConversationManager()
    
    # Test scenarios for different student situations
    test_scenarios = [
        {
            "name": "CS Student with Summer Courses (Ahead of Schedule)",
            "session_id": "test_cs_summer",
            "queries": [
                "Hi, I'm a sophomore CS student",
                "I've taken CS 18000, CS 18200, CS 24000, MA 16100, MA 16200 over summer and fall",
                "I want to plan my entire coursework until graduation for Machine Intelligence track"
            ]
        },
        {
            "name": "Data Science Student (Standard Progress)",
            "session_id": "test_ds_standard", 
            "queries": [
                "Hello, I'm a Data Science freshman",
                "I've completed CS 18000 and MA 16100 this semester",
                "Can you help me plan my graduation timeline?"
            ]
        },
        {
            "name": "CS Student (Early Graduation Goal)",
            "session_id": "test_cs_early",
            "queries": [
                "Hi! I'm a freshman who wants to graduate in 3.5 years",
                "I have CS 18000, CS 18200, and MA 16100 done",
                "Can you create a personalized plan for Software Engineering track?"
            ]
        },
        {
            "name": "Advanced CS Student (Need Specific Scheduling)",
            "session_id": "test_cs_advanced",
            "queries": [
                "I'm a junior CS student",
                "I've completed all foundation courses through CS 38100, plus MA 16100, MA 16200, MA 26100",
                "When should I take CS 47100 and what's my graduation timeline for MI track?"
            ]
        },
        {
            "name": "Data Science Student (Behind Schedule)", 
            "session_id": "test_ds_behind",
            "queries": [
                "I'm a sophomore in Data Science but I'm behind",
                "I only have CS 18000 and MA 16100 completed so far",
                "How can I catch up and graduate on time?"
            ]
        }
    ]
    
    # Run test scenarios
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 Test Scenario {i}: {scenario['name']}")
        print("-" * 50)
        
        session_id = scenario["session_id"]
        
        for j, query in enumerate(scenario["queries"], 1):
            print(f"\n🔹 Query {j}: {query}")
            print("📤 Response:")
            
            try:
                response = manager.process_query(session_id, query)
                print(response)
                
                # Add some spacing between responses
                if j < len(scenario["queries"]):
                    print("\n" + "." * 30)
                    
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n" + "=" * 60)

def test_questioning_system():
    """Test the intelligent questioning system"""
    
    print("\n🤔 Testing Intelligent Questioning System")
    print("=" * 60)
    
    manager = IntelligentConversationManager()
    
    # Test with minimal information
    minimal_queries = [
        {
            "session_id": "test_questions_1",
            "query": "I want to plan my graduation",
            "expected_questions": True,
            "description": "Student with no specific information"
        },
        {
            "session_id": "test_questions_2", 
            "query": "I'm a CS student and want to graduate early",
            "expected_questions": True,
            "description": "CS student with graduation goal but no progress info"
        },
        {
            "session_id": "test_questions_3",
            "query": "I need help planning my Data Science degree",
            "expected_questions": True,
            "description": "Data Science student with no progress info"
        }
    ]
    
    for i, test_case in enumerate(minimal_queries, 1):
        print(f"\n📋 Question Test {i}: {test_case['description']}")
        print("-" * 40)
        print(f"🔹 Query: {test_case['query']}")
        
        try:
            response = manager.process_query(test_case["session_id"], test_case["query"])
            print("📤 Response:")
            print(response)
            
            # Check if response contains questions
            has_questions = any(char in response for char in "?") and len(response.split("?")) > 2
            
            if test_case["expected_questions"] and has_questions:
                print("✅ Successfully asked clarifying questions")
            elif not test_case["expected_questions"] and not has_questions:
                print("✅ Didn't ask unnecessary questions")
            else:
                print("⚠️ Question behavior unexpected")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "=" * 40)

def test_course_extraction():
    """Test enhanced course extraction from various query formats"""
    
    print("\n📚 Testing Enhanced Course Extraction")
    print("=" * 60)
    
    manager = IntelligentConversationManager()
    
    extraction_tests = [
        {
            "query": "I've taken CS 18000, CS 18200, CS 24000 and MA 16100, MA 16200",
            "expected_courses": ["CS 18000", "CS 18200", "CS 24000", "MA 16100", "MA 16200"],
            "description": "Standard course format"
        },
        {
            "query": "I completed CS180, CS182, MA161 over summer to speed things up",
            "expected_courses": ["CS 18000", "CS 18200", "MA 16100"],
            "description": "Abbreviated course codes with summer context"
        },
        {
            "query": "I'm ahead having finished CS 18000, CS 18200, CS 24000, CS 25000, and CS 25100",
            "expected_courses": ["CS 18000", "CS 18200", "CS 24000", "CS 25000", "CS 25100"],
            "description": "Advanced progress with many courses"
        },
        {
            "query": "I have credit for CS18000 and CS18200 from high school AP",
            "expected_courses": ["CS 18000", "CS 18200"],
            "description": "Concatenated course codes"
        }
    ]
    
    for i, test in enumerate(extraction_tests, 1):
        print(f"\n📋 Extraction Test {i}: {test['description']}")
        print("-" * 40)
        print(f"🔹 Query: {test['query']}")
        
        session_id = f"extraction_test_{i}"
        
        try:
            response = manager.process_query(session_id, test['query'])
            
            # Get the context to check extracted courses
            context = manager.conversation_contexts.get(session_id)
            if context:
                extracted_courses = context.extracted_context.get("completed_courses", [])
                print(f"📤 Extracted courses: {extracted_courses}")
                
                # Check if extraction was successful
                expected_set = set(test["expected_courses"])
                extracted_set = set(extracted_courses)
                
                if expected_set.issubset(extracted_set):
                    print("✅ Successfully extracted expected courses")
                else:
                    missing = expected_set - extracted_set
                    if missing:
                        print(f"⚠️ Missing courses: {missing}")
                    extra = extracted_set - expected_set
                    if extra:
                        print(f"ℹ️ Extra courses: {extra}")
            else:
                print("❌ No context found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "." * 40)

def test_data_science_integration():
    """Test Data Science specific functionality"""
    
    print("\n🔬 Testing Data Science Integration")
    print("=" * 60)
    
    manager = IntelligentConversationManager()
    
    # Test Data Science specific scenarios
    ds_scenarios = [
        {
            "session_id": "ds_test_1",
            "queries": [
                "I'm a Data Science sophomore",
                "I've completed CS 18000, CS 18200, MA 16100, MA 16200, STAT 35500",
                "What should I take next semester and when do I graduate?"
            ],
            "description": "Data Science student with some foundation courses"
        },
        {
            "session_id": "ds_test_2", 
            "queries": [
                "I'm in Data Science and took summer courses",
                "I have CS 18000, CS 18200, CS 24200, MA 16100, MA 16200, MA 26100 done",
                "Can you create my personalized graduation plan?"
            ],
            "description": "Data Science student ahead of schedule"
        }
    ]
    
    for i, scenario in enumerate(ds_scenarios, 1):
        print(f"\n📋 DS Test {i}: {scenario['description']}")
        print("-" * 40)
        
        for j, query in enumerate(scenario["queries"], 1):
            print(f"\n🔹 Query {j}: {query}")
            
            try:
                response = manager.process_query(scenario["session_id"], query)
                print("📤 Response:")
                print(response[:500] + "..." if len(response) > 500 else response)
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n" + "=" * 40)

def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive Personalized Planning Tests")
    print("=" * 70)
    
    try:
        # Test main personalized planning functionality
        test_personalized_planning()
        
        # Test intelligent questioning system
        test_questioning_system()
        
        # Test course extraction improvements
        test_course_extraction()
        
        # Test Data Science integration
        test_data_science_integration()
        
        print("\n🎉 All tests completed!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()