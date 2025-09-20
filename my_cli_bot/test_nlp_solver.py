#!/usr/bin/env python3
"""
Test NLP Knowledge Solver
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_ai_engine import SmartAIEngine

def test_nlp_solver():
    """Test that the NLP knowledge solver works with proper semantic understanding"""
    
    print("🧠 TESTING NLP KNOWLEDGE SOLVER")
    print("=" * 50)
    
    engine = SmartAIEngine()
    
    # Test queries that should trigger NLP understanding
    test_queries = [
        "I want to graduate with both machine intelligence and software engineering tracks",
        "How hard is CS 25100?",
        "What courses should I take as a freshman?",
        "Which track should I choose for AI careers?",
        "What are the prerequisites for CS 37300?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 40)
        
        try:
            response = engine.process_query(query)
            
            # Check if response uses NLP and knowledge graphs
            if "SEMANTIC" in response and "KNOWLEDGE GRAPH" in response:
                print("✅ NLP KNOWLEDGE SOLVER DETECTED")
                print(f"Response length: {len(response)} characters")
                print(f"Contains semantic analysis: {'SEMANTIC' in response}")
                print(f"Contains knowledge graph: {'KNOWLEDGE GRAPH' in response}")
                print(f"Preview: {response[:200]}...")
            else:
                print("❌ RESPONSE NOT USING NLP SOLVER")
                print(f"Response: {response}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print(f"\n{'='*50}")
    print("🏁 NLP SOLVER TEST COMPLETED")

if __name__ == "__main__":
    test_nlp_solver() 