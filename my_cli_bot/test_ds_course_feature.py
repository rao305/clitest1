#!/usr/bin/env python3
"""
Test script for Data Science course query feature
"""

import sys
import os

# Add the directory containing our modules to the Python path
sys.path.append('/Users/rrao/Desktop/BCLI/my_cli_bot')

from intelligent_conversation_manager import IntelligentConversationManager

def test_data_science_course_queries():
    """Test the Data Science course query feature"""
    
    manager = IntelligentConversationManager()
    session_id = "test_ds_session"
    
    # Test cases for Data Science courses
    test_queries = [
        # Ethics selective courses
        "What is ILS 23000?",
        "Tell me about PHIL 20700",
        "What do you learn in PHIL 20800?",
        
        # Statistics selective courses  
        "What is MA 43200 about?",
        "Tell me about STAT 42000",
        "What do you learn in STAT 51200?",
        "What is STAT 50600?",
        
        # Capstone courses
        "What is CS 44100?",
        "Tell me about CS 49000",
        
        # Core courses
        "What is CS 25300 about?",
        "What do you learn in STAT 35500?",
        
        # Non-DS course (should use regular processing)
        "What is CS 25100?",
        
        # Learning outcomes specific query
        "What are the learning outcomes for ILS 23000?",
        "What do you learn in MA 43200?"
    ]
    
    print("=== Testing Data Science Course Query Feature ===\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"Test {i}: {query}")
        print("-" * 50)
        
        try:
            response = manager.process_query(session_id, query)
            print(response)
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_data_science_course_queries()