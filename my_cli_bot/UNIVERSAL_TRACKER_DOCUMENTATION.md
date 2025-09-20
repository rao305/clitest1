# Universal Query Tracker Documentation

## 🔍 Overview

The Universal Query Tracker provides complete visibility into how ANY query gets processed through the BoilerAI system. Unlike basic debug modes, this tracks the entire journey from input to response across ALL query types.

## 🚀 Quick Start

### Enable Tracker
```bash
# Method 1: Command line flag
python boiler_ai_complete.py --tracker

# Method 2: Interactive commands
You> tracker on
🔍 Query Tracker Mode ENABLED - You'll now see detailed query processing

You> tracker off  
📴 Query Tracker Mode DISABLED
```

### Example Tracked Query
```
You> What courses should a sophomore take?

🔍 [TRACKER] QUERY_INPUT
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    📋 Received user query
    📊 session_id: session_20240720_143022
    📊 raw_query: What courses should a sophomore take?
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 [TRACKER] INTENT_ANALYSIS
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    📋 Intent classification completed
    📊 primary_intent: course_planning
    📊 confidence: 0.95
    📊 all_intents: {'course_planning': 0.95}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 [TRACKER] YEAR_LEVEL_DETECTED
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    📋 Year-level course planning detected: sophomore
    📊 detected_year: sophomore
    📊 indicators_matched: ['sophomore']
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Bot> Here are the essential courses for computer science sophomores at Purdue:
[Response continues...]
```

## 📊 Tracking Capabilities

### 🔍 Query Processing Stages
1. **QUERY_INPUT** - Raw user input reception and session management
2. **QUERY_VALIDATION** - Input sanitization and cleaning
3. **SESSION_CREATED** - New conversation session initialization
4. **CONTEXT_EXTRACTION** - Student context and profile building
5. **INTENT_ANALYSIS** - Intent classification with confidence scoring
6. **RESPONSE_ROUTING** - Handler selection and routing logic
7. **RESPONSE_GENERATED** - Final response creation and delivery

### 🎯 Intent Classification Tracking
Shows how queries get categorized:

- **greeting** - Welcome messages and casual interactions
- **course_planning** - Course selection guidance (all year levels)
- **track_selection** - MI/SE track decisions and comparisons
- **graduation_planning** - Timeline analysis and requirements
- **course_difficulty** - Study tips and challenge guidance
- **failure_recovery** - Course retake strategies and recovery
- **codo_advice** - Major change guidance and requirements
- **career_guidance** - Career planning and internship advice

### 🗺️ Knowledge Graph Access Tracking
Monitors data retrieval from the knowledge base:

- **Course catalog traversal** - Which courses are being accessed
- **Prerequisite chain analysis** - Dependency resolution tracking
- **CODO requirements lookup** - Admission requirement checks
- **Track requirements validation** - Specialization requirement verification
- **GPA and credit calculations** - Academic standing analysis

### 🧭 Routing Decision Tracking
Shows the decision-making process:

- **Year-level detection** - How freshman/sophomore/junior/senior is identified
- **Track-specific routing** - MI vs SE pattern matching logic
- **Pattern matching explanations** - Why certain patterns matched
- **Handler selection rationale** - Which method processes the query

### 📊 Context Tracking
Monitors conversation state:

- **Student profile building** - How user information is extracted
- **Conversation history maintenance** - Session continuity tracking
- **Context changes between queries** - Profile updates and modifications
- **Information extraction** - What data is pulled from each query

## 🧪 Comprehensive Query Type Support

The tracker works with ALL query types:

### Course Planning (All Year Levels)
```
You> What courses should a freshman take?
You> Sophomore course requirements
You> Junior track selection
You> Senior capstone planning
```

### Track and Specialization
```
You> Should I choose MI or SE track?
You> Machine intelligence course requirements
You> Software engineering track options
```

### Academic Challenges
```
You> I failed CS 25100, what should I do?
You> How hard is CS 25200?
You> CODO requirements for CS
```

### Career and Planning
```
You> What careers can I pursue with CS?
You> When will I graduate?
You> How do I get an internship?
```

### General Information
```
You> What is CS 18000?
You> Prerequisites for CS 25000?
You> Hi there, can you help me?
```

### Complex Queries
```
You> I'm a junior CS student with a 3.2 GPA who failed CS 25100 and wants to graduate on time while pursuing the MI track
```

## 📋 Tracking Output Format

### Standard Tracking Block
```
🔍 [TRACKER] STAGE_NAME
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    📋 Human-readable description of what's happening
    📊 key_data: value
    📊 additional_info: details
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Key Tracking Symbols
- **🔍 [TRACKER]** - Main tracking identifier
- **📋** - Description/explanation
- **📊** - Data/metrics
- **📝** - Text content
- **━━━━** - Visual separators

## 🛠️ CLI Commands

### Interactive Commands
```bash
# Enable tracking
tracker on
tracker
track on

# Disable tracking  
tracker off
track off

# Check status
status

# Get help
help
```

### Command Line Flags
```bash
# Start with tracker enabled
python boiler_ai_complete.py --tracker
python boiler_ai_complete.py --track

# Regular start (tracker disabled)
python boiler_ai_complete.py
```

## 🔧 Technical Implementation

### Core Components

1. **IntelligentConversationManager**
   - `tracker_mode` parameter controls tracking
   - `_track_query()` method handles all logging
   - Integrated throughout the processing pipeline

2. **Universal Tracking Method**
   ```python
   def _track_query(self, stage: str, data: Any, description: str = ""):
       """Track query processing when tracker mode is enabled"""
       if self.tracker_mode:
           # Display formatted tracking information
   ```

3. **CLI Integration**
   - `BoilerAIComplete` class manages tracker state
   - Real-time enable/disable without restart
   - Help system integration

### Tracking Points
The tracker has monitoring points at:
- Query input and validation
- Context extraction and updates
- Intent analysis and classification
- Knowledge graph data access
- Routing decisions and handler selection
- Response generation and delivery

## 📈 Benefits

### For Users
- **Complete Transparency** - See exactly how queries are processed
- **Learning Tool** - Understand the AI's decision-making process
- **Debugging Aid** - Identify why certain responses are generated
- **Confidence Building** - See the systematic approach to answering

### For Developers
- **System Understanding** - Complete visibility into processing flow
- **Bug Detection** - Identify routing and classification issues
- **Performance Analysis** - Spot bottlenecks and inefficiencies
- **Feature Validation** - Verify new features work correctly

### For Academic Purposes
- **AI Education** - Demonstrate how conversational AI systems work
- **Process Documentation** - Complete audit trail of decisions
- **Research Data** - Detailed logs for analysis and improvement
- **Transparency** - Open-book approach to AI decision making

## 🚀 Usage Examples

### Debugging Incorrect Responses
If a query gives unexpected results:
1. Enable tracker: `tracker on`
2. Re-ask the question
3. Review the intent classification and routing
4. Identify where the logic diverged from expectations

### Understanding Complex Queries
For multi-part questions:
1. Watch how context gets extracted
2. See how multiple intents are handled
3. Observe knowledge graph traversal
4. Track the synthesis process

### Learning System Behavior
To understand how the AI works:
1. Ask similar questions and compare routing
2. See how student context affects responses
3. Observe pattern matching in action
4. Learn about the knowledge base structure

## 🎯 Key Features

- **Universal Coverage** - Works with ALL query types, not just specific examples
- **Real-time Control** - Enable/disable without restarting
- **Detailed Visibility** - Complete processing pipeline exposure
- **Structured Output** - Consistent, readable format
- **Performance Conscious** - Zero overhead when disabled
- **Educational Value** - Learn how conversational AI works

The Universal Query Tracker transforms the BoilerAI system from a "black box" into a transparent, educational tool that shows exactly how every query gets processed, classified, and responded to.