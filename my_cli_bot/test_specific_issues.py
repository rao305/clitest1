#!/usr/bin/env python3
"""
Test specific AI issues with knowledge base extraction
"""

from simple_boiler_ai import SimpleBoilerAI
import io
from contextlib import redirect_stdout, redirect_stderr

def test_knowledge_extraction():
    print("Testing Knowledge Extraction Issues")
    print("=" * 40)

    # Initialize AI with suppressed output
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
        bot = SimpleBoilerAI()

    # Test 1: Prerequisites extraction
    print("\n--- Testing Prerequisites Extraction ---")
    query1 = "What are the prerequisites for CS 25200?"
    relevant1 = bot.extract_relevant_knowledge(query1)
    print(f"Query: {query1}")
    print(f"Extracted sections: {list(relevant1.keys())}")
    if 'prerequisites' in relevant1:
        print(f"Prerequisites for CS 25200: {relevant1['prerequisites'].get('CS 25200', 'Not found')}")

    # Test 2: CODO extraction
    print("\n--- Testing CODO Extraction ---")
    query2 = "What are the CODO requirements?"
    relevant2 = bot.extract_relevant_knowledge(query2)
    print(f"Query: {query2}")
    print(f"Extracted sections: {list(relevant2.keys())}")
    if 'codo_requirements' in relevant2:
        print(f"CODO requirements found: {relevant2['codo_requirements']}")

    # Test 3: Full AI response with prerequisites
    print("\n--- Testing Full AI Response with Prerequisites ---")
    response = bot.get_general_ai_response(query1)
    print(f"AI Response: {response}")

    # Test 4: Full AI response with CODO
    print("\n--- Testing Full AI Response with CODO ---")
    response2 = bot.get_general_ai_response(query2)
    print(f"AI Response: {response2}")

if __name__ == "__main__":
    test_knowledge_extraction()