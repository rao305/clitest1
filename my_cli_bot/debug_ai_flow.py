#!/usr/bin/env python3
"""
Debug the AI flow to see why degree progression isn't being used
"""

from simple_boiler_ai import SimpleBoilerAI
import io
from contextlib import redirect_stdout, redirect_stderr

def debug_ai_flow():
    print("Debugging AI Flow for Sophomore Fall Query")
    print("=" * 50)

    bot = SimpleBoilerAI()
    query = "What courses should a sophomore take in fall semester?"

    # Step 1: Check query classification
    classification = bot.classify_query_for_hybrid_routing(query)
    print(f"Query classification: {classification}")

    # Step 2: Check if it goes through SQL or JSON path
    query_lower = query.lower()

    # Check year/semester detection
    student_year = "unknown"
    semester = "unknown"

    if "freshman" in query_lower or "first year" in query_lower:
        student_year = "freshman"
    elif "sophomore" in query_lower or "second year" in query_lower:
        student_year = "sophomore"
    elif "junior" in query_lower or "third year" in query_lower:
        student_year = "junior"
    elif "senior" in query_lower or "fourth year" in query_lower:
        student_year = "senior"

    if "fall" in query_lower:
        semester = "fall"
    elif "spring" in query_lower:
        semester = "spring"

    print(f"Detected year: {student_year}")
    print(f"Detected semester: {semester}")
    print(f"Should use degree progression: {student_year != 'unknown' and semester != 'unknown'}")

    # Step 3: Test the degree progression engine directly
    if student_year != "unknown" and semester != "unknown":
        try:
            from degree_progression_engine import get_accurate_semester_recommendation
            accurate_response = get_accurate_semester_recommendation(student_year, semester, [])
            print("\nDegree progression engine output:")
            print(accurate_response[:300] + "...")
        except Exception as e:
            print(f"Degree progression engine failed: {e}")

    # Step 4: See what the AI actually returns
    print("\nActual AI response:")
    response = bot.get_ai_response(query)
    print(response[:300] + "...")

if __name__ == "__main__":
    debug_ai_flow()