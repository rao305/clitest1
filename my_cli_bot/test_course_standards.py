#!/usr/bin/env python3
"""
Test the course standards module without unicode issues
"""

from course_standards import (
    normalize_course_code,
    get_course_difficulty,
    get_course_prerequisites,
    get_course_hierarchy_text,
    validate_prerequisites
)

def test_course_standards():
    print("Testing Course Standards Module")
    print("="*40)

    # Test course normalization
    test_courses = ["CS 180", "CS 182", "CS 240", "CS 241", "CS 250", "CS 251"]
    print("Course Normalization Tests:")
    for course in test_courses:
        normalized = normalize_course_code(course)
        print(f"  {course} -> {normalized}")

    print(f"\nDifficulty Tests:")
    for course in ["CS 18000", "CS 25100", "CS 25000"]:
        difficulty = get_course_difficulty(course)
        print(f"  {course}: {difficulty}")

    print(f"\nPrerequisite Tests:")
    for course in ["CS 18200", "CS 25100", "CS 25200"]:
        prereqs = get_course_prerequisites(course)
        print(f"  {course}: {prereqs}")

    # Test prerequisite validation
    print(f"\nPrerequisite Validation Tests:")
    completed = ["CS 18000", "CS 18200", "CS 24000"]
    for course in ["CS 25000", "CS 25100", "CS 25200"]:
        can_take, missing = validate_prerequisites(course, completed)
        print(f"  Can take {course}: {can_take}, Missing: {missing}")

    print(f"\nAll tests completed successfully!")

if __name__ == "__main__":
    test_course_standards()