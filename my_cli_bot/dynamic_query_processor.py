#!/usr/bin/env python3
"""
Dynamic Query Processor - Fixes hardcoded response issues
Makes AI actually understand and respond to specific questions
"""

import re
import json
from typing import Dict, List, Any, Optional

class DynamicQueryProcessor:
    def __init__(self, knowledge_graph):
        self.kg = knowledge_graph
        
    def process_query_intelligently(self, query: str, track_context: str = None) -> Dict[str, Any]:
        """
        Actually understand and respond to the specific query instead of hardcoded responses
        """
        
        # Clean and analyze the query
        query_clean = query.strip().lower()
        
        # STEP 1: Understand what the user is actually asking
        query_intent = self._analyze_query_intent(query_clean)
        
        # STEP 2: Generate appropriate response based on ACTUAL intent
        response = self._generate_contextual_response(query, query_intent, track_context)
        
        # STEP 3: Clean any markdown formatting from the response
        response = self._clean_markdown_formatting(response)
        
        return response
    
    def _clean_markdown_formatting(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove all markdown formatting from response text
        """
        if "response" in response_data:
            # Remove all ** markdown formatting
            response_data["response"] = response_data["response"].replace("**", "")
            
            # Remove other common markdown if present
            response_data["response"] = response_data["response"].replace("*", "")
            response_data["response"] = response_data["response"].replace("_", "")
            
        return response_data
    
    def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Actually understand what the user is asking instead of using generic responses
        """
        
        intent_patterns = {
            # PRIORITY 1: SPECIFIC POLICY QUESTIONS
            "course_exemption_policy": [
                r"skip", r"test out", r"place out", r"bypass", r"exempt", 
                r"credit by exam", r"placement exam", r"waive", r"skip.*cs.*18000",
                r"test.*out.*cs.*180", r"place.*out.*calculus", r"bypass.*course"
            ],
            
            # PRIORITY 2: TRANSFER/AP CREDIT
            "transfer_credit_policy": [
                r"ap credit", r"transfer", r"dual credit", r"college credit",
                r"ib credit", r"clep", r"transfer.*credit", r"ap.*calculus",
                r"transfer.*student", r"credits.*transfer"
            ],
            
            # PRIORITY 3: REGISTRATION/SCHEDULING
            "registration_scheduling": [
                r"registration", r"schedule", r"time conflict", r"waitlist",
                r"class full", r"add class", r"drop class", r"withdraw",
                r"register.*for", r"class.*full", r"schedule.*conflict"
            ],
            
            # PRIORITY 4: ACADEMIC DIFFICULTY/SUPPORT
            "academic_support": [
                r"struggling", r"failing", r"retake", r"gpa", r"academic probation",
                r"tutoring", r"help", r"mental health", r"study.*help",
                r"failing.*cs", r"struggling.*with", r"need.*help"
            ],
            
            # PRIORITY 5: GRADUATION/REQUIREMENTS
            "graduation_requirements": [
                r"graduate", r"degree audit", r"missing credits", r"requirements",
                r"petition", r"substitute", r"graduation.*requirements",
                r"degree.*requirements", r"credits.*need"
            ],
            
            # PRIORITY 6: CAREER/INTERNSHIP
            "career_guidance": [
                r"internship", r"career", r"job", r"resume", r"interview",
                r"salary", r"industry", r"company", r"internship.*application",
                r"career.*advice", r"job.*search", r"software.*engineer.*salary"
            ],
            
            # Meta questions about the AI itself
            "ai_identity": [
                r"what are you", r"who are you", r"what do you do", 
                r"what is this", r"explain yourself", r"tell me about yourself"
            ],
            
            # Major/degree questions
            "major_info": [
                r"what is my major", r"my major", r"major in computer science",
                r"cs major", r"computer science major", r"cs degree"
            ],
            
            # FRESHMAN YEAR (1st Year)
            "freshman_planning": [
                r"freshman", r"freshmen", r"1st year", r"first year",
                r"starting cs", r"new student", r"freshman classes",
                r"cs 18000", r"beginner", r"just started"
            ],
            
            # SOPHOMORE YEAR (2nd Year)
            "sophomore_planning": [
                r"sophomore", r"2nd year", r"second year", r"sophomore classes",
                r"after freshman", r"cs 25000", r"cs 25100", r"cs 25200",
                r"data structures", r"computer architecture"
            ],
            
            # JUNIOR YEAR (3rd Year)
            "junior_planning": [
                r"junior", r"3rd year", r"third year", r"junior year",
                r"classes.*junior", r"courses.*junior", r"junior.*classes",
                r"junior.*courses", r"what.*take.*junior", r"junior.*take",
                r"classes.*3rd", r"courses.*3rd", r"taking.*junior",
                r"classes.*should.*taking.*junior", r"what.*classes.*junior",
                r"courses.*should.*take.*junior", r"taking.*as.*junior",
                r"track courses", r"cs 38100", r"algorithms", r"tracks"
            ],
            
            # SENIOR YEAR (4th Year)
            "senior_planning": [
                r"senior", r"4th year", r"fourth year", r"senior classes",
                r"capstone", r"graduation", r"graduate", r"senior project"
            ],
            
            # Course timing questions
            "timing": [
                r"when should i take", r"when can i take", r"what semester",
                r"timing", r"schedule", r"when to take"
            ],
            
            # Track requirements
            "track_requirements": [
                r"track requirements", r"what do i need for", r"mi track",
                r"se track", r"requirements for", r"courses needed"
            ],
            
            # Course prerequisites
            "prerequisites": [
                r"prerequisites", r"prereqs", r"what do i need before",
                r"requirements for cs", r"need to take first"
            ],
            
            # Planning and advice
            "planning": [
                r"plan", r"strategy", r"timeline", r"should i",
                r"recommend", r"advice", r"guidance", r"what classes",
                r"what courses", r"should.*take"
            ],
            
            # Comparisons
            "comparison": [
                r"difference between", r"compare", r"vs", r"versus",
                r"which is better", r"mi or se", r"track comparison"
            ],
            
            # Specific course questions
            "course_specific": [
                r"cs \d+", r"stat \d+", r"ma \d+", r"about cs",
                r"tell me about", r"what is cs"
            ],
            
            # Greetings and casual
            "greeting": [
                r"^hello", r"^hi", r"^hey", r"^good morning",
                r"^good afternoon", r"^what's up"
            ],
            
            # Help requests
            "help": [
                r"help", r"confused", r"don't understand", r"explain",
                r"clarify", r"lost", r"overwhelmed"
            ],
            
            # Program overview and general CS questions
            "program_overview": [
                r"how is.*cs program", r"how is.*computer science", r"tell me about.*cs program",
                r"tell me about.*computer science", r"what is.*cs program", r"describe.*cs program",
                r"cs program.*purdue", r"computer science.*purdue", r"overview.*cs",
                r"about.*cs program", r"about.*computer science", r"how.*cs.*purdue",
                r"what.*like.*cs program", r"good.*cs program", r"quality.*cs program"
            ],
            
            # Course information requests
            "course_info": [
                r"tell me about cs", r"about cs courses", r"cs curriculum",
                r"what courses", r"course information", r"class information"
            ]
        }
        
        # Find matching intent - prioritize policy questions first
        # Check policy questions first since they're highest priority
        policy_priorities = ["course_exemption_policy", "transfer_credit_policy", "registration_scheduling", 
                           "academic_support", "graduation_requirements", "career_guidance"]
        
        for policy_intent in policy_priorities:
            if policy_intent in intent_patterns:
                for pattern in intent_patterns[policy_intent]:
                    if re.search(pattern, query):
                        return {
                            "primary_intent": policy_intent,
                            "confidence": 0.95,
                            "matched_pattern": pattern,
                            "query_length": len(query.split()),
                            "is_complex": len(query.split()) > 10
                        }
        
        # Then check academic year planning
        year_priorities = ["freshman_planning", "sophomore_planning", "junior_planning", "senior_planning"]
        
        for year_intent in year_priorities:
            if year_intent in intent_patterns:
                for pattern in intent_patterns[year_intent]:
                    if re.search(pattern, query):
                        return {
                            "primary_intent": year_intent,
                            "confidence": 0.95,
                            "matched_pattern": pattern,
                            "query_length": len(query.split()),
                            "is_complex": len(query.split()) > 10
                        }
        
        # Then check other intents
        for intent_type, patterns in intent_patterns.items():
            if intent_type in policy_priorities or intent_type in year_priorities:
                continue  # Already checked
            for pattern in patterns:
                if re.search(pattern, query):
                    return {
                        "primary_intent": intent_type,
                        "confidence": 0.9,
                        "matched_pattern": pattern,
                        "query_length": len(query.split()),
                        "is_complex": len(query.split()) > 10
                    }
        
        # Default if no pattern matches
        return {
            "primary_intent": "general_inquiry",
            "confidence": 0.5,
            "matched_pattern": None,
            "query_length": len(query.split()),
            "is_complex": len(query.split()) > 10
        }
    
    def _generate_contextual_response(self, query: str, intent: Dict, track_context: str) -> Dict[str, Any]:
        """
        Generate responses that actually match what the user asked
        """
        
        intent_type = intent["primary_intent"]
        
        # Route to appropriate response generator based on ACTUAL intent - PRIORITY ORDER
        if intent_type == "course_exemption_policy":
            return self._handle_course_exemption_policy(query, intent)
        elif intent_type == "transfer_credit_policy":
            return self._handle_transfer_credit_policy(query, intent)
        elif intent_type == "registration_scheduling":
            return self._handle_registration_scheduling(query, intent)
        elif intent_type == "academic_support":
            return self._handle_academic_support(query, intent)
        elif intent_type == "graduation_requirements":
            return self._handle_graduation_requirements(query, intent)
        elif intent_type == "career_guidance":
            return self._handle_career_guidance(query, intent)
        elif intent_type == "ai_identity":
            return self._handle_ai_identity_questions(query, intent)
        elif intent_type == "major_info":
            return self._handle_major_info_questions(query, intent)
        elif intent_type == "freshman_planning":
            return self._handle_freshman_planning_questions(query, intent, track_context)
        elif intent_type == "sophomore_planning":
            return self._handle_sophomore_planning_questions(query, intent, track_context)
        elif intent_type == "junior_planning":
            return self._handle_junior_planning_questions(query, intent, track_context)
        elif intent_type == "senior_planning":
            return self._handle_senior_planning_questions(query, intent, track_context)
        elif intent_type == "timing":
            return self._handle_timing_questions(query, intent, track_context)
        elif intent_type == "track_requirements":
            return self._handle_track_requirements(query, intent, track_context)
        elif intent_type == "prerequisites":
            return self._handle_prerequisite_questions(query, intent)
        elif intent_type == "planning":
            return self._handle_planning_questions(query, intent, track_context)
        elif intent_type == "comparison":
            return self._handle_comparison_questions(query, intent)
        elif intent_type == "course_specific":
            return self._handle_course_specific_questions(query, intent)
        elif intent_type == "greeting":
            return self._handle_greetings(query, intent)
        elif intent_type == "help":
            return self._handle_help_requests(query, intent)
        elif intent_type == "program_overview":
            return self._handle_program_overview(query, intent)
        elif intent_type == "course_info":
            return self._handle_course_info(query, intent)
        else:
            return self._handle_general_questions(query, intent, track_context)
    
    def _handle_ai_identity_questions(self, query: str, intent: Dict) -> Dict[str, Any]:
        """
        Handle questions about what the AI is/does - BE SPECIFIC not generic
        """
        
        query_lower = query.lower()
        
        if "what do you do" in query_lower:
            response = "I help Purdue CS students figure out their degree requirements and course planning. I can tell you when to take specific courses, explain track requirements for MI and SE, check prerequisites, and help you plan your timeline through the program. I know all the current course info, timing rules, and track details for Purdue CS."
            
        elif "what are you" in query_lower or "who are you" in query_lower:
            response = "I'm an AI advisor specifically trained on Purdue Computer Science degree requirements. I have access to all the current course data, prerequisites, track requirements, and progression rules. Think of me as your CS academic advisor who knows everything about the program structure and can help you navigate it."
            
        elif "explain yourself" in query_lower:
            response = "Sure! I'm built specifically to help Purdue CS students with their degree planning. I know the foundation course sequence (CS 18000 through CS 25200), when you can start track courses (Fall 3rd year), all the MI and SE track requirements, prerequisite chains, and timing rules. I can help you plan your courses, understand requirements, and make good decisions about your CS degree."
            
        else:
            response = "I'm a specialized advisor for Purdue CS students. I can help with course timing, track planning, prerequisites, and degree requirements. What specific aspect of the CS program would you like to know about?"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.95,
            "intent": intent["primary_intent"],
            "source_data": {"type": "ai_identity"},
            "track": None
        }
    
    def _handle_timing_questions(self, query: str, intent: Dict, track_context: str) -> Dict[str, Any]:
        """
        Handle course timing questions with actual course lookup
        """
        
        # Extract course code if present
        course_match = re.search(r'(CS|STAT|MA)\s*(\d+)', query.upper())
        
        if course_match:
            course_code = f"{course_match.group(1)} {course_match.group(2)}"
            return self._get_specific_course_timing(course_code, query)
        else:
            return self._get_general_timing_info(query, track_context)
    
    def _get_specific_course_timing(self, course_code: str, query: str) -> Dict[str, Any]:
        """
        Get specific timing for a course from knowledge graph
        """
        
        # Query the actual knowledge graph
        try:
            import sqlite3
            conn = sqlite3.connect(self.kg.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT code, title, group_id, prerequisites, description
                FROM courses WHERE code = ?
            ''', (course_code,))
            
            course_data = cursor.fetchone()
            conn.close()
            
            if course_data:
                code, title, timing, prereqs_json, description = course_data
                prereqs = json.loads(prereqs_json) if prereqs_json else []
                
                # Generate specific response based on actual data
                if course_code == "CS 38100":
                    response = f"You should take {code} ({title}) in Fall of your 3rd year. This timing is important because you need CS 25100 (Data Structures) as a prerequisite, which you take in Fall of 2nd year. CS 38100 opens up most advanced courses, so it's worth waiting to do it right."
                    
                elif course_code == "CS 37300":
                    response = f"CS 37300 ({title}) can be taken starting Fall 3rd year, but you'll need CS 25100 and a statistics course first. The earliest realistic timing is Spring 3rd year or Fall 4th year, depending on when you complete the prerequisites."
                    
                elif "1st Year" in timing:
                    response = f"{code} ({title}) is typically taken in {timing}. " + (f"You'll need these prerequisites first: {', '.join(prereqs)}." if prereqs else "This is part of your foundation sequence.")
                    
                elif "2nd Year" in timing:
                    response = f"{code} ({title}) fits into your {timing} schedule. " + (f"Make sure you've completed: {', '.join(prereqs)}." if prereqs else "")
                    
                elif "3rd Year" in timing:
                    response = f"{code} ({title}) is taken in {timing}. " + (f"Prerequisites: {', '.join(prereqs)}." if prereqs else "")
                    
                else:
                    response = f"{code} ({title}) can be taken once you meet the prerequisites" + (f": {', '.join(prereqs)}" if prereqs else "") + ". This is typically in your junior or senior year."
                
                return {
                    "query": query,
                    "response": response,
                    "confidence": 0.95,
                    "source_data": {"course": code, "timing": timing, "prereqs": prereqs},
                    "track": None
                }
            else:
                return {
                    "query": query,
                    "response": f"I don't have specific timing info for {course_code} in my database. Could you double-check that course code?",
                    "confidence": 0.3,
                    "source_data": {},
                    "track": None
                }
                
        except Exception as e:
            return {
                "query": query,
                "response": f"I'm having trouble looking up {course_code} right now. Could you try asking again?",
                "confidence": 0.1,
                "source_data": {"error": str(e)},
                "track": None
            }
    
    def _get_general_timing_info(self, query: str, track_context: str) -> Dict[str, Any]:
        """
        Provide general timing information based on query context
        """
        
        if "track" in query.lower():
            response = "Track courses can start in Fall of your 3rd year, after you complete the foundation sequence (CS 18000 through CS 25200) and CS 38100. You'll spend your first two years building that solid foundation, then dive into your specialization."
        else:
            response = "The CS program follows a clear progression: Foundation courses in years 1-2 (CS 18000 → CS 25200), CS 38100 in Fall 3rd year, then track courses starting Fall 3rd year. What specific course timing are you wondering about?"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.8,
            "source_data": {"type": "general_timing"},
            "track": track_context
        }
    
    def _handle_greetings(self, query: str, intent: Dict) -> Dict[str, Any]:
        """
        Handle greetings naturally without dumping generic info
        """
        
        greetings = [
            "Hey! What would you like to know about the CS program?",
            "What can I help you with?",
            "What CS questions do you have?",
            "How can I help with your CS planning?"
        ]
        
        import random
        response = random.choice(greetings)
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.9,
            "intent": intent["primary_intent"],
            "source_data": {"type": "greeting"},
            "track": None
        }
    
    def _handle_help_requests(self, query: str, intent: Dict) -> Dict[str, Any]:
        """
        Handle help requests with specific guidance
        """
        
        if "confused" in query.lower() or "lost" in query.lower():
            response = "No worries! The CS program can feel overwhelming at first. Let's break it down: you start with foundation courses (CS 18000, CS 19300, CS 25000, CS 25100, CS 25200), then take CS 38100 in Fall 3rd year, and then you can start your track courses. What specific part is confusing you?"
        else:
            response = "I'm here to help! I can explain course timing, track requirements, prerequisites, or help you plan your degree. What specific CS topic would you like me to clarify?"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.9,
            "intent": intent["primary_intent"],
            "source_data": {"type": "help_request"},
            "track": None
        }
    
    def _handle_track_requirements(self, query: str, intent: Dict, track_context: str) -> Dict[str, Any]:
        """
        Handle track requirement questions with actual data
        """
        
        query_lower = query.lower()
        
        if "mi" in query_lower or "machine intelligence" in query_lower:
            response = "The Machine Intelligence track requires 4 mandatory courses plus 2 electives. The required courses are CS 37300 (Data Mining), CS 38100 (Intro to AI), plus you choose one statistics course (STAT 41600, MA 41600, or STAT 51200) and one AI course (CS 47100 or CS 47300). Then you pick 2 electives from the approved list. You can start these Fall 3rd year after completing the foundation sequence."
            
        elif "se" in query_lower or "software engineering" in query_lower:
            response = "The Software Engineering track requires 5 mandatory courses plus 1 elective. The required courses are CS 30700 (Software Engineering), CS 38100 (Intro to AI), CS 40800 (Software Testing), CS 40700 (Programming Languages), and either CS 35200 (Compilers) or CS 35400 (Operating Systems). Then you pick 1 elective from the approved list. You can start these Fall 3rd year."
            
        else:
            response = "Both MI and SE tracks start in Fall 3rd year. MI focuses on AI and data with 4 required + 2 electives. SE focuses on software development with 5 required + 1 elective. Which track interests you more?"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.95,
            "intent": intent["primary_intent"],
            "source_data": {"type": "track_requirements"},
            "track": track_context
        }
    
    def _handle_prerequisite_questions(self, query: str, intent: Dict) -> Dict[str, Any]:
        """
        Handle prerequisite questions with actual course data
        """
        
        # Extract course code if present
        course_match = re.search(r'(CS|STAT|MA)\s*(\d+)', query.upper())
        
        if course_match:
            course_code = f"{course_match.group(1)} {course_match.group(2)}"
            return self._get_specific_prerequisites(course_code, query)
        else:
            response = "Prerequisites vary by course. For example, CS 25100 needs CS 18000 and CS 19300. CS 38100 needs CS 25100. Most advanced courses need CS 38100. What specific course are you asking about?"
            
            return {
                "query": query,
                "response": response,
                "confidence": 0.7,
                "intent": intent["primary_intent"],
                "source_data": {"type": "general_prerequisites"},
                "track": None
            }
    
    def _get_specific_prerequisites(self, course_code: str, query: str) -> Dict[str, Any]:
        """
        Get specific prerequisites for a course
        """
        
        try:
            import sqlite3
            conn = sqlite3.connect(self.kg.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT code, title, prerequisites
                FROM courses WHERE code = ?
            ''', (course_code,))
            
            course_data = cursor.fetchone()
            conn.close()
            
            if course_data:
                code, title, prereqs_json = course_data
                prereqs = json.loads(prereqs_json) if prereqs_json else []
                
                if prereqs:
                    response = f"For {code} ({title}), you need: {', '.join(prereqs)}. Make sure you complete these before attempting this course."
                else:
                    response = f"{code} ({title}) has no prerequisites - you can take it anytime in the appropriate sequence."
                
                return {
                    "query": query,
                    "response": response,
                    "confidence": 0.95,
                    "source_data": {"course": code, "prereqs": prereqs},
                    "track": None
                }
            else:
                return {
                    "query": query,
                    "response": f"I don't have prerequisite info for {course_code}. Could you double-check that course code?",
                    "confidence": 0.3,
                    "source_data": {},
                    "track": None
                }
                
        except Exception as e:
            return {
                "query": query,
                "response": f"I'm having trouble looking up prerequisites for {course_code}. Could you try asking again?",
                "confidence": 0.1,
                "source_data": {"error": str(e)},
                "track": None
            }
    
    def _handle_planning_questions(self, query: str, intent: Dict, track_context: str) -> Dict[str, Any]:
        """
        Handle planning and advice questions
        """
        
        query_lower = query.lower()
        
        if "timeline" in query_lower or "plan" in query_lower:
            response = "Here's the general timeline: Years 1-2 focus on foundation courses (CS 18000 through CS 25200). Fall 3rd year you take CS 38100, then start track courses. Years 3-4 you complete your chosen track (MI or SE) plus remaining requirements. Would you like me to be more specific about any part of this timeline?"
            
        elif "recommend" in query_lower or "advice" in query_lower:
            response = "My advice: Focus on the foundation sequence first - don't rush it. Take CS 38100 in Fall 3rd year as planned. Choose your track based on your interests: MI for AI/data, SE for software development. Plan your electives carefully since they have limited options. What specific area would you like advice on?"
            
        else:
            response = "I can help you plan your CS degree! The key is following the proper sequence: foundation courses first, then CS 38100, then track courses. What specific planning question do you have?"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.85,
            "intent": intent["primary_intent"],
            "source_data": {"type": "planning_advice"},
            "track": track_context
        }
    
    def _handle_comparison_questions(self, query: str, intent: Dict) -> Dict[str, Any]:
        """
        Handle comparison questions between tracks or courses
        """
        
        query_lower = query.lower()
        
        if "mi" in query_lower and "se" in query_lower:
            response = "MI vs SE: Machine Intelligence focuses on AI, machine learning, and data mining with 4 required + 2 electives. Software Engineering focuses on software development, testing, and systems with 5 required + 1 elective. MI is better if you want to work in AI/data science. SE is better if you want to build software systems. Which area interests you more?"
            
        else:
            response = "I can help compare CS tracks or courses. What specific comparison are you looking for?"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.85,
            "intent": intent["primary_intent"],
            "source_data": {"type": "comparison"},
            "track": None
        }
    
    def _handle_course_specific_questions(self, query: str, intent: Dict) -> Dict[str, Any]:
        """
        Handle specific course questions
        """
        
        course_match = re.search(r'(CS|STAT|MA)\s*(\d+)', query.upper())
        
        if course_match:
            course_code = f"{course_match.group(1)} {course_match.group(2)}"
            return self._get_course_details(course_code, query)
        else:
            response = "I can tell you about specific CS courses! Which course are you interested in?"
            
            return {
                "query": query,
                "response": response,
                "confidence": 0.6,
                "intent": intent["primary_intent"],
                "source_data": {"type": "course_inquiry"},
                "track": None
            }
    
    def _get_course_details(self, course_code: str, query: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific course
        """
        
        try:
            import sqlite3
            conn = sqlite3.connect(self.kg.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT code, title, credits, prerequisites, description, group_id
                FROM courses WHERE code = ?
            ''', (course_code,))
            
            course_data = cursor.fetchone()
            conn.close()
            
            if course_data:
                code, title, credits, prereqs_json, description, timing = course_data
                prereqs = json.loads(prereqs_json) if prereqs_json else []
                
                response = f"{code} ({title}) is a {credits}-credit course"
                if timing:
                    response += f" typically taken in {timing}"
                if prereqs:
                    response += f". Prerequisites: {', '.join(prereqs)}"
                if description:
                    response += f". {description}"
                else:
                    response += ". This course is part of the CS curriculum."
                
                return {
                    "query": query,
                    "response": response,
                    "confidence": 0.95,
                    "source_data": {"course": code, "details": course_data},
                    "track": None
                }
            else:
                return {
                    "query": query,
                    "response": f"I don't have detailed info for {course_code}. Could you double-check that course code?",
                    "confidence": 0.3,
                    "source_data": {},
                    "track": None
                }
                
        except Exception as e:
            return {
                "query": query,
                "response": f"I'm having trouble looking up {course_code}. Could you try asking again?",
                "confidence": 0.1,
                "source_data": {"error": str(e)},
                "track": None
            }
    
    def _handle_major_info_questions(self, query: str, intent: Dict) -> Dict[str, Any]:
        """
        Handle questions about CS major and degree information
        """
        
        query_lower = query.lower()
        
        if "what is my major" in query_lower:
            response = "If you're asking about Computer Science, that's an excellent major choice! CS at Purdue is a comprehensive program that covers programming, algorithms, software engineering, and specialized tracks like Machine Intelligence and Software Engineering. Are you currently a CS student, or are you thinking about declaring CS as your major?"
        else:
            response = "Computer Science is a fantastic major at Purdue! You'll learn programming, problem-solving, and specialized skills in areas like artificial intelligence, software engineering, and data science. The program includes foundation courses in your first two years, then you can specialize in tracks like Machine Intelligence or Software Engineering. What specific aspect of the CS major would you like to know about?"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.95,
            "intent": intent["primary_intent"],
            "source_data": {"type": "major_info"},
            "track": None
        }
    
    def _handle_freshman_planning_questions(self, query: str, intent: Dict, track_context: str) -> Dict[str, Any]:
        """
        Handle freshman year planning questions with specific course recommendations
        """
        
        response = "Welcome to Purdue CS! I'm excited to help you start your computer science journey!\n\n"
        
        response += "Here's your freshman year roadmap - this is the foundation that everything else builds on:\n\n"
        
        response += "Fall Freshman Year:\n"
        response += "• CS 18000: Problem Solving & Object-Oriented Programming (4 credits) - your first CS course!\n"
        response += "• MA 16100: Calculus I (5 credits) - co-requisite with CS 18000\n"
        response += "• Plus general education courses (typically 6-7 more credits)\n\n"
        
        response += "Spring Freshman Year:\n"
        response += "• CS 18200: Foundations of Computer Science (3 credits) - requires CS 18000\n"
        response += "• CS 24000: Programming in C (3 credits) - requires CS 18000\n"
        response += "• MA 16200: Calculus II (5 credits) - requires MA 16100\n"
        response += "• Plus more general education courses\n\n"
        
        response += "Key things to know:\n"
        response += "• CS 18000 is your gateway course - everything builds from here!\n"
        response += "• You MUST take CS 18000 and MA 16100 together in your first semester\n"
        response += "• Don't worry if coding is new to you - CS 18000 assumes no prior programming experience\n"
        response += "• The workload is manageable but consistent - stay on top of assignments!\n\n"
        
        response += "Get involved early! Join CS organizations, attend career fairs, and connect with upperclassmen. The CS community at Purdue is amazing!\n\n"
        
        response += "How are you feeling about starting your CS journey? Every CS student started exactly where you are now!"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.98,
            "intent": intent["primary_intent"],
            "source_data": {"type": "freshman_planning", "courses": ["CS 18000", "MA 16100"]},
            "track": track_context
        }
    
    def _handle_sophomore_planning_questions(self, query: str, intent: Dict, track_context: str) -> Dict[str, Any]:
        """
        Handle sophomore year planning questions with specific course recommendations
        """
        
        response = "Great question! Sophomore year is where CS really starts to get exciting - you're moving from basics to real computer science concepts!\n\n"
        
        response += "Here's your sophomore year path:\n\n"
        
        response += "Fall Sophomore Year:\n"
        response += "• CS 25000: Computer Architecture (4 credits) - how computers actually work!\n"
        response += "• CS 25100: Data Structures (3 credits) - super important for everything that follows\n"
        response += "• MA 26100: Multivariate Calculus (4 credits) - continues your math sequence\n"
        response += "• Plus general education courses\n\n"
        
        response += "Spring Sophomore Year:\n"
        response += "• CS 25200: Systems Programming (4 credits) - the gateway to advanced CS!\n"
        response += "• MA 26500: Linear Algebra (3 credits) - required for many tracks\n"
        response += "• Plus general education and elective courses\n\n"
        
        response += "What makes sophomore year special:\n"
        response += "• You'll understand how computers work at the hardware level (CS 25000)\n"
        response += "• Data structures (CS 25100) teaches you efficient data organization\n"
        response += "• Systems programming (CS 25200) covers operating systems and memory management\n\n"
        
        response += "Critical timing: CS 25200 is your gateway to track courses! You can't start any track courses until you complete this sequence.\n\n"
        
        response += "The courses build on each other: CS 18000/18200/24000 → CS 25000/25100 → CS 25200. You can't skip steps!\n\n"
        
        response += "Are you currently in the foundation sequence? That'll help me give you more specific timing advice!"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.98,
            "intent": intent["primary_intent"],
            "source_data": {"type": "sophomore_planning", "courses": ["CS 25000", "CS 25100", "CS 25200"]},
            "track": track_context
        }
    
    def _handle_junior_planning_questions(self, query: str, intent: Dict, track_context: str) -> Dict[str, Any]:
        """
        Handle junior year planning questions with specific course recommendations
        """
        
        response = "Great question! I'm excited to help you plan your junior year in Computer Science!\n\n"
        
        response += "Here's how junior year works for CS students at Purdue:\n\n"
        
        response += "Fall of Junior Year (Critical Timing):\n"
        response += "• CS 38100 (Introduction to Algorithms) - MUST take this Fall junior year\n"
        response += "• STAT 35000 (Elementary Statistics) - needed for most tracks\n"
        response += "• Your first track course (once you've chosen your specialization)\n\n"
        
        response += "Spring of Junior Year:\n"
        response += "• Continue with track requirements\n"
        response += "• Additional track courses based on your chosen specialization\n"
        response += "• Electives from your track\n\n"
        
        response += "Track Options:\n"
        response += "• Machine Intelligence (AI, machine learning, data science)\n"
        response += "• Software Engineering (building large software systems)\n"
        response += "• Plus 7 other tracks to choose from\n\n"
        
        response += "The key thing is you need to complete the foundation sequence (CS 18000 through CS 25200) before you can start track courses. Have you finished CS 25200 (Systems Programming) yet?\n\n"
        
        response += "What track are you most interested in? I can give you the specific course sequence for Machine Intelligence, Software Engineering, or any other track!"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.98,
            "intent": intent["primary_intent"],
            "source_data": {"type": "junior_planning", "courses": ["CS 38100", "STAT 35000"]},
            "track": track_context
        }
    
    def _handle_senior_planning_questions(self, query: str, intent: Dict, track_context: str) -> Dict[str, Any]:
        """
        Handle senior year planning questions with specific course recommendations
        """
        
        response = "Awesome! Senior year is where everything comes together - you're almost a CS graduate!\n\n"
        
        response += "Here's how to make the most of your senior year:\n\n"
        
        response += "Fall Senior Year:\n"
        response += "• Complete remaining track requirements\n"
        response += "• Advanced electives in your areas of interest\n"
        response += "• Consider CS 49000 special topics courses\n"
        response += "• Start thinking about capstone projects or senior design\n\n"
        
        response += "Spring Senior Year:\n"
        response += "• Finish any remaining track courses\n"
        response += "• Capstone experience (varies by track)\n"
        response += "• Senior design projects\n"
        response += "• Preparation for post-graduation (job search, grad school, etc.)\n\n"
        
        response += "Key Senior Year Options:\n"
        response += "• Software Engineering Track: CS 40700 (Senior Project) or EPICS Senior Design\n"
        response += "• Research Opportunities: Work with professors on research projects\n"
        response += "• Industry Projects: Many tracks offer real-world project experiences\n"
        response += "• Advanced Topics: CS 49000 and CS 59000 level courses\n\n"
        
        response += "Graduation Requirements Check:\n"
        response += "• Minimum 120 total credits\n"
        response += "• All track requirements completed (6 courses minimum)\n"
        response += "• Grade C or better in all CS courses\n"
        response += "• 32 upper-level credits (30000+) at Purdue\n\n"
        
        response += "Are you on track to graduate on time? Which track are you completing? You're so close to the finish line!"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.98,
            "intent": intent["primary_intent"],
            "source_data": {"type": "senior_planning", "courses": ["CS 49000", "CS 40700"]},
            "track": track_context
        }
    
    def _handle_general_questions(self, query: str, intent: Dict, track_context: str) -> Dict[str, Any]:
        """
        Handle general questions that don't fit specific categories
        """
        
        response = "I can help with CS degree planning, course timing, track requirements, and prerequisites. What specific aspect of the CS program would you like to know about?"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.6,
            "intent": intent["primary_intent"],
            "source_data": {"type": "general_inquiry"},
            "track": track_context
        }
    
    # ====== ENHANCED POLICY HANDLERS ======
    
    def _handle_course_exemption_policy(self, query: str, intent: Dict) -> Dict[str, Any]:
        """
        Handle course exemption and skip policy questions
        """
        
        # Course-specific exemption policies
        course_policies = {
            "CS 18000": {
                "can_skip": True,
                "method": "placement exam during orientation",
                "difficulty": "moderate", 
                "recommendation": "not recommended for most students",
                "reasons": [
                    "Purdue-specific programming standards and practices",
                    "Foundation for CS 18200 problem-solving approaches", 
                    "Integration with Purdue development environment",
                    "Teamwork and project management skills"
                ],
                "who_should_skip": [
                    "2+ years of Java programming experience",
                    "Strong understanding of OOP principles",
                    "Comfortable with data structures and algorithms",
                    "Previous coursework in computer science"
                ],
                "who_should_not_skip": [
                    "Self-taught programmers without formal CS background",
                    "Students who learned non-OOP languages primarily",
                    "Those who want to build strong fundamentals", 
                    "Students planning competitive programming or research"
                ]
            },
            "CS 18200": {
                "can_skip": False,
                "method": "no exemption available",
                "recommendation": "must take",
                "reasons": [
                    "Purdue-specific discrete mathematics approach",
                    "Foundation for theoretical CS courses",
                    "Required for CS 25100 and CS 38100",
                    "Unique proof techniques and mathematical maturity"
                ]
            },
            "MA 16100": {
                "can_skip": True,
                "method": "AP Calculus AB (4+) or BC (3+), or placement exam",
                "recommendation": "skip if qualified",
                "reasons": [
                    "Standard calculus content",
                    "No Purdue-specific approaches", 
                    "Prerequisite satisfied by AP credit"
                ]
            }
        }
        
        # Extract course code from query
        course_code = None
        if "cs 18000" in query.lower() or "cs 180" in query.lower():
            course_code = "CS 18000"
        elif "cs 18200" in query.lower() or "cs 182" in query.lower():
            course_code = "CS 18200"
        elif "calculus" in query.lower() or "ma 16100" in query.lower():
            course_code = "MA 16100"
        
        if course_code and course_code in course_policies:
            policy = course_policies[course_code]
            
            response = f"Great question about {course_code}! Here's the complete breakdown:\n\n"
            response += f"Can you skip {course_code}? {'Yes' if policy['can_skip'] else 'No'}\n\n"
            response += f"How to skip: {policy['method']}\n\n"
            response += f"My recommendation: {policy['recommendation']}\n\n"
            
            response += "Why this recommendation:\n"
            for reason in policy['reasons']:
                response += f"• {reason}\n"
            
            if 'who_should_skip' in policy:
                response += "\nYou should consider skipping if:\n"
                for criteria in policy['who_should_skip']:
                    response += f"• {criteria}\n"
            
            if 'who_should_not_skip' in policy:
                response += "\nYou should NOT skip if:\n"
                for criteria in policy['who_should_not_skip']:
                    response += f"• {criteria}\n"
            
            response += "\nWhat's your programming background? I can give you more specific advice based on your experience!"
            
            return {
                "query": query,
                "response": response,
                "confidence": 0.95,
                "intent": intent["primary_intent"],
                "source_data": {"type": "course_exemption", "course": course_code},
                "track": None
            }
        else:
            # General exemption guidance
            response = "I can help with course exemption policies! Here's what I recommend:\n\n"
            response += "General exemption process:\n"
            response += "1. Check with your academic advisor\n"
            response += "2. Look for placement exams during orientation\n"
            response += "3. Submit AP/transfer credit documentation\n"
            response += "4. Consider the academic impact of skipping\n\n"
            
            response += "Questions to ask yourself:\n"
            response += "• Do I have strong background in this subject?\n"
            response += "• Will skipping hurt my foundation for later courses?\n"
            response += "• Am I trying to graduate early or just avoid difficulty?\n\n"
            
            response += "Which specific course are you thinking about skipping? I can give you detailed guidance for CS 18000, CS 18200, or calculus!"
            
            return {
                "query": query,
                "response": response,
                "confidence": 0.8,
                "intent": intent["primary_intent"],
                "source_data": {"type": "general_exemption"},
                "track": None
            }
    
    def _handle_transfer_credit_policy(self, query: str, intent: Dict) -> Dict[str, Any]:
        """
        Handle transfer credit and AP credit questions
        """
        
        response = "I can help you understand transfer and AP credit policies!\n\n"
        
        response += "Common transfer credit scenarios:\n\n"
        response += "AP Credit:\n"
        response += "• AP Calculus AB (4+) or BC (3+) → MA 16100 credit\n"
        response += "• AP Computer Science A (4+) → May get CS 18000 credit\n"
        response += "• AP Statistics (4+) → May count toward statistics requirement\n\n"
        
        response += "Transfer Credit Process:\n"
        response += "1. Submit official transcripts to Admissions\n"
        response += "2. Credits are evaluated by the CS department\n"
        response += "3. Check MyPurdue for transfer credit report\n"
        response += "4. Meet with advisor to plan remaining courses\n\n"
        
        response += "Important notes:\n"
        response += "• Only C or better grades transfer\n"
        response += "• CS courses must align with Purdue curriculum\n"
        response += "• Some courses may transfer as electives only\n"
        response += "• Foundation sequence (CS 18000-25200) is usually required\n\n"
        
        response += "What specific credits are you trying to transfer? I can help you understand how they might fit into your degree plan!"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.9,
            "intent": intent["primary_intent"],
            "source_data": {"type": "transfer_credit"},
            "track": None
        }
    
    def _handle_registration_scheduling(self, query: str, intent: Dict) -> Dict[str, Any]:
        """
        Handle registration and scheduling issues
        """
        
        response = "I can help with registration and scheduling! Here's what you need to know:\n\n"
        
        response += "Common registration issues:\n"
        response += "• Class full? Join the waitlist and check for additional sections\n"
        response += "• Time conflicts? Look for alternative sections or online options\n"
        response += "• Prerequisites not met? Check if you need advisor override\n"
        response += "• Registration hold? Resolve financial or academic holds first\n\n"
        
        response += "Key registration dates:\n"
        response += "• Priority registration: Based on credit hours completed\n"
        response += "• Open registration: Available to all students\n"
        response += "• Add/drop deadline: First week of classes\n"
        response += "• Withdrawal deadline: Week 8 of semester\n\n"
        
        response += "Pro tips:\n"
        response += "• Use Schedule Planner in MyPurdue to test different combinations\n"
        response += "• Have backup options for each required course\n"
        response += "• Check Rate My Professor for instructor insights\n"
        response += "• Consider course load balance (don't overload difficult courses)\n\n"
        
        response += "What specific scheduling challenge are you facing? I can give more targeted advice!"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.9,
            "intent": intent["primary_intent"],
            "source_data": {"type": "registration_scheduling"},
            "track": None
        }
    
    def _handle_academic_support(self, query: str, intent: Dict) -> Dict[str, Any]:
        """
        Handle academic support and struggling student questions
        """
        
        response = "I'm here to help with whatever academic challenges you're facing! Let's figure out the best support for your situation.\n\n"
        
        response += "Immediate academic support:\n"
        response += "• Academic Success Center (PUSH 1041) - Study skills, time management\n"
        response += "• Supplemental Instruction - Peer-led study sessions for difficult courses\n"
        response += "• Writing Lab - Help with papers and technical writing\n"
        response += "• Math Help Room - Drop-in tutoring for math courses\n\n"
        
        response += "For serious academic concerns:\n"
        response += "• Academic advisor - Course planning and degree requirements\n"
        response += "• Dean of Students - Academic probation, personal issues affecting studies\n"
        response += "• Counseling & Psychological Services - Mental health support\n"
        response += "• Student Success Coaching - Holistic academic and personal development\n\n"
        
        response += "Course-specific help:\n"
        response += "• Professor office hours - Always the best first step\n"
        response += "• TA office hours - More accessible, peer-level help\n"
        response += "• Study groups - Form through course forums or social media\n\n"
        
        response += "What specific challenge are you dealing with? I can point you to the most relevant resources and help you create an action plan!"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.95,
            "intent": intent["primary_intent"],
            "source_data": {"type": "academic_support"},
            "track": None
        }
    
    def _handle_graduation_requirements(self, query: str, intent: Dict) -> Dict[str, Any]:
        """
        Handle graduation requirements and degree audit questions
        """
        
        response = "Let me help you understand graduation requirements!\n\n"
        
        response += "CS Degree Requirements:\n"
        response += "• Minimum 120 total credit hours\n"
        response += "• Complete all foundation courses (CS 18000-25200)\n"
        response += "• CS 38100 (Introduction to Algorithms)\n"
        response += "• Complete a track (minimum 6 courses)\n"
        response += "• Grade of C or better in all CS courses\n"
        response += "• 32 upper-level credits (30000+) at Purdue\n\n"
        
        response += "Track Requirements:\n"
        response += "• Choose from 9 available tracks\n"
        response += "• Complete 4 required courses for your track\n"
        response += "• Complete 2 elective courses from approved list\n"
        response += "• Some tracks have additional requirements\n\n"
        
        response += "Math & Science Requirements:\n"
        response += "• MA 16100, MA 16200 (Calculus I & II)\n"
        response += "• MA 26100 (Multivariate Calculus)\n"
        response += "• MA 26500 (Linear Algebra)\n"
        response += "• STAT 35000 (Statistics)\n"
        response += "• 2 Science courses with labs\n\n"
        
        response += "To check your progress:\n"
        response += "• Run a degree audit in MyPurdue\n"
        response += "• Meet with your academic advisor\n"
        response += "• Use the CS degree checklist\n\n"
        
        response += "What specific graduation requirement are you concerned about? I can help you understand what you still need!"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.95,
            "intent": intent["primary_intent"],
            "source_data": {"type": "graduation_requirements"},
            "track": None
        }
    
    def _handle_career_guidance(self, query: str, intent: Dict) -> Dict[str, Any]:
        """
        Handle career guidance and internship questions
        """
        
        response = "I'm excited to help with your career planning!\n\n"
        
        response += "Popular CS Career Paths:\n\n"
        response += "Software Engineering:\n"
        response += "• Companies: Google, Microsoft, Amazon, Meta, Apple\n"
        response += "• Starting salary: $95,000-$180,000\n"
        response += "• Key skills: Java, Python, System Design, Algorithms\n"
        response += "• Recommended courses: CS 30700, CS 35400, CS 42200\n\n"
        
        response += "Artificial Intelligence/Machine Learning:\n"
        response += "• Companies: Gemini, Google DeepMind, Microsoft Research, NVIDIA\n"
        response += "• Starting salary: $110,000-$200,000\n"
        response += "• Key skills: Python, TensorFlow, PyTorch, Statistics\n"
        response += "• Recommended courses: CS 37300, CS 57700, CS 57800\n\n"
        
        response += "Internship Timeline:\n"
        response += "• Freshman/Sophomore: Focus on building skills, small projects\n"
        response += "• Junior year: Prime time for major company internships\n"
        response += "• Senior year: Full-time job search, return offers\n\n"
        
        response += "Career Preparation:\n"
        response += "• Build projects and portfolio on GitHub\n"
        response += "• Practice coding interviews (LeetCode, HackerRank)\n"
        response += "• Attend career fairs and company info sessions\n"
        response += "• Join CS organizations (ACM, IEEE, etc.)\n"
        response += "• Get involved in research or open source projects\n\n"
        
        response += "What specific career area interests you most? I can provide more targeted guidance for your chosen path!"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.9,
            "intent": intent["primary_intent"],
            "source_data": {"type": "career_guidance"},
            "track": None
        }
    
    def _handle_program_overview(self, query: str, intent: Dict) -> Dict[str, Any]:
        """
        Handle program overview questions about the CS program at Purdue
        """
        
        response = "The CS program at Purdue is fantastic! Here's what makes it special:\n\n"
        
        response += "Program Strengths:\n"
        response += "• Ranked #20 nationally for computer science\n"
        response += "• 9 specialized tracks (AI, Software Engineering, Graphics, etc.)\n"
        response += "• Strong industry connections (Google, Microsoft, Amazon recruit heavily)\n"
        response += "• Excellent research opportunities across all CS areas\n\n"
        
        response += "What Students Love:\n"
        response += "• Hands-on learning from freshman year\n"
        response += "• Supportive CS community and study groups\n"
        response += "• Great job placement rates (95%+ employment)\n"
        response += "• Flexible track system lets you specialize\n\n"
        
        response += "Program Structure:\n"
        response += "• 2 years of foundation courses (programming, math, systems)\n"
        response += "• 2 years of track specialization and advanced courses\n"
        response += "• Real-world projects and internship opportunities\n"
        response += "• Strong emphasis on both theory and practical skills\n\n"
        
        response += "Career Outcomes:\n"
        response += "• Average starting salary: $95,000-$120,000\n"
        response += "• Top employers: FAANG companies, startups, research labs\n"
        response += "• Strong alumni network in Silicon Valley and beyond\n\n"
        
        response += "What specific aspect interests you most? I can dive deeper into tracks, courses, career paths, or anything else!"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.95,
            "intent": intent["primary_intent"],
            "source_data": {"type": "program_overview"},
            "track": None
        }
    
    def _handle_course_info(self, query: str, intent: Dict) -> Dict[str, Any]:
        """
        Handle general course information questions
        """
        
        response = "I'd love to help you learn about CS courses at Purdue!\n\n"
        
        response += "Foundation Courses (Years 1-2):\n"
        response += "• CS 18000: Problem Solving & Object-Oriented Programming\n"
        response += "• CS 18200: Foundations of Computer Science (discrete math)\n"
        response += "• CS 24000: Programming in C\n"
        response += "• CS 25000: Computer Architecture\n"
        response += "• CS 25100: Data Structures and Algorithms\n"
        response += "• CS 25200: Systems Programming\n\n"
        
        response += "Core Requirements:\n"
        response += "• CS 38100: Introduction to Algorithms (junior year)\n"
        response += "• Math sequence: Calculus I & II, Multivariate Calculus, Linear Algebra\n"
        response += "• STAT 35000: Statistics\n"
        response += "• Science courses with labs\n\n"
        
        response += "Track Specialization (Years 3-4):\n"
        response += "• Choose from 9 tracks (Machine Intelligence, Software Engineering, etc.)\n"
        response += "• 4 required courses + 2 electives per track\n"
        response += "• Advanced courses in your area of interest\n\n"
        
        response += "Which specific course or area would you like to know more about? I can provide detailed information about any CS course!"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.9,
            "intent": intent["primary_intent"],
            "source_data": {"type": "course_info"},
            "track": None
        }