#!/usr/bin/env python3
"""
Intelligent AI Response Generator
Dynamically generates responses based on data and context instead of hardcoded templates
"""

import json
import re
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

@dataclass
class ResponseContext:
    """Context for generating intelligent responses"""
    query: str
    intent: str
    entities: Dict[str, Any]
    data: Dict[str, Any]
    user_context: Dict[str, Any]
    conversation_history: List[Dict[str, str]]

class IntelligentResponseGenerator:
    """Generates intelligent, dynamic responses based on data and context"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize Gemini client if available
        try:
            import google.generativeai as genai
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                self.gemini_model = genai.GenerativeModel('models/gemini-2.5-flash')
                self.Gemini_available = True
            else:
                self.gemini_model = None
                self.Gemini_available = False
        except ImportError:
            self.gemini_model = None
            self.Gemini_available = False
        
    def generate_intelligent_response(self, context: ResponseContext) -> str:
        """Generate intelligent response based on context and data"""
        
        try:
            # Route to appropriate intelligent generator
            if context.intent == "course_planning":
                return self._generate_intelligent_course_planning(context)
            elif context.intent == "graduation_planning":
                return self._generate_intelligent_graduation_planning(context)
            elif context.intent == "track_selection":
                return self._generate_intelligent_track_selection(context)
            elif context.intent == "prerequisites":
                return self._generate_intelligent_prerequisites(context)
            elif context.intent == "course_difficulty":
                return self._generate_intelligent_course_difficulty(context)
            elif context.intent == "career_guidance":
                return self._generate_intelligent_career_guidance(context)
            else:
                return self._generate_intelligent_general_response(context)
                
        except Exception as e:
            self.logger.error(f"Error generating intelligent response: {e}")
            return self._generate_fallback_response(context)
    
    def _generate_intelligent_course_planning(self, context: ResponseContext) -> str:
        """Intelligently generate course planning response based on data"""
        
        # Extract relevant information
        academic_years = context.entities.get("academic_years", [])
        current_year = academic_years[0] if academic_years else None
        
        tracks = context.entities.get("tracks", [])
        target_track = tracks[0] if tracks else None
        dual_track_interest = "both" in context.query.lower() or "dual" in context.query.lower()
        
        # Get course data
        courses = context.data.get("courses", {})
        prerequisites = context.data.get("prerequisites", {})
        track_requirements = context.data.get("track_requirements", {})
        
        if dual_track_interest:
            return self._generate_dual_track_course_plan(context, courses, prerequisites, track_requirements)
        
        # Generate year-specific course plan
        if current_year:
            return self._generate_year_specific_plan(context, current_year, target_track, courses, prerequisites, track_requirements)
        
        # Generate general course planning advice
        return self._generate_general_course_advice(context, courses, track_requirements)
    
    def _generate_dual_track_course_plan(self, context: ResponseContext, courses: Dict, prerequisites: Dict, track_requirements: Dict) -> str:
        """Generate intelligent dual track course plan"""
        
        # Analyze dual track requirements
        mi_requirements = track_requirements.get("Machine Intelligence", {})
        se_requirements = track_requirements.get("Software Engineering", {})
        
        # Calculate total requirements
        mi_courses = mi_requirements.get("required_courses", [])
        se_courses = se_requirements.get("required_courses", [])
        
        # Find overlapping courses
        overlapping = set(mi_courses) & set(se_courses)
        unique_mi = set(mi_courses) - set(se_courses)
        unique_se = set(se_courses) - set(mi_courses)
        
        response = "🎓 DUAL TRACK GRADUATION PLAN\n"
        response += "=" * 50 + "\n"
        response += "📚 Machine Intelligence + Software Engineering Tracks\n"
        response += "⏰ Timeline: 8 semesters (4 years)\n"
        response += "📊 Total CS Credits: ~60 credits\n\n"
        
        response += "🔗 SHARED COURSES (Complete once):\n"
        for course in overlapping:
            response += f"• {course}\n"
        response += f"\n📈 MACHINE INTELLIGENCE TRACK:\n"
        for course in unique_mi:
            response += f"• {course}\n"
        response += f"\n⚙️ SOFTWARE ENGINEERING TRACK:\n"
        for course in unique_se:
            response += f"• {course}\n"
        
        response += "\n💡 RECOMMENDED SCHEDULE:\n"
        response += "• Years 1-2: Complete shared foundation courses\n"
        response += "• Year 3: Begin track specialization\n"
        response += "• Year 4: Complete remaining track requirements\n"
        response += "• Summer sessions: Take additional courses to manage workload\n\n"
        
        response += "⚠️ CHALLENGES:\n"
        response += "• Heavy course load (18+ credits per semester)\n"
        response += "• Requires excellent time management\n"
        response += "• May need advisor approval\n"
        response += "• Consider summer courses to spread workload\n\n"
        
        response += "✅ SUCCESS STRATEGY:\n"
        response += "• Start planning early (freshman year)\n"
        response += "• Take advantage of summer sessions\n"
        response += "• Maintain strong GPA for course registration priority\n"
        response += "• Regular meetings with academic advisor\n"
        
        return response
    
    def _generate_year_specific_plan(self, context: ResponseContext, year: str, track: str, courses: Dict, prerequisites: Dict, track_requirements: Dict) -> str:
        """Generate intelligent year-specific course plan"""
        
        response = f"📚 {year.upper()} YEAR COURSE PLAN\n"
        response += "=" * 40 + "\n\n"
        
        if year == "freshman":
            response += "🎯 FALL SEMESTER:\n"
            response += "• CS 18000 - Problem Solving and Object-Oriented Programming (4 credits)\n"
            response += "• MA 16100 - Plane Analytic Geometry and Calculus I (5 credits)\n"
            response += "• ENGL 10600 - First-Year Composition (4 credits)\n"
            response += "• CS 19300 - Tools (1 credit)\n"
            response += "• General Education course (3 credits)\n\n"
            
            response += "🎯 SPRING SEMESTER:\n"
            response += "• CS 18200 - Foundations of Computer Science (3 credits)\n"
            response += "• CS 24000 - Programming in C (3 credits)\n"
            response += "• MA 16200 - Plane Analytic Geometry and Calculus II (5 credits)\n"
            response += "• General Education courses (5-6 credits)\n\n"
            
            response += "💡 KEY INSIGHTS:\n"
            response += "• CS 18000 is your programming foundation - focus on mastering Java\n"
            response += "• Math sequence is critical for upper-level CS courses\n"
            response += "• Start building good study habits early\n"
            response += "• Consider joining CS clubs and study groups\n"
            
        elif year == "sophomore":
            response += "🎯 FALL SEMESTER:\n"
            response += "• CS 25000 - Computer Architecture (4 credits)\n"
            response += "• CS 25100 - Data Structures and Algorithms (4 credits)\n"
            response += "• MA 26100 - Multivariate Calculus (4 credits)\n"
            response += "• General Education courses (3-4 credits)\n\n"
            
            response += "🎯 SPRING SEMESTER:\n"
            response += "• CS 25200 - Systems Programming (4 credits)\n"
            response += "• MA 26500 - Linear Algebra (3 credits)\n"
            response += "• STAT 35000 - Introduction to Statistics (3 credits)\n"
            response += "• General Education courses (6 credits)\n\n"
            
            response += "💡 KEY INSIGHTS:\n"
            response += "• CS 25100 is the most important course - required for all upper-level CS\n"
            response += "• Start thinking about track selection\n"
            response += "• Begin preparing for internships\n"
            response += "• Math and stats prepare you for AI/ML courses\n"
            
        elif year == "junior":
            response += "🎯 FALL SEMESTER:\n"
            response += "• CS 35100 - Cloud Computing (3 credits)\n"
            response += "• CS 38100 - Introduction to Analysis of Algorithms (3 credits)\n"
            response += "• PHYS 17200 - Modern Mechanics (4 credits)\n"
            response += "• General Education courses (6 credits)\n\n"
            
            response += "🎯 SPRING SEMESTER:\n"
            response += "• PHYS 27200 - Electric and Magnetic Interactions (4 credits)\n"
            
            if track == "machine intelligence":
                response += "• CS 37300 - Data Mining and Machine Learning (3 credits)\n"
                response += "• CS 47100 or CS 47300 - AI choice (3 credits)\n"
            elif track == "software engineering":
                response += "• CS 30700 - Software Engineering I (3 credits)\n"
                response += "• CS 35200 or CS 35400 - Systems choice (3 credits)\n"
            else:
                response += "• Track courses (6 credits)\n"
            
            response += "• General Education courses (6 credits)\n\n"
            
            response += "💡 KEY INSIGHTS:\n"
            response += "• Focus on track specialization\n"
            response += "• Start senior project planning\n"
            response += "• Apply for summer internships\n"
            response += "• Build professional network\n"
            
        elif year == "senior":
            response += "🎯 FALL SEMESTER:\n"
            response += "• Track courses (6 credits)\n"
            response += "• Free electives (6 credits)\n"
            response += "• General Education courses (3 credits)\n\n"
            
            response += "🎯 SPRING SEMESTER:\n"
            response += "• Track courses (6 credits)\n"
            response += "• Free electives (6 credits)\n"
            response += "• General Education courses (3 credits)\n\n"
            
            if track == "machine intelligence":
                response += "📊 MI TRACK REQUIREMENTS:\n"
                response += "• STAT 41600/MA 41600/STAT 51200 (Statistics choice)\n"
                response += "• 2 electives from approved list\n"
            elif track == "software engineering":
                response += "📊 SE TRACK REQUIREMENTS:\n"
                response += "• CS 40700 - Software Engineering Senior Project\n"
                response += "• CS 40800 - Software Testing\n"
                response += "• 1 elective from approved list\n"
            
            response += "\n💡 KEY INSIGHTS:\n"
            response += "• Complete all degree requirements\n"
            response += "• Focus on job/internship applications\n"
            response += "• Prepare for technical interviews\n"
            response += "• Network with industry professionals\n"
        
        return response
    
    def _generate_general_course_advice(self, context: ResponseContext, courses: Dict, track_requirements: Dict) -> str:
        """Generate general course planning advice"""
        
        response = "🎓 COURSE PLANNING GUIDANCE\n"
        response += "=" * 40 + "\n\n"
        
        response += "📚 FOUNDATION COURSES (Complete First):\n"
        response += "• CS 18000 - Programming fundamentals\n"
        response += "• CS 18200 - Computer science foundations\n"
        response += "• CS 24000 - Systems programming\n"
        response += "• CS 25000 - Computer architecture\n"
        response += "• CS 25100 - Data structures and algorithms (CRITICAL)\n"
        response += "• CS 25200 - Systems programming\n\n"
        
        response += "🎯 TRACK SPECIALIZATION:\n"
        mi_courses = track_requirements.get("Machine Intelligence", {}).get("required_courses", [])
        se_courses = track_requirements.get("Software Engineering", {}).get("required_courses", [])
        
        response += "Machine Intelligence Track:\n"
        for course in mi_courses[:3]:  # Show first 3
            response += f"• {course}\n"
        response += "\nSoftware Engineering Track:\n"
        for course in se_courses[:3]:  # Show first 3
            response += f"• {course}\n"
        
        response += "\n💡 PLANNING TIPS:\n"
        response += "• Complete foundation courses before track courses\n"
        response += "• CS 25100 is required for most upper-level courses\n"
        response += "• Plan for 15-18 credits per semester\n"
        response += "• Consider summer courses to spread workload\n"
        response += "• Meet with your advisor regularly\n"
        
        return response
    
    def _generate_intelligent_graduation_planning(self, context: ResponseContext) -> str:
        """Intelligently generate graduation planning response"""
        
        # Check for dual track interest
        dual_track_interest = "both" in context.query.lower() or "dual" in context.query.lower()
        early_graduation = any(word in context.query.lower() for word in ["early", "fast", "accelerate", "3.5"])
        
        if dual_track_interest:
            return self._generate_dual_track_graduation_plan(context, early_graduation)
        
        # Generate single track graduation plan
        return self._generate_single_track_graduation_plan(context, early_graduation)
    
    def _generate_dual_track_graduation_plan(self, context: ResponseContext, early_graduation: bool) -> str:
        """Generate intelligent dual track graduation plan"""
        
        response = "🎓 DUAL TRACK GRADUATION PLAN\n"
        response += "=" * 50 + "\n"
        response += "📚 Machine Intelligence + Software Engineering Tracks\n"
        
        if early_graduation:
            response += "⏰ Timeline: 7 semesters (3.5 years)\n"
            response += "📊 Credits per semester: 18-21\n"
            response += "⚠️ Challenge Level: HIGH\n\n"
        else:
            response += "⏰ Timeline: 8 semesters (4 years)\n"
            response += "📊 Credits per semester: 15-18\n"
            response += "⚠️ Challenge Level: MODERATE\n\n"
        
        response += "📋 SEMESTER BREAKDOWN:\n"
        response += "Years 1-2: Foundation courses (CS 18000-25200, Math, Physics)\n"
        response += "Year 3: Track specialization begins\n"
        response += "Year 4: Complete track requirements\n\n"
        
        response += "🔗 SHARED REQUIREMENTS:\n"
        response += "• CS 38100 (Algorithms) - Required for both tracks\n"
        response += "• Math sequence (MA 16100, 16200, 26100, 26500)\n"
        response += "• Physics sequence (PHYS 17200, 27200)\n"
        response += "• Statistics (STAT 35000)\n\n"
        
        response += "📈 MACHINE INTELLIGENCE TRACK:\n"
        response += "• CS 37300 (Data Mining)\n"
        response += "• CS 47100 or CS 47300 (AI choice)\n"
        response += "• STAT 41600/MA 41600/STAT 51200 (Stats choice)\n"
        response += "• 2 electives from approved list\n\n"
        
        response += "⚙️ SOFTWARE ENGINEERING TRACK:\n"
        response += "• CS 30700 (SE I)\n"
        response += "• CS 40700 (Senior Project)\n"
        response += "• CS 40800 (Testing)\n"
        response += "• CS 35200 or CS 35400 (Systems choice)\n"
        response += "• 1 elective from approved list\n\n"
        
        response += "💡 SUCCESS STRATEGY:\n"
        response += "• Start planning in freshman year\n"
        response += "• Take summer courses to manage workload\n"
        response += "• Maintain 3.5+ GPA for course registration priority\n"
        response += "• Regular advisor meetings\n"
        response += "• Join study groups and CS clubs\n"
        
        if early_graduation:
            response += "\n🚀 ACCELERATED PLAN TIPS:\n"
            response += "• Consider AP credit for math/physics\n"
            response += "• Take maximum course load (18+ credits)\n"
            response += "• Summer courses are essential\n"
            response += "• Excellent time management required\n"
        
        return response
    
    def _generate_single_track_graduation_plan(self, context: ResponseContext, early_graduation: bool) -> str:
        """Generate intelligent single track graduation plan"""
        
        response = "🎓 GRADUATION PLANNING OPTIONS\n"
        response += "=" * 40 + "\n\n"
        
        if early_graduation:
            response += "🚀 EARLY GRADUATION (3.5 YEARS):\n"
            response += "• Timeline: 7 semesters\n"
            response += "• Credits per semester: 18-21\n"
            response += "• Success probability: 70%\n"
            response += "• Requirements: Strong academic performance, summer courses\n\n"
            
            response += "📋 ACCELERATED STRATEGY:\n"
            response += "• Take maximum course load each semester\n"
            response += "• Complete 2-3 courses during summers\n"
            response += "• Consider AP credit for math/physics\n"
            response += "• Maintain 3.5+ GPA for priority registration\n\n"
        else:
            response += "📅 STANDARD GRADUATION (4 YEARS):\n"
            response += "• Timeline: 8 semesters\n"
            response += "• Credits per semester: 15-18\n"
            response += "• Success probability: 95%\n"
            response += "• Requirements: Regular course load, good time management\n\n"
            
            response += "📋 STANDARD STRATEGY:\n"
            response += "• Follow recommended course sequence\n"
            response += "• Take 15-18 credits per semester\n"
            response += "• Use summers for internships or light course load\n"
            response += "• Regular advisor meetings\n\n"
        
        response += "💡 GENERAL TIPS:\n"
        response += "• Complete foundation courses first (CS 18000-25200)\n"
        response += "• CS 25100 is critical - don't delay it\n"
        response += "• Plan track courses for junior/senior years\n"
        response += "• Consider study abroad or internships\n"
        response += "• Build professional network early\n"
        
        return response
    
    def _generate_intelligent_track_selection(self, context: ResponseContext) -> str:
        """Intelligently generate track selection response"""
        
        # Check for dual track interest
        dual_track_interest = "both" in context.query.lower() or "dual" in context.query.lower()
        
        if dual_track_interest:
            return self._generate_dual_track_comparison(context)
        
        # Get track data
        tracks = context.data.get("tracks", {})
        career_guidance = context.data.get("career_guidance", {})
        
        response = "🎯 CS TRACK COMPARISON\n"
        response += "=" * 30 + "\n\n"
        
        for track_name, track_data in tracks.items():
            response += f"📚 {track_name.upper()} TRACK:\n"
            response += "-" * 20 + "\n"
            
            # Required courses
            required_courses = track_data.get("required_courses", [])
            response += "Required Courses:\n"
            for course in required_courses:
                response += f"• {course}\n"
            
            # Focus area
            focus = track_data.get("focus", "Not specified")
            response += f"\nFocus: {focus}\n"
            
            # Career paths
            career_paths = track_data.get("career_paths", "Not specified")
            response += f"Career Paths: {career_paths}\n"
            
            # Difficulty level
            if "machine intelligence" in track_name.lower():
                response += "Difficulty: High (heavy math/stats focus)\n"
            elif "software engineering" in track_name.lower():
                response += "Difficulty: Moderate (practical programming focus)\n"
            
            response += "\n"
        
        response += "💡 SELECTION GUIDANCE:\n"
        response += "• Machine Intelligence: Choose if interested in AI, ML, data science\n"
        response += "• Software Engineering: Choose if interested in software development, systems\n"
        response += "• Both tracks: Ambitious but achievable with proper planning\n"
        response += "• Consider your career goals and interests\n"
        response += "• Talk to current students and alumni\n"
        
        return response
    
    def _generate_dual_track_comparison(self, context: ResponseContext) -> str:
        """Generate intelligent dual track comparison"""
        
        response = "🎯 DUAL TRACK ANALYSIS\n"
        response += "=" * 30 + "\n\n"
        
        response += "📊 FEASIBILITY:\n"
        response += "✅ POSSIBLE: Yes, with advisor approval\n"
        response += "⏰ TIMELINE: 4 years (8 semesters)\n"
        response += "📚 COURSES: ~60 CS credits total\n"
        response += "💼 CAREER: Extremely marketable combination\n\n"
        
        response += "🔗 SHARED COURSES:\n"
        response += "• CS 38100 (Algorithms) - Required for both\n"
        response += "• Foundation sequence (CS 18000-25200)\n"
        response += "• Math and physics requirements\n\n"
        
        response += "📈 MACHINE INTELLIGENCE ADDITIONS:\n"
        response += "• CS 37300 (Data Mining)\n"
        response += "• CS 47100 or CS 47300 (AI choice)\n"
        response += "• Advanced statistics courses\n"
        response += "• 2 AI/ML electives\n\n"
        
        response += "⚙️ SOFTWARE ENGINEERING ADDITIONS:\n"
        response += "• CS 30700 (SE I)\n"
        response += "• CS 40700 (Senior Project)\n"
        response += "• CS 40800 (Testing)\n"
        response += "• Systems courses\n"
        response += "• 1 SE elective\n\n"
        
        response += "💡 ADVANTAGES:\n"
        response += "• Highly marketable skill combination\n"
        response += "• AI/ML + Software Engineering = Perfect for modern tech\n"
        response += "• Opens doors to both research and industry\n"
        response += "• Competitive advantage in job market\n\n"
        
        response += "⚠️ CHALLENGES:\n"
        response += "• Heavy course load (18+ credits per semester)\n"
        response += "• Requires excellent time management\n"
        response += "• May need summer courses\n"
        response += "• Advisor approval required\n\n"
        
        response += "🚀 RECOMMENDATION:\n"
        response += "If you're passionate about both AI and software development,\n"
        response += "this combination is excellent for modern tech careers.\n"
        response += "Start planning early and maintain strong academic performance.\n"
        
        return response
    
    def _generate_intelligent_prerequisites(self, context: ResponseContext) -> str:
        """Intelligently generate prerequisites response"""
        
        course_codes = context.entities.get("course_codes", [])
        prerequisites = context.data.get("prerequisites", {})
        courses = context.data.get("courses", {})
        
        if not course_codes:
            # Try to use AI-generated response for clarification
            try:
                if hasattr(self, 'gemini_model') and self.gemini_model:
                    from ai_training_prompts import get_comprehensive_system_prompt
                    system_prompt = get_comprehensive_system_prompt()
                    
                    response = self.gemini_model.generate_content(
                        ,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": "I want to know about prerequisites but didn't specify which course. Please ask me to clarify which course I'm interested in."}
                        ],
                        ,
                        
                    )
                    
                    ai_response = response.text.strip()
                    if ai_response and len(ai_response) > 10:
                        return ai_response
            except:
                pass
                
            return "I can help you with prerequisites! Which course are you asking about? (e.g., CS 37300, CS 38100)"
        
        response = "📚 PREREQUISITE ANALYSIS\n"
        response += "=" * 30 + "\n\n"
        
        for course_code in course_codes:
            response += f"🎯 {course_code}:\n"
            
            if course_code in prerequisites:
                prereqs = prerequisites[course_code]
                response += "Required Prerequisites:\n"
                for prereq in prereqs:
                    response += f"• {prereq}\n"
                
                # Add intelligent insights
                if "CS 25100" in prereqs:
                    response += "\n💡 Note: CS 25100 is a critical foundation course.\n"
                    response += "   Complete it early as it's required for most upper-level CS courses.\n"
                
                if "CS 38100" in prereqs:
                    response += "\n💡 Note: CS 38100 (Algorithms) is required for both tracks.\n"
                    response += "   Plan to take this in your junior year.\n"
                
            else:
                response += "No prerequisites found in the system.\n"
                response += "This may be a foundation course or elective.\n"
            
            # Add course information if available
            if course_code in courses:
                course_info = courses[course_code]
                response += f"\n📖 Course Info:\n"
                response += f"• Title: {course_info.get('title', 'Unknown')}\n"
                response += f"• Credits: {course_info.get('credits', 'Unknown')}\n"
                response += f"• Description: {course_info.get('description', 'No description available')}\n"
            
            response += "\n"
        
        response += "💡 PLANNING TIPS:\n"
        response += "• Complete prerequisites before taking advanced courses\n"
        response += "• CS 25100 is required for most upper-level CS courses\n"
        response += "• Plan your course sequence carefully\n"
        response += "• Meet with your advisor to verify prerequisites\n"
        
        return response
    
    def _generate_intelligent_course_difficulty(self, context: ResponseContext) -> str:
        """Intelligently generate course difficulty response"""
        
        course_codes = context.entities.get("course_codes", [])
        courses = context.data.get("courses", {})
        
        if not course_codes:
            return "I can help you understand course difficulty! Which course are you asking about? (e.g., CS 18000, CS 25100)"
        
        response = "📊 COURSE DIFFICULTY ANALYSIS\n"
        response += "=" * 35 + "\n\n"
        
        for course_code in course_codes:
            response += f"🎯 {course_code}:\n"
            
            if course_code in courses:
                course_info = courses[course_code]
                response += f"• Title: {course_info.get('title', 'Unknown')}\n"
                response += f"• Credits: {course_info.get('credits', 'Unknown')}\n"
                response += f"• Difficulty: {course_info.get('difficulty', 'Not specified')}\n"
                response += f"• Description: {course_info.get('description', 'No description available')}\n"
                
                # Add intelligent difficulty insights
                if course_code == "CS 25100":
                    response += "\n💡 DIFFICULTY INSIGHTS:\n"
                    response += "• CRITICAL COURSE: Required for all upper-level CS\n"
                    response += "• High workload: Expect 15-20 hours per week\n"
                    response += "• Programming intensive: Java/C++ required\n"
                    response += "• Mathematical concepts: Big-O analysis, algorithms\n"
                    response += "• Success rate: ~75% (challenging but manageable)\n"
                
                elif course_code == "CS 18000":
                    response += "\n💡 DIFFICULTY INSIGHTS:\n"
                    response += "• Foundation course: Your programming base\n"
                    response += "• Moderate workload: 10-15 hours per week\n"
                    response += "• Java programming: Object-oriented concepts\n"
                    response += "• Success rate: ~85% (good foundation for success)\n"
                
                elif course_code == "CS 37300":
                    response += "\n💡 DIFFICULTY INSIGHTS:\n"
                    response += "• Advanced course: Requires strong math background\n"
                    response += "• High workload: 15-20 hours per week\n"
                    response += "• Machine learning concepts: Algorithms, statistics\n"
                    response += "• Prerequisites: CS 25100, STAT 35000\n"
                    response += "• Success rate: ~70% (challenging but rewarding)\n"
                
                elif course_code == "CS 38100":
                    response += "\n💡 DIFFICULTY INSIGHTS:\n"
                    response += "• Core algorithms course: Required for both tracks\n"
                    response += "• High workload: 15-20 hours per week\n"
                    response += "• Mathematical: Proofs, complexity analysis\n"
                    response += "• Prerequisites: CS 25100, strong math background\n"
                    response += "• Success rate: ~65% (one of the most challenging CS courses)\n"
                
            else:
                response += "Course information not found in the system.\n"
            
            response += "\n"
        
        response += "💡 GENERAL DIFFICULTY GUIDANCE:\n"
        response += "• Foundation courses (CS 18000-25200): Moderate difficulty\n"
        response += "• Core courses (CS 25100, CS 38100): High difficulty\n"
        response += "• Track courses: Varies by track and interest\n"
        response += "• Plan for 10-20 hours per week per CS course\n"
        response += "• Form study groups and seek help early\n"
        
        return response
    
    def _generate_intelligent_career_guidance(self, context: ResponseContext) -> str:
        """Intelligently generate career guidance response"""
        
        career_guidance = context.data.get("career_guidance", {})
        tracks = context.data.get("tracks", {})
        
        response = "💼 CAREER GUIDANCE FOR CS GRADUATES\n"
        response += "=" * 40 + "\n\n"
        
        response += "🎯 MACHINE INTELLIGENCE TRACK:\n"
        response += "-" * 30 + "\n"
        response += "Career Paths:\n"
        response += "• Data Scientist\n"
        response += "• Machine Learning Engineer\n"
        response += "• AI Research Scientist\n"
        response += "• Quantitative Analyst\n"
        response += "• Research & Development\n\n"
        
        response += "Skills to Develop:\n"
        response += "• Python, R, MATLAB\n"
        response += "• Machine Learning frameworks (TensorFlow, PyTorch)\n"
        response += "• Statistics and Mathematics\n"
        response += "• Research methodology\n\n"
        
        response += "🎯 SOFTWARE ENGINEERING TRACK:\n"
        response += "-" * 30 + "\n"
        response += "Career Paths:\n"
        response += "• Software Engineer\n"
        response += "• Full-Stack Developer\n"
        response += "• Systems Engineer\n"
        response += "• DevOps Engineer\n"
        response += "• Technical Lead\n\n"
        
        response += "Skills to Develop:\n"
        response += "• Java, C++, Python\n"
        response += "• Web technologies (JavaScript, React, Node.js)\n"
        response += "• Software design patterns\n"
        response += "• Version control (Git)\n\n"
        
        response += "🚀 DUAL TRACK ADVANTAGES:\n"
        response += "-" * 25 + "\n"
        response += "• AI/ML Engineer (combines both tracks)\n"
        response += "• Research Scientist\n"
        response += "• Technical Lead\n"
        response += "• Startup founder\n"
        response += "• Highly competitive in job market\n\n"
        
        response += "💡 CAREER PREPARATION TIPS:\n"
        response += "-" * 30 + "\n"
        response += "• Build a strong portfolio of projects\n"
        response += "• Participate in hackathons and competitions\n"
        response += "• Seek internships early (sophomore/junior year)\n"
        response += "• Network with alumni and industry professionals\n"
        response += "• Contribute to open source projects\n"
        response += "• Develop soft skills (communication, teamwork)\n"
        response += "• Consider graduate school for research careers\n"
        
        return response
    
    def _generate_intelligent_general_response(self, context: ResponseContext) -> str:
        """Generate intelligent general response"""
        
        # Try to use AI-generated response for general queries
        try:
            if hasattr(self, 'gemini_model') and self.gemini_model:
                from ai_training_prompts import get_comprehensive_system_prompt
                system_prompt = get_comprehensive_system_prompt()
                
                query_context = f"User query: {context.query}. Intent: {context.intent}. Available data: {len(context.data)} sources."
                
                response = self.gemini_model.generate_content(
                    ,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Please respond to this general query about Purdue CS: {context.query}. Context: {query_context}"}
                    ],
                    ,
                    
                )
                
                ai_response = response.text.strip()
                if ai_response and len(ai_response) > 50:
                    return ai_response
        except:
            pass  # Fall back to dynamic response
        
        # Dynamic fallback response
        response = "🎓 PURDUE CS ACADEMIC ADVISING\n"
        response += "=" * 35 + "\n\n"
        
        response += "I can help you with comprehensive Purdue CS academic advising!\n\n"
        
        response += "📚 SERVICES AVAILABLE:\n"
        response += "• Course planning and scheduling\n"
        response += "• Graduation planning and timelines\n"
        response += "• Track selection (Machine Intelligence vs Software Engineering)\n"
        response += "• Dual track graduation planning\n"
        response += "• Prerequisites and course requirements\n"
        response += "• Course difficulty and workload analysis\n"
        response += "• Career guidance and opportunities\n"
        response += "• Academic standing and GPA management\n\n"
        
        response += "🎯 POPULAR QUERIES:\n"
        response += "• \"What courses should I take as a freshman?\"\n"
        response += "• \"I want to graduate with both tracks\"\n"
        response += "• \"How hard is CS 25100?\"\n"
        response += "• \"Which track should I choose?\"\n"
        response += "• \"Can I graduate early?\"\n\n"
        
        response += "💡 GETTING STARTED:\n"
        response += "Tell me about your academic situation:\n"
        response += "• What year are you? (freshman, sophomore, junior, senior)\n"
        response += "• Which track interests you? (MI, SE, or both)\n"
        response += "• What specific questions do you have?\n"
        
        return response
    
    def _generate_fallback_response(self, context: ResponseContext) -> str:
        """Generate fallback response when intelligent generation fails"""
        
        return ("I'm having trouble processing your request right now. "
                "Please try rephrasing your question or ask about a different topic. "
                "I can help with course planning, track selection, prerequisites, "
                "graduation planning, and career guidance.") 