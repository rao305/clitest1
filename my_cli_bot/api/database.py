#!/usr/bin/env python3
"""
Database Connection and Management
High-performance database layer with connection pooling and optimization
"""

import sqlite3
import threading
import os
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
import json


@dataclass
class ConnectionPoolStats:
    """Connection pool statistics"""
    active_connections: int
    total_connections: int
    max_connections: int
    successful_queries: int
    failed_queries: int
    avg_query_time_ms: float


class DatabaseConnection:
    """Optimized database connection with performance enhancements"""
    
    def __init__(self, db_path: str):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # Enable dict-like access
        
        # Performance optimizations
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA cache_size=10000")
        self.connection.execute("PRAGMA temp_store=memory")
        self.connection.execute("PRAGMA mmap_size=268435456")  # 256MB
        self.connection.execute("PRAGMA synchronous=NORMAL")
        
        # Enable foreign keys
        self.connection.execute("PRAGMA foreign_keys=ON")
        
        self.connection.commit()
        self._lock = threading.Lock()
    
    def execute(self, query: str, params: tuple = None) -> sqlite3.Cursor:
        """Execute query with thread safety"""
        with self._lock:
            if params:
                return self.connection.execute(query, params)
            else:
                return self.connection.execute(query)
    
    def executemany(self, query: str, params_list: List[tuple]) -> sqlite3.Cursor:
        """Execute many queries with thread safety"""
        with self._lock:
            return self.connection.executemany(query, params_list)
    
    def commit(self):
        """Commit transaction"""
        with self._lock:
            self.connection.commit()
    
    def rollback(self):
        """Rollback transaction"""
        with self._lock:
            self.connection.rollback()
    
    def close(self):
        """Close connection"""
        with self._lock:
            self.connection.close()


class DatabaseConnectionPool:
    """High-performance database connection pool"""
    
    def __init__(self, db_path: str, pool_size: int = 10):
        self.db_path = db_path
        self.pool_size = pool_size
        self._pool = []
        self._lock = threading.Lock()
        self._stats = ConnectionPoolStats(
            active_connections=0,
            total_connections=0,
            max_connections=pool_size,
            successful_queries=0,
            failed_queries=0,
            avg_query_time_ms=0.0
        )
        
        # Initialize pool
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        for _ in range(self.pool_size):
            conn = DatabaseConnection(self.db_path)
            self._pool.append(conn)
            self._stats.total_connections += 1
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool with context manager"""
        with self._lock:
            if not self._pool:
                # Create new connection if pool is empty
                conn = DatabaseConnection(self.db_path)
                self._stats.total_connections += 1
            else:
                conn = self._pool.pop()
            
            self._stats.active_connections += 1
        
        try:
            yield conn
        finally:
            with self._lock:
                self._pool.append(conn)
                self._stats.active_connections -= 1
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute query and return results as list of dictionaries"""
        import time
        start_time = time.time()
        
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                results = [dict(row) for row in cursor.fetchall()]
                
                query_time = (time.time() - start_time) * 1000
                self._update_stats(True, query_time)
                
                return results
                
        except Exception as e:
            query_time = (time.time() - start_time) * 1000
            self._update_stats(False, query_time)
            raise e
    
    def execute_single(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Execute query and return single result"""
        results = self.execute_query(query, params)
        return results[0] if results else None
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute update/insert query and return affected rows"""
        import time
        start_time = time.time()
        
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                conn.commit()
                
                query_time = (time.time() - start_time) * 1000
                self._update_stats(True, query_time)
                
                return cursor.rowcount
                
        except Exception as e:
            query_time = (time.time() - start_time) * 1000
            self._update_stats(False, query_time)
            raise e
    
    def execute_batch(self, query: str, params_list: List[tuple]) -> int:
        """Execute batch operation"""
        import time
        start_time = time.time()
        
        try:
            with self.get_connection() as conn:
                cursor = conn.executemany(query, params_list)
                conn.commit()
                
                query_time = (time.time() - start_time) * 1000
                self._update_stats(True, query_time)
                
                return cursor.rowcount
                
        except Exception as e:
            query_time = (time.time() - start_time) * 1000
            self._update_stats(False, query_time)
            raise e
    
    def _update_stats(self, success: bool, query_time_ms: float):
        """Update performance statistics"""
        with self._lock:
            if success:
                self._stats.successful_queries += 1
            else:
                self._stats.failed_queries += 1
            
            # Update average query time
            total_queries = self._stats.successful_queries + self._stats.failed_queries
            current_avg = self._stats.avg_query_time_ms
            self._stats.avg_query_time_ms = (
                (current_avg * (total_queries - 1) + query_time_ms) / total_queries
            )
    
    def get_stats(self) -> ConnectionPoolStats:
        """Get connection pool statistics"""
        with self._lock:
            return ConnectionPoolStats(
                active_connections=self._stats.active_connections,
                total_connections=self._stats.total_connections,
                max_connections=self._stats.max_connections,
                successful_queries=self._stats.successful_queries,
                failed_queries=self._stats.failed_queries,
                avg_query_time_ms=self._stats.avg_query_time_ms
            )
    
    def close_all(self):
        """Close all connections in pool"""
        with self._lock:
            for conn in self._pool:
                conn.close()
            self._pool.clear()


class DatabaseManager:
    """Database manager with schema migration and maintenance"""
    
    def __init__(self, db_path: str = "purdue_cs_knowledge.db"):
        self.db_path = db_path
        self.pool = DatabaseConnectionPool(db_path)
        self._initialize_schema()
    
    def _initialize_schema(self):
        """Initialize database schema with all required tables"""
        
        # Sessions table
        self.pool.execute_update('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                student_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                context_data TEXT,
                is_active BOOLEAN DEFAULT 1,
                expires_at TIMESTAMP
            )
        ''')
        
        # Conversation history table
        self.pool.execute_update('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_query TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                intent TEXT,
                confidence REAL,
                context_updates TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processing_time_ms REAL,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        # Course information cache table
        self.pool.execute_update('''
            CREATE TABLE IF NOT EXISTS course_cache (
                course_code TEXT PRIMARY KEY,
                course_data TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                cache_hits INTEGER DEFAULT 0
            )
        ''')
        
        # User feedback table
        self.pool.execute_update('''
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                query_id INTEGER,
                rating INTEGER CHECK (rating BETWEEN 1 AND 5),
                feedback_text TEXT,
                category TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id),
                FOREIGN KEY (query_id) REFERENCES conversation_history (id)
            )
        ''')
        
        # Performance metrics table
        self.pool.execute_update('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                category TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # API request audit table
        self.pool.execute_update('''
            CREATE TABLE IF NOT EXISTS api_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                request_size INTEGER,
                response_status INTEGER,
                response_size INTEGER,
                processing_time_ms REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for performance optimization"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_sessions_student_id ON sessions (student_id)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_active ON sessions (is_active)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions (expires_at)",
            "CREATE INDEX IF NOT EXISTS idx_conversation_session ON conversation_history (session_id)",
            "CREATE INDEX IF NOT EXISTS idx_conversation_timestamp ON conversation_history (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_course_cache_updated ON course_cache (last_updated)",
            "CREATE INDEX IF NOT EXISTS idx_feedback_session ON user_feedback (session_id)",
            "CREATE INDEX IF NOT EXISTS idx_feedback_rating ON user_feedback (rating)",
            "CREATE INDEX IF NOT EXISTS idx_metrics_name ON performance_metrics (metric_name)",
            "CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON performance_metrics (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_audit_endpoint ON api_audit (endpoint)",
            "CREATE INDEX IF NOT EXISTS idx_audit_user ON api_audit (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON api_audit (timestamp)"
        ]
        
        for index_sql in indexes:
            try:
                self.pool.execute_update(index_sql)
            except sqlite3.OperationalError:
                pass  # Index might already exist
    
    def create_session(self, session_id: str, student_id: str = None, context_data: Dict[str, Any] = None) -> bool:
        """Create new session"""
        expires_at = datetime.now() + timedelta(hours=4)  # 4-hour session timeout
        
        context_json = json.dumps(context_data) if context_data else "{}"
        
        rows_affected = self.pool.execute_update('''
            INSERT INTO sessions (id, student_id, context_data, expires_at)
            VALUES (?, ?, ?, ?)
        ''', (session_id, student_id, context_json, expires_at))
        
        return rows_affected > 0
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        result = self.pool.execute_single('''
            SELECT id, student_id, created_at, last_active, context_data, 
                   is_active, expires_at
            FROM sessions 
            WHERE id = ? AND is_active = 1
        ''', (session_id,))
        
        if result and result['context_data']:
            try:
                result['context_data'] = json.loads(result['context_data'])
            except json.JSONDecodeError:
                result['context_data'] = {}
        
        return result
    
    def update_session(self, session_id: str, context_updates: Dict[str, Any] = None) -> bool:
        """Update session context and last active time"""
        if context_updates:
            # Get current context
            current_session = self.get_session(session_id)
            if not current_session:
                return False
            
            # Merge updates
            current_context = current_session.get('context_data', {})
            current_context.update(context_updates)
            context_json = json.dumps(current_context)
            
            rows_affected = self.pool.execute_update('''
                UPDATE sessions 
                SET context_data = ?, last_active = CURRENT_TIMESTAMP
                WHERE id = ? AND is_active = 1
            ''', (context_json, session_id))
        else:
            rows_affected = self.pool.execute_update('''
                UPDATE sessions 
                SET last_active = CURRENT_TIMESTAMP
                WHERE id = ? AND is_active = 1
            ''', (session_id,))
        
        return rows_affected > 0
    
    def add_conversation_entry(self, session_id: str, user_query: str, ai_response: str, 
                             intent: str = None, confidence: float = None, 
                             context_updates: Dict[str, Any] = None,
                             processing_time_ms: float = None) -> int:
        """Add conversation entry"""
        context_json = json.dumps(context_updates) if context_updates else None
        
        cursor = self.pool.execute_update('''
            INSERT INTO conversation_history 
            (session_id, user_query, ai_response, intent, confidence, 
             context_updates, processing_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, user_query, ai_response, intent, confidence, 
              context_json, processing_time_ms))
        
        return cursor
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history for session"""
        results = self.pool.execute_query('''
            SELECT id, user_query, ai_response, intent, confidence, 
                   context_updates, timestamp, processing_time_ms
            FROM conversation_history 
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (session_id, limit))
        
        # Parse context_updates JSON
        for result in results:
            if result['context_updates']:
                try:
                    result['context_updates'] = json.loads(result['context_updates'])
                except json.JSONDecodeError:
                    result['context_updates'] = {}
        
        return results
    
    def log_api_request(self, endpoint: str, method: str, user_id: str = None,
                       session_id: str = None, ip_address: str = None,
                       user_agent: str = None, request_size: int = None,
                       response_status: int = None, response_size: int = None,
                       processing_time_ms: float = None) -> bool:
        """Log API request for audit purposes"""
        rows_affected = self.pool.execute_update('''
            INSERT INTO api_audit 
            (endpoint, method, user_id, session_id, ip_address, user_agent,
             request_size, response_status, response_size, processing_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (endpoint, method, user_id, session_id, ip_address, user_agent,
              request_size, response_status, response_size, processing_time_ms))
        
        return rows_affected > 0
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        rows_affected = self.pool.execute_update('''
            UPDATE sessions 
            SET is_active = 0 
            WHERE expires_at < CURRENT_TIMESTAMP AND is_active = 1
        ''')
        
        return rows_affected
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        stats = {}
        
        # Table counts
        tables = ['sessions', 'conversation_history', 'course_cache', 'user_feedback', 
                 'performance_metrics', 'api_audit']
        
        for table in tables:
            result = self.pool.execute_single(f'SELECT COUNT(*) as count FROM {table}')
            stats[f'{table}_count'] = result['count'] if result else 0
        
        # Active sessions
        result = self.pool.execute_single('''
            SELECT COUNT(*) as count FROM sessions 
            WHERE is_active = 1 AND expires_at > CURRENT_TIMESTAMP
        ''')
        stats['active_sessions'] = result['count'] if result else 0
        
        # Recent activity (last 24 hours)
        result = self.pool.execute_single('''
            SELECT COUNT(*) as count FROM conversation_history 
            WHERE timestamp > datetime('now', '-24 hours')
        ''')
        stats['queries_24h'] = result['count'] if result else 0
        
        # Average response time
        result = self.pool.execute_single('''
            SELECT AVG(processing_time_ms) as avg_time FROM conversation_history 
            WHERE processing_time_ms IS NOT NULL 
            AND timestamp > datetime('now', '-24 hours')
        ''')
        stats['avg_response_time_ms'] = result['avg_time'] if result and result['avg_time'] else 0
        
        # Connection pool stats
        pool_stats = self.pool.get_stats()
        stats['pool_stats'] = {
            'active_connections': pool_stats.active_connections,
            'total_connections': pool_stats.total_connections,
            'successful_queries': pool_stats.successful_queries,
            'failed_queries': pool_stats.failed_queries,
            'avg_query_time_ms': pool_stats.avg_query_time_ms
        }
        
        return stats
    
    def close(self):
        """Close database manager and all connections"""
        self.pool.close_all()


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager(db_path: str = "purdue_cs_knowledge.db") -> DatabaseManager:
    """Get or create global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(db_path)
    return _db_manager


def get_db_connection():
    """Dependency for FastAPI to get database connection"""
    db_manager = get_database_manager()
    return db_manager