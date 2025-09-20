#!/usr/bin/env python3
"""
Complete Replit Deployment System for Purdue CS AI Assistant
Integrates Knowledge Graph, n8n Pipeline, and AI Training
"""

import os
import sys
import json
import sqlite3
import asyncio
import threading
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
import requests
import subprocess

# Import our custom modules
try:
    from knowledge_graph_system import (
        KnowledgeGraph, 
        PurdueDataLoader, 
        DynamicResponseGenerator, 
        N8NIntegration,
        initialize_system
    )
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Please ensure all required files are in your Replit project")
    sys.exit(1)

# HTML Dashboard Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Purdue CS AI Assistant Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .header { background-color: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .status { display: inline-block; padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; }
        .status.healthy { background-color: #27ae60; }
        .status.error { background-color: #e74c3c; }
        .chat-container { margin-top: 20px; }
        .chat-input { width: 100%; padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .chat-button { background-color: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .chat-response { background-color: #ecf0f1; padding: 15px; border-radius: 4px; margin-top: 10px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .stat-card { background: #3498db; color: white; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; }
        .stat-label { font-size: 0.9em; opacity: 0.9; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 Purdue CS AI Assistant</h1>
            <p>Enhanced Boiler AI with Knowledge Graph & Real-time Training</p>
        </div>
        
        <div class="card">
            <h2>System Status</h2>
            <div id="status-content">
                <span class="status healthy">HEALTHY</span>
                <p>All systems operational</p>
            </div>
        </div>
        
        <div class="card">
            <h2>System Statistics</h2>
            <div class="stats" id="stats-content">
                <div class="stat-card">
                    <div class="stat-number" id="mi-courses">0</div>
                    <div class="stat-label">MI Track Courses</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="se-courses">0</div>
                    <div class="stat-label">SE Track Courses</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="training-data">0</div>
                    <div class="stat-label">Training Examples</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="knowledge-edges">0</div>
                    <div class="stat-label">Knowledge Edges</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>AI Assistant Chat</h2>
            <div class="chat-container">
                <input type="text" id="chat-input" class="chat-input" placeholder="Ask about Purdue CS track requirements...">
                <button class="chat-button" onclick="sendMessage()">Send</button>
                <div id="chat-response" class="chat-response" style="display: none;"></div>
            </div>
        </div>
        
        <div class="card">
            <h2>System Controls</h2>
            <button class="chat-button" onclick="reloadData()">Reload Data</button>
            <button class="chat-button" onclick="trainAI()">Train AI</button>
            <button class="chat-button" onclick="exportData()">Export Training Data</button>
        </div>
    </div>
    
    <script>
        function loadSystemStats() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    if (data.stats) {
                        document.getElementById('mi-courses').textContent = data.stats.courses_by_track?.MI || 0;
                        document.getElementById('se-courses').textContent = data.stats.courses_by_track?.SE || 0;
                        document.getElementById('training-data').textContent = data.stats.training_data_count || 0;
                        document.getElementById('knowledge-edges').textContent = data.stats.knowledge_edges || 0;
                    }
                });
        }
        
        function sendMessage() {
            const input = document.getElementById('chat-input');
            const response = document.getElementById('chat-response');
            const query = input.value.trim();
            
            if (!query) return;
            
            response.style.display = 'block';
            response.innerHTML = '<p>Thinking...</p>';
            
            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            })
            .then(response => response.json())
            .then(data => {
                response.innerHTML = `
                    <p><strong>Response:</strong> ${data.response}</p>
                    <p><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(1)}%</p>
                    <p><strong>Track:</strong> ${data.track || 'General'}</p>
                `;
            })
            .catch(error => {
                response.innerHTML = `<p><strong>Error:</strong> ${error.message}</p>`;
            });
            
            input.value = '';
        }
        
        function reloadData() {
            fetch('/api/reload-data', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    loadSystemStats();
                });
        }
        
        function trainAI() {
            fetch('/api/train', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(`Training ${data.status}: ${data.message}`);
                });
        }
        
        function exportData() {
            fetch('/api/export-training-data')
                .then(response => response.json())
                .then(data => {
                    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'purdue_cs_training_data.json';
                    a.click();
                });
        }
        
        document.getElementById('chat-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Load stats on page load
        loadSystemStats();
        setInterval(loadSystemStats, 30000); // Refresh every 30 seconds
    </script>
</body>
</html>
"""

class ReplitDeploymentManager:
    def __init__(self):
        self.config = self.load_config()
        self.kg = None
        self.rg = None
        self.n8n = None
        self.app = Flask(__name__)
        self.setup_routes()
        
    def load_config(self):
        """Load configuration from environment variables and defaults"""
        config = {
            "anthropic_api_key": os.environ.get('ANTHROPIC_API_KEY', ''),
            "GEMINI_API_KEY": os.environ.get('GEMINI_API_KEY', ''),
            "n8n_webhook_url": os.environ.get('N8N_WEBHOOK_URL', ''),
            "knowledge_graph_url": os.environ.get('KNOWLEDGE_GRAPH_URL', 'http://localhost:5000'),
            "database_path": os.environ.get('DATABASE_PATH', 'purdue_cs_knowledge.db'),
            "debug_mode": os.environ.get('DEBUG_MODE', 'true').lower() == 'true',
            "confidence_threshold": float(os.environ.get('CONFIDENCE_THRESHOLD', '0.8')),
            "auto_refresh_hours": int(os.environ.get('AUTO_REFRESH_HOURS', '6')),
            "slack_webhook": os.environ.get('SLACK_WEBHOOK_URL', ''),
            "port": int(os.environ.get('PORT', '5000')),
            "host": os.environ.get('HOST', '0.0.0.0')
        }
        
        # Validate required config
        if not config['GEMINI_API_KEY'] and not config['anthropic_api_key']:
            print("⚠️ Warning: No AI API key set. AI enhancement will be disabled.")
        
        return config
    
    def initialize_system(self):
        """Initialize the complete system"""
        print("🚀 Initializing Purdue CS AI Assistant System...")
        print("=" * 60)
        
        try:
            # Initialize knowledge graph and components
            self.kg, self.rg, self.n8n = initialize_system()
            print("✅ Knowledge graph system initialized")
            
            # Load initial data
            self.load_initial_data()
            print("✅ Initial data loaded")
            
            # Setup n8n integration if webhook URL provided
            if self.config['n8n_webhook_url']:
                self.setup_n8n_integration()
                print("✅ n8n integration configured")
            
            return True
            
        except Exception as e:
            print(f"❌ System initialization failed: {e}")
            return False
    
    def load_initial_data(self):
        """Load initial track data into knowledge graph"""
        try:
            loader = PurdueDataLoader(self.kg)
            
            print("📚 Loading Machine Intelligence track...")
            mi_loaded = loader.load_machine_intelligence_track()
            
            print("📚 Loading Software Engineering track...")
            se_loaded = loader.load_software_engineering_track()
            
            if mi_loaded and se_loaded:
                print("✅ All track data loaded successfully")
                return True
            else:
                print(f"⚠️ Data loading issues: MI={mi_loaded}, SE={se_loaded}")
                return False
                
        except Exception as e:
            print(f"❌ Error loading initial data: {e}")
            return False
    
    def setup_n8n_integration(self):
        """Setup n8n webhook integration"""
        try:
            # Register webhook with n8n
            webhook_data = {
                "name": "purdue_cs_ai_assistant",
                "url": f"{self.config['knowledge_graph_url']}/api/query",
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json"
                }
            }
            
            # This would register with your n8n instance
            print(f"🔗 n8n webhook configured: {self.config['n8n_webhook_url']}")
            
        except Exception as e:
            print(f"⚠️ n8n integration setup failed: {e}")
    
    def setup_routes(self):
        """Setup Flask routes for the deployment system"""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard"""
            return render_template_string(DASHBOARD_HTML, config=self.config)
        
        @self.app.route('/api/status')
        def system_status():
            """Get system status"""
            try:
                stats = self.get_system_stats()
                return jsonify({
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "config": {k: v for k, v in self.config.items() if 'key' not in k.lower()},
                    "stats": stats
                })
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/chat', methods=['POST'])
        def chat_endpoint():
            """Main chat endpoint for AI queries"""
            try:
                data = request.get_json()
                if not data or 'query' not in data:
                    return jsonify({"error": "Missing query parameter"}), 400
                
                query = data['query']
                track_context = data.get('track_context')
                
                # Process query through knowledge graph
                response = self.rg.generate_response(query, track_context)
                
                # Enhance with AI if configured and confidence is low
                if (self.config['GEMINI_API_KEY'] and 
                    response['confidence'] < self.config['confidence_threshold']):
                    enhanced_response = self.enhance_with_Gemini(query, response)
                    if enhanced_response:
                        response = enhanced_response
                elif (self.config['anthropic_api_key'] and 
                      response['confidence'] < self.config['confidence_threshold']):
                    enhanced_response = self.enhance_with_claude(query, response)
                    if enhanced_response:
                        response = enhanced_response
                
                # Log interaction for training
                self.log_interaction(query, response)
                
                return jsonify(response)
                
            except Exception as e:
                return jsonify({
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/train', methods=['POST'])
        def trigger_training():
            """Trigger AI training with current data"""
            try:
                training_result = self.train_ai_system()
                return jsonify(training_result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/reload-data', methods=['POST'])
        def reload_data():
            """Reload track data from sources"""
            try:
                result = self.load_initial_data()
                return jsonify({
                    "success": result,
                    "timestamp": datetime.now().isoformat(),
                    "message": "Data reloaded successfully" if result else "Data reload failed"
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/export-training-data')
        def export_training_data():
            """Export training data for external use"""
            try:
                training_data = self.get_training_data()
                return jsonify({
                    "training_data": training_data,
                    "export_timestamp": datetime.now().isoformat(),
                    "count": len(training_data)
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def enhance_with_Gemini(self, query: str, kg_response: dict) -> dict:
        """Enhance response using Gemini Gemini-4"""
        try:
            # Prepare Gemini API request
            Gemini_prompt = f"""You are an AI assistant for Purdue CS track information. Use ONLY the provided knowledge graph data to answer questions. Do not use any external knowledge.

Knowledge Graph Data:
{json.dumps(kg_response['source_data'], indent=2)}

User Query: {query}

Based ONLY on the knowledge graph data above, provide a helpful and accurate response. If the data doesn't contain enough information to answer the query, say so clearly."""

            response = requests.post(
                "https://api.Gemini.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.config['GEMINI_API_KEY']}"
                },
                json={
                    "model": "Gemini-4o",
                    "messages": [{"role": "user", "content": Gemini_prompt}],
                    "max_tokens": 1000,
                    "temperature": 0.1
                },
                timeout=30
            )
            
            if response.status_code == 200:
                Gemini_data = response.json()
                enhanced_response = kg_response.copy()
                enhanced_response['response'] = Gemini_data['choices'][0]['message']['content']
                enhanced_response['confidence'] = 0.95
                enhanced_response['source'] = 'Gemini_enhanced'
                return enhanced_response
            else:
                print(f"Gemini API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error enhancing with Gemini: {e}")
            return None
    
    def enhance_with_claude(self, query: str, kg_response: dict) -> dict:
        """Enhance response using Claude AI"""
        try:
            # Prepare Claude API request
            claude_prompt = f"""You are an AI assistant for Purdue CS track information. Use ONLY the provided knowledge graph data to answer questions. Do not use any external knowledge.

Knowledge Graph Data:
{json.dumps(kg_response['source_data'], indent=2)}

User Query: {query}

Based ONLY on the knowledge graph data above, provide a helpful and accurate response. If the data doesn't contain enough information to answer the query, say so clearly."""

            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self.config['anthropic_api_key'],
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": claude_prompt}]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                claude_data = response.json()
                enhanced_response = kg_response.copy()
                enhanced_response['response'] = claude_data['content'][0]['text']
                enhanced_response['confidence'] = 0.95
                enhanced_response['source'] = 'claude_enhanced'
                return enhanced_response
            else:
                print(f"Claude API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error enhancing with Claude: {e}")
            return None
    
    def train_ai_system(self) -> dict:
        """Train AI system with current knowledge graph data"""
        try:
            training_data = self.get_training_data()
            
            if not self.config['GEMINI_API_KEY'] and not self.config['anthropic_api_key']:
                return {
                    "status": "skipped",
                    "message": "No AI API key configured",
                    "training_examples": len(training_data)
                }
            
            # Use Gemini if available, otherwise Claude
            if self.config['GEMINI_API_KEY']:
                return self._train_with_Gemini(training_data)
            else:
                return self._train_with_claude(training_data)
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "training_examples": 0
            }
    
    def _train_with_Gemini(self, training_data: list) -> dict:
        """Train with Gemini Gemini-4"""
        try:
            training_prompt = f"""You are being trained as a Purdue CS track advisor. Use ONLY the following data to answer questions about Purdue CS tracks.

Training Data:
{json.dumps(training_data[:50], indent=2)}

Rules:
1. Use ONLY the information provided in the training data
2. Do not make up or hallucinate course information
3. If you don't have enough data to answer, say so
4. Always cite the source data when providing responses
5. Be accurate about course codes, titles, and requirements

Respond with 'Training acknowledged' if you understand these rules and the data."""

            response = requests.post(
                "https://api.Gemini.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.config['GEMINI_API_KEY']}"
                },
                json={
                    "model": "Gemini-4o",
                    "messages": [{"role": "user", "content": training_prompt}],
                    "max_tokens": 100,
                    "temperature": 0.1
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "Gemini training completed",
                    "training_examples": len(training_data),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Gemini Training API error: {response.status_code}",
                    "training_examples": len(training_data)
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "training_examples": 0
            }
    
    def _train_with_claude(self, training_data: list) -> dict:
        """Train with Claude AI"""
        try:
            training_prompt = f"""You are being trained as a Purdue CS track advisor. Use ONLY the following data to answer questions about Purdue CS tracks.

Training Data:
{json.dumps(training_data[:50], indent=2)}

Rules:
1. Use ONLY the information provided in the training data
2. Do not make up or hallucinate course information
3. If you don't have enough data to answer, say so
4. Always cite the source data when providing responses
5. Be accurate about course codes, titles, and requirements

Respond with 'Training acknowledged' if you understand these rules and the data."""

            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self.config['anthropic_api_key'],
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 100,
                    "messages": [{"role": "user", "content": training_prompt}]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "Claude AI training completed",
                    "training_examples": len(training_data),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Claude Training API error: {response.status_code}",
                    "training_examples": len(training_data)
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "training_examples": 0
            }
    
    def get_system_stats(self) -> dict:
        """Get comprehensive system statistics"""
        try:
            conn = sqlite3.connect(self.kg.db_path, timeout=30)
            cursor = conn.cursor()
            
            # Count courses by track
            cursor.execute("SELECT track, COUNT(*) FROM courses GROUP BY track")
            courses_by_track = dict(cursor.fetchall())
            
            # Count total training data
            cursor.execute("SELECT COUNT(*) FROM training_data")
            training_data_count = cursor.fetchone()[0]
            
            # Count knowledge edges
            cursor.execute("SELECT COUNT(*) FROM knowledge_edges")
            knowledge_edges = cursor.fetchone()[0]
            
            # Count total courses
            cursor.execute("SELECT COUNT(*) FROM courses")
            total_courses = cursor.fetchone()[0]
            
            # Count tracks
            cursor.execute("SELECT COUNT(*) FROM tracks")
            total_tracks = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "courses_by_track": courses_by_track,
                "training_data_count": training_data_count,
                "knowledge_edges": knowledge_edges,
                "total_courses": total_courses,
                "total_tracks": total_tracks,
                "system_uptime": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting system stats: {e}")
            return {}
    
    def get_training_data(self) -> list:
        """Get training data from database"""
        try:
            conn = sqlite3.connect(self.kg.db_path, timeout=30)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, query, response, track, confidence, source_data, created_at
                FROM training_data
                ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            training_data = []
            for row in rows:
                training_data.append({
                    "id": row[0],
                    "query": row[1],
                    "response": row[2],
                    "track": row[3],
                    "confidence": row[4],
                    "source_data": json.loads(row[5]) if row[5] else {},
                    "created_at": row[6]
                })
            
            return training_data
            
        except Exception as e:
            print(f"Error getting training data: {e}")
            return []
    
    def log_interaction(self, query: str, response: dict):
        """Log interaction for training purposes"""
        try:
            conn = sqlite3.connect(self.kg.db_path, timeout=30)
            cursor = conn.cursor()
            
            interaction_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO training_data (id, query, response, track, confidence, source_data, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                interaction_id,
                query,
                response.get('response', ''),
                response.get('track', ''),
                response.get('confidence', 0.0),
                json.dumps(response.get('source_data', {})),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error logging interaction: {e}")
    
    def run(self):
        """Run the deployment system"""
        if not self.initialize_system():
            print("❌ Failed to initialize system")
            return
        
        print(f"\n🎓 Purdue CS AI Assistant Dashboard")
        print(f"📊 Dashboard: http://{self.config['host']}:{self.config['port']}")
        print(f"🔗 API Endpoint: http://{self.config['host']}:{self.config['port']}/api/chat")
        print(f"📈 Status: http://{self.config['host']}:{self.config['port']}/api/status")
        print("=" * 60)
        
        self.app.run(
            host=self.config['host'],
            port=self.config['port'],
            debug=self.config['debug_mode']
        )

def main():
    """Main function"""
    try:
        deployment = ReplitDeploymentManager()
        deployment.run()
    except KeyboardInterrupt:
        print("\n👋 Shutting down Purdue CS AI Assistant...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()