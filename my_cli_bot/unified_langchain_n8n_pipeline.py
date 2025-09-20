#!/usr/bin/env python3
"""
Unified LangChain + N8N Pipeline Integration
Combines the strengths of both systems for maximum flexibility and intelligence
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

# LangChain imports
from langchain.llms import google.generativeai as genai
from langchain.embeddings import google.generativeai as genaiEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferWindowMemory

# Import existing components
from n8n_style_pipeline import N8NStylePipeline, WorkflowData, WorkflowNode, NodeStatus
from enhanced_n8n_integration import EnhancedN8NIntegration, EnhancedQueryContext
from langchain_advisor_pipeline import EnhancedLangChainPipeline
from intelligent_conversation_manager import IntelligentConversationManager

class PipelineMode(Enum):
    """Pipeline execution modes"""
    N8N_ONLY = "n8n_only"           # Use N8N workflow only
    LANGCHAIN_ONLY = "langchain_only"  # Use LangChain only  
    HYBRID = "hybrid"               # Use both with intelligent routing
    FALLBACK = "fallback"           # Try one, fallback to other

@dataclass
class UnifiedPipelineConfig:
    """Configuration for unified pipeline"""
    default_mode: PipelineMode = PipelineMode.HYBRID
    n8n_webhook_url: str = "http://localhost:5678/webhook/boilerai"
    GEMINI_API_KEY: str = ""
    enable_caching: bool = True
    cache_ttl_minutes: int = 15
    max_retries: int = 3
    timeout_seconds: int = 30
    enable_monitoring: bool = True
    fallback_enabled: bool = True

@dataclass
class UnifiedQueryResult:
    """Result from unified pipeline processing"""
    query: str
    response: str
    pipeline_used: str
    execution_time: float
    intent: str
    entities: Dict[str, Any]
    confidence: float
    n8n_result: Optional[Dict[str, Any]] = None
    langchain_result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    success: bool = True
    error_message: Optional[str] = None

class LangChainN8NNode(WorkflowNode):
    """N8N Node that integrates LangChain processing"""
    
    def __init__(self, langchain_pipeline: EnhancedLangChainPipeline):
        super().__init__("LangChain Integration")
        self.langchain_pipeline = langchain_pipeline
    
    def _process(self, data: WorkflowData) -> WorkflowData:
        """Process data using LangChain pipeline"""
        try:
            # Use LangChain for intent classification and entity extraction
            langchain_result = self.langchain_pipeline.process_query(data.query)
            
            # Enhance workflow data with LangChain insights
            data.entities.update({
                "langchain_intent": langchain_result.get("intent", "unknown"),
                "langchain_entities": langchain_result.get("entities", {}),
                "langchain_method": langchain_result.get("method", "unknown")
            })
            
            # If LangChain provides a complete response, use it
            if langchain_result.get("response") and len(langchain_result["response"]) > 50:
                data.response = langchain_result["response"]
                data.metadata["langchain_response_used"] = True
            
            # Enhance AI context with LangChain analysis
            langchain_context = f"""
LANGCHAIN ANALYSIS:
Intent: {langchain_result.get('intent', 'unknown')}
Entities: {langchain_result.get('entities', {})}
Method: {langchain_result.get('method', 'unknown')}
Confidence: {langchain_result.get('confidence', 0.0)}
"""
            data.ai_context += "\n" + langchain_context
            
            print(f"   🧠 LangChain analysis: Intent={langchain_result.get('intent')}, Method={langchain_result.get('method')}")
            
        except Exception as e:
            print(f"   ⚠️ LangChain processing failed: {e}")
            # Continue with normal N8N processing
        
        return data

class N8NLangChainNode(WorkflowNode):
    """N8N Node that uses N8N workflow results to enhance LangChain"""
    
    def __init__(self, n8n_pipeline: N8NStylePipeline):
        super().__init__("N8N Enhancement")
        self.n8n_pipeline = n8n_pipeline
    
    def _process(self, data: WorkflowData) -> WorkflowData:
        """Enhance data using N8N workflow insights"""
        try:
            # Get N8N workflow result
            n8n_result = self.n8n_pipeline.execute_workflow(data.query)
            
            # Extract entities from N8N processing
            if n8n_result.get("entities"):
                data.entities.update({
                    "n8n_entities": n8n_result["entities"],
                    "n8n_knowledge_sections": n8n_result.get("knowledge_sections", [])
                })
            
            # Enhance knowledge base with N8N findings
            if n8n_result.get("response") and not data.response:
                data.response = n8n_result["response"]
                data.metadata["n8n_response_used"] = True
            
            print(f"   🔧 N8N analysis: Entities={len(data.entities.get('n8n_entities', {}))}, Knowledge sections={len(n8n_result.get('knowledge_sections', []))}")
            
        except Exception as e:
            print(f"   ⚠️ N8N processing failed: {e}")
            # Continue processing
        
        return data

class UnifiedPipelineOrchestrator:
    """Unified orchestrator that intelligently routes between N8N and LangChain"""
    
    def __init__(self, config: UnifiedPipelineConfig):
        self.config = config
        self.logger = self._setup_logging()
        
        # Initialize components
        self._initialize_components()
        
        # Monitoring and caching
        self.query_cache = {}
        self.performance_metrics = {
            "n8n_calls": 0,
            "langchain_calls": 0,
            "hybrid_calls": 0,
            "cache_hits": 0,
            "total_queries": 0,
            "average_response_time": 0.0
        }
        
        self.logger.info("Unified Pipeline Orchestrator initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('unified_pipeline.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _initialize_components(self):
        """Initialize all pipeline components"""
        try:
            # Initialize N8N components
            self.n8n_pipeline = N8NStylePipeline()
            self.enhanced_n8n = EnhancedN8NIntegration(
                n8n_webhook_url=self.config.n8n_webhook_url
            )
            
            # Initialize LangChain components (if API key available)
            if self.config.GEMINI_API_KEY:
                self.langchain_pipeline = EnhancedLangChainPipeline(self.config.GEMINI_API_KEY)
                self.langchain_available = True
            else:
                self.langchain_pipeline = None
                self.langchain_available = False
                self.logger.warning("Gemini API key not provided - LangChain features disabled")
            
            # Initialize conversation manager fallback
            self.conversation_manager = IntelligentConversationManager()
            
            # Create enhanced N8N pipeline with LangChain integration
            if self.langchain_available:
                self._create_enhanced_n8n_pipeline()
            
            self.logger.info(f"Components initialized - LangChain: {self.langchain_available}")
            
        except Exception as e:
            self.logger.error(f"Component initialization failed: {e}")
            raise
    
    def _create_enhanced_n8n_pipeline(self):
        """Create N8N pipeline with LangChain integration"""
        # Create new N8N pipeline with LangChain node
        enhanced_nodes = [
            self.n8n_pipeline.nodes[0],  # QueryParseNode
            LangChainN8NNode(self.langchain_pipeline),  # New LangChain integration
            self.n8n_pipeline.nodes[1],  # KnowledgeRetrievalNode
            self.n8n_pipeline.nodes[2],  # ContextBuilderNode
            self.n8n_pipeline.nodes[3],  # AIResponseNode
            self.n8n_pipeline.nodes[4],  # ResponseFormatterNode
        ]
        
        # Replace nodes in N8N pipeline
        self.n8n_pipeline.nodes = enhanced_nodes
        self.logger.info("Enhanced N8N pipeline with LangChain integration created")
    
    def _generate_cache_key(self, query: str, mode: PipelineMode) -> str:
        """Generate cache key"""
        cache_input = f"{query}_{mode.value}"
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def _should_use_cache(self, cache_key: str) -> Tuple[bool, Optional[UnifiedQueryResult]]:
        """Check if cached result should be used"""
        if not self.config.enable_caching:
            return False, None
        
        if cache_key in self.query_cache:
            result, timestamp = self.query_cache[cache_key]
            if datetime.now() - timestamp < timedelta(minutes=self.config.cache_ttl_minutes):
                self.performance_metrics["cache_hits"] += 1
                return True, result
            else:
                # Remove expired cache entry
                del self.query_cache[cache_key]
        
        return False, None
    
    def _cache_result(self, cache_key: str, result: UnifiedQueryResult):
        """Cache query result"""
        if self.config.enable_caching:
            self.query_cache[cache_key] = (result, datetime.now())
    
    def _determine_optimal_pipeline(self, query: str) -> PipelineMode:
        """Intelligently determine which pipeline to use"""
        
        # Check configuration default
        if self.config.default_mode != PipelineMode.HYBRID:
            return self.config.default_mode
        
        # If LangChain not available, use N8N
        if not self.langchain_available:
            return PipelineMode.N8N_ONLY
        
        query_lower = query.lower()
        
        # Use LangChain for structured queries
        structured_indicators = [
            "what is cs", "prerequisites for", "requirements for",
            "graduation plan", "degree plan", "can i graduate",
            "machine intelligence", "software engineering"
        ]
        
        if any(indicator in query_lower for indicator in structured_indicators):
            return PipelineMode.LANGCHAIN_ONLY
        
        # Use N8N for complex conversational queries
        conversational_indicators = [
            "tell me about", "explain", "how does", "what happens",
            "i failed", "i'm struggling", "help me understand"
        ]
        
        if any(indicator in query_lower for indicator in conversational_indicators):
            return PipelineMode.N8N_ONLY
        
        # Default to hybrid for mixed queries
        return PipelineMode.HYBRID
    
    async def process_query_async(self, 
                                 query: str, 
                                 session_id: str = None,
                                 mode: PipelineMode = None) -> UnifiedQueryResult:
        """Asynchronous query processing with unified pipeline"""
        
        start_time = time.time()
        session_id = session_id or f"unified_{int(time.time())}"
        mode = mode or self._determine_optimal_pipeline(query)
        
        # Check cache
        cache_key = self._generate_cache_key(query, mode)
        use_cache, cached_result = self._should_use_cache(cache_key)
        if use_cache:
            self.logger.info(f"Returning cached result for: {query[:50]}...")
            return cached_result
        
        self.performance_metrics["total_queries"] += 1
        self.logger.info(f"Processing query with mode {mode.value}: {query[:50]}...")
        
        try:
            if mode == PipelineMode.N8N_ONLY:
                result = await self._process_n8n_only(query, session_id)
            elif mode == PipelineMode.LANGCHAIN_ONLY:
                result = await self._process_langchain_only(query, session_id)
            elif mode == PipelineMode.HYBRID:
                result = await self._process_hybrid(query, session_id)
            else:  # FALLBACK
                result = await self._process_with_fallback(query, session_id)
            
            # Update performance metrics
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            self._update_performance_metrics(mode, execution_time)
            
            # Cache successful result
            if result.success:
                self._cache_result(cache_key, result)
            
            self.logger.info(f"Query processed successfully in {execution_time:.2f}s using {result.pipeline_used}")
            return result
            
        except Exception as e:
            self.logger.error(f"Query processing failed: {e}")
            execution_time = time.time() - start_time
            
            # Return error result
            return UnifiedQueryResult(
                query=query,
                response=f"I apologize, but I encountered an error processing your query: {str(e)}",
                pipeline_used="error",
                execution_time=execution_time,
                intent="error",
                entities={},
                confidence=0.0,
                success=False,
                error_message=str(e)
            )
    
    async def _process_n8n_only(self, query: str, session_id: str) -> UnifiedQueryResult:
        """Process using N8N pipeline only"""
        self.performance_metrics["n8n_calls"] += 1
        
        # Use enhanced N8N integration
        enhanced_context = await self.enhanced_n8n.process_query_enhanced(
            query=query,
            session_id=session_id
        )
        
        # Get response using N8N pipeline
        n8n_result = self.n8n_pipeline.execute_workflow(query)
        
        return UnifiedQueryResult(
            query=query,
            response=n8n_result.get("response", "No response generated"),
            pipeline_used="n8n_only",
            execution_time=0.0,  # Will be set by caller
            intent=enhanced_context.extracted_entities.get("intent", "unknown"),
            entities=enhanced_context.extracted_entities,
            confidence=enhanced_context.intent_confidence,
            n8n_result=n8n_result,
            metadata={
                "enhanced_context": asdict(enhanced_context),
                "n8n_success": n8n_result.get("success", False)
            }
        )
    
    async def _process_langchain_only(self, query: str, session_id: str) -> UnifiedQueryResult:
        """Process using LangChain pipeline only"""
        self.performance_metrics["langchain_calls"] += 1
        
        if not self.langchain_available:
            raise Exception("LangChain not available - Gemini API key required")
        
        # Process with LangChain
        langchain_result = self.langchain_pipeline.process_query(query, session_id)
        
        return UnifiedQueryResult(
            query=query,
            response=langchain_result.get("response", "No response generated"),
            pipeline_used="langchain_only",
            execution_time=0.0,  # Will be set by caller
            intent=langchain_result.get("intent", "unknown"),
            entities=langchain_result.get("entities", {}),
            confidence=0.8,  # LangChain generally provides reliable classification
            langchain_result=langchain_result,
            metadata={
                "langchain_method": langchain_result.get("method", "unknown"),
                "langchain_context": langchain_result.get("context", "")
            }
        )
    
    async def _process_hybrid(self, query: str, session_id: str) -> UnifiedQueryResult:
        """Process using both pipelines with intelligent combination"""
        self.performance_metrics["hybrid_calls"] += 1
        
        # Run both pipelines in parallel
        tasks = []
        
        # N8N processing
        tasks.append(self._process_n8n_only(query, session_id))
        
        # LangChain processing (if available)
        if self.langchain_available:
            tasks.append(self._process_langchain_only(query, session_id))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results intelligently
        n8n_result = results[0] if not isinstance(results[0], Exception) else None
        langchain_result = results[1] if len(results) > 1 and not isinstance(results[1], Exception) else None
        
        # Choose best response
        best_response = self._choose_best_response(n8n_result, langchain_result)
        
        # Combine entities
        combined_entities = {}
        if n8n_result:
            combined_entities.update(n8n_result.entities)
        if langchain_result:
            combined_entities.update(langchain_result.entities)
        
        # Choose best intent
        intent = "unknown"
        confidence = 0.0
        if langchain_result and langchain_result.confidence > 0.5:
            intent = langchain_result.intent
            confidence = langchain_result.confidence
        elif n8n_result:
            intent = n8n_result.intent
            confidence = n8n_result.confidence
        
        return UnifiedQueryResult(
            query=query,
            response=best_response,
            pipeline_used="hybrid",
            execution_time=0.0,  # Will be set by caller
            intent=intent,
            entities=combined_entities,
            confidence=confidence,
            n8n_result=n8n_result.n8n_result if n8n_result else None,
            langchain_result=langchain_result.langchain_result if langchain_result else None,
            metadata={
                "n8n_available": n8n_result is not None,
                "langchain_available": langchain_result is not None,
                "response_source": "langchain" if langchain_result and len(langchain_result.response) > len(best_response) * 0.8 else "n8n"
            }
        )
    
    async def _process_with_fallback(self, query: str, session_id: str) -> UnifiedQueryResult:
        """Process with fallback between pipelines"""
        
        # Try primary method first
        primary_mode = self._determine_optimal_pipeline(query)
        if primary_mode == PipelineMode.HYBRID or primary_mode == PipelineMode.FALLBACK:
            primary_mode = PipelineMode.LANGCHAIN_ONLY if self.langchain_available else PipelineMode.N8N_ONLY
        
        try:
            if primary_mode == PipelineMode.LANGCHAIN_ONLY:
                result = await self._process_langchain_only(query, session_id)
            else:
                result = await self._process_n8n_only(query, session_id)
            
            result.pipeline_used = f"{primary_mode.value}_primary"
            return result
            
        except Exception as e:
            self.logger.warning(f"Primary method {primary_mode.value} failed: {e}, trying fallback")
            
            # Try fallback method
            fallback_mode = PipelineMode.N8N_ONLY if primary_mode == PipelineMode.LANGCHAIN_ONLY else PipelineMode.LANGCHAIN_ONLY
            
            try:
                if fallback_mode == PipelineMode.LANGCHAIN_ONLY and self.langchain_available:
                    result = await self._process_langchain_only(query, session_id)
                else:
                    result = await self._process_n8n_only(query, session_id)
                
                result.pipeline_used = f"{fallback_mode.value}_fallback"
                return result
                
            except Exception as e2:
                self.logger.error(f"Fallback method also failed: {e2}")
                raise Exception(f"Both primary ({e}) and fallback ({e2}) methods failed")
    
    def _choose_best_response(self, n8n_result: Optional[UnifiedQueryResult], langchain_result: Optional[UnifiedQueryResult]) -> str:
        """Choose the best response from available results"""
        
        if not n8n_result and not langchain_result:
            return "I'm unable to process your query right now. Please try again."
        
        if not n8n_result:
            return langchain_result.response
        
        if not langchain_result:
            return n8n_result.response
        
        # Prefer LangChain for structured responses
        if langchain_result.confidence > 0.7 and len(langchain_result.response) > 50:
            return langchain_result.response
        
        # Prefer N8N for detailed conversational responses
        if len(n8n_result.response) > len(langchain_result.response) * 1.2:
            return n8n_result.response
        
        # Default to LangChain if available
        return langchain_result.response
    
    def _update_performance_metrics(self, mode: PipelineMode, execution_time: float):
        """Update performance metrics"""
        total_queries = self.performance_metrics["total_queries"]
        current_avg = self.performance_metrics["average_response_time"]
        
        # Update rolling average
        new_avg = ((current_avg * (total_queries - 1)) + execution_time) / total_queries
        self.performance_metrics["average_response_time"] = new_avg
    
    def process_query_sync(self, query: str, session_id: str = None, mode: PipelineMode = None) -> UnifiedQueryResult:
        """Synchronous wrapper for query processing"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.process_query_async(query, session_id, mode))
        finally:
            loop.close()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "status": "operational",
            "components": {
                "n8n_pipeline": "available",
                "enhanced_n8n": "available",
                "langchain_pipeline": "available" if self.langchain_available else "unavailable",
                "conversation_manager": "available"
            },
            "configuration": {
                "default_mode": self.config.default_mode.value,
                "caching_enabled": self.config.enable_caching,
                "cache_ttl_minutes": self.config.cache_ttl_minutes,
                "fallback_enabled": self.config.fallback_enabled
            },
            "performance_metrics": self.performance_metrics,
            "cache_stats": {
                "cache_size": len(self.query_cache),
                "cache_hit_rate": self.performance_metrics["cache_hits"] / max(1, self.performance_metrics["total_queries"])
            }
        }

# Factory function
def create_unified_pipeline(GEMINI_API_KEY: str = None, **config_kwargs) -> UnifiedPipelineOrchestrator:
    """Create unified pipeline orchestrator"""
    config = UnifiedPipelineConfig(
        GEMINI_API_KEY=GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", ""),
        **config_kwargs
    )
    return UnifiedPipelineOrchestrator(config)

# Test function
async def test_unified_pipeline():
    """Test the unified pipeline"""
    # Create orchestrator
    orchestrator = create_unified_pipeline(
        GEMINI_API_KEY=os.getenv("GEMINI_API_KEY"),
        default_mode=PipelineMode.HYBRID
    )
    
    test_queries = [
        "What is CS 18000?",
        "What are the prerequisites for CS 25000?",
        "I failed CS 25100, what should I do?",
        "Can I graduate in 3 years with both MI and SE tracks?",
        "Tell me about the Machine Intelligence track"
    ]
    
    print("🧪 Testing Unified LangChain + N8N Pipeline")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        try:
            result = await orchestrator.process_query_async(query)
            print(f"✅ Pipeline: {result.pipeline_used}")
            print(f"✅ Intent: {result.intent} (confidence: {result.confidence:.2f})")
            print(f"✅ Response: {result.response[:150]}...")
            print(f"✅ Time: {result.execution_time:.2f}s")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Show system status
    print(f"\n📊 System Status:")
    status = orchestrator.get_system_status()
    print(json.dumps(status, indent=2))

if __name__ == "__main__":
    asyncio.run(test_unified_pipeline())