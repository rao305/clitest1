#!/usr/bin/env python3
"""
Unified API Server for LangChain + N8N Integration
Provides REST API and WebSocket endpoints for the unified pipeline
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn

# Import unified pipeline
from unified_langchain_n8n_pipeline import (
    UnifiedPipelineOrchestrator, 
    UnifiedPipelineConfig, 
    PipelineMode,
    UnifiedQueryResult,
    create_unified_pipeline
)

# New: simple CLI chat service adapter for MVP REST /chat endpoint
try:
    from .services.cli_chat_service import CLIChatService  # when run as module
except Exception:
    # fallback for script execution context
    from services.cli_chat_service import CLIChatService

# Pydantic models for API
class QueryRequest(BaseModel):
    query: str = Field(..., description="The user's query")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")
    user_id: Optional[str] = Field(None, description="User ID for personalization")
    mode: Optional[str] = Field("hybrid", description="Pipeline mode: n8n_only, langchain_only, hybrid, fallback")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for query processing")
    api_key: Optional[str] = Field(None, description="Override Gemini API key")

class QueryResponse(BaseModel):
    success: bool
    query: str
    response: str
    pipeline_used: str
    execution_time: float
    intent: str
    entities: Dict[str, Any]
    confidence: float
    session_id: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to process")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")

class SystemStatus(BaseModel):
    status: str
    components: Dict[str, str]
    configuration: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    cache_stats: Dict[str, Any]

class WebSocketMessage(BaseModel):
    type: str = Field(..., description="Message type: query, response, error, status")
    data: Dict[str, Any] = Field(..., description="Message data")
    session_id: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# Global pipeline instance
pipeline_orchestrator: Optional[UnifiedPipelineOrchestrator] = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_data: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.session_data[session_id] = {
            "connected_at": datetime.now().isoformat(),
            "query_count": 0
        }

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.session_data:
            del self.session_data[session_id]

    async def send_message(self, session_id: str, message: WebSocketMessage):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(message.json())
            except:
                self.disconnect(session_id)

    async def broadcast(self, message: WebSocketMessage):
        for session_id in list(self.active_connections.keys()):
            await self.send_message(session_id, message)

manager = ConnectionManager()

# Create FastAPI app
app = FastAPI(
    title="BoilerAI Unified Pipeline API",
    description="LangChain + N8N integrated academic advisor API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the pipeline orchestrator"""
    global pipeline_orchestrator
    
    try:
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if not GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set - LangChain features will be limited")
        
        pipeline_orchestrator = create_unified_pipeline(
            GEMINI_API_KEY=GEMINI_API_KEY,
            default_mode=PipelineMode.HYBRID,
            enable_caching=True,
            cache_ttl_minutes=15,
            enable_monitoring=True
        )
        
        logger.info("Unified pipeline orchestrator initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        pipeline_orchestrator = None

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global pipeline_orchestrator
    if pipeline_orchestrator:
        # Perform any necessary cleanup
        logger.info("Pipeline orchestrator shut down")

# Helper functions
def get_pipeline() -> UnifiedPipelineOrchestrator:
    """Get pipeline orchestrator or raise error"""
    if pipeline_orchestrator is None:
        raise HTTPException(
            status_code=503, 
            detail="Pipeline not initialized. Check server logs and restart."
        )
    return pipeline_orchestrator

def validate_mode(mode: str) -> PipelineMode:
    """Validate and convert pipeline mode"""
    try:
        return PipelineMode(mode)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode '{mode}'. Valid modes: {[m.value for m in PipelineMode]}"
        )

def create_query_response(result: UnifiedQueryResult, session_id: str) -> QueryResponse:
    """Create API response from pipeline result"""
    return QueryResponse(
        success=result.success,
        query=result.query,
        response=result.response,
        pipeline_used=result.pipeline_used,
        execution_time=result.execution_time,
        intent=result.intent,
        entities=result.entities,
        confidence=result.confidence,
        session_id=session_id,
        timestamp=datetime.now().isoformat(),
        metadata=result.metadata,
        error_message=result.error_message
    )

# API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "BoilerAI Unified Pipeline API",
        "version": "1.0.0",
        "description": "LangChain + N8N integrated academic advisor",
        "docs": "/docs",
        "health": "/health",
        "status": "/status"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        pipeline = get_pipeline()
        status = pipeline.get_system_status()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "components": status["components"],
                "version": "1.0.0"
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "version": "1.0.0"
            }
        )

@app.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Get detailed system status"""
    pipeline = get_pipeline()
    status_data = pipeline.get_system_status()
    
    return SystemStatus(**status_data)

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Lightweight chat endpoint using CLIChatService for quick frontend integration.

    This is independent of the unified pipeline modes and returns a minimal payload.
    """
    try:
        service = CLIChatService()
        result = service.process_message(request.session_id, request.message)
        return {
            "session_id": result["session_id"],
            "answer": result["response"],
            "response_time_ms": result["response_time_ms"],
            "intent": result.get("intent"),
            "entities": result.get("entities", {}),
            "metadata": result.get("metadata", {}),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, background_tasks: BackgroundTasks):
    """Process a query using the unified pipeline"""
    pipeline = get_pipeline()
    
    # Validate mode
    mode = validate_mode(request.mode)
    
    # Generate session ID if not provided
    session_id = request.session_id or f"api_{int(datetime.now().timestamp())}"
    
    try:
        # Process query
        result = await pipeline.process_query_async(
            query=request.query,
            session_id=session_id,
            mode=mode
        )
        
        # Create response
        response = create_query_response(result, session_id)
        
        # Log query in background
        background_tasks.add_task(log_query_async, request, response)
        
        return response
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/sync", response_model=QueryResponse)
async def process_query_sync(request: QueryRequest):
    """Process a query synchronously (for compatibility)"""
    pipeline = get_pipeline()
    
    # Validate mode
    mode = validate_mode(request.mode)
    
    # Generate session ID if not provided
    session_id = request.session_id or f"sync_{int(datetime.now().timestamp())}"
    
    try:
        # Process query synchronously
        result = pipeline.process_query_sync(
            query=request.query,
            session_id=session_id,
            mode=mode
        )
        
        return create_query_response(result, session_id)
        
    except Exception as e:
        logger.error(f"Sync query processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/modes")
async def get_available_modes():
    """Get available pipeline modes"""
    return {
        "modes": [
            {
                "value": mode.value,
                "description": {
                    "n8n_only": "Use only N8N workflow pipeline",
                    "langchain_only": "Use only LangChain pipeline", 
                    "hybrid": "Use both pipelines intelligently",
                    "fallback": "Try primary, fallback to secondary"
                }[mode.value]
            }
            for mode in PipelineMode
        ],
        "default": "hybrid"
    }

@app.get("/tools")
async def get_available_tools():
    """Get available tools and their descriptions"""
    pipeline = get_pipeline()
    
    # Get tools from LangChain pipeline if available
    tools = []
    if hasattr(pipeline, 'langchain_pipeline') and pipeline.langchain_pipeline:
        tools = pipeline.langchain_pipeline.get_tool_definitions()
    
    return {
        "tools": tools,
        "total_count": len(tools)
    }

# WebSocket endpoint
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, session_id)
    pipeline = get_pipeline()
    
    try:
        # Send welcome message
        welcome_msg = WebSocketMessage(
            type="status",
            data={
                "message": "Connected to BoilerAI Unified Pipeline",
                "session_id": session_id,
                "available_modes": [mode.value for mode in PipelineMode]
            },
            session_id=session_id
        )
        await manager.send_message(session_id, welcome_msg)
        
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Validate message
            if "query" not in message_data:
                error_msg = WebSocketMessage(
                    type="error",
                    data={"error": "Query is required"},
                    session_id=session_id
                )
                await manager.send_message(session_id, error_msg)
                continue
            
            # Process query
            mode = validate_mode(message_data.get("mode", "hybrid"))
            
            try:
                result = await pipeline.process_query_async(
                    query=message_data["query"],
                    session_id=session_id,
                    mode=mode
                )
                
                # Send response
                response_msg = WebSocketMessage(
                    type="response",
                    data={
                        "query": result.query,
                        "response": result.response,
                        "pipeline_used": result.pipeline_used,
                        "intent": result.intent,
                        "confidence": result.confidence,
                        "execution_time": result.execution_time
                    },
                    session_id=session_id
                )
                await manager.send_message(session_id, response_msg)
                
                # Update session data
                manager.session_data[session_id]["query_count"] += 1
                
            except Exception as e:
                error_msg = WebSocketMessage(
                    type="error",
                    data={"error": str(e)},
                    session_id=session_id
                )
                await manager.send_message(session_id, error_msg)
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info(f"WebSocket disconnected: {session_id}")

# N8N webhook endpoint
@app.post("/webhook/n8n")
async def n8n_webhook(request: QueryRequest):
    """N8N webhook endpoint for external workflow integration"""
    return await process_query(request, BackgroundTasks())

# Background tasks
async def log_query_async(request: QueryRequest, response: QueryResponse):
    """Log query for analytics (background task)"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": response.session_id,
        "user_id": request.user_id,
        "query": request.query,
        "mode_requested": request.mode,
        "pipeline_used": response.pipeline_used,
        "intent": response.intent,
        "confidence": response.confidence,
        "execution_time": response.execution_time,
        "success": response.success
    }
    
    # In production, write to database or analytics service
    logger.info(f"Query Log: {json.dumps(log_entry)}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

# Development server
if __name__ == "__main__":
    # Load environment variables
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    # Run server
    uvicorn.run(
        "unified_api_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )