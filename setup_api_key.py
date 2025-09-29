#!/usr/bin/env python3
"""
Simple API Key Setup Script for BoilerAI
"""

import requests
import json

def setup_api_key():
    """Interactive API key setup"""
    print("BoilerAI API Key Setup")
    print("=" * 30)
    
    # Get provider choice
    print("Select AI Provider:")
    print("1) Gemini (Google) - Free tier available")
    print("2) OpenAI - Paid service")
    
    while True:
        choice = input("Select provider (1/2): ").strip()
        if choice == "1":
            provider = "gemini"
            print("\nGet your Gemini API key from: https://makersuite.google.com/app/apikey")
            print("Your key should start with 'AIzaSy'")
            break
        elif choice == "2":
            provider = "openai"
            print("\nGet your OpenAI API key from: https://platform.openai.com/api-keys")
            print("Your key should start with 'sk-'")
            break
        else:
            print("Invalid choice. Please select 1 or 2.")
    
    # Get API key
    api_key = input(f"\nEnter your {provider} API key: ").strip()
    
    if not api_key:
        print("No API key provided. Exiting.")
        return False
    
    # Validate API key format
    if provider == "gemini" and not api_key.startswith("AIzaSy"):
        print("Warning: Gemini API key should start with 'AIzaSy'")
    elif provider == "openai" and not api_key.startswith("sk-"):
        print("Warning: OpenAI API key should start with 'sk-'")
    
    # Send to API gateway
    try:
        url = "http://127.0.0.1:8000/api/setup"
        data = {
            "provider": provider,
            "api_key": api_key
        }
        
        print(f"\nSending API key to server...")
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API gateway.")
        print("Make sure the server is running on http://127.0.0.1:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_query():
    """Test a query after API key setup"""
    print("\nTesting query...")
    
    try:
        url = "http://127.0.0.1:8000/api/query"
        data = {
            "query": "What are the CS core requirements?"
        }
        
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query successful!")
            print(f"Response: {result['response'][:100]}...")
            print(f"Confidence: {result['confidence']}")
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing query: {e}")

if __name__ == "__main__":
    print("Make sure the API gateway is running:")
    print("python -m uvicorn api_gateway.main:app --reload --port 8000")
    print()
    
    if setup_api_key():
        test_query()
    
    print("\nAPI Gateway URLs:")
    print("- Documentation: http://127.0.0.1:8000/docs")
    print("- Health Check: http://127.0.0.1:8000/health")
    print("- API Status: http://127.0.0.1:8000/api/status")

