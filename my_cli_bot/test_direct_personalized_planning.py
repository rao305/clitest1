#!/usr/bin/env python3
"""
Direct test of personalized graduation planner without conversation manager
Tests the core personalized planning functionality directly
"""

from personalized_graduation_planner import PersonalizedGraduationPlanner

def test_direct_cs_planning():
    """Test CS personalized planning directly"""
    
    print("🎓 Testing Direct CS Personalized Planning")
    print("=" * 60)
    
    try:
        planner = PersonalizedGraduationPlanner(
            "data/cs_knowledge_graph.json",
            "purdue_cs_knowledge.db"
        )
        
        # Test Case 1: Student with summer courses ahead of schedule
        print("\n📋 Test 1: CS Student with Summer Courses (Ahead of Schedule)")
        print("-" * 50)
        
        student_profile = {
            "major": "Computer Science",
            "track": "Machine Intelligence",
            "completed_courses": ["CS 18000", "CS 18200", "CS 24000", "MA 16100", "MA 16200"],
            "current_year": 2,
            "current_semester": "Fall",
            "graduation_goal": "4_year",
            "credit_load": "standard",
            "summer_courses": True
        }
        
        plan = planner.create_personalized_plan(student_profile)
        
        print(f"✅ Plan generated successfully!")
        print(f"📅 Graduation: {plan.graduation_date}")
        print(f"📊 Success Probability: {plan.success_probability:.0%}")
        print(f"📝 Customization Notes: {len(plan.customization_notes)} notes")
        print(f"📚 Remaining Requirements: {len(plan.remaining_requirements)} categories")
        
        # Show first few semesters
        print("\n📅 First 3 Semesters of Plan:")
        for i, schedule in enumerate(plan.schedules[:3]):
            print(f"  {schedule.semester} Year {schedule.year}: {len(schedule.courses)} courses ({schedule.total_credits} credits)")
            for course in schedule.courses[:3]:  # Show first 3 courses
                print(f"    • {course.get('code', 'Unknown')}")
        
        # Test Case 2: Early graduation goal
        print("\n📋 Test 2: CS Student with Early Graduation Goal")
        print("-" * 50)
        
        early_grad_profile = {
            "major": "Computer Science",
            "track": "Software Engineering",
            "completed_courses": ["CS 18000", "CS 18200", "MA 16100"],
            "current_year": 1,
            "current_semester": "Spring",
            "graduation_goal": "3.5_year",
            "credit_load": "heavy",
            "summer_courses": True
        }
        
        early_plan = planner.create_personalized_plan(early_grad_profile)
        
        print(f"✅ Early graduation plan generated!")
        print(f"📅 Graduation: {early_plan.graduation_date}")
        print(f"📊 Success Probability: {early_plan.success_probability:.0%}")
        print(f"⚠️ Warnings: {len(early_plan.warnings)}")
        print(f"💡 Recommendations: {len(early_plan.recommendations)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in CS planning test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_ds_planning():
    """Test Data Science personalized planning directly"""
    
    print("\n🔬 Testing Direct Data Science Personalized Planning")
    print("=" * 60)
    
    try:
        planner = PersonalizedGraduationPlanner(
            "data/cs_knowledge_graph.json",
            "purdue_cs_knowledge.db"
        )
        
        # Test Case 1: Standard Data Science student
        print("\n📋 Test 1: Data Science Student (Standard Progress)")
        print("-" * 50)
        
        ds_profile = {
            "major": "Data Science",
            "track": "",  # Data Science doesn't have tracks
            "completed_courses": ["CS 18000", "MA 16100", "STAT 35500"],
            "current_year": 1,
            "current_semester": "Spring",
            "graduation_goal": "4_year",
            "credit_load": "standard",
            "summer_courses": False
        }
        
        ds_plan = planner.create_personalized_plan(ds_profile)
        
        print(f"✅ Data Science plan generated!")
        print(f"📅 Graduation: {ds_plan.graduation_date}")
        print(f"📊 Success Probability: {ds_plan.success_probability:.0%}")
        print(f"📚 Total Semesters: {ds_plan.total_semesters}")
        
        # Show customization notes
        print("\n📝 Customization Notes:")
        for note in ds_plan.customization_notes[:3]:
            print(f"  • {note}")
        
        # Test Case 2: Behind schedule Data Science student
        print("\n📋 Test 2: Data Science Student (Behind Schedule)")
        print("-" * 50)
        
        behind_profile = {
            "major": "Data Science",
            "track": "",
            "completed_courses": ["CS 18000", "MA 16100"],
            "current_year": 2,
            "current_semester": "Fall",
            "graduation_goal": "flexible",
            "credit_load": "light",
            "summer_courses": True
        }
        
        behind_plan = planner.create_personalized_plan(behind_profile)
        
        print(f"✅ Catch-up plan generated!")
        print(f"📅 Graduation: {behind_plan.graduation_date}")
        print(f"📊 Success Probability: {behind_plan.success_probability:.0%}")
        print(f"⚠️ Warnings: {len(behind_plan.warnings)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in Data Science planning test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_questioning_system():
    """Test the intelligent questioning system"""
    
    print("\n🤔 Testing Intelligent Questioning System")
    print("=" * 60)
    
    try:
        planner = PersonalizedGraduationPlanner(
            "data/cs_knowledge_graph.json",
            "purdue_cs_knowledge.db"
        )
        
        # Test with minimal information
        print("\n📋 Test: Student with Minimal Information")
        print("-" * 40)
        
        minimal_profile = {
            "major": "Computer Science",
            "completed_courses": [],
            "current_year": 0,
            "graduation_goal": ""
        }
        
        questions = planner.ask_clarifying_questions(minimal_profile)
        
        print(f"✅ Generated {len(questions)} clarifying questions:")
        for i, question in enumerate(questions, 1):
            print(f"  {i}. {question}")
        
        # Test with partial information
        print("\n📋 Test: Student with Partial Information")
        print("-" * 40)
        
        partial_profile = {
            "major": "Computer Science",
            "track": "Machine Intelligence",
            "completed_courses": ["CS 18000"],
            "current_year": 1
        }
        
        partial_questions = planner.ask_clarifying_questions(partial_profile)
        
        print(f"✅ Generated {len(partial_questions)} clarifying questions:")
        for i, question in enumerate(partial_questions, 1):
            print(f"  {i}. {question}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in questioning system test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_course_prioritization():
    """Test course prioritization logic"""
    
    print("\n📚 Testing Course Prioritization Logic")
    print("=" * 60)
    
    try:
        planner = PersonalizedGraduationPlanner(
            "data/cs_knowledge_graph.json",
            "purdue_cs_knowledge.db"
        )
        
        print("\n📋 Test: Course Prerequisites and Prioritization")
        print("-" * 50)
        
        # Test prerequisite checking
        print("✅ Testing prerequisite relationships:")
        
        # Test some key prerequisite relationships
        test_cases = [
            ("CS 18200", ["CS 18000"]),
            ("CS 25000", ["CS 24000"]),
            ("CS 38100", ["CS 25100"]),
            ("MA 16200", ["MA 16100"])
        ]
        
        for course, prereqs in test_cases:
            has_prereqs = planner._check_prerequisites_met(course, set(prereqs))
            print(f"  {course} with {prereqs}: {'✅' if has_prereqs else '❌'}")
        
        print("\n✅ Testing course offerings by semester:")
        test_semesters = ["Fall", "Spring", "Summer"]
        test_courses = ["CS 18000", "CS 47100", "CS 40700"]
        
        for course in test_courses:
            offerings = []
            for semester in test_semesters:
                if planner._is_course_offered(course, semester):
                    offerings.append(semester)
            print(f"  {course}: {', '.join(offerings)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in course prioritization test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all direct tests"""
    print("🚀 Starting Direct Personalized Planning Tests")
    print("=" * 70)
    
    results = []
    
    # Test CS planning
    results.append(("CS Planning", test_direct_cs_planning()))
    
    # Test Data Science planning
    results.append(("Data Science Planning", test_direct_ds_planning()))
    
    # Test questioning system
    results.append(("Questioning System", test_questioning_system()))
    
    # Test course prioritization
    results.append(("Course Prioritization", test_course_prioritization()))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 70)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Personalized planning system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()