#!/usr/bin/env python3
"""
Unified AI Query Engine - Final Solution for BoilerAI
Consolidates all AI components into a single, intelligent query processing engine
Solves the query understanding and knowledge base retrieval issues completely
"""

import json
import logging
import time
import os
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re
import google.generativeai as genai

# Import all existing components
from enhanced_n8n_integration import EnhancedN8NIntegration
from smart_ai_engine import SmartAIEngine
from simple_nlp_solver import SimpleNLPSolver
from comprehensive_failure_analyzer import ComprehensiveFailureAnalyzer
from ai_training_prompts import get_comprehensive_system_prompt

class QueryComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    SPECIALIZED = "specialized"

@dataclass
class UnifiedQueryResult:
    """Unified result from query processing"""
    query: str
    response: str
    confidence: float
    complexity: QueryComplexity
    processing_method: str
    entities_extracted: Dict[str, Any]
    knowledge_sources: List[str]
    processing_time: float
    session_id: str
    metadata: Dict[str, Any]

class UnifiedAIQueryEngine:
    """
    Unified AI Query Engine that solves all query understanding and knowledge base issues
    Single point of entry for all query processing with intelligent routing
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        
        # Initialize all components
        self.enhanced_n8n = EnhancedN8NIntegration()
        self.smart_ai = SmartAIEngine()
        self.nlp_solver = SimpleNLPSolver()
        self.failure_analyzer = ComprehensiveFailureAnalyzer()
        
        # Gemini client for advanced processing
        self.gemini_model = None
        self._init_Gemini()
        
        # Load unified knowledge base
        self.unified_knowledge = self._load_unified_knowledge()
        
        # Query routing intelligence
        self.routing_rules = self._initialize_routing_rules()
        
        # Performance tracking
        self.query_stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "avg_processing_time": 0.0,
            "method_usage": {}
        }
        
        self.logger.info("Unified AI Query Engine initialized successfully")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('unified_ai_query_engine.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _init_Gemini(self):
        """Initialize Gemini client"""
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            try:
                # Configure safety settings
                safety_settings = [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
                ]
                self.gemini_model = genai.GenerativeModel('models/gemini-2.5-flash', safety_settings=safety_settings)
                self.logger.info("Gemini client initialized")
            except Exception as e:
                self.logger.warning(f"Gemini initialization failed: {e}")
    
    def _load_unified_knowledge(self) -> Dict[str, Any]:
        """Load unified knowledge base from all sources"""
        unified_knowledge = {
            "courses": {},
            "tracks": {},
            "prerequisites": {},
            "degree_requirements": {},
            "codo_requirements": {},
            "graduation_timelines": {},
            "failure_recovery": {},
            "academic_policies": {}
        }
        
        # Load from multiple sources
        knowledge_files = [
            "data/cs_knowledge_graph.json",
            "data/comprehensive_purdue_cs_data.json"
        ]
        
        for knowledge_file in knowledge_files:
            try:
                if os.path.exists(knowledge_file):
                    with open(knowledge_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Merge data intelligently
                    for key in unified_knowledge.keys():
                        if key in data:
                            if isinstance(data[key], dict):
                                unified_knowledge[key].update(data[key])
                            else:
                                unified_knowledge[key] = data[key]
                    
                    self.logger.info(f"Loaded knowledge from {knowledge_file}")
            except Exception as e:
                self.logger.error(f"Error loading {knowledge_file}: {e}")
        
        # Build knowledge graph for NLP solver
        self.nlp_solver.build_knowledge_graph(unified_knowledge)
        
        return unified_knowledge
    
    def _initialize_routing_rules(self) -> Dict[str, Any]:
        """Initialize intelligent query routing rules"""
        return {
            "failure_analysis": {
                "keywords": ["fail", "failing", "failed", "failure", "retake", "summer", "delay"],
                "course_patterns": [r'cs\s*\d{5}', r'ma\s*\d{5}', r'calc\s*\d?', r'linear'],
                "method": "failure_analyzer",
                "priority": 1
            },
            "course_planning": {
                "keywords": ["course", "semester", "year", "plan", "schedule", "take"],
                "patterns": [r'freshman|sophomore|junior|senior', r'what.*should.*take'],
                "method": "smart_ai_enhanced",
                "priority": 2
            },
            "track_selection": {
                "keywords": ["track", "machine intelligence", "software engineering", "mi", "se", "both", "dual"],
                "patterns": [r'both.*track', r'dual.*track', r'choose.*track'],
                "method": "nlp_solver_enhanced",
                "priority": 2
            },
            "prerequisites": {
                "keywords": ["prerequisite", "prereq", "before", "requirement", "need", "able to take"],
                "patterns": [r'prerequisite.*for', r'before.*taking', r'can.*take'],
                "method": "smart_ai_enhanced",
                "priority": 2
            },
            "graduation_planning": {
                "keywords": ["graduate", "graduation", "timeline", "early", "accelerated", "finish"],
                "patterns": [r'graduate.*early', r'graduation.*plan', r'\d.*year.*plan'],
                "method": "comprehensive_ai",
                "priority": 2
            },
            "codo_inquiry": {
                "keywords": ["codo", "change major", "transfer", "switch", "into cs"],
                "patterns": [r'change.*major', r'transfer.*cs', r'codo.*requirement'],
                "method": "smart_ai_enhanced",
                "priority": 2
            },
            "general_greeting": {
                "keywords": ["hi", "hello", "hey", "help", "what can", "greetings"],
                "patterns": [r'^(hi|hello|hey)', r'what can you', r'how can you help'],
                "method": "comprehensive_ai",
                "priority": 3
            }
        }
    
    def analyze_query_complexity(self, query: str) -> QueryComplexity:
        """Analyze query complexity for intelligent routing"""
        query_lower = query.lower()
        
        # Count entities and keywords
        entity_count = len(re.findall(r'cs\s*\d{5}|ma\s*\d{5}', query_lower))
        keyword_count = sum(1 for rule in self.routing_rules.values() 
                          for keyword in rule["keywords"] 
                          if keyword in query_lower)
        
        # Check for complex patterns
        has_multiple_concepts = len(query.split()) > 10
        has_conditional_logic = any(word in query_lower for word in ["if", "when", "what happens", "suppose"])
        has_multiple_courses = entity_count > 2
        
        if any(word in query_lower for word in ["fail", "failure"]) and entity_count > 0:
            return QueryComplexity.SPECIALIZED
        elif has_multiple_concepts or has_conditional_logic or has_multiple_courses:
            return QueryComplexity.COMPLEX
        elif keyword_count > 2 or entity_count > 0:
            return QueryComplexity.MODERATE
        else:
            return QueryComplexity.SIMPLE
    
    def determine_best_method(self, query: str, complexity: QueryComplexity) -> str:
        """Determine the best processing method for the query"""
        query_lower = query.lower()
        
        # Check routing rules by priority
        matching_rules = []
        for rule_name, rule_config in self.routing_rules.items():
            score = 0
            
            # Check keywords
            keyword_matches = sum(1 for keyword in rule_config["keywords"] if keyword in query_lower)
            score += keyword_matches * 2
            
            # Check patterns
            pattern_matches = sum(1 for pattern in rule_config.get("patterns", []) 
                                if re.search(pattern, query_lower))
            score += pattern_matches * 3
            
            if score > 0:
                matching_rules.append((rule_name, score, rule_config["method"], rule_config["priority"]))
        
        # Sort by score and priority
        matching_rules.sort(key=lambda x: (-x[1], x[3]))
        
        if matching_rules:
            return matching_rules[0][2]
        
        # Default method based on complexity
        if complexity == QueryComplexity.SPECIALIZED:
            return "failure_analyzer"
        elif complexity == QueryComplexity.COMPLEX:
            return "comprehensive_ai"
        elif complexity == QueryComplexity.MODERATE:
            return "smart_ai_enhanced"
        else:
            return "nlp_solver_enhanced"
    
    def process_query(self, 
                     query: str, 
                     session_id: str = None,
                     context: Dict[str, Any] = None) -> UnifiedQueryResult:
        """Main unified query processing method"""
        
        start_time = time.time()
        session_id = session_id or f"unified_{int(time.time())}"
        context = context or {}
        
        self.logger.info(f"Processing unified query: {query[:50]}...")
        
        try:
            # Step 1: Analyze query complexity
            complexity = self.analyze_query_complexity(query)
            
            # Step 2: Determine best processing method
            method = self.determine_best_method(query, complexity)
            
            # Step 3: Extract entities using all available methods
            entities = self._extract_comprehensive_entities(query)
            
            # Step 4: Process query using selected method
            response, knowledge_sources = self._process_with_method(query, method, entities, context)
            
            # Step 5: Post-process and enhance response
            response = self._enhance_response(response, query, entities, method)
            
            # Step 6: Calculate processing metrics
            processing_time = time.time() - start_time
            confidence = self._calculate_confidence(method, entities, len(response))
            
            # Step 7: Update statistics
            self._update_statistics(method, processing_time, True)
            
            # Step 8: Create unified result
            result = UnifiedQueryResult(
                query=query,
                response=response,
                confidence=confidence,
                complexity=complexity,
                processing_method=method,
                entities_extracted=entities,
                knowledge_sources=knowledge_sources,
                processing_time=processing_time,
                session_id=session_id,
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "context": context,
                    "stats": self.query_stats
                }
            )
            
            self.logger.info(f"Query processed successfully using {method} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Unified query processing failed: {e}")
            processing_time = time.time() - start_time
            self._update_statistics("error", processing_time, False)
            
            # Return error result
            return UnifiedQueryResult(
                query=query,
                response=f"I encountered an error processing your query. Please try rephrasing: {str(e)}",
                confidence=0.0,
                complexity=QueryComplexity.SIMPLE,
                processing_method="error_handler",
                entities_extracted={},
                knowledge_sources=[],
                processing_time=processing_time,
                session_id=session_id,
                metadata={"error": str(e)}
            )
    
    def _extract_comprehensive_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities using all available methods"""
        entities = {
            "course_codes": [],
            "academic_years": [],
            "tracks": [],
            "keywords": [],
            "numbers": [],
            "concepts": []
        }
        
        try:
            # Use smart AI engine
            smart_intent = self.smart_ai.understand_query(query)
            entities.update(smart_intent.entities)
            entities["concepts"].extend(smart_intent.specific_topics)
        except Exception as e:
            self.logger.warning(f"Smart AI entity extraction failed: {e}")
        
        try:
            # Use NLP solver
            semantic_query = self.nlp_solver.understand_query_semantically(query)
            entities["course_codes"].extend(semantic_query.entities)
            entities["concepts"].extend(semantic_query.concepts)
        except Exception as e:
            self.logger.warning(f"NLP entity extraction failed: {e}")
        
        try:
            # Use failure analyzer for course codes
            courses = self.failure_analyzer.normalize_course_code(query)
            entities["course_codes"].extend(courses)
        except Exception as e:
            self.logger.warning(f"Failure analyzer entity extraction failed: {e}")
        
        # Remove duplicates
        for key, value in entities.items():
            if isinstance(value, list):
                entities[key] = list(set(value))
        
        return entities
    
    def _process_with_method(self, 
                           query: str, 
                           method: str, 
                           entities: Dict[str, Any], 
                           context: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Process query with the selected method"""
        
        knowledge_sources = []
        
        if method == "failure_analyzer":
            response = self.failure_analyzer.analyze_failure_query(query)
            knowledge_sources = ["failure_scenarios", "course_schedules"]
        
        elif method == "smart_ai_enhanced":
            try:
                intent = self.smart_ai.understand_query(query, context)
                data = self.smart_ai.fetch_relevant_data(intent)
                response = self.smart_ai.generate_accurate_response(query, intent, data, context)
                knowledge_sources = ["smart_ai_knowledge_base", "course_catalog"]
            except Exception as e:
                self.logger.error(f"Smart AI enhanced processing failed: {e}")
                response = self._fallback_to_nlp(query)
                knowledge_sources = ["nlp_fallback"]
        
        elif method == "nlp_solver_enhanced":
            try:
                semantic_query = self.nlp_solver.understand_query_semantically(query)
                response = self.nlp_solver.solve_using_knowledge_graph(semantic_query)
                knowledge_sources = ["knowledge_graph", "semantic_analysis"]
            except Exception as e:
                self.logger.error(f"NLP solver enhanced processing failed: {e}")
                response = self._fallback_to_smart_ai(query, context)
                knowledge_sources = ["smart_ai_fallback"]
        
        elif method == "comprehensive_ai":
            response = self._process_with_comprehensive_ai(query, entities, context)
            knowledge_sources = ["Gemini_Gemini", "unified_knowledge_base"]
        
        else:
            # Default fallback
            response = self._fallback_to_nlp(query)
            knowledge_sources = ["default_fallback"]
        
        return response, knowledge_sources
    
    def _process_with_comprehensive_ai(self, 
                                     query: str, 
                                     entities: Dict[str, Any], 
                                     context: Dict[str, Any]) -> str:
        """Process using comprehensive AI with Gemini integration"""
        
        if not self.gemini_model:
            return self._fallback_to_smart_ai(query, context)
        
        try:
            # Build comprehensive context
            context_parts = []
            context_parts.append(f"Query: {query}")
            context_parts.append(f"Extracted entities: {json.dumps(entities)}")
            
            # Add relevant knowledge
            if entities.get("course_codes"):
                for course in entities["course_codes"]:
                    if course in self.unified_knowledge.get("courses", {}):
                        course_info = self.unified_knowledge["courses"][course]
                        context_parts.append(f"Course {course}: {json.dumps(course_info)}")
            
            if entities.get("tracks"):
                context_parts.append(f"Track data: {json.dumps(self.unified_knowledge.get('tracks', {}))}")
            
            # Add CODO requirements if relevant
            if any(word in query.lower() for word in ["codo", "change major", "transfer"]):
                context_parts.append(f"CODO requirements: {json.dumps(self.unified_knowledge.get('codo_requirements', {}))}")
            
            context_text = "\n".join(context_parts)
            
            # Generate response using Gemini
            system_prompt = get_comprehensive_system_prompt()
            
            response = self.gemini_model.generate_content(
                ,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context_text}
                ],
                ,
                
            )
            
            return response.text.strip()
            
        except Exception as e:
            self.logger.error(f"Comprehensive AI processing failed: {e}")
            return self._fallback_to_smart_ai(query, context)
    
    def _fallback_to_nlp(self, query: str) -> str:
        """Fallback to NLP solver"""
        try:
            semantic_query = self.nlp_solver.understand_query_semantically(query)
            return self.nlp_solver.solve_using_knowledge_graph(semantic_query)
        except Exception as e:
            self.logger.error(f"NLP fallback failed: {e}")
            return "I'm having trouble processing your query. Please try rephrasing your question."
    
    def _fallback_to_smart_ai(self, query: str, context: Dict[str, Any]) -> str:
        """Fallback to smart AI engine"""
        try:
            return self.smart_ai.process_query(query, context)
        except Exception as e:
            self.logger.error(f"Smart AI fallback failed: {e}")
            return self._fallback_to_nlp(query)
    
    def _enhance_response(self, 
                         response: str, 
                         query: str, 
                         entities: Dict[str, Any], 
                         method: str) -> str:
        """Enhance response with additional context if needed"""
        
        # Add helpful follow-up suggestions for certain query types
        if "track" in query.lower() and len(response) < 200:
            response += "\n\nWould you like more details about specific track requirements or career paths?"
        
        elif entities.get("course_codes") and "prerequisite" not in query.lower():
            response += "\n\nNeed information about prerequisites or course scheduling?"
        
        elif any(word in query.lower() for word in ["freshman", "sophomore"]) and len(response) < 300:
            response += "\n\nI can also help with graduation planning and track selection when you're ready!"
        
        return response
    
    def _calculate_confidence(self, method: str, entities: Dict[str, Any], response_length: int) -> float:
        """Calculate confidence score for the response"""
        base_confidence = 0.7
        
        # Method-based confidence
        method_confidence = {
            "failure_analyzer": 0.9,
            "comprehensive_ai": 0.85,
            "smart_ai_enhanced": 0.8,
            "nlp_solver_enhanced": 0.75
        }
        
        confidence = method_confidence.get(method, base_confidence)
        
        # Adjust based on entities found
        if entities.get("course_codes"):
            confidence += 0.1
        if entities.get("tracks"):
            confidence += 0.05
        
        # Adjust based on response quality
        if response_length > 100:
            confidence += 0.05
        if response_length > 300:
            confidence += 0.05
        
        return min(1.0, confidence)
    
    def _update_statistics(self, method: str, processing_time: float, success: bool):
        """Update processing statistics"""
        self.query_stats["total_queries"] += 1
        
        if success:
            self.query_stats["successful_queries"] += 1
        
        # Update average processing time
        total_time = self.query_stats["avg_processing_time"] * (self.query_stats["total_queries"] - 1)
        self.query_stats["avg_processing_time"] = (total_time + processing_time) / self.query_stats["total_queries"]
        
        # Update method usage
        if method not in self.query_stats["method_usage"]:
            self.query_stats["method_usage"][method] = 0
        self.query_stats["method_usage"][method] += 1
    
    def get_response_only(self, query: str, session_id: str = None, context: Dict[str, Any] = None) -> str:
        """Get only the response text (for backward compatibility)"""
        result = self.process_query(query, session_id, context)
        return result.response
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            "query_stats": self.query_stats,
            "knowledge_base": {
                "courses": len(self.unified_knowledge.get("courses", {})),
                "tracks": len(self.unified_knowledge.get("tracks", {})),
                "total_nodes": sum(len(v) if isinstance(v, dict) else 1 
                                 for v in self.unified_knowledge.values())
            },
            "components": {
                "enhanced_n8n": "active",
                "smart_ai": "active",
                "nlp_solver": "active",
                "failure_analyzer": "active",
                "gemini_model": "active" if self.gemini_model else "inactive"
            }
        }

# Global instance for easy access
_unified_engine = None

def get_unified_engine() -> UnifiedAIQueryEngine:
    """Get global unified engine instance"""
    global _unified_engine
    if _unified_engine is None:
        _unified_engine = UnifiedAIQueryEngine()
    return _unified_engine

def process_query_unified(query: str, session_id: str = None, context: Dict[str, Any] = None) -> str:
    """Simple function for processing queries (backward compatibility)"""
    engine = get_unified_engine()
    return engine.get_response_only(query, session_id, context)

# Test function
def test_unified_engine():
    """Test the unified AI query engine"""
    engine = UnifiedAIQueryEngine()
    
    test_queries = [
        "Hi, I'm a freshman, what courses should I take?",
        "I failed CS 25100, what happens to my graduation timeline?",
        "Tell me about both Machine Intelligence and Software Engineering tracks",
        "What are the prerequisites for CS 37300?",
        "How do I get into the CS program through CODO?",
        "Can I graduate early with a dual track?",
        "What happens if I fail calculus 1 in my first semester?"
    ]
    
    print("🧪 Testing Unified AI Query Engine")
    print("=" * 70)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 50)
        
        result = engine.process_query(query)
        
        print(f"Method: {result.processing_method}")
        print(f"Complexity: {result.complexity.value}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Time: {result.processing_time:.2f}s")
        print(f"Entities: {list(result.entities_extracted.keys())}")
        print(f"Response: {result.response[:200]}...")
        print("=" * 70)
    
    # Show system statistics
    print(f"\n📊 System Statistics:")
    stats = engine.get_system_statistics()
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    test_unified_engine()