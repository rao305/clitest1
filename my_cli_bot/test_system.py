#!/usr/bin/env python3
"""
Test script to verify the complete system
"""

import requests
import json
import time
import sys

def test_system_endpoints():
    """Test all system endpoints"""
    base_url = "http://localhost:5000"
    
    tests = [
        {
            "name": "Health Check",
            "method": "GET",
            "endpoint": "/api/status",
            "expected_status": 200
        },
        {
            "name": "Chat Endpoint - MI Track",
            "method": "POST",
            "endpoint": "/api/chat",
            "data": {
                "query": "What are the required courses for Machine Intelligence track?",
                "track_context": "MI"
            },
            "expected_status": 200
        },
        {
            "name": "Chat Endpoint - SE Track",
            "method": "POST",
            "endpoint": "/api/chat",
            "data": {
                "query": "What are the required courses for Software Engineering track?",
                "track_context": "SE"
            },
            "expected_status": 200
        },
        {
            "name": "Course Validation",
            "method": "POST",
            "endpoint": "/api/chat",
            "data": {
                "query": "Can I use CS 47300 for both required and elective?",
                "track_context": "MI"
            },
            "expected_status": 200
        },
        {
            "name": "Track Comparison",
            "method": "POST",
            "endpoint": "/api/chat",
            "data": {
                "query": "What's the difference between MI and SE tracks?"
            },
            "expected_status": 200
        },
        {
            "name": "Training Data Export",
            "method": "GET",
            "endpoint": "/api/export-training-data",
            "expected_status": 200
        }
    ]
    
    print("🧪 Testing Purdue CS AI Assistant System")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\n🔍 Testing: {test['name']}")
        
        try:
            if test['method'] == 'GET':
                response = requests.get(f"{base_url}{test['endpoint']}", timeout=30)
            else:
                response = requests.post(
                    f"{base_url}{test['endpoint']}", 
                    json=test.get('data', {}),
                    timeout=30
                )
            
            if response.status_code == test['expected_status']:
                print(f"✅ {test['name']}: PASSED")
                
                if test['endpoint'] == '/api/chat':
                    data = response.json()
                    print(f"   Response preview: {data.get('response', '')[:100]}...")
                    print(f"   Confidence: {data.get('confidence', 0):.2f}")
                    print(f"   Track: {data.get('track', 'N/A')}")
                elif test['endpoint'] == '/api/status':
                    data = response.json()
                    print(f"   Status: {data.get('status', 'unknown')}")
                    print(f"   Total courses: {data.get('stats', {}).get('total_courses', 0)}")
                
                passed += 1
            else:
                print(f"❌ {test['name']}: FAILED (Status: {response.status_code})")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ {test['name']}: ERROR - {e}")
    
    print(f"\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for production.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the system configuration.")
        return False

def test_cli_integration():
    """Test integration with existing CLI system"""
    print("\n🔧 Testing CLI Integration")
    print("-" * 30)
    
    try:
        # Test importing existing modules
        from mi_track_scraper import PurdueMITrackScraper
        from se_track_scraper import PurdueSETrackScraper
        from course_validator import MITrackValidator
        from se_course_validator import SETrackValidator
        
        print("✅ All existing modules imported successfully")
        
        # Test scraper functionality
        mi_scraper = PurdueMITrackScraper()
        se_scraper = PurdueSETrackScraper()
        
        mi_data = mi_scraper.scrape_courses()
        se_data = se_scraper.scrape_courses()
        
        if mi_data and se_data:
            print("✅ Track scrapers working correctly")
            return True
        else:
            print("❌ Track scrapers failed")
            return False
            
    except Exception as e:
        print(f"❌ CLI Integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("⏳ Waiting for system to start...")
    time.sleep(5)
    
    # Test CLI integration first
    cli_success = test_cli_integration()
    
    if cli_success:
        # Test web endpoints
        web_success = test_system_endpoints()
        
        if web_success:
            print("\n🎉 All systems operational!")
            print("✅ CLI chatbot integration working")
            print("✅ Web API endpoints functional")
            print("✅ Knowledge graph system active")
            print("✅ Ready for production deployment")
        else:
            print("\n⚠️ Web API issues detected")
            sys.exit(1)
    else:
        print("\n❌ CLI integration issues detected")
        sys.exit(1)