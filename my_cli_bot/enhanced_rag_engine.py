#!/usr/bin/env python3
"""
Enhanced RAG engine with knowledge graph integration and fact verification
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from google.generativeai import google.generativeai as genai
import numpy as np
from knowledge_graph import PurdueCSKnowledgeGraph, Course

class EnhancedRAGEngine:
    """Enhanced RAG engine with structured knowledge and fact verification"""
    
    def __init__(self, api_key: str = None):
        self.client = Gemini(api_key=api_key or os.getenv("GEMINI_API_KEY"))
        self.knowledge_graph = PurdueCSKnowledgeGraph()
        self.load_knowledge_graph()
        
    def load_knowledge_graph(self):
        """Load the knowledge graph"""
        try:
            if os.path.exists("data/cs_knowledge_graph.json"):
                self.knowledge_graph.load_from_json("data/cs_knowledge_graph.json")
                print("✓ Knowledge graph loaded")
            else:
                print("⚠ No knowledge graph found, creating default...")
                from knowledge_graph import create_purdue_cs_knowledge_graph
                self.knowledge_graph = create_purdue_cs_knowledge_graph()
                self.knowledge_graph.export_to_json("data/cs_knowledge_graph.json")
        except Exception as e:
            print(f"Error loading knowledge graph: {e}")
    
    def verify_course_info(self, course_code: str) -> Optional[Course]:
        """Verify course information against knowledge graph"""
        return self.knowledge_graph.courses.get(course_code)
    
    def get_accurate_prerequisites(self, course_code: str) -> List[str]:
        """Get verified prerequisites for a course"""
        return self.knowledge_graph.get_prerequisites(course_code)
    
    def get_track_info(self, track_name: str) -> Dict:
        """Get accurate track information"""
        return self.knowledge_graph.get_track_requirements(track_name)
    
    def fact_check_response(self, response: str, query: str) -> Dict:
        """Fact-check response against knowledge graph"""
        fact_check = {
            'verified_facts': [],
            'potential_errors': [],
            'confidence_score': 1.0
        }
        
        # Extract course codes from response
        import re
        course_codes = re.findall(r'CS\s+\d+', response)
        
        for code in course_codes:
            code = code.replace(' ', ' ')  # Normalize spacing
            course = self.verify_course_info(code)
            
            if course:
                fact_check['verified_facts'].append(f"✓ {code} exists: {course.title}")
            else:
                fact_check['potential_errors'].append(f"⚠ {code} not found in knowledge base")
                fact_check['confidence_score'] -= 0.2
        
        return fact_check
    
    def generate_verified_response(self, query: str, context: str = "") -> Dict:
        """Generate response with fact verification"""
        
        # Check if query is about specific courses
        import re
        course_codes = re.findall(r'CS\s+\d+', query)
        
        # Build structured context from knowledge graph
        structured_context = ""
        
        if course_codes:
            structured_context += "\n=== VERIFIED COURSE INFORMATION ===\n"
            for code in course_codes:
                course = self.verify_course_info(code)
                if course:
                    structured_context += f"{code}: {course.title} ({course.credits} cr)\n"
                    prereqs = self.get_accurate_prerequisites(code)
                    if prereqs:
                        structured_context += f"Prerequisites: {', '.join(prereqs)}\n"
                    structured_context += "\n"
        
        # Check for track-related queries
        track_keywords = {
            'machine intelligence': 'machine_intelligence',
            'artificial intelligence': 'machine_intelligence',
            'ai': 'machine_intelligence',
            'ml': 'machine_intelligence'
        }
        
        for keyword, track_name in track_keywords.items():
            if keyword in query.lower():
                track_info = self.get_track_info(track_name)
                if 'error' not in track_info:
                    structured_context += f"\n=== VERIFIED TRACK INFORMATION: {track_name.upper()} ===\n"
                    structured_context += f"Required courses:\n"
                    for course in track_info['required_courses']:
                        structured_context += f"- {course.code}: {course.title} ({course.credits} cr)\n"
                    structured_context += f"Elective options:\n"
                    for course in track_info['elective_options']:
                        structured_context += f"- {course.code}: {course.title} ({course.credits} cr)\n"
                    structured_context += f"Minimum electives required: {track_info['min_electives']}\n"
                break
        
        # Generate response with structured context
        messages = [
            {
                "role": "system",
                "content": """You are Roo_CS_Advisor, a Purdue Computer Science academic advisor.
                
ACCURACY REQUIREMENTS:
- Use ONLY the verified information provided in the structured context
- If information is not in the structured context, say "I don't have verified information about that"
- Never make up course numbers, prerequisites, or track requirements
- Always format courses as "CS XXXXX – Title (X cr)"
- Always prepend responses with "Bot> "

STRUCTURED CONTEXT PRIORITY:
- Information marked as "VERIFIED" takes absolute precedence
- Only use this information to answer course and track questions
- If the structured context is empty, explicitly state the limitation
"""
            },
            {
                "role": "user",
                "content": f"Structured Context:\n{structured_context}\n\nOriginal Context:\n{context}\n\nQuery: {query}"
            }
        ]
        
        try:
            response = self.client.generate_content(
                ,
                messages=messages,
                ,  # Lower temperature for more accurate responses
                
            )
            
            generated_response = response.text.strip()
            
            # Fact-check the response
            fact_check = self.fact_check_response(generated_response, query)
            
            return {
                'response': generated_response,
                'fact_check': fact_check,
                'structured_context_used': bool(structured_context),
                'confidence_score': fact_check['confidence_score']
            }
            
        except Exception as e:
            return {
                'response': f"Bot> I encountered an error: {str(e)}",
                'fact_check': {'verified_facts': [], 'potential_errors': [str(e)], 'confidence_score': 0.0},
                'structured_context_used': False,
                'confidence_score': 0.0
            }

def main():
    """Test the enhanced RAG engine"""
    engine = EnhancedRAGEngine()
    
    test_queries = [
        "What are the six core CS courses?",
        "What are the prerequisites for CS 25000?",
        "Tell me about the machine intelligence track",
        "Can I take CS 35400 before CS 25200?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print(f"{'='*50}")
        
        result = engine.generate_verified_response(query)
        
        print(f"Response: {result['response']}")
        print(f"Confidence: {result['confidence_score']:.2f}")
        print(f"Structured context used: {result['structured_context_used']}")
        
        if result['fact_check']['verified_facts']:
            print("Verified facts:")
            for fact in result['fact_check']['verified_facts']:
                print(f"  {fact}")
        
        if result['fact_check']['potential_errors']:
            print("Potential errors:")
            for error in result['fact_check']['potential_errors']:
                print(f"  {error}")

if __name__ == "__main__":
    main()