#!/usr/bin/env python3
"""
API Key Management System for BoilerAI
======================================

This module handles API key management and synchronization between CLI and frontend.
All API keys are stored securely and prompted from the user.
"""

import os
import json
import getpass
from typing import Optional, Dict, Any
from pathlib import Path

class APIKeyManager:
    """Manages API keys for BoilerAI system"""
    
    def __init__(self):
        self.config_file = Path.home() / ".boilerai" / "api_keys.json"
        self.config_file.parent.mkdir(exist_ok=True)
        self.api_keys = self._load_api_keys()
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from secure storage"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_api_keys(self):
        """Save API keys to secure storage"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.api_keys, f)
            # Set restrictive permissions
            os.chmod(self.config_file, 0o600)
        except IOError as e:
            print(f"Warning: Could not save API keys: {e}")
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider"""
        return self.api_keys.get(provider)
    
    def set_api_key(self, provider: str, api_key: str):
        """Set API key for a specific provider"""
        self.api_keys[provider] = api_key
        self._save_api_keys()
    
    def prompt_for_api_key(self, provider: str) -> str:
        """Prompt user for API key with copy-paste support and remember option"""
        print(f"\nAPI Key Required for {provider}")
        print("=" * 40)
        
        if provider.lower() == "openai":
            print("Get your OpenAI API key from: https://platform.openai.com/api-keys")
            print("Your key should start with 'sk-'")
            print("\n[COPY-PASTE FRIENDLY] You can copy and paste your API key here:")
            api_key = input("Enter your OpenAI API key: ").strip()
            
            # More lenient validation - just check if it looks like a key
            if not api_key or len(api_key) < 10:
                print("[ERROR] API key seems too short. Please check and try again.")
                return self.prompt_for_api_key(provider)
            elif not api_key.startswith('sk-'):
                print("[WARNING] OpenAI API key usually starts with 'sk-'")
                print("Are you sure this is correct? (y/n): ", end="")
                confirm = input().strip().lower()
                if confirm != 'y':
                    return self.prompt_for_api_key(provider)
                
        elif provider.lower() == "gemini":
            print("Get your Gemini API key from: https://makersuite.google.com/app/apikey")
            print("Your key should start with 'AIzaSy'")
            print("\n[COPY-PASTE FRIENDLY] You can copy and paste your API key here:")
            api_key = input("Enter your Gemini API key: ").strip()
            
            # More lenient validation
            if not api_key or len(api_key) < 10:
                print("[ERROR] API key seems too short. Please check and try again.")
                return self.prompt_for_api_key(provider)
            elif not api_key.startswith('AIzaSy'):
                print("[WARNING] Gemini API key usually starts with 'AIzaSy'")
                print("Are you sure this is correct? (y/n): ", end="")
                confirm = input().strip().lower()
                if confirm != 'y':
                    return self.prompt_for_api_key(provider)
        else:
            print(f"\n[COPY-PASTE FRIENDLY] You can copy and paste your API key here:")
            api_key = input(f"Enter your {provider} API key: ").strip()
        
        if not api_key:
            print("[ERROR] No API key provided. Exiting.")
            exit(1)
        
        # Ask if user wants to remember the key
        print(f"\nAPI key received: {api_key[:10]}...")
        print("Would you like to save this API key for future use? (y/n): ", end="")
        remember = input().strip().lower()
        
        if remember == 'y':
            # Save the API key
            self.set_api_key(provider, api_key)
            print(f"[OK] {provider} API key saved securely for future use")
        else:
            print(f"[INFO] {provider} API key will be used for this session only")
        
        return api_key
    
    def get_or_prompt_api_key(self, provider: str) -> str:
        """Get existing API key or prompt for new one"""
        # Check environment variables first
        env_key = None
        if provider.lower() == "openai":
            env_key = os.environ.get("OPENAI_API_KEY")
        elif provider.lower() == "gemini":
            env_key = os.environ.get("GEMINI_API_KEY")
        
        if env_key:
            print(f"[OK] Using {provider} API key from environment")
            return env_key
        
        # Check saved keys
        saved_key = self.get_api_key(provider)
        if saved_key:
            print(f"\n[INFO] Found saved {provider} API key: {saved_key[:10]}...")
            print("Would you like to use the saved API key? (y/n): ", end="")
            use_saved = input().strip().lower()
            
            if use_saved == 'y':
                print(f"[OK] Using saved {provider} API key")
                return saved_key
            else:
                print(f"[INFO] Will prompt for new {provider} API key")
        
        # Prompt for new key
        return self.prompt_for_api_key(provider)
    
    def select_provider(self) -> str:
        """Let user select AI provider"""
        print("\nSelect AI Provider")
        print("=" * 20)
        print("1) Gemini (Google) - Free tier available")
        print("2) OpenAI - Paid service")
        
        while True:
            choice = input("Select provider (1/2): ").strip()
            if choice == "1":
                return "gemini"
            elif choice == "2":
                return "openai"
            else:
                print("[ERROR] Invalid choice. Please select 1 or 2.")
    
    def setup_api_key(self) -> tuple[str, str]:
        """Complete API key setup process"""
        provider = self.select_provider()
        api_key = self.get_or_prompt_api_key(provider)
        
        # Set environment variables for current session
        if provider.lower() == "openai":
            os.environ["OPENAI_API_KEY"] = api_key
            os.environ["LLM_PROVIDER"] = "openai"
        elif provider.lower() == "gemini":
            os.environ["GEMINI_API_KEY"] = api_key
            os.environ["LLM_PROVIDER"] = "gemini"
        
        return provider, api_key
    
    def manage_saved_keys(self):
        """Manage saved API keys"""
        print("\nSaved API Keys Management")
        print("=" * 30)
        
        if not self.api_keys:
            print("[INFO] No saved API keys found")
            return
        
        for provider, key in self.api_keys.items():
            print(f"{provider.title()}: {key[:10]}...")
        
        print("\nOptions:")
        print("1. Clear all saved keys")
        print("2. Clear specific provider")
        print("3. Back to main menu")
        
        choice = input("Select option (1-3): ").strip()
        
        if choice == "1":
            confirm = input("Are you sure you want to clear ALL saved keys? (y/n): ").strip().lower()
            if confirm == 'y':
                self.clear_api_keys()
                print("[OK] All saved API keys cleared")
        
        elif choice == "2":
            print("Available providers:")
            for i, provider in enumerate(self.api_keys.keys(), 1):
                print(f"{i}. {provider}")
            
            try:
                provider_choice = int(input("Select provider to clear: ")) - 1
                providers = list(self.api_keys.keys())
                if 0 <= provider_choice < len(providers):
                    provider = providers[provider_choice]
                    confirm = input(f"Clear {provider} API key? (y/n): ").strip().lower()
                    if confirm == 'y':
                        del self.api_keys[provider]
                        self._save_api_keys()
                        print(f"[OK] {provider} API key cleared")
                else:
                    print("[ERROR] Invalid choice")
            except ValueError:
                print("[ERROR] Invalid input")
        
        elif choice == "3":
            return
        
        else:
            print("[ERROR] Invalid choice")
    
    def clear_api_keys(self):
        """Clear all saved API keys"""
        self.api_keys = {}
        if self.config_file.exists():
            self.config_file.unlink()
        print("[OK] All API keys cleared")
    
    def list_providers(self):
        """List available providers with their status"""
        print("\nAvailable AI Providers")
        print("=" * 25)
        
        providers = ["openai", "gemini"]
        for provider in providers:
            status = "[OK] Configured" if self.get_api_key(provider) else "[ERROR] Not configured"
            print(f"{provider.title()}: {status}")
    
    def get_frontend_config(self) -> Dict[str, Any]:
        """Get configuration for frontend integration"""
        return {
            "providers": {
                "openai": {
                    "configured": bool(self.get_api_key("openai")),
                    "has_key": bool(self.get_api_key("openai"))
                },
                "gemini": {
                    "configured": bool(self.get_api_key("gemini")),
                    "has_key": bool(self.get_api_key("gemini"))
                }
            },
            "current_provider": os.environ.get("LLM_PROVIDER", "none")
        }

# Global instance
api_key_manager = APIKeyManager()

def get_api_key_manager() -> APIKeyManager:
    """Get the global API key manager instance"""
    return api_key_manager

def setup_api_key() -> tuple[str, str]:
    """Convenience function to setup API key"""
    return api_key_manager.setup_api_key()

def get_api_key(provider: str) -> Optional[str]:
    """Convenience function to get API key"""
    return api_key_manager.get_api_key(provider)

if __name__ == "__main__":
    # Test the API key manager
    print("Testing API Key Manager")
    print("=" * 30)
    
    manager = get_api_key_manager()
    manager.list_providers()
    
    print("\nTo setup API keys, use:")
    print("from api_key_manager import setup_api_key")
    print("provider, key = setup_api_key()")
