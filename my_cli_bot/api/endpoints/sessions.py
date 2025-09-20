#!/usr/bin/env python3
"""
Session Management API Endpoints
RESTful endpoints for session lifecycle management
"""

import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import Response

from ..schemas import (
    SessionCreateRequest, SessionResponse, APIResponse, ErrorResponse
)
from ..services.session_service import get_session_service, SessionService
from ..auth import get_current_user, require_permission, UserPermissions
from ..middleware import get_request_id, track_api_call


router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", 
             response_model=SessionResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Create new session",
             description="Create a new conversation session with optional initial context")
@track_api_call
async def create_session(
    request: SessionCreateRequest,
    request_id: str = Depends(get_request_id),
    session_service: SessionService = Depends(get_session_service),
    current_user: Dict[str, Any] = Depends(require_permission(UserPermissions.WRITE))
) -> SessionResponse:
    """
    Create a new conversation session.
    
    - **student_id**: Optional student identifier for session tracking
    - **initial_context**: Optional initial context data (student year, GPA, etc.)
    
    Returns session ID, expiration time, and context data.
    """
    start_time = time.time()
    
    try:
        # Create session using service
        session_data = session_service.create_session(request)
        
        processing_time = (time.time() - start_time) * 1000
        
        return SessionResponse(
            success=True,
            processing_time_ms=processing_time,
            request_id=request_id,
            session_id=session_data["session_id"],
            expires_at=session_data["expires_at"],
            context=session_data["context"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                success=False,
                processing_time_ms=processing_time,
                request_id=request_id,
                error_code="INTERNAL_ERROR",
                error_message="Failed to create session",
                details={"exception": str(e)}
            ).dict()
        )


@router.get("/{session_id}",
            response_model=SessionResponse,
            summary="Get session details",
            description="Retrieve session information and current context")
@track_api_call
async def get_session(
    session_id: str,
    request_id: str = Depends(get_request_id),
    session_service: SessionService = Depends(get_session_service),
    current_user: Dict[str, Any] = Depends(require_permission(UserPermissions.READ))
) -> SessionResponse:
    """
    Retrieve session information by ID.
    
    - **session_id**: Unique session identifier
    
    Returns session details including context and expiration.
    """
    start_time = time.time()
    
    try:
        # Get session using service
        session_data = session_service.get_session(session_id)
        
        processing_time = (time.time() - start_time) * 1000
        
        return SessionResponse(
            success=True,
            processing_time_ms=processing_time,
            request_id=request_id,
            session_id=session_data["session_id"],
            expires_at=session_data["expires_at"],
            context=session_data["context"]
        )
        
    except HTTPException as e:
        processing_time = (time.time() - start_time) * 1000
        
        # Re-raise with proper error format
        if isinstance(e.detail, dict):
            error_response = ErrorResponse(
                success=False,
                processing_time_ms=processing_time,
                request_id=request_id,
                error_code=e.detail.get("error_code", "UNKNOWN_ERROR"),
                error_message=e.detail.get("error_message", str(e.detail)),
                details=e.detail.get("details")
            )
            raise HTTPException(status_code=e.status_code, detail=error_response.dict())
        else:
            raise e
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                success=False,
                processing_time_ms=processing_time,
                request_id=request_id,
                error_code="INTERNAL_ERROR",
                error_message="Failed to retrieve session",
                details={"exception": str(e)}
            ).dict()
        )


@router.patch("/{session_id}",
              response_model=SessionResponse,
              summary="Update session context",
              description="Update session context data")
@track_api_call
async def update_session(
    session_id: str,
    context_updates: Dict[str, Any],
    request_id: str = Depends(get_request_id),
    session_service: SessionService = Depends(get_session_service),
    current_user: Dict[str, Any] = Depends(require_permission(UserPermissions.WRITE))
) -> SessionResponse:
    """
    Update session context data.
    
    - **session_id**: Unique session identifier
    - **context_updates**: Context fields to update
    
    Returns updated session information.
    """
    start_time = time.time()
    
    try:
        # Parse request body
        updates = {"context_updates": context_updates}
        
        # Update session using service
        session_data = session_service.update_session(session_id, updates["context_updates"])
        
        processing_time = (time.time() - start_time) * 1000
        
        return SessionResponse(
            success=True,
            processing_time_ms=processing_time,
            request_id=request_id,
            session_id=session_data["session_id"],
            expires_at=session_data["expires_at"],
            context=session_data["context"]
        )
        
    except HTTPException as e:
        processing_time = (time.time() - start_time) * 1000
        
        # Re-raise with proper error format
        if isinstance(e.detail, dict):
            error_response = ErrorResponse(
                success=False,
                processing_time_ms=processing_time,
                request_id=request_id,
                error_code=e.detail.get("error_code", "UNKNOWN_ERROR"),
                error_message=e.detail.get("error_message", str(e.detail)),
                details=e.detail.get("details")
            )
            raise HTTPException(status_code=e.status_code, detail=error_response.dict())
        else:
            raise e
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                success=False,
                processing_time_ms=processing_time,
                request_id=request_id,
                error_code="INTERNAL_ERROR",
                error_message="Failed to update session",
                details={"exception": str(e)}
            ).dict()
        )


@router.delete("/{session_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete session",
               description="Delete/deactivate a session")
@track_api_call
async def delete_session(
    session_id: str,
    request_id: str = Depends(get_request_id),
    session_service: SessionService = Depends(get_session_service),
    current_user: Dict[str, Any] = Depends(require_permission(UserPermissions.WRITE))
) -> Response:
    """
    Delete/deactivate a session.
    
    - **session_id**: Unique session identifier
    
    Returns 204 No Content on success.
    """
    start_time = time.time()
    
    try:
        # Delete session using service
        success = session_service.delete_session(session_id)
        
        if success:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            processing_time = (time.time() - start_time) * 1000
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorResponse(
                    success=False,
                    processing_time_ms=processing_time,
                    request_id=request_id,
                    error_code="DELETE_FAILED",
                    error_message="Failed to delete session"
                ).dict()
            )
        
    except HTTPException as e:
        processing_time = (time.time() - start_time) * 1000
        
        # Handle known errors (like session not found)
        if isinstance(e.detail, dict):
            error_response = ErrorResponse(
                success=False,
                processing_time_ms=processing_time,
                request_id=request_id,
                error_code=e.detail.get("error_code", "UNKNOWN_ERROR"),
                error_message=e.detail.get("error_message", str(e.detail)),
                details=e.detail.get("details")
            )
            raise HTTPException(status_code=e.status_code, detail=error_response.dict())
        else:
            raise e
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                success=False,
                processing_time_ms=processing_time,
                request_id=request_id,
                error_code="INTERNAL_ERROR",
                error_message="Failed to delete session",
                details={"exception": str(e)}
            ).dict()
        )