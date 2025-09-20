#!/usr/bin/env python3
"""
Test script for AI system - diagnose knowledge base and AI behavior issues
"""

import sys
import os
import json
import traceback

def test_knowledge_base():
    """Test knowledge base loading and structure"""
    print("=== Testing Knowledge Base ===")

    try:
        # Test JSON knowledge base loading
        knowledge_file = "data/cs_knowledge_graph.json"
        if os.path.exists(knowledge_file):
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                kb = json.load(f)

            print(f"[OK] Knowledge base loaded successfully")
            print(f"[OK] Found {len(kb.get('courses', {}))} courses")
            print(f"[OK] Found {len(kb.get('tracks', {}))} tracks")

            # Test specific course data
            if 'CS 25100' in kb.get('courses', {}):
                cs251 = kb['courses']['CS 25100']
                print(f"[OK] CS 25100 data: {cs251.get('title', 'No title')}")
                print(f"[OK] CS 25100 difficulty: {cs251.get('difficulty_level', 'No difficulty')}")
            else:
                print("[ERROR] CS 25100 not found in knowledge base")

            # Test track data
            tracks = kb.get('tracks', {})
            print(f"[OK] Available tracks: {list(tracks.keys())}")

            return True, kb
        else:
            print(f"[ERROR] Knowledge base file not found: {knowledge_file}")
            return False, None

    except Exception as e:
        print(f"[ERROR] Knowledge base loading failed: {e}")
        traceback.print_exc()
        return False, None

def test_ai_initialization():
    """Test AI system initialization"""
    print("\n=== Testing AI System Initialization ===")

    try:
        # Import with modified print handling
        import io
        from contextlib import redirect_stdout, redirect_stderr

        # Capture outputs to avoid Unicode errors
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            from simple_boiler_ai import SimpleBoilerAI
            bot = SimpleBoilerAI()

        # Check what was captured
        stdout_content = stdout_capture.getvalue()
        stderr_content = stderr_capture.getvalue()

        if stdout_content:
            print(f"Stdout captured: {stdout_content[:200]}...")
        if stderr_content:
            print(f"Stderr captured: {stderr_content[:200]}...")

        print("[OK] AI system initialized successfully")
        return True, bot

    except Exception as e:
        print(f"[ERROR] AI system initialization failed: {e}")
        traceback.print_exc()
        return False, None

def test_knowledge_extraction(bot, kb):
    """Test knowledge extraction methods"""
    print("\n=== Testing Knowledge Extraction ===")

    try:
        # Test 1: Course extraction
        query1 = "What is CS 25100?"
        relevant = bot.extract_relevant_knowledge(query1)
        print(f"[OK] Query: '{query1}'")
        print(f"[OK] Extracted courses: {list(relevant.get('courses', {}).keys())}")

        # Test 2: Track extraction
        query2 = "What are the machine intelligence track requirements?"
        relevant2 = bot.extract_relevant_knowledge(query2)
        print(f"[OK] Query: '{query2}'")
        print(f"[OK] Extracted tracks: {list(relevant2.get('tracks', {}).keys())}")

        # Test 3: CODO extraction
        query3 = "What are the CODO requirements?"
        relevant3 = bot.extract_relevant_knowledge(query3)
        print(f"[OK] Query: '{query3}'")
        print(f"[OK] Has CODO info: {'codo_requirements' in relevant3}")

        return True

    except Exception as e:
        print(f"[ERROR] Knowledge extraction failed: {e}")
        traceback.print_exc()
        return False

def test_ai_responses(bot):
    """Test AI response generation"""
    print("\n=== Testing AI Response Generation ===")

    test_queries = [
        "What is CS 25100?",
        "What tracks are available?",
        "What are the prerequisites for CS 25200?",
        "Tell me about Machine Intelligence track"
    ]

    for i, query in enumerate(test_queries, 1):
        try:
            print(f"\n--- Test {i}: {query} ---")

            # Test the AI response
            response = bot.get_ai_response(query)

            if response:
                print(f"[OK] Response received ({len(response)} chars)")
                print(f"Response preview: {response[:150]}...")

                # Check for common issues
                if "I'm having trouble" in response or "error" in response.lower():
                    print("[WARNING] Response indicates an error")
                if len(response) < 50:
                    print("[WARNING] Response seems too short")

            else:
                print("[ERROR] No response received")

        except Exception as e:
            print(f"[ERROR] Query failed: {e}")
            traceback.print_exc()

def main():
    """Main test function"""
    print("Boiler AI System Diagnostic Test")
    print("=" * 50)

    # Test 1: Knowledge Base
    kb_success, kb = test_knowledge_base()
    if not kb_success:
        print("Cannot proceed without knowledge base")
        return

    # Test 2: AI Initialization
    ai_success, bot = test_ai_initialization()
    if not ai_success:
        print("Cannot proceed without AI system")
        return

    # Test 3: Knowledge Extraction
    extraction_success = test_knowledge_extraction(bot, kb)

    # Test 4: AI Responses
    test_ai_responses(bot)

    print("\n=== Diagnostic Summary ===")
    print(f"Knowledge Base: {'[OK]' if kb_success else '[ERROR]'}")
    print(f"AI System: {'[OK]' if ai_success else '[ERROR]'}")
    print(f"Knowledge Extraction: {'[OK]' if extraction_success else '[ERROR]'}")
    print("\nDiagnostic complete!")

if __name__ == "__main__":
    main()