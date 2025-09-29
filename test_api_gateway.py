#!/usr/bin/env python3
"""
Test script for BoilerAI API Gateway
"""

import requests
import json
import time

def test_api_gateway():
    """Test the API gateway endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing BoilerAI API Gateway")
    print("=" * 40)
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"Root endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Root endpoint error: {e}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"\nHealth endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health endpoint error: {e}")
    
    # Test providers endpoint
    try:
        response = requests.get(f"{base_url}/api/providers")
        print(f"\nProviders endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Providers endpoint error: {e}")
    
    # Test API status
    try:
        response = requests.get(f"{base_url}/api/status")
        print(f"\nAPI status endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"API status endpoint error: {e}")

if __name__ == "__main__":
    # Wait a moment for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    test_api_gateway()

