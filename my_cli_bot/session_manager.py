#!/usr/bin/env python3
"""
Session Manager for Multi-Turn Conversations
Maintains context and conversation history across interactions
"""

import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class SessionManager:
    def __init__(self, db_path="purdue_cs_knowledge.db"):
        self.db_path = db_path
        self.current_session_id = None
        
    def create_session(self, student_id: str = None) -> str:
        """Create a new conversation session"""
        session_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO session_context 
            (session_id, student_id, current_topic, conversation_history, extracted_context, last_activity)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session_id, student_id, '', '[]', '{}', datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        self.current_session_id = session_id
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieve session information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id, student_id, current_topic, conversation_history, extracted_context, last_activity
            FROM session_context WHERE session_id = ?
        ''', (session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'session_id': result[0],
                'student_id': result[1],
                'current_topic': result[2],
                'conversation_history': json.loads(result[3]) if result[3] else [],
                'extracted_context': json.loads(result[4]) if result[4] else {},
                'last_activity': result[5]
            }
        return None
    
    def update_session(self, session_id: str, query: str, response: str, context: Dict = None):
        """Update session with new conversation turn"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Add to conversation history
        conversation_turn = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response,
            'query_type': self._classify_query_type(query)
        }
        
        session['conversation_history'].append(conversation_turn)
        
        # Update extracted context
        if context:
            session['extracted_context'].update(context)
        
        # Update current topic
        session['current_topic'] = self._extract_current_topic(session['conversation_history'])
        
        # Keep only last 20 conversation turns for performance
        if len(session['conversation_history']) > 20:
            session['conversation_history'] = session['conversation_history'][-20:]
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE session_context 
            SET current_topic = ?, conversation_history = ?, extracted_context = ?, last_activity = ?
            WHERE session_id = ?
        ''', (
            session['current_topic'],
            json.dumps(session['conversation_history']),
            json.dumps(session['extracted_context']),
            datetime.now().isoformat(),
            session_id
        ))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_conversation_context(self, session_id: str) -> str:
        """Get conversation context for AI prompt"""
        session = self.get_session(session_id)
        if not session:
            return ""
        
        context_parts = []
        
        # Add current topic
        if session['current_topic']:
            context_parts.append(f"Current conversation topic: {session['current_topic']}")
        
        # Add recent conversation history
        recent_history = session['conversation_history'][-5:]  # Last 5 turns
        if recent_history:
            context_parts.append("Recent conversation:")
            for turn in recent_history:
                context_parts.append(f"  Student: {turn['query']}")
                context_parts.append(f"  BoilerAI: {turn['response'][:100]}...")
        
        # Add extracted context
        if session['extracted_context']:
            context_parts.append("Extracted context:")
            for key, value in session['extracted_context'].items():
                context_parts.append(f"  {key}: {value}")
        
        return "\n".join(context_parts)
    
    def _classify_query_type(self, query: str) -> str:
        """Classify the type of query for context tracking"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['prerequisite', 'prereq', 'requirement']):
            return 'prerequisites'
        elif any(word in query_lower for word in ['track', 'specialization', 'mi', 'se']):
            return 'track_planning'
        elif any(word in query_lower for word in ['professor', 'instructor', 'teacher']):
            return 'professor_info'
        elif any(word in query_lower for word in ['schedule', 'semester', 'planning']):
            return 'course_planning'
        elif any(word in query_lower for word in ['internship', 'career', 'job']):
            return 'career_guidance'
        elif any(word in query_lower for word in ['policy', 'exemption', 'transfer']):
            return 'academic_policy'
        else:
            return 'general_inquiry'
    
    def _extract_current_topic(self, conversation_history: List[Dict]) -> str:
        """Extract the current conversation topic"""
        if not conversation_history:
            return ""
        
        # Look at recent queries to determine topic
        recent_queries = [turn['query_type'] for turn in conversation_history[-3:]]
        
        # Find most common query type
        from collections import Counter
        topic_counts = Counter(recent_queries)
        most_common = topic_counts.most_common(1)
        
        if most_common:
            return most_common[0][0]
        
        return ""
    
    def extract_context_from_query(self, query: str) -> Dict[str, Any]:
        """Extract contextual information from user query"""
        context = {}
        
        import re
        
        # Extract course codes
        course_codes = re.findall(r'CS\s*(\d{5})', query.upper())
        if course_codes:
            context['mentioned_courses'] = [f'CS {code}' for code in course_codes]
        
        # Extract academic year mentions
        year_patterns = {
            'freshman': ['freshman', 'first year', '1st year'],
            'sophomore': ['sophomore', 'second year', '2nd year'],
            'junior': ['junior', 'third year', '3rd year'],
            'senior': ['senior', 'fourth year', '4th year']
        }
        
        query_lower = query.lower()
        for year, patterns in year_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                context['academic_year'] = year
                break
        
        # Extract track mentions
        track_patterns = {
            'Machine Intelligence': ['machine intelligence', 'mi track', 'ai', 'artificial intelligence'],
            'Software Engineering': ['software engineering', 'se track', 'software development']
        }
        
        for track, patterns in track_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                context['track_interest'] = track
                break
        
        # Extract difficulty preferences
        if any(word in query_lower for word in ['easy', 'simple', 'basic']):
            context['difficulty_preference'] = 'easy'
        elif any(word in query_lower for word in ['hard', 'challenging', 'difficult']):
            context['difficulty_preference'] = 'challenging'
        elif any(word in query_lower for word in ['moderate', 'medium', 'average']):
            context['difficulty_preference'] = 'moderate'
        
        return context
    
    def cleanup_old_sessions(self, days_old: int = 30):
        """Clean up sessions older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM session_context 
            WHERE last_activity < ?
        ''', (cutoff_date.isoformat(),))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count

if __name__ == "__main__":
    # Test session manager
    session_mgr = SessionManager()
    
    # Create test session
    session_id = session_mgr.create_session("test_student")
    print(f"Created session: {session_id}")
    
    # Test conversation
    session_mgr.update_session(session_id, 
                              "What are the prerequisites for CS 25000?", 
                              "CS 25000 requires CS 18000 and CS 18200...")
    
    # Get context
    context = session_mgr.get_conversation_context(session_id)
    print(f"Context: {context}")