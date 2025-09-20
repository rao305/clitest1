#!/usr/bin/env python3
"""
Test script for Artificial Intelligence major personalized planning functionality
Tests AI major four-year customization planning with various scenarios
"""

import sys
import json
from datetime import datetime

# Add the project directory to sys.path so we can import modules
sys.path.append('/Users/rrao/Desktop/BCLI/my_cli_bot')

def test_ai_major_planning():
    """Test AI major personalized planning"""
    
    try:
        from personalized_graduation_planner import PersonalizedGraduationPlanner
        print("\n🤖 Testing AI Major Personalized Planning")
        print("=" * 60)
        
        planner = PersonalizedGraduationPlanner(
            "data/cs_knowledge_graph.json",
            "purdue_cs_knowledge.db"
        )
        
        # Test AI major student profile - freshman just starting
        ai_freshman_profile = {
            "major": "Artificial Intelligence",
            "completed_courses": [],
            "current_semester": "Fall",
            "current_year": 1,
            "summer_courses": True,
            "credit_load": "standard",
            "graduation_goal": "4_year"
        }
        
        print(f"📋 Testing AI Major - Freshman Profile")
        print(f"   Major: {ai_freshman_profile['major']}")
        print(f"   Completed: {len(ai_freshman_profile['completed_courses'])} courses")
        print(f"   Goal: {ai_freshman_profile['graduation_goal']} graduation")
        
        ai_plan = planner.create_personalized_plan(ai_freshman_profile)
        
        print(f"\n✅ AI Major plan generated!")
        print(f"📅 Graduation: {ai_plan.graduation_date}")
        print(f"📊 Success Probability: {ai_plan.success_probability:.0%}")
        print(f"📚 Total Semesters: {ai_plan.total_semesters}")
        print(f"🎯 Major: {ai_plan.major}")
        
        # Display some schedule details
        if ai_plan.schedules:
            print(f"\n📅 Sample Semester Schedules:")
            for i, schedule in enumerate(ai_plan.schedules[:3]):  # Show first 3 semesters
                print(f"   {schedule.semester} Year {schedule.year}: {schedule.total_credits} credits")
                for course in schedule.courses[:3]:  # Show first 3 courses
                    print(f"     • {course.get('code', 'Unknown')}")
                if len(schedule.courses) > 3:
                    print(f"     • ... and {len(schedule.courses) - 3} more courses")
        
        # Display customization notes
        if ai_plan.customization_notes:
            print(f"\n🎯 Customization Notes:")
            for note in ai_plan.customization_notes[:3]:
                print(f"   ✓ {note}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in AI major planning test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_major_advanced_student():
    """Test AI major with advanced student (some courses completed)"""
    
    try:
        from personalized_graduation_planner import PersonalizedGraduationPlanner
        print("\n🧠 Testing AI Major - Advanced Student Profile")
        print("=" * 60)
        
        planner = PersonalizedGraduationPlanner(
            "data/cs_knowledge_graph.json",
            "purdue_cs_knowledge.db"
        )
        
        # Advanced AI student profile - sophomore with some progress
        ai_advanced_profile = {
            "major": "Artificial Intelligence",
            "completed_courses": ["CS 17600", "CS 18000", "CS 18200", "PSY 12000", "MA 16100", "MA 16200"],
            "current_semester": "Fall",
            "current_year": 2,
            "summer_courses": True,
            "credit_load": "standard",
            "graduation_goal": "4_year"
        }
        
        print(f"📋 Advanced AI Student Profile")
        print(f"   Major: {ai_advanced_profile['major']}")
        print(f"   Completed: {len(ai_advanced_profile['completed_courses'])} courses")
        print(f"   Sample completed: {', '.join(ai_advanced_profile['completed_courses'][:4])}")
        print(f"   Current: {ai_advanced_profile['current_semester']} Year {ai_advanced_profile['current_year']}")
        
        ai_plan = planner.create_personalized_plan(ai_advanced_profile)
        
        print(f"\n✅ Advanced AI plan generated!")
        print(f"📅 Graduation: {ai_plan.graduation_date}")
        print(f"📊 Success Probability: {ai_plan.success_probability:.0%}")
        print(f"📚 Total Semesters: {ai_plan.total_semesters}")
        
        # Show remaining requirements
        remaining = ai_plan.remaining_requirements
        print(f"\n📋 Remaining Requirements Summary:")
        for req_type, courses in remaining.items():
            if courses:
                print(f"   {req_type.replace('_', ' ').title()}: {len(courses)} courses")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in advanced AI student test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_major_course_choices():
    """Test AI major course choice functionality"""
    
    try:
        from personalized_graduation_planner import PersonalizedGraduationPlanner
        print("\n🎯 Testing AI Major Course Choices")
        print("=" * 60)
        
        planner = PersonalizedGraduationPlanner(
            "data/cs_knowledge_graph.json",
            "purdue_cs_knowledge.db"
        )
        
        # AI student ready for elective choices
        ai_choice_profile = {
            "major": "Artificial Intelligence", 
            "completed_courses": ["CS 17600", "CS 18000", "CS 18200", "CS 24300", "CS 25300", "CS 37300", "CS 38100"],
            "current_semester": "Fall",
            "current_year": 4,
            "summer_courses": False,
            "credit_load": "standard",
            "graduation_goal": "4_year"
        }
        
        print(f"📋 AI Student Ready for Choices")
        print(f"   Completed Core CS: {len([c for c in ai_choice_profile['completed_courses'] if c.startswith('CS')])}")
        
        # This should trigger choice requests
        ai_plan = planner.create_personalized_plan(ai_choice_profile)
        
        # Check if choices are requested
        if hasattr(ai_plan, 'choice_request') and ai_plan.choice_request:
            print(f"✅ Course choices requested!")
            print(f"📝 Choice categories: {list(ai_plan.choice_request.keys())}")
            
            for choice_key, choice_info in ai_plan.choice_request.items():
                print(f"\n🎯 {choice_info['category']}:")
                print(f"   Requirement: {choice_info['requirement_type']}")
                print(f"   Options: {len(choice_info['options'])} available")
        else:
            print(f"✅ Plan generated without needing choices")
            print(f"📅 Graduation: {ai_plan.graduation_date}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in AI course choices test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_knowledge_base_integration():
    """Test that AI major is properly integrated in knowledge base"""
    
    try:
        print("\n📚 Testing AI Major Knowledge Base Integration")
        print("=" * 60)
        
        with open('/Users/rrao/Desktop/BCLI/my_cli_bot/data/cs_knowledge_graph.json', 'r') as f:
            knowledge = json.load(f)
        
        # Check if AI major exists
        if "Artificial Intelligence" in knowledge:
            ai_info = knowledge["Artificial Intelligence"]
            print(f"✅ AI major found in knowledge base")
            print(f"📋 Description: {ai_info.get('description', 'N/A')[:100]}...")
            print(f"🎓 Degree: {ai_info.get('degree_title', 'N/A')}")
            print(f"🏫 College: {ai_info.get('college', 'N/A')}")
            
            # Check sample plan
            if "sample_4_year_plan" in ai_info:
                sample_plan = ai_info["sample_4_year_plan"]
                print(f"📅 Sample 4-year plan: {len(sample_plan)} semesters defined")
                
                # Check first semester
                if "fall_1" in sample_plan:
                    fall_1 = sample_plan["fall_1"]
                    courses = fall_1.get("courses", [])
                    print(f"📚 Fall 1st Year: {len(courses)} courses")
                    print(f"   Sample: {courses[0].get('code', 'N/A')} - {courses[0].get('title', 'N/A')}")
            
            # Check major requirements
            if "major_requirements" in ai_info:
                requirements = ai_info["major_requirements"]
                print(f"📋 Major requirements defined:")
                core_cs = requirements.get("core_cs_courses", [])
                print(f"   Core CS courses: {len(core_cs)}")
                print(f"   Grade requirement: {requirements.get('grade_requirement', 'N/A')}")
            
            # Check career outcomes
            if "career_outcomes" in ai_info:
                careers = ai_info["career_outcomes"]
                print(f"💼 Career outcomes: {len(careers)} listed")
                print(f"   Sample: {careers[0] if careers else 'N/A'}")
            
            return True
        else:
            print(f"❌ AI major not found in knowledge base")
            return False
            
    except Exception as e:
        print(f"❌ Error in knowledge base integration test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all AI major tests"""
    print("🤖 AI MAJOR PERSONALIZED PLANNING TESTS")
    print("=" * 80)
    
    results = []
    
    # Test basic AI major planning
    results.append(("AI Major Basic Planning", test_ai_major_planning()))
    
    # Test advanced student scenario
    results.append(("AI Major Advanced Student", test_ai_major_advanced_student()))
    
    # Test course choices
    results.append(("AI Major Course Choices", test_ai_major_course_choices()))
    
    # Test knowledge base integration
    results.append(("AI Knowledge Base Integration", test_ai_knowledge_base_integration()))
    
    # Summary
    print(f"\n🏁 TEST RESULTS SUMMARY")
    print("=" * 60)
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All AI major personalized planning tests PASSED!")
        print("🚀 AI major customization feature is ready!")
    else:
        print("⚠️  Some tests failed - check implementation")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)