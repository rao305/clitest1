# Boiler AI Academic Advisor API Documentation

## Overview

The Boiler AI Academic Advisor API provides comprehensive academic guidance services for Purdue Computer Science students. Built with FastAPI, it offers high-performance, secure, and scalable endpoints for session management, academic planning, course information, and advisory services.

## Architecture

### Technology Stack
- **Framework**: FastAPI 0.104.1
- **Authentication**: JWT with bcrypt password hashing
- **Database**: SQLite with connection pooling
- **Validation**: Pydantic v2 schemas
- **Testing**: pytest with 85%+ coverage requirement
- **Security**: Multiple middleware layers with rate limiting

### Key Features
- 🔒 **JWT-based Authentication** with role-based access control
- ⚡ **High Performance** with connection pooling and caching
- 🛡️ **Security First** with comprehensive middleware stack
- 📊 **Real-time Monitoring** with performance tracking
- 🧪 **Test-Driven Development** with comprehensive test suite
- 📝 **Comprehensive Validation** with Pydantic schemas

## API Endpoints

### Base URL
```
Production: https://api.boilerai.com
Development: http://localhost:8000
```

### Authentication

All API endpoints require Bearer token authentication except for health checks and registration.

```http
Authorization: Bearer <jwt_token>
```

## Session Management

### Create Session
Create a new conversation session with optional initial context.

```http
POST /api/v1/sessions
Content-Type: application/json
Authorization: Bearer <token>

{
  "student_id": "student123",
  "initial_context": {
    "current_year": "sophomore",
    "gpa": 3.2,
    "completed_courses": ["CS 18000", "CS 18200"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2024-12-01T14:30:22Z",
  "processing_time_ms": 15.2,
  "request_id": "req_abc123",
  "session_id": "session_20241201_143022_xyz789",
  "expires_at": "2024-12-01T18:30:22Z",
  "context": {
    "current_year": "sophomore",
    "gpa": 3.2,
    "completed_courses": ["CS 18000", "CS 18200"],
    "conversation_count": 0
  }
}
```

**Status Codes:**
- `201 Created` - Session created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `500 Internal Server Error` - Server error

### Get Session
Retrieve session information and current context.

```http
GET /api/v1/sessions/{session_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2024-12-01T14:30:25Z",
  "processing_time_ms": 8.7,
  "request_id": "req_def456",
  "session_id": "session_20241201_143022_xyz789",
  "expires_at": "2024-12-01T18:30:22Z",
  "context": {
    "current_year": "sophomore",
    "gpa": 3.2,
    "completed_courses": ["CS 18000", "CS 18200"],
    "conversation_count": 5,
    "last_topic": "course_info"
  }
}
```

**Status Codes:**
- `200 OK` - Session retrieved successfully
- `404 Not Found` - Session not found
- `410 Gone` - Session expired
- `401 Unauthorized` - Authentication required

### Update Session
Update session context data.

```http
PATCH /api/v1/sessions/{session_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "context_updates": {
    "current_year": "junior",
    "gpa": 3.5,
    "completed_courses": ["CS 18000", "CS 18200", "CS 25100"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2024-12-01T14:35:00Z",
  "processing_time_ms": 12.3,
  "request_id": "req_ghi789",
  "session_id": "session_20241201_143022_xyz789",
  "expires_at": "2024-12-01T18:30:22Z",
  "context": {
    "current_year": "junior",
    "gpa": 3.5,
    "completed_courses": ["CS 18000", "CS 18200", "CS 25100"],
    "conversation_count": 5
  }
}
```

**Status Codes:**
- `200 OK` - Session updated successfully
- `400 Bad Request` - Invalid context data
- `404 Not Found` - Session not found
- `422 Unprocessable Entity` - Validation errors

### Delete Session
Delete/deactivate a session.

```http
DELETE /api/v1/sessions/{session_id}
Authorization: Bearer <token>
```

**Response:**
- `204 No Content` - Session deleted successfully
- `404 Not Found` - Session not found
- `401 Unauthorized` - Authentication required

## Authentication Endpoints

### Register
Register a new user account.

```http
POST /auth/register
Content-Type: application/json

{
  "username": "jdoe",
  "email": "jdoe@purdue.edu",
  "password": "securepassword123",
  "student_id": "student123",
  "is_student": true
}
```

### Login
Authenticate user and receive JWT tokens.

```http
POST /auth/login
Content-Type: application/json

{
  "username": "jdoe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user_info": {
    "user_id": "user123",
    "username": "jdoe",
    "email": "jdoe@purdue.edu",
    "is_student": true,
    "permissions": ["read", "write", "student"]
  }
}
```

### Refresh Token
Generate new access token using refresh token.

```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Logout
Revoke tokens and logout user.

```http
POST /auth/logout
Authorization: Bearer <token>
```

## System Endpoints

### Health Check
Check system health and component status.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "checks": {
    "database": "healthy",
    "knowledge_base": "healthy",
    "ai_service": "healthy",
    "response_time": "15.2ms"
  },
  "timestamp": "2024-12-01T14:50:00Z",
  "uptime_seconds": 3600.5
}
```

### API Information
Get detailed API information and capabilities.

```http
GET /api/info
```

**Response:**
```json
{
  "api": {
    "name": "Boiler AI Academic Advisor API",
    "version": "1.0.0",
    "environment": "production",
    "uptime_seconds": 3600.5
  },
  "features": {
    "session_management": true,
    "academic_planning": true,
    "course_information": true,
    "failure_recovery": true,
    "track_guidance": true,
    "codo_support": true,
    "performance_monitoring": true
  },
  "limits": {
    "requests_per_minute": 60,
    "requests_per_hour": 1000,
    "max_request_size": "10MB",
    "session_timeout": "4 hours"
  }
}
```

## Data Models

### Session Context
```typescript
interface SessionContext {
  current_year?: "freshman" | "sophomore" | "junior" | "senior" | "graduate";
  gpa?: number; // 0.0 - 4.0
  completed_courses?: string[];
  failed_courses?: string[];
  target_track?: "Machine Intelligence" | "Software Engineering" | "Systems Programming" | "Security" | "General";
  graduation_goal?: string;
  student_id?: string;
  conversation_count?: number;
  last_topic?: string;
  preferences?: object;
}
```

### User Permissions
```typescript
type Permission = "read" | "write" | "admin" | "student" | "advisor";

interface User {
  user_id: string;
  username: string;
  email: string;
  is_student: boolean;
  student_id?: string;
  permissions: Permission[];
}
```

## Error Handling

All API errors follow a consistent format:

```json
{
  "success": false,
  "timestamp": "2024-12-01T14:45:00Z",
  "processing_time_ms": 5.2,
  "request_id": "req_error123",
  "error_code": "SESSION_NOT_FOUND",
  "error_message": "Session not found or expired",
  "details": {
    "session_id": "invalid_session_123",
    "suggestion": "Create a new session"
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR` - Request validation failed
- `SESSION_NOT_FOUND` - Session doesn't exist
- `SESSION_EXPIRED` - Session has expired
- `AUTHENTICATION_REQUIRED` - Valid token required
- `PERMISSION_DENIED` - Insufficient permissions
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_ERROR` - Server error

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **60 requests per minute** per IP address
- **1000 requests per hour** per IP address

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1701434400
```

When rate limited (429 status):
```json
{
  "error_code": "RATE_LIMIT_EXCEEDED",
  "error_message": "Too many requests",
  "retry_after": 60
}
```

## Security

### Authentication Security
- **JWT tokens** with 30-minute expiration
- **Refresh tokens** with 7-day expiration
- **bcrypt password hashing** with salt
- **Account lockout** after 5 failed attempts (15-minute lock)
- **Secure session IDs** with cryptographic randomness

### Request Security
- **Input validation** for all requests
- **SQL injection prevention** with parameterized queries
- **XSS protection** headers
- **CSRF protection** for state-changing operations
- **Request size limits** (10MB maximum)
- **Malicious pattern detection** in URLs

### Network Security
- **TLS encryption** for all communications
- **CORS configuration** for browser security
- **Security headers** (HSTS, CSP, X-Frame-Options)
- **IP-based rate limiting**

## Performance

### Response Times
- **Session operations**: < 100ms average
- **Authentication**: < 200ms average
- **Database queries**: < 50ms average
- **Health checks**: < 10ms average

### Scalability
- **Connection pooling** for database efficiency
- **Request tracking** for performance monitoring
- **Automatic cleanup** of expired sessions
- **Performance metrics** collection and analysis

### Monitoring
- **Real-time performance tracking**
- **Request/response logging**
- **Error rate monitoring**
- **System resource tracking**

## Development

### Local Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export JWT_SECRET_KEY="your-secret-key"
export OPENAI_API_KEY="your-openai-key"

# Run development server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run all tests with coverage
pytest --cov=api --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m security
pytest -m performance
```

### API Documentation
- **Interactive docs**: `/docs` (Swagger UI)
- **Alternative docs**: `/redoc` (ReDoc)
- **OpenAPI spec**: `/openapi.json`

## Production Deployment

### Environment Variables
```bash
ENVIRONMENT=production
JWT_SECRET_KEY=<secure-random-key>
OPENAI_API_KEY=<your-openai-key>
DATABASE_URL=<database-connection-string>
```

### Health Monitoring
- Monitor `/health` endpoint for system status
- Set up alerts for response time > 1000ms
- Monitor error rates and set alerts for > 1%
- Track database connection pool utilization

### Scaling Considerations
- Use load balancer for multiple API instances
- Implement Redis for session storage in multi-instance setup
- Monitor database performance and add read replicas if needed
- Implement caching layer for knowledge base queries

## Support

### Contact Information
- **Email**: support@boilerai.com
- **Documentation**: `/docs`
- **Health Status**: `/health`
- **API Info**: `/api/info`

### Troubleshooting
1. Check health endpoint for system status
2. Verify authentication tokens are valid
3. Review rate limiting headers
4. Check request format against schemas
5. Monitor error logs for detailed information

---

*Last Updated: December 1, 2024*
*API Version: 1.0.0*