#!/usr/bin/env python3
"""
Simple test script to verify the conversation fixes are working correctly
"""

import sys
import os

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from course_normalization_fix import normalize_course_code_fixed, get_correct_prerequisite_info

def test_course_normalization():
    """Test that course normalization is working correctly"""
    print("=== Testing Course Normalization Fixes ===")

    test_cases = [
        ("CS 180", "CS 18000"),
        ("CS 182", "CS 18200"),  # This was incorrectly going to CS 18000
        ("CS 240", "CS 24000"),
        ("CS 241", "CS 25100"),  # This was incorrectly going to CS 24100
        ("CS 250", "CS 25000"),
        ("CS 251", "CS 25100"),
        ("CS 252", "CS 25200"),
        ("CS 320", "CS 35200"),  # This was incorrectly going to CS 32000
        ("CS 307", "CS 30700"),
    ]

    all_passed = True
    for input_course, expected in test_cases:
        result = normalize_course_code_fixed(input_course)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            all_passed = False
        print(f"{input_course} -> {result} (expected {expected}) {status}")

    return all_passed

def test_prerequisite_logic():
    """Test that prerequisite logic is correct"""
    print("\n=== Testing Prerequisite Logic ===")

    prereqs = get_correct_prerequisite_info()

    test_cases = [
        ("CS 18000", [], "Starting course"),
        ("CS 18200", ["CS 18000", "MA 16100"], "Requires CS 18000 AND Calc I"),
        ("CS 24000", ["CS 18000"], "Requires CS 18000"),
        ("CS 25000", ["CS 18200", "CS 24000"], "Requires both CS 18200 and CS 24000"),
        ("CS 25100", ["CS 18200", "CS 24000"], "Requires both CS 18200 and CS 24000"),
        ("CS 25200", ["CS 25000", "CS 25100"], "Requires both CS 25000 and CS 25100"),
    ]

    all_passed = True
    for course, expected_prereqs, description in test_cases:
        actual_prereqs = prereqs.get(course, [])
        status = "PASS" if set(actual_prereqs) == set(expected_prereqs) else "FAIL"
        if set(actual_prereqs) != set(expected_prereqs):
            all_passed = False
        print(f"{course}: {actual_prereqs} - {description} {status}")

    return all_passed

def main():
    """Run all tests"""
    print("Testing Boiler AI Conversation Fixes\n")

    norm_passed = test_course_normalization()
    prereq_passed = test_prerequisite_logic()

    print("\n" + "="*50)
    print("SUMMARY:")
    print(f"Course Normalization: {'PASS' if norm_passed else 'FAIL'}")
    print(f"Prerequisite Logic: {'PASS' if prereq_passed else 'FAIL'}")

    if all([norm_passed, prereq_passed]):
        print("\nALL TESTS PASSED! The conversation fixes are working correctly.")
        return 0
    else:
        print("\nSOME TESTS FAILED. The fixes need more work.")
        return 1

if __name__ == "__main__":
    sys.exit(main())