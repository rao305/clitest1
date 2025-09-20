#!/usr/bin/env python3
"""
Enhanced Flask API with Session Management and Feedback
Integrates all new features into the web API
"""

from flask import Flask, request, jsonify
import os
import uuid
from datetime import datetime

# Import enhanced components
from session_manager import SessionManager
from feedback_system import FeedbackSystem, FeedbackPromptGenerator
from smart_ai_engine import SmartAIEngine
from enhanced_database import EnhancedDatabase

app = Flask(__name__)

# Initialize enhanced components
session_manager = SessionManager()
feedback_system = FeedbackSystem()
smart_ai = SmartAIEngine()

# Initialize database
enhanced_db = EnhancedDatabase()

@app.route('/api/chat', methods=['POST'])
def enhanced_chat():
    """Enhanced chat endpoint with session management"""
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        session_id = data.get('session_id')
        student_id = data.get('student_id')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Create or get session
        if not session_id:
            session_id = session_manager.create_session(student_id)
        elif not session_manager.get_session(session_id):
            session_id = session_manager.create_session(student_id)
        
        # Get conversation context
        conversation_context = session_manager.get_conversation_context(session_id)
        
        # Extract query context
        query_context = session_manager.extract_context_from_query(query)
        
        # Combine contexts for AI
        full_context = {
            'conversation_history': conversation_context,
            'query_context': query_context
        }
        
        # Generate intelligent response with context
        start_time = datetime.now()
        response_data = smart_ai.generate_intelligent_response(query, full_context)
        end_time = datetime.now()
        
        # Add session metadata
        response_data['session_id'] = session_id
        response_data['response_time_ms'] = int((end_time - start_time).total_seconds() * 1000)
        response_data['query_type'] = session_manager._classify_query_type(query)
        
        # Update session context
        session_manager.update_session(session_id, query, response_data['response'], query_context)
        
        # Add feedback prompt
        feedback_prompt = FeedbackPromptGenerator.get_feedback_prompt(response_data['query_type'])
        response_data['feedback_prompt'] = feedback_prompt
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/feedback', methods=['POST'])
def collect_feedback():
    """Collect user feedback for responses"""
    
    try:
        data = request.get_json()
        
        required_fields = ['session_id', 'query', 'response', 'rating']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate rating
        rating = data.get('rating')
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400
        
        # Collect feedback
        success = feedback_system.collect_feedback(
            session_id=data['session_id'],
            query=data['query'],
            response=data['response'],
            rating=rating,
            feedback_text=data.get('feedback_text', ''),
            intent_classification=data.get('intent_classification', ''),
            response_time_ms=data.get('response_time_ms', 0),
            student_id=data.get('student_id')
        )
        
        if success:
            # Generate follow-up message
            follow_up = FeedbackPromptGenerator.get_follow_up_prompt(rating)
            
            return jsonify({
                'success': True,
                'message': 'Feedback collected successfully',
                'follow_up': follow_up
            })
        else:
            return jsonify({'error': 'Failed to collect feedback'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/session', methods=['POST'])
def create_session():
    """Create a new chat session"""
    
    try:
        data = request.get_json() or {}
        student_id = data.get('student_id')
        
        session_id = session_manager.create_session(student_id)
        
        return jsonify({
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'student_id': student_id
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session information"""
    
    try:
        session = session_manager.get_session(session_id)
        
        if session:
            return jsonify(session)
        else:
            return jsonify({'error': 'Session not found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/session/<session_id>/context', methods=['GET'])
def get_session_context(session_id):
    """Get conversation context for a session"""
    
    try:
        context = session_manager.get_conversation_context(session_id)
        
        return jsonify({
            'session_id': session_id,
            'context': context
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/feedback/stats', methods=['GET'])
def get_feedback_stats():
    """Get feedback statistics"""
    
    try:
        days = request.args.get('days', 30, type=int)
        stats = feedback_system.get_feedback_stats(days)
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/feedback/suggestions', methods=['GET'])
def get_improvement_suggestions():
    """Get improvement suggestions based on feedback"""
    
    try:
        suggestions = feedback_system.get_improvement_suggestions()
        
        return jsonify({
            'suggestions': suggestions,
            'count': len(suggestions)
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/policies', methods=['GET'])
def get_policies():
    """Get academic policies"""
    
    try:
        import sqlite3
        conn = sqlite3.connect('purdue_cs_knowledge.db')
        cursor = conn.cursor()
        
        category = request.args.get('category')
        
        if category:
            cursor.execute('''
                SELECT policy_id, category, title, description, applicable_courses, source_url
                FROM policies WHERE category = ?
            ''', (category,))
        else:
            cursor.execute('''
                SELECT policy_id, category, title, description, applicable_courses, source_url
                FROM policies
            ''')
        
        policies = []
        for row in cursor.fetchall():
            import json
            policies.append({
                'policy_id': row[0],
                'category': row[1],
                'title': row[2],
                'description': row[3],
                'applicable_courses': json.loads(row[4]) if row[4] else [],
                'source_url': row[5]
            })
        
        conn.close()
        
        return jsonify({
            'policies': policies,
            'count': len(policies)
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/resources', methods=['GET'])
def get_resources():
    """Get student resources"""
    
    try:
        import sqlite3
        conn = sqlite3.connect('purdue_cs_knowledge.db')
        cursor = conn.cursor()
        
        resource_type = request.args.get('type')
        
        if resource_type:
            cursor.execute('''
                SELECT resource_id, type, name, description, contact_info, meeting_times, location, website_url
                FROM resources WHERE type = ?
            ''', (resource_type,))
        else:
            cursor.execute('''
                SELECT resource_id, type, name, description, contact_info, meeting_times, location, website_url
                FROM resources
            ''')
        
        resources = []
        for row in cursor.fetchall():
            resources.append({
                'resource_id': row[0],
                'type': row[1],
                'name': row[2],
                'description': row[3],
                'contact_info': row[4],
                'meeting_times': row[5],
                'location': row[6],
                'website_url': row[7]
            })
        
        conn.close()
        
        return jsonify({
            'resources': resources,
            'count': len(resources)
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard with system statistics"""
    
    try:
        # Get feedback stats
        feedback_stats = feedback_system.get_feedback_stats()
        
        # Get session count
        import sqlite3
        conn = sqlite3.connect('purdue_cs_knowledge.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM session_context')
        total_sessions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM session_context WHERE last_activity > datetime("now", "-1 day")')
        active_sessions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM policies')
        total_policies = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM resources')
        total_resources = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'system_status': 'active',
            'feedback': feedback_stats,
            'sessions': {
                'total': total_sessions,
                'active_today': active_sessions
            },
            'knowledge_base': {
                'policies': total_policies,
                'resources': total_resources,
                'courses': 55  # From knowledge graph
            },
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    
    try:
        # Test database connection
        import sqlite3
        conn = sqlite3.connect('purdue_cs_knowledge.db')
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        conn.close()
        
        # Test AI engine
        test_response = smart_ai.generate_intelligent_response("test")
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'ai_engine': 'active',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # Check for required environment variables
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        exit(1)
    
    print("🚀 Starting Enhanced BoilerAI API...")
    print("📊 Dashboard: http://0.0.0.0:5000/api/dashboard")
    print("🔗 Chat API: http://0.0.0.0:5000/api/chat")
    print("📝 Feedback API: http://0.0.0.0:5000/api/feedback")
    print("📋 Policies API: http://0.0.0.0:5000/api/policies")
    print("📚 Resources API: http://0.0.0.0:5000/api/resources")
    
    app.run(host='0.0.0.0', port=5000, debug=True)