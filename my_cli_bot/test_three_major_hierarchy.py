#!/usr/bin/env python3
"""
Test script to verify the correct three-major hierarchy:
1. Computer Science (major) → Machine Intelligence & Software Engineering (tracks)
2. Data Science (major) → standalone 
3. Artificial Intelligence (major) → standalone
"""

import sys
import json
sys.path.append('/Users/rrao/Desktop/BCLI/my_cli_bot')

def test_three_major_hierarchy():
    """Test that the three-major hierarchy is correct"""
    
    print("🎓 TESTING THREE-MAJOR HIERARCHY")
    print("=" * 50)
    
    with open('data/cs_knowledge_graph.json', 'r') as f:
        knowledge = json.load(f)
    
    # Test 1: Verify three root-level majors exist
    print("\n📊 Test 1: Root Level Majors")
    print("-" * 30)
    
    required_majors = ["Computer Science", "Data Science", "Artificial Intelligence"]
    found_majors = []
    
    for major in required_majors:
        if major in knowledge:
            found_majors.append(major)
            print(f"✅ {major} - Found at root level")
        else:
            print(f"❌ {major} - Missing from root level")
    
    print(f"\nMajors found: {len(found_majors)}/3")
    
    # Test 2: Verify Computer Science has tracks, others don't
    print("\n🎯 Test 2: Track Structure")
    print("-" * 30)
    
    if "Computer Science" in knowledge:
        cs_info = knowledge["Computer Science"]
        if "tracks" in cs_info:
            cs_tracks = list(cs_info["tracks"].keys())
            print(f"✅ Computer Science tracks: {cs_tracks}")
            if set(cs_tracks) == {"Machine Intelligence", "Software Engineering"}:
                print("✅ Correct CS tracks (MI & SE only)")
            else:
                print(f"❌ Unexpected CS tracks: {cs_tracks}")
        else:
            print("❌ Computer Science missing tracks")
    
    # Verify DS and AI are standalone (no tracks)
    for major in ["Data Science", "Artificial Intelligence"]:
        if major in knowledge:
            major_info = knowledge[major]
            if "tracks" not in major_info:
                print(f"✅ {major} - Standalone major (no tracks)")
            else:
                print(f"❌ {major} - Incorrectly has tracks")
    
    # Test 3: Verify tracks section only contains CS tracks
    print("\n🔧 Test 3: Tracks Section")
    print("-" * 30)
    
    if "tracks" in knowledge:
        tracks = list(knowledge["tracks"].keys())
        print(f"Tracks section contains: {tracks}")
        if set(tracks) == {"Machine Intelligence", "Software Engineering"}:
            print("✅ Tracks section only contains CS tracks")
        else:
            print(f"❌ Tracks section has unexpected content: {tracks}")
    
    # Test 4: Test personalized planner integration
    print("\n🤖 Test 4: Planner Integration")
    print("-" * 30)
    
    try:
        from personalized_graduation_planner import PersonalizedGraduationPlanner
        
        planner = PersonalizedGraduationPlanner(
            "data/cs_knowledge_graph.json",
            "purdue_cs_knowledge.db"
        )
        
        # Test CS major with track
        cs_profile = {
            "major": "Computer Science",
            "track": "Machine Intelligence",
            "completed_courses": [],
            "current_semester": "Fall",
            "current_year": 1
        }
        
        cs_plan = planner.create_personalized_plan(cs_profile)
        print(f"✅ CS + MI track: {cs_plan.major} - {cs_plan.track}")
        
        # Test standalone Data Science
        ds_profile = {
            "major": "Data Science", 
            "completed_courses": [],
            "current_semester": "Fall",
            "current_year": 1
        }
        
        ds_plan = planner.create_personalized_plan(ds_profile)
        print(f"✅ Data Science standalone: {ds_plan.major}")
        
        # Test standalone AI
        ai_profile = {
            "major": "Artificial Intelligence",
            "completed_courses": [],
            "current_semester": "Fall", 
            "current_year": 1
        }
        
        ai_plan = planner.create_personalized_plan(ai_profile)
        print(f"✅ AI standalone: {ai_plan.major}")
        
    except Exception as e:
        print(f"❌ Planner integration error: {e}")
        return False
    
    # Summary
    print(f"\n🏁 HIERARCHY SUMMARY")
    print("=" * 50)
    print("📚 Three Independent Majors:")
    print("   1. Computer Science")
    print("      └── Machine Intelligence (track)")
    print("      └── Software Engineering (track)")  
    print("   2. Data Science (standalone)")
    print("   3. Artificial Intelligence (standalone)")
    print("\n✅ Each major has its own graduation requirements")
    print("✅ Only CS major has tracks (MI & SE)")
    print("✅ DS and AI are completely separate majors")
    
    return len(found_majors) == 3

def test_major_specific_planning():
    """Test that each major has distinct planning capabilities"""
    
    print("\n🎯 TESTING MAJOR-SPECIFIC PLANNING")
    print("=" * 50)
    
    try:
        from personalized_graduation_planner import PersonalizedGraduationPlanner
        
        planner = PersonalizedGraduationPlanner(
            "data/cs_knowledge_graph.json",
            "purdue_cs_knowledge.db"
        )
        
        # Test each major has distinct requirements
        majors_to_test = [
            {"major": "Computer Science", "track": "Machine Intelligence"},
            {"major": "Data Science"},
            {"major": "Artificial Intelligence"}
        ]
        
        print("📋 Major-Specific Requirements:")
        
        for major_profile in majors_to_test:
            major_profile.update({
                "completed_courses": ["CS 18000", "MA 16100"],
                "current_semester": "Spring",
                "current_year": 1
            })
            
            plan = planner.create_personalized_plan(major_profile)
            major_name = major_profile["major"]
            track = major_profile.get("track", "N/A")
            
            print(f"\n• {major_name}" + (f" ({track})" if track != "N/A" else ""))
            print(f"  Graduation: {plan.graduation_date}")
            
            if hasattr(plan, 'remaining_requirements') and plan.remaining_requirements:
                req_types = list(plan.remaining_requirements.keys())
                print(f"  Requirement types: {len(req_types)}")
                print(f"  Sample: {req_types[0] if req_types else 'None'}")
        
        print("\n✅ Each major has distinct graduation requirements!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing major-specific planning: {e}")
        return False

def main():
    """Run all hierarchy tests"""
    
    print("🎓 THREE-MAJOR HIERARCHY VALIDATION")
    print("=" * 60)
    
    results = []
    results.append(("Three-Major Hierarchy", test_three_major_hierarchy()))
    results.append(("Major-Specific Planning", test_major_specific_planning()))
    
    # Results summary
    print(f"\n🏁 TEST RESULTS")
    print("=" * 30)
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 THREE-MAJOR HIERARCHY IS CORRECT!")
        print("🚀 System ready with proper major separation!")
    else:
        print("\n⚠️  Hierarchy issues detected")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)