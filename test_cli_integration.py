#!/usr/bin/env python3
"""
Test CLI Integration with BoilerAI
==================================

This script tests the CLI integration to ensure it meets the BoilerAI requirements.
"""

import sys
import os

# Add CLI path
cli_path = r"C:\Users\raoro\OneDrive\Desktop\clitest1-main\my_cli_bot"
sys.path.insert(0, cli_path)

def test_cli_integration():
    """Test CLI integration with BoilerAI"""
    try:
        # Try to import your CLI
        from simple_boiler_ai import SimpleBoilerAI
        from api_key_manager import setup_api_key
        
        print("Note: This test will prompt for API key...")
        print("You can use a dummy key for testing: 'test-key'")
        print()
        
        # For testing, we'll use a dummy API key to avoid prompting
        # In real usage, you would call: provider, api_key = setup_api_key()
        cli = SimpleBoilerAI(api_key="test-key")
        
        # Test queries
        test_queries = [
            "What are the CS core requirements?",
            "How do I plan my CS degree?",
            "What courses should I take next semester?",
            "What is CS 18000?",
            "How do I CODO into CS?"
        ]
        
        print("Testing CLI Integration...")
        print("=" * 50)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\nTest {i}: {query}")
            print("-" * 30)
            
            try:
                result = cli.process_query(query)
                
                if isinstance(result, dict):
                    print(f"[OK] Response: {result.get('response', 'No response')[:100]}...")
                    print(f"[OK] Thinking: {result.get('thinking', 'No thinking')[:50]}...")
                    print(f"[OK] Sources: {len(result.get('sources', []))} sources")
                    print(f"[OK] Confidence: {result.get('confidence', 'N/A')}")
                    
                    # Validate required keys
                    required_keys = ['response', 'thinking', 'sources', 'confidence']
                    missing_keys = [key for key in required_keys if key not in result]
                    if missing_keys:
                        print(f"[WARNING] Missing required keys: {missing_keys}")
                    else:
                        print("[OK] All required keys present")
                        
                else:
                    print(f"[WARNING] Non-dict result: {type(result)}")
                    print(f"[INFO] Content: {str(result)[:100]}...")
                    
            except Exception as e:
                print(f"[ERROR] Error: {e}")
        
        print("\n" + "=" * 50)
        print("[OK] CLI Integration Test Complete!")
        
        # Test error handling
        print("\nTesting Error Handling...")
        print("-" * 30)
        try:
            error_result = cli.process_query("")
            if isinstance(error_result, dict):
                print(f"[OK] Empty query handled: {error_result.get('response', 'No response')[:50]}...")
            else:
                print(f"[WARNING] Empty query returned: {type(error_result)}")
        except Exception as e:
            print(f"[ERROR] Error handling failed: {e}")
        
    except ImportError as e:
        print(f"[ERROR] Import Error: {e}")
        print("Make sure your CLI file is in the correct location and has the required interface.")
    except Exception as e:
        print(f"[ERROR] Test Error: {e}")

if __name__ == "__main__":
    test_cli_integration()
