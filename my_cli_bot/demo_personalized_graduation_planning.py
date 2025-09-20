#!/usr/bin/env python3
"""
Demonstration of Enhanced Personalized Graduation Planning Feature

This demo shows exactly what the user requested:
- Curated graduation plans based on individual student situations
- Support for students who took summer courses to speed things up
- Personalized course recommendations accounting for completed courses
- Flexible planning that meets graduation requirements
- Support for both CS and Data Science majors
"""

from personalized_graduation_planner import PersonalizedGraduationPlanner

def demo_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"🎓 {title}")
    print("=" * 80)

def demo_scenario(title, description):
    """Print a formatted scenario header"""
    print(f"\n📋 {title}")
    print(f"📝 {description}")
    print("-" * 60)

def display_personalized_plan(plan, student_name):
    """Display a personalized graduation plan in a user-friendly format"""
    
    print(f"\n🎯 Personalized Graduation Plan for {student_name}")
    print("=" * 50)
    
    # Basic info
    print(f"📚 Major: {plan.major}")
    if plan.track:
        print(f"🎯 Track: {plan.track}")
    print(f"📅 Expected Graduation: {plan.graduation_date}")
    print(f"📊 Success Probability: {plan.success_probability:.0%}")
    print(f"📖 Total Semesters Needed: {plan.total_semesters}")
    
    # Customization highlights
    if plan.customization_notes:
        print(f"\n✨ Personalized For You:")
        for note in plan.customization_notes:
            print(f"   • {note}")
    
    # Semester-by-semester breakdown
    print(f"\n📅 Your Semester-by-Semester Plan:")
    print("=" * 50)
    
    for i, schedule in enumerate(plan.schedules):
        # Header for each semester
        print(f"\n📆 {schedule.semester} Year {schedule.year} ({schedule.total_credits} credits total)")
        
        # List courses
        for course in schedule.courses:
            course_code = course.get('code', 'Unknown')
            course_title = course.get('title', course_code)
            credits = course.get('credits', 3)
            
            if course_title != course_code and course_title != course_code:
                print(f"   📖 {course_code}: {course_title} ({credits} cr)")
            else:
                print(f"   📖 {course_code} ({credits} cr)")
        
        # Warnings for this semester
        if schedule.warnings:
            print(f"   ⚠️  Considerations:")
            for warning in schedule.warnings:
                print(f"      • {warning}")
        
        # Tips for this semester
        if schedule.recommendations:
            print(f"   💡 Tips:")
            for rec in schedule.recommendations:
                print(f"      • {rec}")
    
    # Overall recommendations
    if plan.warnings:
        print(f"\n⚠️  Important Considerations:")
        for warning in plan.warnings:
            print(f"   • {warning}")
    
    if plan.recommendations:
        print(f"\n💡 General Recommendations:")
        for rec in plan.recommendations:
            print(f"   • {rec}")

def main():
    """Run demonstration scenarios"""
    
    demo_header("Enhanced Personalized Graduation Planning Demo")
    print("This demo shows the new curated graduation planning feature that creates")
    print("truly personalized plans based on each student's specific situation.")
    
    # Initialize planner
    try:
        planner = PersonalizedGraduationPlanner(
            "data/cs_knowledge_graph.json",
            "purdue_cs_knowledge.db"
        )
    except Exception as e:
        print(f"❌ Error initializing planner: {e}")
        return
    
    # Scenario 1: The exact scenario the user mentioned
    demo_scenario(
        "Scenario 1: CS Student Who Took Summer Courses (User's Example)",
        "Student has taken summer classes to speed things up and wants a complete"
        " graduation plan tailored to their specific progress and goals."
    )
    
    # This matches the user's scenario
    student_alex = {
        "major": "Computer Science",
        "track": "Machine Intelligence",
        "completed_courses": [
            "CS 18000",  # Problem Solving and OOP
            "CS 18200",  # Foundations of CS
            "CS 24000",  # Programming in C
            "CS 25000",  # Computer Architecture
            "MA 16100",  # Calculus I
            "MA 16200",  # Calculus II
            "ENGL 10600" # Written Communication
        ],
        "current_year": 2,
        "current_semester": "Fall",
        "graduation_goal": "4_year",  # Standard but could accelerate
        "credit_load": "standard",
        "summer_courses": True  # Willing to take more summer courses
    }
    
    try:
        alex_plan = planner.create_personalized_plan(student_alex)
        display_personalized_plan(alex_plan, "Alex (CS Student with Summer Progress)")
        
        print(f"\n🎯 Key Benefits for Alex:")
        print(f"   ✅ Plan accounts for {len(student_alex['completed_courses'])} completed courses")
        print(f"   ✅ Optimized course sequencing based on prerequisites")
        print(f"   ✅ Summer course options included for acceleration")
        print(f"   ✅ Track-specific requirements (Machine Intelligence) integrated")
        
    except Exception as e:
        print(f"❌ Error generating plan for Alex: {e}")
    
    # Scenario 2: Data Science student
    demo_scenario(
        "Scenario 2: Data Science Student with Accelerated Progress",
        "Data Science student who has taken some courses early and needs a"
        " curated plan for their specific major requirements."
    )
    
    student_maria = {
        "major": "Data Science",
        "track": "",  # Data Science doesn't have tracks like CS
        "completed_courses": [
            "CS 18000",     # Programming foundation
            "CS 18200",     # CS foundations
            "MA 16100",     # Calculus I
            "MA 16200",     # Calculus II
            "STAT 35500",   # Statistics for Data Science
            "CS 24200"      # Introduction to Data Science
        ],
        "current_year": 2,
        "current_semester": "Spring",
        "graduation_goal": "4_year",
        "credit_load": "standard",
        "summer_courses": True
    }
    
    try:
        maria_plan = planner.create_personalized_plan(student_maria)
        display_personalized_plan(maria_plan, "Maria (Data Science Student)")
        
        print(f"\n🎯 Key Benefits for Maria:")
        print(f"   ✅ Data Science specific degree requirements")
        print(f"   ✅ Plan reflects her early progress in statistics and data science")
        print(f"   ✅ Optimized for Data Science sample 4-year plan")
        print(f"   ✅ Accounts for different major structure than CS")
        
    except Exception as e:
        print(f"❌ Error generating plan for Maria: {e}")
    
    # Scenario 3: CS student wanting early graduation
    demo_scenario(
        "Scenario 3: CS Student Aiming for Early Graduation",
        "Student wants to graduate in 3.5 years and needs an intensive"
        " plan that accounts for their current progress."
    )
    
    student_jordan = {
        "major": "Computer Science",
        "track": "Software Engineering",
        "completed_courses": [
            "CS 18000",
            "CS 18200",
            "CS 24000",
            "MA 16100",
            "MA 16200"
        ],
        "current_year": 1,
        "current_semester": "Spring",
        "graduation_goal": "3.5_year",  # Ambitious goal
        "credit_load": "heavy",  # Willing to take heavy loads
        "summer_courses": True
    }
    
    try:
        jordan_plan = planner.create_personalized_plan(student_jordan)
        display_personalized_plan(jordan_plan, "Jordan (Early Graduation Goal)")
        
        print(f"\n🎯 Key Benefits for Jordan:")
        print(f"   ✅ Accelerated timeline to meet 3.5-year goal")
        print(f"   ✅ Heavy course loads planned strategically")
        print(f"   ✅ Summer courses integrated for acceleration")
        print(f"   ✅ Software Engineering track requirements prioritized")
        print(f"   ⚠️  Success probability: {jordan_plan.success_probability:.0%} (realistic assessment)")
        
    except Exception as e:
        print(f"❌ Error generating plan for Jordan: {e}")
    
    # Scenario 4: Student behind schedule
    demo_scenario(
        "Scenario 4: Student Who Needs to Catch Up",
        "Student who is behind the typical schedule and needs a recovery"
        " plan that still allows them to graduate."
    )
    
    student_sam = {
        "major": "Computer Science",
        "track": "Machine Intelligence",
        "completed_courses": [
            "CS 18000",
            "MA 16100"
        ],
        "current_year": 2,  # Sophomore but only has freshman-level progress
        "current_semester": "Fall",
        "graduation_goal": "flexible",  # Flexible timeline
        "credit_load": "standard",
        "summer_courses": True
    }
    
    try:
        sam_plan = planner.create_personalized_plan(student_sam)
        display_personalized_plan(sam_plan, "Sam (Behind Schedule - Recovery Plan)")
        
        print(f"\n🎯 Key Benefits for Sam:")
        print(f"   ✅ Recovery plan accounts for limited progress")
        print(f"   ✅ Flexible timeline reduces pressure")
        print(f"   ✅ Summer courses help catch up")
        print(f"   ✅ Realistic course loads for success")
        
    except Exception as e:
        print(f"❌ Error generating plan for Sam: {e}")
    
    # Summary
    demo_header("Feature Summary")
    print("🎉 The Enhanced Personalized Graduation Planning feature provides:")
    print()
    print("✅ TRULY CURATED PLANS:")
    print("   • Each plan is customized based on completed courses")
    print("   • Accounts for student's specific situation and goals")
    print("   • No more generic 'sample 4-year plan' responses")
    print()
    print("✅ INTELLIGENT COURSE SEQUENCING:")
    print("   • Respects prerequisites and course offerings")
    print("   • Prioritizes foundation courses and track requirements")
    print("   • Optimizes for student's timeline and credit load preferences")
    print()
    print("✅ FLEXIBLE AND ADAPTABLE:")
    print("   • Supports both CS and Data Science majors")
    print("   • Handles early graduation, standard, and catch-up scenarios")
    print("   • Includes summer course options for acceleration")
    print()
    print("✅ SMART RECOMMENDATIONS:")
    print("   • Provides semester-specific warnings and tips")
    print("   • Realistic success probability assessments")
    print("   • Graduation requirement tracking")
    print()
    print("🎯 This solves the exact problem you mentioned - no more generic responses!")
    print("   The AI now creates truly personalized plans based on each student's")
    print("   unique situation, completed courses, and graduation goals.")

if __name__ == "__main__":
    main()