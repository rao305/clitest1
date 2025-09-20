#!/usr/bin/env python3
"""
Enhanced N8N Pipeline Integration for BoilerAI
Solves AI query understanding and knowledge base integration issues
Creates a unified, robust pipeline that processes queries intelligently
"""

import json
import os
import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import sqlite3
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import hashlib

# Import existing components
from smart_ai_engine import SmartAIEngine, QueryIntent
from simple_nlp_solver import SimpleNLPSolver, SemanticQuery
from comprehensive_failure_analyzer import ComprehensiveFailureAnalyzer
from n8n_style_pipeline import N8NStylePipeline

class PipelineStatus(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SYNCHRONIZING = "synchronizing"

@dataclass
class EnhancedQueryContext:
    """Enhanced context for query processing"""
    session_id: str
    user_id: Optional[str]
    query: str
    timestamp: datetime
    previous_queries: List[str]
    extracted_entities: Dict[str, Any]
    intent_confidence: float
    knowledge_sources_used: List[str]
    processing_time: float
    cache_key: str

@dataclass
class N8NWorkflowResult:
    """Result from N8N workflow execution"""
    workflow_id: str
    status: PipelineStatus
    data: Dict[str, Any]
    execution_time: float
    errors: List[str]
    metadata: Dict[str, Any]

class EnhancedN8NIntegration:
    """Enhanced N8N Integration that solves AI query and knowledge base issues"""
    
    def __init__(self, 
                 n8n_webhook_url: str = "http://localhost:5678/webhook/boilerai",
                 knowledge_sync_interval: int = 300):
        
        self.logger = self._setup_logging()
        self.n8n_webhook_url = n8n_webhook_url
        self.knowledge_sync_interval = knowledge_sync_interval
        
        # Initialize unified components
        self.smart_ai_engine = SmartAIEngine()
        self.nlp_solver = SimpleNLPSolver()
        self.failure_analyzer = ComprehensiveFailureAnalyzer()
        self.n8n_pipeline = N8NStylePipeline()
        
        # Enhanced caching and synchronization
        self.query_cache = {}
        self.knowledge_cache = {}
        self.last_sync_time = datetime.now()
        self.cache_ttl = timedelta(minutes=15)
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Knowledge base synchronization
        self.knowledge_sources = {
            "cs_knowledge_graph": "data/cs_knowledge_graph.json",
            "comprehensive_data": "data/comprehensive_purdue_cs_data.json",
            "conversation_contexts": "conversation_contexts.json"
        }
        
        # Initialize unified knowledge base
        self._initialize_unified_knowledge_base()
        
        # Start background synchronization
        self.sync_thread = threading.Thread(target=self._background_sync, daemon=True)
        self.sync_thread.start()
        
        self.logger.info("Enhanced N8N Integration initialized successfully")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('enhanced_n8n_integration.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _initialize_unified_knowledge_base(self):
        """Initialize unified knowledge base from all sources"""
        self.logger.info("Initializing unified knowledge base...")
        
        unified_data = {
            "courses": {},
            "tracks": {},
            "prerequisites": {},
            "degree_requirements": {},
            "last_updated": datetime.now().isoformat()
        }
        
        # Load and merge all knowledge sources
        for source_name, source_path in self.knowledge_sources.items():
            try:
                if os.path.exists(source_path):
                    with open(source_path, 'r', encoding='utf-8') as f:
                        source_data = json.load(f)
                    
                    # Merge data intelligently
                    self._merge_knowledge_source(unified_data, source_data, source_name)
                    self.logger.info(f"Loaded knowledge source: {source_name}")
                else:
                    self.logger.warning(f"Knowledge source not found: {source_path}")
            except Exception as e:
                self.logger.error(f"Error loading {source_name}: {e}")
        
        # Build unified knowledge graph for NLP solver
        self.nlp_solver.build_knowledge_graph(unified_data)
        
        # Cache unified data
        self.knowledge_cache["unified"] = unified_data
        self.logger.info(f"Unified knowledge base initialized with {len(unified_data.get('courses', {}))} courses")
    
    def _merge_knowledge_source(self, unified_data: Dict, source_data: Dict, source_name: str):
        """Intelligently merge knowledge source into unified data"""
        
        if source_name == "cs_knowledge_graph":
            # Merge courses
            if "courses" in source_data:
                unified_data["courses"].update(source_data["courses"])
            
            # Merge tracks
            if "tracks" in source_data:
                unified_data["tracks"].update(source_data["tracks"])
            
            # Merge prerequisites
            if "prerequisites" in source_data:
                unified_data["prerequisites"].update(source_data["prerequisites"])
            
            # Merge degree requirements
            if "degree_requirements" in source_data:
                unified_data["degree_requirements"].update(source_data["degree_requirements"])
        
        elif source_name == "comprehensive_data":
            # Merge comprehensive course data
            if "courses" in source_data:
                for course_id, course_data in source_data["courses"].items():
                    if course_id in unified_data["courses"]:
                        # Merge course data
                        unified_data["courses"][course_id].update(course_data)
                    else:
                        unified_data["courses"][course_id] = course_data
        
        elif source_name == "conversation_contexts":
            # Add conversation history for context
            unified_data["conversation_history"] = source_data
    
    def _background_sync(self):
        """Background thread for knowledge base synchronization"""
        while True:
            try:
                time.sleep(self.knowledge_sync_interval)
                
                # Check if knowledge sources have been updated
                if self._should_sync_knowledge():
                    self.logger.info("Starting background knowledge synchronization...")
                    self._initialize_unified_knowledge_base()
                    self._clear_expired_cache()
                    self.last_sync_time = datetime.now()
                    self.logger.info("Background synchronization completed")
                
            except Exception as e:
                self.logger.error(f"Background sync error: {e}")
    
    def _should_sync_knowledge(self) -> bool:
        """Check if knowledge base should be synchronized"""
        try:
            for source_path in self.knowledge_sources.values():
                if os.path.exists(source_path):
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(source_path))
                    if file_mtime > self.last_sync_time:
                        return True
            return False
        except Exception:
            return True  # Sync on error to be safe
    
    def _clear_expired_cache(self):
        """Clear expired cache entries"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, (data, timestamp) in self.query_cache.items():
            if current_time - timestamp > self.cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.query_cache[key]
        
        if expired_keys:
            self.logger.info(f"Cleared {len(expired_keys)} expired cache entries")
    
    def _generate_cache_key(self, query: str, context: Dict[str, Any] = None) -> str:
        """Generate cache key for query"""
        cache_input = f"{query}_{json.dumps(context, sort_keys=True) if context else ''}"
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    async def process_query_enhanced(self, 
                                   query: str, 
                                   session_id: str = None,
                                   user_id: str = None,
                                   context: Dict[str, Any] = None) -> EnhancedQueryContext:
        """Enhanced query processing that solves AI understanding issues"""
        
        start_time = time.time()
        session_id = session_id or f"session_{int(time.time())}"
        cache_key = self._generate_cache_key(query, context)
        
        self.logger.info(f"Processing enhanced query: {query[:50]}...")
        
        # Check cache first
        if cache_key in self.query_cache:
            cached_data, timestamp = self.query_cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                self.logger.info("Returning cached result")
                return cached_data
        
        try:
            # Step 1: Multi-engine query understanding
            query_analysis = await self._analyze_query_multi_engine(query, context)
            
            # Step 2: Enhanced knowledge retrieval
            knowledge_data = await self._retrieve_enhanced_knowledge(query_analysis)
            
            # Step 3: Unified response generation
            response = await self._generate_unified_response(query, query_analysis, knowledge_data)
            
            # Step 4: Create enhanced context
            processing_time = time.time() - start_time
            
            enhanced_context = EnhancedQueryContext(
                session_id=session_id,
                user_id=user_id,
                query=query,
                timestamp=datetime.now(),
                previous_queries=context.get("previous_queries", []) if context else [],
                extracted_entities=query_analysis.get("entities", {}),
                intent_confidence=query_analysis.get("confidence", 0.0),
                knowledge_sources_used=knowledge_data.get("sources_used", []),
                processing_time=processing_time,
                cache_key=cache_key
            )
            
            # Cache the result
            self.query_cache[cache_key] = (enhanced_context, datetime.now())
            
            # Trigger N8N workflow for advanced processing
            await self._trigger_n8n_workflow(enhanced_context, response)
            
            self.logger.info(f"Query processed successfully in {processing_time:.2f}s")
            return enhanced_context
            
        except Exception as e:
            self.logger.error(f"Enhanced query processing failed: {e}")
            raise
    
    async def _analyze_query_multi_engine(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze query using multiple AI engines for enhanced understanding"""
        
        # Run multiple engines in parallel
        tasks = [
            self._run_smart_ai_analysis(query, context),
            self._run_nlp_semantic_analysis(query),
            self._run_failure_analysis_check(query)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results intelligently
        combined_analysis = {
            "entities": {},
            "concepts": [],
            "intent": "general_query",
            "confidence": 0.0,
            "analysis_methods": [],
            "specialized_handling": None
        }
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.warning(f"Engine {i} failed: {result}")
                continue
            
            if result:
                combined_analysis["analysis_methods"].append(f"engine_{i}")
                
                # Merge entities
                if "entities" in result:
                    combined_analysis["entities"].update(result["entities"])
                
                # Merge concepts
                if "concepts" in result:
                    combined_analysis["concepts"].extend(result["concepts"])
                
                # Use highest confidence intent
                if result.get("confidence", 0) > combined_analysis["confidence"]:
                    combined_analysis["intent"] = result.get("intent", "general_query")
                    combined_analysis["confidence"] = result.get("confidence", 0)
                
                # Check for specialized handling
                if result.get("specialized_handling"):
                    combined_analysis["specialized_handling"] = result["specialized_handling"]
        
        # Remove duplicates from concepts
        combined_analysis["concepts"] = list(set(combined_analysis["concepts"]))
        
        return combined_analysis
    
    async def _run_smart_ai_analysis(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run smart AI engine analysis"""
        try:
            intent = self.smart_ai_engine.understand_query(query, context)
            return {
                "entities": intent.entities,
                "concepts": intent.specific_topics,
                "intent": intent.primary_intent,
                "confidence": intent.confidence,
                "source": "smart_ai_engine"
            }
        except Exception as e:
            self.logger.error(f"Smart AI analysis failed: {e}")
            return {}
    
    async def _run_nlp_semantic_analysis(self, query: str) -> Dict[str, Any]:
        """Run NLP semantic analysis"""
        try:
            semantic_query = self.nlp_solver.understand_query_semantically(query)
            return {
                "entities": {entity: "nlp_extracted" for entity in semantic_query.entities},
                "concepts": semantic_query.concepts,
                "intent": semantic_query.intent,
                "confidence": 0.8,  # NLP solver provides reliable analysis
                "source": "nlp_solver"
            }
        except Exception as e:
            self.logger.error(f"NLP semantic analysis failed: {e}")
            return {}
    
    async def _run_failure_analysis_check(self, query: str) -> Dict[str, Any]:
        """Check if query needs specialized failure analysis"""
        try:
            # Check if this is a failure/prerequisite query
            failure_keywords = ['fail', 'failing', 'failed', 'failure', 'prerequisite', 'prereq']
            if any(keyword in query.lower() for keyword in failure_keywords):
                courses = self.failure_analyzer.normalize_course_code(query)
                if courses:
                    return {
                        "specialized_handling": "failure_analysis",
                        "entities": {course: "failed_course" for course in courses},
                        "intent": "failure_analysis",
                        "confidence": 0.9,
                        "source": "failure_analyzer"
                    }
            return {}
        except Exception as e:
            self.logger.error(f"Failure analysis check failed: {e}")
            return {}
    
    async def _retrieve_enhanced_knowledge(self, query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced knowledge retrieval using unified knowledge base"""
        
        knowledge_data = {
            "sources_used": [],
            "courses": {},
            "tracks": {},
            "prerequisites": {},
            "specialized_data": {}
        }
        
        # Get unified knowledge base
        unified_data = self.knowledge_cache.get("unified", {})
        
        # Extract relevant courses
        entities = query_analysis.get("entities", {})
        for entity, entity_type in entities.items():
            if entity in unified_data.get("courses", {}):
                knowledge_data["courses"][entity] = unified_data["courses"][entity]
                knowledge_data["sources_used"].append("course_catalog")
        
        # Extract relevant tracks
        intent = query_analysis.get("intent", "")
        if "track" in intent or "dual" in intent:
            knowledge_data["tracks"] = unified_data.get("tracks", {})
            knowledge_data["sources_used"].append("track_data")
        
        # Extract prerequisites
        if "prerequisite" in intent or query_analysis.get("specialized_handling") == "failure_analysis":
            knowledge_data["prerequisites"] = unified_data.get("prerequisites", {})
            knowledge_data["sources_used"].append("prerequisite_data")
        
        # Get specialized data for failure analysis
        if query_analysis.get("specialized_handling") == "failure_analysis":
            knowledge_data["specialized_data"]["failure_scenarios"] = True
            knowledge_data["sources_used"].append("failure_analyzer")
        
        return knowledge_data
    
    async def _generate_unified_response(self, 
                                       query: str, 
                                       query_analysis: Dict[str, Any], 
                                       knowledge_data: Dict[str, Any]) -> str:
        """Generate unified response using the best available method"""
        
        # Use specialized handling if available
        if query_analysis.get("specialized_handling") == "failure_analysis":
            try:
                return self.failure_analyzer.analyze_failure_query(query)
            except Exception as e:
                self.logger.error(f"Failure analysis failed: {e}")
        
        # Use smart AI engine for complex queries
        if query_analysis.get("confidence", 0) > 0.7:
            try:
                intent = QueryIntent(
                    primary_intent=query_analysis.get("intent", "general_query"),
                    confidence=query_analysis.get("confidence", 0.0),
                    entities=query_analysis.get("entities", {}),
                    context_clues={},
                    requires_clarification=False,
                    specific_topics=query_analysis.get("concepts", [])
                )
                return self.smart_ai_engine.generate_accurate_response(query, intent, knowledge_data)
            except Exception as e:
                self.logger.error(f"Smart AI response generation failed: {e}")
        
        # Fall back to NLP solver
        try:
            semantic_query = self.nlp_solver.understand_query_semantically(query)
            return self.nlp_solver.solve_using_knowledge_graph(semantic_query)
        except Exception as e:
            self.logger.error(f"NLP solver failed: {e}")
        
        # Final fallback
        return "I'm having trouble processing your query right now. Please try rephrasing your question."
    
    async def _trigger_n8n_workflow(self, context: EnhancedQueryContext, response: str):
        """Trigger N8N workflow for advanced processing and logging"""
        
        try:
            workflow_data = {
                "session_id": context.session_id,
                "query": context.query,
                "response": response,
                "entities": context.extracted_entities,
                "intent_confidence": context.intent_confidence,
                "processing_time": context.processing_time,
                "knowledge_sources": context.knowledge_sources_used,
                "timestamp": context.timestamp.isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.n8n_webhook_url,
                    json=workflow_data,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        self.logger.info(f"N8N workflow triggered successfully for session {context.session_id}")
                    else:
                        self.logger.warning(f"N8N workflow trigger failed: {resp.status}")
        
        except asyncio.TimeoutError:
            self.logger.warning("N8N workflow trigger timed out")
        except Exception as e:
            self.logger.error(f"N8N workflow trigger error: {e}")
    
    def process_query_sync(self, query: str, context: Dict[str, Any] = None) -> str:
        """Synchronous wrapper for enhanced query processing"""
        
        async def async_wrapper():
            enhanced_context = await self.process_query_enhanced(query, context=context)
            # Get the actual response using the unified method
            query_analysis = await self._analyze_query_multi_engine(query, context)
            knowledge_data = await self._retrieve_enhanced_knowledge(query_analysis)
            return await self._generate_unified_response(query, query_analysis, knowledge_data)
        
        # Run async function in new event loop
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(async_wrapper())
        finally:
            loop.close()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "status": "operational",
            "knowledge_base": {
                "last_sync": self.last_sync_time.isoformat(),
                "sources": len(self.knowledge_sources),
                "courses": len(self.knowledge_cache.get("unified", {}).get("courses", {})),
                "tracks": len(self.knowledge_cache.get("unified", {}).get("tracks", {}))
            },
            "cache": {
                "query_cache_size": len(self.query_cache),
                "knowledge_cache_size": len(self.knowledge_cache)
            },
            "n8n_integration": {
                "webhook_url": self.n8n_webhook_url,
                "status": "active"
            }
        }

# Factory function for easy integration
def create_enhanced_n8n_integration(**kwargs) -> EnhancedN8NIntegration:
    """Create enhanced N8N integration instance"""
    return EnhancedN8NIntegration(**kwargs)

# Test function
async def test_enhanced_integration():
    """Test the enhanced N8N integration"""
    integration = EnhancedN8NIntegration()
    
    test_queries = [
        "What courses should I take as a freshman?",
        "I failed CS 25100, what should I do?",
        "Tell me about both Machine Intelligence and Software Engineering tracks",
        "What are the prerequisites for CS 37300?",
        "How do I graduate early with both tracks?"
    ]
    
    print("🧪 Testing Enhanced N8N Integration")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        try:
            response = integration.process_query_sync(query)
            print(f"✅ Response: {response[:200]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Show system status
    print(f"\n📊 System Status:")
    status = integration.get_system_status()
    print(json.dumps(status, indent=2))

if __name__ == "__main__":
    asyncio.run(test_enhanced_integration())