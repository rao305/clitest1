#!/usr/bin/env python3
"""
Test the improved AI system with knowledge base integration
"""

from simple_boiler_ai import SimpleBoilerAI
import io
from contextlib import redirect_stdout, redirect_stderr

def test_improved_ai():
    print("Testing Improved AI System with Knowledge Base Integration")
    print("=" * 60)

    # Initialize AI with suppressed output
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
        bot = SimpleBoilerAI()

    test_queries = [
        "What is CS 25100?",
        "What tracks are available for CS students?",
        "What are the prerequisites for CS 25200?",
        "Tell me about the Machine Intelligence track",
        "What are the CODO requirements?",
        "What courses should a sophomore take in fall semester?"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i}: {query} ---")
        try:
            response = bot.get_ai_response(query)
            print(f"Response: {response}")

            # Analysis of response quality
            if len(response) < 30:
                print("[WARNING] Response seems too short")
            if "track" in query.lower() and ("Machine Intelligence" not in response and "Software Engineering" not in response):
                print("[WARNING] Track response missing track names")
            if "prerequisite" in query.lower() and len(response) < 50:
                print("[WARNING] Prerequisite response seems incomplete")

        except Exception as e:
            print(f"[ERROR] Query failed: {e}")

if __name__ == "__main__":
    test_improved_ai()