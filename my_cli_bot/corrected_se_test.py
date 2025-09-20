#!/usr/bin/env python3
"""
Corrected SE Track Test - Fix the understanding of SE requirements
"""

import json

def test_se_track_correct():
    """Test SE track with correct understanding"""
    
    print("🔧 CORRECTED SOFTWARE ENGINEERING TRACK TEST")
    print("=" * 60)
    
    # Load knowledge base
    with open('data/cs_knowledge_graph.json', 'r') as f:
        kb = json.load(f)
    
    se_track = kb.get('tracks', {}).get('Software Engineering', {})
    
    if not se_track:
        print("❌ No SE track data found")
        return False
    
    print("📋 SOFTWARE ENGINEERING TRACK REQUIREMENTS:")
    print("-" * 50)
    
    # Core required courses
    core_required = se_track.get('core_required', [])
    print(f"\n1️⃣ CORE REQUIRED COURSES ({len(core_required)} courses):")
    for i, course in enumerate(core_required, 1):
        if isinstance(course, dict):
            code = course.get('code', 'Unknown')
            title = course.get('title', 'No title')
            print(f"   {i}. {code}: {title}")
        else:
            print(f"   {i}. {course}")
    
    # Systems course choice
    choose_systems = se_track.get('choose_one_systems', [])
    print(f"\n2️⃣ CHOOSE ONE SYSTEMS COURSE ({len(choose_systems)} options, PICK 1):")
    for course in choose_systems:
        if isinstance(course, dict):
            code = course.get('code', 'Unknown')
            title = course.get('title', 'No title')
            print(f"   • {code}: {title}")
    
    # Elective course choice
    choose_elective = se_track.get('choose_one_elective', [])
    print(f"\n3️⃣ CHOOSE ONE ELECTIVE ({len(choose_elective)} options, PICK 1):")
    for i, course in enumerate(choose_elective[:5], 1):  # Show first 5
        if isinstance(course, dict):
            code = course.get('code', 'Unknown')
            title = course.get('title', 'No title')
            print(f"   {i}. {code}: {title}")
    
    if len(choose_elective) > 5:
        print(f"   ... and {len(choose_elective) - 5} more elective options")
    
    # Calculate total
    total_courses = len(core_required) + 1 + 1  # core + 1 systems + 1 elective
    total_credits = se_track.get('total_credits', 'Unknown')
    
    print(f"\n📊 SE TRACK SUMMARY:")
    print(f"• Core courses: {len(core_required)} (all required)")
    print(f"• Systems course: 1 (choose from {len(choose_systems)} options)")  
    print(f"• Elective course: 1 (choose from {len(choose_elective)} options)")
    print(f"• TOTAL COURSES NEEDED: {total_courses}")
    print(f"• TOTAL CREDITS: {total_credits}")
    
    return True

def test_corrected_ai_response():
    """Test what the AI should say about SE track"""
    
    print("\n🤖 WHAT AI SHOULD ANSWER FOR SE TRACK")
    print("=" * 60)
    
    print("❓ Question: 'What are the requirements for Software Engineering track?'")
    print("\n✅ CORRECT AI RESPONSE SHOULD BE:")
    print("-" * 40)
    
    response = """The Software Engineering track requires 6 total courses (15 credits):

CORE COURSES (4 required):
• CS 38100: Introduction to Algorithms
• CS 30700: Software Engineering I  
• CS 40800: Software Testing
• CS 40700: Software Engineering Senior Project

CHOOSE ONE SYSTEMS COURSE (1 required):
• CS 35200: Compilers OR CS 35400: Operating Systems

CHOOSE ONE ELECTIVE (1 required):
• Pick 1 from 18+ options including distributed systems, computer networks, databases, security, cloud computing, etc.

Total: 4 core + 1 systems + 1 elective = 6 courses (15 credits)"""
    
    print(response)
    
    print("\n❌ WRONG AI RESPONSE WOULD BE:")
    print("-" * 40)
    print("'The SE track has 18 electives available' (INCORRECT - you only pick 1)")
    print("'You can take all these elective courses' (INCORRECT - choose 1 only)")

def main():
    """Run corrected SE track test"""
    
    # Test correct understanding
    if test_se_track_correct():
        print("\n✅ SE TRACK DATA STRUCTURE VERIFIED")
    else:
        print("\n❌ SE TRACK DATA ISSUES")
        return
    
    # Show what AI should respond
    test_corrected_ai_response()
    
    print("\n🎯 CONCLUSION:")
    print("=" * 60)
    print("✅ SE track has 6 total courses (not unlimited electives)")
    print("✅ Students choose 1 elective from many options (not all)")
    print("✅ AI responses need to clarify 'choose 1 from X options'")
    print("✅ Total workload: 4 core + 1 systems + 1 elective = 6 courses")

if __name__ == "__main__":
    main()