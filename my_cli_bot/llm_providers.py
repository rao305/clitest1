#!/usr/bin/env python3
"""
Multiple LLM Provider Support for Enhanced Boiler AI
Supports Gemini, Anthropic, and Google Gemini providers
"""

import os
import json
from typing import Dict, List, Optional, Union
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: str, model_name: str = None):
        self.api_key = api_key
        self.model_name = model_name
        self.provider_name = self.__class__.__name__.replace('Provider', '')
    
    @abstractmethod
    def generate_response(self, messages: List[Dict], system_prompt: str = None) -> str:
        """Generate response from the LLM provider"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available and configured"""
        pass

class GeminiProvider(LLMProvider):
    """Gemini Gemini provider"""
    
    def __init__(self, api_key: str, model_name: str = "Gemini-4o"):
        super().__init__(api_key, model_name)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client"""
        try:
            from google.generativeai import google.generativeai as genai
            self.client = Gemini(api_key=self.api_key)
        except ImportError:
            raise ImportError("Gemini package not installed. Install with: pip install Gemini")
    
    def generate_response(self, messages: List[Dict], system_prompt: str = None) -> str:
        """Generate response using Gemini API"""
        try:
            # Add system prompt if provided
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages
            
            response = self.client.generate_content(
                model=self.model_name,
                messages=messages,
                ,
                
            )
            
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        try:
            return self.client is not None and self.api_key is not None
        except:
            return False

class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key, model_name)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Anthropic client"""
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("Anthropic package not installed. Install with: pip install anthropic")
    
    def generate_response(self, messages: List[Dict], system_prompt: str = None) -> str:
        """Generate response using Anthropic API"""
        try:
            # Convert messages to Anthropic format
            anthropic_messages = []
            for msg in messages:
                if msg["role"] != "system":  # Anthropic handles system separately
                    anthropic_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            response = self.client.messages.create(
                model=self.model_name,
                ,
                ,
                system=system_prompt or "You are a helpful assistant.",
                messages=anthropic_messages
            )
            
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Anthropic is available"""
        try:
            return self.client is not None and self.api_key is not None
        except:
            return False

class GeminiProvider(LLMProvider):
    """Google Gemini provider"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        super().__init__(api_key, model_name)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client"""
        try:
            from google import genai
            from google.genai import types
            self.client = genai.Client(api_key=self.api_key)
            self.types = types
        except ImportError:
            raise ImportError("Google GenAI package not installed. Install with: pip install google-genai")
    
    def generate_response(self, messages: List[Dict], system_prompt: str = None) -> str:
        """Generate response using Gemini API"""
        try:
            # Convert messages to Gemini format
            gemini_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    gemini_messages.append(
                        self.types.Content(
                            role="user",
                            parts=[self.types.Part(text=msg["content"])]
                        )
                    )
                elif msg["role"] == "assistant":
                    gemini_messages.append(
                        self.types.Content(
                            role="model",
                            parts=[self.types.Part(text=msg["content"])]
                        )
                    )
            
            config = self.types.GenerateContentConfig(
                ,
                max_output_tokens=1000
            )
            
            if system_prompt:
                config.system_instruction = system_prompt
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=gemini_messages,
                config=config
            )
            
            return response.text if response.text else "No response generated"
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        try:
            return self.client is not None and self.api_key is not None
        except:
            return False

class MultiLLMManager:
    """Manager for multiple LLM providers"""
    
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self.active_provider = None
        self.fallback_order = ["Gemini", "Anthropic", "Gemini"]
        self._load_providers()
    
    def _load_providers(self):
        """Load available providers based on environment variables"""
        # Gemini
        Gemini_key = os.environ.get('GEMINI_API_KEY')
        if Gemini_key:
            try:
                self.providers["Gemini"] = GeminiProvider(Gemini_key)
                if not self.active_provider:
                    self.active_provider = "Gemini"
            except Exception as e:
                print(f"Failed to load Gemini provider: {e}")
        
        # Anthropic
        anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        if anthropic_key:
            try:
                self.providers["Anthropic"] = AnthropicProvider(anthropic_key)
                if not self.active_provider:
                    self.active_provider = "Anthropic"
            except Exception as e:
                print(f"Failed to load Anthropic provider: {e}")
        
        # Gemini
        gemini_key = os.environ.get('GEMINI_API_KEY')
        if gemini_key:
            try:
                self.providers["Gemini"] = GeminiProvider(gemini_key)
                if not self.active_provider:
                    self.active_provider = "Gemini"
            except Exception as e:
                print(f"Failed to load Gemini provider: {e}")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return [name for name, provider in self.providers.items() if provider.is_available()]
    
    def set_active_provider(self, provider_name: str) -> bool:
        """Set active provider"""
        if provider_name in self.providers and self.providers[provider_name].is_available():
            self.active_provider = provider_name
            return True
        return False
    
    def get_active_provider(self) -> Optional[str]:
        """Get current active provider"""
        return self.active_provider
    
    def generate_response(self, messages: List[Dict], system_prompt: str = None, 
                         preferred_provider: str = None) -> Dict:
        """Generate response with fallback support"""
        
        # Try preferred provider first
        if preferred_provider and preferred_provider in self.providers:
            try:
                provider = self.providers[preferred_provider]
                if provider.is_available():
                    response = provider.generate_response(messages, system_prompt)
                    return {
                        "response": response,
                        "provider": preferred_provider,
                        "success": True
                    }
            except Exception as e:
                print(f"Failed to use preferred provider {preferred_provider}: {e}")
        
        # Try active provider
        if self.active_provider and self.active_provider in self.providers:
            try:
                provider = self.providers[self.active_provider]
                if provider.is_available():
                    response = provider.generate_response(messages, system_prompt)
                    return {
                        "response": response,
                        "provider": self.active_provider,
                        "success": True
                    }
            except Exception as e:
                print(f"Failed to use active provider {self.active_provider}: {e}")
        
        # Fallback to available providers
        for provider_name in self.fallback_order:
            if provider_name in self.providers:
                try:
                    provider = self.providers[provider_name]
                    if provider.is_available():
                        response = provider.generate_response(messages, system_prompt)
                        return {
                            "response": response,
                            "provider": provider_name,
                            "success": True
                        }
                except Exception as e:
                    print(f"Failed to use fallback provider {provider_name}: {e}")
                    continue
        
        # No providers available - this should trigger an emergency AI-generated response
        return {
            "response": None,  # Will be handled by calling code to generate AI response
            "provider": None,
            "success": False,
            "error": "no_providers_available"
        }
    
    def get_provider_status(self) -> Dict:
        """Get status of all providers"""
        status = {}
        for name, provider in self.providers.items():
            status[name] = {
                "available": provider.is_available(),
                "model": provider.model_name,
                "active": name == self.active_provider
            }
        return status
    
    def add_provider(self, provider_name: str, provider: LLMProvider):
        """Add a custom provider"""
        self.providers[provider_name] = provider
        if not self.active_provider:
            self.active_provider = provider_name
    
    def remove_provider(self, provider_name: str):
        """Remove a provider"""
        if provider_name in self.providers:
            del self.providers[provider_name]
            if self.active_provider == provider_name:
                # Set new active provider
                available = self.get_available_providers()
                self.active_provider = available[0] if available else None