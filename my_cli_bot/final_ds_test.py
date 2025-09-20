#!/usr/bin/env python3
"""
Final comprehensive test of Data Science course feature
"""

import sys
import os

# Add the directory containing our modules to the Python path
sys.path.append('/Users/rrao/Desktop/BCLI/my_cli_bot')

from intelligent_conversation_manager import IntelligentConversationManager

def test_final_ds_course_system():
    """Final test of Data Science course system"""
    
    manager = IntelligentConversationManager()
    session_id = "final_test_session"
    
    # Test cases to verify the feature works exactly as requested
    test_cases = [
        "What is ILS 23000?",                    # Should show description + prompt for learning outcomes
        "What do you learn in PHIL 20800?",     # Should show description + learning outcomes immediately  
        "Tell me about MA 43200",               # Should show description + prompt for learning outcomes
        "What is STAT 42000?",                  # Should show description + prompt for learning outcomes
        "What are the learning outcomes for ILS 23000?",  # Should show description + learning outcomes
        "What is CS 44100?",                    # Capstone course
        "What is CS 25100?",                    # Non-DS course (should use regular system)
    ]
    
    print("=== Final Data Science Course Feature Test ===\n")
    
    for i, query in enumerate(test_cases, 1):
        print(f"Test {i}: {query}")
        print("-" * 60)
        
        try:
            response = manager.process_query(session_id, query)
            # Extract just the main response, ignore logging
            lines = response.split('\n')
            main_response_lines = []
            for line in lines:
                # Skip logging lines but keep the actual response
                if not line.startswith('Context extraction error:') and not line.startswith('✓ Loaded'):
                    main_response_lines.append(line)
            
            main_response = '\n'.join(main_response_lines).strip()
            print(main_response)
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    test_final_ds_course_system()