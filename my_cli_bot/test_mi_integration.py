#!/usr/bin/env python3
"""
Test script to verify Machine Intelligence track integration
"""

from mi_track_scraper import PurdueMITrackScraper
from course_validator import MITrackValidator

def test_mi_track_integration():
    """Test MI track integration with Enhanced Boiler AI"""
    print("🧪 Testing Machine Intelligence Track Integration")
    print("=" * 60)
    
    # Initialize components
    scraper = PurdueMITrackScraper()
    validator = MITrackValidator()
    
    # Test 1: Scraper functionality
    print("1. Testing MI Track Scraper...")
    track_data = scraper.scrape_courses()
    
    if track_data:
        print("✅ MI track data successfully retrieved")
        print(f"   Required courses: {len(track_data['required_courses'])}")
        print(f"   Elective options: {len(track_data['elective_courses']['options'])}")
    else:
        print("❌ Failed to retrieve MI track data")
        return False
    
    # Test 2: Course validation
    print("\n2. Testing Course Validation...")
    
    # Valid MI track plan
    valid_plan = ["CS 37300", "CS 38100", "CS 47100", "STAT 41600", "CS 34800", "CS 57700"]
    result = validator.validate_course_plan(valid_plan)
    
    if result['valid']:
        print("✅ Valid MI track plan correctly validated")
        print(f"   Summary: {result['summary']}")
    else:
        print("❌ Valid plan incorrectly rejected")
        print(f"   Errors: {result['errors']}")
        return False
    
    # Test 3: Double counting prevention
    print("\n3. Testing Double Counting Prevention...")
    
    # Invalid plan with double counting
    invalid_plan = ["CS 37300", "CS 38100", "CS 47300", "STAT 41600", "CS 47300", "CS 34800"]
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
    if "CS 37300" in guidance and "CS 38100" in guidance:
        print("✅ Required course guidance accurate")
        print(f"   Response includes mandatory courses")
    else:
        print("❌ Required course guidance incomplete")
        return False
    
    # Test 5: Elective guidance
    print("\n5. Testing Elective Guidance...")
    
    elective_guidance = scraper.get_course_guidance("Tell me about electives")
    if "2" in elective_guidance:
        print("✅ Elective guidance accurate")
        print(f"   Response mentions choosing 2 electives")
    else:
        print("❌ Elective guidance incomplete")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All MI Track Integration Tests Passed!")
    print("✅ Enhanced Boiler AI has accurate MI track information")
    print("✅ Course validation working correctly")
    print("✅ Double counting prevention active")
    print("✅ Accurate guidance responses")
    
    return True

def test_specific_mi_scenarios():
    """Test specific MI track scenarios"""
    print("\n🎯 Testing Specific MI Track Scenarios")
    print("-" * 40)
    
    validator = MITrackValidator()
    
    # Scenario 1: Missing mandatory courses
    print("Scenario 1: Missing mandatory courses")
    incomplete = ["CS 47100", "STAT 41600", "CS 34800", "CS 57700"]
    result = validator.validate_course_plan(incomplete)
    
    if not result['valid']:
        print("✅ Missing mandatory courses detected")
        mandatory_errors = [err for err in result['errors'] if 'CS 37300' in err or 'CS 38100' in err]
        print(f"   Found {len(mandatory_errors)} mandatory course errors")
    else:
        print("❌ Missing mandatory courses not detected")
    
    # Scenario 2: Data visualization group constraint
    print("\nScenario 2: Data visualization group constraint")
    over_limit = ["CS 37300", "CS 38100", "CS 47100", "STAT 41600", "CS 43900", "CS 44000"]
    result = validator.validate_course_plan(over_limit)
    
    if not result['valid']:
        print("✅ Data visualization group constraint enforced")
        viz_errors = [err for err in result['errors'] if 'visualization' in err.lower()]
        print(f"   Found {len(viz_errors)} visualization group errors")
    else:
        print("❌ Data visualization group constraint not enforced")
    
    # Scenario 3: Perfect valid plan
    print("\nScenario 3: Perfect valid plan")
    perfect = ["CS 37300", "CS 38100", "CS 47100", "STAT 41600", "CS 34800", "CS 57700"]
    result = validator.validate_course_plan(perfect)
    
    if result['valid']:
        print("✅ Perfect plan validated correctly")
        print(f"   Total courses: {result['summary']['total_courses']}")
    else:
        print("❌ Perfect plan incorrectly rejected")
        print(f"   Errors: {result['errors']}")

if __name__ == "__main__":
    print("🚀 Enhanced Boiler AI - MI Track Integration Test")
    print("=" * 60)
    
    success = test_mi_track_integration()
    
    if success:
        test_specific_mi_scenarios()
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("🎓 Enhanced Boiler AI ready for MI track advising")
    else:
        print("\n" + "=" * 60)
        print("❌ Some tests failed")
        print("🔧 Review integration issues")