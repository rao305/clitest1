#!/usr/bin/env python3
"""
Enhanced NLP Engine for Perfect Purdue CS Understanding
Advanced natural language processing for precise intent recognition and entity extraction
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import google.generativeai as genai
from dataclasses import dataclass

@dataclass
class StudentContext:
    """Student context extracted from conversation"""
    current_year: Optional[str] = None
    current_semester: Optional[str] = None
    gpa: Optional[float] = None
    completed_courses: List[str] = None
    current_courses: List[str] = None
    failed_courses: List[str] = None
    target_track: Optional[str] = None
    career_goal: Optional[str] = None
    graduation_target: Optional[str] = None
    concerns: List[str] = None
    
    def __post_init__(self):
        if self.completed_courses is None:
            self.completed_courses = []
        if self.current_courses is None:
            self.current_courses = []
        if self.failed_courses is None:
            self.failed_courses = []
        if self.concerns is None:
            self.concerns = []

@dataclass
class QueryIntent:
    """Structured query intent"""
    primary_intent: str
    secondary_intents: List[str]
    confidence: float
    entities: Dict[str, List[str]]
    context_requirements: List[str]
    complexity_level: str  # 'simple', 'moderate', 'complex'

class EnhancedNLPEngine:
    def __init__(self):
        self.gemini_model = Gemini.Gemini()
        
        # Advanced intent patterns with semantic understanding
        self.intent_patterns = {
            'course_inquiry': {
                'patterns': [
                    r'what is (cs|math|stat|phys|engr)\s*\d+',
                    r'tell me about (cs|math|stat|phys|engr)\s*\d+',
                    r'describe (cs|math|stat|phys|engr)\s*\d+',
                    r'(cs|math|stat|phys|engr)\s*\d+ description',
                    r'course information for',
                    r'details about.*course'
                ],
                'semantic_keywords': ['course', 'class', 'subject', 'learn', 'study', 'covers', 'about'],
                'complexity_indicators': ['comparison', 'vs', 'versus', 'difference', 'similar']
            },
            'prerequisite_analysis': {
                'patterns': [
                    r'prerequisites? for',
                    r'what do i need for',
                    r'requirements for',
                    r'what comes before',
                    r'path to take',
                    r'sequence for'
                ],
                'semantic_keywords': ['prerequisite', 'requirement', 'need', 'before', 'first', 'sequence', 'path'],
                'complexity_indicators': ['complete chain', 'all prerequisites', 'full path']
            },
            'degree_planning': {
                'patterns': [
                    r'graduation plan',
                    r'degree plan',
                    r'course schedule',
                    r'semester plan',
                    r'when will i graduate',
                    r'how long until',
                    r'graduation timeline'
                ],
                'semantic_keywords': ['graduation', 'degree', 'schedule', 'plan', 'timeline', 'semester'],
                'complexity_indicators': ['custom', 'personalized', 'optimized', 'fastest', 'alternative']
            },
            'course_failure_recovery': {
                'patterns': [
                    r'failed (cs|math|stat|phys)\s*\d+',
                    r'failing.*course',
                    r'retake.*course',
                    r'what if i fail',
                    r'course failure',
                    r'bad grade'
                ],
                'semantic_keywords': ['failed', 'fail', 'retake', 'repeat', 'bad', 'poor', 'struggle'],
                'complexity_indicators': ['multiple', 'several', 'many', 'all', 'worst case']
            },
            'codo_guidance': {
                'patterns': [
                    r'codo into cs',
                    r'change.*major',
                    r'switch.*computer science',
                    r'transfer.*cs',
                    r'get into cs',
                    r'cs admission'
                ],
                'semantic_keywords': ['codo', 'change', 'switch', 'transfer', 'admission', 'major'],
                'complexity_indicators': ['eligibility', 'chances', 'probability', 'timeline']
            },
            'track_selection': {
                'patterns': [
                    r'(machine intelligence|mi) track',
                    r'(software engineering|se) track',
                    r'systems track',
                    r'which track',
                    r'track requirements',
                    r'track comparison'
                ],
                'semantic_keywords': ['track', 'specialization', 'focus', 'concentration', 'area'],
                'complexity_indicators': ['comparison', 'vs', 'best for', 'career alignment']
            },
            'career_guidance': {
                'patterns': [
                    r'career options',
                    r'job prospects',
                    r'internship',
                    r'after graduation',
                    r'industry',
                    r'work in'
                ],
                'semantic_keywords': ['career', 'job', 'work', 'internship', 'industry', 'profession'],
                'complexity_indicators': ['path', 'preparation', 'requirements', 'timeline']
            },
            'academic_policies': {
                'patterns': [
                    r'gpa requirement',
                    r'academic probation',
                    r'withdrawal',
                    r'add.*drop',
                    r'academic policy'
                ],
                'semantic_keywords': ['policy', 'rule', 'requirement', 'regulation', 'procedure'],
                'complexity_indicators': ['exceptions', 'special cases', 'appeals']
            }
        }
        
        # Entity extraction patterns
        self.entity_patterns = {
            'courses': r'\b([A-Z]{2,4})\s*(\d{5}|\d{3})\b',
            'gpa': r'(?:gpa|grade point average)[:\s]*(\d\.\d+)|(\d\.\d+)\s*gpa',
            'year_level': r'\b(freshman|sophomore|junior|senior|first year|second year|third year|fourth year)\b',
            'semester': r'\b(fall|spring|summer)\s*(?:semester|term)?\s*(?:20\d{2})?\b',
            'track': r'\b(machine intelligence|mi|software engineering|se|systems?|security|computer graphics|theoretical)\s*(?:track|specialization|concentration)?\b',
            'timeline': r'\b(\d+)\s*(?:years?|semesters?|months?)\b',
            'career_goals': r'\b(software engineer|data scientist|ai engineer|machine learning|cybersecurity|web developer|game developer|researcher)\b'
        }
        
        # Contextual understanding patterns
        self.context_indicators = {
            'uncertainty': ['not sure', 'confused', 'unclear', 'don\'t know', 'uncertain'],
            'urgency': ['urgent', 'asap', 'quickly', 'immediate', 'deadline', 'time sensitive'],
            'comparison_request': ['vs', 'versus', 'compare', 'difference', 'which is better', 'pros and cons'],
            'personalization_needed': ['my situation', 'for me', 'in my case', 'personally', 'given my'],
            'planning_horizon': ['next semester', 'next year', 'graduation', 'long term', 'future']
        }
    
    def analyze_query(self, query: str, conversation_history: List[Dict] = None) -> Tuple[QueryIntent, StudentContext]:
        """
        Perform comprehensive query analysis with semantic understanding
        """
        query_lower = query.lower().strip()
        
        # Extract student context from query and history
        student_context = self.extract_student_context(query, conversation_history)
        
        # Determine primary intent using pattern matching + AI
        primary_intent = self.classify_primary_intent(query_lower)
        secondary_intents = self.identify_secondary_intents(query_lower)
        
        # Extract entities with semantic understanding
        entities = self.extract_entities_semantic(query_lower)
        
        # Assess complexity level
        complexity = self.assess_complexity(query_lower, entities)
        
        # Determine context requirements
        context_requirements = self.identify_context_requirements(query_lower, entities)
        
        # Calculate confidence based on pattern matches and entity extraction
        confidence = self.calculate_confidence(primary_intent, entities, query_lower)
        
        intent = QueryIntent(
            primary_intent=primary_intent,
            secondary_intents=secondary_intents,
            confidence=confidence,
            entities=entities,
            context_requirements=context_requirements,
            complexity_level=complexity
        )
        
        return intent, student_context
    
    def classify_primary_intent(self, query: str) -> str:
        """Classify primary intent using patterns and semantic analysis"""
        best_match = "general_inquiry"
        best_score = 0
        
        for intent, config in self.intent_patterns.items():
            score = 0
            
            # Pattern matching
            for pattern in config['patterns']:
                if re.search(pattern, query, re.IGNORECASE):
                    score += 3
            
            # Semantic keyword matching
            for keyword in config['semantic_keywords']:
                if keyword in query:
                    score += 1
            
            # Complexity indicators
            for indicator in config.get('complexity_indicators', []):
                if indicator in query:
                    score += 0.5
            
            if score > best_score:
                best_score = score
                best_match = intent
        
        return best_match
    
    def identify_secondary_intents(self, query: str) -> List[str]:
        """Identify secondary/related intents"""
        secondary = []
        
        # Look for multiple intent indicators
        for intent, config in self.intent_patterns.items():
            score = 0
            for pattern in config['patterns']:
                if re.search(pattern, query, re.IGNORECASE):
                    score += 1
            
            if score > 0:
                secondary.append(intent)
        
        return secondary[1:]  # Exclude primary intent
    
    def extract_entities_semantic(self, query: str) -> Dict[str, List[str]]:
        """Extract entities with semantic understanding"""
        entities = {
            'courses': [],
            'gpa': [],
            'year_level': [],
            'semester': [],
            'track': [],
            'timeline': [],
            'career_goals': [],
            'concerns': []
        }
        
        # Extract using patterns
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.finditer(pattern, query, re.IGNORECASE)
            for match in matches:
                if entity_type == 'courses':
                    # Combine subject and number
                    course = f"{match.group(1).upper()} {match.group(2)}"
                    entities[entity_type].append(course)
                elif entity_type == 'gpa':
                    # Extract GPA value
                    gpa_val = match.group(1) or match.group(2)
                    if gpa_val:
                        entities[entity_type].append(float(gpa_val))
                else:
                    entities[entity_type].append(match.group().strip())
        
        # Extract concerns and emotions
        concern_indicators = ['worried', 'concerned', 'anxious', 'stressed', 'behind', 'struggling']
        for indicator in concern_indicators:
            if indicator in query:
                entities['concerns'].append(indicator)
        
        return entities
    
    def extract_student_context(self, query: str, history: List[Dict] = None) -> StudentContext:
        """Extract comprehensive student context"""
        context = StudentContext()
        
        query_lower = query.lower()
        
        # Extract from current query
        entities = self.extract_entities_semantic(query_lower)
        
        if entities['year_level']:
            context.current_year = entities['year_level'][0]
        if entities['gpa']:
            context.gpa = entities['gpa'][0]
        if entities['track']:
            context.target_track = entities['track'][0]
        if entities['career_goals']:
            context.career_goal = entities['career_goals'][0]
        if entities['concerns']:
            context.concerns = entities['concerns']
        
        # Extract courses mentioned
        if entities['courses']:
            # Determine if courses are completed, current, or failed based on context
            if any(word in query_lower for word in ['failed', 'failing', 'retake']):
                context.failed_courses.extend(entities['courses'])
            elif any(word in query_lower for word in ['took', 'completed', 'finished', 'passed']):
                context.completed_courses.extend(entities['courses'])
            elif any(word in query_lower for word in ['taking', 'enrolled', 'current']):
                context.current_courses.extend(entities['courses'])
        
        # Extract from conversation history if available
        if history:
            for exchange in history[-5:]:  # Last 5 exchanges
                if 'user' in exchange:
                    hist_entities = self.extract_entities_semantic(exchange['user'].lower())
                    # Merge historical context
                    if not context.current_year and hist_entities['year_level']:
                        context.current_year = hist_entities['year_level'][0]
                    if not context.gpa and hist_entities['gpa']:
                        context.gpa = hist_entities['gpa'][0]
        
        return context
    
    def assess_complexity(self, query: str, entities: Dict) -> str:
        """Assess query complexity level"""
        complexity_score = 0
        
        # Multiple courses mentioned
        if len(entities.get('courses', [])) > 1:
            complexity_score += 1
        
        # Multiple intents
        intent_count = sum(1 for intent_config in self.intent_patterns.values() 
                          if any(re.search(pattern, query, re.IGNORECASE) 
                                for pattern in intent_config['patterns']))
        if intent_count > 1:
            complexity_score += 1
        
        # Complexity indicators
        complex_indicators = ['all', 'everything', 'complete', 'comprehensive', 'optimal', 'best', 'comparison']
        if any(indicator in query for indicator in complex_indicators):
            complexity_score += 1
        
        # Conditional statements
        if any(word in query for word in ['if', 'what if', 'suppose', 'assuming']):
            complexity_score += 1
        
        if complexity_score >= 3:
            return 'complex'
        elif complexity_score >= 1:
            return 'moderate'
        else:
            return 'simple'
    
    def identify_context_requirements(self, query: str, entities: Dict) -> List[str]:
        """Identify what context is needed for optimal response"""
        requirements = []
        
        # Check for personalization indicators
        if any(indicator in query for indicator in self.context_indicators['personalization_needed']):
            requirements.extend(['student_profile', 'academic_history', 'goals'])
        
        # Check for planning horizon
        if any(indicator in query for indicator in self.context_indicators['planning_horizon']):
            requirements.append('timeline_preferences')
        
        # Check for comparison requests
        if any(indicator in query for indicator in self.context_indicators['comparison_request']):
            requirements.append('decision_criteria')
        
        # Course-specific context
        if entities.get('courses'):
            requirements.append('course_history')
        
        # Track-specific context
        if entities.get('track') or 'track' in query:
            requirements.append('career_alignment')
        
        return list(set(requirements))
    
    def calculate_confidence(self, intent: str, entities: Dict, query: str) -> float:
        """Calculate confidence in intent classification"""
        confidence = 0.5  # Base confidence
        
        # High confidence for strong pattern matches
        if intent in self.intent_patterns:
            pattern_matches = sum(1 for pattern in self.intent_patterns[intent]['patterns']
                                if re.search(pattern, query, re.IGNORECASE))
            confidence += min(0.3, pattern_matches * 0.1)
        
        # Boost for entity extraction
        entity_count = sum(len(entity_list) for entity_list in entities.values())
        confidence += min(0.2, entity_count * 0.05)
        
        # Reduce for ambiguous queries
        if len(query.split()) < 3:
            confidence -= 0.1
        
        return min(1.0, max(0.1, confidence))
    
    def enhance_with_ai_understanding(self, query: str, initial_analysis: Tuple[QueryIntent, StudentContext]) -> Tuple[QueryIntent, StudentContext]:
        """Use AI to enhance understanding of complex queries"""
        intent, context = initial_analysis
        
        if intent.complexity_level == 'complex' or intent.confidence < 0.7:
            try:
                # Use AI for deeper understanding
                prompt = f"""
                Analyze this Purdue CS student query for precise intent and context:
                
                Query: "{query}"
                
                Extract:
                1. Primary intent (course_inquiry, prerequisite_analysis, degree_planning, etc.)
                2. Student context (year, GPA, courses, concerns)
                3. Specific requirements for optimal response
                4. Complexity level and confidence
                
                Respond in JSON format.
                """
                
                response = self.gemini_model.generate_content(
                    ,
                    prompt,
                    ,
                    
                )
                
                ai_analysis = json.loads(response.text)
                
                # Merge AI insights with pattern-based analysis
                if ai_analysis.get('confidence', 0) > intent.confidence:
                    intent.primary_intent = ai_analysis.get('primary_intent', intent.primary_intent)
                    intent.confidence = max(intent.confidence, ai_analysis.get('confidence', intent.confidence))
                
            except Exception as e:
                print(f"AI enhancement error: {e}")
        
        return intent, context

def main():
    """Test the enhanced NLP engine"""
    nlp = EnhancedNLPEngine()
    
    test_queries = [
        "I failed CS 180 and CS 182, can I still graduate on time?",
        "What's the best track for AI careers and what courses do I need?",
        "I'm a sophomore with a 2.8 GPA, what are my CODO chances?",
        "Compare Machine Intelligence vs Software Engineering tracks for someone interested in machine learning",
        "I need to plan my remaining semesters to graduate by Spring 2026"
    ]
    
    print("🧠 Enhanced NLP Engine - Testing")
    print("=" * 60)
    
    for query in test_queries:
        intent, context = nlp.analyze_query(query)
        print(f"\nQuery: {query}")
        print(f"Intent: {intent.primary_intent} (confidence: {intent.confidence:.2f})")
        print(f"Complexity: {intent.complexity_level}")
        print(f"Entities: {intent.entities}")
        print(f"Context: {context}")
        print("-" * 40)

if __name__ == "__main__":
    main()