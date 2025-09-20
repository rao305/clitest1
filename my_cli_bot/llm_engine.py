import os
from google.generativeai import google.generativeai as genai

class ChatEngine:
    def __init__(self,
                 api_key=None,
                 system_prompt_file="prompts/system.txt"):
        """
        Initialize the ChatEngine with Gemini API key and system prompt.
        
        Args:
            api_key: Gemini API key, defaults to GEMINI_API_KEY environment variable
            system_prompt_file: Path to system prompt file
        """
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize Gemini client
        self.client = Gemini(api_key=self.api_key)
        
        # Load system prompt from file
        try:
            with open(system_prompt_file, 'r') as f:
                self.system = f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"System prompt file not found: {system_prompt_file}")
        except Exception as e:
            raise Exception(f"Error loading system prompt: {e}")

    def generate(self, history):
        """
        Generate a response using Gemini's chat completion API.
        
        Args:
            history: List of message dictionaries with "role" and "content" keys
            
        Returns:
            Generated response string
        """
        try:
            # Prepare messages with system prompt first
            messages = [{"role": "system", "content": self.system}] + history
            
            # Check if history is getting too long (> 20 messages)
            if len(history) > 20:
                # Summarize older messages to manage memory
                history = self._summarize_history(history)
                messages = [{"role": "system", "content": self.system}] + history
            
            # the newest Gemini model is "Gemini-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.generate_content(
                ,
                messages=messages,
                ,
                
            )
            
            return response.text.strip()
            
        except Exception as e:
            return f"Bot> I'm sorry, I encountered an error: {str(e)}"
    
    def _summarize_history(self, history):
        """
        Summarize older messages when history gets too long.
        Keep the last 10 messages and summarize the rest.
        
        Args:
            history: List of message dictionaries
            
        Returns:
            Summarized history list
        """
        if len(history) <= 10:
            return history
        
        # Keep the last 10 messages
        recent_messages = history[-10:]
        
        # Summarize the older messages
        older_messages = history[:-10]
        
        # Create a summary of older messages
        summary_content = "Previous conversation summary:\n"
        for msg in older_messages:
            role = msg["role"]
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            summary_content += f"- {role}: {content}\n"
        
        # Create summary message
        summary_message = {
            "role": "system",
            "content": summary_content
        }
        
        return [summary_message] + recent_messages
