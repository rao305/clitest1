#!/usr/bin/env python3
"""
BoilerAI Server Bridge
======================

This server acts as a bridge between the frontend and CLI.
It handles API key synchronization and query processing.
"""

import os
import sys
import json
from typing import Dict, Any, Optional
from pathlib import Path

# Add CLI path
cli_path = Path(__file__).parent / "my_cli_bot"
sys.path.insert(0, str(cli_path))

try:
    from simple_boiler_ai import SimpleBoilerAI
    from api_key_manager import get_api_key_manager, setup_api_key
except ImportError as e:
    print(f"Error importing CLI modules: {e}")
    print("Make sure the CLI is properly set up")
    sys.exit(1)

class BoilerAIServer:
    """Server bridge for BoilerAI frontend integration"""
    
    def __init__(self):
        self.cli_instance = None
        self.api_manager = get_api_key_manager()
        self.current_provider = None
        
    def initialize_cli(self, api_key: str = None, provider: str = None):
        """Initialize CLI with API key"""
        try:
            if api_key and provider:
                # Use provided API key and provider
                self.cli_instance = SimpleBoilerAI(api_key=api_key)
                self.current_provider = provider
                print(f"✅ CLI initialized with {provider} API key")
            else:
                # Prompt for API key setup
                print("🔑 Setting up API key for BoilerAI...")
                provider, api_key = setup_api_key()
                self.cli_instance = SimpleBoilerAI(api_key=api_key)
                self.current_provider = provider
                print(f"✅ CLI initialized with {provider}")
                
        except Exception as e:
            print(f"❌ Error initializing CLI: {e}")
            return False
        
        return True
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process query through CLI"""
        if not self.cli_instance:
            return {
                "response": "CLI not initialized. Please set up API key first.",
                "thinking": "CLI initialization required",
                "sources": [],
                "confidence": 0.0
            }
        
        try:
            result = self.cli_instance.process_query(query)
            return result
        except Exception as e:
            return {
                "response": f"Error processing query: {str(e)}",
                "thinking": "Error occurred during processing",
                "sources": [],
                "confidence": 0.1
            }
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get API key status for frontend"""
        return self.api_manager.get_frontend_config()
    
    def set_api_key(self, provider: str, api_key: str) -> bool:
        """Set API key from frontend"""
        try:
            self.api_manager.set_api_key(provider, api_key)
            
            # Reinitialize CLI with new API key
            self.cli_instance = SimpleBoilerAI(api_key=api_key)
            self.current_provider = provider
            
            # Set environment variables
            if provider.lower() == "openai":
                os.environ["OPENAI_API_KEY"] = api_key
                os.environ["LLM_PROVIDER"] = "openai"
            elif provider.lower() == "gemini":
                os.environ["GEMINI_API_KEY"] = api_key
                os.environ["LLM_PROVIDER"] = "gemini"
            
            return True
        except Exception as e:
            print(f"Error setting API key: {e}")
            return False
    
    def clear_api_keys(self):
        """Clear all API keys"""
        self.api_manager.clear_api_keys()
        self.cli_instance = None
        self.current_provider = None

# Global server instance
server = BoilerAIServer()

def get_server() -> BoilerAIServer:
    """Get the global server instance"""
    return server

def initialize_server(api_key: str = None, provider: str = None) -> bool:
    """Initialize the server with API key"""
    return server.initialize_cli(api_key, provider)

def process_query(query: str) -> Dict[str, Any]:
    """Process a query through the server"""
    return server.process_query(query)

def get_api_status() -> Dict[str, Any]:
    """Get API status"""
    return server.get_api_status()

def set_api_key(provider: str, api_key: str) -> bool:
    """Set API key"""
    return server.set_api_key(provider, api_key)

if __name__ == "__main__":
    # Test the server bridge
    print("Testing BoilerAI Server Bridge")
    print("=" * 40)
    
    # Initialize server
    if initialize_server():
        print("[OK] Server initialized successfully")
        
        # Test query processing
        test_query = "What are the CS core requirements?"
        print(f"\nTesting query: {test_query}")
        
        result = process_query(test_query)
        print(f"[OK] Response: {result.get('response', 'No response')[:100]}...")
        print(f"[OK] Confidence: {result.get('confidence', 'N/A')}")
        
        # Show API status
        status = get_api_status()
        print(f"\nAPI Status: {status}")
        
    else:
        print("[ERROR] Failed to initialize server")
