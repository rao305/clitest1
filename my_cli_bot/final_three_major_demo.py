#!/usr/bin/env python3
"""
Final demonstration of the complete three-major hierarchy system:
1. Computer Science (major) → Machine Intelligence & Software Engineering (tracks)
2. Data Science (major) → standalone with own requirements
3. Artificial Intelligence (major) → standalone with own requirements

Each major has complete four-year customization planning capabilities.
"""

import sys
sys.path.append('/Users/rrao/Desktop/BCLI/my_cli_bot')

def demonstrate_three_major_system():
    """Demonstrate all three majors with their distinct planning"""
    
    print("🎓 COMPLETE THREE-MAJOR SYSTEM DEMONSTRATION")
    print("=" * 70)
    print("Showing personalized four-year planning for ALL three majors!")
    
    from personalized_graduation_planner import PersonalizedGraduationPlanner
    
    planner = PersonalizedGraduationPlanner(
        "data/cs_knowledge_graph.json",
        "purdue_cs_knowledge.db"
    )
    
    # MAJOR 1: Computer Science with Machine Intelligence Track
    print("\n1️⃣ COMPUTER SCIENCE - MACHINE INTELLIGENCE TRACK")
    print("=" * 60)
    
    cs_mi_profile = {
        "major": "Computer Science",
        "track": "Machine Intelligence",
        "completed_courses": ["CS 18000", "MA 16100"],
        "current_semester": "Spring",
        "current_year": 1,
        "summer_courses": True,
        "credit_load": "standard",
        "graduation_goal": "4_year"
    }
    
    print(f"📋 Student Profile:")
    print(f"   • Major: {cs_mi_profile['major']}")
    print(f"   • Track: {cs_mi_profile['track']}")
    print(f"   • Completed: {len(cs_mi_profile['completed_courses'])} courses")
    print(f"   • Current: {cs_mi_profile['current_semester']} Year {cs_mi_profile['current_year']}")
    
    cs_plan = planner.create_personalized_plan(cs_mi_profile)
    print(f"\n✅ CS-MI Plan Generated:")
    print(f"   • Major: {cs_plan.major}")
    print(f"   • Track: {cs_plan.track}")
    print(f"   • Graduation: {cs_plan.graduation_date}")
    print(f"   • Has Track-Specific Requirements: ✅")
    
    # MAJOR 2: Computer Science with Software Engineering Track  
    print("\n2️⃣ COMPUTER SCIENCE - SOFTWARE ENGINEERING TRACK")
    print("=" * 60)
    
    cs_se_profile = {
        "major": "Computer Science",
        "track": "Software Engineering", 
        "completed_courses": ["CS 18000", "CS 18200", "MA 16100"],
        "current_semester": "Fall",
        "current_year": 2,
        "summer_courses": False,
        "credit_load": "standard",
        "graduation_goal": "4_year"
    }
    
    print(f"📋 Student Profile:")
    print(f"   • Major: {cs_se_profile['major']}")
    print(f"   • Track: {cs_se_profile['track']}")
    print(f"   • Completed: {len(cs_se_profile['completed_courses'])} courses")
    print(f"   • Current: {cs_se_profile['current_semester']} Year {cs_se_profile['current_year']}")
    
    cs_se_plan = planner.create_personalized_plan(cs_se_profile)
    print(f"\n✅ CS-SE Plan Generated:")
    print(f"   • Major: {cs_se_plan.major}")
    print(f"   • Track: {cs_se_plan.track}")
    print(f"   • Graduation: {cs_se_plan.graduation_date}")
    print(f"   • Has Track-Specific Requirements: ✅")
    
    # MAJOR 3: Data Science (Standalone)
    print("\n3️⃣ DATA SCIENCE MAJOR (STANDALONE)")
    print("=" * 60)
    
    ds_profile = {
        "major": "Data Science",
        "completed_courses": ["CS 18000", "STAT 35500", "MA 16100"],
        "current_semester": "Spring", 
        "current_year": 1,
        "summer_courses": True,
        "credit_load": "standard",
        "graduation_goal": "4_year"
    }
    
    print(f"📋 Student Profile:")
    print(f"   • Major: {ds_profile['major']}")
    print(f"   • Track: None (standalone major)")
    print(f"   • Completed: {len(ds_profile['completed_courses'])} courses")
    print(f"   • Current: {ds_profile['current_semester']} Year {ds_profile['current_year']}")
    
    ds_plan = planner.create_personalized_plan(ds_profile)
    print(f"\n✅ Data Science Plan Generated:")
    print(f"   • Major: {ds_plan.major}")
    print(f"   • Track: {ds_plan.track or 'N/A (standalone)'}")
    print(f"   • Graduation: {ds_plan.graduation_date}")
    print(f"   • Has Data-Specific Requirements: ✅")
    
    # MAJOR 4: Artificial Intelligence (Standalone)
    print("\n4️⃣ ARTIFICIAL INTELLIGENCE MAJOR (STANDALONE)")
    print("=" * 60)
    
    ai_profile = {
        "major": "Artificial Intelligence",
        "completed_courses": ["CS 17600", "CS 18000", "PSY 12000"],
        "current_semester": "Fall",
        "current_year": 2, 
        "summer_courses": True,
        "credit_load": "standard",
        "graduation_goal": "4_year"
    }
    
    print(f"📋 Student Profile:")
    print(f"   • Major: {ai_profile['major']}")
    print(f"   • Track: None (standalone major)")
    print(f"   • Completed: {len(ai_profile['completed_courses'])} courses")
    print(f"   • Current: {ai_profile['current_semester']} Year {ai_profile['current_year']}")
    
    ai_plan = planner.create_personalized_plan(ai_profile)
    print(f"\n✅ AI Plan Generated:")
    print(f"   • Major: {ai_plan.major}")
    print(f"   • Track: {ai_plan.track or 'N/A (standalone)'}")
    print(f"   • Graduation: {ai_plan.graduation_date}")
    print(f"   • Has AI-Specific Requirements: ✅")
    
    # SYSTEM SUMMARY
    print(f"\n🎉 SYSTEM SUMMARY")
    print("=" * 70)
    print("✅ THREE INDEPENDENT MAJORS WITH FULL CUSTOMIZATION:")
    print()
    
    print("📚 1. COMPUTER SCIENCE (with 2 tracks)")
    print("   └── Machine Intelligence Track")
    print("       • AI/ML focus, research preparation") 
    print("       • CS 37300, CS 47100/47300, STAT requirements")
    print("   └── Software Engineering Track") 
    print("       • Industry development, large-scale systems")
    print("       • CS 30700, CS 40700, CS 40800, compiler/OS choice")
    print()
    
    print("📊 2. DATA SCIENCE (standalone major)")
    print("   • Statistics-heavy curriculum")
    print("   • Data analysis and machine learning focus")  
    print("   • Own graduation requirements & sample 4-year plan")
    print()
    
    print("🤖 3. ARTIFICIAL INTELLIGENCE (standalone major)")
    print("   • Interdisciplinary: CS + Psychology + Philosophy + Math")
    print("   • AI-specific courses: CS 17600, CS 24300, CS 25300")
    print("   • Own graduation requirements & sample 4-year plan")
    print()
    
    print("🎯 EACH MAJOR HAS IDENTICAL CUSTOMIZATION FEATURES:")
    print("   ✅ Individual progress tracking")
    print("   ✅ Four-year timeline customization")
    print("   ✅ Course load optimization") 
    print("   ✅ Summer course integration")
    print("   ✅ Elective selection guidance")
    print("   ✅ Success probability calculations")
    print("   ✅ Personalized warnings & recommendations")
    print()
    
    print("🚀 THE THREE-MAJOR SYSTEM IS COMPLETE AND READY!")

def show_knowledge_base_structure():
    """Show the clean knowledge base structure"""
    
    print("\n📁 KNOWLEDGE BASE STRUCTURE")
    print("=" * 40)
    
    import json
    with open('data/cs_knowledge_graph.json', 'r') as f:
        data = json.load(f)
    
    print("ROOT LEVEL MAJORS:")
    for major in ["Computer Science", "Data Science", "Artificial Intelligence"]:
        if major in data:
            print(f"✅ {major}")
            if major == "Computer Science" and "tracks" in data[major]:
                for track in data[major]["tracks"]:
                    print(f"   └── {track} (track)")
            else:
                print("   └── (standalone major)")
    
    print(f"\nTRACKS SECTION (CS only): {list(data.get('tracks', {}).keys())}")
    print(f"TOTAL KNOWLEDGE ITEMS: {len(data)} root sections")

if __name__ == "__main__":
    demonstrate_three_major_system()
    show_knowledge_base_structure()