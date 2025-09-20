#!/usr/bin/env python3
"""
Comprehensive test script for the universal query tracker
Tests tracking across all intent categories and query types
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_universal_tracker():
    """Test the universal tracker with various query types"""
    
    from boiler_ai_complete import BoilerAIComplete
    
    print("🔍 Testing Universal Query Tracker")
    print("=" * 80)
    print("This will show how ANY query gets processed through the system")
    print("=" * 80)
    
    # Initialize with tracker mode enabled
    boiler_ai = BoilerAIComplete(tracker_mode=True)
    
    # Comprehensive test queries covering all intent categories
    test_queries = [
        # 1. Course Planning (all year levels)
        ("Course Planning - Freshman", "What courses should a freshman take?"),
        ("Course Planning - Sophomore", "What should a sophomore computer science major take?"),
        ("Course Planning - Junior", "Junior course requirements"),
        ("Course Planning - Senior", "Senior capstone planning"),
        
        # 2. Track Selection
        ("Track Selection", "Should I choose Machine Intelligence or Software Engineering track?"),
        ("MI Track Courses", "What courses do I need for machine intelligence track?"),
        ("SE Track Courses", "Software engineering track requirements"),
        
        # 3. CODO Advice
        ("CODO Requirements", "How do I CODO into computer science?"),
        ("CODO Eligibility", "What are the requirements to change major to CS?"),
        
        # 4. Course Difficulty
        ("Course Difficulty", "How hard is CS 25200?"),
        ("Course Tips", "What are some tips for CS 18000?"),
        
        # 5. Failure Recovery
        ("Course Failure", "I failed CS 25100, what should I do?"),
        ("Multiple Failures", "I failed CS 18000 and Math 16100"),
        
        # 6. Graduation Planning
        ("Graduation Timeline", "When will I graduate if I'm a sophomore?"),
        ("Early Graduation", "Can I graduate early?"),
        
        # 7. Career Guidance
        ("Career Planning", "What careers can I pursue with a CS degree?"),
        ("Internship Advice", "How do I get an internship?"),
        
        # 8. General Queries
        ("Course Info", "What is CS 18000?"),
        ("Prerequisites", "What are the prerequisites for CS 25000?"),
        
        # 9. Greetings
        ("Greeting", "Hi there!"),
        ("Greeting with Question", "Hello, can you help me with course planning?"),
        
        # 10. Edge Cases
        ("Complex Query", "I'm a junior CS student with a 3.2 GPA who failed CS 25100 and wants to graduate on time while pursuing the MI track"),
    ]
    
    print(f"\n📋 Testing {len(test_queries)} different query types...")
    print("🔍 Tracker will show the complete journey of each query\n")
    
    for i, (category, query) in enumerate(test_queries, 1):
        print(f"\n{'='*100}")
        print(f"🧪 TEST {i}/{len(test_queries)}: {category}")
        print(f"❓ Query: \"{query}\"")
        print('='*100)
        
        try:
            # Process the query with full tracking
            response = boiler_ai.ask_question(query)
            
            print(f"\n✅ TRACKING COMPLETE - Response Generated Successfully")
            print(f"📊 Response Length: {len(response)} characters")
            
            # Brief response preview
            preview = response[:150] + "..." if len(response) > 150 else response
            print(f"📝 Response Preview: {preview}")
            
        except Exception as e:
            print(f"\n❌ ERROR during tracking: {e}")
        
        print(f"\n{'⬇'*100}")
        print("NEXT TEST")
        print(f"{'⬇'*100}")

def show_tracker_capabilities():
    """Show what the tracker can monitor"""
    
    print("\n🔍 Universal Query Tracker Capabilities")
    print("=" * 60)
    
    capabilities = {
        "🔍 Query Processing Stages": [
            "QUERY_INPUT - Raw user input reception",
            "QUERY_VALIDATION - Input sanitization",
            "SESSION_CREATED - New session initialization", 
            "CONTEXT_EXTRACTION - Student context building",
            "INTENT_ANALYSIS - Intent classification with confidence",
            "RESPONSE_ROUTING - Handler selection logic",
            "RESPONSE_GENERATED - Final response creation"
        ],
        
        "🎯 Intent Classification Tracking": [
            "greeting - Welcome messages", 
            "course_planning - Course selection guidance",
            "track_selection - MI/SE track decisions",
            "graduation_planning - Timeline and requirements",
            "course_difficulty - Study tips and challenges",
            "failure_recovery - Course retake strategies", 
            "codo_advice - Major change guidance",
            "career_guidance - Career and internship advice"
        ],
        
        "🗺️ Knowledge Graph Access": [
            "Course catalog traversal",
            "Prerequisite chain analysis", 
            "CODO requirements lookup",
            "Track requirements validation",
            "GPA and credit calculations"
        ],
        
        "🧭 Routing Decisions": [
            "Year-level detection (freshman → senior)",
            "Track-specific routing (MI/SE)",
            "Pattern matching explanations",
            "Handler selection rationale"
        ],
        
        "📊 Context Tracking": [
            "Student profile building",
            "Conversation history maintenance",
            "Context changes between queries",
            "Information extraction from queries"
        ]
    }
    
    for category, items in capabilities.items():
        print(f"\n{category}")
        for item in items:
            print(f"  • {item}")
    
    print(f"\n💡 Usage Tips:")
    print(f"  • Use 'tracker on' to enable detailed tracking")
    print(f"  • Use 'tracker off' to disable tracking")
    print(f"  • Start with --tracker flag: python boiler_ai_complete.py --tracker")
    print(f"  • Every query type will show its complete processing journey")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--capabilities":
        show_tracker_capabilities()
    else:
        print("⚠️  Note: This test requires Gemini module. Run in the proper environment.")
        print("🔍 To see tracker capabilities: python test_universal_tracker.py --capabilities")
        print("\n📋 Test Query Categories:")
        
        categories = [
            "Course Planning (all year levels)", "Track Selection", "CODO Advice",
            "Course Difficulty", "Failure Recovery", "Graduation Planning", 
            "Career Guidance", "General Queries", "Greetings", "Complex Edge Cases"
        ]
        
        for i, category in enumerate(categories, 1):
            print(f"  {i}. {category}")
        
        print(f"\n🚀 To run actual tests (requires Gemini setup):")
        print(f"   python test_universal_tracker.py")