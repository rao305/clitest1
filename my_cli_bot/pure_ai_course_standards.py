#!/usr/bin/env python3
"""
Pure AI + Knowledge Base Course Standards Module
Provides ONLY data normalization and KB lookup - NO hardcoded responses
All responses must be AI-generated using this data
"""

from typing import Dict, List, Tuple, Optional

# OFFICIAL COURSE MAPPINGS (Data Only - No Response Templates)
COURSE_MAPPINGS = {
    "CS 180": "CS 18000", "CS180": "CS 18000", "cs180": "CS 18000",
    "CS 182": "CS 18200", "CS182": "CS 18200", "cs182": "CS 18200",
    "CS 240": "CS 24000", "CS240": "CS 24000", "cs240": "CS 24000",
    "CS 241": "CS 25100", "CS241": "CS 25100", "cs241": "CS 25100",
    "CS 250": "CS 25000", "CS250": "CS 25000", "cs250": "CS 25000",
    "CS 251": "CS 25100", "CS251": "CS 25100", "cs251": "CS 25100",
    "CS 252": "CS 25200", "CS252": "CS 25200", "cs252": "CS 25200",
    "CS 307": "CS 30700", "CS307": "CS 30700", "cs307": "CS 30700",
    "CS 320": "CS 35200", "CS320": "CS 35200", "cs320": "CS 35200",
    "MA 161": "MA 16100", "MA161": "MA 16100",
    "MA 162": "MA 16200", "MA162": "MA 16200",
    "MA 261": "MA 26100", "MA261": "MA 26100",
    "MA 265": "MA 26500", "MA265": "MA 26500",
}

# OFFICIAL DIFFICULTY RATINGS (Knowledge Base Data Only)
DIFFICULTY_RATINGS = {
    "CS 18000": 4.2, "CS 18200": 4.0, "CS 24000": 3.8,
    "CS 25000": 4.1, "CS 25100": 4.5, "CS 25200": 4.4,
    "CS 30700": 3.5, "CS 35200": 4.0, "CS 37300": 4.2,
    "CS 38100": 4.3, "MA 16100": 3.0, "MA 16200": 3.5,
    "MA 26100": 3.8, "MA 26500": 3.6,
}

# OFFICIAL PREREQUISITES (Knowledge Base Data Only)
PREREQUISITES = {
    "CS 18000": [],
    "CS 18200": ["CS 18000", "MA 16100"],
    "CS 24000": ["CS 18000"],
    "CS 25000": ["CS 18200", "CS 24000"],
    "CS 25100": ["CS 18200", "CS 24000"],
    "CS 25200": ["CS 25000", "CS 25100"],
    "CS 30700": ["CS 25200"],
    "CS 35200": ["CS 25100"],
    "CS 37300": ["CS 25100", "STAT 35000"],
    "CS 38100": ["CS 25100"],
    "MA 16100": [],
    "MA 16200": ["MA 16100"],
    "MA 26100": ["MA 16200"],
    "MA 26500": ["MA 16200"],
}

# FOUNDATION SEQUENCE (Data Only)
FOUNDATION_SEQUENCE = [
    "CS 18000", "CS 18200", "CS 24000",
    "CS 25000", "CS 25100", "CS 25200"
]

# COURSE TITLES (Data Only)
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
    PURE DATA FUNCTION: Normalize course code to official format
    Returns normalized course code or original if not found
    NO response generation - data only
    """
    if not course_code:
        return ""

    course_code = course_code.strip()

    # Direct lookup
    if course_code in COURSE_MAPPINGS:
        return COURSE_MAPPINGS[course_code]

    # Case-insensitive lookup
    for key, value in COURSE_MAPPINGS.items():
        if key.lower() == course_code.lower():
            return value

    return course_code

def get_course_difficulty(course_code: str) -> float:
    """
    PURE DATA FUNCTION: Get difficulty rating from knowledge base
    Returns float rating or 3.0 default
    NO response generation - data only
    """
    normalized = normalize_course_code(course_code)
    return DIFFICULTY_RATINGS.get(normalized, 3.0)

def get_course_prerequisites(course_code: str) -> List[str]:
    """
    PURE DATA FUNCTION: Get prerequisites from knowledge base
    Returns list of prerequisite course codes
    NO response generation - data only
    """
    normalized = normalize_course_code(course_code)
    return PREREQUISITES.get(normalized, [])

def get_course_title(course_code: str) -> str:
    """
    PURE DATA FUNCTION: Get course title from knowledge base
    Returns official title or "Unknown Course"
    NO response generation - data only
    """
    normalized = normalize_course_code(course_code)
    return COURSE_TITLES.get(normalized, "Unknown Course")

def is_foundation_course(course_code: str) -> bool:
    """
    PURE DATA FUNCTION: Check if course is in foundation sequence
    Returns boolean
    NO response generation - data only
    """
    normalized = normalize_course_code(course_code)
    return normalized in FOUNDATION_SEQUENCE

def get_foundation_sequence() -> List[str]:
    """
    PURE DATA FUNCTION: Get foundation sequence list
    Returns copy of foundation sequence
    NO response generation - data only
    """
    return FOUNDATION_SEQUENCE.copy()

def validate_prerequisites(course_code: str, completed_courses: List[str]) -> Tuple[bool, List[str]]:
    """
    PURE DATA FUNCTION: Validate prerequisites against completed courses
    Returns (prerequisites_met, missing_prerequisites)
    NO response generation - data only
    """
    normalized_course = normalize_course_code(course_code)
    prerequisites = get_course_prerequisites(normalized_course)
    normalized_completed = [normalize_course_code(c) for c in completed_courses]
    missing = [prereq for prereq in prerequisites if prereq not in normalized_completed]
    return len(missing) == 0, missing

def get_prerequisite_data_for_ai(course_code: str) -> Dict:
    """
    PURE DATA FUNCTION: Get structured prerequisite data for AI to use
    Returns dictionary with all relevant data for AI response generation
    NO response generation - data only
    """
    normalized = normalize_course_code(course_code)
    return {
        "course_code": normalized,
        "title": get_course_title(normalized),
        "prerequisites": get_course_prerequisites(normalized),
        "difficulty_rating": get_course_difficulty(normalized),
        "is_foundation": is_foundation_course(normalized),
        "foundation_sequence": get_foundation_sequence(),
    }

def get_course_hierarchy_data() -> Dict:
    """
    PURE DATA FUNCTION: Get all hierarchy data for AI to generate responses
    Returns structured data about course relationships
    NO response generation - data only
    """
    return {
        "foundation_sequence": FOUNDATION_SEQUENCE,
        "all_prerequisites": PREREQUISITES,
        "course_titles": COURSE_TITLES,
        "difficulty_ratings": DIFFICULTY_RATINGS,
        "course_mappings": COURSE_MAPPINGS,
    }

def fix_legacy_course_references(text: str) -> str:
    """
    PURE DATA FUNCTION: Fix old course number references in text
    Returns text with corrected course numbers
    NO response generation - just data correction
    """
    # Only fix clear course references, don't add content
    for old, new in COURSE_MAPPINGS.items():
        if " " in old:  # "CS 180" format
            text = text.replace(old, new)

    # Fix common legacy terms
    text = text.replace("skip_cs180", "skip_cs18000")
    text = text.replace("CS 180/182", "CS 18000/18200")

    return text

# Export only data functions - NO response generators
__all__ = [
    'normalize_course_code',
    'get_course_difficulty',
    'get_course_prerequisites',
    'get_course_title',
    'is_foundation_course',
    'get_foundation_sequence',
    'validate_prerequisites',
    'get_prerequisite_data_for_ai',
    'get_course_hierarchy_data',
    'fix_legacy_course_references',
    'COURSE_MAPPINGS',
    'DIFFICULTY_RATINGS',
    'PREREQUISITES',
    'FOUNDATION_SEQUENCE',
    'COURSE_TITLES'
]

if __name__ == "__main__":
    # Test data functions only - no hardcoded responses
    print("Pure AI Course Standards - Data Functions Only")
    print("="*50)

    # Test normalization
    print("Course Normalization:")
    for course in ["CS 180", "CS 182", "CS 241"]:
        print(f"  {course} -> {normalize_course_code(course)}")

    # Test data retrieval
    print(f"\nData for CS 25100:")
    data = get_prerequisite_data_for_ai("CS 251")
    for key, value in data.items():
        print(f"  {key}: {value}")

    print(f"\nHierarchy data available for AI:")
    hierarchy_data = get_course_hierarchy_data()
    print(f"  Foundation sequence: {hierarchy_data['foundation_sequence']}")
    print(f"  Total courses with prereqs: {len(hierarchy_data['all_prerequisites'])}")

    print("\nNOTE: This module provides ONLY data - AI must generate all responses")