#!/usr/bin/env python3
"""
Authentication and Authorization System
Secure JWT-based authentication with role-based access control
"""

import os
import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import sqlite3
from dataclasses import dataclass


# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


# Security scheme
security = HTTPBearer()


@dataclass
class UserPermissions:
    """User permission levels"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    STUDENT = "student"
    ADVISOR = "advisor"


class TokenData(BaseModel):
    """JWT token data structure"""
    user_id: str
    username: str
    email: str
    permissions: List[str]
    exp: datetime
    iat: datetime
    is_student: bool = False
    student_id: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "username": "jdoe",
                "email": "jdoe@purdue.edu",
                "permissions": ["read", "write", "student"],
                "exp": "2024-12-01T15:30:00Z",
                "iat": "2024-12-01T14:30:00Z",
                "is_student": True,
                "student_id": "student123"
            }
        }


class LoginRequest(BaseModel):
    """Login request model"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    
    class Config:
        schema_extra = {
            "example": {
                "username": "jdoe",
                "password": "securepassword123"
            }
        }


class RegisterRequest(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    password: str = Field(..., min_length=8, max_length=128)
    student_id: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9]+$")
    is_student: bool = Field(True, description="Whether user is a student")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "jdoe",
                "email": "jdoe@purdue.edu",
                "password": "securepassword123",
                "student_id": "student123",
                "is_student": True
            }
        }


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user_info": {
                    "user_id": "user123",
                    "username": "jdoe",
                    "email": "jdoe@purdue.edu",
                    "is_student": True
                }
            }
        }


class AuthManager:
    """Comprehensive authentication manager"""
    
    def __init__(self, db_path: str = "purdue_cs_knowledge.db"):
        self.db_path = db_path
        self._initialize_auth_tables()
    
    def _initialize_auth_tables(self):
        """Initialize authentication tables"""
        conn = sqlite3.connect(self.db_path)
        
        # Users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                student_id TEXT,
                is_student BOOLEAN DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )
        ''')
        
        # User permissions table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_permissions (
                user_id TEXT,
                permission TEXT,
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                granted_by TEXT,
                PRIMARY KEY (user_id, permission),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Refresh tokens table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                token_hash TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Login audit table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS login_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                username TEXT,
                ip_address TEXT,
                user_agent TEXT,
                success BOOLEAN,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                failure_reason TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def _generate_user_id(self) -> str:
        """Generate unique user ID"""
        return f"user_{secrets.token_urlsafe(16)}"
    
    def register_user(self, registration: RegisterRequest) -> Dict[str, Any]:
        """Register new user with validation"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Check if username or email already exists
            cursor = conn.execute(
                "SELECT username, email FROM users WHERE username = ? OR email = ?",
                (registration.username, registration.email)
            )
            existing = cursor.fetchone()
            
            if existing:
                if existing[0] == registration.username:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Username already exists"
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Email already registered"
                    )
            
            # Validate Purdue email for students
            if registration.is_student and not registration.email.endswith('@purdue.edu'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Students must use Purdue email address"
                )
            
            # Create user
            user_id = self._generate_user_id()
            password_hash = self._hash_password(registration.password)
            
            conn.execute('''
                INSERT INTO users (id, username, email, password_hash, student_id, is_student)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                registration.username,
                registration.email,
                password_hash,
                registration.student_id,
                registration.is_student
            ))
            
            # Assign default permissions
            default_permissions = [UserPermissions.READ, UserPermissions.WRITE]
            if registration.is_student:
                default_permissions.append(UserPermissions.STUDENT)
            
            for permission in default_permissions:
                conn.execute('''
                    INSERT INTO user_permissions (user_id, permission)
                    VALUES (?, ?)
                ''', (user_id, permission))
            
            conn.commit()
            
            return {
                "user_id": user_id,
                "username": registration.username,
                "email": registration.email,
                "is_student": registration.is_student,
                "permissions": default_permissions
            }
            
        except sqlite3.IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User registration failed due to constraint violation"
            )
        finally:
            conn.close()
    
    def authenticate_user(self, username: str, password: str, ip_address: str = None, user_agent: str = None) -> Optional[Dict[str, Any]]:
        """Authenticate user with rate limiting and audit logging"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Check if user exists and is not locked
            cursor = conn.execute('''
                SELECT id, username, email, password_hash, student_id, is_student, 
                       failed_login_attempts, locked_until
                FROM users 
                WHERE username = ? AND is_active = 1
            ''', (username,))
            
            user = cursor.fetchone()
            
            # Log failed attempt if user not found
            if not user:
                self._log_login_attempt(conn, None, username, ip_address, user_agent, False, "User not found")
                conn.commit()
                return None
            
            user_id, username, email, password_hash, student_id, is_student, failed_attempts, locked_until = user
            
            # Check if account is locked
            if locked_until and datetime.fromisoformat(locked_until) > datetime.now():
                self._log_login_attempt(conn, user_id, username, ip_address, user_agent, False, "Account locked")
                conn.commit()
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail="Account temporarily locked due to failed login attempts"
                )
            
            # Verify password
            if not self._verify_password(password, password_hash):
                # Increment failed attempts
                failed_attempts += 1
                lock_duration = None
                
                # Lock account after 5 failed attempts
                if failed_attempts >= 5:
                    lock_duration = datetime.now() + timedelta(minutes=15)
                
                conn.execute('''
                    UPDATE users 
                    SET failed_login_attempts = ?, locked_until = ?
                    WHERE id = ?
                ''', (failed_attempts, lock_duration, user_id))
                
                self._log_login_attempt(conn, user_id, username, ip_address, user_agent, False, "Invalid password")
                conn.commit()
                return None
            
            # Reset failed attempts on successful login
            conn.execute('''
                UPDATE users 
                SET failed_login_attempts = 0, locked_until = NULL, last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user_id,))
            
            # Get user permissions
            cursor = conn.execute(
                "SELECT permission FROM user_permissions WHERE user_id = ?",
                (user_id,)
            )
            permissions = [row[0] for row in cursor.fetchall()]
            
            # Log successful login
            self._log_login_attempt(conn, user_id, username, ip_address, user_agent, True, None)
            conn.commit()
            
            return {
                "user_id": user_id,
                "username": username,
                "email": email,
                "student_id": student_id,
                "is_student": bool(is_student),
                "permissions": permissions
            }
            
        finally:
            conn.close()
    
    def _log_login_attempt(self, conn, user_id: str, username: str, ip_address: str, user_agent: str, success: bool, failure_reason: str):
        """Log login attempt for audit purposes"""
        conn.execute('''
            INSERT INTO login_audit (user_id, username, ip_address, user_agent, success, failure_reason)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, ip_address, user_agent, success, failure_reason))
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        now = datetime.utcnow()
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "user_id": user_data["user_id"],
            "username": user_data["username"],
            "email": user_data["email"],
            "permissions": user_data["permissions"],
            "is_student": user_data["is_student"],
            "student_id": user_data.get("student_id"),
            "iat": now,
            "exp": expire,
            "type": "access"
        }
        
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token and store in database"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            now = datetime.utcnow()
            expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            
            token_id = secrets.token_urlsafe(32)
            token_data = {
                "token_id": token_id,
                "user_id": user_id,
                "exp": expire,
                "iat": now,
                "type": "refresh"
            }
            
            refresh_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
            
            # Store token hash in database
            token_hash = bcrypt.hashpw(refresh_token.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            conn.execute('''
                INSERT INTO refresh_tokens (id, user_id, token_hash, expires_at)
                VALUES (?, ?, ?, ?)
            ''', (token_id, user_id, token_hash, expire))
            
            conn.commit()
            return refresh_token
            
        finally:
            conn.close()
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Check token expiration
            if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
                return None
            
            return payload
            
        except jwt.InvalidTokenError:
            return None
    
    def revoke_refresh_token(self, token: str) -> bool:
        """Revoke refresh token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            token_id = payload.get("token_id")
            
            if not token_id:
                return False
            
            conn = sqlite3.connect(self.db_path)
            
            try:
                conn.execute(
                    "UPDATE refresh_tokens SET is_active = 0 WHERE id = ?",
                    (token_id,)
                )
                conn.commit()
                return True
                
            finally:
                conn.close()
                
        except jwt.InvalidTokenError:
            return False
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Generate new access token from refresh token"""
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            token_id = payload.get("token_id")
            user_id = payload.get("user_id")
            
            if not token_id or not user_id:
                return None
            
            # Verify refresh token exists and is active
            conn = sqlite3.connect(self.db_path)
            
            try:
                cursor = conn.execute('''
                    SELECT token_hash, expires_at FROM refresh_tokens 
                    WHERE id = ? AND user_id = ? AND is_active = 1
                ''', (token_id, user_id))
                
                token_data = cursor.fetchone()
                if not token_data:
                    return None
                
                token_hash, expires_at = token_data
                
                # Check if token is expired
                if datetime.fromisoformat(expires_at) < datetime.utcnow():
                    return None
                
                # Get current user data
                cursor = conn.execute('''
                    SELECT username, email, student_id, is_student 
                    FROM users WHERE id = ? AND is_active = 1
                ''', (user_id,))
                
                user_data = cursor.fetchone()
                if not user_data:
                    return None
                
                username, email, student_id, is_student = user_data
                
                # Get permissions
                cursor = conn.execute(
                    "SELECT permission FROM user_permissions WHERE user_id = ?",
                    (user_id,)
                )
                permissions = [row[0] for row in cursor.fetchall()]
                
                # Create new access token
                user_info = {
                    "user_id": user_id,
                    "username": username,
                    "email": email,
                    "student_id": student_id,
                    "is_student": bool(is_student),
                    "permissions": permissions
                }
                
                return self.create_access_token(user_info)
                
            finally:
                conn.close()
                
        except jwt.InvalidTokenError:
            return None


# Global auth manager instance
auth_manager = AuthManager()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    
    payload = auth_manager.verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify user still exists and is active
    conn = sqlite3.connect(auth_manager.db_path)
    try:
        cursor = conn.execute(
            "SELECT is_active FROM users WHERE id = ?",
            (payload["user_id"],)
        )
        user = cursor.fetchone()
        
        if not user or not user[0]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    finally:
        conn.close()


def require_permission(required_permission: str):
    """Decorator to require specific permission"""
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        if required_permission not in current_user.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{required_permission}' required"
            )
        return current_user
    
    return permission_checker


def require_student():
    """Require user to be a student"""
    def student_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        if not current_user.get("is_student", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Student access required"
            )
        return current_user
    
    return student_checker


def require_admin():
    """Require admin permission"""
    return require_permission(UserPermissions.ADMIN)


# Rate limiting decorator
def rate_limit(max_requests: int, window_seconds: int):
    """Rate limiting decorator"""
    from collections import defaultdict
    from time import time
    
    request_counts = defaultdict(list)
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            # In a real implementation, you'd use Redis or similar
            # For now, using in-memory storage
            current_time = time()
            client_id = "global"  # Would extract from request in real implementation
            
            # Clean old requests
            request_counts[client_id] = [
                req_time for req_time in request_counts[client_id]
                if current_time - req_time < window_seconds
            ]
            
            # Check rate limit
            if len(request_counts[client_id]) >= max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            # Record this request
            request_counts[client_id].append(current_time)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator