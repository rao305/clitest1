#!/usr/bin/env python3
"""
Intelligent Prerequisite Chain Analyzer
Provides comprehensive prerequisite analysis with the same intelligence level as Claude Code
Handles course number pattern recognition (CS 182 -> CS 18200) and complete dependency analysis
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CourseImpact:
    """Detailed impact analysis for a course failure"""
    course_code: str
    can_take: bool
    blocked_reason: Optional[str]
    alternative_paths: List[str]
    recovery_timeline: str
    graduation_delay: int  # in semesters

@dataclass 
class PrerequisiteAnalysis:
    """Complete prerequisite chain analysis result"""
    query_course: str
    target_courses: List[str]
    prerequisite_chain: Dict[str, List[str]]
    impact_analysis: List[CourseImpact]
    recovery_strategy: str
    detailed_explanation: str

class IntelligentPrerequisiteAnalyzer:
    """
    Advanced prerequisite analyzer that matches Claude Code's analytical capabilities
    Provides detailed prerequisite chain analysis, course impact assessment, and recovery strategies
    """
    
    def __init__(self, knowledge_file: str = "data/cs_knowledge_graph.json"):
        self.knowledge_file = knowledge_file
        self.knowledge_base = self._load_knowledge_base()
        
        # Course number pattern mappings (CS 182 -> CS 18200, etc.)
        self.course_mappings = {
            '180': 'CS 18000',
            '182': 'CS 18200', 
            '240': 'CS 24000',
            '250': 'CS 25000',
            '251': 'CS 25100',
            '252': 'CS 25200',
            '381': 'CS 38100'
        }
        
        # Enhanced patterns for course recognition
        self.course_patterns = [
            r'\bcs\s*(\d{3})\b',     # CS 182, CS 240
            r'\bcs\s*(\d{5})\b',     # CS 18200, CS 24000  
            r'\b(\d{3})\b',          # 182, 240
            r'\b(\d{5})\b'           # 18200, 24000
        ]
        
        # Failure scenario templates from knowledge base
        self.failure_scenarios = self.knowledge_base.get("failure_recovery_scenarios", {})
        
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load comprehensive knowledge base"""
        try:
            with open(self.knowledge_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def normalize_course_code(self, query: str) -> List[str]:
        """
        Extract and normalize course codes from query using intelligent pattern matching
        Handles: CS 182, CS 18200, 182, 240, etc.
        """
        normalized_courses = []
        query_lower = query.lower()
        
        # Try all course patterns
        for pattern in self.course_patterns:
            matches = re.findall(pattern, query_lower)
            for match in matches:
                # Handle 3-digit patterns (182 -> CS 18200)
                if len(match) == 3:
                    if match in self.course_mappings:
                        normalized_courses.append(self.course_mappings[match])
                    else:
                        # Try to construct course code
                        if match.startswith('1') or match.startswith('2'):
                            normalized_courses.append(f"CS {match}00")
                        else:
                            normalized_courses.append(f"CS {match}")
                            
                # Handle 5-digit patterns (18200 -> CS 18200)
                elif len(match) == 5:
                    normalized_courses.append(f"CS {match}")
                    
        # Remove duplicates while preserving order
        return list(dict.fromkeys(normalized_courses))
    
    def get_prerequisite_chain(self, course_code: str) -> List[str]:
        """
        Get complete prerequisite chain for a course using graph traversal
        Returns all courses that must be completed before taking the target course
        """
        prerequisites = self.knowledge_base.get("prerequisites", {})
        visited = set()
        chain = []
        
        def traverse_prereqs(course):
            if course in visited or course not in prerequisites:
                return
            
            visited.add(course)
            course_prereqs = prerequisites.get(course, [])
            
            for prereq in course_prereqs:
                traverse_prereqs(prereq)
                if prereq not in chain:
                    chain.append(prereq)
            
            if course not in chain:
                chain.append(course)
        
        traverse_prereqs(course_code)
        return chain[:-1]  # Remove the target course itself
    
    def analyze_failure_impact(self, failed_course: str, target_courses: List[str]) -> List[CourseImpact]:
        """
        Analyze impact of failing a course on ability to take target courses
        Provides detailed analysis like Claude Code's approach
        """
        impacts = []
        
        for target_course in target_courses:
            # Get prerequisite chain for target course
            prereq_chain = self.get_prerequisite_chain(target_course)
            
            # Check if failed course is in prerequisite chain
            can_take = failed_course not in prereq_chain
            
            if can_take:
                impact = CourseImpact(
                    course_code=target_course,
                    can_take=True,
                    blocked_reason=None,
                    alternative_paths=[],
                    recovery_timeline="No delay - can proceed normally",
                    graduation_delay=0
                )
            else:
                # Analyze blocking scenario
                course_info = self.knowledge_base.get("courses", {}).get(target_course, {})
                direct_prereqs = self.knowledge_base.get("prerequisites", {}).get(target_course, [])
                
                blocked_reason = f"Requires {failed_course} as prerequisite"
                if failed_course in direct_prereqs:
                    blocked_reason = f"Direct prerequisite: {failed_course} must be completed first"
                else:
                    blocked_reason = f"Indirect prerequisite: {failed_course} required earlier in sequence"
                
                # Get failure scenario data if available
                failure_key = f"{failed_course.replace(' ', '_')}_failure"
                failure_data = self.failure_scenarios.get(failure_key, {})
                
                delay_semesters = failure_data.get("delay_semesters", 1)
                recovery_strategy = failure_data.get("recovery_strategy", "Retake course next semester")
                
                impact = CourseImpact(
                    course_code=target_course,
                    can_take=False,
                    blocked_reason=blocked_reason,
                    alternative_paths=self._get_alternative_paths(target_course, failed_course),
                    recovery_timeline=f"Delay of {delay_semesters} semester(s) - {recovery_strategy}",
                    graduation_delay=delay_semesters
                )
            
            impacts.append(impact)
        
        return impacts
    
    def _get_alternative_paths(self, target_course: str, failed_course: str) -> List[str]:
        """Get alternative paths or summer course options"""
        alternatives = []
        
        # Check for summer course availability
        failure_key = f"{failed_course.replace(' ', '_')}_failure"
        failure_data = self.failure_scenarios.get(failure_key, {})
        
        if failure_data.get("summer_option", False):
            alternatives.append(f"Retake {failed_course} in summer")
        
        # Add specific recovery strategies
        if failure_data.get("recovery_strategy"):
            alternatives.append(failure_data["recovery_strategy"])
        
        return alternatives
    
    def analyze_prerequisite_query(self, query: str) -> PrerequisiteAnalysis:
        """
        Main analysis function - provides comprehensive prerequisite analysis
        Matches the intelligence level of Claude Code's analysis
        """
        # Extract course codes from query
        detected_courses = self.normalize_course_code(query)
        
        if not detected_courses:
            return PrerequisiteAnalysis(
                query_course="Unknown",
                target_courses=[],
                prerequisite_chain={},
                impact_analysis=[],
                recovery_strategy="Could not identify course codes in query",
                detailed_explanation="Please specify course numbers (e.g., CS 182, CS 240, Calc 1)"
            )
        
        # Determine analysis type based on query content
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['fail', 'failing', 'failed']):
            return self._analyze_failure_scenario(query, detected_courses)
        elif any(word in query_lower for word in ['take', 'taking', 'still', 'can i']):
            return self._analyze_course_availability(query, detected_courses)
        else:
            return self._analyze_general_prerequisites(query, detected_courses)
    
    def _analyze_failure_scenario(self, query: str, courses: List[str]) -> PrerequisiteAnalysis:
        """Analyze course failure impact scenarios"""
        query_lower = query.lower()
        
        # Identify failed course and target courses
        failed_course = None
        target_courses = []
        
        # Look for failure indicators
        if 'calc' in query_lower and ('1' in query_lower or 'i' in query_lower):
            failed_course = 'MA 16100'  # Calc 1
        else:
            # Assume first detected course is the one that failed
            if courses:
                failed_course = courses[0]
        
        # Identify target courses from query
        for course in courses:
            if course != failed_course:
                target_courses.append(course)
        
        # If no specific target courses, analyze common next courses
        if not target_courses:
            if failed_course == 'MA 16100':  # Calc 1 failure
                target_courses = ['CS 18200', 'CS 24000']  # Common spring courses
            elif failed_course == 'CS 18000':
                target_courses = ['CS 18200', 'CS 24000']
            elif failed_course == 'CS 18200':
                target_courses = ['CS 25000', 'CS 25100', 'CS 25200']
        
        # Perform impact analysis
        impact_analysis = self.analyze_failure_impact(failed_course, target_courses)
        
        # Build prerequisite chains
        prereq_chains = {}
        for course in target_courses:
            prereq_chains[course] = self.get_prerequisite_chain(course)
        
        # Generate detailed explanation
        explanation = self._generate_failure_explanation(failed_course, target_courses, impact_analysis)
        
        # Generate recovery strategy
        recovery_strategy = self._generate_recovery_strategy(failed_course, impact_analysis)
        
        return PrerequisiteAnalysis(
            query_course=failed_course,
            target_courses=target_courses,
            prerequisite_chain=prereq_chains,
            impact_analysis=impact_analysis,
            recovery_strategy=recovery_strategy,
            detailed_explanation=explanation
        )
    
    def _analyze_course_availability(self, query: str, courses: List[str]) -> PrerequisiteAnalysis:
        """Analyze whether courses can be taken (availability analysis)"""
        # Similar logic but focused on availability rather than failure
        # This would handle queries like "Can I take CS 182 if I haven't finished Calc 1?"
        
        target_courses = courses
        impact_analysis = []
        
        for course in target_courses:
            prereqs = self.get_prerequisite_chain(course)
            direct_prereqs = self.knowledge_base.get("prerequisites", {}).get(course, [])
            
            # Check if prerequisites are mentioned as potentially missing
            can_take = True
            blocked_reason = None
            
            # Simple heuristic - if calc/math is mentioned and course requires it
            if 'calc' in query.lower() or 'math' in query.lower():
                if any('MA ' in prereq for prereq in direct_prereqs):
                    can_take = False
                    blocked_reason = "Requires calculus prerequisite"
            
            impact = CourseImpact(
                course_code=course,
                can_take=can_take,
                blocked_reason=blocked_reason,
                alternative_paths=[],
                recovery_timeline="Check prerequisite completion",
                graduation_delay=0 if can_take else 1
            )
            impact_analysis.append(impact)
        
        explanation = self._generate_availability_explanation(target_courses, impact_analysis)
        
        return PrerequisiteAnalysis(
            query_course="Availability Check",
            target_courses=target_courses,
            prerequisite_chain={course: self.get_prerequisite_chain(course) for course in target_courses},
            impact_analysis=impact_analysis,
            recovery_strategy="Complete missing prerequisites",
            detailed_explanation=explanation
        )
    
    def _analyze_general_prerequisites(self, query: str, courses: List[str]) -> PrerequisiteAnalysis:
        """General prerequisite analysis"""
        target_courses = courses
        prereq_chains = {}
        
        for course in target_courses:
            prereq_chains[course] = self.get_prerequisite_chain(course)
        
        explanation = f"Prerequisite analysis for {', '.join(target_courses)}:\n\n"
        
        for course in target_courses:
            course_info = self.knowledge_base.get("courses", {}).get(course, {})
            direct_prereqs = self.knowledge_base.get("prerequisites", {}).get(course, [])
            
            explanation += f"**{course}** - {course_info.get('title', 'Unknown Course')}\n"
            explanation += f"Direct prerequisites: {', '.join(direct_prereqs) if direct_prereqs else 'None'}\n"
            explanation += f"Complete prerequisite chain: {' → '.join(prereq_chains[course]) if prereq_chains[course] else 'None'}\n\n"
        
        return PrerequisiteAnalysis(
            query_course="General Analysis",
            target_courses=target_courses,
            prerequisite_chain=prereq_chains,
            impact_analysis=[],
            recovery_strategy="Follow prerequisite sequence",
            detailed_explanation=explanation
        )
    
    def _generate_failure_explanation(self, failed_course: str, target_courses: List[str], impacts: List[CourseImpact]) -> str:
        """Generate detailed explanation similar to Claude Code's response style"""
        
        explanation = f"**If you fail {failed_course}:**\n\n"
        
        for impact in impacts:
            course_info = self.knowledge_base.get("courses", {}).get(impact.course_code, {})
            course_title = course_info.get("title", "Unknown Course")
            
            if impact.can_take:
                explanation += f"✅ **{impact.course_code}** ({course_title}) - You **can** still take this course\n"
                explanation += f"   • No prerequisite dependency on {failed_course}\n"
            else:
                explanation += f"❌ **{impact.course_code}** ({course_title}) - You **cannot** take this course\n"
                explanation += f"   • {impact.blocked_reason}\n"
                if impact.alternative_paths:
                    explanation += f"   • Recovery options: {', '.join(impact.alternative_paths)}\n"
            
            explanation += f"   • Timeline: {impact.recovery_timeline}\n\n"
        
        # Add overall impact assessment
        total_delays = sum(impact.graduation_delay for impact in impacts if not impact.can_take)
        if total_delays > 0:
            explanation += f"**Overall Impact:**\n"
            explanation += f"• Expected delay: {max(impact.graduation_delay for impact in impacts)} semester(s)\n"
            explanation += f"• Recovery strategy recommended for minimal graduation impact\n"
        
        return explanation
    
    def _generate_availability_explanation(self, courses: List[str], impacts: List[CourseImpact]) -> str:
        """Generate availability explanation"""
        explanation = "**Course Availability Analysis:**\n\n"
        
        for impact in impacts:
            course_info = self.knowledge_base.get("courses", {}).get(impact.course_code, {})
            prereqs = self.knowledge_base.get("prerequisites", {}).get(impact.course_code, [])
            
            explanation += f"**{impact.course_code}** - {course_info.get('title', 'Unknown Course')}\n"
            explanation += f"Prerequisites required: {', '.join(prereqs) if prereqs else 'None'}\n"
            
            if impact.can_take:
                explanation += "✅ Can proceed if prerequisites are met\n"
            else:
                explanation += f"❌ Cannot proceed: {impact.blocked_reason}\n"
            
            explanation += "\n"
        
        return explanation
    
    def _generate_recovery_strategy(self, failed_course: str, impacts: List[CourseImpact]) -> str:
        """Generate comprehensive recovery strategy"""
        
        # Get failure scenario data
        failure_key = f"{failed_course.replace(' ', '_')}_failure"
        failure_data = self.failure_scenarios.get(failure_key, {})
        
        strategy = f"**Recovery Strategy for {failed_course} failure:**\n\n"
        
        if failure_data:
            strategy += f"• Expected delay: {failure_data.get('delay_semesters', 1)} semester(s)\n"
            strategy += f"• Recovery approach: {failure_data.get('recovery_strategy', 'Retake immediately')}\n"
            if failure_data.get('summer_option', False):
                strategy += f"• Summer option: Available to accelerate recovery\n"
            strategy += f"• Difficulty: {failure_data.get('difficulty', 'Medium')}\n"
        
        # Add course-specific strategies
        blocked_courses = [impact.course_code for impact in impacts if not impact.can_take]
        available_courses = [impact.course_code for impact in impacts if impact.can_take]
        
        if available_courses:
            strategy += f"\n**Courses you can still take:** {', '.join(available_courses)}\n"
        
        if blocked_courses:
            strategy += f"**Courses blocked until recovery:** {', '.join(blocked_courses)}\n"
        
        return strategy

    def format_analysis_response(self, analysis: PrerequisiteAnalysis) -> str:
        """
        Format the analysis into a natural, conversational response
        Similar to how Claude Code responds
        """
        if not analysis.target_courses:
            return analysis.detailed_explanation
        
        response = analysis.detailed_explanation
        
        if analysis.impact_analysis:
            response += f"\n**Recovery Strategy:**\n{analysis.recovery_strategy}\n"
        
        # Add prerequisite chains for reference
        if analysis.prerequisite_chain:
            response += "\n**Complete Prerequisite Chains:**\n"
            for course, chain in analysis.prerequisite_chain.items():
                if chain:
                    response += f"• {course}: {' → '.join(chain)} → {course}\n"
                else:
                    response += f"• {course}: No prerequisites\n"
        
        return response

# Testing function
def test_analyzer():
    """Test the intelligent prerequisite analyzer"""
    analyzer = IntelligentPrerequisiteAnalyzer()
    
    # Test the exact query from the user
    test_query = "if i fail calc 1 would i still be able to take cs 182 or cs 240 after my freshman fall semester for spring semester"
    
    print(f"Query: {test_query}")
    print("=" * 80)
    
    analysis = analyzer.analyze_prerequisite_query(test_query)
    response = analyzer.format_analysis_response(analysis)
    
    print(response)

if __name__ == "__main__":
    test_analyzer()