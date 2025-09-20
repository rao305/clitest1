#!/usr/bin/env python3
"""
Test Dual Track Integration
Verifies that the conversation manager can detect and handle dual track requests
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from intelligent_conversation_manager import IntelligentConversationManager

def test_dual_track_detection():
    """Test that dual track requests are properly detected and handled"""
    
    print("🧪 TESTING DUAL TRACK INTEGRATION")
    print("=" * 50)
    
    # Initialize conversation manager
    manager = IntelligentConversationManager(tracker_mode=True)
    
    # Test queries that should trigger dual track detection
    test_queries = [
        "give me a graduation plan for someone taking both tracks",
        "I want to graduate with both machine intelligence and software engineering tracks",
        "easiest way to graduate while taking both machine intelligence track and the software engineering track fastest",
        "freshman year im interesting in both Machine intelligence and software engineering track",
        "can I do both MI and SE tracks?",
        "dual track graduation plan",
        "multiple tracks completion"
    ]
    
    session_id = "test_dual_track_session"
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 40)
        
        try:
            response = manager.process_query(session_id, query)
            
            # Check if response contains dual track content
            dual_track_indicators = [
                "dual track", "both tracks", "machine intelligence and software engineering",
                "CS 38100 counts for both", "advisor approval", "heavy course loads"
            ]
            
            has_dual_track_content = any(indicator in response.lower() for indicator in dual_track_indicators)
            
            if has_dual_track_content:
                print("✅ DUAL TRACK DETECTED - Response contains dual track information")
                print(f"📝 Response preview: {response[:200]}...")
            else:
                print("❌ DUAL TRACK NOT DETECTED - Response doesn't contain dual track info")
                print(f"📝 Response preview: {response[:200]}...")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 TESTING SPECIFIC DUAL TRACK GRADUATION PLAN")
    print("=" * 50)
    
    # Test the specific query that was failing
    specific_query = "No im a freshman year i want to graduate with both tracks so curate a graduation plan"
    print(f"🔍 Testing: {specific_query}")
    
    try:
        response = manager.process_query(session_id, specific_query)
        
        # Check for comprehensive dual track plan
        plan_indicators = [
            "dual track graduation plan", "semester breakdown", "shared courses",
            "machine intelligence track courses", "software engineering track courses"
        ]
        
        has_comprehensive_plan = any(indicator in response.lower() for indicator in plan_indicators)
        
        if has_comprehensive_plan:
            print("✅ COMPREHENSIVE DUAL TRACK PLAN GENERATED")
            print("📝 Plan includes semester breakdown and course details")
        else:
            print("❌ COMPREHENSIVE PLAN NOT GENERATED")
            print("📝 Response may be generic or incomplete")
            
        print(f"\n📄 Full Response Length: {len(response)} characters")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_dual_track_detection() 