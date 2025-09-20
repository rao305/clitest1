#!/usr/bin/env python3
"""
Test the hybrid system with the exact dual track query from the user
"""

import os
from hybrid_ai_system import HybridAISystem

def test_dual_track_query():
    """Test with the real query that was problematic"""
    
    # Check for real API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key or not api_key.startswith('sk-'):
        print("❌ Need real Gemini API key for testing")
        print("Set with: export GEMINI_API_KEY='sk-your-key'")
        return
    
    try:
        # Initialize hybrid system
        print("🚀 Initializing Hybrid AI System...")
        hybrid_system = HybridAISystem()
        
        # Test the exact query that was failing
        test_query = "So basically i want to graudate ASAP with the two tracks in se and mi can you curate a plan for this?"
        
        print(f"\n📝 Testing query: {test_query}")
        print("=" * 80)
        
        # Process with hybrid system
        result = hybrid_system.process_query(test_query)
        
        print(f"🎯 Classification: {result['classification']}")
        print(f"📊 Intent: {result['intent']}")
        print(f"✅ Confidence: {result['confidence']:.2f}")
        print(f"🔧 Source: {result['source']}")
        print(f"\n💬 Response ({len(result['response'])} chars):")
        print(result['response'])
        
        # Verify it's not empty or generic
        if len(result['response']) < 100:
            print("\n⚠️ Response seems too short")
        elif "semantic" in result['response'].lower():
            print("\n❌ Still getting semantic analysis fallback")
        elif "DUAL TRACK" in result['response'] or "graduation" in result['response'].lower():
            print("\n✅ Getting proper dual track response!")
        else:
            print("\n⚠️ Response doesn't seem dual-track specific")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_other_track_queries():
    """Test other track-related queries"""
    
    queries = [
        "What are the MI track requirements?",
        "What are the SE track requirements?", 
        "What are the requirements for both tracks?",
        "I want to do dual track with machine intelligence and software engineering"
    ]
    
    try:
        hybrid_system = HybridAISystem()
        
        for query in queries:
            print(f"\n📝 Testing: {query}")
            print("-" * 60)
            
            result = hybrid_system.process_query(query)
            print(f"🎯 {result['classification']} | Intent: {result['intent']} | Confidence: {result['confidence']:.2f}")
            print(f"Response preview: {result['response'][:100]}...")
            
    except Exception as e:
        print(f"❌ Error in additional tests: {e}")

if __name__ == "__main__":
    print("🧪 Testing Hybrid System with Dual Track Queries")
    print("=" * 60)
    
    success = test_dual_track_query()
    
    if success:
        print("\n🔍 Testing additional track queries...")
        test_other_track_queries()
        print("\n🎉 Hybrid system testing completed!")
    else:
        print("\n❌ Primary test failed")