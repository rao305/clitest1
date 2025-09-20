#!/usr/bin/env python3
"""
Test for hardcoded responses in the Boiler AI system
This test can run without Gemini API key and will detect hardcoded responses
"""

import sys
import os

def test_hardcoded_responses():
    """Test to identify hardcoded responses in the smart AI engine"""
    
    print("🔍 Testing for Hardcoded Responses")
    print("=" * 50)
    
    try:
        # Import the smart AI engine
        from smart_ai_engine import SmartAIEngine
        
        # Create engine instance
        engine = SmartAIEngine()
        
        # Test queries that should produce different responses
        test_queries = [
            "What are the prerequisites for CS 25000?",
            "What are the prerequisites for CS 18000?", 
            "What are the prerequisites for CS 38100?",
            "I'm a sophomore interested in Machine Intelligence track",
            "I'm a junior interested in Software Engineering track",
            "I'm a freshman looking at career guidance",
            "Help me plan my graduation timeline",
            "Can I do both MI and SE tracks?"
        ]
        
        print("\n🧪 Testing Different Queries for Hardcoded Responses:")
        print("-" * 60)
        
        responses = []
        hardcoded_detected = False
        
        for query in test_queries:
            try:
                # Test with minimal context to trigger fallback
                context = {"session_id": "test_session"}
                response = engine._generate_fallback_response(
                    engine._analyze_intent(query, context), 
                    context
                )
                responses.append((query, response))
                print(f"\nQuery: {query}")
                print(f"Response: {response[:100]}...")
                
                # Check for hardcoded patterns
                if "I can help you" in response and response.count("I can help you") > 0:
                    if any(hardcoded in response for hardcoded in [
                        "I can help you plan courses for both Machine Intelligence",
                        "I can help you create a dual track graduation plan!",
                        "I can help you choose between Machine Intelligence and Software Engineering tracks!",
                        "I can help you with prerequisites! Which course are you asking about?",
                        "I can help you understand course difficulty! Which course are you asking about?"
                    ]):
                        print("⚠️  HARDCODED RESPONSE DETECTED!")
                        hardcoded_detected = True
                
            except Exception as e:
                print(f"❌ Error testing query '{query}': {e}")
                hardcoded_detected = True
        
        # Check for identical responses to different queries
        print("\n🔍 Checking for Identical Responses to Different Queries:")
        print("-" * 60)
        
        for i, (query1, response1) in enumerate(responses):
            for j, (query2, response2) in enumerate(responses):
                if i < j and response1 == response2:
                    print(f"⚠️  IDENTICAL RESPONSES DETECTED:")
                    print(f"   Query 1: {query1}")
                    print(f"   Query 2: {query2}")
                    print(f"   Response: {response1}")
                    hardcoded_detected = True
        
        if hardcoded_detected:
            print("\n❌ HARDCODED RESPONSES FOUND!")
            print("The system is using fallback responses instead of personalized AI-generated responses.")
            print("This happens when the Gemini API is not available or there are issues with the smart AI engine.")
            return False
        else:
            print("\n✅ No obvious hardcoded responses detected in this test.")
            print("However, full testing requires Gemini API key for complete AI response generation.")
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_smart_ai_engine_direct():
    """Test the smart AI engine directly"""
    
    print("\n🔬 Testing Smart AI Engine Directly")
    print("=" * 50)
    
    try:
        from smart_ai_engine import SmartAIEngine
        
        engine = SmartAIEngine()
        
        # Test a simple query
        query = "What courses should I take as a freshman?"
        context = {"session_id": "test_session"}
        
        print(f"Query: {query}")
        
        # This will likely fail without Gemini API but will show us the fallback behavior
        try:
            response = engine.process_query(query, context)
            print(f"Response: {response}")
            
            # Check if it's a fallback response
            if "I can help you" in response and len(response) < 200:
                print("⚠️  This appears to be a fallback/hardcoded response")
                return False
            else:
                print("✅ Response appears to be personalized/AI-generated")
                return True
                
        except Exception as e:
            print(f"⚠️  Engine failed (expected without Gemini API): {e}")
            
            # Test the fallback method directly
            intent = engine._analyze_intent(query, context)
            fallback_response = engine._generate_fallback_response(intent, context)
            print(f"Fallback Response: {fallback_response}")
            
            if "I can help you" in fallback_response:
                print("⚠️  Fallback response is hardcoded")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Boiler AI - Hardcoded Response Detection Test")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_hardcoded_responses()
    test2_passed = test_smart_ai_engine_direct()
    
    print("\n📊 TEST RESULTS:")
    print("=" * 60)
    print(f"Hardcoded Response Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Smart AI Engine Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if not test1_passed or not test2_passed:
        print("\n🔧 RECOMMENDED FIXES:")
        print("1. Remove hardcoded fallback responses from smart_ai_engine.py")
        print("2. Implement dynamic response generation using knowledge base")
        print("3. Make fallback responses context-aware and personalized")
        print("4. Set up Gemini API key for full AI response generation")
        sys.exit(1)
    else:
        print("\n✅ All tests passed! The system appears to be working correctly.")
        sys.exit(0)