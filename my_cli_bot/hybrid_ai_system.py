#!/usr/bin/env python3
"""
Hybrid AI System for Boiler AI - Purdue CS Academic Advisor
Implements Logic + LLM approach: Lookup tables → Rule-based logic → Google Gemini
"""

import json
import re
import os
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import google.generativeai as genai
from enum import Enum

class QueryType(Enum):
    LOOKUP_TABLE = "lookup_table"
    RULE_BASED = "rule_based"
    LLM_ENHANCED = "llm_enhanced"
    HYBRID = "hybrid"

@dataclass
class QueryClassification:
    query_type: QueryType
    intent: str
    entities: Dict[str, Any]
    confidence: float
    should_use_llm: bool
    lookup_result: Optional[Dict] = None

class HybridAISystem:
    """
    Hybrid AI System that routes queries through:
    1. Lookup Tables (for official answers)
    2. Rule-based Logic (for structured queries)
    3. Google Gemini (for flexibility when needed)
    """
    
    def __init__(self, data_path: str = "data/cs_knowledge_graph.json"):
        self.data_path = data_path
        self.knowledge_base = {}
        self.lookup_tables = {}
        self.rule_patterns = {}
        # Initialize LLM provider based on environment
        provider = os.environ.get("LLM_PROVIDER", "gemini").lower()
        if provider == "openai":
            openai_key = os.environ.get("OPENAI_API_KEY")
            if not openai_key:
                raise ValueError("OPENAI_API_KEY not set. Provide a key at startup.")
            # Lazy-import to avoid dependency if unused
            try:
                import openai
                openai.api_key = openai_key
                self.openai_client = openai
                self.gemini_model = None
                print("✅ OpenAI provider initialized")
            except Exception as e:
                raise ValueError(f"OpenAI initialization failed: {e}")
        else:
            gemini_key = os.environ.get("GEMINI_API_KEY")
            if not gemini_key:
                raise ValueError("GEMINI_API_KEY not set. Provide a key at startup.")
            # Configure Gemini
            genai.configure(api_key=gemini_key)
            # Configure safety settings
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
            ]
            self.gemini_model = genai.GenerativeModel('models/gemini-2.5-flash', safety_settings=safety_settings)
            # Test the API key immediately
            try:
                _ = self.gemini_model.generate_content("Hello")
                print("✅ Gemini API key validated successfully")
            except Exception as e:
                raise ValueError(f"Gemini API key validation failed: {e}")
        
        self.load_knowledge_base()
        self.build_lookup_tables()
        self.define_rule_patterns()
        
        print("🤖 Hybrid AI System initialized with Logic + LLM architecture using Gemini")
    
    def load_knowledge_base(self):
        """Load comprehensive knowledge base"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
            print(f"✓ Knowledge base loaded: {len(self.knowledge_base.get('courses', {}))} courses")
        except FileNotFoundError:
            print("⚠️ Knowledge base not found, using empty base")
            self.knowledge_base = {"courses": {}, "tracks": {}, "policies": {}}
    
    def build_lookup_tables(self):
        """Build lookup tables for instant official answers"""
        
        # Course information lookup table
        self.lookup_tables["course_info"] = {}
        for course_id, course_data in self.knowledge_base.get("courses", {}).items():
            # Normalize course ID patterns
            normalized_id = self.normalize_course_id(course_id)
            self.lookup_tables["course_info"][normalized_id] = {
                "title": course_data.get("title", ""),
                "credits": course_data.get("credits", 0),
                "description": course_data.get("description", ""),
                "prerequisites": course_data.get("prerequisites", []),
                "difficulty_rating": course_data.get("difficulty_rating", 0),
                "course_type": course_data.get("course_type", ""),
                "semester": course_data.get("semester", "Any")
            }
        
        # Track requirements lookup table
        self.lookup_tables["track_requirements"] = {
            "machine_intelligence": {
                "name": "Machine Intelligence (MI)",
                "description": "Focus on AI, Machine Learning, and Data Science",
                "required_courses": [
                    "CS 37300 - Data Mining and Machine Learning",
                    "CS 48300 - Fundamentals of Artificial Intelligence", 
                    "CS 57300 - Neural Networks",
                    "CS 54401 - Numerical Methods",
                    "STAT 51100 - Statistical Methods"
                ],
                "career_paths": ["AI Engineer", "Data Scientist", "ML Engineer", "Research Scientist"],
                "total_credits": 15
            },
            "software_engineering": {
                "name": "Software Engineering (SE)",
                "description": "Focus on large-scale software development and engineering practices",
                "required_courses": [
                    "CS 30700 - Software Engineering I", 
                    "CS 40800 - Software Engineering II",
                    "CS 41000 - Numerical Computing",
                    "CS 42200 - Computer Networks",
                    "CS 34800 - Information Systems"
                ],
                "career_paths": ["Software Engineer", "DevOps Engineer", "System Architect", "Technical Lead"],
                "total_credits": 15
            }
        }
        
        # CODO requirements lookup table
        self.lookup_tables["codo_requirements"] = {
            "minimum_gpa": 2.75,
            "required_courses": {
                "CS 18000": {"grade": "B", "description": "Problem Solving and Object-Oriented Programming"},
            },
            "math_requirement": "B or better in ONE of: MA 16100, MA 16200, MA 26100, MA 26500",
            "other_requirements": [
                "Minimum 1 semester at Purdue",
                "Minimum 12 credit hours at Purdue main campus",
                "Good academic standing (not on academic notice)",
                "Space available basis only"
            ],
            "application_terms": ["Fall", "Spring", "Summer"],
            "contact": "csug@purdue.edu"
        }
        
        # Academic policies lookup table
        self.lookup_tables["academic_policies"] = {
            "gpa_requirements": {
                "good_standing": 2.0,
                "codo_cs": 2.75,
                "deans_list": 3.5,
                "graduation_honors": 3.5
            },
            "credit_requirements": {
                "total_graduation": 120,
                "cs_core": 45,
                "track_requirements": 15,
                "math_science": 30,
                "general_education": 30
            },
            "course_load_limits": {
                "freshman_cs": 2,
                "sophomore_plus_cs": 3,
                "summer_cs": 2,
                "maximum_total": 18
            }
        }
        
        # Prerequisite chains lookup table
        self.lookup_tables["prerequisite_chains"] = {
            "CS 25000": ["CS 18000", "CS 18200", "CS 24000"],
            "CS 25100": ["CS 18000", "CS 18200", "CS 24000"],
            "CS 25200": ["CS 25000", "CS 25100"],
            "CS 30700": ["CS 25200"],
            "CS 37300": ["CS 25200", "STAT 51100"],
            "CS 48300": ["CS 25200"]
        }
        
        print(f"✓ Built {len(self.lookup_tables)} lookup tables")
    
    def define_rule_patterns(self):
        """Define rule-based patterns for structured queries"""
        
        self.rule_patterns = {
            # Course information patterns
            "course_info": {
                "patterns": [
                    r"what is (cs|math|stat|phys)\s*(\d{5}|\d{3})",
                    r"tell me about (cs|math|stat|phys)\s*(\d{5}|\d{3})", 
                    r"describe (cs|math|stat|phys)\s*(\d{5}|\d{3})",
                    r"(cs|math|stat|phys)\s*(\d{5}|\d{3})\s*(description|info)"
                ],
                "handler": "handle_course_info"
            },
            
            # Prerequisites patterns
            "prerequisites": {
                "patterns": [
                    r"prerequisites for (cs|math|stat|phys)\s*(\d{5}|\d{3})",
                    r"what do i need for (cs|math|stat|phys)\s*(\d{5}|\d{3})",
                    r"prereqs for (cs|math|stat|phys)\s*(\d{5}|\d{3})",
                    r"what comes before (cs|math|stat|phys)\s*(\d{5}|\d{3})"
                ],
                "handler": "handle_prerequisites"
            },
            
            # Track requirements patterns
            "track_requirements": {
                "patterns": [
                    r"(machine intelligence|mi)\s*(track|requirements)",
                    r"(software engineering|se)\s*(track|requirements)",
                    r"track requirements",
                    r"what.*track.*courses",
                    r"both.*tracks",
                    r"dual.*track",
                    r"se.*and.*mi",
                    r"mi.*and.*se",
                    r"two tracks"
                ],
                "handler": "handle_track_requirements"
            },
            
            # CODO patterns
            "codo": {
                "patterns": [
                    r"codo into cs",
                    r"change.*to computer science",
                    r"switch.*to cs",
                    r"codo requirements",
                    r"how to get into cs"
                ],
                "handler": "handle_codo"
            },
            
            # Course failure patterns
            "course_failure": {
                "patterns": [
                    r"failed (cs|math|stat|phys)\s*(\d{5}|\d{3})",
                    r"failing (cs|math|stat|phys)\s*(\d{5}|\d{3})",
                    r"retake (cs|math|stat|phys)\s*(\d{5}|\d{3})",
                    r"what if i fail"
                ],
                "handler": "handle_course_failure"
            },
            
            # Graduation planning patterns
            "graduation_planning": {
                "patterns": [
                    r"graduate.*asap",
                    r"graduation.*plan",
                    r"curate.*plan",
                    r"fastest.*graduation",
                    r"plan.*graduate",
                    r"timeline.*graduate"
                ],
                "handler": "handle_graduation_planning"
            }
        }
        
        print(f"✓ Defined {len(self.rule_patterns)} rule pattern categories")
    
    def normalize_course_id(self, course_id: str) -> str:
        """Normalize course ID for consistent lookup"""
        # Remove spaces and convert to uppercase
        normalized = re.sub(r'\s+', ' ', course_id.upper().strip())
        # Ensure format like "CS 18000"
        match = re.match(r'([A-Z]+)\s*(\d{3,5})', normalized)
        if match:
            return f"{match.group(1)} {match.group(2)}"
        return normalized
    
    def extract_course_entities(self, query: str) -> List[str]:
        """Extract course codes from query"""
        course_pattern = re.compile(r'(cs|math|stat|phys|engr)\s*(\d{5}|\d{3})', re.IGNORECASE)
        matches = course_pattern.findall(query)
        return [self.normalize_course_id(f"{match[0]} {match[1]}") for match in matches]
    
    def classify_query(self, query: str) -> QueryClassification:
        """
        Classify query to determine routing strategy:
        1. Check if it can be answered by lookup tables
        2. Check if it matches rule patterns  
        3. Determine if LLM enhancement needed
        """
        
        query_lower = query.lower()
        entities = {"courses": self.extract_course_entities(query)}
        
        # Check for exact lookup table matches
        lookup_result = None
        intent = "general"
        confidence = 0.0
        
        # Pattern matching for intent classification
        for pattern_intent, pattern_data in self.rule_patterns.items():
            for pattern in pattern_data["patterns"]:
                if re.search(pattern, query_lower):
                    intent = pattern_intent
                    confidence = 0.9
                    break
            if confidence > 0:
                break
        
        # Check if we can answer directly from lookup tables
        can_use_lookup = False
        if intent == "course_info" and entities["courses"]:
            # Check if all courses exist in lookup table
            course = entities["courses"][0]
            if course in self.lookup_tables["course_info"]:
                lookup_result = self.lookup_tables["course_info"][course]
                can_use_lookup = True
        
        elif intent == "track_requirements":
            # Extract track from query - handle dual track requests
            if any(word in query_lower for word in ["both", "dual", "two tracks", "se and mi", "mi and se"]):
                # Dual track request - combine both tracks
                lookup_result = {
                    "dual_track": True,
                    "mi_track": self.lookup_tables["track_requirements"]["machine_intelligence"],
                    "se_track": self.lookup_tables["track_requirements"]["software_engineering"]
                }
                can_use_lookup = True
            elif any(word in query_lower for word in ["machine intelligence", "mi"]):
                lookup_result = self.lookup_tables["track_requirements"]["machine_intelligence"]
                can_use_lookup = True
            elif any(word in query_lower for word in ["software engineering", "se"]):
                lookup_result = self.lookup_tables["track_requirements"]["software_engineering"]
                can_use_lookup = True
        
        elif intent == "codo":
            lookup_result = self.lookup_tables["codo_requirements"]
            can_use_lookup = True
        
        # Determine query type and LLM usage
        if can_use_lookup and confidence > 0.8:
            query_type = QueryType.LOOKUP_TABLE
            should_use_llm = False
        elif confidence > 0.7:
            query_type = QueryType.RULE_BASED
            should_use_llm = False
        else:
            query_type = QueryType.LLM_ENHANCED
            should_use_llm = True
            confidence = 0.6
        
        return QueryClassification(
            query_type=query_type,
            intent=intent,
            entities=entities,
            confidence=confidence,
            should_use_llm=should_use_llm,
            lookup_result=lookup_result
        )
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Main query processing with hybrid routing:
        1. Classify query
        2. Route to appropriate handler
        3. Enhance with LLM if needed
        """
        
        classification = self.classify_query(query)
        
        print(f"🎯 Query classification: {classification.query_type.value}")
        print(f"📊 Intent: {classification.intent}, Confidence: {classification.confidence:.2f}")
        
        # Route to appropriate handler
        if classification.query_type == QueryType.LOOKUP_TABLE:
            result = self.handle_lookup_table(query, classification)
        elif classification.query_type == QueryType.RULE_BASED:
            result = self.handle_rule_based(query, classification)
        else:
            result = self.handle_llm_enhanced(query, classification)
        
        # Enhance with LLM if needed
        if classification.should_use_llm and result.get("enhance_with_llm", True):
            result = self.enhance_with_gemini(query, result, classification)
        
        return {
            "response": result.get("response", "I couldn't process your query."),
            "classification": classification.query_type.value,
            "intent": classification.intent,
            "confidence": classification.confidence,
            "source": result.get("source", "hybrid_system"),
            "timestamp": datetime.now().isoformat()
        }
    
    def handle_lookup_table(self, query: str, classification: QueryClassification) -> Dict[str, Any]:
        """Handle queries that can be answered directly from lookup tables"""
        
        if not classification.lookup_result:
            return {"response": "Lookup data not found", "enhance_with_llm": True}
        
        if classification.intent == "course_info":
            course = classification.entities["courses"][0]
            data = classification.lookup_result
            
            response = f"{course} - {data['title']}\n\n"
            response += f"Credits: {data['credits']}\n"
            response += f"Description: {data['description']}\n"
            
            if data.get('difficulty_rating'):
                response += f"Difficulty Rating: {data['difficulty_rating']}/5.0\n"
            
            if data.get('semester'):
                response += f"Typical Semester: {data['semester']}\n"
            
            return {
                "response": response,
                "source": "lookup_table",
                "enhance_with_llm": False
            }
        
        elif classification.intent == "track_requirements":
            data = classification.lookup_result
            
            if data.get("dual_track"):
                # Handle dual track request
                mi_data = data["mi_track"]
                se_data = data["se_track"]
                
                response = "DUAL TRACK PLAN: Machine Intelligence + Software Engineering\n\n"
                
                # Calculate combined requirements
                mi_courses = set(mi_data['required_courses'])
                se_courses = set(se_data['required_courses'])
                shared_courses = mi_courses.intersection(se_courses)
                total_unique_courses = mi_courses.union(se_courses)
                
                response += f"OVERVIEW:\n"
                response += f"• Total unique courses needed: {len(total_unique_courses)}\n"
                response += f"• MI-specific courses: {len(mi_courses - se_courses)}\n"
                response += f"• SE-specific courses: {len(se_courses - mi_courses)}\n"
                response += f"• Shared courses: {len(shared_courses)}\n\n"
                
                response += "MACHINE INTELLIGENCE REQUIREMENTS:\n"
                for course in mi_data['required_courses']:
                    marker = "(SHARED)" if course in shared_courses else ""
                    response += f"• {course} {marker}\n"
                
                response += "\nSOFTWARE ENGINEERING REQUIREMENTS:\n"
                for course in se_data['required_courses']:
                    marker = "(SHARED)" if course in shared_courses else ""
                    response += f"• {course} {marker}\n"
                
                response += f"\nESTIMATED TIMELINE:\n"
                response += f"• Minimum additional semesters: {max(3, len(total_unique_courses) // 3)}\n"
                response += f"• Recommended course load: 2-3 track courses per semester\n\n"
                
                response += "CAREER OPPORTUNITIES:\n"
                all_careers = set(mi_data['career_paths'] + se_data['career_paths'])
                for career in sorted(all_careers):
                    response += f"• {career}\n"
                
                return {
                    "response": response,
                    "source": "lookup_table",
                    "enhance_with_llm": True  # This complex plan can benefit from LLM enhancement
                }
            else:
                # Single track request
                response = f"{data['name']}\n\n"
                response += f"Description: {data['description']}\n\n"
                response += "Required Courses:\n"
                for course in data['required_courses']:
                    response += f"• {course}\n"
                response += f"\nTotal Credits: {data['total_credits']}\n\n"
                response += "Career Paths:\n"
                for career in data['career_paths']:
                    response += f"• {career}\n"
                
                return {
                    "response": response,
                    "source": "lookup_table",
                    "enhance_with_llm": False
                }
        
        elif classification.intent == "codo":
            data = classification.lookup_result
            
            response = "CODO into Computer Science Requirements\n\n"
            response += f"Minimum GPA: {data['minimum_gpa']}\n\n"
            response += "Required Courses:\n"
            for course, req in data['required_courses'].items():
                response += f"• {course}: {req['grade']} or better - {req['description']}\n"
            response += f"\nMath Requirement: {data['math_requirement']}\n\n"
            response += "Other Requirements:\n"
            for req in data['other_requirements']:
                response += f"• {req}\n"
            response += f"\nApplication Terms: {', '.join(data['application_terms'])}\n"
            response += f"Contact: {data['contact']}\n"
            
            return {
                "response": response,
                "source": "lookup_table", 
                "enhance_with_llm": False
            }
        
        return {"response": "Lookup handler not implemented for this intent", "enhance_with_llm": True}
    
    def handle_rule_based(self, query: str, classification: QueryClassification) -> Dict[str, Any]:
        """Handle queries using rule-based logic"""
        
        if classification.intent == "prerequisites":
            courses = classification.entities["courses"]
            if not courses:
                return {"response": "Please specify which course you need prerequisite information for.", "enhance_with_llm": True}
            
            course = courses[0]
            prereq_chain = self.lookup_tables["prerequisite_chains"].get(course, [])
            
            if prereq_chain:
                response = f"Complete prerequisite chain for {course}:\n\n"
                response += "You must complete these courses in order:\n"
                for i, prereq in enumerate(prereq_chain, 1):
                    response += f"{i}. {prereq}\n"
                response += f"\nThen you can take {course}"
            else:
                response = f"{course} has no prerequisites listed in our system."
            
            return {
                "response": response,
                "source": "rule_based",
                "enhance_with_llm": False
            }
        
        elif classification.intent == "course_failure":
            courses = classification.entities["courses"]
            if not courses:
                return {"response": "Please specify which course you failed or are concerned about.", "enhance_with_llm": True}
            
            course = courses[0]
            course_info = self.lookup_tables["course_info"].get(course, {})
            
            response = f"Course Failure Recovery for {course}\n\n"
            
            if course_info.get("is_critical"):
                response += "⚠️ This is a critical foundation course. Failure will impact your graduation timeline.\n\n"
            
            response += "Immediate Steps:\n"
            response += "1. Meet with your academic advisor\n"
            response += "2. Understand why you failed\n"
            response += "3. Plan retake strategy\n"
            response += "4. Consider support resources\n\n"
            
            # Check what courses depend on this one
            dependent_courses = []
            for dep_course, prereqs in self.lookup_tables["prerequisite_chains"].items():
                if course in prereqs:
                    dependent_courses.append(dep_course)
            
            if dependent_courses:
                response += f"Courses you cannot take until retaking {course}:\n"
                for dep in dependent_courses:
                    response += f"• {dep}\n"
            
            return {
                "response": response,
                "source": "rule_based",
                "enhance_with_llm": True  # This can benefit from LLM enhancement
            }
        
        elif classification.intent == "graduation_planning":
            # Handle graduation planning requests
            entities = classification.entities
            
            # Check if it's a dual track request
            query_lower = query.lower()
            if any(word in query_lower for word in ["both", "dual", "two tracks", "se and mi", "mi and se"]):
                response = "ACCELERATED DUAL TRACK GRADUATION PLAN\n\n"
                response += "OVERVIEW:\n"
                response += "Completing both Machine Intelligence and Software Engineering tracks requires strategic planning.\n\n"
                
                response += "REQUIREMENTS ANALYSIS:\n"
                response += "• MI Track: 5 courses (15 credits)\n"
                response += "• SE Track: 5 courses (15 credits)\n"
                response += "• Total unique courses: ~8-9 (some overlap possible)\n"
                response += "• Core CS courses: Still required (CS 18000-25200 sequence)\n\n"
                
                response += "FASTEST TIMELINE STRATEGY:\n"
                response += "• Complete all foundation courses first (CS 18000, 18200, 24000, 25000, 25100, 25200)\n"
                response += "• Take 2-3 track courses per semester\n"
                response += "• Use summer sessions for acceleration\n"
                response += "• Consider course overlap and prerequisites\n\n"
                
                response += "SEMESTER RECOMMENDATIONS:\n"
                response += "• Avoid taking more than 2 advanced CS courses per semester\n"
                response += "• Balance difficulty - mix easier and harder track courses\n"
                response += "• Plan around course offering schedules\n\n"
                
                response += "REALISTIC TIMELINE:\n"
                response += "• Minimum: 4 years (very aggressive, requires summer courses)\n"
                response += "• Recommended: 4.5-5 years (more manageable workload)\n"
                response += "• Depends on: Current year, completed courses, GPA goals\n\n"
                
                response += "NEXT STEPS:\n"
                response += "• Share your current completed courses for a personalized plan\n"
                response += "• Meet with academic advisor to verify feasibility\n"
                response += "• Consider internship timeline impact\n"
                
                return {
                    "response": response,
                    "source": "rule_based",
                    "enhance_with_llm": True
                }
            else:
                response = "GRADUATION PLANNING ASSISTANCE\n\n"
                response += "To create an optimal graduation plan, I need to know:\n"
                response += "• Your current year level\n"
                response += "• Courses already completed\n"
                response += "• Target track(s)\n"
                response += "• Any specific timeline goals\n\n"
                response += "Please provide this information for a personalized plan."
                
                return {
                    "response": response,
                    "source": "rule_based",
                    "enhance_with_llm": True
                }
        
        return {"response": "Rule-based handler not implemented for this intent", "enhance_with_llm": True}
    
    def handle_llm_enhanced(self, query: str, classification: QueryClassification) -> Dict[str, Any]:
        """Handle complex queries that require LLM processing"""
        
        # Build context from knowledge base
        context_parts = []
        
        # Add relevant course information
        if classification.entities.get("courses"):
            for course in classification.entities["courses"]:
                course_info = self.lookup_tables["course_info"].get(course)
                if course_info:
                    context_parts.append(f"{course}: {course_info}")
        
        # Add relevant track information based on query content
        query_lower = query.lower()
        if any(word in query_lower for word in ["track", "machine intelligence", "software engineering"]):
            context_parts.append(f"Track Requirements: {self.lookup_tables['track_requirements']}")
        
        # Add CODO info if relevant
        if any(word in query_lower for word in ["codo", "change major", "switch"]):
            context_parts.append(f"CODO Requirements: {self.lookup_tables['codo_requirements']}")
        
        context = "\n".join(context_parts)
        
        prompt = f"""You are an expert Purdue Computer Science academic advisor helping a student.

Student Question: "{query}"
Query Intent: {classification.intent}

Relevant Data from Knowledge Base:
{context}

Instructions:
- Provide a helpful, accurate response as a knowledgeable CS advisor
- Include specific details and actionable guidance
- Be encouraging and supportive
- Use natural language without markdown formatting
- Focus on practical advice for this student's situation
- If recommending courses or actions, explain why
- Keep response length appropriate to the question complexity

Response:"""
        
        provider = os.environ.get("LLM_PROVIDER", "gemini").lower()
        if provider == "openai":
            try:
                import openai
                completion = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                text = completion.choices[0].message.content
                return {
                    "response": text,
                    "source": "llm_enhanced_openai",
                    "enhance_with_llm": False
                }
            except Exception as e:
                print(f"❌ OpenAI error: {e}")
                return {
                    "response": "I'm having trouble processing your query right now. Please try again or contact your academic advisor.",
                    "source": "error",
                    "enhance_with_llm": False
                }
        else:
            try:
                response = self.gemini_model.generate_content(prompt)
                return {
                    "response": response.text,
                    "source": "llm_enhanced_gemini",
                    "enhance_with_llm": False
                }
            except Exception as e:
                print(f"❌ Gemini error: {e}")
                return {
                    "response": "I'm having trouble processing your query right now. Please try again or contact your academic advisor.",
                    "source": "error",
                    "enhance_with_llm": False
                }
    
    def enhance_with_gemini(self, query: str, base_result: Dict, classification: QueryClassification) -> Dict[str, Any]:
        """Enhance rule-based or lookup results with Gemini for better context and personalization"""
        
        base_response = base_result.get("response", "")
        
        enhancement_prompt = f"""
        You are enhancing an academic advisor response for a Purdue CS student.
        
        Original Query: "{query}"
        Intent: {classification.intent}
        
        Current Response:
        {base_response}
        
        Please enhance this response by:
        1. Making it more conversational and personalized
        2. Adding helpful context or related information
        3. Suggesting follow-up actions or resources
        4. Maintaining accuracy of the original information
        
        Keep the response natural and avoid markdown formatting.
        """
        
        provider = os.environ.get("LLM_PROVIDER", "gemini").lower()
        if provider == "openai":
            try:
                import openai
                completion = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": enhancement_prompt}]
                )
                enhanced_response = completion.choices[0].message.content
                return {
                    "response": enhanced_response,
                    "source": f"{base_result.get('source', 'unknown')}_enhanced",
                    "enhance_with_llm": False
                }
            except Exception as e:
                print(f"❌ Enhancement error (OpenAI): {e}")
                return base_result
        else:
            try:
                response = self.gemini_model.generate_content(enhancement_prompt)
                enhanced_response = response.text
                return {
                    "response": enhanced_response,
                    "source": f"{base_result.get('source', 'unknown')}_enhanced",
                    "enhance_with_llm": False
                }
            except Exception as e:
                print(f"❌ Enhancement error (Gemini): {e}")
                return base_result

def main():
    """Test the hybrid AI system"""
    try:
        hybrid_system = HybridAISystem()
        
        test_queries = [
            "What is CS 18000?",  # Should use lookup table
            "What are the track requirements for MI?",  # Should use lookup table
            "What are the CODO requirements?",  # Should use lookup table
            "What are the prerequisites for CS 25000?",  # Should use rule-based
            "I failed CS 18000, what should I do?",  # Should use rule-based + LLM
            "What career paths are available with CS?",  # Should use LLM
            "How do I choose between MI and SE tracks?"  # Should use LLM
        ]
        
        print("🧪 Testing Hybrid AI System")
        print("=" * 60)
        
        for query in test_queries:
            print(f"\n🎓 Query: {query}")
            print("-" * 40)
            
            result = hybrid_system.process_query(query)
            
            print(f"💬 Response:\n{result['response']}")
            print(f"\n📊 Classification: {result['classification']}")
            print(f"🎯 Intent: {result['intent']}")
            print(f"✅ Confidence: {result['confidence']:.2f}")
            print("=" * 60)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure GEMINI_API_KEY is set in your environment")

if __name__ == "__main__":
    main()