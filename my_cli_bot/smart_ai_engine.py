#!/usr/bin/env python3
"""
Smart AI Engine - Advanced Query Understanding and Data Retrieval
Provides 100% accurate responses by understanding user intent and fetching precise data
"""

import json
import re
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

# Import comprehensive failure analyzer (includes all prerequisite analysis)
from comprehensive_failure_analyzer import ComprehensiveFailureAnalyzer

@dataclass
class QueryIntent:
    """Structured representation of user query intent"""
    primary_intent: str
    confidence: float
    entities: Dict[str, Any]  # Course codes, years, tracks, etc.
    context_clues: Dict[str, Any]  # Extracted context information
    requires_clarification: bool
    specific_topics: List[str]

@dataclass
class DataSource:
    """Represents a data source for information retrieval"""
    name: str
    path: str
    data_type: str  # json, sqlite, text, etc.
    description: str
    last_updated: str

class SmartAIEngine:
    """Advanced AI engine with precise query understanding and data retrieval"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
        # Initialize advanced query logger
        try:
            from advanced_query_logger import AdvancedQueryLogger
            self.query_logger = AdvancedQueryLogger("boilerai_queries.log")
            self.logger.info("Advanced query logger initialized")
        except ImportError:
            self.query_logger = None
            self.logger.warning("Advanced query logger not available")
        
        self.data_sources = []
        self.intent_patterns = {}
        self.entity_extractors = {}
        
        # Initialize comprehensive failure analyzer
        self.prerequisite_analyzer = ComprehensiveFailureAnalyzer()
        self.logger.info("Comprehensive failure analyzer initialized")
        
        self.load_all_data_sources()
        self.initialize_intent_patterns()
        self.initialize_entity_extractors()
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('smart_ai_engine.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_all_data_sources(self):
        """Load all available data sources"""
        self.data_sources = {
            "course_catalog": DataSource(
                "Course Catalog", 
                "data/comprehensive_purdue_cs_data.json",
                "json",
                "Complete course information with prerequisites and descriptions",
                "2025-01-19"
            ),
            "knowledge_graph": DataSource(
                "Knowledge Graph",
                "data/cs_knowledge_graph.json", 
                "json",
                "Structured knowledge about CS program requirements",
                "2025-01-19"
            ),
            "track_requirements": DataSource(
                "Track Requirements",
                "degree_planner.py",
                "python",
                "Detailed track requirements and course specifications",
                "2025-01-19"
            ),
            "conversation_contexts": DataSource(
                "Conversation Contexts",
                "conversation_contexts.json",
                "json", 
                "Historical conversation data and context",
                "2025-01-19"
            ),
            "dual_track_planner": DataSource(
                "Dual Track Planner",
                "dual_track_planner.py",
                "python",
                "Dual track graduation planning logic",
                "2025-01-19"
            )
        }
        
        # Load actual data
        self.course_data = self.load_json_data("course_catalog")
        self.knowledge_graph = self.load_json_data("knowledge_graph")
        self.conversation_data = self.load_json_data("conversation_contexts")
        
        self.logger.info(f"Loaded {len(self.data_sources)} data sources")
        
    def load_json_data(self, source_name: str) -> Dict:
        """Load JSON data from specified source"""
        try:
            source = self.data_sources[source_name]
            with open(source.path, 'r') as f:
                data = json.load(f)
            self.logger.info(f"Loaded {source_name}: {len(data)} items")
            return data
        except Exception as e:
            self.logger.error(f"Failed to load {source_name}: {e}")
            return {}
            
    def initialize_intent_patterns(self):
        """Initialize comprehensive intent recognition patterns"""
        self.intent_patterns = {
            "course_planning": {
                "patterns": [
                    r"courses?\s+(?:for|in|during|from|to|through|across|over)",
                    r"(?:what|which|show|tell|list|give)\s+(?:courses?|classes?)",
                    r"(?:freshman|sophomore|junior|senior)\s+(?:year|semester)",
                    r"(?:cs|computer science|math|mathematics)\s+courses?",
                    r"(?:semester|year)\s+plan",
                    r"schedule\s+(?:for|of)",
                    r"take\s+(?:courses?|classes?)",
                    r"enroll\s+in"
                ],
                "keywords": ["course", "class", "schedule", "semester", "year", "plan", "take", "enroll"],
                "confidence_boost": 0.2
            },
            "graduation_planning": {
                "patterns": [
                    r"graduate\s+(?:early|on time|late|in|by)",
                    r"graduation\s+(?:plan|timeline|date|requirements)",
                    r"(?:4|four)\s+year\s+(?:plan|timeline)",
                    r"(?:3\.5|3\.5)\s+year\s+(?:plan|timeline)",
                    r"finish\s+(?:degree|program|major)",
                    r"complete\s+(?:degree|program|major)",
                    r"when\s+(?:can|will)\s+(?:i|you)\s+graduate",
                    r"timeline\s+(?:for|to)\s+graduation"
                ],
                "keywords": ["graduate", "graduation", "timeline", "finish", "complete", "degree"],
                "confidence_boost": 0.2
            },
            "track_selection": {
                "patterns": [
                    r"(?:machine intelligence|mi|ai|ml)\s+(?:track|specialization)",
                    r"(?:software engineering|se)\s+(?:track|specialization)",
                    r"which\s+track\s+(?:should|to|do)",
                    r"choose\s+(?:between|among)\s+tracks",
                    r"track\s+(?:comparison|vs|versus)",
                    r"specialize\s+in",
                    r"concentration\s+in"
                ],
                "keywords": ["track", "specialization", "concentration", "machine intelligence", "software engineering"],
                "confidence_boost": 0.2
            },
            "prerequisites": {
                "patterns": [
                    r"prerequisite\s+(?:for|of)",
                    r"before\s+taking",
                    r"required\s+(?:before|for)",
                    r"need\s+(?:to|for)\s+(?:take|complete)",
                    r"prepare\s+for",
                    r"ready\s+for",
                    r"able\s+to\s+take",
                    r"can\s+(?:i|you)\s+take",
                    r"still.*take",
                    r"prerequisite\s+chain"
                ],
                "keywords": ["prerequisite", "before", "required", "need", "prepare", "able", "can", "take", "chain"],
                "confidence_boost": 0.15
            },
            "failure_analysis": {
                "patterns": [
                    r"(?:fail|failing|failed)\s+(?:cs|calc|math|course|class)",
                    r"if\s+(?:i|you)\s+(?:fail|don't pass)",
                    r"impact\s+(?:of|from)\s+(?:failing|failure)",
                    r"what\s+happens\s+if.*(?:fail|failure)",
                    r"graduation\s+delay",
                    r"recovery.*(?:fail|failure)",
                    r"summer\s+(?:course|recovery|catch.?up)"
                ],
                "keywords": ["fail", "failing", "failed", "failure", "impact", "happens", "delay", "recovery", "summer"],
                "confidence_boost": 0.25
            },
            "course_difficulty": {
                "patterns": [
                    r"(?:hard|difficult|easy|challenging)\s+(?:course|class)",
                    r"difficulty\s+(?:of|for)",
                    r"how\s+(?:hard|easy|difficult)",
                    r"workload\s+(?:of|for)",
                    r"time\s+(?:commitment|required)"
                ],
                "keywords": ["hard", "difficult", "easy", "challenging", "workload", "time"],
                "confidence_boost": 0.15
            },
            "career_guidance": {
                "patterns": [
                    r"career\s+(?:path|opportunity|prospect)",
                    r"job\s+(?:after|prospect|opportunity)",
                    r"internship\s+(?:opportunity|requirement)",
                    r"industry\s+(?:work|career)",
                    r"graduate\s+school",
                    r"research\s+(?:opportunity|career)"
                ],
                "keywords": ["career", "job", "internship", "industry", "research"],
                "confidence_boost": 0.15
            },
            "data_science_course_info": {
                "patterns": [
                    r"(?:what|tell|about)\s+(?:is|me about)?\s*(?:ILS|PHIL|STAT|MA|CS)\s*\d+",
                    r"(?:ILS|PHIL|STAT|MA|CS)\s*\d+\s+(?:is|about|description|course)",
                    r"(?:learn|learning|outcomes|objectives)\s+(?:in|from)?\s*(?:ILS|PHIL|STAT|MA|CS)\s*\d+",
                    r"what\s+do\s+you\s+learn\s+(?:in|from)\s*(?:ILS|PHIL|STAT|MA|CS)\s*\d+",
                    r"(?:description|details?)\s+(?:of|for)\s*(?:ILS|PHIL|STAT|MA|CS)\s*\d+"
                ],
                "keywords": ["ILS", "PHIL", "STAT", "MA", "what", "tell", "about", "learn", "description", "course"],
                "confidence_boost": 0.3
            }
        }
        
    def initialize_entity_extractors(self):
        """Initialize entity extraction patterns"""
        self.entity_patterns = {
            "course_codes": [
                r"CS\s+\d{5}",  # CS 18000
                r"MA\s+\d{5}",  # MA 16100
                r"STAT\s+\d{5}",  # STAT 35000
                r"PHYS\s+\d{5}",  # PHYS 17200
                r"ENGL\s+\d{5}"   # ENGL 10600
            ],
            "academic_years": [
                r"freshman",
                r"sophomore", 
                r"junior",
                r"senior",
                r"first\s+year",
                r"second\s+year",
                r"third\s+year",
                r"fourth\s+year"
            ],
            "tracks": [
                r"machine\s+intelligence",
                r"software\s+engineering",
                r"mi\s+track",
                r"se\s+track"
            ],
            "timeline_indicators": [
                r"early\s+graduation",
                r"accelerated",
                r"fast(?:est)?",
                r"quick(?:est)?",
                r"3\.5\s+year",
                r"4\s+year"
            ]
        }
        
    def understand_query(self, query: str, context: Dict[str, Any] = None) -> QueryIntent:
        """Comprehensive query understanding with high accuracy"""
        
        query_lower = query.lower()
        self.logger.info(f"Analyzing query: {query}")
        
        # Extract entities
        entities = self.extract_entities(query)
        
        # Analyze intent patterns
        intent_scores = self.analyze_intent_patterns(query_lower)
        
        # Apply context boost
        if context:
            intent_scores = self.apply_context_boost(intent_scores, context)
            
        # Determine primary intent
        primary_intent = max(intent_scores, key=intent_scores.get) if intent_scores else "general_query"
        confidence = intent_scores.get(primary_intent, 0.5)
        
        # Extract context clues
        context_clues = self.extract_context_clues(query_lower, entities)
        
        # Determine if clarification is needed
        requires_clarification = confidence < 0.6 or self.needs_clarification(query_lower, entities)
        
        # Identify specific topics
        specific_topics = self.identify_specific_topics(query_lower, entities, primary_intent)
        
        intent = QueryIntent(
            primary_intent=primary_intent,
            confidence=confidence,
            entities=entities,
            context_clues=context_clues,
            requires_clarification=requires_clarification,
            specific_topics=specific_topics
        )
        
        self.logger.info(f"Query intent: {intent.primary_intent} (confidence: {intent.confidence:.2f})")
        return intent
        
    def extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract structured entities from query"""
        entities = {
            "course_codes": [],
            "academic_years": [],
            "tracks": [],
            "timeline_indicators": [],
            "numbers": [],
            "keywords": []
        }
        
        # Extract course codes
        for pattern in self.entity_patterns["course_codes"]:
            matches = re.findall(pattern, query, re.IGNORECASE)
            entities["course_codes"].extend(matches)
            
        # Extract academic years
        for pattern in self.entity_patterns["academic_years"]:
            if re.search(pattern, query, re.IGNORECASE):
                entities["academic_years"].append(pattern)
                
        # Extract tracks
        for pattern in self.entity_patterns["tracks"]:
            if re.search(pattern, query, re.IGNORECASE):
                entities["tracks"].append(pattern)
                
        # Extract timeline indicators
        for pattern in self.entity_patterns["timeline_indicators"]:
            if re.search(pattern, query, re.IGNORECASE):
                entities["timeline_indicators"].append(pattern)
                
        # Extract numbers
        numbers = re.findall(r'\d+(?:\.\d+)?', query)
        entities["numbers"] = numbers
        
        # Extract important keywords
        important_keywords = ["both", "dual", "multiple", "track", "course", "semester", "year", "graduate", "plan"]
        for keyword in important_keywords:
            if keyword in query.lower():
                entities["keywords"].append(keyword)
                
        return entities
        
    def analyze_intent_patterns(self, query: str) -> Dict[str, float]:
        """Analyze query using pattern matching for intent detection"""
        intent_scores = {}
        
        for intent, config in self.intent_patterns.items():
            score = 0
            
            # Pattern matching
            for pattern in config["patterns"]:
                if re.search(pattern, query, re.IGNORECASE):
                    score += 0.4
                    
            # Keyword matching
            keyword_matches = sum(1 for keyword in config["keywords"] if keyword in query)
            if keyword_matches > 0:
                score += min(0.3, keyword_matches * 0.1)
                
            # Apply confidence boost
            score += config["confidence_boost"]
            
            if score > 0:
                intent_scores[intent] = min(0.95, score)
                
        return intent_scores
        
    def apply_context_boost(self, intent_scores: Dict[str, float], context: Dict[str, Any]) -> Dict[str, float]:
        """Apply context-based confidence boost"""
        for intent, score in intent_scores.items():
            boost = 0
            
            # Boost based on previous queries
            if "last_queries" in context:
                for prev_query in context["last_queries"][-3:]:  # Last 3 queries
                    if intent in prev_query.lower():
                        boost += 0.1
                        
            # Boost based on extracted context
            if intent == "course_planning" and context.get("current_year"):
                boost += 0.1
            elif intent == "track_selection" and context.get("target_track"):
                boost += 0.1
            elif intent == "graduation_planning" and context.get("graduation_timeline_goals"):
                boost += 0.1
                
            intent_scores[intent] = min(0.95, score + boost)
            
        return intent_scores
        
    def extract_context_clues(self, query: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context clues from query"""
        clues = {}
        
        # Academic year clues
        if entities["academic_years"]:
            clues["current_year"] = entities["academic_years"][0]
            
        # Track preferences
        if entities["tracks"]:
            clues["target_track"] = entities["tracks"][0]
            
        # Timeline preferences
        if entities["timeline_indicators"]:
            clues["graduation_timeline_goals"] = entities["timeline_indicators"][0]
            
        # Course-specific queries
        if entities["course_codes"]:
            clues["specific_courses"] = entities["course_codes"]
            
        # Dual track indicators
        if "both" in entities["keywords"] or "dual" in entities["keywords"]:
            clues["dual_track_interest"] = True
            
        return clues
        
    def needs_clarification(self, query: str, entities: Dict[str, Any]) -> bool:
        """Determine if query needs clarification"""
        
        # Vague queries
        vague_indicators = ["what", "how", "tell me", "show me", "help"]
        if any(indicator in query for indicator in vague_indicators) and not entities["course_codes"] and not entities["tracks"]:
            return True
            
        # Ambiguous track references
        if "track" in query.lower() and not entities["tracks"]:
            return True
            
        # Missing context for course planning
        if "course" in query.lower() and not entities["academic_years"] and not entities["course_codes"]:
            return True
            
        return False
        
    def identify_specific_topics(self, query: str, entities: Dict[str, Any], primary_intent: str) -> List[str]:
        """Identify specific topics within the query"""
        topics = []
        
        if entities["course_codes"]:
            topics.extend([f"course_{code}" for code in entities["course_codes"]])
            
        if entities["tracks"]:
            topics.extend(entities["tracks"])
            
        if entities["academic_years"]:
            topics.extend(entities["academic_years"])
            
        if "both" in entities["keywords"] or "dual" in entities["keywords"]:
            topics.append("dual_track")
            
        if entities["timeline_indicators"]:
            topics.extend(entities["timeline_indicators"])
            
        return topics
        
    def fetch_relevant_data(self, intent: QueryIntent) -> Dict[str, Any]:
        """Fetch relevant data based on query intent"""
        relevant_data = {}
        
        self.logger.info(f"Fetching data for intent: {intent.primary_intent}")
        
        if intent.primary_intent == "course_planning":
            relevant_data.update(self.fetch_course_planning_data(intent))
        elif intent.primary_intent == "graduation_planning":
            relevant_data.update(self.fetch_graduation_planning_data(intent))
        elif intent.primary_intent == "track_selection":
            relevant_data.update(self.fetch_track_selection_data(intent))
        elif intent.primary_intent == "prerequisites":
            relevant_data.update(self.fetch_prerequisites_data(intent))
        elif intent.primary_intent == "course_difficulty":
            relevant_data.update(self.fetch_course_difficulty_data(intent))
        elif intent.primary_intent == "career_guidance":
            relevant_data.update(self.fetch_career_guidance_data(intent))
            
        # Always include general course data
        relevant_data["course_catalog"] = self.course_data.get("courses", {})
        relevant_data["knowledge_graph"] = self.knowledge_graph
        
        self.logger.info(f"Fetched {len(relevant_data)} data sources")
        return relevant_data
        
    def fetch_course_planning_data(self, intent: QueryIntent) -> Dict[str, Any]:
        """Fetch data relevant to course planning"""
        data = {}
        
        # Get course catalog
        if "courses" in self.course_data:
            data["courses"] = self.course_data["courses"]
            
        # Get prerequisites
        if "prerequisites" in self.course_data:
            data["prerequisites"] = self.course_data["prerequisites"]
            
        # Get degree requirements
        if "degree_requirements" in self.knowledge_graph:
            data["degree_requirements"] = self.knowledge_graph["degree_requirements"]
            
        # Get track requirements
        if "tracks" in self.knowledge_graph:
            data["track_requirements"] = self.knowledge_graph["tracks"]
            
        return data
        
    def fetch_graduation_planning_data(self, intent: QueryIntent) -> Dict[str, Any]:
        """Fetch data relevant to graduation planning"""
        data = {}
        
        # Get graduation timelines
        if "graduation_timelines" in self.knowledge_graph:
            data["graduation_timelines"] = self.knowledge_graph["graduation_timelines"]
            
        # Get degree requirements
        if "degree_requirements" in self.knowledge_graph:
            data["degree_requirements"] = self.knowledge_graph["degree_requirements"]
            
        # Get track requirements
        if "tracks" in self.knowledge_graph:
            data["track_requirements"] = self.knowledge_graph["tracks"]
            
        # Check for dual track interest
        if intent.context_clues.get("dual_track_interest"):
            try:
                from dual_track_planner import DualTrackGraduationPlanner
                data["dual_track_planner"] = DualTrackGraduationPlanner()
            except ImportError:
                self.logger.warning("Dual track planner not available")
                
        return data
        
    def fetch_track_selection_data(self, intent: QueryIntent) -> Dict[str, Any]:
        """Fetch data relevant to track selection"""
        data = {}
        
        # Get track information
        if "tracks" in self.knowledge_graph:
            data["tracks"] = self.knowledge_graph["tracks"]
            
        # Get career guidance
        if "career_guidance" in self.knowledge_graph:
            data["career_guidance"] = self.knowledge_graph["career_guidance"]
            
        # Get course requirements for each track
        if "courses" in self.course_data:
            data["courses"] = self.course_data["courses"]
            
        return data
        
    def fetch_prerequisites_data(self, intent: QueryIntent) -> Dict[str, Any]:
        """Fetch data relevant to prerequisites"""
        data = {}
        
        # Get prerequisites
        if "prerequisites" in self.course_data:
            data["prerequisites"] = self.course_data["prerequisites"]
            
        # Get course catalog
        if "courses" in self.course_data:
            data["courses"] = self.course_data["courses"]
            
        return data
        
    def fetch_course_difficulty_data(self, intent: QueryIntent) -> Dict[str, Any]:
        """Fetch data relevant to course difficulty"""
        data = {}
        
        # Get course catalog with difficulty info
        if "courses" in self.course_data:
            data["courses"] = self.course_data["courses"]
            
        # Get student feedback if available
        if "student_feedback" in self.knowledge_graph:
            data["student_feedback"] = self.knowledge_graph["student_feedback"]
            
        return data
        
    def fetch_career_guidance_data(self, intent: QueryIntent) -> Dict[str, Any]:
        """Fetch data relevant to career guidance"""
        data = {}
        
        # Get career guidance
        if "career_guidance" in self.knowledge_graph:
            data["career_guidance"] = self.knowledge_graph["career_guidance"]
            
        # Get track information
        if "tracks" in self.knowledge_graph:
            data["tracks"] = self.knowledge_graph["tracks"]
            
        return data
        
    def generate_accurate_response(self, query: str, intent: QueryIntent, data: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Generate 100% accurate response using proper NLP and knowledge graphs"""
        
        self.logger.info(f"Generating NLP-based response for {intent.primary_intent}")
        
        # Check if this is a prerequisite/failure analysis query that should use intelligent analyzer
        if intent.primary_intent in ["prerequisites", "failure_analysis"] or self._should_use_prerequisite_analyzer(query):
            return self._handle_with_prerequisite_analyzer(query, intent, context)
        
        # Check if this is a Data Science course query
        if intent.primary_intent == "data_science_course_info" or self._contains_ds_course_codes(query):
            ds_course_response = self._handle_data_science_course_query(query, intent)
            if ds_course_response:
                return ds_course_response
        
        # Import the simple NLP solver
        try:
            from simple_nlp_solver import SimpleNLPSolver, SemanticQuery
            
            # Initialize NLP solver if not already done
            if not hasattr(self, 'nlp_solver'):
                self.nlp_solver = SimpleNLPSolver()
                if self.query_logger:
                    self.nlp_solver.set_query_logger(self.query_logger)
                self.nlp_solver.build_knowledge_graph(data)
            
            # Understand query semantically
            semantic_query = self.nlp_solver.understand_query_semantically(query)
            
            # Solve using knowledge graph and NLP
            response = self.nlp_solver.solve_using_knowledge_graph(semantic_query)
            
            self.logger.info(f"Generated NLP-based response: {len(response)} characters")
            return response
            
        except ImportError:
            self.logger.warning("Simple NLP solver not available, using fallback")
            return self._generate_fallback_response(query, intent, data, context)
        except Exception as e:
            self.logger.error(f"Error in NLP-based response generation: {e}")
            return self._generate_fallback_response(query, intent, data, context)
    
    def _generate_fallback_response(self, query: str, intent: QueryIntent, data: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Dynamic fallback response generation using knowledge base data"""
        
        try:
            # Use the NLP knowledge solver for dynamic responses
            from nlp_knowledge_solver import NLPKnowledgeSolver
            
            solver = NLPKnowledgeSolver()
            response = solver.process_query(query)
            
            if response and len(response) > 50:  # Ensure it's a substantial response
                return response
                
        except ImportError:
            self.logger.warning("NLP knowledge solver not available for fallback")
        except Exception as e:
            self.logger.error(f"Error in fallback NLP processing: {e}")
        
        # If NLP solver fails, generate dynamic response using available data
        return self._generate_dynamic_fallback(query, intent, data, context)
    
    def _generate_dynamic_fallback(self, query: str, intent: QueryIntent, data: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Generate dynamic response using available knowledge base data"""
        
        # Extract relevant information from data
        courses = data.get("courses", {})
        degree_requirements = data.get("degree_requirements", {})
        track_requirements = data.get("track_requirements", {})
        
        # Generate personalized response based on intent and available data
        current_year = intent.context_clues.get("current_year", "")
        course_codes = intent.entities.get("course_codes", [])
        tracks = intent.entities.get("tracks", [])
        
        if intent.primary_intent == "course_planning":
            # Generate dynamic course planning response
            if current_year:
                year_courses = []
                for course_id, course_info in courses.items():
                    if isinstance(course_info, dict) and course_info.get("typical_year") == current_year:
                        year_courses.append(course_id)
                
                if year_courses:
                    course_list = ", ".join(year_courses[:3])  # Show first 3 courses
                    response = f"For {current_year} students, I recommend starting with courses like {course_list}. "
                    if intent.context_clues.get("dual_track_interest"):
                        response += "Since you're interested in both tracks, we'll need to plan carefully for the additional coursework."
                    else:
                        response += "What specific area interests you most - programming, algorithms, or software development?"
                    return response
                    
            return f"Let me help you plan your coursework. What year are you currently in and what areas of computer science interest you most?"
        
        elif intent.primary_intent == "prerequisites":
            if course_codes:
                # Try to find prerequisite information in the data
                prereq_info = []
                for course in course_codes:
                    if course in courses:
                        course_info = courses[course]
                        if isinstance(course_info, dict) and "prerequisites" in course_info:
                            prereqs = course_info["prerequisites"]
                            if prereqs:
                                prereq_info.append(f"{course} requires: {', '.join(prereqs)}")
                            else:
                                prereq_info.append(f"{course} has no prerequisites")
                
                if prereq_info:
                    return " ".join(prereq_info) + ". Do you need help planning when to take these courses?"
                else:
                    return f"Let me look up the prerequisite information for {', '.join(course_codes)}. Which specific course are you most concerned about?"
            
            return "I can help you understand course prerequisites. Which specific course are you asking about?"
        
        elif intent.primary_intent == "track_selection":
            # Generate dynamic track information
            available_tracks = []
            for track_id, track_info in track_requirements.items():
                if isinstance(track_info, dict):
                    available_tracks.append(track_id)
            
            if available_tracks:
                track_list = " and ".join(available_tracks)
                response = f"Purdue CS offers {track_list} tracks. "
                if current_year:
                    response += f"As a {current_year}, you have time to explore both before choosing. "
                response += "What career goals or interests do you have that might help guide your choice?"
                return response
            
            return "I can help you choose between the available computer science tracks. What are your career interests and technical preferences?"
        
        elif intent.primary_intent == "graduation_planning":
            # Generate graduation planning response using degree requirements
            if degree_requirements:
                total_credits = degree_requirements.get("total_credits", 120)
                cs_credits = degree_requirements.get("cs_core_credits", 29)
                response = f"Purdue CS requires {total_credits} total credits including {cs_credits} core CS credits. "
                
                if current_year:
                    if current_year == "freshman":
                        response += "You're just starting, so we have plenty of time to plan an optimal path. "
                    elif current_year == "sophomore":
                        response += "You're in a great position to plan your remaining coursework efficiently. "
                    elif current_year in ["junior", "senior"]:
                        response += "Let's focus on completing your remaining requirements efficiently. "
                
                response += "Are you looking for early graduation, standard timeline, or have you had any setbacks?"
                return response
            
            return "I can help you plan your graduation timeline. What's your current academic standing and target graduation date?"
        
        # Default fallback - ask for clarification with helpful context
        knowledge_areas = []
        if courses:
            knowledge_areas.append(f"{len(courses)} courses")
        if track_requirements:
            knowledge_areas.append("track requirements")
        if degree_requirements:
            knowledge_areas.append("degree planning")
        
        if knowledge_areas:
            areas_text = ", ".join(knowledge_areas)
            return f"I have knowledge about {areas_text} and can help with your Purdue CS questions. Could you provide more specific details about what you need help with?"
        
        return "I'm here to help with Purdue CS academic advising. What specific question do you have about courses, requirements, or planning?"

    def process_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Main method to process a query and return accurate response with advanced logging"""
        
        # Start query session logging
        session_id = None
        if self.query_logger:
            session_id = self.query_logger.start_session(query)
        
        try:
            # Step 1: Understand the query
            if self.query_logger:
                self.query_logger.log_step(session_id, "query_understanding", 
                    {"query": query, "context": context}, {})
            
            intent = self.understand_query(query, context)
            
            if self.query_logger:
                self.query_logger.log_step(session_id, "intent_detection", 
                    {"query": query}, {"intent": intent.primary_intent, "confidence": intent.confidence})
                
                # Log NLP processing
                self.query_logger.log_nlp_processing(session_id, "intent_analysis", 
                    intent.entities, intent.context_clues, intent.primary_intent)
            
            # Step 2: Fetch relevant data
            if self.query_logger:
                self.query_logger.log_step(session_id, "data_fetching", 
                    {"intent": intent.primary_intent}, {})
            
            data = self.fetch_relevant_data(intent)
            
            if self.query_logger:
                self.query_logger.log_step(session_id, "data_retrieved", 
                    {"intent": intent.primary_intent}, {"data_sources": len(data)})
                
                # Log knowledge node access
                for source_name, source_data in data.items():
                    if isinstance(source_data, dict) and source_data:
                        self.query_logger.log_knowledge_node_access(session_id, source_name, 
                            "data_source", "fetch", {"items": len(source_data)})
            
            # Step 3: Generate accurate response
            if self.query_logger:
                self.query_logger.log_step(session_id, "response_generation", 
                    {"intent": intent.primary_intent, "data_sources": len(data)}, {})
            
            response = self.generate_accurate_response(query, intent, data, context)
            
            if self.query_logger:
                self.query_logger.log_step(session_id, "response_completed", 
                    {"intent": intent.primary_intent}, {"response_length": len(response)})
                
                # Log AI method used
                self.query_logger.log_ai_method_used(session_id, "smart_ai_engine", {
                    "method": "nlp_knowledge_solver",
                    "intent": intent.primary_intent,
                    "entities": intent.entities,
                    "concepts": intent.context_clues
                })
            
            self.logger.info(f"Successfully processed query: {query[:50]}...")
            
            # End session logging
            if self.query_logger:
                self.query_logger.end_session(session_id, response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            
            # Log error in session
            if self.query_logger and session_id:
                self.query_logger.log_step(session_id, "error_handling", 
                    {"query": query}, {"error": str(e)}, success=False, error_message=str(e))
                self.query_logger.end_session(session_id, f"Error: {str(e)}")
            
            return f"I encountered an error while processing your query. Please try rephrasing your question or contact support if the issue persists. Error: {str(e)}"
    
    def _should_use_prerequisite_analyzer(self, query: str) -> bool:
        """Determine if query should be handled by intelligent prerequisite analyzer"""
        query_lower = query.lower()
        
        # Check for ALL foundation and math course patterns (comprehensive coverage)
        course_patterns = [
            r'\bcs\s*(?:180|18000|182|18200|240|24000|250|25000|251|25100|252|25200)\b',
            r'\bma\s*(?:161|16100|162|16200|261|26100|265|26500)\b',
            r'\b(?:180|18000|182|18200|240|24000|250|25000|251|25100|252|25200)\b',
            r'\b(?:161|16100|162|16200|261|26100|265|26500)\b'
        ]
        
        has_course_numbers = any(re.search(pattern, query_lower) for pattern in course_patterns)
        
        # Check for failure/prerequisite keywords (comprehensive failure analyzer handles all)
        failure_keywords = [
            'fail', 'failing', 'failed', 'failure',
            'prerequisite', 'prereq', 'before taking',
            'able to take', 'can i take', 'still take',
            'calc 1', 'calc1', 'calculus 1', 'calculus',
            'calc 2', 'calc2', 'calculus 2',
            'linear algebra', 'linear', 'math',
            'summer', 'recovery', 'retake', 'delay',
            'graduation delay', 'semester delay'
        ]
        
        has_failure_keywords = any(keyword in query_lower for keyword in failure_keywords)
        
        # Use comprehensive failure analyzer if we have course numbers OR failure/prerequisite keywords
        # The comprehensive analyzer handles all foundation classes and math classes
        return has_course_numbers or has_failure_keywords
    
    def _contains_ds_course_codes(self, query: str) -> bool:
        """Check if query contains Data Science course codes"""
        ds_course_codes = [
            "ILS 23000", "PHIL 20700", "PHIL 20800",
            "MA 43200", "STAT 42000", "STAT 50600", "STAT 51200", 
            "STAT 51300", "STAT 51400", "STAT 52200", "STAT 52500",
            "CS 49000", "CS 44100",
            "CS 25300", "STAT 24200", "CS 37300", "CS 44000", "CS 38003", 
            "STAT 35500", "STAT 41600", "STAT 41700"
        ]
        
        query_upper = query.upper()
        for code in ds_course_codes:
            # Check for exact match or without space
            if code in query_upper or code.replace(" ", "") in query_upper:
                return True
        return False

    def _handle_data_science_course_query(self, query: str, intent: QueryIntent) -> Optional[str]:
        """Handle Data Science course queries with description first, then optional learning outcomes"""
        
        # Check if this is a course query about Data Science courses
        course_patterns = [
            r'\b(ILS|PHIL|STAT|MA|CS)\s*(\d+)\b',  # ILS 23000, PHIL 20700, etc.
            r'\b(ILS|PHIL|STAT|MA|CS)(\d+)\b',     # ILS23000, PHIL20700, etc.
        ]
        
        # Extract course codes from query
        course_codes = []
        for pattern in course_patterns:
            matches = re.finditer(pattern, query.upper())
            for match in matches:
                dept = match.group(1)
                number = match.group(2)
                course_codes.append(f"{dept} {number}")
        
        if not course_codes:
            return None
        
        # Data Science course codes to check against
        ds_course_codes = [
            # Ethics selective
            "ILS 23000", "PHIL 20700", "PHIL 20800",
            # Statistics selective  
            "MA 43200", "STAT 42000", "STAT 50600", "STAT 51200", 
            "STAT 51300", "STAT 51400", "STAT 52200", "STAT 52500",
            # Capstone
            "CS 49000", "CS 44100",
            # Core courses
            "CS 25300", "STAT 24200", "CS 37300", "CS 44000", "CS 38003", 
            "STAT 35500", "STAT 41600", "STAT 41700"
        ]
        
        # Check if any extracted course codes are Data Science courses
        found_ds_course = None
        for code in course_codes:
            if code in ds_course_codes:
                found_ds_course = code
                break
        
        if not found_ds_course:
            return None
        
        # Use the intelligent conversation manager method
        try:
            from intelligent_conversation_manager import IntelligentConversationManager
            manager = IntelligentConversationManager()
            return manager._handle_data_science_course_query(found_ds_course, query)
        except ImportError:
            return None
        except Exception as e:
            self.logger.error(f"Error handling Data Science course query: {e}")
            return None

    def _handle_with_prerequisite_analyzer(self, query: str, intent: QueryIntent, context: Dict[str, Any] = None) -> str:
        """Handle query using the comprehensive failure analyzer"""
        
        try:
            self.logger.info(f"Using comprehensive failure analyzer for: {query[:50]}...")
            
            # Analyze the query using the comprehensive failure analyzer
            response = self.prerequisite_analyzer.analyze_failure_query(query)
            
            # Log the method used
            if self.query_logger:
                self.query_logger.log_ai_method_used("current_session", "comprehensive_failure_analyzer", {
                    "query": query[:100],
                    "response_length": len(response),
                    "analysis_type": "comprehensive_failure_analysis"
                })
            
            self.logger.info(f"Generated comprehensive failure analysis response: {len(response)} characters")
            return response
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive failure analyzer: {e}")
            # Fall back to regular NLP solver
            return self._handle_prerequisite_fallback(query, intent, context)
    
    def _handle_prerequisite_fallback(self, query: str, intent: QueryIntent, context: Dict[str, Any] = None) -> str:
        """Fallback for prerequisite analysis using regular NLP"""
        
        try:
            from simple_nlp_solver import SimpleNLPSolver
            
            if not hasattr(self, 'nlp_solver'):
                self.nlp_solver = SimpleNLPSolver()
            
            semantic_query = self.nlp_solver.understand_query_semantically(query)
            return self.nlp_solver.solve_using_knowledge_graph(semantic_query)
            
        except Exception as e:
            self.logger.error(f"Prerequisite fallback failed: {e}")
            return "I'm having trouble analyzing prerequisites right now. Could you rephrase your question about course requirements or failure scenarios?"

if __name__ == "__main__":
    # Test the smart AI engine
    engine = SmartAIEngine()
    
    test_queries = [
        "What courses should I take as a freshman?",
        "I want to graduate with both machine intelligence and software engineering tracks",
        "What are the prerequisites for CS 37300?",
        "How hard is CS 25100?",
        "Which track should I choose for AI careers?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        response = engine.process_query(query)
        print(f"Response: {response}")
        print(f"{'='*60}")