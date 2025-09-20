#!/usr/bin/env python3
"""
High-Performance Session Manager
Optimizes database queries, implements caching, and reduces serialization overhead
"""

import sqlite3
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from functools import lru_cache
from dataclasses import dataclass, asdict
import msgpack  # Much faster than JSON for serialization

from .connection_pool import get_connection, initialize_pool


@dataclass
class SessionData:
    """Strongly typed session data for better performance"""
    session_id: str
    student_id: Optional[str]
    current_topic: str
    conversation_history: List[Dict[str, Any]]
    extracted_context: Dict[str, Any]
    last_activity: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class OptimizedSessionManager:
    """High-performance session manager with connection pooling and caching"""
    
    def __init__(self, db_path: str = "purdue_cs_knowledge.db", cache_size: int = 1000):
        self.db_path = db_path
        self.cache_size = cache_size
        
        # Initialize connection pool
        initialize_pool(db_path, pool_size=10)
        
        # LRU cache for frequently accessed sessions
        self._session_cache: Dict[str, Tuple[SessionData, float]] = {}
        self._cache_ttl = 300  # 5 minutes TTL
        
        # Performance tracking
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'queries_executed': 0,
            'avg_query_time': 0.0,
            'serialization_time': 0.0
        }
        
        # Pre-compiled SQL statements
        self.sql_statements = {
            'create_session': '''
                INSERT INTO session_context 
                (session_id, student_id, current_topic, conversation_history, extracted_context, last_activity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''',
            'get_session': '''
                SELECT session_id, student_id, current_topic, conversation_history, 
                       extracted_context, last_activity
                FROM session_context WHERE session_id = ?
            ''',
            'update_session': '''
                UPDATE session_context 
                SET conversation_history = ?, extracted_context = ?, last_activity = ?, current_topic = ?
                WHERE session_id = ?
            ''',
            'get_recent_sessions': '''
                SELECT session_id, student_id, last_activity 
                FROM session_context 
                WHERE last_activity > ? 
                ORDER BY last_activity DESC LIMIT ?
            ''',
            'cleanup_old_sessions': '''
                DELETE FROM session_context 
                WHERE last_activity < ?
            '''
        }
    
    def create_session(self, student_id: str = None) -> str:
        """Create a new conversation session with optimized insertion"""
        session_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        start_time = time.time()
        
        with get_connection() as conn:
            cursor = conn.connection.cursor()
            cursor.execute(self.sql_statements['create_session'], (
                session_id, student_id, '', '[]', '{}', current_time
            ))
            conn.connection.commit()
        
        self._update_query_stats(time.time() - start_time)
        
        # Cache the new session
        session_data = SessionData(
            session_id=session_id,
            student_id=student_id,
            current_topic='',
            conversation_history=[],
            extracted_context={},
            last_activity=current_time
        )
        self._cache_session(session_data)
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Retrieve session with caching optimization"""
        # Check cache first
        cached_session = self._get_cached_session(session_id)
        if cached_session:
            self.stats['cache_hits'] += 1
            return cached_session
        
        self.stats['cache_misses'] += 1
        start_time = time.time()
        
        with get_connection() as conn:
            result = conn.execute_cached(self.sql_statements['get_session'], (session_id,))
        
        self._update_query_stats(time.time() - start_time)
        
        if result:
            row = result[0]
            
            # Fast deserialization using msgpack if available, fallback to JSON
            try:
                conversation_history = self._fast_deserialize(row[3]) if row[3] else []
                extracted_context = self._fast_deserialize(row[4]) if row[4] else {}
            except (json.JSONDecodeError, msgpack.exceptions.ExtraData):
                # Fallback to JSON if msgpack fails
                conversation_history = json.loads(row[3]) if row[3] else []
                extracted_context = json.loads(row[4]) if row[4] else {}
            
            session_data = SessionData(
                session_id=row[0],
                student_id=row[1],
                current_topic=row[2],
                conversation_history=conversation_history,
                extracted_context=extracted_context,
                last_activity=row[5]
            )
            
            # Cache the session
            self._cache_session(session_data)
            return session_data
        
        return None
    
    def update_session(self, session_id: str, query: str, response: str, 
                      context: Dict = None, topic: str = None) -> bool:
        """Update session with batch operations and optimized serialization"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        start_serialize = time.time()
        
        # Add to conversation history
        conversation_turn = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response,
            'query_type': self._classify_query_type_cached(query)
        }
        
        session.conversation_history.append(conversation_turn)
        
        # Update extracted context
        if context:
            session.extracted_context.update(context)
        
        # Update topic if provided
        if topic:
            session.current_topic = topic
        
        session.last_activity = datetime.now().isoformat()
        
        # Fast serialization
        serialized_history = self._fast_serialize(session.conversation_history)
        serialized_context = self._fast_serialize(session.extracted_context)
        
        self.stats['serialization_time'] += time.time() - start_serialize
        
        start_time = time.time()
        
        with get_connection() as conn:
            cursor = conn.connection.cursor()
            cursor.execute(self.sql_statements['update_session'], (
                serialized_history,
                serialized_context,
                session.last_activity,
                session.current_topic,
                session_id
            ))
            conn.connection.commit()
        
        self._update_query_stats(time.time() - start_time)
        
        # Update cache
        self._cache_session(session)
        return True
    
    def get_recent_sessions(self, limit: int = 50, hours_back: int = 24) -> List[Dict[str, str]]:
        """Get recent sessions with optimized query"""
        cutoff_time = (datetime.now() - timedelta(hours=hours_back)).isoformat()
        
        start_time = time.time()
        
        with get_connection() as conn:
            results = conn.execute_cached(
                self.sql_statements['get_recent_sessions'], 
                (cutoff_time, limit)
            )
        
        self._update_query_stats(time.time() - start_time)
        
        return [
            {
                'session_id': row[0],
                'student_id': row[1],
                'last_activity': row[2]
            }
            for row in results
        ]
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Remove old sessions to maintain performance"""
        cutoff_time = (datetime.now() - timedelta(days=days_old)).isoformat()
        
        with get_connection() as conn:
            cursor = conn.connection.cursor()
            cursor.execute(self.sql_statements['cleanup_old_sessions'], (cutoff_time,))
            conn.connection.commit()
            rows_deleted = cursor.rowcount
        
        # Clear cache of deleted sessions
        self._clear_expired_cache()
        
        return rows_deleted
    
    @lru_cache(maxsize=500)
    def _classify_query_type_cached(self, query: str) -> str:
        """Cached query classification for performance"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['course', 'class', 'cs ']):
            return 'course_info'
        elif any(word in query_lower for word in ['graduate', 'graduation', 'plan']):
            return 'graduation_planning'
        elif any(word in query_lower for word in ['track', 'major', 'specialization']):
            return 'track_info'
        elif any(word in query_lower for word in ['codo', 'change major', 'transfer']):
            return 'codo_advice'
        elif any(word in query_lower for word in ['failed', 'fail', 'retake']):
            return 'failure_recovery'
        else:
            return 'general'
    
    def _fast_serialize(self, data: Any) -> str:
        """Fast serialization using msgpack if available, fallback to JSON"""
        try:
            # msgpack is much faster for complex nested data
            return msgpack.packb(data, use_bin_type=True).hex()
        except:
            # Fallback to JSON
            return json.dumps(data, separators=(',', ':'))
    
    def _fast_deserialize(self, data: str) -> Any:
        """Fast deserialization using msgpack if available, fallback to JSON"""
        try:
            # Try msgpack first (hex encoded)
            return msgpack.unpackb(bytes.fromhex(data), raw=False)
        except:
            # Fallback to JSON
            return json.loads(data)
    
    def _cache_session(self, session: SessionData):
        """Cache session with TTL"""
        current_time = time.time()
        
        # Remove expired entries if cache is full
        if len(self._session_cache) >= self.cache_size:
            self._clear_expired_cache()
        
        self._session_cache[session.session_id] = (session, current_time)
    
    def _get_cached_session(self, session_id: str) -> Optional[SessionData]:
        """Get session from cache with TTL check"""
        if session_id in self._session_cache:
            session, cached_time = self._session_cache[session_id]
            
            # Check TTL
            if time.time() - cached_time < self._cache_ttl:
                return session
            else:
                # Remove expired entry
                del self._session_cache[session_id]
        
        return None
    
    def _clear_expired_cache(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, cached_time) in self._session_cache.items()
            if current_time - cached_time >= self._cache_ttl
        ]
        
        for key in expired_keys:
            del self._session_cache[key]
    
    def _update_query_stats(self, query_time: float):
        """Update query performance statistics"""
        self.stats['queries_executed'] += 1
        
        if self.stats['queries_executed'] == 1:
            self.stats['avg_query_time'] = query_time
        else:
            # Rolling average
            total_queries = self.stats['queries_executed']
            self.stats['avg_query_time'] = (
                (self.stats['avg_query_time'] * (total_queries - 1) + query_time) 
                / total_queries
            )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        cache_total = self.stats['cache_hits'] + self.stats['cache_misses']
        cache_hit_ratio = (
            self.stats['cache_hits'] / cache_total if cache_total > 0 else 0.0
        )
        
        return {
            'cache_hit_ratio': cache_hit_ratio,
            'cache_size': len(self._session_cache),
            'total_queries': self.stats['queries_executed'],
            'avg_query_time_ms': self.stats['avg_query_time'] * 1000,
            'avg_serialization_time_ms': self.stats['serialization_time'] * 1000,
            **self.stats
        }