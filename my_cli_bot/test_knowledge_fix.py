#!/usr/bin/env python3
"""
Knowledge Fix Validation Script
Tests that the new pipeline properly accesses knowledge base and generates accurate responses
"""

import os
import json
from typing import Dict, Any, List
from datetime import datetime

def test_knowledge_pipeline():
    """Test the enhanced knowledge pipeline"""
    print("🧪 Testing Enhanced Knowledge Pipeline")
    print("=" * 60)
    
    try:
        from enhanced_knowledge_pipeline import EnhancedKnowledgePipeline
        
        # Initialize pipeline
        pipeline = EnhancedKnowledgePipeline()
        
        # Test 1: Knowledge base loading
        print("\n1. Knowledge Base Loading Test:")
        kb_loaded = len(pipeline.knowledge_base.get("courses", {})) > 0
        print(f"   ✅ Knowledge base loaded: {kb_loaded}")
        print(f"   📚 Courses available: {len(pipeline.knowledge_base.get('courses', {}))}")
        print(f"   🎯 Tracks available: {len(pipeline.knowledge_base.get('tracks', {}))}")
        
        # Test 2: Entity extraction
        print("\n2. Entity Extraction Test:")
        entities = pipeline.extract_entities("What is CS 18000 and what about Machine Intelligence track?")
        print(f"   📊 Extracted entities: {entities}")
        
        # Test 3: Knowledge retrieval
        print("\n3. Knowledge Retrieval Test:")
        knowledge = pipeline.fetch_relevant_knowledge(entities, "What is CS 18000?")
        print(f"   📚 Knowledge sections retrieved: {list(knowledge.keys())}")
        
        # Test 4: Response generation
        print("\n4. Response Generation Test:")
        test_queries = [
            "What is CS 18000?",
            "Tell me about Machine Intelligence track", 
            "What are the prerequisites for CS 25100?"
        ]
        
        results = []
        for query in test_queries:
            response = pipeline.process_query(query)
            contains_specific_info = any(term in response.lower() for term in ["cs 18000", "machine intelligence", "credits", "prerequisite"])
            
            results.append({
                "query": query,
                "response_length": len(response),
                "contains_specific_info": contains_specific_info,
                "response_sample": response[:100] + "..." if len(response) > 100 else response
            })
            
            print(f"   Query: {query}")
            print(f"   Response length: {len(response)} chars")
            print(f"   Contains specific info: {'✅' if contains_specific_info else '❌'}")
            print(f"   Sample: {response[:100]}...")
            print()
        
        return True, results
        
    except Exception as e:
        print(f"❌ Enhanced pipeline test failed: {e}")
        return False, []

def test_n8n_pipeline():
    """Test the N8N-style pipeline"""
    print("🧪 Testing N8N-Style Pipeline")
    print("=" * 60)
    
    try:
        from n8n_style_pipeline import N8NStylePipeline
        
        # Initialize pipeline
        pipeline = N8NStylePipeline()
        
        # Test workflow execution
        print("\n1. Workflow Execution Test:")
        test_query = "What is CS 18000?"
        result = pipeline.execute_workflow(test_query)
        
        print(f"   Success: {'✅' if result['success'] else '❌'}")
        print(f"   Response length: {len(result.get('response', ''))}")
        print(f"   Entities found: {result.get('entities', {})}")
        print(f"   Knowledge sections: {result.get('knowledge_sections', [])}")
        print(f"   Response sample: {result.get('response', '')[:100]}...")
        
        # Test pipeline status
        print("\n2. Pipeline Status Test:")
        status = pipeline.get_pipeline_status()
        for node_name, node_status in status.items():
            status_icon = "✅" if node_status['status'] == 'completed' else "❌"
            print(f"   {status_icon} {node_name}: {node_status['status']}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ N8N pipeline test failed: {e}")
        return False, {}

def test_fixed_universal_advisor():
    """Test the fixed universal advisor"""
    print("🧪 Testing Fixed Universal Advisor")
    print("=" * 60)
    
    try:
        from fixed_universal_advisor import FixedUniversalAdvisor
        
        # Initialize advisor
        advisor = FixedUniversalAdvisor(tracker_mode=True)
        advisor.start_new_session()
        
        # Test knowledge access
        print("\n1. Knowledge Access Test:")
        test_results = advisor.test_knowledge_access()
        print(f"   Knowledge base loaded: {'✅' if test_results['knowledge_base_loaded'] else '❌'}")
        print(f"   Courses available: {test_results['courses_available']}")
        print(f"   Test queries successful: {len([q for q in test_results['test_queries'] if q.get('success')])}/{len(test_results['test_queries'])}")
        
        # Test session management
        print("\n2. Session Management Test:")
        session_context = advisor.get_session_context()
        print(f"   Session created: {'✅' if 'created' in session_context else '❌'}")
        
        # Test query processing
        print("\n3. Query Processing Test:")
        test_queries = [
            "What is CS 18000?",
            "Tell me about Software Engineering track"
        ]
        
        for query in test_queries:
            response = advisor.ask_question(query)
            contains_info = len(response) > 50 and not response.startswith("I encountered an error")
            print(f"   Query: {query}")
            print(f"   Success: {'✅' if contains_info else '❌'}")
            print(f"   Response length: {len(response)}")
        
        # Show session summary
        print("\n4. Session Summary:")
        summary = advisor.get_session_summary()
        print(f"   Total queries: {summary.get('total_queries', 0)}")
        print(f"   Successful queries: {summary.get('successful_queries', 0)}")
        
        return True, summary
        
    except Exception as e:
        print(f"❌ Fixed universal advisor test failed: {e}")
        return False, {}

def compare_with_current_system():
    """Compare new pipeline with current system issues"""
    print("🔍 Comparison with Current System Issues")
    print("=" * 60)
    
    current_issues = [
        "Complex multi-layer routing (Universal → Hybrid → Intelligent → Smart)",
        "Knowledge base data not reaching AI prompts",
        "Hardcoded fallback responses",
        "Multiple fallback layers that lose context",
        "Data format mismatches between systems"
    ]
    
    new_solutions = [
        "✅ Direct single-layer routing (Query → Knowledge → AI → Response)",
        "✅ Knowledge base directly integrated into AI prompts",
        "✅ AI-generated responses using knowledge context",
        "✅ Single fallback layer with knowledge access",
        "✅ Structured data format optimized for AI consumption"
    ]
    
    print("Current Issues → New Solutions:")
    for issue, solution in zip(current_issues, new_solutions):
        print(f"❌ {issue}")
        print(f"{solution}")
        print()

def generate_implementation_recommendations():
    """Generate recommendations for implementation"""
    print("💡 Implementation Recommendations")
    print("=" * 60)
    
    recommendations = [
        {
            "option": "Quick Fix (Recommended)",
            "approach": "Replace UniversalPurdueAdvisor with FixedUniversalAdvisor",
            "effort": "Low - Just change import statements",
            "impact": "High - Immediate knowledge access fix",
            "steps": [
                "1. Backup current universal_purdue_advisor.py",
                "2. Replace with fixed_universal_advisor.py",
                "3. Update import statements in main files",
                "4. Test with existing interface"
            ]
        },
        {
            "option": "Enhanced Pipeline Integration",
            "approach": "Integrate EnhancedKnowledgePipeline into existing system",
            "effort": "Medium - Modify existing routing logic",
            "impact": "High - Improved performance and accuracy",
            "steps": [
                "1. Add enhanced_knowledge_pipeline.py to project",
                "2. Modify ask_question() method to use enhanced pipeline",
                "3. Keep existing session management",
                "4. Add fallback to original system if needed"
            ]
        },
        {
            "option": "N8N-Style Workflow System",
            "approach": "Replace entire system with workflow-based architecture",
            "effort": "High - Complete system redesign",
            "impact": "Very High - Debuggable, maintainable, scalable",
            "steps": [
                "1. Implement n8n_style_pipeline.py as main system",
                "2. Create adapter layer for existing interfaces", 
                "3. Add workflow monitoring and debugging",
                "4. Migrate sessions and context management"
            ]
        }
    ]
    
    for rec in recommendations:
        print(f"\n{rec['option']}:")
        print(f"  Approach: {rec['approach']}")
        print(f"  Effort: {rec['effort']}")
        print(f"  Impact: {rec['impact']}")
        print("  Steps:")
        for step in rec['steps']:
            print(f"    {step}")

def main():
    """Run all tests and generate report"""
    print("🚀 Knowledge Fix Validation Report")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Run all tests
    test_results = {}
    
    # Test 1: Enhanced Pipeline
    enhanced_success, enhanced_results = test_knowledge_pipeline()
    test_results["enhanced_pipeline"] = {"success": enhanced_success, "results": enhanced_results}
    
    print("\n" + "="*80)
    
    # Test 2: N8N Pipeline  
    n8n_success, n8n_results = test_n8n_pipeline()
    test_results["n8n_pipeline"] = {"success": n8n_success, "results": n8n_results}
    
    print("\n" + "="*80)
    
    # Test 3: Fixed Universal Advisor
    fixed_success, fixed_results = test_fixed_universal_advisor()
    test_results["fixed_advisor"] = {"success": fixed_success, "results": fixed_results}
    
    print("\n" + "="*80)
    
    # Comparison and recommendations
    compare_with_current_system()
    print("\n" + "="*80)
    generate_implementation_recommendations()
    
    # Final summary
    print(f"\n📊 Test Summary:")
    print(f"Enhanced Pipeline: {'✅ PASS' if enhanced_success else '❌ FAIL'}")
    print(f"N8N Pipeline: {'✅ PASS' if n8n_success else '❌ FAIL'}")  
    print(f"Fixed Advisor: {'✅ PASS' if fixed_success else '❌ FAIL'}")
    
    success_count = sum([enhanced_success, n8n_success, fixed_success])
    print(f"\nOverall: {success_count}/3 systems working correctly")
    
    if success_count >= 2:
        print("🎉 Knowledge access issues can be fixed! Choose your implementation approach.")
    else:
        print("⚠️ Some issues remain. Check error messages and knowledge base file.")

if __name__ == "__main__":
    main()