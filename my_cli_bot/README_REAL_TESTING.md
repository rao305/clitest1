# Real-World Testing with OpenAI API

## Overview
The Hybrid AI System now requires a real OpenAI API key and provides no mock or template fallbacks. All responses are generated using actual OpenAI integration.

## Setup

### 1. Get a Real OpenAI API Key
1. Go to https://platform.openai.com/account/api-keys
2. Create a new API key (starts with `sk-`)
3. Ensure your account has available credits

### 2. Set Environment Variable
```bash
export OPENAI_API_KEY='sk-your-real-openai-key-here'
```

### 3. Verify Setup
```bash
echo $OPENAI_API_KEY
# Should show: sk-your-key...
```

## Testing Scripts

### Interactive Testing
```bash
python3 interactive_real_test.py
```
- Real-time conversation with the hybrid system
- Ask any Purdue CS questions
- See immediate responses using real OpenAI

### Automated Testing  
```bash
python3 real_world_test.py
```
- Tests 8 realistic student queries
- Shows routing decisions (lookup/rule/LLM)
- Validates response quality

### Routing-Only Testing
```bash
python3 real_world_test.py --routing-only
```
- Focuses on query classification
- Tests routing logic with real API calls

## Example Real Queries

### Lookup Table Queries (Instant)
- "What is CS 18000?"
- "What are the MI track requirements?" 
- "What are CODO requirements?"

### Rule-Based Queries (Fast Logic)
- "What prerequisites do I need for CS 25000?"
- "I failed CS 18000, what should I do?"

### LLM-Enhanced Queries (Full OpenAI)
- "Help me choose between AI and software engineering careers"
- "How do the MI and SE tracks compare?"
- "I'm interested in machine learning, what's my best path?"

## System Validation

The system validates your OpenAI API key on startup:
- ✅ Checks format (must start with 'sk-')
- ✅ Tests actual API connection
- ✅ Validates credits/permissions

## No Fallbacks

- ❌ No mock responses
- ❌ No template answers  
- ❌ No offline mode
- ✅ Real OpenAI integration only
- ✅ Hybrid routing with actual API calls
- ✅ Dynamic responses based on real student queries

## Architecture in Action

```
Real Student Query
        ↓
Query Classification (Real Analysis)
        ↓
Route Decision:
├── Lookup Table → Official Data (Instant)
├── Rule-Based → Logic + Structure (Fast)  
└── LLM Enhanced → OpenAI GPT-4 (Full AI)
        ↓
Real Response to Student
```

## Cost Efficiency

The hybrid system minimizes OpenAI API costs:
- **Lookup queries**: $0 (instant database responses)
- **Rule-based queries**: $0 (structured logic responses)
- **LLM queries**: ~$0.01-0.05 per query (only when needed)

Most student queries (60-70%) use lookup tables or rules, significantly reducing API costs while maintaining response quality.

## Getting Started

1. Set your real OpenAI API key
2. Run: `python3 interactive_real_test.py`
3. Ask: "What is CS 18000?"
4. See instant lookup table response
5. Ask: "How do I choose between tracks?"
6. See real OpenAI analysis

The system will show you exactly which routing method was used for each query, demonstrating the hybrid Logic + LLM architecture in action.