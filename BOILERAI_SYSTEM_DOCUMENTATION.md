# BoilerAI System Documentation
## Complete System Architecture & Integration Guide

### 🎯 **SYSTEM OVERVIEW**

**BoilerAI** is a comprehensive Purdue CS Academic Advisor system consisting of:
- **CLI AI Assistant** (`my_cli_bot/`) - Handles all AI processing
- **API Gateway** (`api_gateway/`) - Bridge between frontend and CLI
- **Frontend** (`bfrontend-main/`) - User interface (separate directory)

**Architecture Flow:**
```
User Query → Frontend (bfrontend-main) → API Gateway → CLI AI Assistant → Response → API Gateway → Frontend → User
```

---

### 📁 **FILE STRUCTURE**

```
C:\Users\raoro\OneDrive\Desktop\
├── clitest1-main\                           # Main CLI project
│   ├── my_cli_bot\                          # CLI AI Assistant
│   │   ├── simple_boiler_ai.py              # ✅ Main CLI class
│   │   ├── api_key_manager.py               # ✅ Secure API key management
│   │   ├── enhanced_chat.py                 # Enhanced chat system
│   │   ├── [200+ other files]               # Supporting modules
│   │   └── api\                            # Legacy API (not used)
│   ├── api_gateway\                         # ✅ API Gateway (NEW)
│   │   ├── main.py                         # FastAPI server
│   │   └── __init__.py                     # Package file
│   ├── boilerai_server_bridge.py            # ✅ Server bridge
│   ├── start_boilerai_system.py             # ✅ Complete system startup
│   ├── quick_start.py                       # ✅ Quick startup script
│   ├── setup_api_key.py                    # ✅ API key setup script
│   ├── test_cli_integration.py              # ✅ CLI test script
│   └── [documentation files]
└── bfrontend-main\                          # Frontend project (separate)
    └── [frontend files]
```

---

### 🔑 **API KEY MANAGEMENT SYSTEM**

**CRITICAL**: No hardcoded API keys anywhere in the system!

#### **API Key Storage**
- **Location**: `~/.boilerai/api_keys.json` (secure file)
- **Providers**: Gemini (free) and OpenAI (paid)
- **Validation**: Automatic format checking
- **Synchronization**: Shared between CLI and frontend

#### **How Users Enter API Keys**

**Method 1: API Gateway Setup (Recommended)**
```bash
# Run setup script
python setup_api_key.py

# Or use API directly
curl -X POST "http://127.0.0.1:8000/api/setup" \
     -H "Content-Type: application/json" \
     -d '{"provider": "gemini", "api_key": "your-api-key"}'
```

**Method 2: Browser Interface**
- Go to: `http://127.0.0.1:8000/docs`
- Use `/api/setup` endpoint
- Enter API key through web interface

**Method 3: Direct CLI**
```bash
python my_cli_bot/simple_boiler_ai.py  # Prompts for API key
```

**Method 4: Environment Variables**
```bash
set GEMINI_API_KEY=your-key-here
set OPENAI_API_KEY=your-key-here
```

---

### 🚀 **STARTING THE SYSTEM**

#### **Method 1: Complete System Startup (Recommended)**
```bash
cd "C:\Users\raoro\OneDrive\Desktop\clitest1-main"
python start_boilerai_system.py
```
**What this does:**
- Prompts for API key
- Starts CLI server with API key
- Starts frontend
- Opens browser to AI Assistant

#### **Method 2: Quick Start (Uses Existing CLI Server)**
```bash
cd "C:\Users\raoro\OneDrive\Desktop\clitest1-main"
python quick_start.py
```
**What this does:**
- Starts CLI server (prompts for API key)
- Starts frontend
- Opens browser

#### **Method 3: Manual Setup**
```bash
# Terminal 1: Start CLI Server
cd "C:\Users\raoro\OneDrive\Desktop\bfrontend-main"
python cli_server.py

# Terminal 2: Start Frontend
cd "C:\Users\raoro\OneDrive\Desktop\bfrontend-main"
npm run dev
```

#### **Method 4: API Gateway (Alternative)**
```bash
# Terminal 1: Start API Gateway
cd "C:\Users\raoro\OneDrive\Desktop\clitest1-main"
python -m uvicorn api_gateway.main:app --reload --port 8000

# Terminal 2: Setup API Key
python setup_api_key.py

# Terminal 3: Start Frontend
cd "C:\Users\raoro\OneDrive\Desktop\bfrontend-main"
npm run dev
```

---

### 🔌 **API GATEWAY ENDPOINTS**

**Base URL**: `http://127.0.0.1:8000`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Root endpoint |
| `/health` | GET | Health check |
| `/docs` | GET | API documentation |
| `/api/setup` | POST | Setup API key |
| `/api/status` | GET | Get API status |
| `/api/query` | POST | Process queries |
| `/api/providers` | GET | Available providers |
| `/api/initialize` | POST | Initialize CLI |

#### **Query Request Format**
```json
{
  "query": "What are the CS core requirements?",
  "session_id": "optional-session-id",
  "api_key": "optional-override",
  "provider": "optional-override"
}
```

#### **Query Response Format**
```json
{
  "success": true,
  "query": "What are the CS core requirements?",
  "response": "The CS core requirements are...",
  "thinking": "Processed using AI with comprehensive knowledge base",
  "sources": ["Purdue CS knowledge graph", "Academic advising database"],
  "confidence": 0.85,
  "execution_time": 1.23,
  "timestamp": "2025-01-26T15:30:00"
}
```

---

### 🤖 **CLI AI ASSISTANT**

#### **Main Class**: `SimpleBoilerAI`
- **File**: `my_cli_bot/simple_boiler_ai.py`
- **Required Method**: `process_query(query: str) -> dict`
- **API Key**: Prompts user on first use
- **Providers**: Gemini and OpenAI support

#### **Key Features**
- ✅ Purdue CS academic knowledge
- ✅ Course recommendations
- ✅ Track guidance (MI/SE)
- ✅ CODO support
- ✅ Failure recovery
- ✅ Graduation planning
- ✅ Session management
- ✅ Error handling

#### **Response Format**
```python
{
    "response": "Main answer text",
    "thinking": "Reasoning process",
    "sources": ["source1", "source2"],
    "confidence": 0.85
}
```

---

### 🔧 **TESTING & VALIDATION**

#### **Test CLI Integration**
```bash
python test_cli_integration.py
```

#### **Test API Gateway**
```bash
python setup_api_key.py  # Tests API key setup and query
```

#### **Test API Key Manager**
```bash
python my_cli_bot/api_key_manager.py
```

#### **Test Server Bridge**
```bash
python boilerai_server_bridge.py
```

---

### 🛠️ **DEVELOPMENT & DEBUGGING**

#### **Common Issues & Solutions**

**1. "No module named 'api_gateway'"**
- **Solution**: Use `python -m uvicorn api_gateway.main:app --reload --port 8000`

**2. "CLI not initialized"**
- **Solution**: Set API key via `/api/setup` endpoint

**3. "API key not found"**
- **Solution**: Run `python setup_api_key.py` or use API gateway

**4. Unicode errors in Windows**
- **Solution**: All files use ASCII characters (no emojis in code)

#### **Logs & Monitoring**
- **API Gateway**: Console output
- **CLI**: Console output
- **Monitoring**: `my_cli_bot/logs/ai_monitoring.log`

---

### 📋 **INTEGRATION REQUIREMENTS**

#### **Frontend Integration**
- **API Base URL**: `http://127.0.0.1:8000`
- **Authentication**: API key via `/api/setup`
- **Query Processing**: `/api/query` endpoint
- **Status Checking**: `/api/status` endpoint

#### **CLI Requirements**
- **Python 3.8+**
- **Required packages**: `fastapi`, `uvicorn`, `requests`
- **API key**: User-provided (no hardcoded keys)

#### **Security Features**
- ✅ No hardcoded API keys
- ✅ Secure file storage (`~/.boilerai/api_keys.json`)
- ✅ API key validation
- ✅ CORS support
- ✅ Error handling

---

### 🎯 **SYSTEM GOALS**

1. **User Experience**: Seamless frontend-to-CLI integration
2. **Security**: No hardcoded API keys, user-controlled authentication
3. **Flexibility**: Support for multiple AI providers
4. **Reliability**: Comprehensive error handling and fallbacks
5. **Maintainability**: Clean separation between frontend, API, and CLI

---

### 📞 **SUPPORT & TROUBLESHOOTING**

#### **Quick Commands**
```bash
# Start system
python -m uvicorn api_gateway.main:app --reload --port 8000

# Setup API key
python setup_api_key.py

# Test integration
python test_cli_integration.py

# Check health
curl http://127.0.0.1:8000/health
```

#### **Key Files to Remember**
- **Main CLI**: `my_cli_bot/simple_boiler_ai.py`
- **API Gateway**: `api_gateway/main.py`
- **API Key Manager**: `my_cli_bot/api_key_manager.py`
- **Setup Script**: `setup_api_key.py`
- **Frontend**: `bfrontend-main/` (separate directory)

#### **Important URLs**
- **API Documentation**: `http://127.0.0.1:8000/docs`
- **Health Check**: `http://127.0.0.1:8000/health`
- **API Status**: `http://127.0.0.1:8000/api/status`

---

### 🔄 **SYSTEM STATUS**

**✅ COMPLETED FEATURES**
- CLI AI Assistant with API key management
- API Gateway with FastAPI
- Server bridge for frontend integration
- Secure API key storage and synchronization
- Comprehensive error handling
- Test scripts and validation
- Documentation and setup guides

**🔄 READY FOR**
- Frontend integration
- Production deployment
- User testing
- Feature expansion

---

**Last Updated**: January 26, 2025
**System Version**: 1.0.0
**Status**: Production Ready ✅
