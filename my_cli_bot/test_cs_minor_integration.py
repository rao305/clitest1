#!/usr/bin/env python3
"""
Test CS Minor Integration - Comprehensive AI Testing
Tests the enhanced AI system's ability to handle CS minor queries dynamically
"""

import json
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from intelligent_conversation_manager import IntelligentConversationManager

def test_cs_minor_scenarios():
    """Test various CS minor scenarios with AI responses"""
    
    print("🧪 Testing CS Minor Integration - Pure AI System")
    print("=" * 60)
    
    # Initialize the conversation manager
    manager = IntelligentConversationManager()
    
    # CS Minor test scenarios
    cs_minor_test_cases = [
        # Basic requirements
        {
            "description": "Basic CS minor requirements inquiry",
            "query": "What are the requirements for a CS minor?",
            "expected_topics": ["5 courses", "C grade", "off-peak terms"]
        },
        
        # Scheduling questions
        {
            "description": "Peak/off-peak scheduling question",
            "query": "When can I take CS courses for my minor? I heard about peak and off-peak terms.",
            "expected_topics": ["off-peak only", "fall availability", "spring availability", "summer"]
        },
        
        # Course planning
        {
            "description": "CS minor course sequence planning",
            "query": "I'm a sophomore in engineering, how should I plan my CS minor courses?",
            "expected_topics": ["CS 18000", "prerequisite", "timeline", "advisor"]
        },
        
        # Specific course availability
        {
            "description": "Specific course availability question",
            "query": "Can I take CS 18000 in the fall semester for my minor?",
            "expected_topics": ["PEAK", "not available", "spring", "summer"]
        },
        
        # Grade requirements
        {
            "description": "Grade requirements clarification",
            "query": "I got a C- in CS 18200, does that count for my CS minor?",
            "expected_topics": ["C- not accepted", "minimum C", "retake"]
        },
        
        # Post-completion restrictions
        {
            "description": "Post-completion course restrictions",
            "query": "After I complete my CS minor, can I take more CS courses?",
            "expected_topics": ["cannot take", "5 course limit", "completion restriction"]
        },
        
        # Registration process
        {
            "description": "Registration timing and process",
            "query": "How do I register for CS courses as a minor student?",
            "expected_topics": ["advisor adds", "Friday before", "space available", "priority"]
        },
        
        # Complex scenario
        {
            "description": "Complex minor planning scenario",
            "query": "I'm a junior in mechanical engineering with no CS background. Can you help me plan a CS minor that I can complete before graduation?",
            "expected_topics": ["start early", "foundation", "timeline", "summer courses"]
        }
    ]
    
    session_id = "cs_minor_test_session"
    
    # Test each scenario
    for i, test_case in enumerate(cs_minor_test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['description']}")
        print(f"Query: \"{test_case['query']}\"")
        print("-" * 50)
        
        try:
            # Get AI response
            response = manager.process_query(session_id, test_case['query'])
            
            print("✅ AI Response:")
            print(response)
            
            # Check if expected topics are covered
            response_lower = response.lower()
            topics_covered = []
            topics_missing = []
            
            for topic in test_case['expected_topics']:
                if topic.lower() in response_lower:
                    topics_covered.append(topic)
                else:
                    topics_missing.append(topic)
            
            print(f"\n📊 Coverage Analysis:")
            if topics_covered:
                print(f"✅ Topics covered: {', '.join(topics_covered)}")
            if topics_missing:
                print(f"⚠️  Topics missing: {', '.join(topics_missing)}")
            
            # Quality assessment
            if len(topics_covered) >= len(test_case['expected_topics']) * 0.7:
                print("✅ Quality: Good coverage")
            else:
                print("⚠️ Quality: Needs improvement")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("=" * 60)
    
    # Test conversation memory with CS minor context
    print("\n🧠 Testing Conversation Memory with CS Minor Context")
    print("=" * 60)
    
    memory_session = "cs_minor_memory_test"
    
    # First query to establish context
    context_query = "I'm interested in getting a CS minor. I'm currently a sophomore in biology."
    print(f"Context Query: \"{context_query}\"")
    context_response = manager.process_query(memory_session, context_query)
    print("Context Response:")
    print(context_response)
    print("-" * 40)
    
    # Follow-up query that should use the established context
    followup_query = "What courses should I start with?"
    print(f"Follow-up Query: \"{followup_query}\"")
    followup_response = manager.process_query(memory_session, followup_query)
    print("Follow-up Response:")
    print(followup_response)
    
    # Check if the response references the established context
    if "biology" in followup_response.lower() or "sophomore" in followup_response.lower():
        print("✅ Context memory: Working correctly")
    else:
        print("⚠️ Context memory: May need improvement")
    
    print("\n🎯 CS Minor Integration Test Complete!")
    
    # Summary
    print("\n📋 Summary:")
    print("• Knowledge base updated with comprehensive CS minor data")
    print("• AI training prompts enhanced with CS minor expertise")
    print("• Intent recognition patterns added for CS minor queries")
    print("• Conversation manager updated with CS minor handler")
    print("• Pure AI responses - no hardcoded templates")
    print("• Dynamic, personalized responses based on student context")

def test_intent_recognition():
    """Test specific intent recognition for CS minor queries"""
    
    print("\n🎯 Testing CS Minor Intent Recognition")
    print("=" * 60)
    
    manager = IntelligentConversationManager()
    
    test_phrases = [
        "cs minor requirements",
        "computer science minor",
        "minor in computer science", 
        "off-peak courses",
        "peak vs off-peak CS",
        "5 CS courses for minor",
        "CS minor course access",
        "minor course scheduling"
    ]
    
    for phrase in test_phrases:
        # Test the intent recognition patterns
        patterns = manager.intent_patterns.get("cs_minor_planning", [])
        match_found = False
        
        for pattern in patterns:
            if __import__('re').search(pattern, phrase.lower()):
                match_found = True
                break
        
        status = "✅" if match_found else "❌"
        print(f"{status} \"{phrase}\" - Intent recognition: {'PASSED' if match_found else 'FAILED'}")

if __name__ == "__main__":
    test_cs_minor_scenarios()
    test_intent_recognition()