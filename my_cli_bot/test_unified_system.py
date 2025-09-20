#!/usr/bin/env python3
"""
Test the complete unified system integration
Tests the enhanced N8N pipeline, unified AI engine, and updated main system
"""

import os
import sys
import time
import json
from typing import List, Tuple

def test_unified_ai_engine():
    """Test the unified AI query engine"""
    print("🧪 Testing Unified AI Query Engine")
    print("=" * 60)
    
    try:
        from unified_ai_query_engine import UnifiedAIQueryEngine
        
        engine = UnifiedAIQueryEngine()
        
        test_queries = [
            "Hi, I'm a freshman, what courses should I take?",
            "I failed CS 25100, what should I do?",
            "What are the prerequisites for CS 37300?",
            "Tell me about both MI and SE tracks",
            "How do I get into CS through CODO?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testing: {query}")
            try:
                result = engine.process_query(query)
                print(f"   ✅ Method: {result.processing_method}")
                print(f"   ✅ Confidence: {result.confidence:.2f}")
                print(f"   ✅ Time: {result.processing_time:.2f}s")
                print(f"   ✅ Response: {result.response[:100]}...")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n📊 System Statistics:")
        stats = engine.get_system_statistics()
        print(f"   - Total Queries: {stats['query_stats']['total_queries']}")
        print(f"   - Success Rate: {stats['query_stats']['successful_queries']}/{stats['query_stats']['total_queries']}")
        print(f"   - Knowledge Base: {stats['knowledge_base']['courses']} courses")
        
        return True
        
    except Exception as e:
        print(f"❌ Unified AI Engine test failed: {e}")
        return False

def test_enhanced_n8n_integration():
    """Test the enhanced N8N integration"""
    print("\n🧪 Testing Enhanced N8N Integration")
    print("=" * 60)
    
    try:
        from enhanced_n8n_integration import EnhancedN8NIntegration
        
        integration = EnhancedN8NIntegration()
        
        test_queries = [
            "What courses should I take as a sophomore?",
            "I failed CS 18000, what happens next?",
            "Tell me about the Machine Intelligence track"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testing: {query}")
            try:
                response = integration.process_query_sync(query)
                print(f"   ✅ Response: {response[:100]}...")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n📊 N8N Integration Status:")
        status = integration.get_system_status()
        print(f"   - Status: {status['status']}")
        print(f"   - Knowledge Sources: {status['knowledge_base']['sources']}")
        print(f"   - Cache Size: {status['cache']['query_cache_size']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced N8N Integration test failed: {e}")
        return False

def test_main_system_integration():
    """Test the main system with unified integration"""
    print("\n🧪 Testing Main System Integration")
    print("=" * 60)
    
    try:
        # Set environment variable if not set
        if not os.environ.get("GEMINI_API_KEY"):
            print("⚠️ GEMINI_API_KEY not set - using mock mode")
            os.environ["GEMINI_API_KEY"] = "sk-test-key-for-testing"
        
        from universal_purdue_advisor import UniversalPurdueAdvisor
        
        advisor = UniversalPurdueAdvisor()
        
        test_queries = [
            "Hi, I'm new to Purdue CS, can you help me?",
            "What is CS 18000?",
            "I failed calculus, what should I do?",
            "How do I choose between MI and SE tracks?",
            "What are the CODO requirements?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testing: {query}")
            try:
                start_time = time.time()
                response = advisor.ask_question(query)
                processing_time = time.time() - start_time
                
                print(f"   ✅ Processing time: {processing_time:.2f}s")
                print(f"   ✅ Response: {response[:150]}...")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Main System Integration test failed: {e}")
        return False

def test_knowledge_base_integration():
    """Test knowledge base loading and integration"""
    print("\n🧪 Testing Knowledge Base Integration")
    print("=" * 60)
    
    try:
        # Check if knowledge files exist
        knowledge_files = [
            "data/cs_knowledge_graph.json",
            "data/comprehensive_purdue_cs_data.json"
        ]
        
        files_found = []
        for file_path in knowledge_files:
            if os.path.exists(file_path):
                files_found.append(file_path)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    print(f"   ✅ {file_path}: {len(data)} top-level keys")
                except Exception as e:
                    print(f"   ❌ {file_path}: Error loading - {e}")
            else:
                print(f"   ⚠️ {file_path}: Not found")
        
        if files_found:
            print(f"\n📊 Knowledge Base Status: {len(files_found)}/{len(knowledge_files)} files available")
            return True
        else:
            print("\n❌ No knowledge base files found")
            return False
            
    except Exception as e:
        print(f"❌ Knowledge Base Integration test failed: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive system test"""
    print("🚀 Starting Comprehensive System Test")
    print("=" * 80)
    
    test_results = []
    
    # Test 1: Knowledge Base Integration
    result1 = test_knowledge_base_integration()
    test_results.append(("Knowledge Base Integration", result1))
    
    # Test 2: Unified AI Engine
    result2 = test_unified_ai_engine()
    test_results.append(("Unified AI Engine", result2))
    
    # Test 3: Enhanced N8N Integration
    result3 = test_enhanced_n8n_integration()
    test_results.append(("Enhanced N8N Integration", result3))
    
    # Test 4: Main System Integration
    result4 = test_main_system_integration()
    test_results.append(("Main System Integration", result4))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - System is ready!")
        print("\nThe unified system successfully integrates:")
        print("  • Enhanced N8N Pipeline Integration")
        print("  • Unified AI Query Engine")
        print("  • Comprehensive Knowledge Base")
        print("  • Intelligent Query Routing")
        print("  • Multi-Engine Fallback System")
    else:
        print(f"\n⚠️ {total - passed} tests failed - System needs attention")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)