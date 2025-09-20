#!/bin/bash
echo "🔑 Setting up OpenAI API Key for Boiler AI"
echo "=========================================="

# Check if API key is provided as argument
if [ -z "$1" ]; then
    echo "Usage: ./setup_api_key.sh YOUR_API_KEY"
    echo ""
    echo "Example:"
    echo "./setup_api_key.sh sk-proj-abcd1234..."
    echo ""
    echo "Or export it manually:"
    echo "export OPENAI_API_KEY='sk-proj-your-key-here'"
    exit 1
fi

# Set the API key
export OPENAI_API_KEY="$1"

# Verify it's set
echo "✅ API key set (length: ${#OPENAI_API_KEY} characters)"

# Test the system
echo ""
echo "🧪 Testing the AI system..."
python3 simple_boiler_ai.py << EOF
What is CS 18200?
quit
EOF