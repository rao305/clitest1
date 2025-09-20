#!/usr/bin/env python3
"""
Enhanced API Error Handling for Pure AI System
Implements rate limiting, exponential backoff, and proper error handling.
"""

import time
import random
from typing import Optional
import google.generativeai as genai
from google.generativeai import google.generativeai as genai

class ResilientGeminiClient:
    """Gemini client with built-in resilience for overload scenarios"""
    
    def __init__(self, api_key: str):
        self.client = Gemini(api_key=api_key)
        self.last_request_time = 0
        self.min_interval = 1.0  # Minimum 1 second between requests
        
    def _wait_if_needed(self):
        """Implement request throttling"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _exponential_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        base_delay = 2 ** attempt  # 2, 4, 8, 16, 32 seconds
        jitter = random.uniform(0, 1)  # Add randomness
        return min(base_delay + jitter, 60)  # Cap at 60 seconds
    
    def chat_completion_with_retry(self, **kwargs) -> Optional[str]:
        """Make chat completion with automatic retry for overload errors"""
        max_retries = 5
        
        for attempt in range(max_retries):
            try:
                self._wait_if_needed()
                
                response = self.client.generate_content(**kwargs)
                return response.text.strip()
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Handle overload errors specifically
                if "overloaded" in error_str or "529" in error_str:
                    if attempt < max_retries - 1:
                        delay = self._exponential_backoff(attempt)
                        print(f"⏳ API overloaded, retrying in {delay:.1f} seconds... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        continue
                    else:
                        raise Exception(f"API overloaded after {max_retries} attempts. Please try again later.")
                
                # Handle other API errors
                elif "rate limit" in error_str:
                    if attempt < max_retries - 1:
                        delay = self._exponential_backoff(attempt + 2)  # Longer delay for rate limits
                        print(f"⏳ Rate limited, waiting {delay:.1f} seconds... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        continue
                    else:
                        raise Exception(f"Rate limited after {max_retries} attempts. Please try again later.")
                
                # Re-raise other errors immediately
                else:
                    raise e
        
        return None
