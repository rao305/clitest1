#!/bin/bash
"""
BoilerAI Complete - Startup Script
"""

echo "🚀 Starting BoilerAI Complete System..."
echo "Setting up environment..."

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install requests beautifulsoup4 PyPDF2 openai networkx
else
    source venv/bin/activate
fi

# Set API key
export OPENAI_API_KEY="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"

echo "✅ Environment ready!"
echo ""

# Start BoilerAI
python boiler_ai_complete.py