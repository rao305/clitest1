#!/usr/bin/env python3
"""
User Feedback Collection System
Collects ratings and learns from user interactions to improve responses
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class FeedbackSystem:
    def __init__(self, db_path="purdue_cs_knowledge.db"):
        self.db_path = db_path
        
    def collect_feedback(self, session_id: str, query: str, response: str, 
                        rating: int, feedback_text: str = "", 
                        intent_classification: str = "", 
                        response_time_ms: int = 0, 
                        student_id: str = None) -> bool:
        """Collect user feedback for a response"""
        
        if rating < 1 or rating > 5:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_feedback 
            (session_id, student_id, query, response, rating, feedback_text, 
             intent_classification, response_time_ms, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id, student_id, query, response, rating, 
            feedback_text, intent_classification, response_time_ms,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # Analyze feedback to improve system
        self._analyze_feedback_patterns()
        
        return True
    
    def get_feedback_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get feedback statistics for the last N days"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get overall stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_feedback,
                AVG(rating) as avg_rating,
                MIN(rating) as min_rating,
                MAX(rating) as max_rating
            FROM user_feedback 
            WHERE timestamp > datetime('now', '-{} days')
        '''.format(days))
        
        overall_stats = cursor.fetchone()
        
        # Get rating distribution
        cursor.execute('''
            SELECT rating, COUNT(*) as count
            FROM user_feedback 
            WHERE timestamp > datetime('now', '-{} days')
            GROUP BY rating
            ORDER BY rating
        '''.format(days))
        
        rating_distribution = dict(cursor.fetchall())
        
        # Get feedback by intent type
        cursor.execute('''
            SELECT intent_classification, AVG(rating) as avg_rating, COUNT(*) as count
            FROM user_feedback 
            WHERE timestamp > datetime('now', '-{} days')
            AND intent_classification != ''
            GROUP BY intent_classification
            ORDER BY avg_rating DESC
        '''.format(days))
        
        intent_stats = cursor.fetchall()
        
        # Get low-rated responses for improvement
        cursor.execute('''
            SELECT query, response, rating, feedback_text
            FROM user_feedback 
            WHERE rating <= 2
            AND timestamp > datetime('now', '-{} days')
            ORDER BY timestamp DESC
            LIMIT 10
        '''.format(days))
        
        low_rated_responses = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_feedback': overall_stats[0] if overall_stats[0] else 0,
            'average_rating': round(overall_stats[1], 2) if overall_stats[1] else 0,
            'min_rating': overall_stats[2] if overall_stats[2] else 0,
            'max_rating': overall_stats[3] if overall_stats[3] else 0,
            'rating_distribution': rating_distribution,
            'intent_performance': [
                {'intent': row[0], 'avg_rating': round(row[1], 2), 'count': row[2]}
                for row in intent_stats
            ],
            'low_rated_responses': [
                {'query': row[0], 'response': row[1][:100] + '...', 'rating': row[2], 'feedback': row[3]}
                for row in low_rated_responses
            ]
        }
    
    def get_improvement_suggestions(self) -> List[Dict[str, Any]]:
        """Get suggestions for improving the system based on feedback"""
        
        suggestions = []
        stats = self.get_feedback_stats()
        
        # Check overall performance
        if stats['average_rating'] < 3.5:
            suggestions.append({
                'type': 'overall_performance',
                'priority': 'high',
                'message': f"Overall rating is low ({stats['average_rating']}/5). Review response quality and accuracy.",
                'action': 'Review low-rated responses and improve knowledge base'
            })
        
        # Check intent-specific performance
        for intent in stats['intent_performance']:
            if intent['avg_rating'] < 3.0 and intent['count'] >= 5:
                suggestions.append({
                    'type': 'intent_performance',
                    'priority': 'medium',
                    'message': f"Intent '{intent['intent']}' has low rating ({intent['avg_rating']}/5)",
                    'action': f"Improve responses for {intent['intent']} queries"
                })
        
        # Check for common issues in feedback text
        common_issues = self._analyze_common_feedback_issues()
        for issue in common_issues:
            suggestions.append({
                'type': 'common_issue',
                'priority': 'medium',
                'message': f"Common feedback issue: {issue['issue']}",
                'action': issue['suggested_action']
            })
        
        return suggestions
    
    def _analyze_feedback_patterns(self):
        """Analyze feedback patterns to identify trends"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Look for recent patterns
        cursor.execute('''
            SELECT intent_classification, AVG(rating), COUNT(*)
            FROM user_feedback 
            WHERE timestamp > datetime('now', '-7 days')
            AND intent_classification != ''
            GROUP BY intent_classification
            HAVING COUNT(*) >= 3
        ''')
        
        recent_patterns = cursor.fetchall()
        
        # Log patterns for review
        for pattern in recent_patterns:
            intent, avg_rating, count = pattern
            if avg_rating < 3.0:
                print(f"⚠️ Low performance alert: {intent} intent has {avg_rating:.1f}/5 rating over {count} responses")
        
        conn.close()
    
    def _analyze_common_feedback_issues(self) -> List[Dict[str, str]]:
        """Analyze feedback text for common issues"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT feedback_text
            FROM user_feedback 
            WHERE rating <= 3
            AND feedback_text != ''
            AND timestamp > datetime('now', '-30 days')
        ''')
        
        feedback_texts = [row[0].lower() for row in cursor.fetchall()]
        conn.close()
        
        common_issues = []
        
        # Analyze for common complaint patterns
        issue_patterns = {
            'incorrect information': ['wrong', 'incorrect', 'inaccurate', 'false'],
            'missing information': ['missing', "doesn't know", 'incomplete', 'lacking'],
            'unclear response': ['confusing', 'unclear', "doesn't understand", 'vague'],
            'slow response': ['slow', 'took too long', 'delayed'],
            'irrelevant response': ['irrelevant', 'off-topic', "doesn't answer"]
        }
        
        for issue_type, keywords in issue_patterns.items():
            count = sum(1 for text in feedback_texts if any(keyword in text for keyword in keywords))
            
            if count >= 2:  # If 2 or more instances
                action_map = {
                    'incorrect information': 'Update knowledge base with correct information',
                    'missing information': 'Expand knowledge base coverage',
                    'unclear response': 'Improve response clarity and structure',
                    'slow response': 'Optimize response generation speed',
                    'irrelevant response': 'Improve intent classification accuracy'
                }
                
                common_issues.append({
                    'issue': f"{issue_type} ({count} instances)",
                    'suggested_action': action_map[issue_type]
                })
        
        return common_issues
    
    def prompt_for_feedback(self, query: str, response: str, session_id: str) -> str:
        """Generate a prompt asking for user feedback"""
        
        prompts = [
            "How helpful was this response? Rate 1-5 (5=very helpful):",
            "Was this answer useful? Please rate 1-5:",
            "Rate the quality of this response (1-5):",
            "How satisfied are you with this answer? (1-5 scale):"
        ]
        
        import random
        return random.choice(prompts)
    
    def process_feedback_input(self, feedback_input: str) -> Optional[Dict[str, Any]]:
        """Process user feedback input and extract rating/comments"""
        
        import re
        
        # Look for rating (1-5)
        rating_match = re.search(r'[1-5]', feedback_input)
        if not rating_match:
            return None
        
        rating = int(rating_match.group())
        
        # Extract additional comments
        feedback_text = feedback_input.strip()
        
        # Remove the rating number from feedback text
        feedback_text = re.sub(r'[1-5]', '', feedback_text).strip()
        feedback_text = feedback_text.replace('rating:', '').replace('rate:', '').strip()
        
        return {
            'rating': rating,
            'feedback_text': feedback_text if len(feedback_text) > 3 else ""
        }

class FeedbackPromptGenerator:
    """Generate natural feedback prompts for different contexts"""
    
    @staticmethod
    def get_feedback_prompt(query_type: str = "general") -> str:
        """Get context-appropriate feedback prompt"""
        
        prompts = {
            'prerequisites': "Did I correctly explain the prerequisites? Rate 1-5:",
            'track_planning': "Was this track guidance helpful? Rate 1-5:",
            'professor_info': "Was the professor information accurate? Rate 1-5:",
            'course_planning': "Did this help with your course planning? Rate 1-5:",
            'career_guidance': "Was this career advice useful? Rate 1-5:",
            'academic_policy': "Did I answer your policy question clearly? Rate 1-5:",
            'general_inquiry': "How helpful was this response? Rate 1-5:"
        }
        
        return prompts.get(query_type, prompts['general_inquiry'])
    
    @staticmethod
    def get_follow_up_prompt(rating: int) -> str:
        """Get follow-up prompt based on rating"""
        
        if rating >= 4:
            return "Great! Any additional questions about this topic?"
        elif rating == 3:
            return "Thanks for the feedback. What could I improve?"
        else:
            return "Sorry this wasn't helpful. Can you tell me what went wrong?"

if __name__ == "__main__":
    # Test feedback system
    feedback_system = FeedbackSystem()
    
    # Test collecting feedback
    test_session = "test_session_123"
    success = feedback_system.collect_feedback(
        session_id=test_session,
        query="What are the prerequisites for CS 25000?",
        response="CS 25000 requires CS 18000 and CS 18200...",
        rating=4,
        feedback_text="Very helpful explanation",
        intent_classification="prerequisites",
        response_time_ms=1500
    )
    
    print(f"Feedback collected: {success}")
    
    # Get stats
    stats = feedback_system.get_feedback_stats()
    print(f"Feedback stats: {stats}")
    
    # Get suggestions
    suggestions = feedback_system.get_improvement_suggestions()
    print(f"Improvement suggestions: {suggestions}")