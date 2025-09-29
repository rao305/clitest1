# BoilerAI Complete Integration Guide

## Overview
This guide helps you integrate your CLI AI assistant with the BoilerAI frontend system. The CLI handles all AI processing, while the server acts as a simple bridge.

## System Architecture
```
User Query → Frontend (bfrontend-main) → Server Bridge → CLI AI Assistant → Response → Server → Frontend → User
```

## Required CLI Interface ✅ COMPLETED

Your CLI now implements the required interface:

### 1. Main Class Structure
```python
class SimpleBoilerAI:
    def __init__(self, api_key: str = None):
        # Prompts for API key if not provided
        pass
    
    def process_query(self, query: str) -> dict:
        """
        Process a query and return a standardized response
        
        Args:
            query (str): The user's question/query
            
        Returns:
            dict: Standardized response with these keys:
                - response (str): Main answer text
                - thinking (str): Reasoning process
                - sources (list): Source documents
                - confidence (float): Confidence score (0.0-1.0)
        """
        pass
```

### 2. Response Format ✅ IMPLEMENTED
Your `process_query` method returns:
```python
{
    "response": "Your main answer here",
    "thinking": "Your reasoning process",
    "sources": ["source1", "source2"],
    "confidence": 0.85
}
```

### 3. Error Handling ✅ IMPLEMENTED
Handles errors gracefully and returns a response even if processing fails:
```python
{
    "response": "I'm having trouble processing your request: [error]",
    "thinking": "Error occurred during processing",
    "sources": [],
    "confidence": 0.1
}
```

## Integration Steps

### Step 1: CLI Setup ✅ COMPLETED
Your CLI file (`my_cli_bot/simple_boiler_ai.py`) has been updated with:
- ✅ Required `process_query(query: str) -> dict` method
- ✅ System prompt for BoilerAI integration
- ✅ API key prompting (Gemini or OpenAI)
- ✅ Standardized response format
- ✅ Error handling

### Step 2: Test Your CLI Integration ✅ COMPLETED
Run the test script to verify your CLI works:
```bash
python test_cli_integration.py
```

### Step 3: Frontend Integration Setup

#### 3.1: Frontend Location
Your frontend is located at: `C:\Users\raoro\OneDrive\Desktop\bfrontend-main`

#### 3.2: Server Bridge Setup
The server bridge should be configured to:
1. Import your CLI: `from simple_boiler_ai import SimpleBoilerAI`
2. Initialize with API key: `cli = SimpleBoilerAI(api_key="your_api_key")`
3. Process queries: `result = cli.process_query(query)`
4. Return the response: `return result["response"]`

#### 3.3: API Key Management
- ✅ CLI prompts for API key on startup
- ✅ Supports both Gemini and OpenAI
- ✅ API key is handled in CLI only (not frontend)

### Step 4: Start the Complete System

#### 4.1: Start Backend Server
```bash
# In your main project directory
python -m uvicorn api_gateway.main:app --reload --port 8000
```

#### 4.2: Start Frontend
```bash
# In bfrontend-main directory
cd "C:\Users\raoro\OneDrive\Desktop\bfrontend-main"
npm run dev
```

#### 4.3: Test Integration
1. Open frontend in browser (usually `http://localhost:3000`)
2. Enter a test query: "What are the CS core requirements?"
3. Verify response comes from your CLI

## Testing Your Integration

### Test Script ✅ CREATED
The test script (`test_cli_integration.py`) verifies:
- ✅ CLI imports correctly
- ✅ `process_query` method exists
- ✅ Returns correct dictionary format
- ✅ All required keys present
- ✅ Error handling works

### Manual Testing
Test these queries in the frontend:
1. "What are the CS core requirements?"
2. "How do I plan my CS degree?"
3. "What courses should I take next semester?"
4. "What is CS 18000?"
5. "How do I CODO into CS?"

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure your CLI file is in the correct path
   - ✅ Path: `C:\Users\raoro\OneDrive\Desktop\clitest1-main\my_cli_bot\simple_boiler_ai.py`

2. **Method Not Found**: Ensure your CLI has `process_query(query: str) -> dict` method
   - ✅ Method implemented and tested

3. **Wrong Return Format**: Make sure you return a dictionary with required keys
   - ✅ Format verified in test script

4. **API Key Issues**: Set your API key in the CLI, not in the frontend
   - ✅ CLI prompts for API key on startup

### Debug Steps

1. ✅ Run the test script: `python test_cli_integration.py`
2. Check the server logs for CLI integration errors
3. ✅ Verify your CLI file path is correct
4. ✅ Ensure your CLI returns the correct format

## File Structure
```
C:\Users\raoro\OneDrive\Desktop\
├── clitest1-main\                    # Your CLI project
│   ├── my_cli_bot\
│   │   └── simple_boiler_ai.py       # ✅ Updated CLI with integration
│   └── test_cli_integration.py       # ✅ Test script
└── bfrontend-main\                   # Frontend project
    └── [frontend files]
```

## Next Steps

1. ✅ Update your CLI with the system prompt
2. ✅ Run the test script to verify integration
3. 🔄 Start the BoilerAI servers:
   - Backend: `python -m uvicorn api_gateway.main:app --reload --port 8000`
   - Frontend: `npm run dev` (in bfrontend-main directory)
4. 🔄 Test queries in the web interface

## Support

If you encounter issues:
1. ✅ Check the test script output
2. Review server logs
3. ✅ Verify CLI file format matches requirements
4. ✅ Ensure API key is set in CLI only

## API Key Management System ✅ IMPLEMENTED

### Secure API Key Storage
- ✅ No hardcoded API keys anywhere in the system
- ✅ API keys stored securely in `~/.boilerai/api_keys.json`
- ✅ Keys are prompted from user on first use
- ✅ Support for both Gemini and OpenAI providers
- ✅ API keys synchronized between CLI and frontend

### Usage Examples

#### CLI Usage:
```python
from simple_boiler_ai import SimpleBoilerAI
from api_key_manager import setup_api_key

# Option 1: Let CLI prompt for API key
cli = SimpleBoilerAI()  # Will prompt for provider and API key

# Option 2: Use existing API key
cli = SimpleBoilerAI(api_key="your-api-key-here")

# Option 3: Setup API key first
provider, api_key = setup_api_key()
cli = SimpleBoilerAI(api_key=api_key)
```

#### Server Bridge Usage:
```python
from boilerai_server_bridge import initialize_server, process_query

# Initialize server (will prompt for API key)
if initialize_server():
    result = process_query("What are the CS core requirements?")
    print(result["response"])
```

### Frontend Integration
The server bridge (`boilerai_server_bridge.py`) provides:
- ✅ API key synchronization between frontend and CLI
- ✅ Secure API key storage
- ✅ Provider selection (Gemini/OpenAI)
- ✅ Query processing through CLI

## Integration Status: ✅ COMPLETE

- ✅ CLI Interface: Implemented
- ✅ Response Format: Standardized
- ✅ Error Handling: Added
- ✅ API Key Management: Secure and synchronized
- ✅ Server Bridge: Created for frontend integration
- ✅ Test Script: Updated
- ✅ Documentation: Complete

Your CLI is now ready for BoilerAI frontend integration with secure API key management!
