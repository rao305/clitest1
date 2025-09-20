#!/usr/bin/env python3
"""
API Middleware
Request tracking, performance monitoring, and security middleware
"""

import time
import secrets
import logging
from typing import Dict, Any, Callable, Optional
from functools import wraps
from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
import json

from .database import get_database_manager


# Request context storage
request_context: Dict[str, Any] = {}


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware for request tracking and performance monitoring"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request with tracking and monitoring"""
        
        # Generate request ID
        request_id = f"req_{secrets.token_urlsafe(8)}"
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Extract request metadata
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        method = request.method
        endpoint = str(request.url.path)
        
        # Get request size
        request_size = len(await request.body()) if hasattr(request, 'body') else 0
        
        # Store in request context
        request_context[request_id] = {
            "start_time": start_time,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "method": method,
            "endpoint": endpoint,
            "request_size": request_size
        }
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            # Get response size
            response_size = 0
            if hasattr(response, 'body'):
                response_size = len(response.body)
            
            # Log to database
            await self._log_request(
                request_id=request_id,
                endpoint=endpoint,
                method=method,
                client_ip=client_ip,
                user_agent=user_agent,
                request_size=request_size,
                response_status=response.status_code,
                response_size=response_size,
                processing_time_ms=processing_time
            )
            
            # Add performance headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Processing-Time"] = f"{processing_time:.2f}ms"
            
            return response
            
        except Exception as e:
            # Calculate processing time for failed requests
            processing_time = (time.time() - start_time) * 1000
            
            # Log failed request
            await self._log_request(
                request_id=request_id,
                endpoint=endpoint,
                method=method,
                client_ip=client_ip,
                user_agent=user_agent,
                request_size=request_size,
                response_status=500,
                response_size=0,
                processing_time_ms=processing_time,
                error=str(e)
            )
            
            # Re-raise the exception
            raise e
        
        finally:
            # Cleanup request context
            if request_id in request_context:
                del request_context[request_id]
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers (common in load balancers)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        return request.client.host if request.client else "unknown"
    
    async def _log_request(self, request_id: str, endpoint: str, method: str,
                          client_ip: str, user_agent: str, request_size: int,
                          response_status: int, response_size: int,
                          processing_time_ms: float, error: str = None):
        """Log request to database"""
        try:
            db_manager = get_database_manager()
            
            db_manager.log_api_request(
                endpoint=endpoint,
                method=method,
                ip_address=client_ip,
                user_agent=user_agent,
                request_size=request_size,
                response_status=response_status,
                response_size=response_size,
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            # Log error but don't fail the request
            logging.error(f"Failed to log request {request_id}: {e}")


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with sliding window"""
    
    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.request_history = {}  # In production, use Redis
        
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Apply rate limiting"""
        
        # Get client identifier
        client_id = self._get_client_id(request)
        current_time = time.time()
        
        # Clean old entries
        self._cleanup_old_requests(client_id, current_time)
        
        # Check rate limits
        if self._is_rate_limited(client_id, current_time):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "error_message": "Too many requests",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Record this request
        self._record_request(client_id, current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self._get_remaining_requests(client_id, current_time)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # In production, might use API key or user ID
        # For now, use IP address
        return self._get_client_ip(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        return request.client.host if request.client else "unknown"
    
    def _cleanup_old_requests(self, client_id: str, current_time: float):
        """Remove old request records"""
        if client_id not in self.request_history:
            self.request_history[client_id] = []
        
        # Keep only requests from last hour
        hour_ago = current_time - 3600
        self.request_history[client_id] = [
            req_time for req_time in self.request_history[client_id]
            if req_time > hour_ago
        ]
    
    def _is_rate_limited(self, client_id: str, current_time: float) -> bool:
        """Check if client is rate limited"""
        if client_id not in self.request_history:
            return False
        
        requests = self.request_history[client_id]
        
        # Check per-minute limit
        minute_ago = current_time - 60
        recent_requests = sum(1 for req_time in requests if req_time > minute_ago)
        
        if recent_requests >= self.requests_per_minute:
            return True
        
        # Check per-hour limit
        if len(requests) >= self.requests_per_hour:
            return True
        
        return False
    
    def _record_request(self, client_id: str, current_time: float):
        """Record a request"""
        if client_id not in self.request_history:
            self.request_history[client_id] = []
        
        self.request_history[client_id].append(current_time)
    
    def _get_remaining_requests(self, client_id: str, current_time: float) -> int:
        """Get remaining requests for client"""
        if client_id not in self.request_history:
            return self.requests_per_minute
        
        minute_ago = current_time - 60
        recent_requests = sum(1 for req_time in self.request_history[client_id] if req_time > minute_ago)
        
        return max(0, self.requests_per_minute - recent_requests)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for headers and validation"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Apply security measures"""
        
        # Validate request size
        if hasattr(request, 'body'):
            body = await request.body()
            if len(body) > 10 * 1024 * 1024:  # 10MB limit
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Request too large"
                )
        
        # Check for malicious patterns in URL
        if self._contains_malicious_patterns(str(request.url)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Malicious request detected"
            )
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response
    
    def _contains_malicious_patterns(self, url: str) -> bool:
        """Check for malicious patterns in URL"""
        malicious_patterns = [
            "../",
            "..\\",
            "<script",
            "javascript:",
            "vbscript:",
            "onload=",
            "onerror=",
            "eval(",
            "setTimeout(",
            "setInterval("
        ]
        
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in malicious_patterns)


# Dependency functions
def get_request_id(request: Request) -> str:
    """Get request ID from request state"""
    return getattr(request.state, 'request_id', 'unknown')


def track_api_call(func: Callable) -> Callable:
    """Decorator to track API endpoint calls"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        """Wrapper function for API call tracking"""
        
        # Extract request if available
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        
        # For now, just call the function
        # In a full implementation, would add more detailed tracking
        return await func(*args, **kwargs)
    
    return wrapper


# Performance monitoring functions
def get_performance_monitor():
    """Get performance monitor instance"""
    # Mock implementation for testing
    class MockPerformanceMonitor:
        def start_request(self):
            return f"req_{secrets.token_urlsafe(8)}"
        
        def end_request(self, request_id: str, success: bool = True):
            pass
        
        def get_performance_summary(self):
            return {
                "current": {
                    "cpu_percent": 25.0,
                    "memory_percent": 45.0
                },
                "averages": {
                    "response_time_ms": 150.0
                }
            }
    
    return MockPerformanceMonitor()


class CORSMiddleware(BaseHTTPMiddleware):
    """CORS middleware for API access"""
    
    def __init__(self, app, allow_origins: list = None, allow_methods: list = None):
        super().__init__(app)
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Handle CORS"""
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-Requested-With"
            response.headers["Access-Control-Max-Age"] = "86400"
            return response
        
        # Process request
        response = await call_next(request)
        
        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response