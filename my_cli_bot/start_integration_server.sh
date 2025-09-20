#!/bin/bash

# BoilerAI Integration Server Launcher
# Simple setup for existing website integration

echo "🔌 BoilerAI Integration Server"
echo "============================="

# Check directory
if [ ! -f "simple_api_server.py" ]; then
    echo "❌ Please run from my_cli_bot directory"
    echo "💡 Usage: cd my_cli_bot && ./start_integration_server.sh"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 required"
    exit 1
fi

# Set API keys if provided as arguments
if [ "$1" ]; then
    export OPENAI_API_KEY="$1"
    echo "🔑 OpenAI API key set"
fi

if [ "$2" ]; then
    export CLADO_API_KEY="$2"
    echo "🔑 Clado API key set"
fi

# Check API keys
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not set"
    echo "💡 Usage: ./start_integration_server.sh YOUR_OPENAI_KEY [CLADO_KEY]"
    echo "💡 Or: export OPENAI_API_KEY='your-key' && ./start_integration_server.sh"
    exit 1
fi

# Install Flask if needed
if ! python3 -c "import flask" &> /dev/null; then
    echo "📦 Installing Flask..."
    pip3 install Flask Flask-CORS
fi

echo ""
echo "✅ All set! Starting BoilerAI Integration Server..."
echo ""
echo "🌐 API Server: http://localhost:3001"
echo "📡 Main endpoint: POST /api/chat"
echo "📚 Client library: http://localhost:3001/boilerai-client.js"
echo "🔍 Health check: http://localhost:3001/api/health"
echo ""
echo "📋 Quick integration for your website:"
echo "   <script src=\"http://localhost:3001/boilerai-client.js\"></script>"
echo "   <div id=\"boilerai\"></div>"
echo "   <script>const ai = new BoilerAI(); ai.createWidget('boilerai');</script>"
echo ""
echo "📖 Full guide: See INTEGRATION_GUIDE.md"
echo "🛑 Stop server: Press Ctrl+C"
echo ""

# Start server
python3 simple_api_server.py