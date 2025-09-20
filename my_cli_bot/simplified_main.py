#!/usr/bin/env python3
"""
Simplified main entry point for development
"""

import os
import sys
import json
from flask import Flask, request, jsonify
from enhanced_llm_engine import EnhancedLLMEngine
from enhanced_smart_advisor import EnhancedSmartAdvisor

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# Initialize enhanced LLM engine and smart advisor
llm_engine = EnhancedLLMEngine()
enhanced_advisor = EnhancedSmartAdvisor()

# Simple in-memory knowledge base
KNOWLEDGE_BASE = {
    "MI_TRACK": {
        "name": "Machine Intelligence Track",
        "required_courses": ["CS 37300", "CS 38100"],
        "choice_courses": {
            "ai_requirement": ["CS 47100", "CS 47300"],
            "stats_requirement": ["STAT 41600", "MA 41600", "STAT 51200"]
        },
        "electives": [
            "CS 31100", "CS 41100", "CS 31400", "CS 34800", "CS 35200",
            "CS 44800", "CS 45600", "CS 45800", "CS 48300", "CS 43900",
            "CS 44000", "CS 47500", "CS 57700", "CS 57800"
        ]
    },
    "SE_TRACK": {
        "name": "Software Engineering Track",
        "required_courses": ["CS 30700", "CS 38100", "CS 40800", "CS 40700"],
        "choice_courses": {
            "compilers_os": ["CS 35200", "CS 35400"]
        },
        "electives": [
            "CS 31100", "CS 41100", "CS 34800", "CS 35100", "CS 35200",
            "CS 35300", "CS 35400", "CS 37300", "CS 42200", "CS 42600",
            "CS 44800", "CS 45600", "CS 47100", "CS 47300", "CS 48900",
            "CS 49000-DSO", "CS 49000-SWS", "CS 51000", "CS 59000-SRS"
        ]
    }
}

@app.route('/')
def dashboard():
    """Simple dashboard"""
    return f"""
    <h1>🎓 Purdue CS AI Assistant</h1>
    <p>Enhanced Boiler AI with Knowledge Graph</p>
    <h2>System Status: ✅ Online</h2>
    <p>API Endpoints:</p>
    <ul>
        <li><a href="/api/status">Status</a></li>
        <li><a href="/api/tracks">Tracks</a></li>
    </ul>
    <h3>Test Query:</h3>
    <form method="POST" action="/api/chat">
        <input type="text" name="query" placeholder="Ask about CS tracks..." style="width: 300px;">
        <button type="submit">Ask</button>
    </form>
    """

@app.route('/api/status')
def status():
    """System status with AI provider info"""
    return jsonify({
        "status": "healthy",
        "tracks": list(KNOWLEDGE_BASE.keys()),
        "total_courses": {
            "MI": len(KNOWLEDGE_BASE["MI_TRACK"]["required_courses"]) + len(KNOWLEDGE_BASE["MI_TRACK"]["electives"]),
            "SE": len(KNOWLEDGE_BASE["SE_TRACK"]["required_courses"]) + len(KNOWLEDGE_BASE["SE_TRACK"]["electives"])
        },
        "ai_providers": {
            "available": llm_engine.get_available_providers(),
            "active": llm_engine.get_active_provider(),
            "status": llm_engine.get_provider_status()
        }
    })

@app.route('/api/tracks')
def tracks():
    """Get all tracks"""
    return jsonify(KNOWLEDGE_BASE)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint with friendly responses and multi-provider support"""
    try:
        data = request.get_json() if request.is_json else {"query": request.form.get("query", "")}
        query = data.get("query", "")
        preferred_provider = data.get("provider", None)
        thinking_mode = data.get("thinking", False)
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        # Detect course failure questions for specific answers
        if any(phrase in query.lower() for phrase in [
            'failed cs 180', 'failed cs 18000', 'retake cs 180', 'cs 180 failure',
            'failed a course', 'failing', 'will i graduate on time', 'failed 180',
            'more than 4 years', 'delayed graduation'
        ]):
            # Use enhanced smart advisor for specific course failure analysis
            result = enhanced_advisor.handle_academic_query(query, None, None)
            return jsonify({
                "response": result['response'],
                "source": result['source'], 
                "confidence": result.get('confidence', 0.95),
                "query_type": "course_failure_analysis"
            })
        
        # Check if this is a provider command
        if query.lower().startswith('provider '):
            provider_name = query[9:].strip().title()
            if llm_engine.set_provider(provider_name):
                return jsonify({
                    "response": f"Switched to {provider_name} provider!",
                    "provider": provider_name,
                    "command": True
                })
            else:
                return jsonify({
                    "response": f"Provider {provider_name} not available. Available: {', '.join(llm_engine.get_available_providers())}",
                    "provider": None,
                    "command": True
                })
        
        if query.lower() == 'providers':
            return jsonify({
                "response": "Provider Status",
                "provider_status": llm_engine.get_provider_status(),
                "recommendations": llm_engine.get_provider_recommendations(),
                "command": True
            })
        
        # Generate friendly response with AI provider if available
        available_providers = llm_engine.get_available_providers()
        if available_providers:
            if thinking_mode:
                # Use thinking mode for enhanced reasoning
                from thinking_advisor import ThinkingAIAdvisor
                thinking_advisor = ThinkingAIAdvisor(None, llm_engine)
                
                # Process with thinking (but without visual animation for API)
                thinking_advisor.thinking_indicator.thinking = False  # Disable animation for API
                result = thinking_advisor.process_query_with_thinking(query, None)
                
                return jsonify({
                    "response": result["response"],
                    "provider": result.get("provider", preferred_provider),
                    "confidence": result["confidence"],
                    "ai_enhanced": True,
                    "thinking_mode": True,
                    "thinking_process": result.get("thinking_process", {})
                })
            else:
                # Use Smart AI Engine for intelligent responses instead of templates
                from smart_ai_engine import SmartAIEngine
                
                # Initialize smart AI engine
                smart_ai = SmartAIEngine(None)
                
                # Generate intelligent response using Gemini API
                response_data = smart_ai.generate_intelligent_response(query, None)
                
                return jsonify({
                    "response": response_data["response"],
                    "provider": response_data.get("provider", "smart_ai_engine"),
                    "confidence": response_data["confidence"],
                    "ai_enhanced": True,
                    "thinking_mode": False,
                    "intent": response_data.get("intent", "unknown"),
                    "source": "smart_ai_engine"
                })
        else:
            # No AI providers available, use dynamic query processor
            from dynamic_query_processor import DynamicQueryProcessor
            from friendly_response_generator import FriendlyStudentAdvisor
            
            dynamic_processor = DynamicQueryProcessor(None)
            response_data = dynamic_processor.process_query_intelligently(query, None)
            
            advisor = FriendlyStudentAdvisor(None)
            final_response = advisor._apply_friendly_formatting(response_data)
            
            return jsonify({
                "response": final_response["response"],
                "provider": "dynamic_processor",
                "confidence": final_response["confidence"],
                "ai_enhanced": False,
                "thinking_mode": False,
                "intent": final_response.get("intent", "unknown"),
                "source": "dynamic_query_processing"
            })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/providers', methods=['GET'])
def get_providers():
    """Get AI provider information"""
    return jsonify({
        "available": llm_engine.get_available_providers(),
        "active": llm_engine.get_active_provider(),
        "status": llm_engine.get_provider_status(),
        "recommendations": llm_engine.get_provider_recommendations()
    })

@app.route('/api/providers/<provider_name>', methods=['POST'])
def set_provider(provider_name):
    """Set active AI provider"""
    if llm_engine.set_provider(provider_name):
        return jsonify({
            "success": True,
            "message": f"Switched to {provider_name} provider",
            "active_provider": provider_name
        })
    else:
        return jsonify({
            "success": False,
            "message": f"Provider {provider_name} not available",
            "available_providers": llm_engine.get_available_providers()
        }), 400

def generate_friendly_response(query):
    """Generate friendly, encouraging responses using AI - no hardcoded templates"""
    # Use AI to generate natural, contextual responses instead of templates
    try:
        from simple_boiler_ai import SimpleBoilerAI
        ai_engine = SimpleBoilerAI()
        
        # Generate AI-powered greeting and response
        response_prompt = f"""
        A student asked: "{query}"
        
        Generate a friendly, encouraging response that:
        1. Acknowledges their question naturally
        2. Provides helpful information about their topic
        3. Uses a warm, supportive tone
        4. Avoids markdown formatting
        5. Focuses on their academic success
        
        Be conversational and genuine, not robotic.
        """
        
        return ai_engine.get_ai_response(response_prompt)
        
    except Exception as e:
        # Emergency fallback - minimal AI response
        try:
            import google.generativeai as genai
            import os
            
            if os.environ.get("GEMINI_API_KEY"):
                client = Gemini.Gemini(api_key=os.environ.get("GEMINI_API_KEY"))
                response = client.generate_content(
                    ,
                    messages=[
                        {"role": "system", "content": "You are a helpful Purdue CS advisor. Be brief and friendly."},
                        {"role": "user", "content": f"A student asked: '{query}'. Provide a brief, helpful response."}
                    ],
                    ,
                    
                )
                return response.text.strip()
        except Exception:
            # Return empty instead of hardcoded fallback
            return ""

if __name__ == "__main__":
    print("🚀 Starting Simplified Purdue CS AI Assistant...")
    print("📊 Dashboard: http://0.0.0.0:5000")
    print("🔗 API: http://0.0.0.0:5000/api/chat")
    app.run(host="0.0.0.0", port=5000, debug=True)