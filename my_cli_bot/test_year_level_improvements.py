#!/usr/bin/env python3
"""
Test script for year-level course planning and debug mode improvements
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_year_level_queries():
    """Test queries for all year levels"""
    
    from boiler_ai_complete import BoilerAIComplete
    
    print("🧪 Testing Year-Level Course Planning Improvements")
    print("=" * 60)
    
    # Initialize with debug mode
    boiler_ai = BoilerAIComplete(debug_mode=True)
    
    # Test queries for each year level
    test_queries = [
        # Freshman queries
        "What courses should a freshman take in computer science?",
        "What are the compulsory courses for freshman?",
        "I'm a first year student, what should I start with?",
        
        # Sophomore queries  
        "What courses should a sophomore take?",
        "I'm a second year CS student, what's next?",
        "Sophomore computer science course requirements",
        
        # Junior queries
        "What courses should a junior take?", 
        "Third year CS course planning",
        "I'm a junior, what track courses should I choose?",
        
        # Senior queries
        "What courses should a senior take?",
        "Fourth year CS requirements",
        "Senior capstone course planning",
        
        # Original problematic query
        "Hi there, so what are some courses compulsory courses that a freshman should be taking as a computer science major"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {query}")
        print('='*80)
        
        try:
            response = boiler_ai.ask_question(query)
            print(f"✅ Response generated successfully")
            print(f"📝 Response length: {len(response)} characters")
            
            # Check if response is appropriate
            if "Software Engineering track course options" in response:
                print("❌ ERROR: Still routing to SE track incorrectly!")
            elif any(year in response.lower() for year in ["freshman", "sophomore", "junior", "senior"]):
                print("✅ SUCCESS: Year-level specific response detected")
            else:
                print("⚠️  WARNING: Response doesn't seem year-level specific")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print("-" * 80)

if __name__ == "__main__":
    test_year_level_queries()