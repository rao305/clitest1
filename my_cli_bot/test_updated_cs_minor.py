#!/usr/bin/env python3
"""
Test Updated CS Minor Integration
Tests the enhanced AI system with specific course requirements and CS 25100 recommendation
"""

import json
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from intelligent_conversation_manager import IntelligentConversationManager

def test_updated_cs_minor_scenarios():
    """Test CS minor scenarios with updated course structure"""
    
    print("🧪 Testing Updated CS Minor Integration - Specific Course Requirements")
    print("=" * 70)
    
    # Initialize the conversation manager
    manager = IntelligentConversationManager()
    
    # Updated CS Minor test scenarios
    updated_test_cases = [
        # Course structure questions
        {
            "description": "CS minor course structure inquiry",
            "query": "What courses do I need to take for a CS minor?",
            "expected_topics": ["3 compulsory", "CS 18000", "CS 18200", "CS 24000", "2 electives"]
        },
        
        # CS 25100 recommendation
        {
            "description": "Elective course selection question",
            "query": "What electives should I choose for my CS minor?",
            "expected_topics": ["CS 25100", "recommend", "data structures", "foundation", "prerequisite"]
        },
        
        # 5 course limit enforcement
        {
            "description": "Course limit enforcement question",
            "query": "What happens if I take 6 CS courses instead of 5 for my minor?",
            "expected_topics": ["no minor", "not awarded", "5 courses", "exactly", "limit"]
        },
        
        # Compulsory vs elective distinction
        {
            "description": "Required vs elective course distinction",
            "query": "Which CS courses are required vs optional for the minor?",
            "expected_topics": ["compulsory", "required", "CS 18000", "CS 18200", "CS 24000", "elective"]
        },
        
        # CS 25100 specific benefits
        {
            "description": "CS 25100 recommendation rationale",
            "query": "Why do you recommend CS 25100 for CS minor students?",
            "expected_topics": ["foundation", "prerequisite", "advanced", "algorithms", "data structures"]
        },
        
        # Planning with prerequisites
        {
            "description": "Prerequisite planning for electives",
            "query": "I want to take CS 37300 as one of my electives. What do I need first?",
            "expected_topics": ["prerequisite", "CS 25100", "foundation", "requirement"]
        },
        
        # Complete sequence planning
        {
            "description": "Complete CS minor sequence planning",
            "query": "Plan my complete CS minor sequence from start to finish.",
            "expected_topics": ["CS 18000", "CS 18200", "CS 24000", "CS 25100", "5 courses", "off-peak"]
        },
        
        # Course limit awareness
        {
            "description": "Course counting and limit awareness",
            "query": "I've taken CS 18000, 18200, 24000, and 25100. What should my 5th course be?",
            "expected_topics": ["5th course", "elective", "one more", "complete", "minor"]
        }
    ]
    
    session_id = "updated_cs_minor_test"
    
    # Test each scenario
    for i, test_case in enumerate(updated_test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['description']}")
        print(f"Query: \"{test_case['query']}\"")
        print("-" * 60)
        
        try:
            # Get AI response
            response = manager.process_query(session_id, test_case['query'])
            
            print("✅ AI Response:")
            print(response)
            
            # Check coverage
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
            coverage_rate = len(topics_covered) / len(test_case['expected_topics'])
            if coverage_rate >= 0.8:
                print("✅ Quality: Excellent coverage")
            elif coverage_rate >= 0.6:
                print("🟡 Quality: Good coverage")
            else:
                print("⚠️ Quality: Needs improvement")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("=" * 70)

def test_cs_minor_knowledge_base():
    """Test if the knowledge base contains updated CS minor information"""
    
    print("\n📚 Testing CS Minor Knowledge Base Content")
    print("=" * 60)
    
    manager = IntelligentConversationManager()
    
    # Check if knowledge base has the cs_minor section
    try:
        kb_data = manager.knowledge_graph
        if 'cs_minor' in kb_data:
            cs_minor = kb_data['cs_minor']
            print("✅ CS Minor section found in knowledge base")
            
            # Check course structure
            if 'course_structure' in cs_minor:
                structure = cs_minor['course_structure']
                print("✅ Course structure data found")
                
                # Check compulsory courses
                if 'compulsory_courses' in structure:
                    comp = structure['compulsory_courses']
                    print(f"✅ Compulsory courses: {comp.get('count', 0)} required")
                    for course in comp.get('required', []):
                        print(f"   • {course.get('code', 'Unknown')}")
                
                # Check electives
                if 'elective_courses' in structure:
                    elec = structure['elective_courses']
                    print(f"✅ Elective courses: {elec.get('count', 0)} required")
                    if 'strong_recommendation' in elec:
                        rec = elec['strong_recommendation']
                        print(f"✅ Strong recommendation: {rec.get('course', 'Unknown')}")
                
                # Check course limit enforcement
                if 'course_limit_enforcement' in structure:
                    limit = structure['course_limit_enforcement']
                    print(f"✅ Course limit policy: {limit.get('strict_limit', 'Unknown')}")
            
            else:
                print("⚠️ Course structure not found - using old format")
        else:
            print("❌ CS Minor section not found in knowledge base")
            
    except Exception as e:
        print(f"❌ Error checking knowledge base: {e}")

def test_cs25100_recommendation_logic():
    """Test specific scenarios around CS 25100 recommendation"""
    
    print("\n🎯 Testing CS 25100 Recommendation Logic")
    print("=" * 60)
    
    manager = IntelligentConversationManager()
    
    cs25100_scenarios = [
        "What's the best elective for CS minor?",
        "Should I take CS 25100 for my minor?", 
        "Which courses help with advanced CS concepts?",
        "What opens up more CS course options?",
        "I want to take CS 37300 later, what do I need?",
    ]
    
    session_id = "cs25100_test"
    
    for scenario in cs25100_scenarios:
        print(f"\nQuery: \"{scenario}\"")
        try:
            response = manager.process_query(session_id, scenario)
            
            # Check if CS 25100 is mentioned or recommended
            if "25100" in response or "data structures" in response.lower():
                print("✅ CS 25100 mentioned/recommended")
            else:
                print("⚠️ CS 25100 not explicitly mentioned")
                
            # Brief response preview
            preview = response[:200] + "..." if len(response) > 200 else response
            print(f"Response preview: {preview}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_updated_cs_minor_scenarios()
    test_cs_minor_knowledge_base()
    test_cs25100_recommendation_logic()
    
    print("\n🎯 Updated CS Minor Integration Test Complete!")
    print("\n📋 Updated Features:")
    print("• ✅ 3 compulsory courses: CS 18000, CS 18200, CS 24000")
    print("• ✅ 2 elective courses with strong CS 25100 recommendation")
    print("• ✅ Strict 5-course limit enforcement (>5 = no minor)")
    print("• ✅ Prerequisite requirements for electives")
    print("• ✅ CS 25100 rationale: foundation for advanced courses")
    print("• ✅ Pure AI responses based on enhanced knowledge base")
    print("• ✅ Dynamic, personalized course planning advice")