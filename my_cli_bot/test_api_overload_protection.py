#!/usr/bin/env python3
"""
API Overload Protection Test
Tests that the system handles API overload errors gracefully without crashing.
"""

import os
import sys
import time
import threading
from unittest.mock import patch, MagicMock
from simple_boiler_ai import SimpleBoilerAI, ResilientGeminiClient

def test_resilient_client_backoff():
    """Test that the resilient client implements proper backoff"""
    print("🧪 TESTING RESILIENT CLIENT BACKOFF")
    print("=" * 40)
    
    # Set up test environment
    os.environ["GEMINI_API_KEY"] = "sk-test-key-for-testing"
    
    client = ResilientGeminiClient("sk-test-key-for-testing")
    
    # Test backoff calculation
    for attempt in range(5):
        delay = client._exponential_backoff(attempt)
        expected_min = 2 ** attempt
        expected_max = min(2 ** attempt, 30) + 1
        
        print(f"   Attempt {attempt}: {delay:.1f}s (expected: {expected_min}-{expected_max}s)")
        
        if not (expected_min <= delay <= expected_max):
            print(f"   ❌ Backoff calculation incorrect for attempt {attempt}")
            return False
    
    print("   ✅ Backoff calculation working correctly")
    return True

def test_request_throttling():
    """Test that requests are throttled properly"""
    print("\n⏱️ TESTING REQUEST THROTTLING")
    print("=" * 40)
    
    os.environ["GEMINI_API_KEY"] = "sk-test-key-for-testing"
    client = ResilientGeminiClient("sk-test-key-for-testing")
    
    # Time multiple rapid requests
    start_times = []
    
    def make_request():
        start_times.append(time.time())
        client._wait_if_needed()
    
    # Make 3 rapid requests
    for i in range(3):
        make_request()
    
    # Check timing
    if len(start_times) >= 3:
        gap1 = start_times[1] - start_times[0] 
        gap2 = start_times[2] - start_times[1]
        
        print(f"   Time between requests: {gap1:.3f}s, {gap2:.3f}s")
        
        # First gap might be small since last_request_time starts at 0
        # But second gap should respect the interval
        if gap2 >= client.min_interval:
            print("   ✅ Request throttling working correctly")
            return True
        else:
            print(f"   ❌ Requests not throttled (min interval: {client.min_interval}s)")
            return False
    else:
        print("   ❌ Not enough requests recorded")
        return False

def test_overload_error_simulation():
    """Test handling of simulated overload errors"""
    print("\n🚨 TESTING OVERLOAD ERROR HANDLING")
    print("=" * 40)
    
    os.environ["GEMINI_API_KEY"] = "sk-test-key-for-testing"
    
    # Mock Gemini client to simulate overload errors
    with patch('Gemini.Gemini') as mock_Gemini_class:
        mock_client = MagicMock()
        mock_Gemini_class.return_value = mock_client
        
        # Simulate overload error (529)
        overload_error = Exception("overloaded_error: Too many requests")
        mock_client.chat.completions.create.side_effect = [
            overload_error,  # First attempt fails
            overload_error,  # Second attempt fails  
            overload_error   # Third attempt fails
        ]
        
        resilient_client = ResilientGeminiClient("sk-test-key-for-testing")
        
        try:
            response = resilient_client.chat_completion_with_retry(
                ,
                prompt,
                
            )
            print("   ❌ Should have failed after max retries")
            return False
        except Exception as e:
            if "overloaded after" in str(e):
                print("   ✅ Overload error handled correctly with max retries")
                print(f"   ✅ Error message: {str(e)[:60]}...")
                return True
            else:
                print(f"   ❌ Unexpected error: {e}")
                return False

def test_successful_retry_after_overload():
    """Test successful request after initial overload"""
    print("\n✅ TESTING SUCCESSFUL RETRY")
    print("=" * 40)
    
    os.environ["GEMINI_API_KEY"] = "sk-test-key-for-testing"
    
    with patch('Gemini.Gemini') as mock_Gemini_class:
        mock_client = MagicMock()
        mock_Gemini_class.return_value = mock_client
        
        # Simulate overload then success
        overload_error = Exception("overloaded_error: API overloaded")
        success_response = MagicMock()
        success_response.choices = [MagicMock()]
        success_response.text = "Test response"
        
        mock_client.chat.completions.create.side_effect = [
            overload_error,  # First attempt fails
            success_response  # Second attempt succeeds
        ]
        
        resilient_client = ResilientGeminiClient("sk-test-key-for-testing")
        
        try:
            response = resilient_client.chat_completion_with_retry(
                , 
                prompt,
                
            )
            
            if response == "Test response":
                print("   ✅ Successfully retried after overload error")
                return True
            else:
                print(f"   ❌ Unexpected response: {response}")
                return False
                
        except Exception as e:
            print(f"   ❌ Retry failed: {e}")
            return False

def test_main_system_integration():
    """Test that the main system uses resilient client"""
    print("\n🎯 TESTING MAIN SYSTEM INTEGRATION")
    print("=" * 40)
    
    os.environ["GEMINI_API_KEY"] = "sk-test-key-for-testing"
    
    try:
        # Initialize the main system
        bot = SimpleBoilerAI()
        
        # Check that it uses ResilientGeminiClient
        if isinstance(bot.gemini_model, ResilientGeminiClient):
            print("   ✅ Main system uses ResilientGeminiClient")
        else:
            print(f"   ❌ Main system uses: {type(bot.gemini_model)}")
            return False
        
        # Check that client has retry methods
        if hasattr(bot.gemini_model, 'chat_completion_with_retry'):
            print("   ✅ Resilient client has retry methods")
        else:
            print("   ❌ Resilient client missing retry methods")
            return False
        
        # Check query processing doesn't crash
        test_queries = [
            "What courses should I take?",
            "I failed CS 18000",
            "What is CODO?"
        ]
        
        for query in test_queries:
            try:
                query_type = bot.detect_query_type(query)
                relevant_data = bot.extract_relevant_knowledge(query)
                print(f"   ✅ Query processing works: '{query}' → {query_type}")
            except Exception as e:
                print(f"   ❌ Query processing failed: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ System integration error: {e}")
        return False

def main():
    """Run all API overload protection tests"""
    print("🛡️ API OVERLOAD PROTECTION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Resilient Client Backoff", test_resilient_client_backoff),
        ("Request Throttling", test_request_throttling),
        ("Overload Error Handling", test_overload_error_simulation),
        ("Successful Retry", test_successful_retry_after_overload),
        ("Main System Integration", test_main_system_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running: {test_name}")
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ TEST CRASHED: {test_name} - {e}")
            results.append(False)
    
    # Summary
    print("\n📊 TEST RESULTS SUMMARY")
    print("=" * 40)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ API overload protection is working correctly")
        print("✅ System will handle 529 errors gracefully")
        print("✅ No more API overload crashes expected")
        return True
    else:
        print(f"\n❌ {total - passed} TESTS FAILED")
        print("⚠️ API overload protection needs fixes")
        return False

if __name__ == "__main__":
    main()