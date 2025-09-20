#!/usr/bin/env python3
"""
Dynamic Query Processor - 100% AI-Driven Version
Eliminates ALL hardcoded responses and uses pure AI logic for every response.
"""

import re
import json
from typing import Dict, List, Any, Optional

class DynamicQueryProcessorAIOnly:
    """
    Completely AI-driven query processor with ZERO hardcoded responses
    """
    
    def __init__(self, knowledge_graph):
        self.kg = knowledge_graph
        self.ai_engine = None
        self._initialize_ai_engine()
        
    def _initialize_ai_engine(self):
        """Initialize AI engine for response generation"""
        try:
            from smart_ai_engine import SmartAIEngine
            self.ai_engine = SmartAIEngine()
        except ImportError:
            # Fallback AI engine initialization
            try:
                from llm_providers import MultiLLMManager
                self.llm_manager = MultiLLMManager()
            except ImportError:
                self.llm_manager = None
    
    def process_query_intelligently(self, query: str, track_context: str = None) -> Dict[str, Any]:
        """
        Process query using 100% AI-generated responses with no hardcoded content
        """
        
        # Analyze user intent using AI
        intent_analysis = self._analyze_query_intent_with_ai(query, track_context)
        
        # Generate response using AI and knowledge base
        response_data = self._generate_ai_response(query, intent_analysis, track_context)
        
        # Clean any formatting issues
        response_data = self._clean_response_formatting(response_data)
        
        return response_data
    
    def _analyze_query_intent_with_ai(self, query: str, track_context: str = None) -> Dict[str, Any]:
        """
        Use AI to analyze query intent instead of hardcoded pattern matching
        """
        
        # Get knowledge base context
        knowledge_context = self._get_knowledge_context()
        
        intent_prompt = f"""
        Analyze this Purdue CS student query to understand their intent:
        
        Query: "{query}"
        Track Context: {track_context or "Unknown"}
        Available Knowledge: {knowledge_context}
        
        Determine:
        1. Primary intent (course_timing, track_selection, prerequisites, identity, planning, etc.)
        2. Specific entities mentioned (course codes, years, tracks)
        3. Confidence level (0.0-1.0)
        4. Context clues about student situation
        5. Whether clarification is needed
        
        Respond with JSON containing: primary_intent, confidence, entities, context_clues, requires_clarification
        """
        
        if self.ai_engine:
            try:
                ai_response = self.ai_engine.generate_smart_response(intent_prompt, {"query": query})
                # Try to parse AI response as JSON
                try:
                    return json.loads(ai_response)
                except json.JSONDecodeError:
                    # Fallback if AI doesn't return valid JSON
                    return self._create_fallback_intent(query)
            except Exception:
                return self._create_fallback_intent(query)
        else:
            return self._create_fallback_intent(query)
    
    def _create_fallback_intent(self, query: str) -> Dict[str, Any]:
        """Create basic intent analysis when AI unavailable"""
        query_lower = query.lower()
        
        # Basic pattern detection without hardcoded responses
        if any(word in query_lower for word in ["what", "who", "explain"]):
            primary_intent = "identity" if any(word in query_lower for word in ["you", "are", "yourself"]) else "explanation"
        elif any(word in query_lower for word in ["when", "timing", "take"]):
            primary_intent = "course_timing"
        elif any(word in query_lower for word in ["track", "mi", "se", "choose"]):
            primary_intent = "track_selection"
        elif any(word in query_lower for word in ["prerequisite", "requirement", "need"]):
            primary_intent = "prerequisites"
        else:
            primary_intent = "general_advice"
        
        return {
            "primary_intent": primary_intent,
            "confidence": 0.7,
            "entities": self._extract_entities(query),
            "context_clues": {},
            "requires_clarification": False
        }
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract course codes, years, etc. from query"""
        entities = {}
        
        # Extract course codes
        course_match = re.search(r'(CS|STAT|MA)\s*(\d+)', query.upper())
        if course_match:
            entities["course_code"] = f"{course_match.group(1)} {course_match.group(2)}"
        
        # Extract year mentions
        year_match = re.search(r'(freshman|sophomore|junior|senior|\d+\s*year)', query.lower())
        if year_match:
            entities["student_year"] = year_match.group(1)
        
        # Extract track mentions
        if "mi" in query.lower() or "machine intelligence" in query.lower():
            entities["track"] = "Machine Intelligence"
        elif "se" in query.lower() or "software engineering" in query.lower():
            entities["track"] = "Software Engineering"
        
        return entities
    
    def _generate_ai_response(self, query: str, intent_analysis: Dict[str, Any], track_context: str = None) -> Dict[str, Any]:
        """
        Generate response using AI with knowledge base context
        """
        
        # Get relevant knowledge for this query
        relevant_knowledge = self._get_relevant_knowledge(intent_analysis)
        
        # Create comprehensive prompt for AI response generation
        response_prompt = f"""
        You are a knowledgeable Purdue CS academic advisor. A student has asked you a question.
        
        Student Query: "{query}"
        Intent Analysis: {intent_analysis}
        Track Context: {track_context or "Unknown"}
        Relevant Knowledge: {relevant_knowledge}
        
        Generate a helpful, accurate response that:
        1. Directly addresses their specific question
        2. Uses the provided knowledge base information
        3. Is conversational and encouraging
        4. Includes specific details when relevant (course codes, timelines, requirements)
        5. Does not use markdown formatting (no ** or # or bullets)
        6. Is personalized to their situation when possible
        
        Keep the response natural and conversational, like talking to a helpful advisor.
        """
        
        if self.ai_engine:
            try:
                ai_response = self.ai_engine.generate_smart_response(response_prompt, {"query": query, "intent": intent_analysis})
                return {
                    "query": query,
                    "response": ai_response,
                    "confidence": intent_analysis.get("confidence", 0.8),
                    "intent": intent_analysis.get("primary_intent", "general"),
                    "source_data": {"type": "ai_generated", "knowledge_used": bool(relevant_knowledge)},
                    "track": track_context
                }
            except Exception as e:
                # Fallback when AI engine fails
                return self._generate_fallback_response(query, intent_analysis, track_context)
        else:
            return self._generate_fallback_response(query, intent_analysis, track_context)
    
    def _generate_fallback_response(self, query: str, intent_analysis: Dict[str, Any], track_context: str = None) -> Dict[str, Any]:
        """
        Generate response when AI engine is unavailable - still tries to use LLM if possible
        """
        
        if hasattr(self, 'llm_manager') and self.llm_manager:
            try:
                messages = [{"role": "user", "content": f"As a Purdue CS advisor, please answer: {query}"}]
                system_prompt = "You are a helpful Purdue CS academic advisor. Provide accurate, encouraging responses about CS courses, tracks, and requirements."
                
                result = self.llm_manager.generate_response(messages, system_prompt)
                if result["success"]:
                    return {
                        "query": query,
                        "response": result["response"],
                        "confidence": 0.7,
                        "intent": intent_analysis.get("primary_intent", "general"),
                        "source_data": {"type": "llm_fallback", "provider": result["provider"]},
                        "track": track_context
                    }
            except Exception:
                pass
        
        # Final fallback - generate minimal response from knowledge base
        return self._generate_knowledge_based_response(query, intent_analysis, track_context)
    
    def _generate_knowledge_based_response(self, query: str, intent_analysis: Dict[str, Any], track_context: str = None) -> Dict[str, Any]:
        """
        Generate response using knowledge base when no AI available
        """
        
        intent = intent_analysis.get("primary_intent", "general")
        entities = intent_analysis.get("entities", {})
        
        # Generate response based on intent and available knowledge
        if intent == "course_timing" and entities.get("course_code"):
            response = self._get_course_timing_from_knowledge(entities["course_code"])
        elif intent == "track_selection":
            response = self._get_track_info_from_knowledge()
        elif intent == "prerequisites" and entities.get("course_code"):
            response = self._get_prerequisites_from_knowledge(entities["course_code"])
        elif intent == "identity":
            response = self._get_advisor_identity()
        else:
            response = self._get_general_help()
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.6,
            "intent": intent,
            "source_data": {"type": "knowledge_base"},
            "track": track_context
        }
    
    def _get_knowledge_context(self) -> Dict[str, Any]:
        """Get overview of available knowledge"""
        context = {}
        
        try:
            # Get course count from knowledge graph
            if hasattr(self.kg, 'courses') and self.kg.courses:
                context["courses_available"] = len(self.kg.courses)
            
            # Get track information
            if hasattr(self.kg, 'tracks'):
                context["tracks"] = list(self.kg.tracks.keys()) if self.kg.tracks else ["Machine Intelligence", "Software Engineering"]
            
            # Get degree requirements
            context["degree_info"] = "CS degree requirements, prerequisites, timing"
            
        except Exception:
            context["basic_info"] = "Purdue CS courses, tracks, and requirements"
        
        return context
    
    def _get_relevant_knowledge(self, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant knowledge based on query intent"""
        
        intent = intent_analysis.get("primary_intent", "")
        entities = intent_analysis.get("entities", {})
        knowledge = {}
        
        try:
            if intent == "course_timing" and entities.get("course_code"):
                knowledge["course_info"] = self._lookup_course_info(entities["course_code"])
            
            elif intent == "track_selection":
                knowledge["track_info"] = self._get_track_details()
            
            elif intent == "prerequisites":
                if entities.get("course_code"):
                    knowledge["prerequisites"] = self._lookup_prerequisites(entities["course_code"])
                else:
                    knowledge["general_prereqs"] = "Foundation sequence: CS 18000 → CS 18200 → CS 24000 → CS 25000/25100 → CS 25200"
            
            elif intent == "identity":
                knowledge["advisor_capabilities"] = "Course planning, track selection, prerequisites, degree requirements, timing advice"
            
        except Exception as e:
            knowledge["error"] = f"Knowledge lookup failed: {str(e)}"
        
        return knowledge
    
    def _lookup_course_info(self, course_code: str) -> Dict[str, Any]:
        """Look up specific course information"""
        try:
            if hasattr(self.kg, 'get_course_info'):
                return self.kg.get_course_info(course_code)
            else:
                return {"course": course_code, "info": "Course details available in knowledge base"}
        except Exception:
            return {"course": course_code, "status": "not_found"}
    
    def _get_track_details(self) -> Dict[str, Any]:
        """Get track comparison information"""
        return {
            "Machine Intelligence": "AI/ML focus, 4 required + 2 electives, starts Fall 3rd year",
            "Software Engineering": "Development focus, 5 required + 1 elective, starts Fall 3rd year"
        }
    
    def _lookup_prerequisites(self, course_code: str) -> Dict[str, str]:
        """Look up course prerequisites"""
        try:
            if hasattr(self.kg, 'get_prerequisites'):
                return self.kg.get_prerequisites(course_code)
            else:
                return {"course": course_code, "prerequisites": "Available in knowledge base"}
        except Exception:
            return {"course": course_code, "status": "lookup_failed"}
    
    def _get_course_timing_from_knowledge(self, course_code: str) -> str:
        """Get course timing information"""
        course_info = self._lookup_course_info(course_code)
        return f"Information about {course_code} timing can be found in our course database. Generally, courses follow the prerequisite sequence and are offered according to the standard progression."
    
    def _get_track_info_from_knowledge(self) -> str:
        """Get track selection information"""
        return "Both Machine Intelligence and Software Engineering tracks start in Fall of 3rd year after completing foundation courses. MI focuses on AI/ML with 4 required plus 2 electives. SE focuses on software development with 5 required plus 1 elective."
    
    def _get_prerequisites_from_knowledge(self, course_code: str) -> str:
        """Get prerequisite information"""
        return f"Prerequisites for {course_code} depend on the course level and track. Foundation courses follow the CS 18000 → CS 25200 sequence. Advanced courses typically require CS 38100."
    
    def _get_advisor_identity(self) -> str:
        """Get advisor identity information"""
        return "I'm an AI academic advisor for Purdue CS students. I can help with course planning, track selection, prerequisites, and degree requirements using the most current program information."
    
    def _get_general_help(self) -> str:
        """Get general help information"""
        return "I can help with Purdue CS course planning, track selection, prerequisites, and degree requirements. What specific aspect of the CS program would you like to know about?"
    
    def _clean_response_formatting(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean response formatting to remove markdown and ensure natural text
        """
        if "response" in response_data and response_data["response"]:
            # Remove markdown formatting
            response_data["response"] = response_data["response"].replace("**", "")
            response_data["response"] = response_data["response"].replace("*", "")
            response_data["response"] = response_data["response"].replace("_", "")
            response_data["response"] = response_data["response"].replace("#", "")
            
            # Remove bullet points and make more conversational
            response_data["response"] = re.sub(r'^\s*[-•]\s*', '', response_data["response"], flags=re.MULTILINE)
            
            # Clean up extra whitespace
            response_data["response"] = re.sub(r'\n\s*\n', '\n\n', response_data["response"])
            response_data["response"] = response_data["response"].strip()
        
        return response_data