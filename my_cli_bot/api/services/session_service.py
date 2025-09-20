#!/usr/bin/env python3
"""
Session Management Service
Business logic for session operations with optimized performance
"""

import secrets
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status

from ..database import get_database_manager
from ..schemas import SessionCreateRequest, SessionResponse


class SessionService:
    """Session management service with business logic"""
    
    def __init__(self):
        self.db_manager = get_database_manager()
        self.session_timeout_hours = 4
        self.max_sessions_per_user = 10
    
    def create_session(self, request: SessionCreateRequest) -> Dict[str, Any]:
        """Create new session with validation and optimization"""
        
        # Generate secure session ID
        session_id = self._generate_session_id()
        
        # Validate and sanitize initial context
        sanitized_context = self._sanitize_context(request.initial_context or {})
        
        # Check session limits for user
        if request.student_id:
            self._enforce_session_limits(request.student_id)
        
        # Create session in database
        success = self.db_manager.create_session(
            session_id=session_id,
            student_id=request.student_id,
            context_data=sanitized_context
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create session"
            )
        
        # Calculate expiration time
        expires_at = datetime.now() + timedelta(hours=self.session_timeout_hours)
        
        return {
            "session_id": session_id,
            "expires_at": expires_at,
            "context": sanitized_context
        }
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session with validation"""
        
        # Validate session ID format
        if not self._is_valid_session_id(session_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session ID format"
            )
        
        # Get session from database
        session = self.db_manager.get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_code": "SESSION_NOT_FOUND",
                    "error_message": "Session not found or expired"
                }
            )
        
        # Check if session is expired
        if self._is_session_expired(session):
            # Mark as inactive
            self.db_manager.update_session(session_id, {"is_active": False})
            
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail={
                    "error_code": "SESSION_EXPIRED",
                    "error_message": "Session has expired"
                }
            )
        
        return {
            "session_id": session['id'],
            "expires_at": session['expires_at'],
            "context": session['context_data'] or {}
        }
    
    def update_session(self, session_id: str, context_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update session context with validation"""
        
        # Validate session exists and is active
        session = self.get_session(session_id)  # This will raise if invalid
        
        # Validate and sanitize updates
        sanitized_updates = self._sanitize_context(context_updates)
        
        # Validate context updates
        validation_errors = self._validate_context_updates(sanitized_updates)
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "VALIDATION_ERROR",
                    "error_message": "Invalid context data",
                    "validation_errors": validation_errors
                }
            )
        
        # Update session
        success = self.db_manager.update_session(session_id, sanitized_updates)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update session"
            )
        
        # Return updated session
        return self.get_session(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete/deactivate session"""
        
        # Check if session exists
        session = self.db_manager.get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_code": "SESSION_NOT_FOUND",
                    "error_message": "Session not found"
                }
            )
        
        # Deactivate session
        success = self.db_manager.update_session(session_id, {"is_active": False})
        
        return success
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions (background task)"""
        return self.db_manager.cleanup_expired_sessions()
    
    def get_user_sessions(self, student_id: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all sessions for a user"""
        # Implementation would query database for user sessions
        # For now, return empty list
        return []
    
    def _generate_session_id(self) -> str:
        """Generate cryptographically secure session ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_part = secrets.token_urlsafe(16)
        return f"session_{timestamp}_{random_part}"
    
    def _is_valid_session_id(self, session_id: str) -> bool:
        """Validate session ID format"""
        if not session_id or not isinstance(session_id, str):
            return False
        
        # Basic format validation
        if not session_id.startswith("session_"):
            return False
        
        # Check length (should be reasonable)
        if len(session_id) < 20 or len(session_id) > 100:
            return False
        
        # Check for dangerous characters
        dangerous_chars = ['..', '/', '\\', ';', '--', '<', '>', '"', "'"]
        for char in dangerous_chars:
            if char in session_id:
                return False
        
        return True
    
    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize and validate context data"""
        if not context:
            return {}
        
        sanitized = {}
        
        # Allowed context fields with validation
        allowed_fields = {
            'current_year': ['freshman', 'sophomore', 'junior', 'senior', 'graduate'],
            'gpa': lambda x: isinstance(x, (int, float)) and 0.0 <= x <= 4.0,
            'completed_courses': lambda x: isinstance(x, list) and all(isinstance(c, str) for c in x),
            'failed_courses': lambda x: isinstance(x, list) and all(isinstance(c, str) for c in x),
            'target_track': ['Machine Intelligence', 'Software Engineering', 'Systems Programming', 'Security', 'General'],
            'graduation_goal': lambda x: isinstance(x, str),
            'student_id': lambda x: isinstance(x, str) and len(x) <= 50,
            'conversation_count': lambda x: isinstance(x, int) and x >= 0,
            'last_topic': lambda x: isinstance(x, str) and len(x) <= 100,
            'preferences': lambda x: isinstance(x, dict)
        }
        
        for field, value in context.items():
            if field in allowed_fields:
                validator = allowed_fields[field]
                
                if isinstance(validator, list):
                    # Enum validation
                    if value in validator:
                        sanitized[field] = value
                elif callable(validator):
                    # Function validation
                    if validator(value):
                        sanitized[field] = value
                else:
                    # Direct assignment for simple cases
                    sanitized[field] = value
        
        return sanitized
    
    def _validate_context_updates(self, updates: Dict[str, Any]) -> List[Dict[str, str]]:
        """Validate context updates and return error list"""
        errors = []
        
        # GPA validation
        if 'gpa' in updates:
            gpa = updates['gpa']
            if not isinstance(gpa, (int, float)):
                errors.append({
                    "field": "gpa",
                    "message": "GPA must be a number",
                    "value": str(gpa)
                })
            elif not (0.0 <= gpa <= 4.0):
                errors.append({
                    "field": "gpa",
                    "message": "GPA must be between 0.0 and 4.0",
                    "value": str(gpa)
                })
        
        # Course list validation
        for field in ['completed_courses', 'failed_courses']:
            if field in updates:
                courses = updates[field]
                if not isinstance(courses, list):
                    errors.append({
                        "field": field,
                        "message": f"{field} must be a list",
                        "value": str(type(courses))
                    })
                elif not all(isinstance(c, str) for c in courses):
                    errors.append({
                        "field": field,
                        "message": f"All items in {field} must be strings",
                        "value": str(courses)
                    })
        
        return errors
    
    def _enforce_session_limits(self, student_id: str):
        """Enforce session limits per user"""
        # For now, just a placeholder
        # In real implementation, would check active session count
        pass
    
    def _is_session_expired(self, session: Dict[str, Any]) -> bool:
        """Check if session is expired"""
        if not session.get('expires_at'):
            return False
        
        try:
            expires_at = datetime.fromisoformat(session['expires_at'])
            return expires_at <= datetime.now()
        except (ValueError, TypeError):
            return True


# Global service instance
_session_service: Optional[SessionService] = None


def get_session_service() -> SessionService:
    """Get or create global session service instance"""
    global _session_service
    if _session_service is None:
        _session_service = SessionService()
    return _session_service


# Helper function for testing
def is_session_expired(session: Dict[str, Any]) -> bool:
    """Helper function to check if session is expired (for testing)"""
    service = get_session_service()
    return service._is_session_expired(session)