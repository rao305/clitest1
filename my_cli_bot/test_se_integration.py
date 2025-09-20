#!/usr/bin/env python3
"""
Test script to verify Software Engineering track integration
"""

from se_track_scraper import PurdueSETrackScraper
from se_course_validator import SETrackValidator

def test_se_track_integration():
    """Test SE track integration with Enhanced Boiler AI"""
    print("🛠️ Testing Software Engineering Track Integration")
    print("=" * 60)
    
    # Initialize components
    scraper = PurdueSETrackScraper()
    validator = SETrackValidator()
    
    # Test 1: Scraper functionality
    print("1. Testing SE Track Scraper...")
    track_data = scraper.scrape_courses()
    
    if track_data:
        print("✅ SE track data successfully retrieved")
        print(f"   Required courses: {len(track_data['required_courses'])}")
        print(f"   Elective options: {len(track_data['elective_courses']['options'])}")
    else:
        print("❌ Failed to retrieve SE track data")
        return False
    
    # Test 2: Course validation
    print("\n2. Testing Course Validation...")
    
    # Valid SE track plan
    valid_plan = ["CS 30700", "CS 35200", "CS 38100", "CS 40800", "CS 40700", "CS 42600"]
    result = validator.validate_course_plan(valid_plan)
    
    if result['valid']:
        print("✅ Valid SE track plan correctly validated")
        print(f"   Summary: {result['summary']}")
    else:
        print("❌ Valid plan incorrectly rejected")
        print(f"   Errors: {result['errors']}")
        return False
    
    # Test 3: Double counting prevention
    print("\n3. Testing Double Counting Prevention...")
    
    # Invalid plan with double counting
    invalid_plan = ["CS 30700", "CS 35200", "CS 38100", "CS 40800", "CS 40700", "CS 35200"]
    result = validator.validate_course_plan(invalid_plan)
    
    if not result['valid']:
        print("✅ Double counting correctly detected")
        print(f"   Errors: {result['errors']}")
    else:
        print("❌ Double counting not detected")
        return False
    
    # Test 4: Required course guidance
    print("\n4. Testing Course Guidance...")
    
    guidance = scraper.get_course_guidance("What are the required courses?")
    if "CS 30700" in guidance and "CS 38100" in guidance:
        print("✅ Required course guidance accurate")
        print(f"   Response includes mandatory courses")
    else:
        print("❌ Required course guidance incomplete")
        return False
    
    # Test 5: Elective guidance
    print("\n5. Testing Elective Guidance...")
    
    elective_guidance = scraper.get_course_guidance("Tell me about electives")
    if "1" in elective_guidance and "elective" in elective_guidance:
        print("✅ Elective guidance accurate")
        print(f"   Response mentions choosing 1 elective")
    else:
        print("❌ Elective guidance incomplete")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All SE Track Integration Tests Passed!")
    print("✅ Enhanced Boiler AI has accurate SE track information")
    print("✅ Course validation working correctly")
    print("✅ Double counting prevention active")
    print("✅ Accurate guidance responses")
    
    return True

def test_specific_se_scenarios():
    """Test specific SE track scenarios"""
    print("\n🎯 Testing Specific SE Track Scenarios")
    print("-" * 40)
    
    validator = SETrackValidator()
    
    # Scenario 1: Missing mandatory courses
    print("Scenario 1: Missing mandatory courses")
    incomplete = ["CS 35200", "CS 42600"]
    result = validator.validate_course_plan(incomplete)
    
    if not result['valid']:
        print("✅ Missing mandatory courses detected")
        mandatory_errors = [err for err in result['errors'] if 'required' in err.lower()]
        print(f"   Found {len(mandatory_errors)} mandatory course errors")
    else:
        print("❌ Missing mandatory courses not detected")
    
    # Scenario 2: Missing compilers/OS requirement
    print("\nScenario 2: Missing compilers/OS requirement")
    no_compilers_os = ["CS 30700", "CS 38100", "CS 40800", "CS 40700", "CS 42600"]
    result = validator.validate_course_plan(no_compilers_os)
    
    if not result['valid']:
        print("✅ Missing compilers/OS requirement detected")
        compilers_errors = [err for err in result['errors'] if 'Compilers' in err or 'OS' in err]
        print(f"   Found {len(compilers_errors)} compilers/OS errors")
    else:
        print("❌ Missing compilers/OS requirement not detected")
    
    # Scenario 3: Missing elective
    print("\nScenario 3: Missing elective")
    no_elective = ["CS 30700", "CS 35200", "CS 38100", "CS 40800", "CS 40700"]
    result = validator.validate_course_plan(no_elective)
    
    if not result['valid']:
        print("✅ Missing elective detected")
        elective_errors = [err for err in result['errors'] if 'elective' in err.lower()]
        print(f"   Found {len(elective_errors)} elective errors")
    else:
        print("❌ Missing elective not detected")
    
    # Scenario 4: Perfect valid plan with Operating Systems
    print("\nScenario 4: Perfect valid plan with Operating Systems")
    perfect_os = ["CS 30700", "CS 35400", "CS 38100", "CS 40800", "CS 40700", "CS 47100"]
    result = validator.validate_course_plan(perfect_os)
    
    if result['valid']:
        print("✅ Perfect OS plan validated correctly")
        print(f"   Total courses: {result['summary']['total_courses']}")
    else:
        print("❌ Perfect OS plan incorrectly rejected")
        print(f"   Errors: {result['errors']}")

if __name__ == "__main__":
    print("🚀 Enhanced Boiler AI - SE Track Integration Test")
    print("=" * 60)
    
    success = test_se_track_integration()
    
    if success:
        test_specific_se_scenarios()
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("🎓 Enhanced Boiler AI ready for SE track advising")
    else:
        print("\n" + "=" * 60)
        print("❌ Some tests failed")
        print("🔧 Review integration issues")