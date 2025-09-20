#!/usr/bin/env python3
"""
AI Service Call Optimization
Implements caching, batching, and async processing for Gemini API calls
"""

import asyncio
import hashlib
import json
import time
import google.generativeai as genai
from typing import Dict, List, Any, Optional, Tuple, Callable
from functools import wraps
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import threading
from collections import defaultdict, deque
import pickle
import os


@dataclass
class AICallStats:
    """AI service call performance statistics"""
    total_calls: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_response_time: float = 0.0
    batch_calls: int = 0
    failed_calls: int = 0
    
    @property
    def cache_hit_ratio(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0


@dataclass
class CachedResponse:
    """Cached AI response with metadata"""
    response: str
    timestamp: float
    tokens_used: int
    model: str
    prompt_hash: str


class AIServiceOptimizer:
    """High-performance AI service optimizer with caching and batching"""
    
    def __init__(self, cache_ttl: int = 3600, max_cache_size: int = 10000):
        self.cache_ttl = cache_ttl
        self.max_cache_size = max_cache_size
        self.stats = AICallStats()
        
        # Response cache
        self._response_cache: Dict[str, CachedResponse] = {}
        self._cache_file = "ai_response_cache.pkl"
        
        # Request batching
        self._batch_queue: deque = deque()
        self._batch_size = 5
        self._batch_timeout = 0.5  # seconds
        self._processing_batch = False
        
        # Thread pool for async operations
        self._executor = ThreadPoolExecutor(max_workers=3)
        
        # Rate limiting
        self._rate_limiter = TokenBucketRateLimiter(requests_per_minute=60)
        
        # Lock for thread safety
        self._lock = threading.RLock()
        
        # Load cached responses
        self._load_cache()
        
        # Start batch processor
        self._start_batch_processor()
    
    def _generate_cache_key(self, model: str, messages: List[Dict], temperature: float, 
                          max_tokens: int) -> str:
        """Generate deterministic cache key for AI requests"""
        cache_data = {
            'model': model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens
        }
        
        content = json.dumps(cache_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _load_cache(self):
        """Load cached responses from disk"""
        if os.path.exists(self._cache_file):
            try:
                with open(self._cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                    
                # Filter out expired entries
                current_time = time.time()
                self._response_cache = {
                    key: response for key, response in cached_data.items()
                    if current_time - response.timestamp < self.cache_ttl
                }
                
                print(f"🧠 Loaded {len(self._response_cache)} cached AI responses")
                
            except Exception as e:
                print(f"Warning: Failed to load AI cache: {e}")
                self._response_cache = {}
    
    def _save_cache(self):
        """Save cache to disk"""
        try:
            # Limit cache size
            if len(self._response_cache) > self.max_cache_size:
                # Remove oldest entries
                sorted_items = sorted(
                    self._response_cache.items(),
                    key=lambda x: x[1].timestamp
                )
                self._response_cache = dict(sorted_items[-self.max_cache_size:])
            
            with open(self._cache_file, 'wb') as f:
                pickle.dump(self._response_cache, f)
                
        except Exception as e:
            print(f"Warning: Failed to save AI cache: {e}")
    
    def _start_batch_processor(self):
        """Start background batch processor"""
        def process_batches():
            while True:
                try:
                    if len(self._batch_queue) >= self._batch_size or (
                        len(self._batch_queue) > 0 and 
                        time.time() - self._batch_queue[0]['timestamp'] > self._batch_timeout
                    ):
                        self._process_batch()
                    
                    time.sleep(0.1)  # Check every 100ms
                    
                except Exception as e:
                    print(f"Batch processor error: {e}")
        
        # Start background thread
        batch_thread = threading.Thread(target=process_batches, daemon=True)
        batch_thread.start()
    
    def _process_batch(self):
        """Process queued requests in batch"""
        if self._processing_batch:
            return
        
        self._processing_batch = True
        
        try:
            with self._lock:
                if not self._batch_queue:
                    return
                
                # Extract batch
                batch = []
                for _ in range(min(self._batch_size, len(self._batch_queue))):
                    if self._batch_queue:
                        batch.append(self._batch_queue.popleft())
            
            if batch:
                # Process batch asynchronously
                self._executor.submit(self._execute_batch, batch)
                
        finally:
            self._processing_batch = False
    
    def _execute_batch(self, batch: List[Dict]):
        """Execute batch of AI requests"""
        for request in batch:
            try:
                response = self._execute_single_request(
                    request['model'],
                    request['messages'],
                    request['temperature'],
                    request['max_tokens']
                )
                
                # Fulfill the future
                request['future'].set_result(response)
                
                self.stats.batch_calls += 1
                
            except Exception as e:
                request['future'].set_exception(e)
                self.stats.failed_calls += 1
    
    def _execute_single_request(self, model: str, messages: List[Dict], 
                               temperature: float, max_tokens: int) -> str:
        """Execute single AI request with rate limiting"""
        # Wait for rate limiter
        self._rate_limiter.acquire()
        
        start_time = time.time()
        
        try:
            client = Gemini.Gemini()
            response = client.generate_content(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.text
            tokens_used = response.usage.total_tokens
            
            # Update statistics
            with self._lock:
                self.stats.total_calls += 1
                self.stats.total_tokens += tokens_used
                self.stats.total_cost += self._estimate_cost(model, tokens_used)
                
                # Update average response time
                response_time = time.time() - start_time
                if self.stats.total_calls == 1:
                    self.stats.avg_response_time = response_time
                else:
                    self.stats.avg_response_time = (
                        (self.stats.avg_response_time * (self.stats.total_calls - 1) + response_time)
                        / self.stats.total_calls
                    )
            
            return content
            
        except Exception as e:
            self.stats.failed_calls += 1
            raise e
    
    def _estimate_cost(self, model: str, tokens: int) -> float:
        """Estimate API call cost"""
        # Pricing as of 2024 (adjust as needed)
        pricing = {
            'Gemini-4': 0.03 / 1000,  # $0.03 per 1K tokens
            'Gemini-4o': 0.02 / 1000,  # $0.02 per 1K tokens
            'Gemini-3.5-turbo': 0.001 / 1000,  # $0.001 per 1K tokens
        }
        
        rate = pricing.get(model, 0.02 / 1000)  # Default to Gemini-4o pricing
        return tokens * rate
    
    async def call_ai_cached(self, model: str = "Gemini-4o", messages: List[Dict] = None,
                           temperature: float = 0.7, max_tokens: int = 1000,
                           use_cache: bool = True) -> str:
        """Make AI call with caching and optimization"""
        
        # Generate cache key
        cache_key = self._generate_cache_key(model, messages, temperature, max_tokens)
        
        # Check cache first
        if use_cache and cache_key in self._response_cache:
            cached_response = self._response_cache[cache_key]
            
            # Check if cache entry is still valid
            if time.time() - cached_response.timestamp < self.cache_ttl:
                with self._lock:
                    self.stats.cache_hits += 1
                return cached_response.response
            else:
                # Remove expired entry
                del self._response_cache[cache_key]
        
        with self._lock:
            self.stats.cache_misses += 1
        
        # Execute request
        response = self._execute_single_request(model, messages, temperature, max_tokens)
        
        # Cache the response
        if use_cache:
            cached_response = CachedResponse(
                response=response,
                timestamp=time.time(),
                tokens_used=len(response.split()),  # Rough estimate
                model=model,
                prompt_hash=cache_key
            )
            
            self._response_cache[cache_key] = cached_response
            
            # Save cache periodically
            if len(self._response_cache) % 100 == 0:
                self._save_cache()
        
        return response
    
    def call_ai_batched(self, model: str = "Gemini-4o", messages: List[Dict] = None,
                       temperature: float = 0.7, max_tokens: int = 1000) -> asyncio.Future:
        """Queue AI call for batch processing"""
        
        future = asyncio.Future()
        
        request = {
            'model': model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'timestamp': time.time(),
            'future': future
        }
        
        with self._lock:
            self._batch_queue.append(request)
        
        return future
    
    def optimize_prompt(self, prompt: str) -> str:
        """Optimize prompt for better performance and lower costs"""
        # Remove unnecessary whitespace
        optimized = ' '.join(prompt.split())
        
        # Common optimizations
        replacements = {
            'Please provide a detailed': 'Provide',
            'I would like you to': 'Please',
            'Can you please': 'Please',
            'It would be great if you could': 'Please',
        }
        
        for old, new in replacements.items():
            optimized = optimized.replace(old, new)
        
        return optimized
    
    def clear_cache(self):
        """Clear AI response cache"""
        with self._lock:
            self._response_cache.clear()
            
        if os.path.exists(self._cache_file):
            os.remove(self._cache_file)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        return {
            'cache_hit_ratio': self.stats.cache_hit_ratio,
            'total_calls': self.stats.total_calls,
            'cache_hits': self.stats.cache_hits,
            'cache_misses': self.stats.cache_misses,
            'total_tokens': self.stats.total_tokens,
            'estimated_cost': self.stats.total_cost,
            'avg_response_time_ms': self.stats.avg_response_time * 1000,
            'batch_calls': self.stats.batch_calls,
            'failed_calls': self.stats.failed_calls,
            'cache_size': len(self._response_cache),
            'queue_size': len(self._batch_queue)
        }
    
    def __del__(self):
        """Cleanup and save cache"""
        self._save_cache()
        if self._executor:
            self._executor.shutdown(wait=False)


class TokenBucketRateLimiter:
    """Token bucket rate limiter for API calls"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.capacity = requests_per_minute
        self.tokens = requests_per_minute
        self.fill_rate = requests_per_minute / 60.0  # tokens per second
        self.last_update = time.time()
        self._lock = threading.Lock()
    
    def acquire(self):
        """Acquire a token, blocking if necessary"""
        while True:
            with self._lock:
                now = time.time()
                
                # Add tokens based on elapsed time
                elapsed = now - self.last_update
                self.tokens = min(self.capacity, self.tokens + elapsed * self.fill_rate)
                self.last_update = now
                
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
            
            # Wait a bit before trying again
            time.sleep(0.1)


# Global optimizer instance
_ai_optimizer: Optional[AIServiceOptimizer] = None


def get_ai_optimizer() -> AIServiceOptimizer:
    """Get or create global AI optimizer instance"""
    global _ai_optimizer
    if _ai_optimizer is None:
        _ai_optimizer = AIServiceOptimizer()
    return _ai_optimizer


def cached_ai_call(model: str = "Gemini-4o", temperature: float = 0.7, 
                  max_tokens: int = 1000, use_cache: bool = True):
    """Decorator for caching AI calls"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract prompt from function result
            messages = func(*args, **kwargs)
            
            optimizer = get_ai_optimizer()
            return await optimizer.call_ai_cached(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                use_cache=use_cache
            )
        
        return wrapper
    return decorator