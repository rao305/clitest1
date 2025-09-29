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

# API key will be prompted by the application
echo "API key will be prompted when starting the application"

echo "✅ Environment ready!"
echo ""

# Start BoilerAI
python boiler_ai_complete.py