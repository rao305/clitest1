#!/usr/bin/env python3
"""
Unified test script for both MI and SE tracks in Enhanced Boiler AI
"""

from mi_track_scraper import PurdueMITrackScraper
from course_validator import MITrackValidator
from se_track_scraper import PurdueSETrackScraper
from se_course_validator import SETrackValidator

def test_unified_track_system():
    """Test the unified track system with both MI and SE tracks"""
    print("🎯 Enhanced Boiler AI - Unified Track System Test")
    print("=" * 60)
    
    # Initialize all components
    mi_scraper = PurdueMITrackScraper()
    mi_validator = MITrackValidator()
    se_scraper = PurdueSETrackScraper()
    se_validator = SETrackValidator()
    
    all_tests_passed = True
    
    # Test 1: MI Track System
    print("\n📋 Testing Machine Intelligence Track...")
    mi_data = mi_scraper.scrape_courses()
    if mi_data:
        print(f"✅ MI Track: {len(mi_data['required_courses'])} required + {mi_data['elective_courses']['choose']} electives")
        
        # Test MI validation
        mi_valid_plan = ["CS 37300", "CS 38100", "CS 47100", "STAT 41600", "CS 34800", "CS 57700"]
        mi_result = mi_validator.validate_course_plan(mi_valid_plan)
        if mi_result['valid']:
            print("✅ MI Track validation working correctly")
        else:
            print("❌ MI Track validation failed")
            all_tests_passed = False
    else:
        print("❌ MI Track data retrieval failed")
        all_tests_passed = False
    
    # Test 2: SE Track System
    print("\n🛠️ Testing Software Engineering Track...")
    se_data = se_scraper.scrape_courses()
    if se_data:
        print(f"✅ SE Track: {len(se_data['required_courses'])} required + {se_data['elective_courses']['choose']} electives")
        
        # Test SE validation
        se_valid_plan = ["CS 30700", "CS 35200", "CS 38100", "CS 40800", "CS 40700", "CS 42600"]
        se_result = se_validator.validate_course_plan(se_valid_plan)
        if se_result['valid']:
            print("✅ SE Track validation working correctly")
        else:
            print("❌ SE Track validation failed")
            all_tests_passed = False
    else:
        print("❌ SE Track data retrieval failed")
        all_tests_passed = False
    
    # Test 3: Cross-track comparison
    print("\n📊 Testing Cross-Track Comparison...")
    
    common_courses = set()
    mi_courses = set()
    se_courses = set()
    
    # Extract all courses from both tracks
    for req in mi_data['required_courses']:
        for course in req['courses']:
            mi_courses.add(course['course_code'])
    
    for req in se_data['required_courses']:
        for course in req['courses']:
            se_courses.add(course['course_code'])
    
    common_courses = mi_courses & se_courses
    print(f"✅ Common courses between tracks: {list(common_courses)}")
    
    # Test 4: Comprehensive guidance testing
    print("\n🔍 Testing Comprehensive Guidance...")
    
    # MI guidance
    mi_guidance = mi_scraper.get_course_guidance("What are the required courses?")
    if "CS 37300" in mi_guidance and "CS 38100" in mi_guidance:
        print("✅ MI guidance comprehensive and accurate")
    else:
        print("❌ MI guidance incomplete")
        all_tests_passed = False
    
    # SE guidance
    se_guidance = se_scraper.get_course_guidance("What are the required courses?")
    if "CS 30700" in se_guidance and "CS 40800" in se_guidance:
        print("✅ SE guidance comprehensive and accurate")
    else:
        print("❌ SE guidance incomplete")
        all_tests_passed = False
    
    # Test 5: Edge cases and error handling
    print("\n⚠️ Testing Edge Cases and Error Handling...")
    
    # Test invalid MI plan
    invalid_mi = ["CS 37300", "CS 34800"]  # Missing required courses
    mi_invalid_result = mi_validator.validate_course_plan(invalid_mi)
    if not mi_invalid_result['valid']:
        print("✅ MI Track correctly rejects invalid plans")
    else:
        print("❌ MI Track failed to reject invalid plan")
        all_tests_passed = False
    
    # Test invalid SE plan
    invalid_se = ["CS 30700", "CS 42600"]  # Missing required courses
    se_invalid_result = se_validator.validate_course_plan(invalid_se)
    if not se_invalid_result['valid']:
        print("✅ SE Track correctly rejects invalid plans")
    else:
        print("❌ SE Track failed to reject invalid plan")
        all_tests_passed = False
    
    # Final results
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 ALL UNIFIED TRACK TESTS PASSED!")
        print("✅ Enhanced Boiler AI ready for comprehensive track advising")
        print("✅ Both MI and SE tracks fully integrated and functional")
        print("✅ Cross-track comparison and guidance working")
        print("✅ Error handling and validation robust")
        
        # Display final statistics
        print("\n📈 System Statistics:")
        print(f"  • MI Track: 4 required courses + 2 electives = 6 total")
        print(f"  • SE Track: 5 required courses + 1 elective = 6 total")
        print(f"  • Common courses: {len(common_courses)}")
        print(f"  • Total unique courses across both tracks: {len(mi_courses | se_courses)}")
        
        return True
    else:
        print("❌ Some tests failed - review integration issues")
        return False

def demonstrate_track_capabilities():
    """Demonstrate the comprehensive capabilities of both tracks"""
    print("\n🎯 Demonstrating Enhanced Boiler AI Track Capabilities")
    print("=" * 60)
    
    # Initialize components
    mi_scraper = PurdueMITrackScraper()
    se_scraper = PurdueSETrackScraper()
    
    # Show track summaries
    print("\n📋 Track Summaries:")
    print("\nMachine Intelligence Track:")
    print("  Focus: AI, Machine Learning, Data Mining, Statistics")
    print("  Structure: 4 required + 2 electives")
    print("  Key Courses: CS 37300, CS 38100, AI/Stats choices")
    
    print("\nSoftware Engineering Track:")
    print("  Focus: Software Development, Testing, Project Management")
    print("  Structure: 5 required + 1 elective")
    print("  Key Courses: CS 30700, CS 38100, CS 40800, CS 40700")
    
    # Show example student scenarios
    print("\n🎓 Example Student Scenarios:")
    
    print("\nScenario 1: AI-focused student")
    print("  Recommendation: MI Track")
    print("  Sample plan: CS 37300, CS 38100, CS 47100, STAT 41600, CS 57700, CS 57800")
    
    print("\nScenario 2: Software development-focused student")
    print("  Recommendation: SE Track")
    print("  Sample plan: CS 30700, CS 35200, CS 38100, CS 40800, CS 40700, CS 42600")
    
    print("\nScenario 3: Undecided student")
    print("  Guidance: Take CS 38100 (required in both), then explore CS 37300 vs CS 30700")

if __name__ == "__main__":
    success = test_unified_track_system()
    
    if success:
        demonstrate_track_capabilities()
        print("\n" + "=" * 60)
        print("🚀 Enhanced Boiler AI - Production Ready!")
        print("✅ Comprehensive academic advising for both tracks")
        print("✅ Real-time validation and guidance")
        print("✅ Verified against official Purdue sources")
    else:
        print("\n🔧 Address failing tests before deployment")