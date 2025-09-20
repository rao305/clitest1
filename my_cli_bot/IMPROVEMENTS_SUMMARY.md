# BoilerAI Course Planning & Debug Mode Improvements

## 🎯 Issues Resolved

### 1. Course Planning Query Routing Bug
**Problem**: The system was incorrectly routing freshman course questions to Software Engineering track handlers due to aggressive pattern matching that detected "se" in words like "cour**se**s".

**Root Cause**: 
```python
# BEFORE (problematic):
elif "se" in query.lower():
    return self._handle_se_track_courses(query, context, intent)
```

**Solution**: Implemented word boundary matching to prevent false positives:
```python
# AFTER (fixed):
elif re.search(r'\bse\b', query.lower()):
    return self._handle_se_track_courses(query, context, intent)
```

### 2. Limited Year-Level Support
**Problem**: Only supported freshman course planning queries.

**Solution**: Implemented comprehensive year-level detection and handlers for all years (freshman → senior).

## ✨ New Features Implemented

### 1. Comprehensive Year-Level Course Planning

#### Enhanced Intent Patterns
Added patterns to detect course planning queries for all year levels:
```python
"course_planning": [
    # All year levels supported
    r"freshman.*should.*take", r"sophomore.*should.*take", 
    r"junior.*should.*take", r"senior.*should.*take",
    r"compulsory.*courses.*(freshman|sophomore|junior|senior)",
    r"required.*courses.*(freshman|sophomore|junior|senior)",
    r"(freshman|sophomore|junior|senior).*computer.*science",
    r"first.*year.*courses", r"second.*year.*courses", 
    r"third.*year.*courses", r"fourth.*year.*courses",
    # ... more patterns
]
```

#### Year-Level Detection Logic
```python
year_indicators = {
    "freshman": ["freshman", "first year"],
    "sophomore": ["sophomore", "second year"],
    "junior": ["junior", "third year"],
    "senior": ["senior", "fourth year"]
}

# Intelligent year detection with context validation
for year, indicators in year_indicators.items():
    if any(indicator in query_lower for indicator in indicators):
        if any(word in query_lower for word in ["compulsory", "required", "should take", "courses", "start", "begin", "take"]):
            detected_year = year
            break
```

#### Comprehensive Course Plans

**Freshman Course Plan**:
- Fall: CS 18000, MA 16100, General Education (6-8 credits)
- Spring: CS 18200, MA 16200, General Education (6-8 credits)
- Guidelines: Max 2 CS courses per semester, 14-16 total credits
- Critical warnings about CS 18000 importance

**Sophomore Course Plan**:
- Fall: CS 25100, CS 24000, MA 26100, Gen Ed
- Spring: CS 25200, MA 26500, STAT 35000, Gen Ed
- Guidelines: Max 3 CS courses, CS 25100/25200 difficulty warnings
- Success tips for challenging courses

**Junior Course Plan**:
- Core: CS 38100 (Analysis of Algorithms)
- Track selection guidance (MI vs SE)
- Upper-level requirements and science sequence
- Career preparation focus

**Senior Course Plan**:
- Graduation requirements verification
- Capstone projects (CS 49X00)
- Track completion requirements
- Career transition preparation

### 2. CLI Debug/Tracker Mode

#### Debug Mode Activation
Multiple ways to enable debug tracking:

1. **Command Line Flag**:
   ```bash
   python boiler_ai_complete.py --debug
   python boiler_ai_complete.py --tracker
   ```

2. **Interactive Commands**:
   ```
   You> debug
   🔍 Debug/Tracker Mode ENABLED - You'll now see query routing details
   
   You> debug off
   📴 Debug/Tracker Mode DISABLED
   ```

3. **Programmatic**:
   ```python
   boiler_ai = BoilerAIComplete(debug_mode=True)
   ```

#### Debug Logging System
Comprehensive debug output showing query processing flow:

```
🔍 [DEBUG] QUERY_INPUT
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    📋 Received user query
    📊 session_id: session_20240720_143022
    📊 raw_query: What courses should a sophomore take?
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 [DEBUG] QUERY_VALIDATION
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    📋 Query validation completed
    📊 original: What courses should a sophomore take?
    📊 validated: What courses should a sophomore take?
    📊 changed: False
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 [DEBUG] CONTEXT_EXTRACTION
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    📋 Context extraction and update
    📊 previous_context: {}
    📊 updated_context: {'current_year': 'sophomore'}
    📊 context_changes: {'current_year': 'sophomore'}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 [DEBUG] INTENT_ANALYSIS
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    📋 Intent classification completed
    📊 primary_intent: course_planning
    📊 confidence: 0.95
    📊 all_intents: {'course_planning': 0.95}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 [DEBUG] YEAR_LEVEL_DETECTED
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    📋 Year-level course planning detected: sophomore
    📊 detected_year: sophomore
    📊 query: what courses should a sophomore take?
    📊 indicators_matched: ['sophomore']
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 [DEBUG] RESPONSE_GENERATED
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    📋 Response generation completed
    📊 response_length: 2847
    📊 response_preview: Here are the essential courses for computer science sophomores at Purdue:

**Prerequisites Check:**
Before sophomore courses, you should have completed:
• CS 18000 (Problem Solving and Object-...
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### Debug Stages Tracked
1. **QUERY_INPUT**: Raw user input and session information
2. **QUERY_VALIDATION**: Input sanitization and validation
3. **SESSION_CREATED**: New session creation (if applicable)
4. **CONTEXT_EXTRACTION**: Student context and information extraction
5. **INTENT_ANALYSIS**: Intent classification and confidence scoring
6. **YEAR_LEVEL_DETECTED**: Year-level specific routing
7. **TRACK_ROUTING**: Track-specific routing (MI/SE)
8. **RESPONSE_ROUTING**: Handler method routing
9. **RESPONSE_GENERATED**: Final response generation

## 🚀 Usage Examples

### Year-Level Course Planning
```bash
# All of these now work correctly:
You> What courses should a freshman take?
You> Sophomore course requirements
You> What should a junior computer science major take?
You> Senior capstone planning
You> What are the compulsory courses for a freshman computer science major?
```

### Debug Mode Usage
```bash
# Start with debug mode
python boiler_ai_complete.py --debug

# Or enable during session
You> debug
🔍 Debug/Tracker Mode ENABLED

You> What courses should a sophomore take?
[Shows detailed debug output...]

You> debug off
📴 Debug/Tracker Mode DISABLED
```

## 📁 Files Modified

### Core Improvements
- **`intelligent_conversation_manager.py`**: 
  - Added comprehensive year-level detection and handlers
  - Implemented debug logging system
  - Fixed pattern matching bugs
  - Added 4 new course planning methods

### CLI Enhancements  
- **`boiler_ai_complete.py`**: 
  - Added debug mode support
  - Added interactive debug commands
  - Enhanced help system

- **`universal_purdue_advisor.py`**: 
  - Added debug mode parameter passing

### Testing
- **`test_year_level_improvements.py`**: Created comprehensive test suite

## 🎯 Benefits

### For Users
1. **Accurate Course Guidance**: No more incorrect track routing
2. **Comprehensive Coverage**: Support for all year levels (freshman → senior)
3. **Detailed Planning**: Semester-by-semester course recommendations
4. **Success Tips**: Year-specific guidelines and warnings

### For Developers/Debugging
1. **Complete Visibility**: See exactly how queries are processed
2. **Intent Tracking**: Understand why certain responses are generated
3. **Routing Transparency**: Track the decision-making process
4. **Performance Insights**: Identify bottlenecks and improve accuracy

### For Future Development
1. **Robust Pattern Matching**: Prevents similar routing bugs
2. **Extensible Framework**: Easy to add new year levels or tracks
3. **Debug Infrastructure**: Built-in tools for troubleshooting
4. **Comprehensive Testing**: Validation framework for new features

## 🔧 Technical Details

### Pattern Matching Improvements
- Word boundary regex patterns (`\b`) prevent false matches
- Multi-level validation (keyword + context requirements)
- Explicit year-level detection with confidence scoring

### Debug System Architecture
- Non-intrusive logging (only when debug_mode=True)
- Structured output with clear visual separation
- Performance-conscious (minimal overhead when disabled)
- Comprehensive coverage of all processing stages

### Course Planning Framework
- Modular design with separate handlers per year level
- Consistent format across all year levels
- Prerequisite validation and dependency tracking
- Career preparation guidance integrated throughout

The system now provides accurate, comprehensive course planning guidance for all CS students at Purdue while offering complete visibility into the decision-making process through the debug/tracker mode.