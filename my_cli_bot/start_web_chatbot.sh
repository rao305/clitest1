#!/bin/bash

# BoilerAI Web Chatbot Launcher
# Complete frontend integration for Purdue CS Academic Advisor

echo "🚀 BoilerAI Web Interface Launcher"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "chatbot_api.py" ]; then
    echo "❌ Error: Please run this script from the my_cli_bot directory"
    echo "💡 Usage: cd my_cli_bot && ./start_web_chatbot.sh"
    exit 1
fi

echo "🔧 Environment Setup Check..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo "✅ Python 3 found"

# Check API Keys
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set in environment"
    echo "💡 Please set it with: export OPENAI_API_KEY='your-key-here'"
    echo "🔑 Using key from environment variable if available..."
fi

if [ -z "$CLADO_API_KEY" ]; then
    echo "⚠️  CLADO_API_KEY not set (optional for career networking)"
    echo "💡 Set with: export CLADO_API_KEY='lk_26267cec2bcd4f34b9894bc07a00af1b'"
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "📥 Installing Flask..."
    pip3 install Flask
fi

if ! python3 -c "import flask_cors" &> /dev/null; then
    echo "📥 Installing Flask-CORS..."
    pip3 install Flask-CORS
fi

# Check if other dependencies exist
echo "🔍 Checking core chatbot modules..."
if [ ! -f "intelligent_conversation_manager.py" ]; then
    echo "❌ intelligent_conversation_manager.py not found"
    exit 1
fi

if [ ! -f "smart_ai_engine.py" ]; then
    echo "❌ smart_ai_engine.py not found"
    exit 1
fi

echo "✅ All dependencies and modules found"

# Create .env reminder
if [ ! -f ".env" ]; then
    echo "💡 Creating .env reminder file..."
    cat > .env << EOF
# Set your API keys here
# export OPENAI_API_KEY='your-openai-key-here'
# export CLADO_API_KEY='lk_26267cec2bcd4f34b9894bc07a00af1b'

# Then source this file: source .env
EOF
fi

echo ""
echo "🌐 Starting BoilerAI Web Interface..."
echo "🔗 Access URL: http://localhost:5000"
echo "📱 Open in your browser after startup completes"
echo ""
echo "🛑 To stop the server: Press Ctrl+C"
echo "📊 Health check: http://localhost:5000/api/health"
echo ""

# Set API keys if provided as arguments
if [ "$1" ]; then
    export OPENAI_API_KEY="$1"
    echo "🔑 OpenAI API key set from argument"
fi

if [ "$2" ]; then
    export CLADO_API_KEY="$2"
    echo "🔑 Clado API key set from argument"
fi

# Launch the web server
python3 chatbot_api.py