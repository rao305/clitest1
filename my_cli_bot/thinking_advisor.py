#!/usr/bin/env python3
"""
AI Thinking/Reasoning Layer for Purdue CS Advisor
Implements step-by-step reasoning before generating responses
"""

import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from enhanced_llm_engine import EnhancedLLMEngine

class ThinkingIndicator:
    """Visual thinking indicator for CLI"""
    
    def __init__(self):
        self.thinking = False
        self.thread = None
        self.steps = []
        self.current_step = 0
    
    def start_thinking(self, message="Thinking"):
        """Start the thinking animation"""
        self.thinking = True
        self.steps = []
        self.current_step = 0
        self.thread = threading.Thread(target=self._animate_thinking, args=(message,))
        self.thread.daemon = True
        self.thread.start()
    
    def add_step(self, step_description):
        """Add a thinking step"""
        self.steps.append(step_description)
        self.current_step = len(self.steps) - 1
    
    def stop_thinking(self):
        """Stop the thinking animation"""
        self.thinking = False
        if self.thread:
            self.thread.join(timeout=1)
        print("\r" + " " * 80 + "\r", end="", flush=True)  # Clear line
    
    def _animate_thinking(self, message):
        """Animate the thinking process"""
        dots = ["", ".", "..", "..."]
        i = 0
        
        while self.thinking:
            if self.steps and self.current_step < len(self.steps):
                current_message = f"🤔 {self.steps[self.current_step]}"
            else:
                current_message = f"🤔 {message}"
            
            print(f"\r{current_message}{dots[i % 4]}  ", end="", flush=True)
            time.sleep(0.5)
            i += 1

class ThinkingAIAdvisor:
    """AI Advisor with visible thinking process"""
    
    def __init__(self, knowledge_graph=None, llm_engine=None):
        self.kg = knowledge_graph
        self.llm_engine = llm_engine or EnhancedLLMEngine()
        self.thinking_indicator = ThinkingIndicator()
        
    def process_query_with_thinking(self, query: str, track_context: str = None) -> Dict[str, Any]:
        """
        Main method that implements the thinking process with visual feedback
        """
        
        try:
            # Start thinking animation
            self.thinking_indicator.start_thinking("Analyzing your question")
            
            # Step 1: Initial Analysis
            self.thinking_indicator.add_step("Analyzing question intent and requirements")
            thinking_process = self._start_thinking_process(query, track_context)
            
            # Step 2: Deep Reasoning
            self.thinking_indicator.add_step("Gathering relevant course data")
            reasoning_result = self._perform_deep_reasoning(thinking_process)
            
            # Step 3: Generate Thoughtful Response
            self.thinking_indicator.add_step("Formulating helpful response")
            final_response = self._generate_thoughtful_response(reasoning_result)
            
            # Stop thinking animation
            self.thinking_indicator.stop_thinking()
            
            return final_response
            
        except Exception as e:
            self.thinking_indicator.stop_thinking()
            return {
                "query": query,
                "response": "I'm sorry, I encountered an issue while thinking through your question. Let me try a simpler approach.",
                "confidence": 0.5,
                "source": "thinking_error",
                "error": str(e)
            }
    
    def _start_thinking_process(self, query: str, track_context: str) -> Dict[str, Any]:
        """
        Step 1: AI analyzes the query and plans its thinking approach
        """
        
        analysis_prompt = f"""You are analyzing a student's question about Purdue CS. Think through this systematically:

Student Question: "{query}"
Track Context: {track_context or "Not specified"}

Analyze this question by considering:

1. What is the student really asking?
2. What type of information do they need?
3. What courses or concepts are relevant?
4. What level of detail is appropriate?

Provide your analysis in this JSON format:
{{
  "primary_intent": "what they're asking",
  "information_type": "requirements/planning/advice/timing",
  "relevant_courses": ["list of relevant courses"],
  "complexity": "basic/intermediate/advanced",
  "student_concerns": ["implied concerns or worries"]
}}

Think carefully and provide detailed analysis."""

        try:
            # Use the enhanced LLM engine for analysis
            result = self.llm_engine.generate_response(analysis_prompt)
            
            if result["success"]:
                # Try to extract JSON from response
                response_text = result["response"]
                try:
                    # Find JSON in the response
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}') + 1
                    if start_idx != -1 and end_idx != -1:
                        json_str = response_text[start_idx:end_idx]
                        analysis = json.loads(json_str)
                    else:
                        analysis = self._fallback_analysis(query, track_context)
                except json.JSONDecodeError:
                    analysis = self._fallback_analysis(query, track_context)
                
                return {
                    "original_query": query,
                    "track_context": track_context,
                    "thinking_analysis": analysis,
                    "raw_thinking": response_text,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return self._fallback_analysis(query, track_context)
                
        except Exception as e:
            return self._fallback_analysis(query, track_context, str(e))
    
    def _perform_deep_reasoning(self, thinking_process: Dict) -> Dict[str, Any]:
        """
        Step 2: Gather data and perform deep reasoning based on the analysis
        """
        
        analysis = thinking_process.get('thinking_analysis', {})
        courses_needed = analysis.get('relevant_courses', [])
        
        # Gather relevant data from knowledge graph
        relevant_data = self._gather_knowledge_data(courses_needed, thinking_process['track_context'])
        
        # Create reasoning prompt
        reasoning_prompt = f"""Based on your analysis, reason through the answer using this knowledge:

ORIGINAL QUESTION: {thinking_process['original_query']}
ANALYSIS: {json.dumps(analysis, indent=2)}
KNOWLEDGE DATA: {json.dumps(relevant_data, indent=2)}

Think through:
1. What are the key facts from the data?
2. How do prerequisites and timing affect the answer?
3. What guidance would be most helpful?
4. What tone should I use?

Provide reasoning in JSON format:
{{
  "key_facts": ["most important facts"],
  "considerations": ["timing, prerequisites, etc."],
  "guidance_strategy": "how to be most helpful",
  "tone": "encouraging/supportive/explanatory"
}}"""

        try:
            result = self.llm_engine.generate_response(reasoning_prompt)
            
            if result["success"]:
                response_text = result["response"]
                try:
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}') + 1
                    if start_idx != -1 and end_idx != -1:
                        json_str = response_text[start_idx:end_idx]
                        reasoning = json.loads(json_str)
                    else:
                        reasoning = {"error": "Could not parse reasoning"}
                except json.JSONDecodeError:
                    reasoning = {"error": "Invalid JSON in reasoning"}
                
                return {
                    **thinking_process,
                    "reasoning_result": reasoning,
                    "raw_reasoning": response_text,
                    "knowledge_data": relevant_data
                }
            else:
                return {**thinking_process, "reasoning_error": "Failed to generate reasoning"}
                
        except Exception as e:
            return {**thinking_process, "reasoning_error": str(e)}
    
    def _generate_thoughtful_response(self, reasoning_result: Dict) -> Dict[str, Any]:
        """
        Step 3: Generate the final response based on all the thinking and reasoning
        """
        
        # Extract key information
        original_query = reasoning_result['original_query']
        analysis = reasoning_result.get('thinking_analysis', {})
        reasoning = reasoning_result.get('reasoning_result', {})
        
        # Create the final response generation prompt
        final_prompt = f"""Based on your thorough analysis and reasoning, provide a final response to the student.

STUDENT'S QUESTION: {original_query}

YOUR ANALYSIS:
- Intent: {analysis.get('primary_intent', 'Unknown')}
- Type: {analysis.get('information_type', 'Unknown')}
- Complexity: {analysis.get('complexity', 'Unknown')}

YOUR REASONING:
- Key Facts: {reasoning.get('key_facts', [])}
- Considerations: {reasoning.get('considerations', [])}
- Strategy: {reasoning.get('guidance_strategy', 'Be helpful')}

RESPONSE GUIDELINES:
- Be friendly and encouraging
- Use natural, conversational language
- Start with an encouraging phrase like "Great question!" or "I'm happy to help!"
- Explain the reasoning behind your advice
- End supportively
- No markdown formatting

Generate a thoughtful, helpful response that shows you've carefully considered their question."""

        try:
            result = self.llm_engine.generate_response(final_prompt)
            
            if result["success"]:
                return {
                    "query": original_query,
                    "response": result["response"],
                    "confidence": 0.95,  # High confidence due to thorough thinking
                    "source": "thinking_ai",
                    "provider": result.get("provider", "Unknown"),
                    "thinking_process": reasoning_result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return self._generate_simple_fallback(original_query)
                
        except Exception as e:
            return self._generate_simple_fallback(original_query)
    
    def _gather_knowledge_data(self, courses: List[str], track_context: str) -> Dict[str, Any]:
        """
        Gather relevant data from knowledge graph based on identified needs
        """
        
        knowledge_data = {
            "courses": {},
            "tracks": {},
            "general_info": {}
        }
        
        # If knowledge graph is available, use it
        if self.kg:
            try:
                # Get course information
                for course in courses:
                    course_info = self.kg.get_course_info(course)
                    if course_info:
                        knowledge_data["courses"][course] = course_info
                
                # Get track information
                if track_context:
                    track_info = self.kg.get_track_info(track_context)
                    if track_info:
                        knowledge_data["tracks"][track_context] = track_info
                        
            except Exception as e:
                knowledge_data["error"] = f"Error gathering knowledge: {str(e)}"
        
        return knowledge_data
    
    def _fallback_analysis(self, query: str, track_context: str, error: str = None) -> Dict[str, Any]:
        """
        Fallback analysis when AI analysis fails
        """
        
        # Simple keyword-based analysis
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['prerequisite', 'prereq', 'before', 'first']):
            info_type = "requirements"
        elif any(word in query_lower for word in ['when', 'semester', 'schedule', 'plan']):
            info_type = "timing"
        elif any(word in query_lower for word in ['track', 'specialization', 'focus']):
            info_type = "planning"
        else:
            info_type = "general"
        
        # Extract potential course codes
        import re
        course_codes = re.findall(r'CS\s*\d{5}', query.upper())
        
        return {
            "original_query": query,
            "track_context": track_context,
            "thinking_analysis": {
                "primary_intent": "seeking information",
                "information_type": info_type,
                "relevant_courses": course_codes,
                "complexity": "basic",
                "student_concerns": ["understanding requirements"]
            },
            "fallback_used": True,
            "error": error
        }
    
    def _generate_simple_fallback(self, query: str) -> Dict[str, Any]:
        """
        Generate a simple fallback response
        """
        
        return {
            "query": query,
            "response": "Great question! I'm happy to help with your Purdue CS question. While I'm processing your specific request, I'd recommend checking with your academic advisor for the most up-to-date information. Feel free to ask me more specific questions about courses, prerequisites, or degree planning!",
            "confidence": 0.7,
            "source": "fallback",
            "provider": "fallback"
        }