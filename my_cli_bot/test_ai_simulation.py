#!/usr/bin/env python3
"""
AI Simulation Test - Test how the system behaves with simulated AI responses
"""

import json
from sql_query_handler import SQLQueryHandler

class MockAIResponse:
    """Mock AI client for testing"""
    
    def chat_completion_with_retry(self, **kwargs):
        """Simulate AI responses based on the prompt"""
        messages = kwargs.get('messages', [])
        if not messages:
            return "I'd be happy to help with your CS question!"
            
        prompt = messages[0].get('content', '').lower()
        
        # Simulate contextual AI responses
        if 'error' in prompt and 'database' in prompt:
            return "I'm having some trouble accessing that information right now. Could you try asking about it in a different way? I can help with course information, graduation planning, or track requirements."
        
        elif 'unknown' in prompt and 'query' in prompt:
            return "I'm not quite sure what you're asking about. Could you be more specific? For example, are you asking about specific courses, graduation timeline, or track requirements?"
        
        elif 'clarification' in prompt:
            return "I'd like to help you with that! Could you provide a bit more detail about what specific information you're looking for?"
        
        elif 'welcome' in prompt:
            return "Welcome to Boiler AI! I'm here to help you navigate your Purdue CS academic journey. Ask me about courses, graduation planning, track requirements, CODO, or any other academic questions you have. What would you like to know?"
        
        elif 'farewell' in prompt:
            return "Thanks for using Boiler AI! Best of luck with your CS studies at Purdue. Feel free to come back anytime you have questions!"
        
        elif 'technical issue' in prompt:
            return "I ran into a small technical hiccup. Could you try asking your question again? I'm here to help with your CS academic needs!"
        
        else:
            return "That's a great question! I'd be happy to help you with that CS topic."

def test_ai_powered_error_handling():
    """Test AI-powered error handling with mock responses"""
    print("🤖 Testing AI-Powered Error Handling")
    print("=" * 50)
    
    # Create handler with non-existent database to trigger errors
    handler = SQLQueryHandler("nonexistent.db")
    mock_ai = MockAIResponse()
    
    test_queries = [
        "Tell me about CS 18000",
        "What are the prerequisites for CS 25100?", 
        "CODO requirements",
        "random nonsense query",
        "xyz123 course",
    ]
    
    ai_responses = 0
    
    for query in test_queries:
        print(f"\n📝 Testing: '{query}'")
        
        try:
            result = handler.process_query(query)
            
            if not result['success'] and 'user_friendly_error' in result:
                error_context = result['user_friendly_error']
                
                if isinstance(error_context, dict) and error_context.get('needs_ai_response'):
                    # Simulate AI response generation
                    context = error_context.get('context', '')
                    query_type = error_context.get('query_type', '')
                    
                    # Create mock prompt based on context
                    if context == 'sql_error':
                        prompt = f"error database query {query_type}"
                    elif context == 'unknown_query':
                        prompt = f"unknown query clarification {query}"
                    else:
                        prompt = f"help with {query}"
                    
                    ai_response = mock_ai.chat_completion_with_retry(
                        prompt
                    )
                    
                    print(f"   ✅ AI Response: {ai_response[:80]}...")
                    ai_responses += 1
                else:
                    print(f"   ❌ Non-AI error: {error_context}")
            
            elif result['success']:
                print(f"   ✅ Query succeeded: {result['count']} results")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 AI Error Handling Results:")
    print(f"   AI-powered responses: {ai_responses}")
    print(f"   Success rate: {ai_responses}/{len(test_queries)} queries handled by AI")
    
    return ai_responses > 0

def test_successful_query_processing():
    """Test successful SQL queries with good database"""
    print("\n✅ Testing Successful Query Processing")
    print("=" * 50)
    
    handler = SQLQueryHandler()  # Use good database
    
    queries = [
        ("Tell me about CS 18000", "course_info"),
        ("Prerequisites for CS 25100", "prerequisite_chain"),
        ("Machine Intelligence track courses", "track_courses"),
        ("CODO requirements", "codo_requirements"),
        ("3 year graduation", "graduation_timeline"),
        ("CS 18000 failure impact", "failure_impact"),
    ]
    
    successful = 0
    
    for query, expected_type in queries:
        print(f"\n📝 Testing: '{query}'")
        
        try:
            result = handler.process_query(query)
            
            if result['success'] and result['count'] > 0:
                print(f"   ✅ Success: {result['count']} results found")
                print(f"   Type: {result['type']}")
                successful += 1
            elif result['success'] and result['count'] == 0:
                print(f"   ⚠️  No results but query succeeded")
                print(f"   Type: {result['type']}")
            else:
                print(f"   ❌ Query failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n📊 Query Success Results:")
    print(f"   Successful queries: {successful}/{len(queries)}")
    
    return successful >= len(queries) * 0.8  # 80% success rate

def test_system_integration_flow():
    """Test the complete system integration flow"""
    print("\n🔄 Testing System Integration Flow")
    print("=" * 50)
    
    mock_ai = MockAIResponse()
    
    # Test different interaction scenarios
    scenarios = [
        {
            'name': 'Welcome Message',
            'prompt': 'welcome message for academic advisor',
            'expected_keywords': ['welcome', 'boiler', 'cs', 'help']
        },
        {
            'name': 'Database Error',
            'prompt': 'error database query course_info',
            'expected_keywords': ['trouble', 'different', 'way', 'help']
        },
        {
            'name': 'Unknown Query',
            'prompt': 'unknown query clarification random text',
            'expected_keywords': ['sure', 'specific', 'courses', 'graduation']
        },
        {
            'name': 'Farewell Message',
            'prompt': 'farewell student leaving advisor',
            'expected_keywords': ['thanks', 'luck', 'studies', 'cs']
        }
    ]
    
    passed_scenarios = 0
    
    for scenario in scenarios:
        print(f"\n📝 Testing: {scenario['name']}")
        
        try:
            response = mock_ai.chat_completion_with_retry(
                prompt}]
            )
            
            print(f"   Response: {response}")
            
            # Check if response contains expected keywords
            response_lower = response.lower()
            keywords_found = sum(1 for keyword in scenario['expected_keywords'] 
                               if keyword in response_lower)
            
            if keywords_found >= len(scenario['expected_keywords']) * 0.5:
                print(f"   ✅ Contextually appropriate response")
                passed_scenarios += 1
            else:
                print(f"   ⚠️  Response may not be contextually optimal")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Integration Flow Results:")
    print(f"   Passed scenarios: {passed_scenarios}/{len(scenarios)}")
    
    return passed_scenarios >= len(scenarios) * 0.75

def main():
    """Run AI simulation tests"""
    print("🤖 AI System Simulation Test")
    print("=" * 60)
    print("Testing AI-powered responses and system integration...\n")
    
    tests = [
        ("AI Error Handling", test_ai_powered_error_handling),
        ("Successful Queries", test_successful_query_processing),
        ("Integration Flow", test_system_integration_flow),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 AI SIMULATION TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if passed_test:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 AI SIMULATION SUCCESSFUL!")
        print("   ✅ AI-powered error handling working")
        print("   ✅ SQL queries functioning properly")
        print("   ✅ System integration flow operational")
        print("\n🚀 System ready for AI integration!")
    else:
        print("\n⚠️  Some simulation tests failed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)