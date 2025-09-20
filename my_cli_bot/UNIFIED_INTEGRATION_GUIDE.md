# LangChain + N8N Unified Integration Guide

## Overview

This integration combines the strengths of both LangChain and N8N systems to create a powerful, flexible academic advisor pipeline. The unified system intelligently routes queries between different processing modes based on query characteristics and user preferences.

## 🏗️ Architecture

### Components

1. **Unified Pipeline Orchestrator** (`unified_langchain_n8n_pipeline.py`)
   - Intelligent routing between N8N and LangChain
   - Hybrid processing with fallback capabilities
   - Caching and performance optimization
   - Real-time monitoring and analytics

2. **Enhanced N8N Nodes**
   - LangChain integration within N8N workflows
   - N8N enhancement for LangChain pipelines
   - Seamless data flow between systems

3. **Unified API Server** (`unified_api_server.py`)
   - REST API and WebSocket endpoints
   - Health monitoring and system status
   - Error handling and logging

4. **N8N Workflow Configuration** (`n8n_langchain_workflow.json`)
   - Production-ready N8N workflow
   - Intelligent query routing
   - Error handling and analytics

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install dependencies
pip install -r requirements_langchain.txt

# Set environment variables
export OPENAI_API_KEY='your-openai-api-key'
export N8N_WEBHOOK_URL='http://localhost:5678/webhook/boilerai'
```

### 2. Basic Usage

```python
from unified_langchain_n8n_pipeline import create_unified_pipeline, PipelineMode

# Create pipeline
pipeline = create_unified_pipeline(
    openai_api_key="your-key",
    default_mode=PipelineMode.HYBRID
)

# Process queries
result = pipeline.process_query_sync("What is CS 18000?")
print(result.response)

# Async processing
result = await pipeline.process_query_async(
    query="What are the prerequisites for CS 25000?",
    session_id="user123",
    mode=PipelineMode.LANGCHAIN_ONLY
)
```

### 3. API Server

```bash
# Start the unified API server
python unified_api_server.py

# Server runs on http://localhost:8000
# API docs: http://localhost:8000/docs
# Health check: http://localhost:8000/health
```

### 4. Test the Integration

```bash
# Run comprehensive tests
python test_unified_integration.py

# Or with pytest
pytest test_unified_integration.py -v
```

## 🎯 Pipeline Modes

### Mode Selection Strategy

The system intelligently chooses the optimal processing mode:

#### N8N Only (`n8n_only`)
- **Best for**: Conversational queries, complex context building
- **Examples**: "Tell me about the MI track", "I failed CS 25100, help me"
- **Characteristics**: Detailed responses, context-aware processing

#### LangChain Only (`langchain_only`) 
- **Best for**: Structured queries, specific information requests
- **Examples**: "What is CS 18000?", "Prerequisites for CS 25000?"
- **Characteristics**: Fast, precise responses with function calling

#### Hybrid (`hybrid`) - Default
- **Best for**: Complex queries requiring both systems
- **Examples**: "Can I graduate early with both tracks?"
- **Characteristics**: Combines strengths of both systems

#### Fallback (`fallback`)
- **Best for**: Reliability-critical scenarios
- **Characteristics**: Tries primary method, falls back to secondary

### Manual Mode Selection

```python
# Force specific mode
result = pipeline.process_query_sync(
    query="What is CS 18000?",
    mode=PipelineMode.LANGCHAIN_ONLY
)

# Let system decide (recommended)
result = pipeline.process_query_sync(
    query="What is CS 18000?",
    mode=PipelineMode.HYBRID
)
```

## 📡 API Usage

### REST API

```bash
# Basic query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is CS 18000?",
    "session_id": "user123",
    "mode": "hybrid"
  }'

# With context
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What should I take next?",
    "session_id": "user123",
    "context": {
      "previous_queries": ["What is CS 18000?"],
      "student_context": {"year": "sophomore", "gpa": 3.5}
    }
  }'
```

### WebSocket

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/user123');

// Send query
ws.send(JSON.stringify({
  query: "What are the CODO requirements?",
  mode: "hybrid"
}));

// Receive response
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Response:', data.data.response);
};
```

### Python Client

```python
import asyncio
import aiohttp

async def query_api(query: str, session_id: str = "test"):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/query",
            json={
                "query": query,
                "session_id": session_id,
                "mode": "hybrid"
            }
        ) as response:
            result = await response.json()
            return result["response"]

# Usage
response = asyncio.run(query_api("What is CS 18000?"))
print(response)
```

## 🔧 Configuration

### Pipeline Configuration

```python
from unified_langchain_n8n_pipeline import UnifiedPipelineConfig, PipelineMode

config = UnifiedPipelineConfig(
    default_mode=PipelineMode.HYBRID,
    n8n_webhook_url="http://localhost:5678/webhook/boilerai",
    openai_api_key="your-key",
    enable_caching=True,
    cache_ttl_minutes=15,
    max_retries=3,
    timeout_seconds=30,
    enable_monitoring=True,
    fallback_enabled=True
)

orchestrator = UnifiedPipelineOrchestrator(config)
```

### Environment Variables

```bash
# Required
export OPENAI_API_KEY='your-openai-api-key'

# Optional
export N8N_WEBHOOK_URL='http://localhost:5678/webhook/boilerai'
export HOST='0.0.0.0'
export PORT='8000'
export RELOAD='true'
```

## 🔄 N8N Integration

### Import Workflow

1. Open N8N interface
2. Create new workflow
3. Import `n8n_langchain_workflow.json`
4. Configure webhook URL
5. Set environment variables
6. Activate workflow

### Webhook Configuration

```json
{
  "webhook_url": "http://localhost:5678/webhook/boilerai-langchain",
  "method": "POST",
  "authentication": "none",
  "response_mode": "onReceived"
}
```

### N8N Environment Setup

```javascript
// In N8N Environment node
{
  "OPENAI_API_KEY": "{{ $env.OPENAI_API_KEY }}",
  "LANGCHAIN_ENDPOINT": "http://localhost:8000",
  "N8N_ENDPOINT": "http://localhost:8001",
  "UNIFIED_ENDPOINT": "http://localhost:8002"
}
```

## 📊 Monitoring & Analytics

### System Status

```python
# Get system status
status = pipeline.get_system_status()
print(json.dumps(status, indent=2))

# API endpoint
curl http://localhost:8000/status
```

### Performance Metrics

```python
# Access performance metrics
metrics = pipeline.performance_metrics
print(f"Total queries: {metrics['total_queries']}")
print(f"Average response time: {metrics['average_response_time']:.2f}s")
print(f"Cache hit rate: {metrics['cache_hits'] / metrics['total_queries']:.2%}")
```

### Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unified_pipeline.log'),
        logging.StreamHandler()
    ]
)
```

## 🧪 Testing

### Run Test Suite

```bash
# All tests
python test_unified_integration.py

# Specific test categories
pytest test_unified_integration.py -m "not integration"  # Unit tests only
pytest test_unified_integration.py -m integration        # Integration tests
pytest test_unified_integration.py -m performance       # Performance tests
```

### Manual Testing

```python
# Test different modes
test_queries = [
    ("What is CS 18000?", PipelineMode.LANGCHAIN_ONLY),
    ("Tell me about the MI track", PipelineMode.N8N_ONLY), 
    ("Can I graduate early?", PipelineMode.HYBRID),
]

for query, mode in test_queries:
    result = pipeline.process_query_sync(query, mode=mode)
    print(f"Query: {query}")
    print(f"Mode: {mode.value}")
    print(f"Response: {result.response[:100]}...")
    print(f"Pipeline used: {result.pipeline_used}")
    print("-" * 50)
```

## 🚀 Production Deployment

### Docker Setup

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements_langchain.txt .
RUN pip install -r requirements_langchain.txt

COPY . .
EXPOSE 8000

CMD ["python", "unified_api_server.py"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  unified-pipeline:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - N8N_WEBHOOK_URL=http://n8n:5678/webhook/boilerai
    depends_on:
      - n8n
      
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=password
    volumes:
      - ./n8n-data:/home/node/.n8n
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: unified-pipeline
spec:
  replicas: 3
  selector:
    matchLabels:
      app: unified-pipeline
  template:
    metadata:
      labels:
        app: unified-pipeline
    spec:
      containers:
      - name: unified-pipeline
        image: your-registry/unified-pipeline:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: api-key
---
apiVersion: v1
kind: Service
metadata:
  name: unified-pipeline-service
spec:
  selector:
    app: unified-pipeline
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

## 🔧 Troubleshooting

### Common Issues

#### 1. OpenAI API Key Issues
```bash
Error: OpenAI API key required
Solution: export OPENAI_API_KEY='your-key'
```

#### 2. LangChain Import Errors
```bash
Error: ModuleNotFoundError: No module named 'langchain'
Solution: pip install -r requirements_langchain.txt
```

#### 3. N8N Connection Issues
```bash
Error: N8N webhook not responding
Solution: Check N8N is running and webhook URL is correct
```

#### 4. Performance Issues
```bash
Issue: Slow response times
Solutions:
- Enable caching: enable_caching=True
- Reduce timeout: timeout_seconds=15
- Use specific modes instead of hybrid
- Check system resources
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debug configuration
config = UnifiedPipelineConfig(
    enable_monitoring=True,
    timeout_seconds=60,  # Longer timeout for debugging
    max_retries=1        # Reduce retries for faster debugging
)
```

### Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Check component status
curl http://localhost:8000/status

# Check available modes
curl http://localhost:8000/modes
```

## 📈 Performance Optimization

### Caching Strategy

```python
# Optimize cache settings
config = UnifiedPipelineConfig(
    enable_caching=True,
    cache_ttl_minutes=30,  # Longer cache for better performance
)

# Clear cache manually if needed
pipeline.query_cache.clear()
```

### Mode Selection Optimization

```python
# Use specific modes for better performance
structured_queries = ["What is", "Prerequisites for", "Requirements for"]
conversational_queries = ["Tell me about", "Explain", "Help me"]

def get_optimal_mode(query: str) -> PipelineMode:
    query_lower = query.lower()
    
    if any(pattern in query_lower for pattern in structured_queries):
        return PipelineMode.LANGCHAIN_ONLY  # Faster for structured queries
    elif any(pattern in query_lower for pattern in conversational_queries):
        return PipelineMode.N8N_ONLY        # Better for conversations
    else:
        return PipelineMode.HYBRID          # Default
```

### Async Processing

```python
# Use async for better concurrency
async def process_multiple_queries(queries: List[str]):
    tasks = [
        pipeline.process_query_async(query, f"session_{i}")
        for i, query in enumerate(queries)
    ]
    return await asyncio.gather(*tasks)

# Usage
queries = ["What is CS 18000?", "What is CS 18200?", "What is CS 24000?"]
results = await process_multiple_queries(queries)
```

## 🔄 Migration from Existing Systems

### From Pure N8N

```python
# Existing N8N usage
n8n_pipeline = N8NStylePipeline()
result = n8n_pipeline.execute_workflow(query)

# Migrated to unified
unified_pipeline = create_unified_pipeline()
result = unified_pipeline.process_query_sync(
    query=query,
    mode=PipelineMode.N8N_ONLY  # Keep N8N behavior initially
)

# Gradually move to hybrid
result = unified_pipeline.process_query_sync(
    query=query,
    mode=PipelineMode.HYBRID    # Enable intelligent routing
)
```

### From Pure LangChain

```python
# Existing LangChain usage
langchain_pipeline = EnhancedLangChainPipeline(api_key)
result = langchain_pipeline.process_query(query)

# Migrated to unified
unified_pipeline = create_unified_pipeline(openai_api_key=api_key)
result = unified_pipeline.process_query_sync(
    query=query,
    mode=PipelineMode.LANGCHAIN_ONLY  # Keep LangChain behavior initially
)

# Enable enhanced capabilities
result = unified_pipeline.process_query_sync(
    query=query,
    mode=PipelineMode.HYBRID  # Get best of both systems
)
```

## 🎓 Best Practices

### 1. Mode Selection
- Use `LANGCHAIN_ONLY` for structured, factual queries
- Use `N8N_ONLY` for conversational, context-heavy queries  
- Use `HYBRID` for complex queries requiring both systems
- Use `FALLBACK` for mission-critical applications

### 2. Session Management
- Always provide session IDs for conversation continuity
- Include user context when available
- Track conversation history for better responses

### 3. Error Handling
- Implement retry logic for critical operations
- Use fallback modes for reliability
- Monitor system health regularly

### 4. Performance
- Enable caching for repeated queries
- Use async processing for concurrent requests
- Monitor response times and optimize bottlenecks

### 5. Security
- Secure OpenAI API keys properly
- Validate all input data
- Implement rate limiting in production
- Use HTTPS in production deployments

## 📚 Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [N8N Documentation](https://docs.n8n.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

---

This unified integration provides a robust, scalable foundation for academic advising while maintaining the flexibility to use either system independently or in combination based on specific needs.