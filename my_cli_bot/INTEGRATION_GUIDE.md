# 🔌 BoilerAI Integration Guide

## Quick Setup (5 minutes)

### **Step 1: Start the API Server** 🚀
```bash
cd my_cli_bot

# Set your API keys
export OPENAI_API_KEY="your-openai-key-here"
export CLADO_API_KEY="lk_26267cec2bcd4f34b9894bc07a00af1b"

# Start the server
python3 simple_api_server.py
```

Server will be running at: `http://localhost:3001`

### **Step 2: Add to Your Website** 🌐

#### **Option A: Simple Widget (Easiest)**
Add this to your HTML:

```html
<!-- Include BoilerAI client -->
<script src="http://localhost:3001/boilerai-client.js"></script>

<!-- Create container -->
<div id="boilerai-widget"></div>

<script>
// Initialize BoilerAI
const boilerAI = new BoilerAI('http://localhost:3001');

// Create widget
boilerAI.createWidget('boilerai-widget', {
    title: 'BoilerAI',
    subtitle: 'CS Academic Advisor',
    height: '500px'
});
</script>
```

#### **Option B: Custom Integration**
```html
<script src="http://localhost:3001/boilerai-client.js"></script>

<script>
const boilerAI = new BoilerAI('http://localhost:3001');

async function askBoilerAI() {
    const userQuestion = document.getElementById('question').value;
    const response = await boilerAI.chat(userQuestion);
    
    if (response.success) {
        document.getElementById('answer').innerHTML = response.message;
    } else {
        console.error('Error:', response.error);
    }
}
</script>

<input type="text" id="question" placeholder="Ask BoilerAI...">
<button onclick="askBoilerAI()">Ask</button>
<div id="answer"></div>
```

#### **Option C: Direct API Calls**
```javascript
async function chatWithBoilerAI(message) {
    try {
        const response = await fetch('http://localhost:3001/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: 'your-session-id'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            return data.response;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('BoilerAI Error:', error);
        return 'Sorry, BoilerAI is temporarily unavailable.';
    }
}

// Usage
const answer = await chatWithBoilerAI('What courses do I need for MI track?');
console.log(answer);
```

## **API Endpoints** 📡

### **POST /api/chat**
Main chatbot endpoint

**Request:**
```json
{
    "message": "What courses do I need for the MI track?",
    "session_id": "optional_session_id"
}
```

**Response:**
```json
{
    "success": true,
    "response": "For the Machine Intelligence track, you'll need...",
    "session_id": "session_123",
    "timestamp": "2024-01-20T10:30:00Z"
}
```

### **GET /api/health**
Check if BoilerAI is running

**Response:**
```json
{
    "status": "healthy",
    "service": "BoilerAI",
    "version": "2.0"
}
```

### **GET /api/info**
Get system information

**Response:**
```json
{
    "name": "BoilerAI",
    "description": "Purdue CS Academic Advisor",
    "capabilities": [
        "Course planning and prerequisites",
        "Track selection (MI/SE)",
        "Graduation timeline planning"
    ]
}
```

## **Advanced Integration Examples** 🔧

### **React Integration**
```jsx
import React, { useState, useEffect } from 'react';

function BoilerAIChat() {
    const [boilerAI, setBoilerAI] = useState(null);
    const [message, setMessage] = useState('');
    const [response, setResponse] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        // Initialize BoilerAI client
        const client = new window.BoilerAI('http://localhost:3001');
        setBoilerAI(client);
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!boilerAI || !message.trim()) return;

        setLoading(true);
        const result = await boilerAI.chat(message);
        setResponse(result.message);
        setLoading(false);
        setMessage('');
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Ask BoilerAI..."
                    disabled={loading}
                />
                <button type="submit" disabled={loading}>
                    {loading ? 'Asking...' : 'Ask'}
                </button>
            </form>
            {response && (
                <div style={{ marginTop: '20px', padding: '10px', background: '#f5f5f5' }}>
                    {response}
                </div>
            )}
        </div>
    );
}
```

### **Vue.js Integration**
```vue
<template>
    <div>
        <input 
            v-model="question" 
            @keyup.enter="askBoilerAI" 
            placeholder="Ask BoilerAI..."
        />
        <button @click="askBoilerAI" :disabled="loading">
            {{ loading ? 'Asking...' : 'Ask' }}
        </button>
        <div v-if="answer" class="answer">
            {{ answer }}
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            boilerAI: null,
            question: '',
            answer: '',
            loading: false
        }
    },
    mounted() {
        this.boilerAI = new window.BoilerAI('http://localhost:3001');
    },
    methods: {
        async askBoilerAI() {
            if (!this.question.trim() || this.loading) return;
            
            this.loading = true;
            const response = await this.boilerAI.chat(this.question);
            this.answer = response.message;
            this.loading = false;
            this.question = '';
        }
    }
}
</script>
```

## **Production Deployment** 🌐

### **1. Change API URL**
Update your frontend code to use your production server:
```javascript
const boilerAI = new BoilerAI('https://your-domain.com');
```

### **2. Configure CORS**
In `simple_api_server.py`, update CORS settings:
```python
# Replace this line:
CORS(app, origins=["*"], methods=["GET", "POST", "OPTIONS"])

# With your specific domain:
CORS(app, origins=["https://your-website.com"], methods=["GET", "POST", "OPTIONS"])
```

### **3. Use Environment Variables**
```bash
export OPENAI_API_KEY="your-production-key"
export CLADO_API_KEY="your-clado-key"
export FLASK_ENV="production"
```

### **4. Run with Production Server**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:3001 simple_api_server:app
```

## **Testing Your Integration** 🧪

### **1. Quick Test**
```bash
# Test API directly
curl -X POST http://localhost:3001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What courses do I need for MI track?"}'
```

### **2. Browser Console Test**
```javascript
// Open browser console on your website
fetch('http://localhost:3001/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'Hello BoilerAI!' })
})
.then(r => r.json())
.then(console.log);
```

## **Troubleshooting** 🔧

### **CORS Issues**
If you get CORS errors:
1. Make sure the API server is running
2. Check the CORS configuration in `simple_api_server.py`
3. Use the correct API URL in your frontend

### **API Key Issues**
```bash
# Check if keys are set
echo $OPENAI_API_KEY
echo $CLADO_API_KEY

# Set them if missing
export OPENAI_API_KEY="your-key-here"
```

### **Server Not Starting**
1. Make sure you're in the `my_cli_bot` directory
2. Check that all Python dependencies are installed
3. Verify the chatbot modules exist

## **Support** 📞

- **Health Check**: `GET http://localhost:3001/api/health`
- **System Info**: `GET http://localhost:3001/api/info`
- **Logs**: Check the terminal where you started the server

That's it! Your website now has BoilerAI integration. 🎉