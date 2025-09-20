#!/usr/bin/env python3
"""
Simple test for Data Science CS Electives data
Tests if the knowledge base contains the electives information
"""

import json

def test_data_science_electives_data():
    """Test if Data Science CS electives data is properly loaded"""
    print("🔍 Testing Data Science CS Electives Data")
    print("=" * 50)
    
    try:
        # Load knowledge graph
        with open("data/cs_knowledge_graph.json", "r") as f:
            knowledge_graph = json.load(f)
        
        # Check if Data Science section exists
        if "tracks" in knowledge_graph and "Data Science" in knowledge_graph["tracks"]:
            ds_section = knowledge_graph["tracks"]["Data Science"]
            print("✅ Data Science section found in knowledge graph")
            
            # Check if CS electives requirement exists
            if "cs_electives_requirement" in ds_section:
                electives_req = ds_section["cs_electives_requirement"]
                print("✅ CS electives requirement found")
                
                print(f"   📚 Total credits required: {electives_req['total_credits_required']}")
                print(f"   📖 Courses to choose: {electives_req['courses_to_choose']}")
                print(f"   🎯 Minimum grade: {electives_req['minimum_grade']}")
                print(f"   📝 Description: {electives_req['description']}")
                print(f"   📋 Available courses: {len(electives_req['available_courses'])}")
                
                # List some example courses
                print("\n📚 Example CS Electives Available:")
                for i, course in enumerate(electives_req['available_courses'][:5]):
                    print(f"   {i+1}. {course['code']} - {course['title']} ({course['credits']} credits)")
                    print(f"      {course['description'][:80]}...")
                
                # Show selection guidance
                if "selection_guidance" in electives_req:
                    print("\n🎯 Selection Guidance:")
                    guidance = electives_req['selection_guidance']
                    for focus, courses in guidance.items():
                        print(f"   {focus}: {', '.join(courses)}")
                
                print("\n✅ All Data Science CS electives data is properly loaded!")
                return True
            else:
                print("❌ CS electives requirement not found in Data Science section")
                return False
        else:
            print("❌ Data Science section not found in knowledge graph")
            return False
            
    except FileNotFoundError:
        print("❌ Knowledge graph file not found")
        return False
    except json.JSONDecodeError:
        print("❌ Invalid JSON in knowledge graph file")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_specific_elective_courses():
    """Test if specific elective courses are in the data"""
    print("\n🔍 Testing Specific CS Elective Courses")
    print("=" * 50)
    
    try:
        with open("data/cs_knowledge_graph.json", "r") as f:
            knowledge_graph = json.load(f)
        
        ds_section = knowledge_graph["tracks"]["Data Science"]
        available_courses = ds_section["cs_electives_requirement"]["available_courses"]
        
        # Check for specific courses mentioned in the user's requirements
        expected_courses = [
            "CS 31100", "CS 41100", "CS 31400", "CS 35500", "CS 43900",
            "CS 45800", "CS 47100", "CS 47300", "CS 47500", "CS 30700",
            "CS 40800", "CS 34800", "CS 44800", "CS 38100", "CS 48300"
        ]
        
        found_courses = []
        missing_courses = []
        
        course_codes = [course['code'] for course in available_courses]
        
        for expected_course in expected_courses:
            if expected_course in course_codes:
                found_courses.append(expected_course)
            else:
                missing_courses.append(expected_course)
        
        print(f"✅ Found {len(found_courses)}/{len(expected_courses)} expected courses")
        print(f"   Found: {', '.join(found_courses)}")
        
        if missing_courses:
            print(f"❌ Missing: {', '.join(missing_courses)}")
            return False
        else:
            print("✅ All expected CS elective courses are present!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Data Science CS Electives Data Test")
    print("=" * 60)
    
    test1_success = test_data_science_electives_data()
    test2_success = test_specific_elective_courses()
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    if test1_success and test2_success:
        print("🎉 All tests passed! Data Science CS electives data is complete and correct.")
    else:
        print("⚠️ Some tests failed. Data may be incomplete.")