#!/usr/bin/env python3
"""
BoilerAI API Gateway
====================

This is the main API gateway that integrates the CLI with the frontend.
It handles API key management and query processing.
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Add CLI path
cli_path = Path(__file__).parent.parent / "my_cli_bot"
sys.path.insert(0, str(cli_path))

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Import our CLI and API key manager
try:
    from simple_boiler_ai import SimpleBoilerAI
    from api_key_manager import get_api_key_manager, setup_api_key
    from boilerai_server_bridge import get_server, initialize_server, process_query, get_api_status, set_api_key
except ImportError as e:
    print(f"Error importing CLI modules: {e}")
    print("Make sure the CLI is properly set up")
    sys.exit(1)

# Pydantic models
class QueryRequest(BaseModel):
    query: str = Field(..., description="The user's query")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    provider: Optional[str] = Field(None, description="AI provider (gemini or openai)")

class QueryResponse(BaseModel):
    success: bool
    query: str
    response: str
    thinking: Optional[str] = None
    sources: Optional[list] = None
    confidence: Optional[float] = None
    execution_time: float
    timestamp: str

class APIKeyRequest(BaseModel):
    provider: str = Field(..., description="AI provider (gemini or openai)")
    api_key: str = Field(..., description="API key")

class APIKeyResponse(BaseModel):
    success: bool
    message: str
    provider: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    api_status: Dict[str, Any]
    cli_initialized: bool

# Initialize FastAPI app
app = FastAPI(
    title="BoilerAI API Gateway",
    description="API Gateway for BoilerAI CLI integration with frontend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global server instance
server = get_server()

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "BoilerAI API Gateway",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    api_status = get_api_status()
    cli_initialized = server.cli_instance is not None
    
    return HealthResponse(
        status="healthy" if cli_initialized else "needs_setup",
        timestamp=datetime.now().isoformat(),
        api_status=api_status,
        cli_initialized=cli_initialized
    )

@app.post("/api/setup", response_model=APIKeyResponse)
async def setup_api_key_endpoint(request: APIKeyRequest):
    """Setup API key for the system"""
    try:
        success = set_api_key(request.provider, request.api_key)
        
        if success:
            return APIKeyResponse(
                success=True,
                message=f"API key set successfully for {request.provider}",
                provider=request.provider
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to set API key"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error setting API key: {str(e)}"
        )

@app.get("/api/status", response_model=Dict[str, Any])
async def get_api_status_endpoint():
    """Get API key status"""
    return get_api_status()

@app.post("/api/query", response_model=QueryResponse)
async def process_query_endpoint(request: QueryRequest):
    """Process a query through the CLI"""
    start_time = datetime.now()
    
    try:
        # Initialize server if needed
        if not server.cli_instance:
            if request.api_key and request.provider:
                success = initialize_server(request.api_key, request.provider)
                if not success:
                    raise HTTPException(
                        status_code=400,
                        detail="Failed to initialize CLI with provided API key"
                    )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="CLI not initialized. Please provide API key and provider."
                )
        
        # Process the query
        result = process_query(request.query)
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return QueryResponse(
            success=True,
            query=request.query,
            response=result.get("response", "No response generated"),
            thinking=result.get("thinking"),
            sources=result.get("sources", []),
            confidence=result.get("confidence"),
            execution_time=execution_time,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return QueryResponse(
            success=False,
            query=request.query,
            response=f"Error processing query: {str(e)}",
            thinking="Error occurred during processing",
            sources=[],
            confidence=0.0,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat()
        )

@app.post("/api/initialize")
async def initialize_cli_endpoint(request: APIKeyRequest):
    """Initialize CLI with API key"""
    try:
        success = initialize_server(request.api_key, request.provider)
        
        if success:
            return {
                "success": True,
                "message": f"CLI initialized successfully with {request.provider}",
                "provider": request.provider
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to initialize CLI"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error initializing CLI: {str(e)}"
        )

@app.get("/api/providers")
async def get_available_providers():
    """Get available AI providers"""
    return {
        "providers": [
            {
                "name": "gemini",
                "display_name": "Google Gemini",
                "description": "Google's AI model with free tier available"
            },
            {
                "name": "openai",
                "display_name": "OpenAI",
                "description": "OpenAI's GPT models (paid service)"
            }
        ]
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    print("Starting BoilerAI API Gateway...")
    print("=" * 40)
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("=" * 40)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

