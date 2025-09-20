#!/usr/bin/env python3
"""
FastAPI Server for Enhanced LangChain Academic Advisor
Provides REST API endpoints for the Boiler AI academic advisor
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import uvicorn
import os
import json
import logging
from datetime import datetime

# Import the enhanced pipeline
from langchain_advisor_pipeline import EnhancedLangChainPipeline

# Pydantic models for API
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    api_key: Optional[str] = None
    include_context: bool = True

class ChatResponse(BaseModel):
    intent: str
    entities: Dict[str, Any]
    response: str
    method: str
    context: Optional[str] = None
    session_id: str
    timestamp: str
    processing_time_ms: float

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    components: Dict[str, str]

# FastAPI app initialization
app = FastAPI(
    title="Boiler AI Academic Advisor API",
    description="Enhanced LangChain-based academic advisor for Purdue CS students",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline instance
pipeline: Optional[EnhancedLangChainPipeline] = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize the pipeline on startup"""
    global pipeline
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set")
        raise RuntimeError("Gemini API key required")
    
    try:
        pipeline = EnhancedLangChainPipeline(api_key)
        logger.info("Pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        raise RuntimeError(f"Pipeline initialization failed: {e}")

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        components={
            "pipeline": "initialized" if pipeline else "not_initialized",
            "vector_store": "available" if pipeline and pipeline.vector_store else "unavailable",
            "conversation_manager": "available" if pipeline and pipeline.conversation_manager else "unavailable"
        }
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    components_status = {}
    
    try:
        # Test vector store
        if pipeline.vector_store:
            test_results = pipeline.vector_store.similarity_search("test", k=1)
            components_status["vector_store"] = "healthy"
        else:
            components_status["vector_store"] = "unavailable"
    except Exception as e:
        components_status["vector_store"] = f"error: {str(e)}"
    
    try:
        # Test conversation manager
        if pipeline.conversation_manager:
            components_status["conversation_manager"] = "healthy"
        else:
            components_status["conversation_manager"] = "unavailable"
    except Exception as e:
        components_status["conversation_manager"] = f"error: {str(e)}"
    
    try:
        # Test LLM
        if pipeline.llm:
            components_status["llm"] = "healthy"
        else:
            components_status["llm"] = "unavailable"
    except Exception as e:
        components_status["llm"] = f"error: {str(e)}"
    
    return HealthResponse(
        status="healthy" if all("error" not in status for status in components_status.values()) else "degraded",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        components=components_status
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for academic advisor queries"""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    start_time = datetime.now()
    
    try:
        # Use provided API key if available
        if request.api_key:
            # Create a temporary pipeline with the provided API key
            temp_pipeline = EnhancedLangChainPipeline(request.api_key)
            result = temp_pipeline.process_query(request.query, request.session_id)
        else:
            # Use the global pipeline
            result = pipeline.process_query(request.query, request.session_id)
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return ChatResponse(
            intent=result.get("intent", "unknown"),
            entities=result.get("entities", {}),
            response=result.get("response", ""),
            method=result.get("method", "unknown"),
            context=result.get("context") if request.include_context else None,
            session_id=request.session_id or "default",
            timestamp=datetime.now().isoformat(),
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/tools", response_model=List[ToolDefinition])
async def get_tools():
    """Get available function calling tools"""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        tool_definitions = pipeline.get_tool_definitions()
        return [ToolDefinition(**tool) for tool in tool_definitions]
    except Exception as e:
        logger.error(f"Error getting tool definitions: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting tools: {str(e)}")

@app.get("/courses/{course_code}")
async def get_course_info(course_code: str):
    """Get information about a specific course"""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        result = pipeline._get_course_info(course_code)
        return {"course_code": course_code, "info": result}
    except Exception as e:
        logger.error(f"Error getting course info: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting course info: {str(e)}")

@app.get("/courses/{course_code}/prerequisites")
async def get_course_prerequisites(course_code: str):
    """Get prerequisites for a specific course"""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        result = pipeline._get_prerequisites(course_code)
        return {"course_code": course_code, "prerequisites": result}
    except Exception as e:
        logger.error(f"Error getting prerequisites: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting prerequisites: {str(e)}")

@app.post("/degree-plan")
async def generate_degree_plan(
    major: str = "Computer Science",
    entry_term: str = "Fall", 
    entry_year: int = 2024
):
    """Generate a degree plan for a student"""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        result = pipeline._get_degree_plan(major, entry_term, entry_year)
        return {
            "major": major,
            "entry_term": entry_term,
            "entry_year": entry_year,
            "degree_plan": result
        }
    except Exception as e:
        logger.error(f"Error generating degree plan: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating degree plan: {str(e)}")

@app.get("/search")
async def search_knowledge_base(query: str, limit: int = 5):
    """Search the knowledge base"""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        if pipeline.vector_store:
            docs = pipeline.vector_store.similarity_search(query, k=limit)
            results = []
            for doc in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": 1.0  # FAISS doesn't return scores by default
                })
            return {"query": query, "results": results, "count": len(results)}
        else:
            raise HTTPException(status_code=503, detail="Vector store not available")
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")

@app.get("/statistics")
async def get_statistics():
    """Get system statistics"""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        stats = {
            "vector_store_size": 0,
            "tools_available": len(pipeline.tools) if pipeline.tools else 0,
            "knowledge_sources": 0
        }
        
        # Get vector store size
        if pipeline.vector_store:
            stats["vector_store_size"] = pipeline.vector_store.index.ntotal if hasattr(pipeline.vector_store, 'index') else 0
        
        # Count knowledge sources
        if hasattr(pipeline.smart_ai_engine, 'data_sources'):
            stats["knowledge_sources"] = len(pipeline.smart_ai_engine.data_sources)
        
        return stats
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

# WebSocket endpoint for real-time chat (optional)
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    if not pipeline:
        await websocket.send_json({"error": "Pipeline not initialized"})
        await websocket.close()
        return
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            query = data.get("query", "")
            session_id = data.get("session_id", "ws_session")
            
            if not query:
                await websocket.send_json({"error": "Query required"})
                continue
            
            # Process query
            start_time = datetime.now()
            result = pipeline.process_query(query, session_id)
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Send response
            response = {
                "intent": result.get("intent", "unknown"),
                "response": result.get("response", ""),
                "method": result.get("method", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "processing_time_ms": processing_time
            }
            
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({"error": str(e)})

if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable is required")
        exit(1)
    
    # Run the server
    uvicorn.run(
        "fastapi_advisor_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )