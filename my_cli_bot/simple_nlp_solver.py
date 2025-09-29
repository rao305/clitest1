#!/usr/bin/env python3
"""
Simple NLP Knowledge Solver
Uses basic Python libraries and knowledge graph concepts
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from collections import defaultdict

@dataclass
class KnowledgeNode:
    """Represents a knowledge node"""
    id: str
    type: str
    content: Dict[str, Any]
    connections: List[str] = None

@dataclass
class SemanticQuery:
    """Represents semantic understanding of query"""
    intent: str
    entities: List[str]
    concepts: List[str]
    context: Dict[str, Any]

class SimpleNLPSolver:
    """Simple NLP solver using knowledge graphs and semantic understanding"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.knowledge_graph = {}
        self.course_nodes = {}
        self.track_nodes = {}
        self.concept_nodes = {}
        self.query_logger = None  # Will be set externally
        
    def set_query_logger(self, query_logger):
        """Set the query logger for detailed logging"""
        self.query_logger = query_logger
    
    def build_knowledge_graph(self, data: Dict[str, Any]):
        """Build knowledge graph from data"""
        self.logger.info("Building simple knowledge graph...")
        
        # Add course nodes
        courses = data.get("courses", {})
        for course_code, course_data in courses.items():
            node = KnowledgeNode(
                id=course_code,
                type="course",
                content=course_data,
                connections=[]
            )
            self.course_nodes[course_code] = node
            self.knowledge_graph[course_code] = node
            
            if self.query_logger:
                self.query_logger.log_knowledge_node_access("system", course_code, "course", "create", course_data)
        
        # Add track nodes
        tracks = data.get("track_requirements", {})
        for track_name, track_data in tracks.items():
            node = KnowledgeNode(
                id=track_name,
                type="track",
                content=track_data,
                connections=[]
            )
            self.track_nodes[track_name] = node
            self.knowledge_graph[track_name] = node
            
            if self.query_logger:
                self.query_logger.log_knowledge_node_access("system", track_name, "track", "create", track_data)
        
        # Add concept nodes
        concepts = {
            "foundation_courses": ["CS 18000", "CS 18200", "CS 24000", "CS 25000", "CS 25100", "CS 25200"],
            "advanced_courses": ["CS 37300", "CS 38100", "CS 40700", "CS 40800"],
            "ai_ml_courses": ["CS 37300", "CS 47100", "CS 47300"],
            "software_engineering_courses": ["CS 30700", "CS 40700", "CS 40800"],
            "dual_track": ["Machine Intelligence", "Software Engineering"]
        }
        
        for concept_name, related_items in concepts.items():
            node = KnowledgeNode(
                id=concept_name,
                type="concept",
                content={"related_items": related_items, "description": concept_name},
                connections=related_items
            )
            self.concept_nodes[concept_name] = node
            self.knowledge_graph[concept_name] = node
            
            if self.query_logger:
                self.query_logger.log_knowledge_node_access("system", concept_name, "concept", "create", 
                    {"related_items": related_items})
        
        # Add prerequisite relationships
        prerequisites = data.get("prerequisites", {})
        for course, prereqs in prerequisites.items():
            if course in self.course_nodes:
                self.course_nodes[course].connections.extend(prereqs)
                
                # Log graph traversal for prerequisites
                if self.query_logger:
                    for prereq in prereqs:
                        self.query_logger.log_graph_traversal("system", prereq, course, [prereq, course], "prerequisite")
        
        self.logger.info(f"Knowledge graph built with {len(self.knowledge_graph)} nodes")
    
    def understand_query_semantically(self, query: str) -> SemanticQuery:
        """Understand query using semantic analysis"""
        self.logger.info(f"Performing semantic analysis: {query}")
        
        # Extract entities
        entities = self._extract_entities(query)
        
        # Extract concepts
        concepts = self._extract_concepts(query)
        
        # Determine intent
        intent = self._determine_semantic_intent(query, entities, concepts)
        
        # Build context
        context = self._build_semantic_context(query, entities, concepts)
        
        return SemanticQuery(
            intent=intent,
            entities=entities,
            concepts=concepts,
            context=context
        )
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract entities from query"""
        entities = []
        
        # Course codes
        course_pattern = r'CS\s+\d{5}'
        entities.extend(re.findall(course_pattern, query))
        
        # Academic years
        year_pattern = r'\b(freshman|sophomore|junior|senior)\b'
        entities.extend(re.findall(year_pattern, query))
        
        # Tracks
        track_pattern = r'\b(machine intelligence|software engineering|MI|SE)\b'
        entities.extend(re.findall(track_pattern, query))
        
        return list(set(entities))
    
    def _extract_concepts(self, query: str) -> List[str]:
        """Extract concepts from query"""
        concepts = []
        query_lower = query.lower()
        
        concept_mapping = {
            "difficulty": ["hard", "difficult", "challenging", "easy", "workload"],
            "planning": ["plan", "schedule", "timeline", "graduation"],
            "prerequisites": ["prereq", "requirement", "before", "need"],
            "career": ["job", "career", "industry", "work", "ai"],
            "dual_track": ["both", "dual", "two tracks", "combine"],
            "foundation": ["foundation", "basic", "intro", "first", "freshman"],
            "advanced": ["advanced", "upper", "senior", "specialized"]
        }
        
        for concept, keywords in concept_mapping.items():
            if any(keyword in query_lower for keyword in keywords):
                concepts.append(concept)
        
        return concepts
    
    def _determine_semantic_intent(self, query: str, entities: List[str], concepts: List[str]) -> str:
        """Determine semantic intent"""
        query_lower = query.lower()
        
        if "dual_track" in concepts or "both" in query_lower:
            return "dual_track_planning"
        elif "difficulty" in concepts:
            return "course_difficulty"
        elif "planning" in concepts:
            return "course_planning"
        elif "prerequisites" in concepts:
            return "prerequisites"
        elif "career" in concepts:
            return "career_guidance"
        elif "foundation" in concepts:
            return "foundation_planning"
        else:
            return "general_advice"
    
    def _build_semantic_context(self, query: str, entities: List[str], concepts: List[str]) -> Dict[str, Any]:
        """Build semantic context"""
        return {
            "entities": entities,
            "concepts": concepts,
            "query_terms": query.lower().split(),
            "has_course_codes": bool(re.search(r'CS\s+\d{5}', query)),
            "has_tracks": bool(re.search(r'\b(machine intelligence|software engineering)\b', query.lower())),
            "has_years": bool(re.search(r'\b(freshman|sophomore|junior|senior)\b', query.lower())),
            "is_dual_track": "both" in query.lower() or "dual" in query.lower()
        }
    
    def solve_using_knowledge_graph(self, semantic_query: SemanticQuery) -> str:
        """Solve using knowledge graph and semantic understanding"""
        self.logger.info(f"Solving with knowledge graph for intent: {semantic_query.intent}")
        
        if semantic_query.intent == "dual_track_planning":
            return self._solve_dual_track_semantically(semantic_query)
        elif semantic_query.intent == "course_difficulty":
            return self._solve_course_difficulty_semantically(semantic_query)
        elif semantic_query.intent == "course_planning":
            return self._solve_course_planning_semantically(semantic_query)
        elif semantic_query.intent == "prerequisites":
            return self._solve_prerequisites_semantically(semantic_query)
        elif semantic_query.intent == "career_guidance":
            return self._solve_career_guidance_semantically(semantic_query)
        elif semantic_query.intent == "general_advice" or semantic_query.intent == "foundation_planning":
            return self._solve_general_advice_dynamically(semantic_query)
        else:
            return self._solve_general_advice_dynamically(semantic_query)
    
    def _solve_dual_track_semantically(self, semantic_query: SemanticQuery) -> str:
        """Solve dual track planning using semantic analysis"""
        
        # Find track nodes
        mi_track = None
        se_track = None
        for track_name, track_node in self.track_nodes.items():
            if "machine intelligence" in track_name.lower():
                mi_track = track_node
            elif "software engineering" in track_name.lower():
                se_track = track_node
        
        if not mi_track or not se_track:
            # Use AI to generate appropriate response for missing track data
            try:
                from intelligent_ai_response_generator import IntelligentAIResponseGenerator
                ai_gen = IntelligentAIResponseGenerator()
                return ai_gen.generate_response(
                    "The user asked about track information but the data is not available in the knowledge base. Generate a helpful response suggesting they contact an advisor.",
                    {"context": "missing_track_data", "query_topic": "track_comparison"}
                )
            except:
                return "I don't have complete track information available right now. Please contact a CS advisor for the most current track requirements."
        
        # Analyze requirements
        mi_courses = mi_track.content.get("required_courses", [])
        se_courses = se_track.content.get("required_courses", [])
        
        # Find overlapping courses
        overlapping = set(mi_courses) & set(se_courses)
        unique_mi = set(mi_courses) - set(se_courses)
        unique_se = set(se_courses) - set(mi_courses)
        
        # Build semantic response
        response_parts = []
        response_parts.append("🧠 SEMANTIC DUAL TRACK ANALYSIS")
        response_parts.append("=" * 50)
        response_parts.append("")
        
        response_parts.append("📊 KNOWLEDGE GRAPH ANALYSIS:")
        response_parts.append(f"• Machine Intelligence track: {len(mi_courses)} courses")
        response_parts.append(f"• Software Engineering track: {len(se_courses)} courses")
        response_parts.append(f"• Shared courses: {len(overlapping)}")
        response_parts.append(f"• Additional MI courses: {len(unique_mi)}")
        response_parts.append(f"• Additional SE courses: {len(unique_se)}")
        response_parts.append("")
        
        if overlapping:
            response_parts.append("🔗 SHARED KNOWLEDGE NODES:")
            for course in sorted(overlapping):
                response_parts.append(f"• {course}")
            response_parts.append("")
        
        # Calculate semantic complexity
        total_unique = len(unique_mi) + len(unique_se)
        complexity_score = self._calculate_semantic_complexity(mi_courses + se_courses)
        
        response_parts.append("🧠 SEMANTIC COMPLEXITY ANALYSIS:")
        response_parts.append(f"• Total unique courses: {total_unique}")
        response_parts.append(f"• Complexity score: {complexity_score:.2f}")
        response_parts.append(f"• Estimated workload: {total_unique / 8:.1f} courses/semester")
        response_parts.append("")
        
        response_parts.append("💡 SEMANTIC RECOMMENDATIONS:")
        response_parts.append("• Complete shared foundation courses first")
        response_parts.append("• Use knowledge graph to identify prerequisites")
        response_parts.append("• Leverage overlapping concepts between tracks")
        response_parts.append("• Plan for semantic complexity in advanced courses")
        
        return "\n".join(response_parts)
    
    def _solve_course_difficulty_semantically(self, semantic_query: SemanticQuery) -> str:
        """Solve course difficulty using semantic analysis"""
        
        course_codes = [e for e in semantic_query.entities if re.match(r'CS\s+\d{5}', e)]
        
        if not course_codes:
            # Use AI to generate response for missing course specification
            try:
                from intelligent_ai_response_generator import IntelligentAIResponseGenerator
                ai_gen = IntelligentAIResponseGenerator()
                return ai_gen.generate_response(
                    "The user asked about course difficulty but didn't specify which course. Ask them to clarify which course they want to know about.",
                    {"context": "course_difficulty_clarification", "available_courses": "CS courses"}
                )
            except:
                return "I'd be happy to help with course difficulty information. Could you specify which CS course you're asking about?"
        
        response_parts = []
        response_parts.append("🧠 SEMANTIC COURSE DIFFICULTY ANALYSIS")
        response_parts.append("=" * 45)
        response_parts.append("")
        
        for course_code in course_codes:
            if course_code not in self.course_nodes:
                response_parts.append(f"❌ {course_code}: Not found in knowledge graph")
                continue
            
            # Get course node and analyze connections
            course_node = self.course_nodes[course_code]
            prerequisites = course_node.connections
            
            response_parts.append(f"🎯 {course_code}:")
            response_parts.append(f"• Prerequisites: {len(prerequisites)}")
            
            # Calculate semantic difficulty
            difficulty_score = self._calculate_course_difficulty_semantically(course_code, prerequisites)
            response_parts.append(f"• Semantic difficulty: {difficulty_score:.2f}/10")
            
            # Analyze concept connections
            concept_connections = self._find_concept_connections(course_code)
            if concept_connections:
                response_parts.append("• Connected concepts:")
                for concept in concept_connections:
                    response_parts.append(f"  - {concept}")
            
            response_parts.append("")
        
        return "\n".join(response_parts)
    
    def _solve_course_planning_semantically(self, semantic_query: SemanticQuery) -> str:
        """Solve course planning using semantic understanding"""
        
        # Extract year information
        years = [e for e in semantic_query.entities if e in ["freshman", "sophomore", "junior", "senior"]]
        year = years[0] if years else None
        
        response_parts = []
        response_parts.append("🧠 SEMANTIC COURSE PLANNING")
        response_parts.append("=" * 35)
        response_parts.append("")
        
        if year:
            response_parts.append(f"📚 {year.upper()} YEAR SEMANTIC ANALYSIS:")
            response_parts.append("")
            
            # Find courses appropriate for this year
            year_courses = self._find_year_appropriate_courses(year)
            
            response_parts.append("🎯 KNOWLEDGE GRAPH RECOMMENDATIONS:")
            for course_code, reason in year_courses:
                response_parts.append(f"• {course_code}: {reason}")
            
            response_parts.append("")
            
            # Analyze semantic progression
            progression = self._analyze_semantic_progression(year_courses)
            response_parts.append("📈 SEMANTIC PROGRESSION:")
            response_parts.append(progression)
            
        else:
            response_parts.append("📊 GENERAL COURSE PLANNING ANALYSIS:")
            response_parts.append("")
            
            # Analyze all courses in knowledge graph
            foundation_courses = self._find_concept_courses("foundation_courses")
            advanced_courses = self._find_concept_courses("advanced_courses")
            
            response_parts.append(f"• Foundation courses: {len(foundation_courses)}")
            response_parts.append(f"• Advanced courses: {len(advanced_courses)}")
            response_parts.append("")
            
            response_parts.append("💡 SEMANTIC PLANNING PRINCIPLES:")
            response_parts.append("• Complete foundation concepts before advanced")
            response_parts.append("• Follow prerequisite chains in knowledge graph")
            response_parts.append("• Consider concept relationships between courses")
        
        return "\n".join(response_parts)
    
    def _solve_prerequisites_semantically(self, semantic_query: SemanticQuery) -> str:
        """Solve prerequisites using knowledge graph traversal"""
        
        course_codes = [e for e in semantic_query.entities if re.match(r'CS\s+\d{5}', e)]
        
        response_parts = []
        response_parts.append("🧠 SEMANTIC PREREQUISITE ANALYSIS")
        response_parts.append("=" * 40)
        response_parts.append("")
        
        for course_code in course_codes:
            if course_code not in self.course_nodes:
                response_parts.append(f"❌ {course_code}: Not in knowledge graph")
                continue
            
            # Find all prerequisites using graph traversal
            all_prereqs = self._find_all_prerequisites(course_code)
            direct_prereqs = self.course_nodes[course_code].connections
            
            response_parts.append(f"🎯 {course_code}:")
            response_parts.append(f"• Direct prerequisites: {len(direct_prereqs)}")
            response_parts.append(f"• Total prerequisite chain: {len(all_prereqs)}")
            
            if direct_prereqs:
                response_parts.append("• Direct requirements:")
                for prereq in direct_prereqs:
                    response_parts.append(f"  - {prereq}")
            
            # Find semantic relationships
            semantic_relations = self._find_semantic_relationships(course_code)
            if semantic_relations:
                response_parts.append("• Semantic relationships:")
                for relation in semantic_relations:
                    response_parts.append(f"  - {relation}")
            
            response_parts.append("")
        
        return "\n".join(response_parts)
    
    def _solve_career_guidance_semantically(self, semantic_query: SemanticQuery) -> str:
        """Solve career guidance using semantic analysis"""
        
        response_parts = []
        response_parts.append("🧠 SEMANTIC CAREER GUIDANCE")
        response_parts.append("=" * 35)
        response_parts.append("")
        
        # Analyze track concepts
        mi_courses = self._find_concept_courses("ai_ml_courses")
        se_courses = self._find_concept_courses("software_engineering_courses")
        
        response_parts.append("📊 KNOWLEDGE GRAPH CAREER ANALYSIS:")
        response_parts.append(f"• AI/ML focused courses: {len(mi_courses)}")
        response_parts.append(f"• Software Engineering courses: {len(se_courses)}")
        response_parts.append("")
        
        # Analyze concept connections
        response_parts.append("🔗 CONCEPT CONNECTIONS:")
        for course in mi_courses:
            connections = self._find_concept_connections(course)
            if connections:
                response_parts.append(f"• {course} connects to: {', '.join(connections)}")
        
        response_parts.append("")
        response_parts.append("💡 SEMANTIC CAREER PATHS:")
        response_parts.append("• AI/ML Engineer: Focus on machine learning concepts")
        response_parts.append("• Software Engineer: Focus on development concepts")
        response_parts.append("• Research Scientist: Combine both concept areas")
        
        return "\n".join(response_parts)
    
    def _solve_general_advice_dynamically(self, semantic_query: SemanticQuery) -> str:
        """Solve general queries using dynamic semantic understanding"""
        
        query_context = semantic_query.context
        original_query = " ".join(query_context.get("query_terms", []))
        
        # Analyze query for greeting patterns
        greeting_patterns = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]
        is_greeting = any(greeting in original_query.lower() for greeting in greeting_patterns)
        
        # Analyze query for help/capability requests
        help_patterns = ["help", "what can you", "what do you", "capabilities", "features", "how can", "assist"]
        is_help_request = any(pattern in original_query.lower() for pattern in help_patterns)
        
        # Analyze for specific academic interests
        has_cs_interest = "cs" in original_query.lower() or "computer science" in original_query.lower()
        has_purdue_interest = "purdue" in original_query.lower() or "boiler" in original_query.lower()
        
        response_parts = []
        
        # For any query (including greetings), use AI for proper course recommendations
        try:
            from ai_training_prompts import get_comprehensive_system_prompt
            import google.generativeai as genai
            import os
            
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                client = genai.GenerativeModel('models/gemini-2.5-flash')
                
                # Build context with knowledge graph insights
                total_courses = len(self.course_nodes)
                total_tracks = len(self.track_nodes)
                
                # Extract year information from the query
                year_info = ""
                track_selection_needed = False
                if "freshman" in original_query.lower():
                    year_info = "freshman year student"
                elif "sophomore" in original_query.lower():
                    year_info = "sophomore year student"
                elif "junior" in original_query.lower():
                    year_info = "junior year student"
                    track_selection_needed = True
                elif "senior" in original_query.lower():
                    year_info = "senior year student"
                    track_selection_needed = True
                
                # Get actual course data from knowledge base 
                year_courses = self._get_courses_for_year(year_info)
                
                # Build comprehensive context for the AI
                track_info = ""
                if track_selection_needed:
                    # Get track information from knowledge graph
                    track_details = []
                    for track_name, track_data in self.track_nodes.items():
                        if isinstance(track_data.content, dict):
                            required = track_data.content.get("required_courses", [])
                            track_details.append(f"- {track_name}: {', '.join(required[:3])}")
                    
                    track_info = f"""
                    
                    TRACK SELECTION NEEDED:
                    As a {year_info}, you need to choose a specialization track:
                    
                    Machine Intelligence Track:
                    - Core: CS 37300 (Data Mining), CS 38100 (Algorithms)
                    - AI Choice: CS 47100 (Machine Learning Theory) OR CS 47300 (Web Search - more applied)
                    - Stats Choice: STAT 41600, MA 41600, OR STAT 51200
                    - 2 electives from approved list
                    - Best for: AI research, data science careers, graduate school
                    
                    Software Engineering Track:
                    - Core: CS 30700 (Software Engineering I), CS 38100 (Algorithms), CS 40700 (Senior Project), CS 40800 (Testing)
                    - Systems Choice: CS 35200 (Compilers) OR CS 35400 (Operating Systems)
                    - 1 elective from approved list  
                    - Best for: Industry software development, large-scale systems
                    
                    IMPORTANT: Ask the user which track they prefer based on their career interests.
                    """
                
                context_info = f"""
                User Query: "{original_query}"
                Student Level: {year_info}
                Knowledge Base: {total_courses} CS courses and {total_tracks} tracks available
                Course Sequence from Knowledge Base:
                {year_courses}
                {track_info}
                Context: {query_context}
                
                IMPORTANT: Use only the actual course data from the knowledge base above. Provide specific semester recommendations.
                """
                
                system_prompt = get_comprehensive_system_prompt()
                response = client.generate_content(
                    ,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": context_info}
                    ],
                    ,
                    
                )
                
                ai_response = response.text.strip()
                if ai_response and len(ai_response) > 20:
                    return ai_response
        except Exception as e:
            self.logger.error(f"AI response generation failed: {e}")
            
        # Fallback response if AI fails
        if is_greeting:
            
            # Dynamic fallback (not hardcoded)
            response_parts.append("👋 Hello! I'm BoilerAI, your intelligent Purdue CS academic advisor.")
            response_parts.append("")
            
            # Dynamic knowledge graph insights
            total_courses = len(self.course_nodes)
            total_tracks = len(self.track_nodes)
            
            if total_courses > 0:
                response_parts.append(f"🎓 I have comprehensive knowledge of {total_courses} CS courses and can help you with:")
                response_parts.append("• Course planning and sequencing")
                response_parts.append("• Prerequisite analysis and degree pathways")
                if total_tracks > 0:
                    response_parts.append(f"• Track comparison ({total_tracks} tracks available)")
                response_parts.append("• CODO requirements and timeline planning")
                response_parts.append("• Career guidance and course recommendations")
                response_parts.append("")
                response_parts.append("💬 Try asking me something like:")
                response_parts.append("   'What courses should I take as a freshman?'")
                response_parts.append("   'How do I get into the CS program?'")
                response_parts.append("   'What's the difference between MI and SE tracks?'")
            else:
                response_parts.append("🔧 I'm currently loading my knowledge base. Ask me about Purdue CS courses, tracks, or planning!")
        
        elif is_help_request:
            response_parts.append("🤖 BoilerAI - Dynamic Academic Intelligence System")
            response_parts.append("")
            response_parts.append("🧠 INTELLIGENT CAPABILITIES:")
            response_parts.append("• Real-time course analysis and recommendations")
            response_parts.append("• Dynamic degree planning with prerequisite tracking")
            response_parts.append("• Intelligent track comparison and selection guidance")
            response_parts.append("• CODO timeline optimization")
            response_parts.append("• Career pathway analysis")
            response_parts.append("")
            response_parts.append("📊 KNOWLEDGE BASE STATUS:")
            response_parts.append(f"• Active course database: {len(self.course_nodes)} courses")
            response_parts.append(f"• Track information: {len(self.track_nodes)} academic tracks")
            response_parts.append(f"• Total knowledge nodes: {len(self.knowledge_graph)}")
            response_parts.append("")
            response_parts.append("💡 Just ask me natural questions about Purdue CS and I'll provide specific, intelligent answers!")
        
        else:
            # For other general queries, provide contextual response
            response_parts.append("🤔 I'm here to help with Purdue CS questions!")
            response_parts.append("")
            
            if has_cs_interest or has_purdue_interest:
                response_parts.append("🎓 Since you're interested in Purdue CS, I can help you with:")
                response_parts.append("• Understanding degree requirements")
                response_parts.append("• Planning your course sequence") 
                response_parts.append("• Choosing between tracks (MI vs SE)")
                response_parts.append("• CODO preparation and requirements")
                response_parts.append("")
                response_parts.append("What specific aspect would you like to know about?")
            else:
                response_parts.append("I specialize in Purdue Computer Science academic advising.")
                response_parts.append("Ask me about courses, degree planning, tracks, CODO requirements, or anything CS-related!")
                response_parts.append("")
                response_parts.append(f"📚 I currently have knowledge of {len(self.course_nodes)} courses and can provide detailed guidance.")
        
        return "\n".join(response_parts)
    
    def _calculate_semantic_complexity(self, courses: List[str]) -> float:
        """Calculate semantic complexity of course list"""
        if not courses:
            return 0.0
        
        complexity = 0.0
        for course in courses:
            if course in self.course_nodes:
                prereqs = len(self.course_nodes[course].connections)
                complexity += prereqs / 10.0
        
        return complexity / len(courses)
    
    def _calculate_course_difficulty_semantically(self, course: str, prerequisites: List[str]) -> float:
        """Calculate course difficulty using semantic analysis"""
        base_difficulty = 5.0
        
        # Adjust based on prerequisites
        if len(prerequisites) > 3:
            base_difficulty += 2.0
        elif len(prerequisites) > 1:
            base_difficulty += 1.0
        
        # Adjust based on course level
        if course and course.startswith("CS 3"):
            base_difficulty += 1.0
        elif course and course.startswith("CS 4"):
            base_difficulty += 2.0
        
        return min(10.0, max(1.0, base_difficulty))
    
    def _find_concept_connections(self, course: str) -> List[str]:
        """Find concept connections for a course"""
        connections = []
        for concept_name, concept_node in self.concept_nodes.items():
            if course in concept_node.connections:
                connections.append(concept_name)
        return connections
    
    def _find_year_appropriate_courses(self, year: str) -> List[Tuple[str, str]]:
        """Find courses appropriate for a given year"""
        courses = []
        
        if year == "freshman":
            foundation_courses = self._find_concept_courses("foundation_courses")
            for course in foundation_courses[:3]:
                courses.append((course, "Foundation course for first year"))
        
        elif year == "sophomore":
            foundation_courses = self._find_concept_courses("foundation_courses")
            for course in foundation_courses[3:6]:
                courses.append((course, "Core foundation course"))
        
        elif year == "junior":
            advanced_courses = self._find_concept_courses("advanced_courses")
            for course in advanced_courses[:2]:
                courses.append((course, "Advanced specialization course"))
        
        elif year == "senior":
            advanced_courses = self._find_concept_courses("advanced_courses")
            for course in advanced_courses[2:]:
                courses.append((course, "Senior-level specialization"))
        
        return courses
    
    def _find_concept_courses(self, concept: str) -> List[str]:
        """Find courses related to a concept"""
        if concept in self.concept_nodes:
            return self.concept_nodes[concept].connections
        return []
    
    def _analyze_semantic_progression(self, courses: List[Tuple[str, str]]) -> str:
        """Analyze semantic progression of courses"""
        if not courses:
            return "No courses to analyze"
        
        course_codes = [course[0] for course in courses]
        
        # Analyze prerequisite chains
        total_prereqs = 0
        for course in course_codes:
            if course in self.course_nodes:
                total_prereqs += len(self.course_nodes[course].connections)
        
        avg_prereqs = total_prereqs / len(course_codes) if course_codes else 0
        
        return f"Average prerequisites per course: {avg_prereqs:.1f}"
    
    def _find_all_prerequisites(self, course: str) -> List[str]:
        """Find all prerequisites using graph traversal"""
        all_prereqs = set()
        visited = set()
        
        def dfs(node):
            if node in visited:
                return
            visited.add(node)
            
            if node in self.course_nodes:
                for prereq in self.course_nodes[node].connections:
                    all_prereqs.add(prereq)
                    dfs(prereq)
        
        dfs(course)
        return list(all_prereqs)
    
    def _find_semantic_relationships(self, course: str) -> List[str]:
        """Find semantic relationships for a course"""
        relationships = []
        
        # Find concept relationships
        for concept_name, concept_node in self.concept_nodes.items():
            if course in concept_node.connections:
                relationships.append(f"Part of {concept_name} concept")
        
        # Find track relationships
        for track_name, track_node in self.track_nodes.items():
            required_courses = track_node.content.get("required_courses", [])
            if course in required_courses:
                relationships.append(f"Required for {track_name} track")
        
        return relationships

    def _get_courses_for_year(self, year_info: str) -> str:
        """Get actual courses for a specific year from the knowledge base"""
        
        year_courses = []
        
        if "freshman" in year_info.lower():
            # Get Fall 1st Year courses
            fall_courses = []
            spring_courses = []
            
            for course_code, course_data in self.course_nodes.items():
                if hasattr(course_data, 'content') and isinstance(course_data.content, dict):
                    semester = course_data.content.get('semester', '')
                    if semester == "Fall 1st Year":
                        title = course_data.content.get('title', course_code)
                        fall_courses.append(f"{course_code} ({title})")
                    elif semester == "Spring 1st Year":
                        title = course_data.content.get('title', course_code)
                        spring_courses.append(f"{course_code} ({title})")
            
            year_courses.append("Freshman Year:")
            if fall_courses:
                year_courses.append("- Fall 1st Year: " + ", ".join(fall_courses))
            if spring_courses:
                year_courses.append("- Spring 1st Year: " + ", ".join(spring_courses))
                
        elif "sophomore" in year_info.lower():
            # Get Fall 2nd Year and Spring 2nd Year courses
            fall_courses = []
            spring_courses = []
            
            for course_code, course_data in self.course_nodes.items():
                if hasattr(course_data, 'content') and isinstance(course_data.content, dict):
                    semester = course_data.content.get('semester', '')
                    if semester == "Fall 2nd Year":
                        title = course_data.content.get('title', course_code)
                        fall_courses.append(f"{course_code} ({title})")
                    elif semester == "Spring 2nd Year":
                        title = course_data.content.get('title', course_code)
                        spring_courses.append(f"{course_code} ({title})")
            
            year_courses.append("Sophomore Year:")
            if fall_courses:
                year_courses.append("- Fall 2nd Year: " + ", ".join(fall_courses))
            if spring_courses:
                year_courses.append("- Spring 2nd Year: " + ", ".join(spring_courses))
                
        elif "junior" in year_info.lower():
            # Get Fall 3rd Year courses if available
            fall_courses = []
            
            for course_code, course_data in self.course_nodes.items():
                if hasattr(course_data, 'content') and isinstance(course_data.content, dict):
                    semester = course_data.content.get('semester', '')
                    if semester == "Fall 3rd Year":
                        title = course_data.content.get('title', course_code)
                        fall_courses.append(f"{course_code} ({title})")
            
            year_courses.append("Junior Year:")
            if fall_courses:
                year_courses.append("- Fall 3rd Year: " + ", ".join(fall_courses))
            year_courses.append("- Track courses: CS 37300 (Data Mining), CS 30700 (Software Engineering I)")
            year_courses.append("- Upper level electives based on chosen track")
                
        elif "senior" in year_info.lower():
            year_courses.append("Senior Year:")
            year_courses.append("- Track-specific courses and electives")
            year_courses.append("- CS 40700 (Software Engineering Project) for SE track")
            year_courses.append("- CS 40800 (Testing) for SE track")
            year_courses.append("- Advanced electives based on chosen track")
        
        if not year_courses:
            return f"Course information for {year_info} not found in knowledge base."
            
        return "\n".join(year_courses) 