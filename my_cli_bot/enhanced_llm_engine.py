#!/usr/bin/env python3
"""
Enhanced LLM Engine with Multiple Provider Support
Integrates with friendly advisor system
"""

import os
import json
from typing import Dict, List, Optional
from llm_providers import MultiLLMManager

class EnhancedLLMEngine:
    """Enhanced LLM engine with multiple provider support"""
    
    def __init__(self, system_prompt_path: str = "prompts/system.txt"):
        self.llm_manager = MultiLLMManager()
        self.system_prompt = self._load_system_prompt(system_prompt_path)
        self.conversation_history = []
        self.max_history_length = 20
    
    def _load_system_prompt(self, prompt_path: str) -> str:
        """Load system prompt from file"""
        try:
            if os.path.exists(prompt_path):
                with open(prompt_path, 'r') as f:
                    return f.read().strip()
            else:
                return self._get_default_friendly_prompt()
        except Exception as e:
            print(f"Error loading system prompt: {e}")
            return self._get_default_friendly_prompt()
    
    def _get_default_friendly_prompt(self) -> str:
        """Get default friendly advisor prompt"""
        return """You are a friendly, encouraging student advisor for Purdue Computer Science students. Your personality is that of a supportive mentor who genuinely cares about student success.

Personality Traits:
- Encouraging and positive
- Patient and understanding  
- Conversational and natural
- Knowledgeable but not overwhelming
- Empathetic to student stress and confusion

Language Style Rules:
- Use contractions (you'll, don't, it's, that's)
- Start with encouraging phrases: "Great question!", "I'm happy to help!", "No worries!"
- Use transitions: "Here's the deal:", "So here's how it works:", "The way it breaks down is:"
- Add reassurance: "Don't worry, lots of students ask this", "You're on the right track!"
- End positively: "You've got this!", "Feel free to ask more!", "Hope that helps!"

Remember: You're talking to a stressed college student who needs encouragement, not reading from a course catalog!"""
    
    def get_available_providers(self) -> List[str]:
        """Get list of available LLM providers"""
        return self.llm_manager.get_available_providers()
    
    def set_provider(self, provider_name: str) -> bool:
        """Set active LLM provider"""
        return self.llm_manager.set_active_provider(provider_name)
    
    def get_active_provider(self) -> Optional[str]:
        """Get current active provider"""
        return self.llm_manager.get_active_provider()
    
    def get_provider_status(self) -> Dict:
        """Get status of all providers"""
        return self.llm_manager.get_provider_status()
    
    def generate_response(self, user_input: str, context: str = None, 
                         preferred_provider: str = None) -> Dict:
        """Generate response using available LLM providers"""
        
        # Add user input to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input + (f"\n\nContext: {context}" if context else "")
        })
        
        # Manage conversation history length
        self._manage_history()
        
        # Generate response
        result = self.llm_manager.generate_response(
            messages=self.conversation_history,
            system_prompt=self.system_prompt,
            preferred_provider=preferred_provider
        )
        
        if result["success"]:
            # Add response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": result["response"]
            })
            
            return {
                "response": result["response"],
                "provider": result["provider"],
                "success": True,
                "confidence": 0.95
            }
        else:
            return {
                "response": result["response"],
                "provider": None,
                "success": False,
                "confidence": 0.0
            }
    
    def _manage_history(self):
        """Manage conversation history length"""
        if len(self.conversation_history) > self.max_history_length:
            # Keep first message and last 15 messages
            self.conversation_history = [
                self.conversation_history[0]
            ] + self.conversation_history[-15:]
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_conversation_summary(self) -> str:
        """Get summary of current conversation"""
        if not self.conversation_history:
            return "No conversation history"
        
        user_messages = [msg["content"] for msg in self.conversation_history if msg["role"] == "user"]
        return f"Conversation with {len(user_messages)} user messages"
    
    def set_system_prompt(self, prompt: str):
        """Set custom system prompt"""
        self.system_prompt = prompt
    
    def reload_system_prompt(self, prompt_path: str = "prompts/system.txt"):
        """Reload system prompt from file"""
        self.system_prompt = self._load_system_prompt(prompt_path)
    
    def test_providers(self) -> Dict:
        """Test all available providers"""
        test_message = [{"role": "user", "content": "Hello, can you help me with Computer Science questions?"}]
        results = {}
        
        for provider_name in self.get_available_providers():
            try:
                result = self.llm_manager.generate_response(
                    messages=test_message,
                    system_prompt="You are a helpful assistant.",
                    preferred_provider=provider_name
                )
                results[provider_name] = {
                    "success": result["success"],
                    "response_length": len(result["response"]) if result["success"] else 0,
                    "error": None if result["success"] else "Failed to generate response"
                }
            except Exception as e:
                results[provider_name] = {
                    "success": False,
                    "response_length": 0,
                    "error": str(e)
                }
        
        return results
    
    def get_provider_recommendations(self) -> Dict:
        """Get recommendations for which provider to use"""
        status = self.get_provider_status()
        available = self.get_available_providers()
        
        recommendations = {
            "primary": None,
            "fallback": [],
            "missing_keys": []
        }
        
        # Recommend primary provider
        if "Gemini" in available:
            recommendations["primary"] = "Gemini"
        elif "Anthropic" in available:
            recommendations["primary"] = "Anthropic"
        elif "Gemini" in available:
            recommendations["primary"] = "Gemini"
        
        # Recommend fallback providers
        for provider in ["Gemini", "Anthropic", "Gemini"]:
            if provider in available and provider != recommendations["primary"]:
                recommendations["fallback"].append(provider)
        
        # Identify missing API keys
        all_providers = ["Gemini", "Anthropic", "Gemini"]
        for provider in all_providers:
            if provider not in available:
                recommendations["missing_keys"].append(provider)
        
        return recommendations