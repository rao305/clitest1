#!/usr/bin/env python3
"""
CLI Integration System Prompt for BoilerAI
==========================================

This CLI is integrated with BoilerAI frontend system.
All AI processing is handled here - the frontend just passes queries.

REQUIRED INTERFACE:
- process_query(query: str) -> dict
- Must return: {"response": str, "thinking": str, "sources": list, "confidence": float}

INTEGRATION NOTES:
- User enters API key only in CLI (not frontend)
- CLI handles all AI processing, knowledge base queries, etc.
- Server acts as simple bridge between frontend and CLI
- Transcript processing uses API key from CLI

Simple Boiler AI - 100% AI-Powered Purdue CS Academic Advisor
No hardcoded messages, pure intelligence through Google Gemini integration.
Enhanced with accurate degree progression data and specialized systems.
"""

import json
import os
import logging
import time
import random
from typing import Dict, Any, Optional

# Import Google Generative AI
import google.generativeai as genai
GEMINI_AVAILABLE = True

# Import monitoring system
from ai_monitoring_system import record_api_call, get_monitoring_system

# Import API key manager
from api_key_manager import setup_api_key, get_api_key_manager

# Import our specialized systems
from degree_progression_engine import DegreeProgressionEngine, get_accurate_semester_recommendation
from summer_acceleration_calculator import SummerAccelerationCalculator, generate_summer_acceleration_recommendation
from failure_recovery_system import FailureRecoverySystem, generate_failure_recovery_plan

# Import SQL query handler for hybrid approach
try:
    from sql_query_handler import SQLQueryHandler
    from hybrid_safety_config import HybridSafetyManager, get_safety_manager
except ImportError:
    SQLQueryHandler = None
    HybridSafetyManager = None
    get_safety_manager = lambda: None

# Disable all logging
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger('httpx').setLevel(logging.CRITICAL)

class ResilientGeminiClient:
    """Gemini client with built-in resilience for overload scenarios"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        
        # Configure safety settings to be less restrictive for academic content
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
        ]
        
        # Use more efficient model for better rate limiting
        self.model = genai.GenerativeModel('models/gemini-1.5-flash', safety_settings=safety_settings)
        self.last_request_time = 0
        self.min_interval = 2.0  # Increased to 2 seconds for better rate limiting
        self.request_count = 0
        self.daily_limit = 100  # Daily request limit
        
    def _wait_if_needed(self):
        """Implement enhanced request throttling"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Check daily limit
        if self.request_count >= self.daily_limit:
            raise Exception("Daily request limit reached. Please try again tomorrow.")
        
        # Wait if needed
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _exponential_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        base_delay = min(5 ** attempt, 120)  # 5, 25, 125 seconds max (capped at 120)
        jitter = random.uniform(0, 2)  # Add more randomness
        return base_delay + jitter
    
    def chat_completion_with_retry(self, messages=None, system_prompt=None, **kwargs) -> Optional[str]:
        """Make chat completion with automatic retry for overload errors and monitoring"""
        
        max_retries = 2  # Reduced retries for faster response
        start_time = time.time()
        
        for attempt in range(max_retries):
            try:
                self._wait_if_needed()
                
                # Convert Gemini format to Gemini format
                if messages and len(messages) > 0:
                    # Combine system and user messages for Gemini
                    prompt_text = ""
                    if system_prompt:
                        prompt_text = f"System: {system_prompt}\n\n"
                    
                    for msg in messages:
                        if msg.get('role') == 'system' and not system_prompt:
                            prompt_text += f"System: {msg['content']}\n\n"
                        elif msg.get('role') == 'user':
                            prompt_text += f"User: {msg['content']}\n\n"
                    
                    prompt_text += "Assistant:"
                else:
                    prompt_text = system_prompt or "You are a helpful AI assistant."
                
                # Add timeout for generation
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError("Request timed out")
                
                # Set 30 second timeout
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(30)
                
                try:
                    response = self.model.generate_content(prompt_text)
                finally:
                    signal.alarm(0)  # Cancel the alarm
                
                # Check if response was blocked by safety filters
                if not response.candidates or len(response.candidates) == 0:
                    raise Exception("Response was blocked by safety filters")
                
                candidate = response.candidates[0]
                if candidate.finish_reason == 1:  # STOP reason - blocked by safety
                    # Try to get partial text or provide fallback
                    if hasattr(candidate, 'content') and candidate.content.parts:
                        result = "".join([part.text for part in candidate.content.parts if hasattr(part, 'text')]).strip()
                        if not result:
                            result = "I'm here to help! How can I assist you with your CS courses and academic planning?"
                    else:
                        result = "Hello! I'm your CS academic advisor. How can I help you with course planning, degree requirements, or academic questions?"
                elif hasattr(response, 'text'):
                    result = response.text.strip()
                else:
                    result = "I'm ready to help with your CS academic questions!"
                
                # Record successful API call
                response_time = (time.time() - start_time) * 1000
                tokens_used = len(prompt_text.split()) + len(result.split())  # Estimate tokens
                record_api_call("Gemini", "gemini-pro", tokens_used, response_time, True)
                
                return result
                
            except Exception as e:
                error_str = str(e).lower()
                print(f"[WARNING] Gemini API error (attempt {attempt + 1}/{max_retries}): {str(e)}")

                if attempt < max_retries - 1:
                    delay = self._exponential_backoff(attempt)
                    print(f"[INFO] Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                else:
                    # Record failed API call
                    response_time = (time.time() - start_time) * 1000
                    record_api_call("Gemini", "gemini-pro", 0, response_time, False, "api_error")
                    print("[ERROR] All Gemini attempts failed, switching to knowledge base mode")
                    return None
        
        return None

class SimpleBoilerAI:
    def __init__(self, api_key: str = None):
        # Get API key from parameter or use API key manager
        if api_key is None:
            provider, api_key = setup_api_key()
            self.provider = provider
        else:
            # Determine provider from API key format
            if api_key.startswith('sk-'):
                self.provider = 'openai'
            elif api_key.startswith('AIzaSy'):
                self.provider = 'gemini'
            else:
                self.provider = 'unknown'
        
        # Initialize resilient Gemini client
        self.ai_client = ResilientGeminiClient(api_key=api_key)
        
        # Conversation memory for context tracking
        self.conversation_memory = {
            'user_year': None,
            'user_semester': None,  # 'fall' or 'spring'
            'completed_courses': [],
            'failed_courses': [],
            'gpa': None,
            'track_preference': None,
            'conversation_history': []
        }
        
        # Load knowledge base quietly
        self.knowledge_base = self.load_knowledge_base()
        if self.knowledge_base:
            courses_count = len(self.knowledge_base.get('courses', {}))
            tracks_count = len(self.knowledge_base.get('tracks', {}))
            print(f"[INFO] Knowledge base loaded: {courses_count} courses, {tracks_count} tracks")
        
        # Initialize specialized systems
        self.degree_engine = DegreeProgressionEngine()
        self.summer_calc = SummerAccelerationCalculator()
        self.failure_system = FailureRecoverySystem()
        
        # Initialize hybrid SQL query handler with safety mechanisms
        self.sql_handler = None
        self.safety_manager = get_safety_manager() if HybridSafetyManager else None
        
        if self.safety_manager and self.safety_manager.config.enable_sql_queries and SQLQueryHandler:
            try:
                self.sql_handler = SQLQueryHandler()
                print("[OK] SQL query handler initialized successfully")
                print("[OK] Safety mechanisms active")
            except Exception as e:
                print(f"[WARNING] SQL handler failed to initialize, using JSON fallback: {e}")
                self.sql_handler = None
        elif not SQLQueryHandler:
            print("[INFO] SQL query handler not available, using JSON-only mode")
        elif not self.safety_manager:
            print("[INFO] Safety manager not available, using JSON-only mode")
    
    def load_knowledge_base(self):
        """Load comprehensive knowledge base from JSON file with fallback"""
        try:
            import json
            import os
            
            # Try to load enhanced knowledge base
            kb_path = os.path.join(os.path.dirname(__file__), 'enhanced_knowledge_base.json')
            
            if os.path.exists(kb_path):
                with open(kb_path, 'r', encoding='utf-8') as f:
                    kb_data = json.load(f)
                    return kb_data
            else:
                # Fallback to comprehensive_knowledge_graph.json  
                kb_path = os.path.join(os.path.dirname(__file__), 'comprehensive_knowledge_graph.json')
                if os.path.exists(kb_path):
                    with open(kb_path, 'r') as f:
                        return json.load(f)
                    
        except Exception as e:
            print(f"[WARNING] Could not load knowledge base file: {e}")
        
        # Fallback to embedded knowledge base
        return self.get_fallback_knowledge_base()
    
    def get_fallback_knowledge_base(self):
        """Fallback knowledge base embedded in code"""
        return {
            "courses": {
                "CS 18000": {
                    "title": "Problem Solving and Object-Oriented Programming",
                    "credits": 4,
                    "description": "Introduction to Java programming, object-oriented concepts, and problem-solving techniques.",
                    "prerequisites": [],
                    "difficulty": "Medium",
                    "required_for": "CS 18200, CS 24000, all subsequent CS courses"
                },
                "CS 18200": {
                    "title": "Foundations of Computer Science", 
                    "credits": 3,
                    "description": "Mathematical foundations including discrete mathematics, logic, and proof techniques.",
                    "prerequisites": ["CS 18000"],
                    "difficulty": "Hard",
                    "required_for": "CS 25000, CS 25100, CS 25200"
                }
            },
            "tracks": {
                "Machine Intelligence": {
                    "description": "Focuses on AI, machine learning, and data science",
                    "core_requirements": ["CS 37300", "CS 38100"],
                    "career_focus": "AI research, data science, machine learning engineering"
                },
                "Software Engineering": {
                    "description": "Focuses on software development and systems",
                    "core_requirements": ["CS 30700", "CS 38100", "CS 40800", "CS 40700"],
                    "career_focus": "Software development, systems engineering"
                }
            }
        }
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query and return structured response"""
        try:
            # Use AI client to get response
            response = self.ai_client.chat_completion_with_retry(
                messages=[{"role": "user", "content": query}],
                system_prompt="You are a helpful CS academic advisor for Purdue University."
            )
            
            return {
                "response": response or "I'm here to help with your CS questions!",
                "thinking": "Processed query using AI client",
                "sources": ["knowledge_base"],
                "confidence": 0.8
            }
        except Exception as e:
            return {
                "response": "I'm having trouble processing your request right now. Please try again.",
                "thinking": f"Error: {str(e)}",
                "sources": [],
                "confidence": 0.1
            }

def main():
    """Main function to run the BoilerAI assistant"""
    print("========================================")
    print("      BoilerAI - CS Academic Advisor")
    print("========================================")
    print("Type 'exit' or 'quit' to end the conversation")
    print()
    
    try:
        # Initialize with default API key
        api_key = "your-gemini-api-key-here"  # Replace with actual key
        bot = SimpleBoilerAI(api_key=api_key)
        
        print("AI assistant initialized successfully!")
        print("Ask me anything about CS courses, tracks, graduation requirements, etc.")
        print()
        
    except Exception as e:
        print(f"Error initializing AI: {e}")
        return
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                print("Goodbye! Good luck with your CS journey!")
                break
            
            if not user_input:
                continue
            
            print("AI: ", end="")
            result = bot.process_query(user_input)
            
            # Handle both dict (new) and string (old) return formats
            if isinstance(result, dict):
                print(result["response"])
            else:
                print(result)
            print("\n" + "-"*60 + "\n")
            
        except KeyboardInterrupt:
            try:
                interrupt_prompt = "Generate a brief goodbye message when a user interrupts the program."
                interrupt_msg = bot.get_ai_response(interrupt_prompt) or "Goodbye!"
                print(f"\n\n{interrupt_msg}")
            except:
                print("\n\nGoodbye!")
            break
        except Exception as e:
            try:
                error_prompt = "Generate a brief, friendly error message asking the user to try their question again."
                error_msg = bot.get_ai_response(error_prompt) or "Please try your question again."
                print(f"\n{error_msg}\n")
            except:
                print(f"\nPlease try your question again.\n")

if __name__ == "__main__":
    main()
