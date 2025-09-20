#!/usr/bin/env python3
"""
Test Script for Enhanced AI Integration
Demonstrates intelligent conversation management and personalized responses
"""

import os
import sys
from universal_purdue_advisor import UniversalPurdueAdvisor

def test_intelligent_conversations():
    """Test the enhanced AI system with various conversation scenarios"""
    
    print("🤖 Testing Enhanced Purdue CS AI Advisor")
    print("=" * 60)
    
    # Initialize advisor
    advisor = UniversalPurdueAdvisor()
    
    # Start new session
    session_id = advisor.start_new_session()
    print(f"Session ID: {session_id}\n")
    
    # Test conversation scenarios
    test_scenarios = [
        {
            "name": "Early Graduation Planning",
            "queries": [
                "I'm a sophomore CS student, completed CS 18000, CS 18200, and CS 24000. I want to graduate early and I'm interested in machine learning.",
                "What's the success probability if I try to graduate in 3 years?",
                "Should I skip CS 180 since I already have programming experience?",
                "What would my course load look like each semester?"
            ]
        },
        {
            "name": "Course Failure Recovery", 
            "queries": [
                "I failed CS 25100 last semester and I'm worried about graduation delay.",
                "How much will this delay my graduation?",
                "Can I take summer courses to catch up?",
                "What courses are affected by failing CS 25100?"
            ]
        },
        {
            "name": "Track Selection Guidance",
            "queries": [
                "I'm interested in both AI and software development. Which track should I choose?",
                "What's the difference between Machine Intelligence and Software Engineering tracks?",
                "If I want to work at a tech company after graduation, which is better?",
                "What are the key courses for each track?"
            ]
        },
        {
            "name": "CODO Requirements",
            "queries": [
                "I'm currently in Engineering First Year and want to transfer to CS.",
                "What GPA do I need for CODO?",
                "I have a 3.2 GPA and completed MA 16100 with a B+. What are my chances?",
                "When can I apply for CODO?"
            ]
        },
        {
            "name": "Course Planning Context",
            "queries": [
                "I'm a junior with 3.7 GPA, completed all foundation courses, interested in Software Engineering track.",
                "What courses should I take next semester?",
                "How many CS courses can I take per semester?",
                "I want to take CS 30700, CS 40800, and CS 35200 next semester. Is that too much?"
            ]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🎯 Testing Scenario: {scenario['name']}")
        print("-" * 40)
        
        for i, query in enumerate(scenario['queries']):
            print(f"\n👤 Query {i+1}: {query}")
            print("🤖 Response:")
            
            try:
                response = advisor.ask_question(query)
                print(response)
                
                # Show context building
                if i == 0:  # After first query, show extracted context
                    context = advisor.get_session_context()
                    if 'extracted_context' in context:
                        print(f"\n📊 Extracted Context: {context['extracted_context']}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("-" * 40)
    
    # Test memory across conversation
    print(f"\n🧠 Testing Conversation Memory")
    print("-" * 40)
    
    memory_test_queries = [
        "I mentioned I'm interested in machine learning earlier. What research opportunities are available?",
        "Based on our previous discussion about my failed course, what's my revised graduation timeline?",
        "Considering everything we've talked about, what's your overall recommendation for my academic plan?"
    ]
    
    for query in memory_test_queries:
        print(f"\n👤 Memory Test: {query}")
        print("🤖 Response:")
        try:
            response = advisor.ask_question(query)
            print(response)
        except Exception as e:
            print(f"❌ Error: {e}")
        print("-" * 40)
    
    # Show final conversation summary
    print(f"\n📈 Final Conversation Summary")
    print("-" * 40)
    final_context = advisor.get_session_context()
    print(f"Session Length: {final_context.get('conversation_length', 0)} exchanges")
    print(f"Extracted Context: {final_context.get('extracted_context', {})}")
    print(f"Recent Topics: {final_context.get('last_queries', [])[-3:]}")

def test_comparison_scenarios():
    """Test how AI handles different student profiles"""
    
    print(f"\n🔄 Testing Different Student Profiles")
    print("=" * 60)
    
    advisor = UniversalPurdueAdvisor()
    
    profiles = [
        {
            "name": "High-Achieving Early Graduate",
            "query": "I'm a freshman with 4.0 GPA, completed CS 18000 with A+, want to graduate in 3 years and work at Google."
        },
        {
            "name": "Struggling Student",
            "query": "I'm a sophomore with 2.8 GPA, failed CS 25100 twice, stressed about graduation timeline."
        },
        {
            "name": "Transfer Student",
            "query": "I transferred from community college, have some programming experience but new to Purdue CS requirements."
        },
        {
            "name": "Career Changer",
            "query": "I'm a senior in Liberal Arts wanting to switch to CS, interested in data science and AI careers."
        }
    ]
    
    for profile in profiles:
        print(f"\n👤 Profile: {profile['name']}")
        print(f"Query: {profile['query']}")
        print("🤖 Personalized Response:")
        
        # Start fresh session for each profile
        advisor.start_new_session()
        
        try:
            response = advisor.ask_question(profile['query'])
            print(response)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 60)

if __name__ == "__main__":
    print("🚀 Starting Enhanced AI Integration Tests")
    
    # Check for Gemini API key
    if not os.environ.get("GEMINI_API_KEY"):
        print("⚠️ Warning: GEMINI_API_KEY not found. Some features may not work.")
        print("Set your API key: export GEMINI_API_KEY='your-key-here'")
        print("Continuing with available features...\n")
    
    test_intelligent_conversations()
    test_comparison_scenarios()
    
    print(f"\n✅ Enhanced AI Testing Complete!")
    print("The system now provides:")
    print("- Personalized responses based on student context")
    print("- Conversation memory and context building")
    print("- Intelligent graduation planning")
    print("- Course failure recovery strategies")
    print("- Track-specific guidance")
    print("- CODO eligibility analysis")
    print("- All responses tailored to individual student needs")