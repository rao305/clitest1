#!/usr/bin/env python3
"""
Simple BoilerAI API Server
Lightweight integration for existing websites
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime
import uuid

# Import your chatbot system
try:
    from intelligent_conversation_manager import IntelligentConversationManager
    from smart_ai_engine import SmartAIEngine
except ImportError as e:
    print(f"❌ Failed to import chatbot modules: {e}")
    print("💡 Make sure you're running from the my_cli_bot directory")
    exit(1)

app = Flask(__name__)

# Configure CORS for all domains (adjust for production)
CORS(app, origins=["*"], methods=["GET", "POST", "OPTIONS"])

# Simple logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Global chatbot instance
chatbot = None

def init_chatbot():
    """Initialize BoilerAI system"""
    global chatbot
    try:
        if not os.environ.get("GEMINI_API_KEY"):
            logger.error("GEMINI_API_KEY not found in environment")
            return False
        
        chatbot = IntelligentConversationManager()
        logger.info("✅ BoilerAI initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize BoilerAI: {e}")
        return False

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat_endpoint():
    """Main chat endpoint for your website"""
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
    
    if not chatbot:
        return jsonify({
            'success': False,
            'error': 'BoilerAI system not initialized'
        }), 503
    
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        message = data['message'].strip()
        session_id = data.get('session_id', f'web_{uuid.uuid4()}')
        
        if not message or len(message) > 1000:
            return jsonify({
                'success': False,
                'error': 'Message must be between 1-1000 characters'
            }), 400
        
        # Process with BoilerAI
        response = chatbot.process_query(session_id, message)
        
        if not response:
            response = "I'm here to help with Purdue CS questions. Could you please rephrase your question or ask about courses, tracks, or graduation planning?"
        
        return jsonify({
            'success': True,
            'response': response,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if chatbot else 'initializing',
        'service': 'BoilerAI',
        'version': '2.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/info', methods=['GET'])
def info():
    """Get BoilerAI information"""
    return jsonify({
        'name': 'BoilerAI',
        'description': 'Purdue CS Academic Advisor',
        'capabilities': [
            'Course planning and prerequisites',
            'Track selection (MI/SE)',
            'Graduation timeline planning',
            'CODO requirements guidance',
            'Career networking assistance',
            'Course failure recovery planning'
        ],
        'usage': {
            'endpoint': '/api/chat',
            'method': 'POST',
            'payload': {
                'message': 'Your question here',
                'session_id': 'optional_session_id'
            }
        }
    })

@app.route('/boilerai-client.js', methods=['GET'])
def serve_client_js():
    """Serve the JavaScript client library"""
    try:
        with open('boilerai-client.js', 'r') as f:
            js_content = f.read()
        
        return app.response_class(
            js_content,
            mimetype='application/javascript',
            headers={'Access-Control-Allow-Origin': '*'}
        )
    except FileNotFoundError:
        return "BoilerAI client library not found", 404

if __name__ == '__main__':
    print("🚀 Starting BoilerAI API Server...")
    print("🔧 Checking environment...")
    
    if not os.environ.get("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY not set")
        print("💡 Set it with: export GEMINI_API_KEY='your-key-here'")
        exit(1)
    
    if init_chatbot():
        print("✅ BoilerAI ready")
        print("🌐 API available at: http://localhost:3001")
        print("📡 Main endpoint: POST /api/chat")
        print("🔍 Health check: GET /api/health")
        print("ℹ️  Info: GET /api/info")
        print("\n🛑 Press Ctrl+C to stop")
        
        app.run(host='0.0.0.0', port=3001, debug=False)
    else:
        print("❌ Failed to start BoilerAI")
        exit(1)