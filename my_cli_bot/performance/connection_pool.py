#!/usr/bin/env python3
"""
High-Performance Database Connection Pool
Eliminates connection overhead and implements prepared statements
"""

import sqlite3
import threading
import time
from contextlib import contextmanager
from typing import Dict, List, Optional, Any
from queue import Queue, Empty
from dataclasses import dataclass


@dataclass
class PoolStats:
    """Connection pool performance statistics"""
    total_connections: int = 0
    active_connections: int = 0
    peak_connections: int = 0
    total_queries: int = 0
    avg_query_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0


class OptimizedConnection:
    """Wrapper for SQLite connection with prepared statements and query caching"""
    
    def __init__(self, db_path: str):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # Enable column access by name
        self.connection.execute("PRAGMA journal_mode=WAL")  # Better concurrency
        self.connection.execute("PRAGMA synchronous=NORMAL")  # Faster writes
        self.connection.execute("PRAGMA cache_size=10000")  # 10MB cache
        self.connection.execute("PRAGMA temp_store=memory")  # Use memory for temp tables
        
        # Prepared statements cache
        self.prepared_statements: Dict[str, sqlite3.Cursor] = {}
        self.query_cache: Dict[str, Any] = {}
        self.last_accessed = time.time()
        
    def get_prepared_cursor(self, query: str) -> sqlite3.Cursor:
        """Get or create a prepared statement cursor"""
        if query not in self.prepared_statements:
            cursor = self.connection.cursor()
            # Pre-compile the query
            cursor.execute("EXPLAIN QUERY PLAN " + query, ())
            cursor.close()
            self.prepared_statements[query] = self.connection.cursor()
        return self.prepared_statements[query]
    
    def execute_cached(self, query: str, params: tuple = ()) -> Any:
        """Execute query with result caching for SELECT statements"""
        cache_key = f"{query}:{params}"
        
        # Check cache for SELECT queries
        if query.strip().upper().startswith('SELECT') and cache_key in self.query_cache:
            return self.query_cache[cache_key]
        
        cursor = self.get_prepared_cursor(query)
        result = cursor.execute(query, params).fetchall()
        
        # Cache SELECT results for 30 seconds
        if query.strip().upper().startswith('SELECT'):
            self.query_cache[cache_key] = result
            # Simple cache eviction - remove entries older than 30 seconds
            current_time = time.time()
            if len(self.query_cache) > 100:  # Limit cache size
                self.query_cache = {k: v for k, v in self.query_cache.items() 
                                  if current_time - self.last_accessed < 30}
        
        return result
    
    def close(self):
        """Close connection and cleanup"""
        for cursor in self.prepared_statements.values():
            cursor.close()
        self.connection.close()


class DatabaseConnectionPool:
    """High-performance connection pool with monitoring"""
    
    def __init__(self, db_path: str, pool_size: int = 10, max_overflow: int = 20):
        self.db_path = db_path
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool = Queue(maxsize=pool_size)
        self.overflow_connections = 0
        self.stats = PoolStats()
        self._lock = threading.Lock()
        
        # Pre-create connections
        for _ in range(pool_size):
            conn = OptimizedConnection(db_path)
            self.pool.put(conn)
            self.stats.total_connections += 1
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool with automatic return"""
        start_time = time.time()
        connection = None
        
        try:
            # Try to get from pool
            try:
                connection = self.pool.get_nowait()
                with self._lock:
                    self.stats.active_connections += 1
                    self.stats.peak_connections = max(
                        self.stats.peak_connections, 
                        self.stats.active_connections
                    )
            except Empty:
                # Create overflow connection if allowed
                if self.overflow_connections < self.max_overflow:
                    connection = OptimizedConnection(self.db_path)
                    with self._lock:
                        self.overflow_connections += 1
                        self.stats.total_connections += 1
                        self.stats.active_connections += 1
                else:
                    # Wait for available connection
                    connection = self.pool.get(timeout=5.0)
                    with self._lock:
                        self.stats.active_connections += 1
            
            connection.last_accessed = time.time()
            yield connection
            
        finally:
            # Return connection to pool
            if connection:
                query_time = time.time() - start_time
                with self._lock:
                    self.stats.active_connections -= 1
                    self.stats.total_queries += 1
                    # Update rolling average
                    if self.stats.total_queries == 1:
                        self.stats.avg_query_time = query_time
                    else:
                        self.stats.avg_query_time = (
                            (self.stats.avg_query_time * (self.stats.total_queries - 1) + query_time) 
                            / self.stats.total_queries
                        )
                
                # Return to pool or close overflow connection
                if self.overflow_connections > 0:
                    connection.close()
                    with self._lock:
                        self.overflow_connections -= 1
                        self.stats.total_connections -= 1
                else:
                    self.pool.put(connection)
    
    def get_stats(self) -> PoolStats:
        """Get current pool statistics"""
        return self.stats
    
    def close_all(self):
        """Close all connections in pool"""
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
                conn.close()
            except Empty:
                break


# Global connection pool instance
_connection_pool: Optional[DatabaseConnectionPool] = None


def initialize_pool(db_path: str, pool_size: int = 10) -> DatabaseConnectionPool:
    """Initialize global connection pool"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = DatabaseConnectionPool(db_path, pool_size)
    return _connection_pool


def get_connection():
    """Get connection from global pool"""
    if _connection_pool is None:
        raise RuntimeError("Connection pool not initialized. Call initialize_pool() first.")
    return _connection_pool.get_connection()


def get_pool_stats() -> PoolStats:
    """Get current pool statistics"""
    if _connection_pool is None:
        return PoolStats()
    return _connection_pool.get_stats()