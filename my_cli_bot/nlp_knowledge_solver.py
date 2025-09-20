#!/usr/bin/env python3
"""
NLP Knowledge Solver
Uses proper NLP, knowledge graphs, and semantic understanding to solve problems
"""

import json
import re
import networkx as nx
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from collections import defaultdict
import spacy
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class KnowledgeNode:
    """Represents a knowledge node in the graph"""
    id: str
    type: str  # course, track, requirement, concept, etc.
    content: Dict[str, Any]
    embeddings: Optional[List[float]] = None
    connections: List[str] = None

@dataclass
class SemanticQuery:
    """Represents a semantic understanding of the query"""
    intent: str
    entities: List[str]
    concepts: List[str]
    relationships: List[Tuple[str, str, str]]  # (entity1, relation, entity2)
    context: Dict[str, Any]

class NLPKnowledgeSolver:
    """Solves problems using NLP, knowledge graphs, and semantic understanding"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.knowledge_graph = nx.DiGraph()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.course_embeddings = {}
        self.concept_embeddings = {}
        
        # Load NLP model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            self.logger.warning("spaCy model not available, using basic NLP")
            self.nlp = None
    
    def build_knowledge_graph(self, data: Dict[str, Any]):
        """Build knowledge graph from data"""
        self.logger.info("Building knowledge graph from data...")
        
        # Add course nodes
        courses = data.get("courses", {})
        for course_code, course_data in courses.items():
            node = KnowledgeNode(
                id=course_code,
                type="course",
                content=course_data,
                connections=[]
            )
            self.knowledge_graph.add_node(course_code, node=node)
        
        # Add track nodes
        tracks = data.get("track_requirements", {})
        for track_name, track_data in tracks.items():
            node = KnowledgeNode(
                id=track_name,
                type="track",
                content=track_data,
                connections=[]
            )
            self.knowledge_graph.add_node(track_name, node=node)
        
        # Add prerequisite relationships
        prerequisites = data.get("prerequisites", {})
        for course, prereqs in prerequisites.items():
            for prereq in prereqs:
                if course in self.knowledge_graph and prereq in self.knowledge_graph:
                    self.knowledge_graph.add_edge(prereq, course, relation="prerequisite")
        
        # Add track-course relationships
        for track_name, track_data in tracks.items():
            required_courses = track_data.get("required_courses", [])
            for course in required_courses:
                if course in self.knowledge_graph and track_name in self.knowledge_graph:
                    self.knowledge_graph.add_edge(course, track_name, relation="required_for")
        
        # Add concept nodes and relationships
        self._add_concept_nodes(data)
        
        self.logger.info(f"Knowledge graph built with {self.knowledge_graph.number_of_nodes()} nodes and {self.knowledge_graph.number_of_edges()} edges")
    
    def _add_concept_nodes(self, data: Dict[str, Any]):
        """Add conceptual knowledge nodes"""
        concepts = {
            "foundation_courses": ["CS 18000", "CS 18200", "CS 24000", "CS 25000", "CS 25100", "CS 25200"],
            "advanced_courses": ["CS 37300", "CS 38100", "CS 40700", "CS 40800"],
            "math_requirements": ["MA 16100", "MA 16200", "MA 26100", "MA 26500"],
            "ai_ml_courses": ["CS 37300", "CS 47100", "CS 47300"],
            "software_engineering_courses": ["CS 30700", "CS 40700", "CS 40800"],
            "dual_track": ["Machine Intelligence", "Software Engineering"]
        }
        
        for concept_name, related_items in concepts.items():
            node = KnowledgeNode(
                id=concept_name,
                type="concept",
                content={"related_items": related_items, "description": concept_name},
                connections=[]
            )
            self.knowledge_graph.add_node(concept_name, node=node)
            
            # Connect concept to related items
            for item in related_items:
                if item in self.knowledge_graph:
                    self.knowledge_graph.add_edge(concept_name, item, relation="contains")
    
    def understand_query_semantically(self, query: str) -> SemanticQuery:
        """Use NLP to understand query semantics"""
        self.logger.info(f"Performing semantic analysis of: {query}")
        
        # Extract entities using NLP
        entities = self._extract_entities(query)
        
        # Extract concepts
        concepts = self._extract_concepts(query)
        
        # Extract relationships
        relationships = self._extract_relationships(query)
        
        # Determine intent using semantic analysis
        intent = self._determine_semantic_intent(query, entities, concepts)
        
        # Build context
        context = self._build_semantic_context(query, entities, concepts)
        
        return SemanticQuery(
            intent=intent,
            entities=entities,
            concepts=concepts,
            relationships=relationships,
            context=context
        )
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract named entities using NLP"""
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
        
        # Use spaCy if available
        if self.nlp:
            doc = self.nlp(query)
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PRODUCT', 'GPE']:
                    entities.append(ent.text)
        
        return list(set(entities))
    
    def _extract_concepts(self, query: str) -> List[str]:
        """Extract conceptual knowledge from query"""
        concepts = []
        query_lower = query.lower()
        
        # Map query to concepts
        concept_mapping = {
            "difficulty": ["hard", "difficult", "challenging", "easy", "workload"],
            "planning": ["plan", "schedule", "timeline", "graduation"],
            "prerequisites": ["prereq", "requirement", "before", "need"],
            "career": ["job", "career", "industry", "work"],
            "dual_track": ["both", "dual", "two tracks", "combine"],
            "foundation": ["foundation", "basic", "intro", "first"],
            "advanced": ["advanced", "upper", "senior", "specialized"]
        }
        
        for concept, keywords in concept_mapping.items():
            if any(keyword in query_lower for keyword in keywords):
                concepts.append(concept)
        
        return concepts
    
    def _extract_relationships(self, query: str) -> List[Tuple[str, str, str]]:
        """Extract relationships between entities"""
        relationships = []
        query_lower = query.lower()
        
        # Extract prerequisite relationships
        if "prerequisite" in query_lower or "need" in query_lower:
            course_codes = re.findall(r'CS\s+\d{5}', query)
            if len(course_codes) >= 2:
                relationships.append((course_codes[0], "requires", course_codes[1]))
        
        # Extract track relationships
        if "track" in query_lower:
            tracks = re.findall(r'\b(machine intelligence|software engineering)\b', query_lower)
            if len(tracks) >= 2:
                relationships.append((tracks[0], "combines_with", tracks[1]))
        
        return relationships
    
    def _determine_semantic_intent(self, query: str, entities: List[str], concepts: List[str]) -> str:
        """Determine intent using semantic analysis"""
        query_lower = query.lower()
        
        # Use concept-based intent detection
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
        elif "advanced" in concepts:
            return "advanced_planning"
        else:
            return "general_advice"
    
    def _build_semantic_context(self, query: str, entities: List[str], concepts: List[str]) -> Dict[str, Any]:
        """Build semantic context for the query"""
        context = {
            "entities": entities,
            "concepts": concepts,
            "query_terms": query.lower().split(),
            "has_course_codes": bool(re.search(r'CS\s+\d{5}', query)),
            "has_tracks": bool(re.search(r'\b(machine intelligence|software engineering)\b', query.lower())),
            "has_years": bool(re.search(r'\b(freshman|sophomore|junior|senior)\b', query.lower())),
            "is_dual_track": "both" in query.lower() or "dual" in query.lower()
        }
        return context
    
    def solve_using_knowledge_graph(self, semantic_query: SemanticQuery) -> str:
        """Solve the problem using knowledge graph traversal and semantic understanding"""
        self.logger.info(f"Solving using knowledge graph for intent: {semantic_query.intent}")
        
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
        else:
            return self._solve_general_semantically(semantic_query)
    
    def _solve_dual_track_semantically(self, semantic_query: SemanticQuery) -> str:
        """Solve dual track planning using knowledge graph analysis"""
        
        # Find track nodes
        mi_track = None
        se_track = None
        for node_id in self.knowledge_graph.nodes():
            node_data = self.knowledge_graph.nodes[node_id].get('node')
            if node_data and node_data.type == "track":
                if "machine intelligence" in node_id.lower():
                    mi_track = node_data
                elif "software engineering" in node_id.lower():
                    se_track = node_data
        
        if not mi_track or not se_track:
            return "Track information not available in knowledge base."
        
        # Analyze requirements using graph traversal
        mi_courses = self._get_track_courses(mi_track.id)
        se_courses = self._get_track_courses(se_track.id)
        
        # Find overlapping courses
        overlapping = set(mi_courses) & set(se_courses)
        unique_mi = set(mi_courses) - set(se_courses)
        unique_se = set(se_courses) - set(mi_courses)
        
        # Build semantic response
        response_parts = []
        response_parts.append("🎯 SEMANTIC DUAL TRACK ANALYSIS")
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
            return "Please specify which course you're asking about."
        
        response_parts = []
        response_parts.append("🧠 SEMANTIC COURSE DIFFICULTY ANALYSIS")
        response_parts.append("=" * 45)
        response_parts.append("")
        
        for course_code in course_codes:
            if course_code not in self.knowledge_graph:
                response_parts.append(f"❌ {course_code}: Not found in knowledge graph")
                continue
            
            # Get course node and analyze connections
            course_node = self.knowledge_graph.nodes[course_code]['node']
            prerequisites = list(self.knowledge_graph.predecessors(course_code))
            dependents = list(self.knowledge_graph.successors(course_code))
            
            response_parts.append(f"🎯 {course_code}:")
            response_parts.append(f"• Prerequisites: {len(prerequisites)}")
            response_parts.append(f"• Required by: {len(dependents)} courses")
            
            # Calculate semantic difficulty
            difficulty_score = self._calculate_course_difficulty_semantically(course_code, prerequisites, dependents)
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
            
            # Find courses appropriate for this year using knowledge graph
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
            if course_code not in self.knowledge_graph:
                response_parts.append(f"❌ {course_code}: Not in knowledge graph")
                continue
            
            # Find all prerequisites using graph traversal
            all_prereqs = self._find_all_prerequisites(course_code)
            direct_prereqs = list(self.knowledge_graph.predecessors(course_code))
            
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
    
    def _solve_general_semantically(self, semantic_query: SemanticQuery) -> str:
        """Solve general queries using semantic understanding"""
        
        response_parts = []
        response_parts.append("🧠 SEMANTIC ACADEMIC ADVISING")
        response_parts.append("=" * 35)
        response_parts.append("")
        
        response_parts.append("📊 KNOWLEDGE GRAPH OVERVIEW:")
        response_parts.append(f"• Total nodes: {self.knowledge_graph.number_of_nodes()}")
        response_parts.append(f"• Total connections: {self.knowledge_graph.number_of_edges()}")
        response_parts.append(f"• Course nodes: {len([n for n in self.knowledge_graph.nodes() if self.knowledge_graph.nodes[n].get('node', {}).type == 'course'])}")
        response_parts.append(f"• Track nodes: {len([n for n in self.knowledge_graph.nodes() if self.knowledge_graph.nodes[n].get('node', {}).type == 'track'])}")
        response_parts.append("")
        
        response_parts.append("💡 SEMANTIC CAPABILITIES:")
        response_parts.append("• Course difficulty analysis using graph connections")
        response_parts.append("• Prerequisite chain traversal")
        response_parts.append("• Track requirement analysis")
        response_parts.append("• Concept relationship mapping")
        response_parts.append("• Dual track feasibility assessment")
        
        return "\n".join(response_parts)
    
    def _get_track_courses(self, track_id: str) -> List[str]:
        """Get courses for a track using graph traversal"""
        courses = []
        for successor in self.knowledge_graph.successors(track_id):
            edge_data = self.knowledge_graph.get_edge_data(track_id, successor)
            if edge_data.get('relation') == 'required_for':
                courses.append(successor)
        return courses
    
    def _calculate_semantic_complexity(self, courses: List[str]) -> float:
        """Calculate semantic complexity of course list"""
        if not courses:
            return 0.0
        
        complexity = 0.0
        for course in courses:
            if course in self.knowledge_graph:
                # Count prerequisites and dependents
                prereqs = len(list(self.knowledge_graph.predecessors(course)))
                dependents = len(list(self.knowledge_graph.successors(course)))
                complexity += (prereqs + dependents) / 10.0
        
        return complexity / len(courses)
    
    def _calculate_course_difficulty_semantically(self, course: str, prerequisites: List[str], dependents: List[str]) -> float:
        """Calculate course difficulty using semantic analysis"""
        base_difficulty = 5.0
        
        # Adjust based on prerequisites
        if len(prerequisites) > 3:
            base_difficulty += 2.0
        elif len(prerequisites) > 1:
            base_difficulty += 1.0
        
        # Adjust based on how many courses depend on this
        if len(dependents) > 5:
            base_difficulty += 1.0  # Important course
        
        # Adjust based on course level
        if course and course.startswith("CS 3"):
            base_difficulty += 1.0
        elif course and course.startswith("CS 4"):
            base_difficulty += 2.0
        
        return min(10.0, max(1.0, base_difficulty))
    
    def _find_concept_connections(self, course: str) -> List[str]:
        """Find concept connections for a course"""
        connections = []
        for predecessor in self.knowledge_graph.predecessors(course):
            node_data = self.knowledge_graph.nodes[predecessor].get('node')
            if node_data and node_data.type == "concept":
                connections.append(predecessor)
        return connections
    
    def _find_year_appropriate_courses(self, year: str) -> List[Tuple[str, str]]:
        """Find courses appropriate for a given year"""
        courses = []
        
        if year == "freshman":
            foundation_courses = self._find_concept_courses("foundation_courses")
            for course in foundation_courses[:3]:  # First 3 foundation courses
                courses.append((course, "Foundation course for first year"))
        
        elif year == "sophomore":
            foundation_courses = self._find_concept_courses("foundation_courses")
            for course in foundation_courses[3:6]:  # Next 3 foundation courses
                courses.append((course, "Core foundation course"))
        
        elif year == "junior":
            advanced_courses = self._find_concept_courses("advanced_courses")
            for course in advanced_courses[:2]:  # First 2 advanced courses
                courses.append((course, "Advanced specialization course"))
        
        elif year == "senior":
            advanced_courses = self._find_concept_courses("advanced_courses")
            for course in advanced_courses[2:]:  # Remaining advanced courses
                courses.append((course, "Senior-level specialization"))
        
        return courses
    
    def _find_concept_courses(self, concept: str) -> List[str]:
        """Find courses related to a concept"""
        courses = []
        if concept in self.knowledge_graph:
            for successor in self.knowledge_graph.successors(concept):
                edge_data = self.knowledge_graph.get_edge_data(concept, successor)
                if edge_data.get('relation') == 'contains':
                    courses.append(successor)
        return courses
    
    def _analyze_semantic_progression(self, courses: List[Tuple[str, str]]) -> str:
        """Analyze semantic progression of courses"""
        if not courses:
            return "No courses to analyze"
        
        course_codes = [course[0] for course in courses]
        
        # Analyze prerequisite chains
        total_prereqs = 0
        for course in course_codes:
            if course in self.knowledge_graph:
                total_prereqs += len(list(self.knowledge_graph.predecessors(course)))
        
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
            
            for predecessor in self.knowledge_graph.predecessors(node):
                edge_data = self.knowledge_graph.get_edge_data(predecessor, node)
                if edge_data.get('relation') == 'prerequisite':
                    all_prereqs.add(predecessor)
                    dfs(predecessor)
        
        dfs(course)
        return list(all_prereqs)
    
    def _find_semantic_relationships(self, course: str) -> List[str]:
        """Find semantic relationships for a course"""
        relationships = []
        
        # Find concept relationships
        for predecessor in self.knowledge_graph.predecessors(course):
            node_data = self.knowledge_graph.nodes[predecessor].get('node')
            if node_data and node_data.type == "concept":
                relationships.append(f"Part of {predecessor} concept")
        
        # Find track relationships
        for successor in self.knowledge_graph.successors(course):
            node_data = self.knowledge_graph.nodes[successor].get('node')
            if node_data and node_data.type == "track":
                relationships.append(f"Required for {successor} track")
        
        return relationships 