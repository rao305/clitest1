#!/usr/bin/env python3
"""
BoilerAI Complete System Startup
================================

This script starts the entire BoilerAI system:
1. Prompts for API key
2. Starts CLI server with API key
3. Starts frontend
4. Provides system status

Usage:
    python start_boilerai_system.py
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path

class BoilerAISystemStarter:
    """Complete BoilerAI system starter"""
    
    def __init__(self):
        self.cli_process = None
        self.frontend_process = None
        self.api_key = None
        self.provider = None
        
        # Paths
        self.frontend_path = Path(r"C:\Users\raoro\OneDrive\Desktop\bfrontend-main")
        self.cli_path = Path(r"C:\Users\raoro\OneDrive\Desktop\clitest1-main\my_cli_bot")
        
    def print_banner(self):
        """Print startup banner"""
        print("=" * 60)
        print("BoilerAI Complete System Startup")
        print("=" * 60)
        print("This will start:")
        print("1. CLI Server (with API key)")
        print("2. Frontend (React app)")
        print("3. Open browser to AI Assistant")
        print("=" * 60)
        print()
    
    def setup_api_key(self):
        """Setup API key interactively"""
        print("API Key Setup")
        print("-" * 20)
        print("Choose your AI provider:")
        print("1. Gemini (Google) - Free tier available")
        print("2. OpenAI - Paid service")
        print()
        
        while True:
            choice = input("Select provider (1/2): ").strip()
            if choice == "1":
                self.provider = "gemini"
                print("\nGemini API Key Setup:")
                print("1. Go to: https://makersuite.google.com/app/apikey")
                print("2. Create a new API key")
                print("3. Copy the key (starts with 'AIzaSy')")
                break
            elif choice == "2":
                self.provider = "openai"
                print("\nOpenAI API Key Setup:")
                print("1. Go to: https://platform.openai.com/api-keys")
                print("2. Create a new API key")
                print("3. Copy the key (starts with 'sk-')")
                break
            else:
                print("[ERROR] Invalid choice. Please select 1 or 2.")
        
        print()
        while True:
            self.api_key = input(f"Enter your {self.provider.upper()} API key: ").strip()
            if self.api_key:
                # Validate format
                if self.provider == "gemini" and not self.api_key.startswith("AIzaSy"):
                    print("[WARNING] Gemini API key should start with 'AIzaSy'")
                elif self.provider == "openai" and not self.api_key.startswith("sk-"):
                    print("[WARNING] OpenAI API key should start with 'sk-'")
                break
            print("[ERROR] API key cannot be empty.")
        
        print(f"[OK] API key set: {self.api_key[:10]}...")
        return True
    
    def start_cli_server(self):
        """Start CLI server with API key"""
        print("\n[INFO] Starting CLI Server...")
        print("-" * 30)
        
        try:
            # Change to frontend directory
            os.chdir(self.frontend_path)
            
            # Create CLI server script with API key
            cli_script = f'''
import sys
import os
sys.path.insert(0, r"{self.cli_path}")

from simple_boiler_ai import SimpleBoilerAI
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading

class CLIServer:
    def __init__(self):
        self.api_key = "{self.api_key}"
        self.provider = "{self.provider}"
        self.cli_agent = SimpleBoilerAI(api_key=self.api_key)
        self.initialized = True
        
    def process_query(self, query):
        try:
            result = self.cli_agent.process_query(query)
            return {{
                "success": True,
                "response": result.get("response", str(result)),
                "thinking": result.get("thinking", ""),
                "sources": result.get("sources", []),
                "confidence": result.get("confidence", 0.8),
                "provider": self.provider
            }}
        except Exception as e:
            return {{
                "success": False,
                "error": str(e),
                "response": f"CLI processing error: {{str(e)}}",
                "provider": self.provider
            }}

class CLIRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/query':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                query = data.get('query', '')
                
                result = cli_server.process_query(query)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                
                response = json.dumps(result)
                self.wfile.write(response.encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = json.dumps({{"error": str(e)}})
                self.wfile.write(error_response.encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass

cli_server = CLIServer()
server_address = ('localhost', 8001)
httpd = HTTPServer(server_address, CLIRequestHandler)

print("CLI Server Started!")
print(f"Server running on: http://localhost:8001")
print(f"Provider: {self.provider}")
print("Ready to serve AI requests!")

httpd.serve_forever()
'''
            
            # Write and run CLI server script
            with open("temp_cli_server.py", "w") as f:
                f.write(cli_script)
            
            # Start CLI server
            self.cli_process = subprocess.Popen([
                sys.executable, "temp_cli_server.py"
            ], cwd=self.frontend_path)
            
            # Wait for server to start
            time.sleep(3)
            
            print("[OK] CLI Server started on port 8001")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to start CLI server: {e}")
            return False
    
    def start_frontend(self):
        """Start frontend development server"""
        print("\n[INFO] Starting Frontend...")
        print("-" * 25)
        
        try:
            # Start frontend
            self.frontend_process = subprocess.Popen([
                "npm", "run", "dev"
            ], cwd=self.frontend_path)
            
            # Wait for frontend to start
            time.sleep(5)
            
            print("[OK] Frontend started on port 3001")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to start frontend: {e}")
            return False
    
    def open_browser(self):
        """Open browser to AI Assistant"""
        print("\n[INFO] Opening Browser...")
        print("-" * 25)
        
        try:
            # Wait a bit more for frontend to be ready
            time.sleep(3)
            
            # Open browser to AI Assistant
            webbrowser.open("http://localhost:3001")
            print("[OK] Browser opened to AI Assistant")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to open browser: {e}")
            return False
    
    def show_system_status(self):
        """Show system status and instructions"""
        print("\n" + "=" * 60)
        print("[SUCCESS] BoilerAI System Started Successfully!")
        print("=" * 60)
        print(f"[INFO] API Key: {self.api_key[:10]}... ({self.provider})")
        print("[INFO] CLI Server: http://localhost:8001")
        print("[INFO] Frontend: http://localhost:3001")
        print("=" * 60)
        print()
        print("How to Use:")
        print("1. Go to http://localhost:3001")
        print("2. Login with Microsoft or development bypass")
        print("3. Click 'AI Assistant' in navigation")
        print("4. Ask questions like:")
        print("   • 'What are the CS core requirements?'")
        print("   • 'How do I plan my CS degree?'")
        print("   • 'What courses should I take next semester?'")
        print()
        print("To Stop System:")
        print("   Press Ctrl+C in this terminal")
        print("=" * 60)
    
    def cleanup(self):
        """Cleanup processes and temp files"""
        print("\n[INFO] Cleaning up...")
        
        if self.cli_process:
            self.cli_process.terminate()
            print("[OK] CLI Server stopped")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            print("[OK] Frontend stopped")
        
        # Remove temp file
        temp_file = self.frontend_path / "temp_cli_server.py"
        if temp_file.exists():
            temp_file.unlink()
            print("[OK] Temp files cleaned")
    
    def start_system(self):
        """Start the complete BoilerAI system"""
        try:
            self.print_banner()
            
            # Setup API key
            if not self.setup_api_key():
                return False
            
            # Start CLI server
            if not self.start_cli_server():
                return False
            
            # Start frontend
            if not self.start_frontend():
                return False
            
            # Open browser
            self.open_browser()
            
            # Show status
            self.show_system_status()
            
            # Keep running until user stops
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n[INFO] Stopping BoilerAI System...")
                self.cleanup()
                print("[INFO] BoilerAI System stopped. Goodbye!")
                
        except Exception as e:
            print(f"[ERROR] System error: {e}")
            self.cleanup()
            return False

def main():
    """Main function"""
    starter = BoilerAISystemStarter()
    starter.start_system()

if __name__ == "__main__":
    main()
