#!/usr/bin/env python3
"""
Enhanced Knowledge Pipeline - Direct AI + Knowledge Base Integration
Fixes the core issues: knowledge access, AI integration, and response quality
"""

import json
import os
import google.generativeai as genai
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

class EnhancedKnowledgePipeline:
    """
    Streamlined pipeline that directly connects knowledge base to AI
    No complex routing - just: Query → Knowledge → AI → Response
    """
    
    def __init__(self, knowledge_file: str = "data/cs_knowledge_graph.json"):
        # Load knowledge base
        self.knowledge_base = self.load_knowledge_base(knowledge_file)
        
        # Initialize Gemini (if available)
        self.gemini_model = None
        self.use_ai = False
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                # Test the API
                test_response = self.gemini_model.generate_content(
                    ,
                    prompt,
                    
                )
                self.use_ai = True
                print("✅ Gemini AI enabled for knowledge synthesis")
            except Exception as e:
                print(f"⚠️ Gemini unavailable: {e}. Using knowledge-base-only responses.")
        else:
            print("💡 Running in knowledge-base-only mode (no Gemini API key)")
    
    def load_knowledge_base(self, knowledge_file: str) -> Dict[str, Any]:
        """Load and structure knowledge base for easy access"""
        try:
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # Structure knowledge for direct access
            structured_knowledge = {
                "courses": raw_data.get("courses", {}),
                "tracks": raw_data.get("tracks", {}),
                "degree_requirements": raw_data.get("degree_requirements", {}),
                "codo_requirements": raw_data.get("codo_requirements", {}),
                "academic_policies": raw_data.get("academic_policies", {}),
                "career_guidance": raw_data.get("career_guidance", {}),
                "graduation_timelines": raw_data.get("graduation_timelines", {}),
                "prerequisites": raw_data.get("prerequisites", {}),
                "failure_recovery": raw_data.get("failure_recovery", {})
            }
            
            print(f"✅ Knowledge base loaded: {len(structured_knowledge['courses'])} courses")
            return structured_knowledge
            
        except FileNotFoundError:
            print("❌ Knowledge base file not found")
            return {"courses": {}, "tracks": {}, "degree_requirements": {}}
        except Exception as e:
            print(f"❌ Error loading knowledge base: {e}")
            return {"courses": {}, "tracks": {}, "degree_requirements": {}}
    
    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract course codes, tracks, and other entities from query"""
        entities = {
            "course_codes": [],
            "track_names": [],
            "student_year": None,
            "gpa": None,
            "intent_keywords": []
        }
        
        # Extract course codes (CS 18000, MA 16100, etc.)
        course_pattern = re.compile(r'(cs|ma|math|stat|phys|engr|com|engl)\s*(\d{5}|\d{3,4})', re.IGNORECASE)
        course_matches = course_pattern.findall(query)
        entities["course_codes"] = [f"{match[0].upper()} {match[1]}" for match in course_matches]
        
        # Extract tracks
        query_lower = query.lower()
        if any(term in query_lower for term in ["machine intelligence", "mi track", "ai", "ml"]):
            entities["track_names"].append("Machine Intelligence")
        if any(term in query_lower for term in ["software engineering", "se track", "software dev"]):
            entities["track_names"].append("Software Engineering")
        
        # Extract student year
        year_patterns = ["freshman", "sophomore", "junior", "senior", "1st year", "2nd year", "3rd year", "4th year"]
        for pattern in year_patterns:
            if pattern in query_lower:
                entities["student_year"] = pattern.replace("1st year", "freshman").replace("2nd year", "sophomore").replace("3rd year", "junior").replace("4th year", "senior")
                break
        
        # Extract GPA if mentioned
        gpa_match = re.search(r'(\d\.\d+)\s*gpa|gpa\s*(\d\.\d+)', query_lower)
        if gpa_match:
            entities["gpa"] = float(gpa_match.group(1) or gpa_match.group(2))
        
        # Intent keywords
        if any(term in query_lower for term in ["prerequisite", "prereq", "before taking"]):
            entities["intent_keywords"].append("prerequisites")
        if any(term in query_lower for term in ["graduation", "graduate", "timeline"]):
            entities["intent_keywords"].append("graduation_planning")
        if any(term in query_lower for term in ["codo", "change major", "transfer"]):
            entities["intent_keywords"].append("codo")
        if any(term in query_lower for term in ["failed", "failing", "retake"]):
            entities["intent_keywords"].append("failure_recovery")
        
        return entities
    
    def fetch_relevant_knowledge(self, entities: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Fetch all relevant knowledge based on entities and query"""
        relevant_data = {}
        
        # Fetch course information
        if entities["course_codes"]:
            relevant_data["courses"] = {}
            for course_code in entities["course_codes"]:
                if course_code in self.knowledge_base["courses"]:
                    relevant_data["courses"][course_code] = self.knowledge_base["courses"][course_code]
        
        # Fetch track information
        if entities["track_names"]:
            relevant_data["tracks"] = {}
            for track_name in entities["track_names"]:
                if track_name in self.knowledge_base["tracks"]:
                    relevant_data["tracks"][track_name] = self.knowledge_base["tracks"][track_name]
        
        # Fetch based on intent
        if "prerequisites" in entities["intent_keywords"]:
            relevant_data["prerequisites"] = self.knowledge_base["prerequisites"]
        
        if "graduation_planning" in entities["intent_keywords"]:
            relevant_data["graduation_timelines"] = self.knowledge_base["graduation_timelines"]
            relevant_data["degree_requirements"] = self.knowledge_base["degree_requirements"]
        
        if "codo" in entities["intent_keywords"]:
            relevant_data["codo_requirements"] = self.knowledge_base["codo_requirements"]
        
        if "failure_recovery" in entities["intent_keywords"]:
            relevant_data["failure_recovery"] = self.knowledge_base["failure_recovery"]
        
        # Always include general data for context
        relevant_data["academic_policies"] = self.knowledge_base["academic_policies"]
        
        return relevant_data
    
    def generate_knowledge_only_response(self, query: str, entities: Dict[str, Any], knowledge: Dict[str, Any]) -> str:
        """Generate response using only knowledge base (no AI)"""
        
        # Course information queries
        if entities["course_codes"]:
            response_parts = []
            for course_code in entities["course_codes"]:
                if course_code in knowledge.get("courses", {}):
                    course_info = knowledge["courses"][course_code]
                    response_parts.append(f"{course_code} - {course_info.get('title', 'No title available')}")
                    response_parts.append(f"Credits: {course_info.get('credits', 'N/A')}")
                    response_parts.append(f"Description: {course_info.get('description', 'No description available')}")
                    
                    if course_info.get('difficulty_rating'):
                        response_parts.append(f"Difficulty Rating: {course_info['difficulty_rating']}/5.0")
                    
                    response_parts.append("")  # Empty line
                else:
                    response_parts.append(f"Course {course_code} not found in knowledge base.")
            
            if not response_parts:
                # Use AI for course not found response
                try:
                    return self._generate_ai_response(
                        "The user asked about a course but it wasn't found in the knowledge base. Provide a helpful response suggesting they check the course code or contact an advisor.",
                        {"context": "course_not_found", "query": query}
                    )
                except:
                    return "I couldn't find information about that course. Please verify the course code or contact a CS advisor for assistance."
            return "\n".join(response_parts)
        
        # Track information queries
        if entities["track_names"]:
            response_parts = []
            for track_name in entities["track_names"]:
                if track_name in knowledge.get("tracks", {}):
                    track_info = knowledge["tracks"][track_name]
                    response_parts.append(f"{track_name} Track:")
                    response_parts.append(f"Description: {track_info.get('description', 'No description available')}")
                    
                    if track_info.get("required_courses"):
                        response_parts.append("Required Courses:")
                        for course in track_info["required_courses"]:
                            response_parts.append(f"  • {course}")
                    
                    response_parts.append("")
                else:
                    response_parts.append(f"{track_name} track information not found.")
            
            if not response_parts:
                # Use AI for track not found response
                try:
                    return self._generate_ai_response(
                        "The user asked about a track but it wasn't found in the knowledge base. Provide a helpful response with available tracks or suggest contacting an advisor.",
                        {"context": "track_not_found", "query": query}
                    )
                except:
                    return "I couldn't find information about that track. The available tracks are Machine Intelligence and Software Engineering. Please contact a CS advisor for more details."
            return "\n".join(response_parts)
        
        # CODO queries
        if "codo" in entities["intent_keywords"] and "codo_requirements" in knowledge:
            codo_info = knowledge["codo_requirements"]
            response_parts = [
                "CODO (Change of Degree Objective) Requirements for Computer Science:",
                ""
            ]
            
            if isinstance(codo_info, dict):
                for key, value in codo_info.items():
                    response_parts.append(f"{key.replace('_', ' ').title()}: {value}")
            elif isinstance(codo_info, str):
                response_parts.append(codo_info)
            
            return "\n".join(response_parts)
        
        # Default knowledge-based response
        available_sections = []
        for section, data in knowledge.items():
            if data and section != "academic_policies":
                available_sections.append(section.replace("_", " ").title())
        
        # Use AI for default response
        try:
            context = {"available_sections": available_sections, "query": query}
            return self._generate_ai_response(
                "The user's query didn't match specific patterns. Generate a helpful response based on available information sections.",
                context
            )
        except:
            if available_sections:
                return f"I have information about: {', '.join(available_sections)}. Please be more specific about what you'd like to know."
            else:
                return "I have access to Purdue CS information but couldn't find relevant data for your query. Please try rephrasing your question."
    
    def generate_ai_enhanced_response(self, query: str, entities: Dict[str, Any], knowledge: Dict[str, Any]) -> str:
        """Generate AI-enhanced response using knowledge base context"""
        
        # Build comprehensive context from knowledge
        context_parts = []
        
        # Add relevant knowledge sections
        for section_name, section_data in knowledge.items():
            if section_data:
                context_parts.append(f"{section_name.upper()}:")
                if isinstance(section_data, dict):
                    for key, value in list(section_data.items())[:3]:  # Limit to prevent token overflow
                        context_parts.append(f"  {key}: {str(value)[:200]}...")
                else:
                    context_parts.append(f"  {str(section_data)[:300]}...")
                context_parts.append("")
        
        # Build comprehensive prompt
        prompt = f"""You are BoilerAI, a helpful Purdue Computer Science academic advisor. Use the provided knowledge base to answer the student's question accurately and helpfully.

STUDENT QUERY: {query}

EXTRACTED ENTITIES: {entities}

RELEVANT KNOWLEDGE BASE DATA:
{chr(10).join(context_parts)}

INSTRUCTIONS:
1. Use ONLY the provided knowledge base information
2. Be specific and accurate with course codes, requirements, and policies
3. If you don't have the exact information, say so and suggest alternatives
4. Write in a friendly, conversational tone
5. Include specific details like course codes, credit hours, prerequisites
6. For complex questions, break down the answer into clear sections

Provide a comprehensive, helpful response:"""

        try:
            response = self.gemini_model.generate_content(
                ,
                prompt,
                ,
                
            )
            
            return response.text.strip()
            
        except Exception as e:
            print(f"⚠️ AI generation failed: {e}, using knowledge-only response")
            return self.generate_knowledge_only_response(query, entities, knowledge)
    
    def _generate_ai_response(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate AI response for error/fallback scenarios"""
        if not self.gemini_model:
            raise Exception("Gemini client not available")
        
        full_prompt = f"""You are BoilerAI, a helpful Purdue CS academic advisor.
        
        Context: {context}
        
        Task: {prompt}
        
        Generate a natural, helpful response that sounds like a knowledgeable advisor."""
        
        response = self.gemini_model.generate_content(
            ,
            prompt,
            ,
            
        )
        
        return response.text.strip()
    
    def process_query(self, query: str) -> str:
        """Main method: process query and return response"""
        
        print(f"\n🎯 Processing: {query}")
        
        # Step 1: Extract entities
        entities = self.extract_entities(query)
        print(f"📊 Entities: {entities}")
        
        # Step 2: Fetch relevant knowledge
        knowledge = self.fetch_relevant_knowledge(entities, query)
        print(f"📚 Knowledge sections: {list(knowledge.keys())}")
        
        # Step 3: Generate response
        if self.use_ai and knowledge:
            print("🤖 Generating AI-enhanced response...")
            response = self.generate_ai_enhanced_response(query, entities, knowledge)
        else:
            print("📖 Generating knowledge-only response...")
            response = self.generate_knowledge_only_response(query, entities, knowledge)
        
        print(f"✅ Response generated ({len(response)} characters)")
        return response

def main():
    """Test the enhanced pipeline"""
    pipeline = EnhancedKnowledgePipeline()
    
    # Test queries
    test_queries = [
        "What is CS 18000?",
        "Tell me about the Machine Intelligence track",
        "What are the CODO requirements?",
        "What courses should I take as a sophomore?",
        "What are the prerequisites for CS 25100?"
    ]
    
    print("🧪 Testing Enhanced Knowledge Pipeline")
    print("=" * 60)
    
    for query in test_queries:
        response = pipeline.process_query(query)
        print(f"\n💬 Response:\n{response}")
        print("\n" + "="*60)

if __name__ == "__main__":
    main()