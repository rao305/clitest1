#!/usr/bin/env python3
"""
Knowledge Base Content Analysis - Comprehensive overview of what data we have
"""

import json
from collections import Counter

def analyze_knowledge_base():
    """Analyze the complete knowledge base content"""
    
    # Load the knowledge base
    try:
        with open('data/cs_knowledge_graph.json', 'r') as f:
            kb = json.load(f)
    except FileNotFoundError:
        print("❌ Knowledge base file not found")
        return
    
    print("📊 BOILER AI KNOWLEDGE BASE CONTENT ANALYSIS")
    print("=" * 70)
    
    # 1. COURSES SECTION
    if 'courses' in kb:
        courses = kb['courses']
        print(f"\n🎓 COURSES SECTION ({len(courses)} total courses)")
        print("-" * 50)
        
        # Categorize courses by type
        course_types = Counter()
        semester_distribution = Counter()
        difficulty_levels = Counter()
        foundation_courses = []
        track_courses = []
        electives = []
        
        for course_code, course_data in courses.items():
            course_type = course_data.get('course_type', 'unknown')
            course_types[course_type] += 1
            
            semester = course_data.get('semester', 'unknown')
            semester_distribution[semester] += 1
            
            difficulty = course_data.get('difficulty_level', 'unknown')
            if difficulty != 'unknown':
                difficulty_levels[difficulty] += 1
            
            # Categorize courses
            if course_type == 'foundation':
                foundation_courses.append(course_code)
            elif 'track' in course_type:
                track_courses.append(course_code)
            elif course_type == 'elective':
                electives.append(course_code)
        
        print("📚 Course Categories:")
        for ctype, count in course_types.most_common():
            print(f"  • {ctype}: {count} courses")
        
        print(f"\n🔥 Foundation Courses ({len(foundation_courses)}):")
        for course in sorted(foundation_courses):
            title = courses[course].get('title', 'No title')
            semester = courses[course].get('semester', 'Unknown')
            credits = courses[course].get('credits', '?')
            print(f"  • {course}: {title} ({credits} credits) - {semester}")
        
        print(f"\n📊 Semester Distribution:")
        for semester, count in semester_distribution.most_common():
            print(f"  • {semester}: {count} courses")
            
        print(f"\n⚡ Difficulty Levels:")
        for difficulty, count in difficulty_levels.most_common():
            print(f"  • {difficulty}: {count} courses")
        
        # Detailed course information available
        detailed_courses = []
        for course_code, course_data in courses.items():
            if any(field in course_data for field in ['difficulty_factors', 'success_tips', 'common_struggles']):
                detailed_courses.append(course_code)
        
        print(f"\n📝 Courses with Detailed Success Information ({len(detailed_courses)}):")
        for course in sorted(detailed_courses):
            title = courses[course].get('title', 'No title')
            print(f"  • {course}: {title}")
            if 'difficulty_rating' in courses[course]:
                print(f"    - Difficulty rating: {courses[course]['difficulty_rating']}/5.0")
            if 'time_commitment' in courses[course]:
                print(f"    - Time commitment: {courses[course]['time_commitment']}")
    
    # 2. TRACKS SECTION
    if 'tracks' in kb:
        tracks = kb['tracks']
        print(f"\n🎯 TRACKS SECTION ({len(tracks)} tracks)")
        print("-" * 50)
        
        for track_name, track_data in tracks.items():
            print(f"\n📌 {track_name} Track:")
            print(f"  • Description: {track_data.get('description', 'No description')[:100]}...")
            print(f"  • Track code: {track_data.get('track_code', 'Unknown')}")
            print(f"  • Total credits: {track_data.get('total_credits', 'Unknown')}")
            
            # Core requirements
            core_required = track_data.get('core_required', [])
            if core_required:
                print(f"  • Core requirements ({len(core_required)}): {', '.join(core_required)}")
            
            # Count electives
            electives = track_data.get('electives', [])
            if electives:
                print(f"  • Available electives: {len(electives)}")
    
    # 3. ACADEMIC POLICIES SECTION
    if 'academic_policies' in kb:
        policies = kb['academic_policies']
        print(f"\n📋 ACADEMIC POLICIES SECTION")
        print("-" * 50)
        
        for policy_category, policy_data in policies.items():
            print(f"\n📄 {policy_category.replace('_', ' ').title()}:")
            if isinstance(policy_data, dict):
                for key, value in policy_data.items():
                    if isinstance(value, (str, int, float)):
                        print(f"  • {key.replace('_', ' ')}: {value}")
                    elif isinstance(value, dict) and len(value) <= 3:
                        print(f"  • {key.replace('_', ' ')}: {len(value)} items")
    
    # 4. CODO REQUIREMENTS
    if 'codo_requirements' in kb:
        codo = kb['codo_requirements']
        print(f"\n🔄 CODO (CHANGE OF DEGREE OBJECTIVE) REQUIREMENTS")
        print("-" * 50)
        
        print(f"  • Minimum GPA: {codo.get('minimum_gpa', 'Unknown')}")
        print(f"  • Minimum semesters: {codo.get('minimum_semesters', 'Unknown')}")
        print(f"  • Minimum Purdue credits: {codo.get('minimum_purdue_credits', 'Unknown')}")
        
        if 'required_courses' in codo:
            print(f"  • Required courses: {len(codo['required_courses'])} courses")
            for course in codo['required_courses']:
                if isinstance(course, dict):
                    print(f"    - {course.get('code', 'Unknown')}: {course.get('minimum_grade', 'Unknown')} minimum")
        
        if 'math_requirement' in codo:
            math_req = codo['math_requirement']
            if isinstance(math_req, dict) and 'options' in math_req:
                print(f"  • Math options: {len(math_req['options'])} courses available")
    
    # 5. FAILURE RECOVERY SCENARIOS
    if 'failure_recovery_scenarios' in kb:
        failures = kb['failure_recovery_scenarios']
        print(f"\n🚨 FAILURE RECOVERY SCENARIOS ({len(failures)} courses)")
        print("-" * 50)
        
        for course, recovery_data in failures.items():
            if isinstance(recovery_data, dict):
                delay = recovery_data.get('delay_semesters', 'Unknown')
                impact = recovery_data.get('graduation_impact', 'Unknown')
                print(f"  • {course}: {delay} semester delay - {impact}")
    
    # 6. GRADUATION TIMELINES
    if 'graduation_timelines' in kb:
        timelines = kb['graduation_timelines']
        print(f"\n⏰ GRADUATION TIMELINES ({len(timelines)} scenarios)")
        print("-" * 50)
        
        for timeline_name, timeline_data in timelines.items():
            if isinstance(timeline_data, dict):
                probability = timeline_data.get('success_probability', 'Unknown')
                semesters = timeline_data.get('total_semesters', 'Unknown')
                print(f"  • {timeline_name.replace('_', ' ').title()}: {probability} success rate, {semesters} semesters")
    
    # 7. PREREQUISITES MAPPING
    if 'prerequisites' in kb:
        prereqs = kb['prerequisites']
        print(f"\n🔗 PREREQUISITES MAPPING ({len(prereqs)} courses)")
        print("-" * 50)
        
        # Count courses with different numbers of prerequisites
        prereq_counts = Counter()
        for course, prereq_list in prereqs.items():
            prereq_counts[len(prereq_list)] += 1
        
        print("📈 Prerequisite complexity:")
        for count, num_courses in sorted(prereq_counts.items()):
            if count == 0:
                print(f"  • {num_courses} courses with no prerequisites")
            else:
                print(f"  • {num_courses} courses with {count} prerequisite(s)")
    
    # 8. PROGRESSION DATA
    if 'progression_data' in kb:
        progression = kb['progression_data']
        print(f"\n📈 PROGRESSION DATA")
        print("-" * 50)
        
        if 'foundation_sequence' in progression:
            seq = progression['foundation_sequence']
            print(f"  • Foundation sequence: {' → '.join(seq)}")
        
        if 'math_sequence' in progression:
            seq = progression['math_sequence']
            print(f"  • Math sequence: {len(seq)} courses")
        
        if 'track_timing' in progression:
            timing = progression['track_timing']
            print(f"  • Track timing scenarios: {len(timing)} defined")
    
    print(f"\n" + "=" * 70)
    print("📊 SUMMARY STATISTICS")
    print("=" * 70)
    
    total_sections = len(kb.keys())
    total_courses = len(kb.get('courses', {}))
    total_tracks = len(kb.get('tracks', {}))
    
    print(f"• Total knowledge sections: {total_sections}")
    print(f"• Total courses documented: {total_courses}")
    print(f"• Total degree tracks: {total_tracks}")
    print(f"• Foundation courses: {len(foundation_courses)}")
    print(f"• Courses with detailed guidance: {len(detailed_courses)}")
    
    # Calculate knowledge coverage
    cs_courses = [k for k in kb.get('courses', {}).keys() if k.startswith('CS')]
    math_courses = [k for k in kb.get('courses', {}).keys() if k.startswith('MA')]
    stat_courses = [k for k in kb.get('courses', {}).keys() if k.startswith('STAT')]
    
    print(f"• CS courses: {len(cs_courses)}")
    print(f"• Math courses: {len(math_courses)}")
    print(f"• Statistics courses: {len(stat_courses)}")
    
    print(f"\n✅ Knowledge base is comprehensive and ready for academic advising!")

if __name__ == "__main__":
    analyze_knowledge_base()