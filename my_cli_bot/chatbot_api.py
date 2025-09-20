#!/usr/bin/env python3
"""
Chatbot API Server - Bridge between frontend and BoilerAI backend
Provides REST API endpoints for web interface integration
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import os
import sys
import logging
from datetime import datetime
import uuid

# Import your existing chatbot system
from intelligent_conversation_manager import IntelligentConversationManager
from smart_ai_engine import SmartAIEngine

app = Flask(__name__)
CORS(app, origins=["*"])  # Allow all origins for development

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
conversation_manager = None
smart_ai_engine = None

def initialize_chatbot():
    """Initialize the chatbot system"""
    global conversation_manager, smart_ai_engine
    
    try:
        # Check environment variables
        if not os.environ.get("GEMINI_API_KEY"):
            logger.error("GEMINI_API_KEY environment variable not set")
            return False
            
        # Initialize AI systems
        conversation_manager = IntelligentConversationManager()
        smart_ai_engine = SmartAIEngine()
        
        logger.info("✅ Chatbot system initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize chatbot: {e}")
        return False

@app.route('/')
def index():
    """Serve the chatbot web interface"""
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BoilerAI - Purdue CS Academic Advisor</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .chat-container {
            width: 90%;
            max-width: 800px;
            height: 80vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #B5651D, #C6A558);
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .chat-header h1 {
            margin: 0;
            font-size: 24px;
        }
        
        .chat-header p {
            margin: 5px 0 0 0;
            opacity: 0.9;
            font-size: 14px;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .message {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        
        .user-message {
            background: #007bff;
            color: white;
            align-self: flex-end;
            margin-left: auto;
        }
        
        .bot-message {
            background: #f1f3f4;
            color: #333;
            align-self: flex-start;
            border: 1px solid #e0e0e0;
        }
        
        .typing {
            background: #f1f3f4;
            color: #666;
            align-self: flex-start;
            font-style: italic;
        }
        
        .chat-input {
            padding: 20px;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
        }
        
        .input-field {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
        }
        
        .input-field:focus {
            border-color: #007bff;
        }
        
        .send-button {
            background: #007bff;
            color: white;
            border: none;
            border-radius: 50%;
            width: 45px;
            height: 45px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.3s;
        }
        
        .send-button:hover {
            background: #0056b3;
        }
        
        .send-button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .error-message {
            background: #ff4444;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 20px;
        }
        
        @media (max-width: 600px) {
            .chat-container {
                width: 95%;
                height: 90vh;
            }
            
            .message {
                max-width: 90%;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤖 BoilerAI</h1>
            <p>Your Purdue CS Academic Advisor</p>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                Hello! I'm BoilerAI, your Purdue Computer Science academic advisor. I can help you with course planning, track selection, graduation requirements, and career guidance. What would you like to know?
            </div>
        </div>
        
        <div class="chat-input">
            <input type="text" class="input-field" id="messageInput" 
                   placeholder="Ask me about CS courses, tracks, graduation planning..." 
                   maxlength="500">
            <button class="send-button" id="sendButton" onclick="sendMessage()">
                ➤
            </button>
        </div>
    </div>

    <script>
        let sessionId = generateSessionId();
        
        function generateSessionId() {
            return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }
        
        function addMessage(content, isUser = false) {
            const messagesContainer = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            messageDiv.textContent = content;
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        function showTyping() {
            const messagesContainer = document.getElementById('chatMessages');
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message typing';
            typingDiv.id = 'typing-indicator';
            typingDiv.textContent = 'BoilerAI is thinking...';
            messagesContainer.appendChild(typingDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        function hideTyping() {
            const typingIndicator = document.getElementById('typing-indicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
        }
        
        function showError(message) {
            const container = document.querySelector('.chat-container');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = message;
            container.insertBefore(errorDiv, container.querySelector('.chat-messages'));
            
            setTimeout(() => {
                errorDiv.remove();
            }, 5000);
        }
        
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const sendButton = document.getElementById('sendButton');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            addMessage(message, true);
            input.value = '';
            
            // Disable input
            sendButton.disabled = true;
            input.disabled = true;
            
            // Show typing indicator
            showTyping();
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        session_id: sessionId
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                
                if (data.success) {
                    hideTyping();
                    addMessage(data.response);
                } else {
                    throw new Error(data.error || 'Unknown error occurred');
                }
                
            } catch (error) {
                console.error('Error:', error);
                hideTyping();
                showError('Sorry, I encountered an error. Please try again.');
                addMessage('I apologize, but I\'m having trouble processing your request right now. Please try again or rephrase your question.');
            } finally {
                // Re-enable input
                sendButton.disabled = false;
                input.disabled = false;
                input.focus();
            }
        }
        
        // Handle Enter key
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Focus input on load
        document.getElementById('messageInput').focus();
    </script>
</body>
</html>
    """)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from frontend"""
    
    if not conversation_manager:
        return jsonify({
            'success': False,
            'error': 'Chatbot system not initialized. Please check server configuration.'
        }), 503
    
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        message = data['message'].strip()
        session_id = data.get('session_id', f'web_session_{uuid.uuid4()}')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400
        
        if len(message) > 500:
            return jsonify({
                'success': False,
                'error': 'Message too long (maximum 500 characters)'
            }), 400
        
        logger.info(f"Processing message for session {session_id}: {message[:100]}...")
        
        # Process message through your chatbot system
        try:
            response = conversation_manager.process_query(session_id, message)
            
            if not response:
                response = "I'm sorry, I couldn't process your question right now. Please try rephrasing it or ask something else about Purdue CS."
            
            logger.info(f"Generated response for session {session_id}: {len(response)} chars")
            
            return jsonify({
                'success': True,
                'response': response,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            
            # Generate AI fallback response
            fallback_response = "I encountered an issue while processing your question. As your Purdue CS advisor, I'm still here to help. Please try asking about course planning, track selection, or graduation requirements."
            
            return jsonify({
                'success': True,
                'response': fallback_response,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
        
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'chatbot_initialized': conversation_manager is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stats')
def stats():
    """Get system statistics"""
    return jsonify({
        'system': 'BoilerAI',
        'version': '2.0',
        'features': [
            'Course Planning',
            'Track Selection', 
            'Graduation Planning',
            'Career Networking',
            'Failure Recovery',
            'AI-Powered Responses'
        ],
        'status': 'operational' if conversation_manager else 'initializing'
    })

if __name__ == '__main__':
    print("🚀 Starting BoilerAI Web Server...")
    
    # Initialize chatbot system
    if initialize_chatbot():
        print("✅ Chatbot system ready")
        print("🌐 Starting web server on http://localhost:5000")
        print("📱 Open your browser and go to: http://localhost:5000")
        print("\n🔧 Environment Check:")
        print(f"   Gemini API Key: {'✅ Set' if os.environ.get('GEMINI_API_KEY') else '❌ Missing'}")
        print(f"   Clado API Key: {'✅ Set' if os.environ.get('CLADO_API_KEY') else '⚠️ Optional'}")
        
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("❌ Failed to initialize chatbot system")
        print("💡 Make sure you have set your environment variables:")
        print("   export GEMINI_API_KEY='your-key-here'")
        print("   export CLADO_API_KEY='your-clado-key-here'")
        sys.exit(1)