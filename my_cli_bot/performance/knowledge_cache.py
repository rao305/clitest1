#!/usr/bin/env python3
"""
High-Performance Knowledge Graph Cache
Eliminates repeated JSON loading and implements intelligent caching strategies
"""

import json
import pickle
import hashlib
import os
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from functools import lru_cache
from dataclasses import dataclass
import threading
from concurrent.futures import ThreadPoolExecutor
import mmap


@dataclass
class CacheStats:
    """Knowledge cache performance statistics"""
    hits: int = 0
    misses: int = 0
    load_time: float = 0.0
    memory_usage: int = 0
    cache_size: int = 0
    
    @property
    def hit_ratio(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class OptimizedKnowledgeCache:
    """High-performance knowledge graph cache with memory mapping and compression"""
    
    def __init__(self, knowledge_file: str = "data/cs_knowledge_graph.json"):
        self.knowledge_file = knowledge_file
        self.cache_file = knowledge_file + ".cache"
        self.stats = CacheStats()
        self._lock = threading.RLock()
        
        # Main knowledge base
        self._knowledge_base: Optional[Dict[str, Any]] = None
        self._file_hash: Optional[str] = None
        self._load_time: float = 0
        
        # Specialized caches for frequent queries
        self._course_cache: Dict[str, Dict[str, Any]] = {}
        self._prerequisite_cache: Dict[str, List[str]] = {}
        self._track_cache: Dict[str, Dict[str, Any]] = {}
        self._search_cache: Dict[str, List[str]] = {}
        
        # Memory-mapped file for ultra-fast access
        self._mmap_file: Optional[mmap.mmap] = None
        
        # Thread pool for async loading
        self._executor = ThreadPoolExecutor(max_workers=2)
        
        # Load knowledge base
        self._load_knowledge_base()
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate file hash for cache invalidation"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _load_knowledge_base(self):
        """Load knowledge base with intelligent caching"""
        start_time = time.time()
        
        try:
            # Check if cache file exists and is newer
            current_hash = self._calculate_file_hash(self.knowledge_file)
            
            if self._try_load_from_cache(current_hash):
                self.stats.hits += 1
                self.stats.load_time = time.time() - start_time
                return
            
            self.stats.misses += 1
            
            # Load from JSON file with memory mapping for large files
            file_size = os.path.getsize(self.knowledge_file)
            
            if file_size > 10 * 1024 * 1024:  # 10MB threshold
                self._load_with_mmap()
            else:
                self._load_traditional()
            
            # Save to cache
            self._save_to_cache(current_hash)
            
            # Build specialized caches
            self._build_specialized_caches()
            
        except Exception as e:
            print(f"Warning: Failed to load knowledge base: {e}")
            self._knowledge_base = {}
        
        finally:
            load_time = time.time() - start_time
            self.stats.load_time = load_time
            self._load_time = load_time
            print(f"📚 Knowledge base loaded in {load_time:.3f}s")
    
    def _load_with_mmap(self):
        """Load large JSON files using memory mapping"""
        with open(self.knowledge_file, 'rb') as f:
            self._mmap_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            json_data = self._mmap_file.read().decode('utf-8')
            self._knowledge_base = json.loads(json_data)
    
    def _load_traditional(self):
        """Traditional JSON loading for smaller files"""
        with open(self.knowledge_file, 'r', encoding='utf-8') as f:
            self._knowledge_base = json.load(f)
    
    def _try_load_from_cache(self, current_hash: str) -> bool:
        """Try to load from pickle cache"""
        if not os.path.exists(self.cache_file):
            return False
        
        try:
            with open(self.cache_file, 'rb') as f:
                cache_data = pickle.load(f)
                
            if cache_data['hash'] == current_hash:
                self._knowledge_base = cache_data['data']
                self._file_hash = current_hash
                self._course_cache = cache_data.get('course_cache', {})
                self._prerequisite_cache = cache_data.get('prerequisite_cache', {})
                self._track_cache = cache_data.get('track_cache', {})
                return True
                
        except (pickle.PickleError, KeyError, FileNotFoundError):
            pass
        
        return False
    
    def _save_to_cache(self, file_hash: str):
        """Save to pickle cache for faster loading"""
        try:
            cache_data = {
                'hash': file_hash,
                'data': self._knowledge_base,
                'course_cache': self._course_cache,
                'prerequisite_cache': self._prerequisite_cache,
                'track_cache': self._track_cache,
                'timestamp': time.time()
            }
            
            with open(self.cache_file, 'wb') as f:
                pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            self._file_hash = file_hash
            
        except Exception as e:
            print(f"Warning: Failed to save cache: {e}")
    
    def _build_specialized_caches(self):
        """Build specialized caches for frequent operations"""
        if not self._knowledge_base:
            return
        
        # Course cache - flatten course data for O(1) access
        courses = self._knowledge_base.get('courses', {})
        for course_code, course_data in courses.items():
            self._course_cache[course_code] = {
                'title': course_data.get('title', ''),
                'credits': course_data.get('credits', 0),
                'description': course_data.get('description', ''),
                'difficulty_rating': course_data.get('difficulty_rating', 0.0),
                'is_critical': course_data.get('is_critical', False)
            }
        
        # Prerequisite cache - flatten prerequisite chains
        prerequisites = self._knowledge_base.get('prerequisites', {})
        for course_code, prereqs in prerequisites.items():
            if isinstance(prereqs, list):
                self._prerequisite_cache[course_code] = prereqs
            elif isinstance(prereqs, dict):
                self._prerequisite_cache[course_code] = prereqs.get('required', [])
        
        # Track cache - optimize track data
        tracks = self._knowledge_base.get('tracks', {})
        for track_name, track_data in tracks.items():
            self._track_cache[track_name] = {
                'description': track_data.get('description', ''),
                'required_courses': track_data.get('required_courses', []),
                'core_required': track_data.get('core_required', []),
                'choose_one_systems': track_data.get('choose_one_systems', []),
                'choose_one_elective': track_data.get('choose_one_elective', [])
            }
        
        # Update stats
        self.stats.cache_size = (
            len(self._course_cache) + 
            len(self._prerequisite_cache) + 
            len(self._track_cache)
        )
    
    def get_course_info(self, course_code: str) -> Optional[Dict[str, Any]]:
        """Get course information with O(1) cache lookup"""
        with self._lock:
            self.stats.hits += 1
            return self._course_cache.get(course_code)
    
    def get_prerequisites(self, course_code: str) -> List[str]:
        """Get course prerequisites with O(1) cache lookup"""
        with self._lock:
            self.stats.hits += 1
            return self._prerequisite_cache.get(course_code, [])
    
    def get_track_info(self, track_name: str) -> Optional[Dict[str, Any]]:
        """Get track information with O(1) cache lookup"""
        with self._lock:
            self.stats.hits += 1
            return self._track_cache.get(track_name)
    
    @lru_cache(maxsize=500)
    def search_courses(self, query: str) -> List[str]:
        """Search courses with LRU cache"""
        query_lower = query.lower()
        matching_courses = []
        
        for course_code, course_data in self._course_cache.items():
            if (query_lower in course_code.lower() or 
                query_lower in course_data.get('title', '').lower() or
                query_lower in course_data.get('description', '').lower()):
                matching_courses.append(course_code)
        
        return matching_courses[:10]  # Limit results
    
    @lru_cache(maxsize=200)
    def get_prerequisite_chain(self, course_code: str) -> List[str]:
        """Get complete prerequisite chain with memoization"""
        def _build_chain(code: str, visited: Set[str]) -> List[str]:
            if code in visited:
                return []  # Circular dependency
            
            visited.add(code)
            chain = []
            
            prereqs = self.get_prerequisites(code)
            for prereq in prereqs:
                chain.extend(_build_chain(prereq, visited.copy()))
                if prereq not in chain:
                    chain.append(prereq)
            
            return chain
        
        return _build_chain(course_code, set())
    
    def get_all_courses(self) -> Dict[str, Dict[str, Any]]:
        """Get all courses (use with caution for large datasets)"""
        return self._course_cache.copy()
    
    def get_all_tracks(self) -> Dict[str, Dict[str, Any]]:
        """Get all tracks"""
        return self._track_cache.copy()
    
    def get_raw_knowledge_base(self) -> Dict[str, Any]:
        """Get raw knowledge base (for legacy compatibility)"""
        return self._knowledge_base or {}
    
    def reload_if_changed(self) -> bool:
        """Reload knowledge base if file has changed"""
        if not os.path.exists(self.knowledge_file):
            return False
        
        current_hash = self._calculate_file_hash(self.knowledge_file)
        if current_hash != self._file_hash:
            print("📚 Knowledge base file changed, reloading...")
            self._load_knowledge_base()
            return True
        
        return False
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        memory_usage = 0
        if self._knowledge_base:
            # Rough memory usage estimation
            memory_usage = len(str(self._knowledge_base).encode('utf-8'))
        
        return {
            'hit_ratio': self.stats.hit_ratio,
            'total_hits': self.stats.hits,
            'total_misses': self.stats.misses,
            'load_time_ms': self.stats.load_time * 1000,
            'cache_size': self.stats.cache_size,
            'memory_usage_mb': memory_usage / (1024 * 1024),
            'courses_cached': len(self._course_cache),
            'prerequisites_cached': len(self._prerequisite_cache),
            'tracks_cached': len(self._track_cache)
        }
    
    def clear_search_cache(self):
        """Clear search LRU caches"""
        self.search_courses.cache_clear()
        self.get_prerequisite_chain.cache_clear()
    
    def __del__(self):
        """Cleanup resources"""
        if self._mmap_file:
            self._mmap_file.close()
        if self._executor:
            self._executor.shutdown(wait=False)


# Global cache instance
_knowledge_cache: Optional[OptimizedKnowledgeCache] = None


def get_knowledge_cache(knowledge_file: str = "data/cs_knowledge_graph.json") -> OptimizedKnowledgeCache:
    """Get or create global knowledge cache instance"""
    global _knowledge_cache
    if _knowledge_cache is None:
        _knowledge_cache = OptimizedKnowledgeCache(knowledge_file)
    return _knowledge_cache


def reload_knowledge_cache() -> bool:
    """Reload knowledge cache if file has changed"""
    if _knowledge_cache:
        return _knowledge_cache.reload_if_changed()
    return False