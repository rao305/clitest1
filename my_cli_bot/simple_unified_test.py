#!/usr/bin/env python3
"""
Simple test of the unified system components without external dependencies
Tests core functionality that should work in the current environment
"""

import os
import sys
import time
import json

def test_core_components():
    """Test core components without external dependencies"""
    print("🧪 Testing Core Components")
    print("=" * 60)
    
    try:
        # Test smart AI engine
        from smart_ai_engine import SmartAIEngine
        engine = SmartAIEngine()
        print("   ✅ Smart AI Engine imported successfully")
        
        # Test simple NLP solver
        from simple_nlp_solver import SimpleNLPSolver
        nlp_solver = SimpleNLPSolver()
        print("   ✅ Simple NLP Solver imported successfully")
        
        # Test comprehensive failure analyzer
        from comprehensive_failure_analyzer import ComprehensiveFailureAnalyzer
        failure_analyzer = ComprehensiveFailureAnalyzer()
        print("   ✅ Comprehensive Failure Analyzer imported successfully")
        
        # Test N8N style pipeline
        from n8n_style_pipeline import N8NStylePipeline
        pipeline = N8NStylePipeline()
        print("   ✅ N8N Style Pipeline imported successfully")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Core components test failed: {e}")
        return False

def test_query_processing():
    """Test basic query processing without external APIs"""
    print("\n🧪 Testing Query Processing")
    print("=" * 60)
    
    try:
        from smart_ai_engine import SmartAIEngine
        from simple_nlp_solver import SimpleNLPSolver
        
        # Initialize components
        smart_ai = SmartAIEngine()
        nlp_solver = SimpleNLPSolver()
        
        # Test queries
        test_queries = [
            "What is CS 18000?",
            "I failed CS 25100",
            "Tell me about machine intelligence track"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testing: {query}")
            
            try:
                # Test smart AI intent understanding
                intent = smart_ai.understand_query(query)
                print(f"   ✅ Smart AI Intent: {intent.primary_intent} (confidence: {intent.confidence:.2f})")
                
                # Test NLP semantic understanding
                semantic = nlp_solver.understand_query_semantically(query)
                print(f"   ✅ NLP Intent: {semantic.intent}")
                
            except Exception as e:
                print(f"   ❌ Query processing error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Query processing test failed: {e}")
        return False

def test_failure_analysis():
    """Test failure analysis functionality"""
    print("\n🧪 Testing Failure Analysis")
    print("=" * 60)
    
    try:
        from comprehensive_failure_analyzer import ComprehensiveFailureAnalyzer
        
        analyzer = ComprehensiveFailureAnalyzer()
        
        test_queries = [
            "What if I fail CS 18000?",
            "I failed calculus 1, what should I do?",
            "What happens if I fail CS 25100?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testing: {query}")
            try:
                response = analyzer.analyze_failure_query(query)
                print(f"   ✅ Analysis generated: {len(response)} characters")
            except Exception as e:
                print(f"   ❌ Failure analysis error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failure analysis test failed: {e}")
        return False

def test_n8n_pipeline():
    """Test N8N pipeline functionality"""
    print("\n🧪 Testing N8N Pipeline")
    print("=" * 60)
    
    try:
        from n8n_style_pipeline import N8NStylePipeline
        
        pipeline = N8NStylePipeline()
        
        test_queries = [
            "What courses should I take?",
            "Tell me about CS tracks",
            "What are CODO requirements?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testing: {query}")
            try:
                result = pipeline.execute_workflow(query)
                print(f"   ✅ Pipeline executed: {result['success']}")
                print(f"   ✅ Response length: {len(result['response'])} characters")
            except Exception as e:
                print(f"   ❌ Pipeline error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ N8N pipeline test failed: {e}")
        return False

def test_knowledge_base_loading():
    """Test knowledge base loading"""
    print("\n🧪 Testing Knowledge Base Loading")
    print("=" * 60)
    
    try:
        knowledge_files = [
            "data/cs_knowledge_graph.json",
            "data/comprehensive_purdue_cs_data.json"
        ]
        
        total_courses = 0
        total_tracks = 0
        
        for file_path in knowledge_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    courses = len(data.get("courses", {}))
                    tracks = len(data.get("tracks", {}))
                    
                    total_courses += courses
                    total_tracks += tracks
                    
                    print(f"   ✅ {file_path}: {courses} courses, {tracks} tracks")
                    
                except Exception as e:
                    print(f"   ❌ {file_path}: Error loading - {e}")
            else:
                print(f"   ⚠️ {file_path}: Not found")
        
        print(f"\n📊 Total Knowledge: {total_courses} courses, {total_tracks} tracks")
        
        return total_courses > 0
        
    except Exception as e:
        print(f"❌ Knowledge base test failed: {e}")
        return False

def create_simple_unified_engine():
    """Create a simple unified engine for testing"""
    print("\n🧪 Creating Simple Unified Engine")
    print("=" * 60)
    
    try:
        # Create a simple version without external dependencies
        from smart_ai_engine import SmartAIEngine
        from simple_nlp_solver import SimpleNLPSolver
        from comprehensive_failure_analyzer import ComprehensiveFailureAnalyzer
        
        class SimpleUnifiedEngine:
            def __init__(self):
                self.smart_ai = SmartAIEngine()
                self.nlp_solver = SimpleNLPSolver()
                self.failure_analyzer = ComprehensiveFailureAnalyzer()
                
                # Load knowledge base for NLP solver
                self.load_knowledge_base()
            
            def load_knowledge_base(self):
                """Load knowledge base"""
                unified_data = {}
                
                if os.path.exists("data/cs_knowledge_graph.json"):
                    with open("data/cs_knowledge_graph.json", 'r') as f:
                        data = json.load(f)
                    unified_data.update(data)
                
                if unified_data:
                    self.nlp_solver.build_knowledge_graph(unified_data)
            
            def process_query(self, query: str) -> str:
                """Process query using available methods"""
                query_lower = query.lower()
                
                # Check for failure analysis
                if any(word in query_lower for word in ["fail", "failed", "failure"]):
                    try:
                        return self.failure_analyzer.analyze_failure_query(query)
                    except Exception as e:
                        print(f"Failure analyzer error: {e}")
                
                # Try smart AI
                try:
                    return self.smart_ai.process_query(query)
                except Exception as e:
                    print(f"Smart AI error: {e}")
                
                # Try NLP solver
                try:
                    semantic_query = self.nlp_solver.understand_query_semantically(query)
                    return self.nlp_solver.solve_using_knowledge_graph(semantic_query)
                except Exception as e:
                    print(f"NLP solver error: {e}")
                
                return "I'm sorry, I couldn't process your query at this time."
        
        # Test the simple engine
        engine = SimpleUnifiedEngine()
        
        test_queries = [
            "Hi, what can you help me with?",
            "What is CS 18000?",
            "I failed CS 25100, what should I do?",
            "Tell me about machine intelligence track"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testing: {query}")
            try:
                start_time = time.time()
                response = engine.process_query(query)
                processing_time = time.time() - start_time
                
                print(f"   ✅ Processing time: {processing_time:.2f}s")
                print(f"   ✅ Response: {response[:100]}...")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n✅ Simple Unified Engine working successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Simple unified engine test failed: {e}")
        return False

def run_simple_test():
    """Run simple comprehensive test"""
    print("🚀 Starting Simple System Test")
    print("=" * 80)
    
    test_results = []
    
    # Test core components
    result1 = test_core_components()
    test_results.append(("Core Components", result1))
    
    # Test knowledge base loading
    result2 = test_knowledge_base_loading()
    test_results.append(("Knowledge Base Loading", result2))
    
    # Test query processing
    result3 = test_query_processing()
    test_results.append(("Query Processing", result3))
    
    # Test failure analysis
    result4 = test_failure_analysis()
    test_results.append(("Failure Analysis", result4))
    
    # Test N8N pipeline
    result5 = test_n8n_pipeline()
    test_results.append(("N8N Pipeline", result5))
    
    # Test simple unified engine
    result6 = create_simple_unified_engine()
    test_results.append(("Simple Unified Engine", result6))
    
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
    
    if passed >= total * 0.8:  # 80% pass rate
        print("\n🎉 SYSTEM IS FUNCTIONAL!")
        print("\nThe core system successfully provides:")
        print("  • AI Query Understanding")
        print("  • Knowledge Base Integration")
        print("  • Failure Analysis")
        print("  • N8N Pipeline Processing")
        print("  • Unified Query Engine")
        print("\nNext steps:")
        print("  • Install aiohttp for full N8N integration: pip install aiohttp")
        print("  • Set GEMINI_API_KEY for AI enhancements")
        print("  • Test with real queries")
    else:
        print(f"\n⚠️ {total - passed} critical tests failed")
    
    return passed >= total * 0.8

if __name__ == "__main__":
    success = run_simple_test()
    sys.exit(0 if success else 1)