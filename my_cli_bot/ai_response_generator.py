#!/usr/bin/env python3
"""
AI-Powered Response Generator for Boiler AI

Eliminates hardcoded messages and templates by generating all responses
dynamically using AI and the knowledge base.
"""

import json
from typing import Dict, List, Any, Optional
from smart_ai_engine import SmartAIEngine

class AIResponseGenerator:
    """
    Generates all responses dynamically using AI instead of hardcoded templates
    """
    
    def __init__(self, knowledge_file: str):
        """Initialize with knowledge base"""
        with open(knowledge_file, 'r') as f:
            self.knowledge_base = json.load(f)
        
        self.ai_engine = SmartAIEngine()
        
        # Context templates for different types of responses
        self.response_contexts = {
            "greeting": {
                "role": "friendly academic advisor",
                "tone": "welcoming and helpful",
                "purpose": "introduce capabilities and invite questions"
            },
            "course_planning": {
                "role": "knowledgeable course advisor", 
                "tone": "informative and encouraging",
                "purpose": "provide specific course guidance"
            },
            "graduation_planning": {
                "role": "strategic graduation planner",
                "tone": "detailed and organized", 
                "purpose": "create comprehensive graduation roadmaps"
            },
            "track_selection": {
                "role": "career-focused track advisor",
                "tone": "comparative and insightful",
                "purpose": "help choose the best academic track"
            },
            "course_selection": {
                "role": "course selection specialist",
                "tone": "explanatory and supportive",
                "purpose": "present course options with clear benefits"
            },
            "error_handling": {
                "role": "helpful problem solver",
                "tone": "understanding and solution-focused",
                "purpose": "acknowledge issues and provide alternatives"
            }
        }
    
    def generate_greeting_response(self, context: Dict[str, Any] = None) -> str:
        """Generate a personalized greeting"""
        
        prompt = f"""
        You are a friendly Purdue CS academic advisor AI. Generate a warm, personalized greeting.
        
        Context: {context or {}}
        Knowledge: You have comprehensive knowledge of {len(self.knowledge_base.get('courses', {}))} CS courses, tracks, and requirements.
        
        Guidelines:
        - Be welcoming and helpful
        - Mention your key capabilities (course planning, graduation planning, track selection)
        - Invite them to ask questions
        - Keep it conversational and encouraging
        - Don't use bullet points or formal formatting
        """
        
        return self._generate_response(prompt, "greeting", context)
    
    def generate_course_planning_response(self, query: str, context: Dict[str, Any], 
                                        extracted_info: Dict[str, Any]) -> str:
        """Generate course planning advice"""
        
        # Get relevant courses from knowledge base
        relevant_courses = self._get_relevant_courses(query, extracted_info)
        
        prompt = f"""
        You are a knowledgeable Purdue CS course advisor. A student is asking about course planning.
        
        Student Query: "{query}"
        Student Context: {context}
        Extracted Info: {extracted_info}
        Relevant Courses Available: {relevant_courses}
        
        Guidelines:
        - Provide specific, actionable course advice
        - Reference actual course codes and prerequisites
        - Consider their current progress and goals
        - Be encouraging and supportive
        - Explain the reasoning behind recommendations
        - Keep response conversational, not bullet-pointed
        """
        
        return self._generate_response(prompt, "course_planning", context)
    
    def generate_graduation_planning_response(self, student_profile: Dict[str, Any], 
                                            plan_type: str = "standard") -> str:
        """Generate graduation planning guidance"""
        
        major = student_profile.get('major', 'Computer Science')
        track = student_profile.get('track', '')
        completed = student_profile.get('completed_courses', [])
        
        prompt = f"""
        You are a strategic graduation planner for Purdue students. A student needs graduation planning help.
        
        Student Profile:
        - Major: {major}
        - Track: {track}
        - Completed Courses: {len(completed)} courses
        - Current Year: {student_profile.get('current_year', 'unknown')}
        - Goals: {student_profile.get('graduation_goal', 'standard timeline')}
        
        Plan Type: {plan_type}
        Available Knowledge: {self._get_relevant_requirements(major, track)}
        
        Guidelines:
        - Create a comprehensive graduation roadmap
        - Account for their specific progress and goals
        - Explain semester-by-semester planning approach
        - Address any challenges or opportunities
        - Be detailed but encouraging
        - Use natural, conversational language
        """
        
        return self._generate_response(prompt, "graduation_planning", student_profile)
    
    def generate_track_selection_response(self, query: str, context: Dict[str, Any]) -> str:
        """Generate track comparison and selection advice"""
        
        track_info = self._get_track_information()
        
        prompt = f"""
        You are a career-focused track advisor at Purdue CS. A student is asking about track selection.
        
        Student Query: "{query}"
        Student Context: {context}
        Track Information Available: {track_info}
        
        Guidelines:
        - Compare tracks based on courses, career outcomes, and student interests
        - Explain the practical differences between tracks
        - Help them understand which aligns with their goals
        - Be insightful and comparative
        - Use specific examples and outcomes
        - Keep it conversational and engaging
        """
        
        return self._generate_response(prompt, "track_selection", context)
    
    def generate_course_choice_request(self, choice_options: Dict[str, Any], 
                                     student_profile: Dict[str, Any]) -> str:
        """Generate interactive course selection request"""
        
        prompt = f"""
        You are a course selection specialist. A student needs to choose between course options for their degree plan.
        
        Student Profile: {student_profile}
        Course Choices Needed: {choice_options}
        
        Guidelines:
        - Present the choices clearly and engagingly
        - Explain why each choice matters for their career goals
        - Highlight the benefits and differences of each option
        - Make it easy for them to understand and respond
        - Be encouraging and supportive of their decision-making
        - Ask them to share their preferences so you can create their final plan
        - Keep it conversational, not formal or templated
        """
        
        return self._generate_response(prompt, "course_selection", student_profile)
    
    def generate_error_response(self, error_context: str, suggested_alternatives: List[str] = None) -> str:
        """Generate helpful error handling response"""
        
        prompt = f"""
        You are a helpful problem solver for Purdue CS academic advising. Something didn't work as expected.
        
        Error Context: {error_context}
        Suggested Alternatives: {suggested_alternatives or []}
        
        Guidelines:
        - Acknowledge the issue without being overly apologetic
        - Provide helpful alternatives or next steps
        - Maintain a positive, solution-focused tone
        - Offer to help in other ways
        - Keep it brief but supportive
        - Don't make excuses, just focus on moving forward
        """
        
        return self._generate_response(prompt, "error_handling", {"error": error_context})
    
    def generate_followup_response(self, original_query: str, context: Dict[str, Any], 
                                 additional_info_needed: List[str]) -> str:
        """Generate follow-up question response"""
        
        prompt = f"""
        You are a thorough academic advisor. A student asked a question, but you need more information to help them properly.
        
        Original Query: "{original_query}"
        Student Context: {context}
        Additional Info Needed: {additional_info_needed}
        
        Guidelines:
        - Acknowledge their question positively
        - Explain why you need additional information
        - Ask for the specific details you need
        - Frame questions in a helpful, non-overwhelming way
        - Show enthusiasm for helping once you have the details
        - Keep it conversational and encouraging
        """
        
        return self._generate_response(prompt, "course_planning", context)
    
    def _generate_response(self, prompt: str, response_type: str, context: Dict[str, Any]) -> str:
        """Generate AI response with appropriate context"""
        
        response_context = self.response_contexts.get(response_type, self.response_contexts["course_planning"])
        
        full_prompt = f"""
        {prompt}
        
        Response Requirements:
        - Act as a {response_context['role']}
        - Use a {response_context['tone']} tone
        - {response_context['purpose']}
        - Be natural and conversational (no bullet points or formal formatting)
        - Base responses on actual knowledge, not generic advice
        - Reference specific Purdue CS information where relevant
        - Keep responses helpful and actionable
        """
        
        try:
            response = self.ai_engine.generate_smart_response(full_prompt, context or {})
            return response
        except Exception as e:
            # Fallback for when AI is not available
            return self._generate_fallback_response(response_type, context)
    
    def _generate_fallback_response(self, response_type: str, context: Dict[str, Any]) -> str:
        """Generate fallback response when AI is unavailable"""
        
        fallbacks = {
            "greeting": "Hello! I'm your Purdue CS academic advisor. I'm here to help with course planning, graduation timelines, track selection, and any CS-related questions you have. What would you like to know?",
            "course_planning": "I'd be happy to help with your course planning. Could you tell me more about your current situation and what specifically you're looking for guidance on?",
            "graduation_planning": "Let me help you create a graduation plan. I'll need to know more about your current progress and goals to give you the best advice.",
            "track_selection": "Both the Machine Intelligence and Software Engineering tracks have great opportunities. Let me help you understand which might be the best fit for your goals.",
            "course_selection": "You have some great course options to choose from. Let me present them clearly so you can make the best decision for your academic and career goals.",
            "error_handling": "I encountered an issue, but I'm still here to help! Let me try a different approach to assist you with your question."
        }
        
        return fallbacks.get(response_type, "I'm here to help with your Purdue CS questions. What would you like to know?")
    
    def _get_relevant_courses(self, query: str, extracted_info: Dict[str, Any]) -> Dict:
        """Get relevant courses from knowledge base"""
        
        courses = self.knowledge_base.get('courses', {})
        
        # Filter courses based on query and student info
        relevant = {}
        query_lower = query.lower()
        current_year = extracted_info.get('current_year', 'freshman')
        
        for course_id, course_info in courses.items():
            # Include foundation courses for early students
            if current_year in ['freshman', 'sophomore'] and course_id.startswith('CS 1') or course_id.startswith('CS 2'):
                relevant[course_id] = course_info
            # Include advanced courses for later students
            elif current_year in ['junior', 'senior'] and (course_id.startswith('CS 3') or course_id.startswith('CS 4')):
                relevant[course_id] = course_info
            # Include if mentioned in query
            elif course_id.lower() in query_lower or any(keyword in query_lower for keyword in course_info.get('keywords', [])):
                relevant[course_id] = course_info
        
        return relevant
    
    def _get_relevant_requirements(self, major: str, track: str) -> Dict:
        """Get relevant degree requirements"""
        
        requirements = {}
        
        # Get major-specific requirements
        if major in self.knowledge_base:
            requirements['major_info'] = self.knowledge_base[major]
        
        # Get track-specific information
        tracks = self.knowledge_base.get('tracks', {})
        if track in tracks:
            requirements['track_info'] = tracks[track]
        
        return requirements
    
    def _get_track_information(self) -> Dict:
        """Get comprehensive track information"""
        
        tracks = self.knowledge_base.get('tracks', {})
        
        # Add career outcome information
        track_careers = {
            'Machine Intelligence': {
                'careers': ['Data Scientist', 'ML Engineer', 'AI Researcher', 'Software Engineer'],
                'skills': ['Python', 'Machine Learning', 'Statistics', 'Data Analysis'],
                'industries': ['Tech', 'Healthcare', 'Finance', 'Research']
            },
            'Software Engineering': {
                'careers': ['Software Engineer', 'Systems Architect', 'DevOps Engineer', 'Product Manager'],
                'skills': ['Java', 'System Design', 'Project Management', 'Software Architecture'],
                'industries': ['Tech', 'Startups', 'Enterprise', 'Consulting']
            }
        }
        
        # Combine track info with career info
        enhanced_tracks = {}
        for track_name, track_info in tracks.items():
            enhanced_tracks[track_name] = {
                **track_info,
                **track_careers.get(track_name, {})
            }
        
        return enhanced_tracks

def main():
    """Test the AI response generator"""
    
    generator = AIResponseGenerator("data/cs_knowledge_graph.json")
    
    # Test greeting
    print("=== Greeting Test ===")
    greeting = generator.generate_greeting_response()
    print(greeting)
    
    # Test course planning
    print("\n=== Course Planning Test ===")
    course_response = generator.generate_course_planning_response(
        "What courses should I take as a sophomore?",
        {"current_year": "sophomore"},
        {"current_year": "sophomore", "completed_courses": ["CS 18000"]}
    )
    print(course_response)
    
    # Test track selection
    print("\n=== Track Selection Test ===")
    track_response = generator.generate_track_selection_response(
        "Should I choose MI or SE track?",
        {"interests": ["AI", "software development"]}
    )
    print(track_response)

if __name__ == "__main__":
    main()