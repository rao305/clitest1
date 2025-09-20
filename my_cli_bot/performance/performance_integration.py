#!/usr/bin/env python3
"""
Performance Integration Layer
Integrates all optimizations with the existing system and provides migration path
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

# Import optimized components
from .optimized_conversation_manager import get_async_conversation_manager
from .optimized_session_manager import OptimizedSessionManager
from .knowledge_cache import get_knowledge_cache
from .ai_service_optimizer import get_ai_optimizer
from .performance_monitor import get_performance_monitor, async_performance_tracking
from .connection_pool import initialize_pool


class PerformanceIntegration:
    """Integration layer for high-performance components"""
    
    def __init__(self, db_path: str = "purdue_cs_knowledge.db"):
        self.db_path = db_path
        
        # Initialize all performance components
        self._initialize_components()
        
        # Performance tracking
        self.monitor = get_performance_monitor()
        
        print("🚀 High-Performance Boiler AI System Ready")
        print(f"📊 Performance monitoring active")
        print(f"🧠 Knowledge cache loaded: {self.knowledge_cache.get_performance_stats()['courses_cached']} courses")
        print(f"💾 Database pool initialized: {self.session_manager.get_performance_stats()['cache_size']} sessions cached")
    
    def _initialize_components(self):
        """Initialize all performance-optimized components"""
        
        # Initialize database connection pool
        initialize_pool(self.db_path, pool_size=15)
        
        # Initialize optimized session manager
        self.session_manager = OptimizedSessionManager(self.db_path)
        
        # Initialize knowledge cache
        self.knowledge_cache = get_knowledge_cache()
        
        # Initialize AI optimizer
        self.ai_optimizer = get_ai_optimizer()
        
        # Initialize async conversation manager
        self.conversation_manager = get_async_conversation_manager()
    
    @async_performance_tracking
    async def process_query(self, session_id: str, query: str) -> str:
        """High-performance query processing"""
        
        start_time = time.time()
        
        try:
            # Use optimized async conversation manager
            response = await self.conversation_manager.process_query_async(session_id, query)
            
            processing_time = time.time() - start_time
            print(f"⚡ Query processed in {processing_time:.3f}s")
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"❌ Query failed after {processing_time:.3f}s: {e}")
            
            # Fallback to basic response
            return "I encountered an error processing your query. Please try again or rephrase your question."
    
    def process_query_sync(self, session_id: str, query: str) -> str:
        """Synchronous wrapper for async processing"""
        
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, use ThreadPoolExecutor
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.process_query(session_id, query))
                    return future.result(timeout=30)
            else:
                return loop.run_until_complete(self.process_query(session_id, query))
        except RuntimeError:
            # Create new event loop if none exists
            return asyncio.run(self.process_query(session_id, query))
    
    def create_session(self, student_id: str = None) -> str:
        """Create optimized session"""
        return self.session_manager.create_session(student_id)
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        session = self.session_manager.get_session(session_id)
        return session.to_dict() if session else None
    
    def get_course_info(self, course_code: str) -> Optional[Dict[str, Any]]:
        """Get optimized course information"""
        return self.knowledge_cache.get_course_info(course_code)
    
    def search_courses(self, query: str) -> List[str]:
        """Search courses with caching"""
        return self.knowledge_cache.search_courses(query)
    
    def get_prerequisites(self, course_code: str) -> List[str]:
        """Get course prerequisites"""
        return self.knowledge_cache.get_prerequisites(course_code)
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        
        return {
            'system_performance': self.monitor.get_performance_summary(),
            'conversation_stats': self.conversation_manager.get_performance_stats(),
            'session_stats': self.session_manager.get_performance_stats(),
            'knowledge_cache_stats': self.knowledge_cache.get_performance_stats(),
            'ai_service_stats': self.ai_optimizer.get_performance_stats(),
            'real_time_metrics': self.monitor.get_real_time_stats()
        }
    
    def cleanup_old_data(self, days: int = 30):
        """Cleanup old data for performance maintenance"""
        
        # Cleanup old sessions
        deleted_sessions = self.session_manager.cleanup_old_sessions(days)
        
        # Clear AI cache if needed
        ai_stats = self.ai_optimizer.get_performance_stats()
        if ai_stats['cache_size'] > 5000:
            self.ai_optimizer.clear_cache()
        
        # Clear knowledge search cache
        self.knowledge_cache.clear_search_cache()
        
        print(f"🧹 Cleanup completed: {deleted_sessions} old sessions removed")
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        
        health_status = {
            'status': 'healthy',
            'checks': {},
            'timestamp': time.time()
        }
        
        try:
            # Test database connection
            test_session = self.session_manager.create_session()
            health_status['checks']['database'] = 'healthy'
        except Exception as e:
            health_status['checks']['database'] = f'error: {e}'
            health_status['status'] = 'degraded'
        
        try:
            # Test knowledge cache
            courses = self.knowledge_cache.search_courses('CS 18000')
            health_status['checks']['knowledge_cache'] = 'healthy' if courses else 'no_data'
        except Exception as e:
            health_status['checks']['knowledge_cache'] = f'error: {e}'
            health_status['status'] = 'degraded'
        
        try:
            # Test AI service
            ai_stats = self.ai_optimizer.get_performance_stats()
            health_status['checks']['ai_service'] = 'healthy'
        except Exception as e:
            health_status['checks']['ai_service'] = f'error: {e}'
            health_status['status'] = 'degraded'
        
        # Check performance metrics
        perf_summary = self.monitor.get_performance_summary()
        current = perf_summary.get('current', {})
        
        if current.get('cpu_percent', 0) > 90:
            health_status['status'] = 'degraded'
            health_status['checks']['cpu'] = 'high_usage'
        else:
            health_status['checks']['cpu'] = 'normal'
        
        if current.get('memory_percent', 0) > 90:
            health_status['status'] = 'degraded'
            health_status['checks']['memory'] = 'high_usage'
        else:
            health_status['checks']['memory'] = 'normal'
        
        return health_status


# Global integration instance
_integration: Optional[PerformanceIntegration] = None


def get_performance_integration(db_path: str = "purdue_cs_knowledge.db") -> PerformanceIntegration:
    """Get or create global performance integration instance"""
    global _integration
    if _integration is None:
        _integration = PerformanceIntegration(db_path)
    return _integration


# Compatibility layer for existing code
class OptimizedUniversalPurdueAdvisor:
    """Drop-in replacement for UniversalPurdueAdvisor with performance optimizations"""
    
    def __init__(self):
        self.integration = get_performance_integration()
        print("🚀 Optimized Universal Purdue Advisor initialized")
    
    def start_new_session(self) -> str:
        """Start a new conversation session"""
        return self.integration.create_session()
    
    def ask_question(self, question: str, session_id: str = None) -> str:
        """Main interface for asking questions with performance optimization"""
        
        # Create session if not provided
        if not session_id:
            session_id = self.integration.create_session()
        
        # Process with optimized system
        return self.integration.process_query_sync(session_id, question)
    
    def generate_comprehensive_response(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive response (compatibility method)"""
        
        session_id = context.get('session_id') if context else None
        if not session_id:
            session_id = self.integration.create_session()
        
        response = self.integration.process_query_sync(session_id, query)
        
        return {
            'response': response,
            'session_id': session_id,
            'timestamp': time.time(),
            'performance_optimized': True
        }
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get session context (compatibility method)"""
        return self.integration.get_session_info(session_id) or {}
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get detailed performance report"""
        return self.integration.get_comprehensive_stats()


# Factory function for easy migration
def create_optimized_advisor() -> OptimizedUniversalPurdueAdvisor:
    """Create optimized advisor instance"""
    return OptimizedUniversalPurdueAdvisor()