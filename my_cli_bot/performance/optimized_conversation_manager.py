#!/usr/bin/env python3
"""
High-Performance Async Conversation Manager
Replaces the monolithic intelligent_conversation_manager.py with async, optimized version
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

from .optimized_session_manager import OptimizedSessionManager, SessionData
from .knowledge_cache import get_knowledge_cache
from .ai_service_optimizer import get_ai_optimizer, cached_ai_call


@dataclass
class ConversationMetrics:
    """Performance metrics for conversation processing"""
    total_requests: int = 0
    avg_response_time: float = 0.0
    cache_hit_ratio: float = 0.0
    concurrent_sessions: int = 0
    peak_concurrent: int = 0


class AsyncConversationManager:
    """High-performance async conversation manager with optimized processing"""
    
    def __init__(self):
        # Initialize optimized components
        self.session_manager = OptimizedSessionManager()
        self.knowledge_cache = get_knowledge_cache()
        self.ai_optimizer = get_ai_optimizer()
        
        # Performance tracking
        self.metrics = ConversationMetrics()
        self._active_sessions = set()
        
        # Async processing pools
        self._semaphore = asyncio.Semaphore(50)  # Limit concurrent processing
        
        print("🚀 High-Performance Async Conversation Manager initialized")
    
    async def process_query_async(self, session_id: str, user_query: str) -> str:
        """Main async query processing with performance optimization"""
        
        async with self._semaphore:  # Limit concurrency
            start_time = time.time()
            
            try:
                # Track active session
                self._active_sessions.add(session_id)
                self.metrics.concurrent_sessions = len(self._active_sessions)
                self.metrics.peak_concurrent = max(
                    self.metrics.peak_concurrent, 
                    self.metrics.concurrent_sessions
                )
                
                # Get or create session
                session = self.session_manager.get_session(session_id)
                if not session:
                    self.session_manager.create_session()
                    session = self.session_manager.get_session(session_id)
                
                # Process query with parallel operations
                intent_task = asyncio.create_task(self._analyze_intent_async(user_query))
                context_task = asyncio.create_task(self._extract_context_async(user_query, session))
                knowledge_task = asyncio.create_task(self._lookup_knowledge_async(user_query))
                
                # Wait for all parallel operations
                intent_analysis, extracted_context, knowledge_results = await asyncio.gather(
                    intent_task, context_task, knowledge_task
                )
                
                # Generate response
                response = await self._generate_response_async(
                    user_query, session, intent_analysis, extracted_context, knowledge_results
                )
                
                # Update session (async)
                asyncio.create_task(self._update_session_async(
                    session_id, user_query, response, extracted_context
                ))
                
                # Update metrics
                response_time = time.time() - start_time
                self.metrics.total_requests += 1
                
                if self.metrics.total_requests == 1:
                    self.metrics.avg_response_time = response_time
                else:
                    self.metrics.avg_response_time = (
                        (self.metrics.avg_response_time * (self.metrics.total_requests - 1) + response_time)
                        / self.metrics.total_requests
                    )
                
                return response
                
            finally:
                # Remove from active sessions
                self._active_sessions.discard(session_id)
                self.metrics.concurrent_sessions = len(self._active_sessions)
    
    async def _analyze_intent_async(self, query: str) -> Dict[str, Any]:
        """Async intent analysis with caching"""
        
        # Fast pattern-based classification first
        intent = self._classify_intent_fast(query)
        confidence = 0.8
        
        # Use AI for complex queries
        if intent == "general" or confidence < 0.7:
            try:
                ai_analysis = await self._ai_intent_analysis(query)
                if ai_analysis:
                    intent = ai_analysis.get('intent', intent)
                    confidence = ai_analysis.get('confidence', confidence)
            except Exception:
                pass  # Fallback to pattern-based
        
        return {
            'primary_intent': intent,
            'confidence': confidence,
            'timestamp': time.time()
        }
    
    def _classify_intent_fast(self, query: str) -> str:
        """Fast pattern-based intent classification"""
        query_lower = query.lower()
        
        # Optimized keyword matching
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
        elif any(word in query_lower for word in ['hi', 'hello', 'hey', 'yo']):
            return 'greeting'
        else:
            return 'general'
    
    @cached_ai_call(, , )
    async def _ai_intent_analysis(self, query: str) -> Optional[Dict[str, Any]]:
        """AI-powered intent analysis with caching"""
        
        prompt = f"""
        Classify this academic advising query into one of these categories:
        - course_info: Questions about specific courses
        - graduation_planning: Questions about graduation timeline/planning
        - track_info: Questions about CS tracks (MI, SE, etc.)
        - codo_advice: Questions about changing major to CS
        - failure_recovery: Questions about failing or retaking courses
        - career_guidance: Questions about careers, internships, jobs
        - general: General questions
        
        Query: "{query}"
        
        Respond with JSON: {{"intent": "category", "confidence": 0.85}}
        """
        
        return [{"role": "user", "content": prompt}]
    
    async def _extract_context_async(self, query: str, session: SessionData) -> Dict[str, Any]:
        """Async context extraction with parallel processing"""
        
        # Fast regex-based extraction
        context_task = asyncio.create_task(self._extract_context_fast(query))
        
        # AI-powered extraction for complex queries (if needed)
        ai_context_task = None
        if len(query) > 100 or any(word in query.lower() for word in 
                                  ['sophomore', 'junior', 'failed', 'completed']):
            ai_context_task = asyncio.create_task(self._ai_context_extraction(query, session))
        
        # Wait for fast extraction
        fast_context = await context_task
        
        # Merge with AI context if available
        if ai_context_task:
            try:
                ai_context = await ai_context_task
                if ai_context:
                    fast_context.update(ai_context)
            except Exception:
                pass  # Use fast context only
        
        return fast_context
    
    async def _extract_context_fast(self, query: str) -> Dict[str, Any]:
        """Fast regex-based context extraction"""
        import re
        
        context = {}
        query_lower = query.lower()
        
        # Extract year information
        if "sophomore" in query_lower:
            context["current_year"] = "sophomore"
        elif "junior" in query_lower:
            context["current_year"] = "junior"
        elif "senior" in query_lower:
            context["current_year"] = "senior"
        elif "freshman" in query_lower:
            context["current_year"] = "freshman"
        
        # Extract course codes
        course_pattern = r'cs\s*(\d{5}|\d{3})'
        courses = re.findall(course_pattern, query_lower)
        if courses:
            context["mentioned_courses"] = [f"CS {c}" if len(c) == 3 else f"CS {c}00" for c in courses]
        
        # Extract track mentions
        if "machine intelligence" in query_lower or "mi track" in query_lower:
            context["target_track"] = "Machine Intelligence"
        elif "software engineering" in query_lower or "se track" in query_lower:
            context["target_track"] = "Software Engineering"
        
        return context
    
    @cached_ai_call(, , )
    async def _ai_context_extraction(self, query: str, session: SessionData) -> Optional[Dict[str, Any]]:
        """AI-powered context extraction for complex queries"""
        
        prompt = f"""
        Extract student information from this query: "{query}"
        
        Previous context: {json.dumps(session.extracted_context)}
        
        Return JSON with any of these fields found:
        - current_year: freshman/sophomore/junior/senior
        - completed_courses: ["CS 18000", "CS 18200"]
        - target_track: "Machine Intelligence" or "Software Engineering"
        - gpa: 3.5
        - failed_courses: ["CS 25100"]
        
        Only include explicitly mentioned information.
        """
        
        return [{"role": "user", "content": prompt}]
    
    async def _lookup_knowledge_async(self, query: str) -> Dict[str, Any]:
        """Async knowledge lookup with parallel searches"""
        
        # Parallel knowledge searches
        tasks = []
        
        # Course search
        if any(word in query.lower() for word in ['course', 'cs ', 'class']):
            tasks.append(asyncio.create_task(self._search_courses_async(query)))
        
        # Track search
        if any(word in query.lower() for word in ['track', 'major', 'specialization']):
            tasks.append(asyncio.create_task(self._search_tracks_async(query)))
        
        # Prerequisite search
        if any(word in query.lower() for word in ['prerequisite', 'prereq', 'required']):
            tasks.append(asyncio.create_task(self._search_prerequisites_async(query)))
        
        # Wait for all searches
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            combined_results = {}
            for result in results:
                if isinstance(result, dict):
                    combined_results.update(result)
            
            return combined_results
        
        return {}
    
    async def _search_courses_async(self, query: str) -> Dict[str, Any]:
        """Async course search"""
        courses = self.knowledge_cache.search_courses(query)
        course_info = {}
        
        for course_code in courses[:5]:  # Limit results
            info = self.knowledge_cache.get_course_info(course_code)
            if info:
                course_info[course_code] = info
        
        return {'courses': course_info}
    
    async def _search_tracks_async(self, query: str) -> Dict[str, Any]:
        """Async track search"""
        tracks = self.knowledge_cache.get_all_tracks()
        return {'tracks': tracks}
    
    async def _search_prerequisites_async(self, query: str) -> Dict[str, Any]:
        """Async prerequisite search"""
        # Extract course codes from query
        import re
        courses = re.findall(r'cs\s*(\d{5}|\d{3})', query.lower())
        
        prereq_info = {}
        for course in courses:
            course_code = f"CS {course}" if len(course) == 3 else f"CS {course}00"
            prereqs = self.knowledge_cache.get_prerequisites(course_code)
            if prereqs:
                prereq_info[course_code] = prereqs
        
        return {'prerequisites': prereq_info}
    
    async def _generate_response_async(self, query: str, session: SessionData,
                                     intent_analysis: Dict, context: Dict,
                                     knowledge: Dict) -> str:
        """Async response generation with AI optimization"""
        
        intent = intent_analysis['primary_intent']
        
        # Handle simple cases without AI
        if intent == 'greeting':
            return self._generate_greeting_response(session, context)
        
        # Use AI for complex responses
        return await self._generate_ai_response(query, session, intent_analysis, context, knowledge)
    
    def _generate_greeting_response(self, session: SessionData, context: Dict) -> str:
        """Generate greeting response without AI"""
        
        greetings = ["Hey! How can I help you today?", "Hi there! What can I assist you with?",
                    "Hello! Ready to help with your CS questions."]
        
        import random
        base_greeting = random.choice(greetings)
        
        # Personalize if we have context
        if context.get('current_year'):
            year = context['current_year']
            base_greeting += f" I see you're a {year} - I'm here to help with any CS questions you have."
        
        return base_greeting
    
    @cached_ai_call(, , )
    async def _generate_ai_response(self, query: str, session: SessionData,
                                  intent_analysis: Dict, context: Dict,
                                  knowledge: Dict) -> str:
        """AI-powered response generation with caching"""
        
        system_prompt = f"""
        You are a Purdue CS academic advisor. Provide helpful, accurate responses.
        
        Student Context: {json.dumps(context)}
        Intent: {intent_analysis['primary_intent']}
        Available Knowledge: {json.dumps(knowledge)}
        
        Respond naturally without markdown formatting.
        """
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    
    async def _update_session_async(self, session_id: str, query: str, response: str,
                                  context: Dict):
        """Async session update (non-blocking)"""
        try:
            self.session_manager.update_session(session_id, query, response, context)
        except Exception as e:
            print(f"Warning: Failed to update session {session_id}: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        
        # Combine stats from all components
        session_stats = self.session_manager.get_performance_stats()
        knowledge_stats = self.knowledge_cache.get_performance_stats()
        ai_stats = self.ai_optimizer.get_performance_stats()
        
        return {
            'conversation_metrics': {
                'total_requests': self.metrics.total_requests,
                'avg_response_time_ms': self.metrics.avg_response_time * 1000,
                'concurrent_sessions': self.metrics.concurrent_sessions,
                'peak_concurrent': self.metrics.peak_concurrent
            },
            'session_performance': session_stats,
            'knowledge_cache_performance': knowledge_stats,
            'ai_service_performance': ai_stats
        }


# Global async manager instance
_async_manager: Optional[AsyncConversationManager] = None


def get_async_conversation_manager() -> AsyncConversationManager:
    """Get or create global async conversation manager"""
    global _async_manager
    if _async_manager is None:
        _async_manager = AsyncConversationManager()
    return _async_manager