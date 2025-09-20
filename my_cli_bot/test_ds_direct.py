#!/usr/bin/env python3
"""
Direct test of Data Science course handler
"""

import sys
import os

# Add the directory containing our modules to the Python path
sys.path.append('/Users/rrao/Desktop/BCLI/my_cli_bot')

from intelligent_conversation_manager import IntelligentConversationManager

def test_ds_course_handler_direct():
    """Test the Data Science course handler directly"""
    
    manager = IntelligentConversationManager()
    
    # Test cases
    test_cases = [
        ("ILS 23000", "What is ILS 23000?"),
        ("PHIL 20700", "Tell me about PHIL 20700"),
        ("PHIL 20800", "What do you learn in PHIL 20800?"),
        ("MA 43200", "What is MA 43200 about?"),
        ("STAT 42000", "Tell me about STAT 42000"),
        ("CS 44100", "What is CS 44100?"),
        ("CS 25300", "What do you learn in CS 25300?"),
    ]
    
    print("=== Testing Data Science Course Handler Directly ===\n")
    
    for i, (course_code, query) in enumerate(test_cases, 1):
        print(f"Test {i}: {course_code} - {query}")
        print("-" * 60)
        
        try:
            response = manager._handle_data_science_course_query(course_code, query)
            print(response)
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    test_ds_course_handler_direct()