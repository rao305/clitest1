#!/usr/bin/env python3
"""
BoilerAI Quick Start
====================

Simple script that starts the CLI server and frontend together.
Uses the existing cli_server.py from the frontend.

Usage:
    python quick_start.py
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def main():
    """Quick start the BoilerAI system"""
    print("BoilerAI Quick Start")
    print("=" * 40)
    print("This will:")
    print("1. Start CLI Server (asks for API key)")
    print("2. Start Frontend")
    print("3. Open browser")
    print("=" * 40)
    print()
    
    # Paths
    frontend_path = Path(r"C:\Users\raoro\OneDrive\Desktop\bfrontend-main")
    
    if not frontend_path.exists():
        print(f"[ERROR] Frontend directory not found: {frontend_path}")
        print("Please make sure bfrontend-main is in the correct location.")
        return
    
    try:
        # Change to frontend directory
        os.chdir(frontend_path)
        
        print("[INFO] Starting CLI Server...")
        print("Follow the prompts to enter your API key.")
        print()
        
        # Start CLI server (this will prompt for API key)
        cli_process = subprocess.Popen([
            sys.executable, "cli_server.py"
        ], cwd=frontend_path)
        
        # Wait for CLI server to start and user to enter API key
        print("[INFO] Waiting for CLI server setup...")
        print("Please complete the API key setup in the CLI server window.")
        print("Press Enter here when CLI server shows 'Ready to serve AI requests'")
        input()
        
        print("\n[INFO] Starting Frontend...")
        
        # Start frontend
        frontend_process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd=frontend_path)
        
        # Wait for frontend to start
        print("[INFO] Waiting for frontend to start...")
        time.sleep(5)
        
        print("\n[INFO] Opening Browser...")
        webbrowser.open("http://localhost:3001")
        
        print("\n" + "=" * 50)
        print("[SUCCESS] BoilerAI System Started!")
        print("=" * 50)
        print("[OK] CLI Server: http://localhost:8001")
        print("[OK] Frontend: http://localhost:3001")
        print("[OK] Browser: Opened to AI Assistant")
        print()
        print("Next Steps:")
        print("1. Complete login in browser")
        print("2. Go to AI Assistant")
        print("3. Ask questions!")
        print()
        print("Press Ctrl+C to stop both servers")
        print("=" * 50)
        
        # Keep running until user stops
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n[INFO] Stopping BoilerAI System...")
            cli_process.terminate()
            frontend_process.terminate()
            print("[OK] Both servers stopped")
            print("Goodbye!")
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        print("Make sure you have:")
        print("1. Python installed")
        print("2. Node.js and npm installed")
        print("3. Frontend dependencies installed (npm install)")

if __name__ == "__main__":
    main()
