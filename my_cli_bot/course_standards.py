#!/usr/bin/env python3
"""
Centralized course mapping and standards module for Boiler AI
This module provides the single source of truth for course information
"""

from typing import Dict, List, Tuple

# OFFICIAL COURSE MAPPINGS (Source: Purdue CS Knowledge Base)
COURSE_MAPPINGS = {
    # CS Foundation Courses (most critical to get right)
    "CS 180": "CS 18000",  # Problem Solving and Object-Oriented Programming
    "CS180": "CS 18000",
    "cs180": "CS 18000",
    "CS 182": "CS 18200",  # Foundations of Computer Science (NOT alternative to CS 18000)
    "CS182": "CS 18200",
    "cs182": "CS 18200",
    "CS 240": "CS 24000",  # Programming in C
    "CS240": "CS 24000",
    "cs240": "CS 24000",
    "CS 241": "CS 25100",  # Data Structures (NOT CS 24100)
    "CS241": "CS 25100",
    "cs241": "CS 25100",
    "CS 250": "CS 25000",  # Computer Architecture
    "CS250": "CS 25000",
    "cs250": "CS 25000",
    "CS 251": "CS 25100",  # Data Structures (same as CS 241)
    "CS251": "CS 25100",
    "cs251": "CS 25100",
    "CS 252": "CS 25200",  # Systems Programming
    "CS252": "CS 25200",
    "cs252": "CS 25200",

    # Upper Level Courses
    "CS 307": "CS 30700",  # Database Systems
    "CS307": "CS 30700",
    "cs307": "CS 30700",
    "CS 320": "CS 35200",  # Operating Systems (NOT CS 32000)
    "CS320": "CS 35200",
    "cs320": "CS 35200",

    # Math Courses
    "MA 161": "MA 16100",
    "MA161": "MA 16100",
    "MA 162": "MA 16200",
    "MA162": "MA 16200",
    "MA 261": "MA 26100",
    "MA261": "MA 26100",
    "MA 265": "MA 26500",
    "MA265": "MA 26500",
}

# OFFICIAL DIFFICULTY RATINGS (Source: CS Knowledge Base)
DIFFICULTY_RATINGS = {
    "CS 18000": 4.2,  # Hard - Problem Solving and OOP
    "CS 18200": 4.0,  # Hard - Foundations of CS
    "CS 24000": 3.8,  # Moderate-Hard - Programming in C
    "CS 25000": 4.1,  # Hard - Computer Architecture
    "CS 25100": 4.5,  # Very Hard - Data Structures
    "CS 25200": 4.4,  # Very Hard - Systems Programming
    "CS 30700": 3.5,  # Moderate - Database Systems
    "CS 35200": 4.0,  # Hard - Operating Systems
    "CS 37300": 4.2,  # Hard - Data Mining and ML
    "CS 38100": 4.3,  # Very Hard - Algorithms
    "MA 16100": 3.0,  # Moderate - Calculus I
    "MA 16200": 3.5,  # Moderate-Hard - Calculus II
    "MA 26100": 3.8,  # Moderate-Hard - Calculus III
    "MA 26500": 3.6,  # Moderate-Hard - Linear Algebra
}

# OFFICIAL PREREQUISITES (Source: CS Knowledge Base)
PREREQUISITES = {
    # Foundation sequence - CRITICAL PATH
    "CS 18000": [],  # Starting course, no CS prerequisites
    "CS 18200": ["CS 18000", "MA 16100"],  # Requires CS 18000 AND Calc I
    "CS 24000": ["CS 18000"],  # Requires CS 18000
    "CS 25000": ["CS 18200", "CS 24000"],  # Requires BOTH CS 18200 and CS 24000
    "CS 25100": ["CS 18200", "CS 24000"],  # Requires BOTH CS 18200 and CS 24000
    "CS 25200": ["CS 25000", "CS 25100"],  # Requires BOTH CS 25000 and CS 25100

    # Upper level courses
    "CS 30700": ["CS 25200"],  # Database Systems requires Systems Programming
    "CS 35200": ["CS 25100"],  # Operating Systems requires Data Structures
    "CS 37300": ["CS 25100", "STAT 35000"],  # Data Mining requires Data Structures + Stats
    "CS 38100": ["CS 25100"],  # Algorithms requires Data Structures

    # Math sequence
    "MA 16100": [],  # Calc I - no prerequisites
    "MA 16200": ["MA 16100"],  # Calc II requires Calc I
    "MA 26100": ["MA 16200"],  # Calc III requires Calc II
    "MA 26500": ["MA 16200"],  # Linear Algebra requires Calc II
}

# FOUNDATION SEQUENCE (Critical Path)
FOUNDATION_SEQUENCE = [
    "CS 18000",  # Problem Solving and OOP
    "CS 18200",  # Foundations of CS
    "CS 24000",  # Programming in C
    "CS 25000",  # Computer Architecture
    "CS 25100",  # Data Structures
    "CS 25200"   # Systems Programming
]

# COURSE TITLES
COURSE_TITLES = {
    "CS 18000": "Problem Solving and Object-Oriented Programming",
    "CS 18200": "Foundations of Computer Science",
    "CS 24000": "Programming in C",
    "CS 25000": "Computer Architecture",
    "CS 25100": "Data Structures and Algorithms",
    "CS 25200": "Systems Programming",
    "CS 30700": "Database Systems",
    "CS 35200": "Operating Systems",
    "CS 37300": "Data Mining and Machine Learning",
    "CS 38100": "Introduction to the Analysis of Algorithms",
    "MA 16100": "Plane Analytic Geometry and Calculus I",
    "MA 16200": "Plane Analytic Geometry and Calculus II",
    "MA 26100": "Multivariate Calculus",
    "MA 26500": "Linear Algebra",
}

def normalize_course_code(course_code: str) -> str:
    """
    Normalize any course code variation to the official 5-digit format

    Args:
        course_code: Any variation of course code (CS 180, cs182, etc.)

    Returns:
        Official course code (CS 18000) or original if not found
    """
    if not course_code:
        return ""

    # Clean up the input
    course_code = course_code.strip()

    # Direct lookup in mappings
    if course_code in COURSE_MAPPINGS:
        return COURSE_MAPPINGS[course_code]

    # Try case-insensitive lookup
    for key, value in COURSE_MAPPINGS.items():
        if key.lower() == course_code.lower():
            return value

    # Return original if no mapping found (already in correct format)
    return course_code

def get_course_difficulty(course_code: str) -> float:
    """
    Get the official difficulty rating for a course

    Args:
        course_code: Course code (CS 18000, etc.)

    Returns:
        Difficulty rating (1.0-5.0 scale)
    """
    normalized = normalize_course_code(course_code)
    return DIFFICULTY_RATINGS.get(normalized, 3.0)  # Default to moderate

def get_course_prerequisites(course_code: str) -> List[str]:
    """
    Get the official prerequisites for a course

    Args:
        course_code: Course code (CS 18000, etc.)

    Returns:
        List of prerequisite course codes
    """
    normalized = normalize_course_code(course_code)
    return PREREQUISITES.get(normalized, [])

def get_course_title(course_code: str) -> str:
    """
    Get the official title for a course

    Args:
        course_code: Course code (CS 18000, etc.)

    Returns:
        Official course title
    """
    normalized = normalize_course_code(course_code)
    return COURSE_TITLES.get(normalized, "Unknown Course")

def is_foundation_course(course_code: str) -> bool:
    """
    Check if a course is part of the foundation sequence

    Args:
        course_code: Course code (CS 18000, etc.)

    Returns:
        True if course is in foundation sequence
    """
    normalized = normalize_course_code(course_code)
    return normalized in FOUNDATION_SEQUENCE

def get_foundation_sequence() -> List[str]:
    """Get the complete foundation sequence in order"""
    return FOUNDATION_SEQUENCE.copy()

def validate_prerequisites(course_code: str, completed_courses: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate if prerequisites are met for a course

    Args:
        course_code: Course to check prerequisites for
        completed_courses: List of completed course codes

    Returns:
        Tuple of (prerequisites_met, missing_prerequisites)
    """
    normalized_course = normalize_course_code(course_code)
    prerequisites = get_course_prerequisites(normalized_course)

    # Normalize completed courses
    normalized_completed = [normalize_course_code(c) for c in completed_courses]

    missing = [prereq for prereq in prerequisites if prereq not in normalized_completed]

    return len(missing) == 0, missing

def get_course_hierarchy_text() -> str:
    """
    Get the official course hierarchy explanation

    Returns:
        Formatted text explaining the course hierarchy
    """
    text = "**CS Foundation Sequence (Critical Path):**\n"
    text += "CS 18000 → CS 18200 → CS 24000 → CS 25000/25100 → CS 25200\n\n"

    text += "**Detailed Prerequisites:**\n"
    text += "• CS 18000: No CS prerequisites (starting point)\n"
    text += "• CS 18200: Requires CS 18000 + MA 16100\n"
    text += "• CS 24000: Requires CS 18000\n"
    text += "• CS 25000: Requires CS 18200 + CS 24000\n"
    text += "• CS 25100: Requires CS 18200 + CS 24000\n"
    text += "• CS 25200: Requires CS 25000 + CS 25100\n\n"

    text += "**Important Notes:**\n"
    text += "• CS 18000 and CS 18200 are sequential, not alternatives\n"
    text += "• Both CS 25000 and CS 25100 require completion of CS 18200 AND CS 24000\n"
    text += "• CS 25200 is a bottleneck - requires both CS 25000 and CS 25100\n"
    text += "• Upper-level courses typically require CS 25100 (Data Structures)"

    return text

def fix_legacy_references(text: str) -> str:
    """
    Fix legacy course references in text

    Args:
        text: Text that may contain old course references

    Returns:
        Text with corrected course references
    """
    # Replace old course number references
    for old, new in COURSE_MAPPINGS.items():
        # Only replace if it's a clear course reference
        if " " in old:  # "CS 180" format
            text = text.replace(old, new)

    # Fix common naming issues
    text = text.replace("skip_cs180", "skip_cs18000")
    text = text.replace("CS 180/182", "CS 18000/18200")
    text = text.replace("cs180", "CS 18000")
    text = text.replace("cs182", "CS 18200")

    return text

# Export key functions and data
__all__ = [
    'normalize_course_code',
    'get_course_difficulty',
    'get_course_prerequisites',
    'get_course_title',
    'is_foundation_course',
    'get_foundation_sequence',
    'validate_prerequisites',
    'get_course_hierarchy_text',
    'fix_legacy_references',
    'COURSE_MAPPINGS',
    'DIFFICULTY_RATINGS',
    'PREREQUISITES',
    'FOUNDATION_SEQUENCE',
    'COURSE_TITLES'
]

if __name__ == "__main__":
    # Test the module
    print("Testing Course Standards Module")
    print("="*40)

    # Test course normalization
    test_courses = ["CS 180", "CS 182", "CS 240", "CS 241", "CS 250", "CS 251"]
    print("Course Normalization Tests:")
    for course in test_courses:
        normalized = normalize_course_code(course)
        print(f"  {course} → {normalized}")

    print(f"\nDifficulty Tests:")
    for course in ["CS 18000", "CS 25100", "CS 25000"]:
        difficulty = get_course_difficulty(course)
        print(f"  {course}: {difficulty}")

    print(f"\nPrerequisite Tests:")
    for course in ["CS 18200", "CS 25100", "CS 25200"]:
        prereqs = get_course_prerequisites(course)
        print(f"  {course}: {prereqs}")

    print(f"\nHierarchy Text:")
    print(get_course_hierarchy_text())