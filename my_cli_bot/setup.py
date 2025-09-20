#!/usr/bin/env python3
"""
Setup script for Purdue CS AI Assistant
"""

import os
import subprocess
import sys

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("📝 Creating .env file...")
        env_content = """# Copy this to .env and fill in your values

# Required: Gemini API Key for Gemini-4 enhancement
GEMINI_API_KEY=your_GEMINI_API_KEY_here

# Optional: Anthropic API Key for Claude AI
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: n8n Integration
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/purdue-cs

# Optional: Slack Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# System Configuration
DEBUG_MODE=true
CONFIDENCE_THRESHOLD=0.8
AUTO_REFRESH_HOURS=6
PORT=5000
HOST=0.0.0.0

# Database
DATABASE_PATH=purdue_cs_knowledge.db
"""
        with open('.env', 'w') as env_file:
            env_file.write(env_content)
        print("✅ .env file created. Please edit it with your API keys.")
    else:
        print("ℹ️ .env file already exists")

def setup_database():
    """Initialize the database"""
    print("🗄️ Setting up database...")
    try:
        from knowledge_graph_system import KnowledgeGraph
        kg = KnowledgeGraph()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def main():
    """Main setup function"""
    print("🎓 Purdue CS AI Assistant Setup")
    print("=" * 40)
    
    steps = [
        ("Installing requirements", install_requirements),
        ("Creating environment file", create_env_file),
        ("Setting up database", setup_database)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            sys.exit(1)
    
    print("\n" + "=" * 40)
    print("✅ Setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: python main.py")
    print("3. Open http://localhost:5000 in your browser")
    print("4. Test the AI assistant!")

if __name__ == "__main__":
    main()