#!/usr/bin/env python3
"""
Test script to verify CS 18200 failure scenario handling
"""

import os
import json

def test_cs182_query():
    """Test CS 18200 failure query processing"""
    
    # Load knowledge base
    try:
        with open('data/cs_knowledge_graph.json', 'r') as f:
            knowledge_base = json.load(f)
        print("✅ Knowledge base loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load knowledge base: {e}")
        return
    
    # Test course lookup
    course_variations = ["CS 182", "CS 18200", "cs182", "cs 18200"]
    
    print("\n📚 Course Lookup Test:")
    for variation in course_variations:
        # Normalize the course code
        normalized = variation.upper().replace(" ", " ")
        if "CS 182" in normalized:
            normalized = "CS 18200"
        
        if normalized in knowledge_base.get('courses', {}):
            course_info = knowledge_base['courses'][normalized]
            print(f"  {variation} → {normalized}: {course_info.get('title', 'No title')}")
        else:
            print(f"  {variation} → {normalized}: Not found")
    
    # Test failure scenario data
    print("\n🔥 Failure Recovery Data:")
    failure_scenarios = knowledge_base.get('failure_recovery_scenarios', {})
    if 'CS 18200' in failure_scenarios:
        scenario = failure_scenarios['CS 18200']
        print(f"  CS 18200 failure impact: {scenario}")
    else:
        print("  No specific CS 18200 failure scenario found")
    
    # Test prerequisites
    print("\n🔗 Prerequisites Data:")
    prerequisites = knowledge_base.get('prerequisites', {})
    if 'CS 18200' in prerequisites:
        prereqs = prerequisites['CS 18200']
        print(f"  CS 18200 prerequisites: {prereqs}")
    else:
        print("  No CS 18200 prerequisites found")
    
    # Check what CS 18200 is required for
    print("\n➡️ What depends on CS 18200:")
    cs18200_info = knowledge_base.get('courses', {}).get('CS 18200', {})
    print(f"  Course info: {cs18200_info.get('title', 'Not found')}")
    print(f"  Critical: {cs18200_info.get('is_critical', 'Unknown')}")
    
    # Look for courses that require CS 18200
    required_for = []
    for course_code, course_info in knowledge_base.get('courses', {}).items():
        if course_code != 'CS 18200':
            # Check in prerequisites
            course_prereqs = prerequisites.get(course_code, [])
            if isinstance(course_prereqs, list) and 'CS 18200' in course_prereqs:
                required_for.append(course_code)
    
    if required_for:
        print(f"  Required for: {', '.join(required_for)}")
    else:
        print("  Required for: Checking course descriptions...")
        # Look in course descriptions for CS 18200 mentions
        for course_code, course_info in knowledge_base.get('courses', {}).items():
            if 'CS 18200' in str(course_info.get('description', '')):
                print(f"    {course_code} mentions CS 18200 in description")

if __name__ == "__main__":
    print("🧪 Testing CS 182/18200 Failure Scenario")
    print("=" * 50)
    test_cs182_query()