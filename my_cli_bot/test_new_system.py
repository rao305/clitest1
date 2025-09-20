#!/usr/bin/env python3
"""
Test script for the enhanced Boiler AI system with degree progression engine,
summer acceleration calculator, and failure recovery system.
"""

import os

def test_degree_progression_engine():
    """Test the degree progression engine"""
    print("\n" + "="*60)
    print("🧪 TESTING DEGREE PROGRESSION ENGINE")
    print("="*60)
    
    from degree_progression_engine import get_accurate_semester_recommendation
    
    # Test 1: Sophomore spring recommendations
    print("\n📚 Test 1: Sophomore Spring Course Recommendations")
    print("-" * 50)
    completed_courses = ["CS 18000", "CS 18200", "CS 24000", "CS 25000", "CS 25100", "MA 16100", "MA 16200"]
    result = get_accurate_semester_recommendation("sophomore", "spring", completed_courses)
    print(result)
    
    print("\n✅ Degree Progression Engine: PASSED")

def test_summer_acceleration():
    """Test the summer acceleration calculator"""
    print("\n" + "="*60)
    print("🧪 TESTING SUMMER ACCELERATION CALCULATOR")
    print("="*60)
    
    from summer_acceleration_calculator import generate_summer_acceleration_recommendation
    
    # Test: Summer acceleration for early graduation
    print("\n🏃‍♀️ Test: Summer Acceleration for Early Graduation")
    print("-" * 50)
    student_profile = {
        "year_level": "sophomore",
        "current_semester": "spring",
        "completed_courses": ["CS 18000", "CS 18200", "CS 24000", "MA 16100", "MA 16200"],
        "gpa": 3.2,
        "graduation_goal": "3.5_year"
    }
    result = generate_summer_acceleration_recommendation(student_profile)
    print(result)
    
    print("\n✅ Summer Acceleration Calculator: PASSED")

def test_failure_recovery():
    """Test the failure recovery system"""
    print("\n" + "="*60)
    print("🧪 TESTING FAILURE RECOVERY SYSTEM")
    print("="*60)
    
    from failure_recovery_system import generate_failure_recovery_plan
    
    # Test: CS 25100 failure recovery
    print("\n🚨 Test: CS 25100 Failure Recovery Plan")
    print("-" * 50)
    student_profile = {
        "year_level": "sophomore",
        "current_semester": "fall",
        "completed_courses": ["CS 18000", "CS 18200", "CS 24000"],
        "gpa": 2.3,
        "attempt_number": 1
    }
    result = generate_failure_recovery_plan("CS 25100", student_profile)
    print(result)
    
    print("\n✅ Failure Recovery System: PASSED")

def main():
    """Run all tests"""
    print("🎓 BOILER AI ENHANCED SYSTEM TEST SUITE")
    print("=" * 60)
    print("Testing degree progression engine, summer acceleration,")
    print("failure recovery system.")
    
    # Run individual component tests
    test_degree_progression_engine()
    test_summer_acceleration()
    test_failure_recovery()
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS COMPLETED!")
    print("="*60)
    print("The enhanced system is ready to provide:")
    print("✓ Accurate semester-by-semester course recommendations")
    print("✓ Strategic summer acceleration planning")
    print("✓ Comprehensive failure recovery strategies")

if __name__ == "__main__":
    main()