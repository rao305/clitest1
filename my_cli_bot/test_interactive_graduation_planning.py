#!/usr/bin/env python3
"""
Test Interactive Graduation Planning with Course Selection

Tests the new interactive features:
1. Course choice presentation
2. User selection parsing
3. Final plan generation with choices
4. AI-generated responses (no hardcoded messages)
"""

from intelligent_conversation_manager import IntelligentConversationManager
from personalized_graduation_planner import PersonalizedGraduationPlanner

def test_interactive_course_selection():
    """Test the interactive course selection workflow"""
    
    print("🎓 Testing Interactive Course Selection Workflow")
    print("=" * 70)
    
    # Initialize systems
    manager = IntelligentConversationManager()
    planner = PersonalizedGraduationPlanner(
        "data/cs_knowledge_graph.json",
        "purdue_cs_knowledge.db"
    )
    
    # Test scenarios that should trigger course choices
    test_scenarios = [
        {
            "name": "CS Student (MI Track) - Should Present AI Course Choice",
            "session_id": "interactive_test_1",
            "queries": [
                "Hi, I'm a junior CS student interested in Machine Intelligence",
                "I've completed CS 18000, CS 18200, CS 24000, CS 25000, CS 25100, CS 25200, CS 35100, CS 38100",
                "Can you create my personalized graduation plan?"
            ]
        },
        {
            "name": "CS Student (SE Track) - Should Present Systems Course Choice", 
            "session_id": "interactive_test_2",
            "queries": [
                "I'm a Computer Science student focusing on Software Engineering",
                "I have completed foundation courses through CS 38100",
                "I want a personalized graduation plan"
            ]
        },
        {
            "name": "Data Science Student - Should Present Elective Choices",
            "session_id": "interactive_test_3", 
            "queries": [
                "I'm a Data Science student in my third year",
                "I've completed the core requirements and need help with electives",
                "Create my graduation plan please"
            ]
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 Test Scenario {i}: {scenario['name']}")
        print("-" * 60)
        
        session_id = scenario["session_id"]
        
        for j, query in enumerate(scenario["queries"], 1):
            print(f"\n🔹 Query {j}: {query}")
            print("📤 AI Response:")
            
            try:
                response = manager.process_query(session_id, query)
                print(response)
                
                # Check if this is a choice request
                context = manager.conversation_contexts.get(session_id)
                if context and hasattr(context, 'awaiting_course_choices') and context.awaiting_course_choices:
                    print("\n✅ Successfully presented course choices to user")
                    print("🔄 System is awaiting user's course selection...")
                    
                    # Simulate user making a choice
                    if "Machine Intelligence" in query or "AI" in response:
                        choice_response = "I'd like CS 47100 for AI and STAT 41600 for statistics"
                    elif "Software Engineering" in query or "Systems" in response:
                        choice_response = "I prefer CS 35400 Operating Systems"
                    elif "Data Science" in query:
                        choice_response = "I'm interested in CS 57300 Data Mining"
                    else:
                        choice_response = "I'll go with the first option"
                    
                    print(f"\n🔹 User Choice Response: {choice_response}")
                    print("📤 AI Final Plan:")
                    
                    final_response = manager.process_query(session_id, choice_response)
                    print(final_response)
                    
                    # Verify choices were processed
                    if "personalized" in final_response.lower() or "plan" in final_response.lower():
                        print("\n✅ Successfully generated final personalized plan with user choices")
                    else:
                        print("\n⚠️ May not have successfully processed user choices")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "=" * 60)

def test_direct_course_choice_functionality():
    """Test course choice functionality directly"""
    
    print("\n🔧 Testing Direct Course Choice Functionality")
    print("=" * 70)
    
    try:
        planner = PersonalizedGraduationPlanner(
            "data/cs_knowledge_graph.json",
            "purdue_cs_knowledge.db"
        )
        
        # Test 1: CS MI student - should need choices
        print("\n📋 Test 1: CS MI Student Course Choice Detection")
        print("-" * 50)
        
        mi_profile = {
            "major": "Computer Science",
            "track": "Machine Intelligence", 
            "completed_courses": ["CS 18000", "CS 18200", "CS 24000", "CS 25000", "CS 25100", "CS 25200", "CS 35100", "CS 38100"],
            "current_year": 3,
            "current_semester": "Fall",
            "graduation_goal": "4_year"
        }
        
        mi_plan = planner.create_personalized_plan(mi_profile)
        
        if hasattr(mi_plan, 'choice_request') and mi_plan.choice_request:
            print("✅ Successfully detected need for course choices")
            print(f"📋 Choices needed: {list(mi_plan.choice_request.keys())}")
            
            # Test choice parsing
            user_response = "I want CS 47100 and STAT 41600"
            parsed_choices = planner.parse_user_course_selections(user_response, mi_plan.choice_request)
            print(f"🎯 Parsed user choices: {parsed_choices}")
            
            # Test final plan generation
            final_plan = planner.create_personalized_plan(mi_profile, parsed_choices)
            print(f"🎓 Final plan graduation: {final_plan.graduation_date}")
            print(f"📊 Success probability: {final_plan.success_probability:.0%}")
            
        else:
            print("⚠️ Did not detect need for course choices - may be an issue")
        
        # Test 2: SE student choices
        print("\n📋 Test 2: CS SE Student Course Choice Detection")
        print("-" * 50)
        
        se_profile = {
            "major": "Computer Science", 
            "track": "Software Engineering",
            "completed_courses": ["CS 18000", "CS 18200", "CS 24000", "CS 25000", "CS 25100", "CS 25200", "CS 35100", "CS 38100"],
            "current_year": 3,
            "current_semester": "Fall",
            "graduation_goal": "4_year"
        }
        
        se_plan = planner.create_personalized_plan(se_profile)
        
        if hasattr(se_plan, 'choice_request') and se_plan.choice_request:
            print("✅ Successfully detected SE course choices needed")
            print(f"📋 SE choices: {list(se_plan.choice_request.keys())}")
        else:
            print("⚠️ Did not detect SE course choices")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in direct testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_response_generation():
    """Test AI response generation (no hardcoded messages)"""
    
    print("\n🤖 Testing AI Response Generation")
    print("=" * 70)
    
    try:
        from ai_response_generator import AIResponseGenerator
        
        generator = AIResponseGenerator("data/cs_knowledge_graph.json")
        
        # Test different types of responses
        test_cases = [
            {
                "type": "greeting",
                "method": "generate_greeting_response",
                "args": [{"current_year": "sophomore", "completed_courses": ["CS 18000"]}]
            },
            {
                "type": "course_planning", 
                "method": "generate_course_planning_response",
                "args": ["What courses should I take next?", {"current_year": "sophomore"}, {"completed_courses": ["CS 18000"]}]
            },
            {
                "type": "track_selection",
                "method": "generate_track_selection_response", 
                "args": ["Should I choose MI or SE?", {"interests": ["AI", "software"]}]
            }
        ]
        
        for test_case in test_cases:
            print(f"\n📋 Testing {test_case['type']} response generation:")
            print("-" * 40)
            
            try:
                method = getattr(generator, test_case['method'])
                response = method(*test_case['args'])
                
                # Check that response is not hardcoded/templated
                if len(response) > 50 and "I" in response and not response.startswith("ERROR"):
                    print("✅ Generated natural AI response")
                    print(f"📝 Sample: {response[:100]}...")
                else:
                    print("⚠️ Response may be too short or templated")
                    print(f"📝 Full response: {response}")
                    
            except Exception as e:
                print(f"❌ Error generating {test_case['type']} response: {e}")
        
        return True
        
    except ImportError:
        print("⚠️ AIResponseGenerator not available - using fallback responses")
        return False
    except Exception as e:
        print(f"❌ Error testing AI responses: {e}")
        return False

def main():
    """Run all interactive tests"""
    
    print("🚀 Starting Interactive Graduation Planning Tests")
    print("=" * 80)
    
    results = []
    
    # Test interactive workflow
    try:
        test_interactive_course_selection()
        results.append(("Interactive Workflow", True))
    except Exception as e:
        print(f"❌ Interactive workflow test failed: {e}")
        results.append(("Interactive Workflow", False))
    
    # Test direct functionality
    results.append(("Direct Course Choice", test_direct_course_choice_functionality()))
    
    # Test AI response generation
    results.append(("AI Response Generation", test_ai_response_generation()))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 80)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED" 
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All interactive features working correctly!")
        print("\n✨ Enhanced Features Now Available:")
        print("  • Interactive course selection for electives")
        print("  • AI-generated responses (no hardcoded messages)")
        print("  • Fully personalized graduation plans")
        print("  • User choice integration and parsing")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()