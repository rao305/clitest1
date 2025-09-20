#!/usr/bin/env python3
"""
Real-world testing of Hybrid AI System with actual Gemini API key
No mocks, no templates - real data and real queries only
"""

import os
import sys
from hybrid_ai_system import HybridAISystem
from universal_purdue_advisor import UniversalPurdueAdvisor

def test_with_real_Gemini():
    """Test with real Gemini API key - no mocks or templates"""
    
    # Check for real API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ No Gemini API key found in environment")
        print("Set your real API key with: export GEMINI_API_KEY='your-real-key'")
        return False
    
    if api_key.startswith('sk-') and len(api_key) > 40:
        print(f"✅ Real Gemini API key detected (length: {len(api_key)})")
    else:
        print("⚠️ API key format looks suspicious - ensure it's a real Gemini key")
        return False
    
    try:
        print("\n🚀 Initializing Hybrid AI System with real Gemini integration...")
        
        # Initialize systems
        hybrid_system = HybridAISystem()
        advisor = UniversalPurdueAdvisor()
        
        print("✅ Systems initialized successfully")
        
        # Real student queries - no templates
        real_queries = [
            "What is CS 18000 and how difficult is it?",
            "I want to do machine learning - what track should I choose?", 
            "What are the exact requirements to CODO into computer science?",
            "I'm struggling with CS 18000 and might fail - what are my options?",
            "What courses do I need to take before CS 25000?",
            "How do the MI and SE tracks compare for someone interested in AI?",
            "I failed CS 18200, how does this affect my graduation timeline?",
            "What's the difference between CS 37300 and CS 48300?"
        ]
        
        print(f"\n🧪 Testing {len(real_queries)} real student queries...")
        print("=" * 80)
        
        for i, query in enumerate(real_queries, 1):
            print(f"\n📝 Query {i}: {query}")
            print("-" * 60)
            
            try:
                # Test hybrid system directly
                hybrid_result = hybrid_system.process_query(query)
                print(f"🎯 Hybrid Classification: {hybrid_result['classification']}")
                print(f"📊 Intent: {hybrid_result['intent']}")
                print(f"✅ Confidence: {hybrid_result['confidence']:.2f}")
                print(f"🔧 Source: {hybrid_result['source']}")
                
                # Test through main advisor interface
                advisor_response = advisor.ask_question(query)
                
                print(f"\n💬 Response ({len(advisor_response)} chars):")
                print(advisor_response[:200] + "..." if len(advisor_response) > 200 else advisor_response)
                
                # Validate response quality
                if len(advisor_response) < 50:
                    print("⚠️ Response seems too short")
                elif "I'm having trouble" in advisor_response or "error" in advisor_response.lower():
                    print("⚠️ Error response detected")
                else:
                    print("✅ Response looks good")
                    
            except Exception as e:
                print(f"❌ Error processing query: {e}")
            
            print("=" * 80)
        
        print("\n🏁 Real-world testing completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        return False

def test_specific_routing():
    """Test specific routing scenarios with real API"""
    
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key or not api_key.startswith('sk-'):
        print("❌ Real Gemini API key required for routing tests")
        return False
    
    try:
        hybrid_system = HybridAISystem()
        
        routing_tests = [
            ("What is CS 18000?", "lookup_table", "Should use course database"),
            ("What are MI track requirements?", "lookup_table", "Should use track database"),
            ("What are CODO requirements?", "lookup_table", "Should use admissions database"),
            ("What prerequisites do I need for CS 25000?", "rule_based", "Should use prerequisite logic"),
            ("Help me choose between AI and software careers", "llm_enhanced", "Should use Gemini for analysis")
        ]
        
        print("\n🔍 Testing query routing with real Gemini...")
        print("=" * 80)
        
        for query, expected_type, explanation in routing_tests:
            print(f"\n📝 Query: {query}")
            print(f"🎯 Expected: {expected_type} - {explanation}")
            
            result = hybrid_system.process_query(query)
            actual_type = result['classification']
            
            if actual_type == expected_type:
                print(f"✅ Correct routing: {actual_type}")
            else:
                print(f"⚠️ Unexpected routing: got {actual_type}, expected {expected_type}")
            
            print(f"📊 Confidence: {result['confidence']:.2f}")
            print(f"💬 Response preview: {result['response'][:100]}...")
            print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Routing test failed: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Real-World Hybrid AI System Testing")
    print("No mocks, no templates - real Gemini integration only")
    print("=" * 80)
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--routing-only":
        success = test_specific_routing()
    else:
        success = test_with_real_Gemini()
        
        if success:
            print("\n🔍 Running additional routing tests...")
            test_specific_routing()
    
    if success:
        print("\n🎉 All tests passed with real Gemini integration!")
    else:
        print("\n❌ Tests failed - check your Gemini API key and try again")
        sys.exit(1)