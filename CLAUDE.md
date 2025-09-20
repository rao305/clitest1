# Boiler AI - Purdue CS Academic Advisor

## Project Overview
This is a comprehensive AI-powered academic advisor for Purdue Computer Science students. The system provides intelligent, personalized guidance for graduation planning, course selection, track specialization, and failure recovery.

## Complete Implementation Status 

### Core Vision Achieved
- **Graduation delay/early planner** referencing actual degree progression guides
- **Machine Intelligence & Software Engineering track specialization**
- **Foundation class failure impact analysis with recovery strategies**
- **Summer course acceleration and catch-up options**
- **Course load optimization (max 2-3 CS courses per semester)**
- **Intelligent AI with conversation memory and personalized responses**
- **Clean, natural responses without markdown formatting**

## Key Files & Architecture

### Primary System Files
1. **`intelligent_conversation_manager.py`** - Main AI conversation system
   - Context extraction from user queries
   - Conversation memory across sessions
   - Intent analysis and personalized responses
   - No hardcoded messages - all responses tailored to user

2. **`graduation_planner.py`** - Advanced graduation planning engine
   - Early graduation scenarios (3-3.5 years)
   - Graduation delay analysis for failed foundation courses
   - Course load calculators with success probabilities
   - Track-specific planning for MI and SE

3. **`ai_training_prompts.py`** - Comprehensive AI training system
   - System prompts with complete knowledge base
   - Clean response formatting (no markdown)
   - Context extraction and personalization templates

4. **`universal_purdue_advisor.py`** - Main interface (updated)
   - Integrates intelligent conversation manager
   - Session management and context building
   - Fallback to legacy system if needed

### Knowledge Base Files
1. **`data/cs_knowledge_graph.json`** - Enhanced comprehensive knowledge base
   - Complete course catalog with prerequisites
   - Graduation timelines and success probabilities
   - Course failure recovery scenarios
   - Track requirements (MI/SE)
   - CODO requirements
   - Course load guidelines by student year

2. **`intelligent_academic_advisor.py`** - Enhanced with graduation planning
   - Integrated with graduation planner
   - Track-specific guidance methods
   - Student profile management

### Testing & Validation
1. **`test_enhanced_ai.py`** - Comprehensive test suite
   - Multiple conversation scenarios
   - Memory and context testing
   - Different student profile comparisons

## Core Capabilities

### <¯ Graduation Planning
- **Early Graduation Analysis**: 3-year (40% success), 3.5-year (65% success), 4-year (85% success)
- **Course Load Optimization**: Freshman (max 2 CS), Sophomore+ (max 3 CS), Summer (max 2 CS)
- **Success Probability Calculations**: Based on GPA, course load, track difficulty
- **Timeline Adjustments**: For different scenarios and setbacks

### = Course Failure Recovery
- **Specific Impact Analysis**: For each foundation course (CS 18000, 18200, 24000, 25000, 25100, 25200)
- **Delay Calculations**: Semester delays and affected course chains
- **Summer Recovery Options**: Strategic course combinations for catch-up
- **Prerequisite Chain Analysis**: Understanding downstream impacts

### <“ Track Specialization
- **Machine Intelligence**: AI/ML focus, research preparation, data science careers
- **Software Engineering**: Industry development, project-based learning, large-scale systems
- **Career Alignment**: Connecting academic choices to career goals
- **Course Sequencing**: Optimal timing for track requirements

### > AI Intelligence Features
- **Context Extraction**: Automatically identifies student year, GPA, completed courses, goals
- **Conversation Memory**: Builds student profile across entire conversation
- **Personalized Responses**: Every response tailored to specific student situation
- **Natural Language**: Clean responses without markdown formatting
- **Intent Understanding**: Sophisticated query classification and routing

## Knowledge Base Coverage

### Course Information
- Complete CS course catalog with prerequisites
- Foundation sequence: CS 18000 ’ CS 18200 ’ CS 24000 ’ CS 25000/25100 ’ CS 25200
- Math sequence: MA 16100 ’ MA 16200 ’ MA 26100 + MA 26500
- Track courses for both MI and SE concentrations

### Requirements & Policies
- **CODO Requirements**: 2.75 GPA, CS 18000 with B+, Math with B+, space available
- **Graduation Requirements**: 120 credits total, 29 CS core, 12 track, 30 gen ed
- **Academic Policies**: Course load limits, retake policies, summer options

### Career Guidance
- Industry preparation for both tracks
- Graduate school preparation
- Internship guidance
- Programming language recommendations

## Usage Instructions

### Starting the System
```bash
cd /Users/rrao/Desktop/BCLI/my_cli_bot
python universal_purdue_advisor.py
```

### Testing the Enhanced AI
```bash
python test_enhanced_ai.py
```

### Key Methods in Code
- `conversation_manager.process_query(session_id, query)` - Main AI interface
- `graduation_planner.generate_comprehensive_plan(profile)` - Graduation planning
- `academic_advisor.analyze_early_graduation_feasibility(student)` - Early grad analysis
- `planner.analyze_foundation_delay_scenario(course, semester)` - Failure recovery

## Development Environment

### Dependencies
- Python 3.8+
- OpenAI API (for intelligent responses)
- NetworkX (for prerequisite graphs)
- SQLite3 (for data storage)
- JSON (for knowledge base)

### API Configuration
Set OpenAI API key: `export OPENAI_API_KEY='your-key-here'`

## Recent Improvements Made

### Response Quality Enhancement
- Removed all markdown formatting (**bold**, ## headers, ### subheaders)
- Implemented natural, conversational language
- Clean prose without formal structure
- Context-aware personalization

### AI Training Enhancement
- Comprehensive system prompts with complete knowledge
- Context extraction prompts for building student profiles
- Response generation prompts for personalization
- Clean formatting instructions

### Memory & Context System
- Session-based conversation tracking
- Student profile building across conversations
- Intent classification with conversation history
- Personalized response generation based on context

## Future Development Notes

### Potential Enhancements
1. Web interface for better user experience
2. Database integration for student tracking
3. Email notifications for important deadlines
4. Integration with Purdue's official systems
5. Mobile app development

### Maintenance Notes
- Update course information annually
- Monitor graduation requirement changes
- Refresh AI training prompts seasonally
- Test conversation quality regularly

## Testing Scenarios Validated

### Early Graduation Planning
- Sophomore wanting 3-year graduation with MI track
- High-achieving freshman with programming background
- Transfer student with community college credits

### Failure Recovery
- CS 25100 failure impacting graduation timeline
- Multiple foundation course failures
- Summer course recovery strategies

### Track Selection
- Career goal alignment with track choice
- Course comparison between MI and SE
- Industry vs. research preparation

### CODO Guidance
- GPA requirements and current standing
- Course completion tracking
- Application timing and process

## Success Metrics Achieved
-  No hardcoded responses - all personalized
-  Conversation memory and context building
-  Comprehensive graduation planning
-  Accurate failure recovery strategies
-  Track-specific career guidance
-  Clean, natural response formatting
-  Integration of all knowledge systems
-  Intelligent query understanding and routing

The Boiler AI system is complete and production-ready for Purdue CS academic advising with intelligent, personalized, and contextually-aware responses.