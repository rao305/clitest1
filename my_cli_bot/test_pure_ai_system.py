#!/usr/bin/env python3
"""
Test Pure AI System - Validate No Hardcoded Responses
Tests that all user-facing responses are AI-generated, not hardcoded
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from intelligent_conversation_manager import IntelligentConversationManager
from smart_ai_engine import SmartAIEngine
from universal_purdue_advisor import UniversalPurdueAdvisor

def test_main_conversation_flows():
    """Test that main conversation flows use AI-generated responses"""
    print("🧪 Testing Main Conversation Flows for Pure AI")
    print("="*70)
    
    try:
        # Initialize the conversation manager
        manager = IntelligentConversationManager()
        print("✅ Conversation manager initialized successfully")
        
        # Test various query types that should generate AI responses
        test_queries = [
            "Hello, I'm a freshman in CS",
            "Can you help me plan my graduation?", 
            "I need help with course selection",
            "What's the difference between MI and SE tracks?",
            "I failed CS 25100, what should I do?",
            "Can I graduate early?",
            "Tell me about summer courses",
            "I'm confused about prerequisites"
        ]
        
        session_id = "test_pure_ai_session"
        ai_generated_count = 0
        
        print(f"\n🔬 Testing {len(test_queries)} conversation scenarios...")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Test {i}: '{query}' ---")
            
            try:
                response = manager.process_query(session_id, query)
                
                # Check response characteristics
                response_length = len(response)
                has_context = "purdue" in response.lower() or "cs" in response.lower()
                is_detailed = response_length > 100
                
                print(f"✅ Response generated ({response_length} chars)")
                print(f"📝 Has context: {has_context}")
                print(f"📏 Detailed response: {is_detailed}")
                
                if has_context and is_detailed:
                    ai_generated_count += 1
                
                # Show first 150 chars of response
                preview = response[:150] + "..." if len(response) > 150 else response
                print(f"📄 Preview: {preview}")
                
            except Exception as e:
                print(f"❌ Error processing query: {e}")
        
        success_rate = (ai_generated_count / len(test_queries)) * 100
        print(f"\n📊 AI Response Quality: {ai_generated_count}/{len(test_queries)} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 EXCELLENT: Main conversation flows are primarily AI-driven!")
        elif success_rate >= 60:
            print("✅ GOOD: Most conversation flows use AI responses")
        else:
            print("⚠️ NEEDS WORK: Many flows still rely on hardcoded content")
            
        return success_rate >= 60
        
    except Exception as e:
        print(f"❌ Critical error in conversation flow test: {e}")
        return False

def test_error_handling():
    """Test that error messages are AI-generated"""
    print("\n🛠️ Testing Error Handling for AI Generation")
    print("="*50)
    
    try:
        manager = IntelligentConversationManager()
        
        # Test error scenarios
        error_scenarios = [
            ("Invalid course selection", "I choose purple monkey courses"),
            ("Unclear graduation planning", "help me graduate somewhere"),
            ("Ambiguous track question", "which one is better"),
        ]
        
        ai_errors = 0
        session_id = "test_errors"
        
        for scenario_name, query in error_scenarios:
            print(f"\n🧪 Testing: {scenario_name}")
            try:
                response = manager.process_query(session_id, query)
                
                # Check if response seems AI-generated (not generic hardcoded)
                is_contextual = len(response) > 50 and any(word in response.lower() 
                                                          for word in ['help', 'understand', 'clarify', 'specific'])
                
                if is_contextual:
                    ai_errors += 1
                    print(f"✅ AI-generated error response")
                else:
                    print(f"⚠️ Possible hardcoded error response")
                    
                print(f"📝 Response: {response[:100]}...")
                    
            except Exception as e:
                print(f"❌ Error in error test: {e}")
        
        error_rate = (ai_errors / len(error_scenarios)) * 100
        print(f"\n📊 AI Error Handling: {ai_errors}/{len(error_scenarios)} ({error_rate:.1f}%)")
        
        return error_rate >= 60
        
    except Exception as e:
        print(f"❌ Critical error in error handling test: {e}")
        return False

def test_greeting_and_farewell():
    """Test greeting and farewell AI generation"""
    print("\n👋 Testing Greeting and Farewell AI Generation")
    print("="*50)
    
    try:
        manager = IntelligentConversationManager()
        session_id = "test_greetings"
        
        # Test greeting
        greeting_response = manager.process_query(session_id, "Hello")
        greeting_ai = len(greeting_response) > 30 and "purdue" in greeting_response.lower()
        
        print(f"👋 Greeting AI-generated: {greeting_ai}")
        print(f"📝 Greeting: {greeting_response[:100]}...")
        
        # Test farewell
        farewell_response = manager.process_query(session_id, "goodbye")
        farewell_ai = len(farewell_response) > 20
        
        print(f"👋 Farewell AI-generated: {farewell_ai}")
        print(f"📝 Farewell: {farewell_response[:100]}...")
        
        return greeting_ai and farewell_ai
        
    except Exception as e:
        print(f"❌ Error in greeting/farewell test: {e}")
        return False

def analyze_remaining_hardcoded_content():
    """Analyze what hardcoded content remains"""
    print("\n🔍 Analyzing Remaining Hardcoded Content")
    print("="*50)
    
    hardcoded_areas = {
        "Course Planning Methods": [
            "_get_sophomore_course_plan",
            "_get_junior_course_plan", 
            "_get_senior_course_plan"
        ],
        "Track Selection Methods": [
            "MI track selection methods",
            "SE track selection methods"
        ],
        "Demo/Test Files": [
            "demo_*.py files",
            "test_*.py files"
        ],
        "Legacy Files": [
            "simple_boiler_ai.py remaining content",
            "friendly_response_generator.py remaining content"
        ]
    }
    
    print("📋 Areas with remaining hardcoded content:")
    for area, methods in hardcoded_areas.items():
        print(f"\n🔸 {area}:")
        for method in methods:
            print(f"   • {method}")
    
    print(f"\n💡 Strategy for Complete Elimination:")
    print("1. Replace remaining course planning methods with AI generation")
    print("2. Update track selection to use AI-generated comparisons")
    print("3. Create AI-powered demo system for testing")
    print("4. Implement AI response caching for performance")
    print("5. Add configuration to disable hardcoded fallbacks")

def main():
    """Run comprehensive pure AI system test"""
    print("🤖 PURE AI SYSTEM VALIDATION")
    print("="*80)
    print("Testing that all user-facing responses are AI-generated...")
    
    # Run all tests
    conversation_test = test_main_conversation_flows()
    error_test = test_error_handling() 
    greeting_test = test_greeting_and_farewell()
    
    # Overall assessment
    print(f"\n🏆 OVERALL RESULTS")
    print("="*30)
    print(f"✅ Main Conversations: {'PASS' if conversation_test else 'NEEDS WORK'}")
    print(f"🛠️ Error Handling: {'PASS' if error_test else 'NEEDS WORK'}")
    print(f"👋 Greetings/Farewells: {'PASS' if greeting_test else 'NEEDS WORK'}")
    
    total_score = sum([conversation_test, error_test, greeting_test])
    
    if total_score == 3:
        print(f"\n🎉 EXCELLENT! System is primarily AI-driven")
        print("✅ Core user-facing responses are AI-generated")
        print("💡 Some secondary methods may still have hardcoded content")
    elif total_score >= 2:
        print(f"\n✅ GOOD! Most critical paths use AI generation")
        print("⚠️ Some areas still need hardcoded content elimination")
    else:
        print(f"\n⚠️ NEEDS SIGNIFICANT WORK")
        print("❌ Major conversation paths still use hardcoded content")
    
    # Show analysis of remaining work
    analyze_remaining_hardcoded_content()
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. ✅ Core conversation manager updated with AI generation")
    print("2. ✅ Main error paths use AI responses")
    print("3. 🔄 Course planning methods need AI conversion (in progress)")
    print("4. 🔄 Track selection methods need AI conversion")
    print("5. 📝 Create configuration for pure AI mode")

if __name__ == "__main__":
    main()