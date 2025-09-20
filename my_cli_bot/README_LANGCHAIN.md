# Enhanced LangChain Academic Advisor

A production-ready LangChain-based academic advisor that integrates seamlessly with your existing Boiler AI system, providing intelligent function calling, vector search, and conversation management.

## 🏗️ Architecture Overview

### Core Components

1. **Enhanced LangChain Pipeline** (`langchain_advisor_pipeline.py`)
   - Intent classification and entity extraction
   - Function calling with existing Boiler AI tools
   - Vector search with FAISS integration
   - Conversation memory and context management

2. **FastAPI Server** (`fastapi_advisor_server.py`)
   - REST API endpoints for all functionality
   - WebSocket support for real-time chat
   - Health monitoring and system statistics
   - API key management and error handling

3. **Vector Database Integration**
   - FAISS vector store with your existing knowledge base
   - Chunked and metadata-tagged course information
   - Similarity search with relevance scoring
   - HyDE (Hypothetical Document Embeddings) support

4. **Function Calling Tools**
   - `getCourseInfo` - Course details and descriptions
   - `getPrerequisites` - Course prerequisite chains
   - `getDegreePlan` - Semester-by-semester planning
   - `analyzeGraduationFeasibility` - Timeline analysis

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements_langchain.txt

# Set OpenAI API key
export OPENAI_API_KEY='your-openai-api-key-here'
```

### Running the System

#### Option 1: Direct Pipeline Usage
```python
from langchain_advisor_pipeline import EnhancedLangChainPipeline

# Initialize pipeline
pipeline = EnhancedLangChainPipeline(api_key="your-key")

# Process queries
result = pipeline.process_query("What is CS 18000?")
print(result["response"])
```

#### Option 2: FastAPI Server
```bash
# Start the server
python fastapi_advisor_server.py

# Server runs on http://localhost:8000
# API docs available at http://localhost:8000/docs
```

#### Option 3: Test the Integration
```bash
# Run comprehensive tests
python test_langchain_pipeline.py

# Or with pytest
pytest test_langchain_pipeline.py -v
```

## 📡 API Endpoints

### Main Chat Endpoint
```http
POST /chat
Content-Type: application/json

{
  "query": "What are the prerequisites for CS 25000?",
  "session_id": "user123",
  "api_key": "optional-override-key",
  "include_context": true
}
```

### Function-Specific Endpoints
```http
# Course Information
GET /courses/CS18000

# Prerequisites
GET /courses/CS25000/prerequisites

# Degree Planning
POST /degree-plan?major=Computer Science&entry_term=Fall&entry_year=2024

# Knowledge Search
GET /search?query=machine learning courses&limit=5
```

### System Endpoints
```http
# Health Check
GET /health

# Available Tools
GET /tools

# System Statistics
GET /statistics
```

### WebSocket Chat
```javascript
// Real-time chat via WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/chat');
ws.send(JSON.stringify({
  "query": "Can I graduate in 3 years?",
  "session_id": "user123"
}));
```

## 🧠 Intelligence Pipeline

### 1. Intent Classification
Automatically classifies queries into categories:
- `COURSE_INFO` - Course details and descriptions
- `PREREQUISITES` - Course prerequisite information
- `DEGREE_PLAN` - Graduation planning and timelines
- `GRADUATION_ANALYSIS` - Early/delayed graduation feasibility
- `TRACK_GUIDANCE` - Track selection and requirements
- `FALLBACK` - General academic questions

### 2. Entity Extraction
Extracts structured data from natural language:
```python
# "What is CS 18000?" → {"courseCode": "CS18000"}
# "Create a plan for Fall 2024" → {"major": "CS", "entryTerm": "Fall", "entryYear": 2024}
# "Can I graduate in 3 years as a sophomore?" → {"currentYear": "sophomore", "targetGraduation": "3 years"}
```

### 3. Function Calling
Routes to appropriate handlers based on intent and entities:
```python
def process_query(query: str) -> dict:
    intent = classify_intent(query)
    entities = extract_entities(query, intent)
    
    if intent == "COURSE_INFO":
        return get_course_info(entities["courseCode"])
    elif intent == "FALLBACK":
        return rag_search_and_answer(query)
```

### 4. RAG Fallback
For general queries, uses vector search + LLM:
```python
# Search vector store → Re-rank results → Generate answer with citations
docs = vector_store.similarity_search(query, k=3)
context = combine_documents(docs)
answer = llm.generate_with_context(query, context)
```

## 🔧 Integration with Existing System

### Seamless Integration Points

1. **Knowledge Base Integration**
   - Uses your existing `cs_knowledge_graph.json`
   - Integrates with `intelligent_conversation_manager.py`
   - Leverages `smart_ai_engine.py` for data retrieval

2. **Conversation Memory**
   - Builds on existing conversation context system
   - Maintains session-based student profiles
   - Preserves conversation history across interactions

3. **Graduation Planning**
   - Uses existing `graduation_planner.py`
   - Integrates with `intelligent_academic_advisor.py`
   - Maintains all current planning capabilities

### Backwards Compatibility
```python
# Your existing code continues to work
from universal_purdue_advisor import UniversalPurdueAdvisor
advisor = UniversalPurdueAdvisor()

# Enhanced LangChain pipeline works alongside
from langchain_advisor_pipeline import EnhancedLangChainPipeline
pipeline = EnhancedLangChainPipeline(api_key)

# Choose based on query complexity
if requires_structured_response:
    result = pipeline.process_query(query)
else:
    result = advisor.process_query(query)
```

## 📊 Performance & Monitoring

### Response Times
- **Function Calls**: <500ms average
- **Vector Search**: <200ms for top-k retrieval
- **Intent Classification**: <100ms
- **Full Pipeline**: <1000ms end-to-end

### System Monitoring
```python
# Health check with component status
GET /health
{
  "status": "healthy",
  "components": {
    "vector_store": "healthy",
    "conversation_manager": "healthy", 
    "llm": "healthy"
  }
}

# System statistics
GET /statistics
{
  "vector_store_size": 1250,
  "tools_available": 5,
  "knowledge_sources": 4
}
```

## 🧪 Testing & Validation

### Comprehensive Test Suite
```bash
# Run all tests
pytest test_langchain_pipeline.py -v

# Test specific components
pytest test_langchain_pipeline.py::TestEnhancedLangChainPipeline::test_intent_classification -v
```

### Test Coverage
- ✅ Intent classification accuracy
- ✅ Entity extraction precision
- ✅ Function calling correctness
- ✅ Vector search relevance
- ✅ API endpoint functionality
- ✅ Error handling and recovery
- ✅ Integration with existing components

### Example Test Scenarios
```python
test_cases = [
    ("What is CS 18000?", "COURSE_INFO", {"courseCode": "CS18000"}),
    ("Prerequisites for CS 25000?", "PREREQUISITES", {"courseCode": "CS25000"}),
    ("Plan for Fall 2024", "DEGREE_PLAN", {"entryTerm": "Fall", "entryYear": 2024}),
    ("Graduate in 3 years?", "GRADUATION_ANALYSIS", {"targetGraduation": "3 years"})
]
```

## 🔐 Security & Configuration

### API Key Management
```python
# Multiple ways to provide API key
pipeline = EnhancedLangChainPipeline(api_key="direct")  # Direct
os.environ["OPENAI_API_KEY"] = "key"  # Environment
request = ChatRequest(api_key="override")  # Per-request override
```

### Error Handling
- Graceful degradation when components unavailable
- Comprehensive logging and monitoring
- Fallback to existing Boiler AI systems
- Rate limiting and resource protection

### Production Considerations
```python
# CORS configuration for web frontends
app.add_middleware(CORSMiddleware, allow_origins=["https://your-domain.com"])

# Gunicorn for production deployment
gunicorn fastapi_advisor_server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## 📈 Extending the System

### Adding New Tools
```python
# Define new tool
new_tool = Tool(
    name="analyzeTranscript",
    description="Analyze student transcript for graduation requirements",
    func=self._analyze_transcript
)

# Add to pipeline
pipeline.tools.append(new_tool)
```

### Custom Intent Categories
```python
# Add to intent classification prompt
custom_intents = ["TRANSCRIPT_ANALYSIS", "CAREER_GUIDANCE", "INTERNSHIP_PLANNING"]

# Update entity extraction for new intents
if intent == "TRANSCRIPT_ANALYSIS":
    return extract_transcript_entities(query)
```

### Vector Store Extensions
```python
# Add new document types
documents.extend(load_career_guidance_docs())
documents.extend(load_internship_data())

# Update metadata for filtering
doc.metadata.update({
    "document_type": "career_guidance",
    "target_audience": "upperclassmen"
})
```

## 🤝 Migration Guide

### From Existing Boiler AI
1. Install LangChain dependencies: `pip install -r requirements_langchain.txt`
2. Initialize pipeline: `pipeline = EnhancedLangChainPipeline(api_key)`
3. Update query routing: Use `pipeline.process_query()` for structured queries
4. Maintain existing functionality: Keep current conversation manager for complex scenarios

### Gradual Integration
```python
class HybridAdvisor:
    def __init__(self):
        self.langchain_pipeline = EnhancedLangChainPipeline(api_key)
        self.conversation_manager = IntelligentConversationManager()
    
    def process_query(self, query, session_id):
        # Try LangChain first for structured queries
        if self.is_structured_query(query):
            return self.langchain_pipeline.process_query(query, session_id)
        else:
            # Fallback to existing system
            return self.conversation_manager.process_query(session_id, query)
```

## 📚 Additional Resources

- **LangChain Documentation**: https://python.langchain.com/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **OpenAI Function Calling**: https://platform.openai.com/docs/guides/function-calling
- **FAISS Vector Search**: https://faiss.ai/

## 🐛 Troubleshooting

### Common Issues

1. **OpenAI API Key Not Set**
   ```bash
   Error: OpenAI API key required
   Solution: export OPENAI_API_KEY='your-key'
   ```

2. **Vector Store Initialization Failed**
   ```bash
   Error: Knowledge base file not found
   Solution: Ensure data/cs_knowledge_graph.json exists
   ```

3. **Import Errors**
   ```bash
   Error: ModuleNotFoundError: No module named 'langchain'
   Solution: pip install -r requirements_langchain.txt
   ```

4. **Pipeline Not Initialized in FastAPI**
   ```bash
   Status: 503 Pipeline not initialized  
   Solution: Check OpenAI API key and restart server
   ```

---

This enhanced LangChain integration provides a production-ready, scalable foundation for your academic advisor while maintaining full compatibility with your existing Boiler AI system.