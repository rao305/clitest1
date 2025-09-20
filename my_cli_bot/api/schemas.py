#!/usr/bin/env python3
"""
API Data Schemas and Models
Pydantic models for request/response validation with comprehensive typing
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class StudentYear(str, Enum):
    """Student academic year enumeration"""
    FRESHMAN = "freshman"
    SOPHOMORE = "sophomore"
    JUNIOR = "junior"
    SENIOR = "senior"
    GRADUATE = "graduate"


class Track(str, Enum):
    """CS track specialization options"""
    MACHINE_INTELLIGENCE = "Machine Intelligence"
    SOFTWARE_ENGINEERING = "Software Engineering"
    SYSTEMS_PROGRAMMING = "Systems Programming"
    SECURITY = "Security"
    GENERAL = "General"


class QueryType(str, Enum):
    """Query classification types"""
    COURSE_INFO = "course_info"
    GRADUATION_PLANNING = "graduation_planning"
    TRACK_INFO = "track_info"
    CODO_ADVICE = "codo_advice"
    FAILURE_RECOVERY = "failure_recovery"
    CAREER_GUIDANCE = "career_guidance"
    GENERAL = "general"
    GREETING = "greeting"


# Request Models
class SessionCreateRequest(BaseModel):
    """Request to create new conversation session"""
    student_id: Optional[str] = Field(None, description="Optional student identifier")
    initial_context: Optional[Dict[str, Any]] = Field(None, description="Initial context data")
    
    class Config:
        schema_extra = {
            "example": {
                "student_id": "student123",
                "initial_context": {
                    "current_year": "sophomore",
                    "gpa": 3.2,
                    "completed_courses": ["CS 18000", "CS 18200"]
                }
            }
        }


class QueryRequest(BaseModel):
    """Request for processing user query"""
    query: str = Field(..., min_length=1, max_length=2000, description="User question or request")
    session_id: str = Field(..., description="Active session identifier")
    context_override: Optional[Dict[str, Any]] = Field(None, description="Context data to merge")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What is CS 18000 and when should I take it?",
                "session_id": "session_20241201_143022",
                "context_override": {"current_year": "freshman"}
            }
        }


class CourseInfoRequest(BaseModel):
    """Request for specific course information"""
    course_code: str = Field(..., pattern=r"^[A-Z]{2,4}\s?\d{3,5}$", description="Course code (e.g., CS 18000)")
    include_prerequisites: bool = Field(True, description="Include prerequisite information")
    include_corequisites: bool = Field(True, description="Include corequisite information")
    
    class Config:
        schema_extra = {
            "example": {
                "course_code": "CS 25100",
                "include_prerequisites": True,
                "include_corequisites": True
            }
        }


class GraduationPlanRequest(BaseModel):
    """Request for graduation planning analysis"""
    student_profile: Dict[str, Any] = Field(..., description="Student academic profile")
    target_graduation: Optional[str] = Field(None, description="Target graduation semester")
    preferred_track: Optional[Track] = Field(None, description="Preferred CS track")
    
    @validator('student_profile')
    def validate_profile(cls, v):
        required_fields = ['current_year', 'completed_courses']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Missing required field: {field}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "student_profile": {
                    "current_year": "sophomore",
                    "gpa": 3.5,
                    "completed_courses": ["CS 18000", "CS 18200", "MA 16100"],
                    "failed_courses": [],
                    "target_track": "Machine Intelligence"
                },
                "target_graduation": "Fall 2026",
                "preferred_track": "Machine Intelligence"
            }
        }


class FailureAnalysisRequest(BaseModel):
    """Request for course failure impact analysis"""
    failed_course: str = Field(..., pattern=r"^[A-Z]{2,4}\s?\d{3,5}$")
    failure_semester: str = Field(..., description="Semester when failure occurred")
    student_profile: Dict[str, Any] = Field(..., description="Current student profile")
    
    class Config:
        schema_extra = {
            "example": {
                "failed_course": "CS 25100",
                "failure_semester": "Fall 2024",
                "student_profile": {
                    "current_year": "sophomore",
                    "completed_courses": ["CS 18000", "CS 18200", "CS 24000"],
                    "gpa": 2.8
                }
            }
        }


# Response Models
class APIResponse(BaseModel):
    """Base API response with metadata"""
    success: bool = Field(..., description="Request success status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    request_id: Optional[str] = Field(None, description="Unique request identifier")


class SessionResponse(APIResponse):
    """Response for session operations"""
    session_id: str = Field(..., description="Session identifier")
    expires_at: Optional[datetime] = Field(None, description="Session expiration time")
    context: Optional[Dict[str, Any]] = Field(None, description="Session context data")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "timestamp": "2024-12-01T14:30:22Z",
                "processing_time_ms": 15.2,
                "session_id": "session_20241201_143022",
                "expires_at": "2024-12-01T18:30:22Z",
                "context": {
                    "current_year": "sophomore",
                    "conversation_count": 0
                }
            }
        }


class QueryResponse(APIResponse):
    """Response for query processing"""
    response: str = Field(..., description="AI-generated response")
    intent: QueryType = Field(..., description="Classified query intent")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Intent classification confidence")
    context_updates: Optional[Dict[str, Any]] = Field(None, description="Context updates from query")
    related_resources: Optional[List[str]] = Field(None, description="Related courses, resources")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "timestamp": "2024-12-01T14:30:25Z",
                "processing_time_ms": 850.3,
                "response": "CS 18000 is Programming I, the first course in the CS sequence...",
                "intent": "course_info",
                "confidence": 0.95,
                "context_updates": {
                    "mentioned_courses": ["CS 18000"],
                    "current_topic": "course_info"
                },
                "related_resources": ["CS 18200", "Programming fundamentals"]
            }
        }


class CourseInfoResponse(APIResponse):
    """Response for course information requests"""
    course_code: str = Field(..., description="Course code")
    course_info: Dict[str, Any] = Field(..., description="Complete course information")
    prerequisites: Optional[List[str]] = Field(None, description="Required prerequisites")
    corequisites: Optional[List[str]] = Field(None, description="Required corequisites")
    difficulty_rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Difficulty rating")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "timestamp": "2024-12-01T14:30:30Z",
                "processing_time_ms": 25.1,
                "course_code": "CS 25100",
                "course_info": {
                    "title": "Data Structures and Algorithms",
                    "credits": 3,
                    "description": "Introduction to data structures and algorithms...",
                    "typical_semester": ["Fall", "Spring"]
                },
                "prerequisites": ["CS 18000", "CS 18200"],
                "corequisites": ["MA 26100"],
                "difficulty_rating": 4.2
            }
        }


class GraduationPlanResponse(APIResponse):
    """Response for graduation planning"""
    feasibility_score: float = Field(..., ge=0.0, le=1.0, description="Plan feasibility score")
    recommended_timeline: Dict[str, List[str]] = Field(..., description="Semester-by-semester plan")
    graduation_date: str = Field(..., description="Projected graduation date")
    requirements_status: Dict[str, Any] = Field(..., description="Requirement completion status")
    warnings: List[str] = Field(default_factory=list, description="Plan warnings or issues")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "timestamp": "2024-12-01T14:35:00Z",
                "processing_time_ms": 1250.8,
                "feasibility_score": 0.85,
                "recommended_timeline": {
                    "Spring 2025": ["CS 25000", "CS 25100", "MA 26500"],
                    "Fall 2025": ["CS 25200", "CS 37300", "STAT 35000"]
                },
                "graduation_date": "May 2027",
                "requirements_status": {
                    "core_cs_completed": 18,
                    "core_cs_remaining": 11,
                    "track_completed": 0,
                    "track_remaining": 12
                },
                "warnings": ["Heavy course load in Spring 2025"]
            }
        }


class FailureAnalysisResponse(APIResponse):
    """Response for failure impact analysis"""
    delay_impact: Dict[str, Any] = Field(..., description="Graduation delay analysis")
    recovery_options: List[Dict[str, Any]] = Field(..., description="Recovery strategies")
    affected_courses: List[str] = Field(..., description="Courses affected by failure")
    recommended_actions: List[str] = Field(..., description="Recommended recovery actions")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "timestamp": "2024-12-01T14:40:00Z",
                "processing_time_ms": 450.2,
                "delay_impact": {
                    "semester_delay": 1,
                    "graduation_pushback": "Spring 2027 → Fall 2027",
                    "affected_timeline": True
                },
                "recovery_options": [
                    {
                        "strategy": "Summer Course",
                        "timeline": "Summer 2025",
                        "cost": "Additional tuition",
                        "feasibility": 0.9
                    }
                ],
                "affected_courses": ["CS 25200", "CS 37300"],
                "recommended_actions": [
                    "Retake CS 25100 in Spring 2025",
                    "Consider tutoring resources",
                    "Review prerequisite material"
                ]
            }
        }


class ErrorResponse(APIResponse):
    """Error response with details"""
    error_code: str = Field(..., description="Error classification code")
    error_message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "timestamp": "2024-12-01T14:45:00Z",
                "error_code": "INVALID_SESSION",
                "error_message": "Session not found or expired",
                "details": {
                    "session_id": "invalid_session_123",
                    "suggestion": "Create a new session"
                }
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="API version")
    checks: Dict[str, str] = Field(..., description="Individual component health")
    timestamp: datetime = Field(default_factory=datetime.now)
    uptime_seconds: Optional[float] = Field(None, description="Service uptime")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "checks": {
                    "database": "healthy",
                    "knowledge_base": "healthy",
                    "ai_service": "healthy"
                },
                "timestamp": "2024-12-01T14:50:00Z",
                "uptime_seconds": 3600.5
            }
        }


# Utility Models
class ValidationError(BaseModel):
    """Validation error details"""
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Validation error message")
    value: Optional[Any] = Field(None, description="Invalid value provided")


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number (1-based)")
    size: int = Field(20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PaginatedResponse(APIResponse):
    """Paginated response wrapper"""
    items: List[Any] = Field(..., description="Response items")
    total: int = Field(..., ge=0, description="Total items available")
    page: int = Field(..., ge=1, description="Current page")
    size: int = Field(..., ge=1, description="Items per page")
    has_next: bool = Field(..., description="More pages available")
    has_prev: bool = Field(..., description="Previous pages available")