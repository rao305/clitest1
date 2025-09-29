#!/usr/bin/env python3
"""
BoilerAI API Key Manager
========================

Interactive script to manage API keys for BoilerAI.
Allows you to save, view, and manage your API keys.

Usage:
    python manage_api_keys.py
"""

import sys
import os
from pathlib import Path

# Add CLI path
cli_path = Path(__file__).parent / "my_cli_bot"
sys.path.insert(0, str(cli_path))

try:
    from api_key_manager import get_api_key_manager
except ImportError as e:
    print(f"Error importing API key manager: {e}")
    print("Make sure the CLI is properly set up")
    sys.exit(1)

def main():
    """Main API key management interface"""
    print("BoilerAI API Key Manager")
    print("=" * 30)
    print("Manage your saved API keys for BoilerAI")
    print()
    
    manager = get_api_key_manager()
    
    while True:
        print("Options:")
        print("1. Setup new API key")
        print("2. View saved keys")
        print("3. Manage saved keys")
        print("4. Test API key")
        print("5. Exit")
        print()
        
        choice = input("Select option (1-5): ").strip()
        
        if choice == "1":
            print("\nSetting up new API key...")
            provider, api_key = manager.setup_api_key()
            print(f"\n[SUCCESS] {provider} API key setup complete!")
            
        elif choice == "2":
            manager.list_providers()
            
        elif choice == "3":
            manager.manage_saved_keys()
            
        elif choice == "4":
            test_api_key(manager)
            
        elif choice == "5":
            print("\nGoodbye!")
            break
            
        else:
            print("[ERROR] Invalid choice. Please select 1-5.")
        
        print("\n" + "-" * 40 + "\n")

def test_api_key(manager):
    """Test an API key"""
    print("\nTest API Key")
    print("-" * 15)
    
    # Check if we have any saved keys
    saved_keys = {}
    for provider in ["openai", "gemini"]:
        key = manager.get_api_key(provider)
        if key:
            saved_keys[provider] = key
    
    if not saved_keys:
        print("[INFO] No saved API keys found.")
        print("Would you like to setup a new API key? (y/n): ", end="")
        if input().strip().lower() == 'y':
            provider, api_key = manager.setup_api_key()
            saved_keys[provider] = api_key
        else:
            return
    
    # Let user choose which key to test
    print("\nAvailable API keys:")
    providers = list(saved_keys.keys())
    for i, provider in enumerate(providers, 1):
        print(f"{i}. {provider.title()}: {saved_keys[provider][:10]}...")
    
    try:
        choice = int(input("Select API key to test (1-{}): ".format(len(providers)))) - 1
        if 0 <= choice < len(providers):
            provider = providers[choice]
            api_key = saved_keys[provider]
            
            print(f"\nTesting {provider} API key...")
            
            # Simple test - try to import and create CLI instance
            try:
                from simple_boiler_ai import SimpleBoilerAI
                cli = SimpleBoilerAI(api_key=api_key)
                
                # Test with a simple query
                result = cli.process_query("test")
                
                if isinstance(result, dict) and result.get('response'):
                    print(f"[SUCCESS] {provider} API key is working!")
                    print(f"Test response: {result['response'][:50]}...")
                else:
                    print(f"[WARNING] {provider} API key test returned unexpected result")
                    
            except Exception as e:
                print(f"[ERROR] {provider} API key test failed: {e}")
                
        else:
            print("[ERROR] Invalid choice")
            
    except ValueError:
        print("[ERROR] Invalid input")

if __name__ == "__main__":
    main()

