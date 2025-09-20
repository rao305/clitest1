#!/usr/bin/env python3
"""
Test script to demonstrate Roo CS Advisor interaction
"""

from roo_engine import RooCSAdvisor

def test_questions():
    """Test some sample questions with Roo"""
    
    # Initialize Roo
    roo = RooCSAdvisor()
    
    # Test questions
    questions = [
        "What are the six core CS courses?",
        "What are the prerequisites for CS 25000?",
        "Can you help me with course planning?"
    ]
    
    print("🤖 Testing Roo CS Advisor responses:")
    print("=" * 50)
    
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * 40)
        
        # Get response
        response = roo.generate_response(question, [])
        print(f"Answer: {response}")
        
        print()

if __name__ == "__main__":
    test_questions()