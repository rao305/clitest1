#!/usr/bin/env python3
"""
Demo script showing the new Artificial Intelligence major personalized planning feature
Shows how the customization works for AI major students
"""

import sys
sys.path.append('/Users/rrao/Desktop/BCLI/my_cli_bot')

from personalized_graduation_planner import PersonalizedGraduationPlanner

def demonstrate_ai_major_planning():
    """Demonstrate AI major personalized planning capabilities"""
    
    print("🤖 ARTIFICIAL INTELLIGENCE MAJOR PLANNING DEMO")
    print("=" * 60)
    print("Demonstrating the new AI major customization feature!")
    
    planner = PersonalizedGraduationPlanner(
        "data/cs_knowledge_graph.json",
        "purdue_cs_knowledge.db"
    )
    
    # Demo 1: Freshman AI student
    print("\n📚 DEMO 1: AI Major Freshman Student")
    print("-" * 40)
    
    ai_freshman = {
        "major": "Artificial Intelligence",
        "completed_courses": [],
        "current_semester": "Fall",
        "current_year": 1,
        "summer_courses": True,
        "credit_load": "standard",
        "graduation_goal": "4_year"
    }
    
    print(f"Student Profile:")
    print(f"  • Major: {ai_freshman['major']}")
    print(f"  • Academic Level: Freshman")
    print(f"  • Graduation Goal: 4 years")
    print(f"  • Summer Courses: Available")
    
    plan = planner.create_personalized_plan(ai_freshman)
    
    print(f"\nPlan Results:")
    print(f"  • Graduation Date: {plan.graduation_date}")
    print(f"  • Major: {plan.major}")
    print(f"  • Requires Course Selections: {hasattr(plan, 'choice_request') and plan.choice_request is not None}")
    
    if hasattr(plan, 'choice_request') and plan.choice_request:
        print(f"  • Choice Categories: {list(plan.choice_request.keys())}")
        for choice_key, choice_info in plan.choice_request.items():
            print(f"    - {choice_info['category']}: {len(choice_info['options'])} options")
    
    # Demo 2: Advanced AI student with courses completed
    print("\n🎓 DEMO 2: AI Major Advanced Student")
    print("-" * 40)
    
    ai_advanced = {
        "major": "Artificial Intelligence",
        "completed_courses": [
            "CS 17600", "CS 18000", "CS 18200", "CS 24300", 
            "PSY 12000", "MA 16100", "MA 16200", "STAT 35000"
        ],
        "current_semester": "Spring",
        "current_year": 2,
        "summer_courses": True,
        "credit_load": "standard", 
        "graduation_goal": "4_year"
    }
    
    print(f"Student Profile:")
    print(f"  • Major: {ai_advanced['major']}")
    print(f"  • Academic Level: Sophomore")
    print(f"  • Completed Courses: {len(ai_advanced['completed_courses'])}")
    print(f"  • Sample: {', '.join(ai_advanced['completed_courses'][:4])}")
    
    plan2 = planner.create_personalized_plan(ai_advanced)
    
    print(f"\nPlan Results:")
    print(f"  • Graduation Date: {plan2.graduation_date}")
    print(f"  • Success Probability: {plan2.success_probability:.0%}")
    print(f"  • Total Semesters: {plan2.total_semesters}")
    
    if plan2.remaining_requirements:
        print(f"  • Remaining Requirements:")
        for req_type, courses in plan2.remaining_requirements.items():
            if courses and len(courses) > 0:
                print(f"    - {req_type.replace('_', ' ').title()}: {len(courses)} courses")
    
    # Demo 3: Show AI major features in knowledge base
    print("\n🧠 DEMO 3: AI Major Knowledge Base Features")
    print("-" * 40)
    
    import json
    with open('data/cs_knowledge_graph.json', 'r') as f:
        knowledge = json.load(f)
    
    if "Artificial Intelligence" in knowledge:
        ai_info = knowledge["Artificial Intelligence"]
        print(f"AI Major Information:")
        print(f"  • Degree Title: {ai_info.get('degree_title', 'N/A')}")
        print(f"  • College: {ai_info.get('college', 'N/A')}")
        print(f"  • Description: {ai_info.get('description', 'N/A')[:80]}...")
        
        if "sample_4_year_plan" in ai_info:
            plan_info = ai_info["sample_4_year_plan"]
            print(f"  • Sample Plan: {len(plan_info)} semesters defined")
            
        if "career_outcomes" in ai_info:
            careers = ai_info["career_outcomes"]
            print(f"  • Career Outcomes: {len(careers)} paths")
            print(f"    - Sample: {careers[0] if careers else 'N/A'}")
            
        if "major_requirements" in ai_info:
            requirements = ai_info["major_requirements"]
            core_cs = requirements.get("core_cs_courses", [])
            print(f"  • Core CS Courses: {len(core_cs)}")
            print(f"    - Sample: {core_cs[0] if core_cs else 'N/A'}")
    
    print("\n🎉 SUMMARY")
    print("-" * 40)
    print("✅ AI major fully integrated with personalized planning!")
    print("✅ Same customization features as CS and Data Science:")
    print("   • Individual progress tracking")
    print("   • Four-year timeline customization") 
    print("   • Course load optimization")
    print("   • Summer course integration")
    print("   • Elective selection guidance")
    print("   • Success probability calculations")
    print("   • Personalized warnings & recommendations")
    print("\n🚀 The AI major is now ready for students!")

if __name__ == "__main__":
    demonstrate_ai_major_planning()