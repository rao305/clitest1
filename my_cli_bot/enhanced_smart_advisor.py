#!/usr/bin/env python3
"""
Enhanced Smart Academic Advisor
Integrates degree planner with enhanced session management and smart AI
"""

import os
from typing import Dict, List, Any, Optional
from degree_planner import StudentProgressTracker, DegreeTrackDatabase
from session_manager import SessionManager
from smart_ai_engine import SmartAIEngine
from feedback_system import FeedbackSystem
from knowledge_graph_academic_advisor import KnowledgeGraphAcademicAdvisor

class EnhancedSmartAdvisor:
    """Comprehensive academic advisor with degree planning capabilities"""
    
    def __init__(self):
        self.degree_planner = StudentProgressTracker()
        self.session_manager = SessionManager()
        self.smart_ai = SmartAIEngine()
        self.feedback_system = FeedbackSystem()
        self.kg_advisor = KnowledgeGraphAcademicAdvisor()
        
    def handle_academic_query(self, query: str, session_id: str = None, student_id: str = None) -> Dict[str, Any]:
        """Handle comprehensive academic queries with degree planning"""
        
        # Create session if needed
        if not session_id:
            session_id = self.session_manager.create_session(student_id)
        
        # Extract context from query
        query_context = self.session_manager.extract_context_from_query(query)
        conversation_context = self.session_manager.get_conversation_context(session_id)
        
        # Determine query type for specialized handling
        query_type = self._classify_advanced_query(query)
        
        # Handle degree planning queries
        if query_type in ['degree_planning', 'track_selection', 'semester_planning', 'graduation_requirements']:
            return self._handle_degree_planning_query(query, query_context, session_id, student_id)
        
        # Handle prerequisite queries with degree context
        elif query_type == 'prerequisites':
            return self._handle_prerequisite_query(query, query_context, session_id, student_id)
        
        # Handle course failure impact with specific timeline analysis
        elif query_type == 'course_failure':
            return self._handle_course_failure_query(query, query_context, session_id, student_id)
        
        # Handle course sequence planning
        elif query_type == 'course_sequence':
            return self._handle_course_sequence_query(query, query_context, session_id, student_id)
        
        # Handle career guidance with track integration
        elif query_type == 'career_guidance':
            return self._handle_career_guidance_query(query, query_context, session_id, student_id)
        
        # Default to smart AI with enhanced context
        else:
            return self._handle_general_query(query, query_context, conversation_context, session_id)
    
    def _classify_advanced_query(self, query: str) -> str:
        """Advanced query classification for degree planning features"""
        
        query_lower = query.lower()
        
        # Degree planning patterns
        if any(phrase in query_lower for phrase in [
            'degree plan', 'graduation plan', 'how to graduate', 'requirements to graduate',
            'what courses do i need', 'track requirements', 'how many courses'
        ]):
            return 'degree_planning'
        
        # Track selection patterns
        if any(phrase in query_lower for phrase in [
            'which track', 'track should i choose', 'mi or se', 'machine intelligence vs software engineering',
            'track comparison', 'best track for'
        ]):
            return 'track_selection'
        
        # Semester planning patterns
        if any(phrase in query_lower for phrase in [
            'next semester', 'semester plan', 'what should i take', 'course schedule',
            'fall courses', 'spring courses', 'course load'
        ]):
            return 'semester_planning'
        
        # Course sequence patterns
        if any(phrase in query_lower for phrase in [
            'course order', 'sequence', 'what comes after', 'progression',
            'roadmap', 'when should i take'
        ]):
            return 'course_sequence'
        
        # Prerequisites patterns
        if any(phrase in query_lower for phrase in [
            'prerequisite', 'prereq', 'before taking', 'requirements for'
        ]):
            return 'prerequisites'
        
        # Career guidance patterns
        if any(phrase in query_lower for phrase in [
            'career', 'job', 'internship', 'industry', 'salary', 'after graduation'
        ]):
            return 'career_guidance'
        
        # Course failure patterns (specific handling for CS 180 and others)
        if any(phrase in query_lower for phrase in [
            'failed cs 180', 'failed cs 18000', 'retake cs 180', 'cs 180 failure', 'failed 180',
            'failed a course', 'failing', 'need to retake', 'will i graduate on time',
            'more than 4 years', 'delayed graduation'
        ]):
            return 'course_failure'
        
        return 'general'
    
    def _handle_degree_planning_query(self, query: str, context: Dict, session_id: str, student_id: str) -> Dict[str, Any]:
        """Handle comprehensive degree planning queries"""
        
        # Check if student profile exists
        student_profile = None
        if student_id:
            student_profile = self.degree_planner.get_student_progress(student_id)
        
        # If no profile or incomplete info, guide through setup
        if not student_profile:
            return self._guide_student_setup(query, context, session_id)
        
        # Analyze degree requirements
        analysis = self.degree_planner.analyze_degree_requirements(student_id)
        
        if 'error' in analysis:
            return {
                'response': f"I need some information to help with your degree planning. {analysis['error']} Let me help you set this up. What's your current academic year and which track interests you?",
                'source': 'degree_planner',
                'session_id': session_id,
                'requires_followup': True
            }
        
        # Generate comprehensive degree planning response
        response = self._generate_degree_planning_response(analysis, query, context)
        
        # Update session
        self.session_manager.update_session(session_id, query, response, context)
        
        return {
            'response': response,
            'source': 'degree_planner',
            'session_id': session_id,
            'analysis': analysis,
            'student_profile': student_profile
        }
    
    def _handle_prerequisite_query(self, query: str, context: Dict, session_id: str, student_id: str) -> Dict[str, Any]:
        """Handle prerequisite queries with student progress context"""
        
        # Extract course from query
        mentioned_courses = context.get('mentioned_courses', [])
        
        if not mentioned_courses:
            return self._handle_general_query(query, context, "", session_id)
        
        course_code = mentioned_courses[0]
        
        # Get student progress if available
        student_profile = None
        if student_id:
            student_profile = self.degree_planner.get_student_progress(student_id)
        
        # Generate prerequisite response with context
        response = self._generate_prerequisite_response(course_code, student_profile, query)
        
        # Update session
        self.session_manager.update_session(session_id, query, response, context)
        
        return {
            'response': response,
            'source': 'prerequisite_analyzer',
            'session_id': session_id,
            'course_analyzed': course_code
        }
    
    def _handle_semester_planning_query(self, query: str, context: Dict, session_id: str, student_id: str) -> Dict[str, Any]:
        """Handle semester planning with personalized recommendations"""
        
        if not student_id:
            return {
                'response': "I'd love to help you plan your semester! To give you personalized recommendations, I need to know your current year and what courses you've completed. What's your academic status?",
                'source': 'semester_planner',
                'session_id': session_id,
                'requires_setup': True
            }
        
        # Get student profile
        student_profile = self.degree_planner.get_student_progress(student_id)
        
        if not student_profile:
            return self._guide_student_setup(query, context, session_id)
        
        # Generate semester plan
        semester_plan = self.degree_planner.generate_semester_plan(
            student_id, 
            "Fall 2025",  # Default to next semester
            max_credits=15
        )
        
        if 'error' in semester_plan:
            response = f"I'm having trouble generating your semester plan: {semester_plan['error']}. Let me help you update your profile first."
        else:
            response = self._generate_semester_plan_response(semester_plan, student_profile, query)
        
        # Update session
        self.session_manager.update_session(session_id, query, response, context)
        
        return {
            'response': response,
            'source': 'semester_planner',
            'session_id': session_id,
            'semester_plan': semester_plan if 'error' not in semester_plan else None
        }
    
    def _handle_career_guidance_query(self, query: str, context: Dict, session_id: str, student_id: str) -> Dict[str, Any]:
        """Handle career guidance with track-specific advice"""
        
        # Get student profile for personalized advice
        student_profile = None
        if student_id:
            student_profile = self.degree_planner.get_student_progress(student_id)
        
        # Determine track from context or profile
        track = None
        if context.get('track_interest'):
            track = context['track_interest']
        elif student_profile and student_profile.get('track'):
            track = student_profile['track']
        
        # Generate career guidance with track context
        career_context = {
            'query': query,
            'track': track,
            'academic_year': context.get('academic_year'),
            'student_profile': student_profile
        }
        
        response = self.smart_ai.generate_intelligent_response(query, career_context)['response']
        
        # Add track-specific career advice
        if track:
            response += self._add_track_specific_career_advice(track)
        
        # Update session
        self.session_manager.update_session(session_id, query, response, context)
        
        return {
            'response': response,
            'source': 'career_advisor',
            'session_id': session_id,
            'track_context': track
        }
    
    def _handle_general_query(self, query: str, context: Dict, conversation_context: str, session_id: str) -> Dict[str, Any]:
        """Handle general queries with enhanced context"""
        
        full_context = {
            'conversation_history': conversation_context,
            'query_context': context
        }
        
        response_data = self.smart_ai.generate_intelligent_response(query, full_context)
        
        # Update session
        self.session_manager.update_session(session_id, query, response_data['response'], context)
        
        return {
            'response': response_data['response'],
            'source': 'smart_ai_engine',
            'session_id': session_id,
            'provider': response_data.get('provider', 'Gemini_Gemini4o')
        }
    
    def _guide_student_setup(self, query: str, context: Dict, session_id: str) -> Dict[str, Any]:
        """Guide student through profile setup"""
        
        response = """I'd love to help you with your degree planning! To give you the most accurate and personalized advice, I need to set up your academic profile.

Let me ask a few quick questions:

1. What's your current academic year? (freshman, sophomore, junior, senior)
2. Which track are you interested in or have you chosen? (Machine Intelligence, Software Engineering, or others)
3. What CS courses have you completed so far?

Once I have this information, I can provide detailed degree planning, semester recommendations, and track-specific guidance tailored just for you!

What's your current academic year?"""
        
        # Update session with setup context
        setup_context = context.copy()
        setup_context['setup_required'] = True
        self.session_manager.update_session(session_id, query, response, setup_context)
        
        return {
            'response': response,
            'source': 'profile_setup',
            'session_id': session_id,
            'requires_setup': True
        }
    
    def _generate_degree_planning_response(self, analysis: Dict, query: str, context: Dict) -> str:
        """Generate comprehensive degree planning response"""
        
        student_id = analysis['student_id']
        track = analysis['track']
        graduation_status = analysis['graduation_readiness']
        
        response_parts = []
        
        # Graduation readiness overview
        if graduation_status['overall_complete']:
            response_parts.append("Congratulations! You've completed all requirements for graduation!")
        else:
            progress_pct = graduation_status.get('overall_percentage', 0)
            remaining_semesters = graduation_status.get('estimated_semesters_remaining', 1)
            
            response_parts.append(f"Great question about your degree progress! You're {progress_pct:.1f}% complete with your {track.replace('_', ' ').title()} track requirements.")
            response_parts.append(f"Based on your progress, you have approximately {remaining_semesters} semester(s) remaining until graduation.")
        
        # Foundation status
        foundation = analysis['foundation_status']
        if foundation['status'] == 'complete':
            response_parts.append("✅ Foundation courses: Complete! Great job finishing the core CS sequence.")
        else:
            remaining_count = len(foundation['remaining'])
            response_parts.append(f"📚 Foundation courses: {remaining_count} remaining ({', '.join(foundation['remaining'][:3])}{'...' if remaining_count > 3 else ''})")
        
        # Track requirements status
        track_reqs = analysis['track_requirements']
        
        # Core requirements
        if 'core_required' in track_reqs:
            core = track_reqs['core_required']
            if core['status'] == 'complete':
                response_parts.append(f"✅ {track.replace('_', ' ').title()} core courses: Complete!")
            else:
                response_parts.append(f"📋 {track.replace('_', ' ').title()} core remaining: {', '.join(core['remaining'])}")
        
        # Choice requirements
        for choice_key, choice_data in track_reqs.items():
            if choice_key.endswith('_choice') or choice_key == 'electives':
                if choice_data['status'] == 'complete':
                    response_parts.append(f"✅ {choice_key.replace('_', ' ').title()}: Complete!")
                else:
                    remaining = choice_data['remaining_count']
                    response_parts.append(f"🎯 {choice_key.replace('_', ' ').title()}: Choose {remaining} more course(s)")
        
        # Next steps
        response_parts.append("")
        response_parts.append("Would you like me to:")
        response_parts.append("• Create a personalized semester plan")
        response_parts.append("• Recommend specific courses for next semester")
        response_parts.append("• Explain any track requirements in detail")
        response_parts.append("• Compare different track options")
        
        return "\n".join(response_parts)
    
    def _generate_prerequisite_response(self, course_code: str, student_profile: Optional[Dict], query: str) -> str:
        """Generate prerequisite response with student context"""
        
        # Use smart AI to get course prerequisites
        prereq_query = f"What are the prerequisites for {course_code}?"
        prereq_response = self.smart_ai.generate_intelligent_response(prereq_query)['response']
        
        # Add personalized context if student profile available
        if student_profile and student_profile.get('completed_courses'):
            completed = student_profile['completed_courses']
            
            # Check if prerequisites are met
            # This would need actual prerequisite checking logic
            prereq_response += f"\n\nBased on your completed courses, I can help you determine if you're ready to take {course_code}. You've completed: {', '.join(completed[-5:])}{'...' if len(completed) > 5 else ''}"
        
        return prereq_response
    
    def _generate_semester_plan_response(self, semester_plan: Dict, student_profile: Dict, query: str) -> str:
        """Generate semester planning response"""
        
        recommended_courses = semester_plan['recommended_courses']
        total_credits = semester_plan['total_credits']
        reasoning = semester_plan.get('reasoning', [])
        
        response_parts = []
        response_parts.append(f"Perfect! Here's my personalized semester recommendation for you:")
        response_parts.append("")
        response_parts.append(f"📅 **Recommended Courses ({total_credits} credits):**")
        
        for course in recommended_courses:
            course_code = course['course']
            course_type = course['type']
            credits = course['credits']
            
            type_emoji = {
                'foundation': '📚',
                'core_required': '⭐',
                'choice': '🎯',
                'elective': '💡'
            }.get(course_type, '📖')
            
            response_parts.append(f"{type_emoji} {course_code} ({credits} credits) - {course_type.replace('_', ' ').title()}")
        
        # Add reasoning
        if reasoning:
            response_parts.append("")
            response_parts.append("🎯 **Why these courses:**")
            for reason in reasoning:
                response_parts.append(f"• {reason}")
        
        response_parts.append("")
        response_parts.append("Does this semester plan look good? I can adjust it based on your preferences or constraints!")
        
        return "\n".join(response_parts)
    
    def _add_track_specific_career_advice(self, track: str) -> str:
        """Add track-specific career advice"""
        
        career_advice = {
            'machine_intelligence': """

**🤖 Machine Intelligence Career Path:**
• **Top Companies**: Google, Microsoft, Meta, Gemini, Tesla
• **Average Starting Salary**: $90,000-120,000
• **Growing Fields**: LLMs, Computer Vision, Robotics, Data Science
• **Key Skills**: Python, TensorFlow/PyTorch, Statistics, Research Methods""",
            
            'software_engineering': """

**💻 Software Engineering Career Path:**
• **Top Companies**: Amazon, Google, Microsoft, Stripe, Airbnb
• **Average Starting Salary**: $85,000-115,000
• **Growing Fields**: Cloud Computing, DevOps, Mobile Apps, Web3
• **Key Skills**: System Design, Multiple Languages, Testing, Agile Methods"""
        }
        
        return career_advice.get(track, "")
    
    def _handle_course_failure_query(self, query: str, query_context: Dict, session_id: str, student_id: str = None) -> Dict[str, Any]:
        """Handle course failure queries with specific timeline analysis"""
        
        # Extract course from query
        course_mentioned = self._extract_course_from_query(query)
        
        if 'CS 180' in query.upper() or 'CS 18000' in query.upper():
            # Use knowledge graph advisor for specific CS 180 analysis
            failure_analysis = self.kg_advisor.analyze_cs180_failure_impact(
                failure_semester="freshman_fall"  # Default assumption
            )
            
            response = failure_analysis['specific_answer']
            
            # Update session with failure context
            self.session_manager.update_session(
                session_id, 
                query, 
                response, 
                {'course_failure': 'CS 18000', 'analysis_type': 'specific_timeline'}
            )
            
            return {
                'response': response,
                'source': 'knowledge_graph_advisor',
                'confidence': 0.95,
                'session_id': session_id,
                'analysis_data': failure_analysis
            }
        
        elif course_mentioned:
            # Use knowledge graph for any course failure analysis
            failure_analysis = self.kg_advisor.analyze_any_course_failure(
                course_code=course_mentioned,
                failure_semester="current"
            )
            
            response = failure_analysis['specific_answer']
            
            return {
                'response': response,
                'source': 'knowledge_graph_advisor',
                'confidence': 0.90,
                'session_id': session_id,
                'analysis_data': failure_analysis
            }
        
        else:
            # General failure guidance
            response = """I understand you're concerned about course failure and graduation timeline. To give you the most accurate guidance, could you tell me:

• Which specific course are you concerned about?
• What semester did you take (or plan to take) this course?
• Are you currently passing your other courses?

With these details, I can provide a specific analysis of how this affects your graduation timeline and create a recovery plan tailored to your situation."""
            
            return {
                'response': response,
                'source': 'enhanced_advisor_general',
                'confidence': 0.85,
                'session_id': session_id
            }
    
    def _extract_course_from_query(self, query: str) -> str:
        """Extract course code from query"""
        
        import re
        
        # Look for CS course patterns
        cs_pattern = r'CS\s*(\d{5}|\d{3})'
        match = re.search(cs_pattern, query.upper())
        
        if match:
            course_num = match.group(1)
            if len(course_num) == 3:
                return f"CS {course_num}00"
            else:
                return f"CS {course_num}"
        
        # Look for specific course mentions
        course_mentions = {
            '180': 'CS 18000',
            '182': 'CS 18200', 
            '240': 'CS 24000',
            '250': 'CS 25000',
            '251': 'CS 25100',
            '252': 'CS 25200',
            '381': 'CS 38100'
        }
        
        for short_code, full_code in course_mentions.items():
            if short_code in query:
                return full_code
        
        return None

if __name__ == "__main__":
    # Test enhanced smart advisor
    advisor = EnhancedSmartAdvisor()
    
    # Test queries
    test_queries = [
        "I'm a sophomore interested in machine learning. What should I take next semester?",
        "What are the graduation requirements for the MI track?",
        "Can you help me plan my degree to graduate on time?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = advisor.handle_academic_query(query)
        print(f"Response: {response['response'][:200]}...")
        print(f"Source: {response['source']}")