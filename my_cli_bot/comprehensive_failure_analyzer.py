#!/usr/bin/env python3
"""
Comprehensive Failure Analyzer for All Foundation and Math Classes
Handles failure scenarios for EVERY CS foundation class and math class
Provides detailed semester predictions, summer recommendations, and recovery timelines
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class Semester(Enum):
    FALL = "Fall"
    SPRING = "Spring"
    SUMMER = "Summer"

class StudentYear(Enum):
    FRESHMAN = "Freshman"
    SOPHOMORE = "Sophomore"
    JUNIOR = "Junior"
    SENIOR = "Senior"

@dataclass
class CourseSchedule:
    """When courses are typically offered"""
    course_code: str
    typical_semesters: List[Semester]  # When it's usually offered
    typical_year: StudentYear  # When students typically take it
    summer_available: bool
    difficulty_level: str
    time_commitment: str

@dataclass
class FailureScenario:
    """Comprehensive failure scenario analysis"""
    failed_course: str
    failure_semester: str  # "Fall Freshman", "Spring Freshman", etc.
    immediate_impact: List[str]  # Courses blocked next semester
    long_term_impact: List[str]  # Courses blocked later
    semester_delay: int  # How many semesters behind
    graduation_delay: int  # Additional semesters to graduate
    summer_recovery_options: List[str]
    fall_recovery_options: List[str]
    spring_recovery_options: List[str]
    recommended_strategy: str
    severity: str  # "Minor", "Moderate", "Severe", "Critical"

class ComprehensiveFailureAnalyzer:
    """
    Complete failure analysis system for all Purdue CS foundation and math courses
    Provides detailed semester predictions and recovery strategies
    """
    
    def __init__(self, knowledge_file: str = "data/cs_knowledge_graph.json"):
        self.knowledge_file = knowledge_file
        self.knowledge_base = self._load_knowledge_base()
        
        # Define all course schedules
        self.course_schedules = self._initialize_course_schedules()
        
        # Define all failure scenarios
        self.failure_scenarios = self._initialize_failure_scenarios()
        
        # Course mappings for pattern recognition
        self.course_mappings = {
            '180': 'CS 18000', '182': 'CS 18200', '240': 'CS 24000',
            '250': 'CS 25000', '251': 'CS 25100', '252': 'CS 25200',
            '161': 'MA 16100', '162': 'MA 16200', '261': 'MA 26100', '265': 'MA 26500',
            'calc 1': 'MA 16100', 'calc1': 'MA 16100', 'calculus 1': 'MA 16100',
            'calc 2': 'MA 16200', 'calc2': 'MA 16200', 'calculus 2': 'MA 16200',
            'calc 3': 'MA 26100', 'calc3': 'MA 26100', 'multivariate': 'MA 26100',
            'linear algebra': 'MA 26500', 'linear': 'MA 26500'
        }
        
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load knowledge base with error handling"""
        try:
            with open(self.knowledge_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Knowledge file {self.knowledge_file} not found")
            return {}
    
    def _initialize_course_schedules(self) -> Dict[str, CourseSchedule]:
        """Initialize typical course schedules for all courses"""
        return {
            # CS Foundation Courses
            'CS 18000': CourseSchedule(
                'CS 18000', [Semester.FALL], StudentYear.FRESHMAN, True,
                "Very Hard", "15-20 hours/week"
            ),
            'CS 18200': CourseSchedule(
                'CS 18200', [Semester.SPRING], StudentYear.FRESHMAN, True,
                "Hard", "12-15 hours/week"  
            ),
            'CS 24000': CourseSchedule(
                'CS 24000', [Semester.SPRING], StudentYear.FRESHMAN, True,
                "Moderate-Hard", "10-15 hours/week"
            ),
            'CS 25000': CourseSchedule(
                'CS 25000', [Semester.FALL], StudentYear.SOPHOMORE, False,
                "Hard", "15-18 hours/week"
            ),
            'CS 25100': CourseSchedule(
                'CS 25100', [Semester.FALL], StudentYear.SOPHOMORE, True,
                "Very Hard", "18-25 hours/week"
            ),
            'CS 25200': CourseSchedule(
                'CS 25200', [Semester.SPRING], StudentYear.SOPHOMORE, False,
                "Very Hard", "20-25 hours/week"
            ),
            
            # Math Courses
            'MA 16100': CourseSchedule(
                'MA 16100', [Semester.FALL, Semester.SPRING], StudentYear.FRESHMAN, True,
                "Moderate", "10-15 hours/week"
            ),
            'MA 16200': CourseSchedule(
                'MA 16200', [Semester.SPRING, Semester.FALL], StudentYear.FRESHMAN, True,
                "Moderate-Hard", "12-18 hours/week"
            ),
            'MA 26100': CourseSchedule(
                'MA 26100', [Semester.FALL], StudentYear.SOPHOMORE, True,
                "Hard", "15-20 hours/week"
            ),
            'MA 26500': CourseSchedule(
                'MA 26500', [Semester.SPRING], StudentYear.SOPHOMORE, True,
                "Moderate-Hard", "12-18 hours/week"
            ),
            'STAT 35000': CourseSchedule(
                'STAT 35000', [Semester.FALL, Semester.SPRING], StudentYear.JUNIOR, True,
                "Moderate", "8-12 hours/week"
            )
        }
    
    def _initialize_failure_scenarios(self) -> Dict[str, FailureScenario]:
        """Initialize comprehensive failure scenarios for all courses"""
        scenarios = {}
        
        # CS 18000 Failure Scenarios
        scenarios['CS 18000_Fall_Freshman'] = FailureScenario(
            failed_course='CS 18000',
            failure_semester='Fall Freshman',
            immediate_impact=['CS 18200', 'CS 24000'],  # Can't take spring courses
            long_term_impact=['CS 25000', 'CS 25100', 'CS 25200', 'All upper-level CS'],
            semester_delay=2,  # Must retake in fall, pushes everything back
            graduation_delay=1,  # At least one extra semester
            summer_recovery_options=[],  # CS 18000 not typically offered in summer
            fall_recovery_options=['Retake CS 18000 next fall', 'Take other gen eds'],
            spring_recovery_options=['Take CS 18200 and CS 24000 after retaking CS 18000'],
            recommended_strategy="Retake CS 18000 immediately next fall. Use spring for math (MA 16200) and gen eds. This pushes your entire CS sequence back by one year. Consider changing majors if struggled significantly.",
            severity="Critical"
        )
        
        # CS 18200 Failure Scenarios  
        scenarios['CS 18200_Spring_Freshman'] = FailureScenario(
            failed_course='CS 18200',
            failure_semester='Spring Freshman',
            immediate_impact=['CS 25000', 'CS 25100'],  # Can't take fall sophomore courses
            long_term_impact=['CS 25200', 'All upper-level CS requiring CS 25100'],
            semester_delay=1,
            graduation_delay=1,
            summer_recovery_options=['Retake CS 18200 in summer'],
            fall_recovery_options=['Retake CS 18200 in fall with reduced course load'],
            spring_recovery_options=['Take CS 25000 and CS 25100 in spring after recovery'],
            recommended_strategy="HIGHLY recommend taking CS 18200 in summer to stay on track. If not possible, retake in fall but this delays CS 25000/25100 to spring sophomore year, creating a bottleneck.",
            severity="Severe"
        )
        
        # CS 24000 Failure Scenarios
        scenarios['CS 24000_Spring_Freshman'] = FailureScenario(
            failed_course='CS 24000',
            failure_semester='Spring Freshman', 
            immediate_impact=['CS 25000', 'CS 25100'],
            long_term_impact=['CS 25200'],
            semester_delay=1,
            graduation_delay=1,
            summer_recovery_options=['Retake CS 24000 in summer'],
            fall_recovery_options=['Retake CS 24000 in fall'],
            spring_recovery_options=['Take CS 25200 after completing CS 25000/25100'],
            recommended_strategy="Take CS 24000 in summer if possible. Otherwise retake in fall and take CS 25000/25100 in spring sophomore (heavy load). CS 25200 will be delayed to fall junior.",
            severity="Moderate"
        )
        
        # CS 25000 Failure Scenarios
        scenarios['CS 25000_Fall_Sophomore'] = FailureScenario(
            failed_course='CS 25000',
            failure_semester='Fall Sophomore',
            immediate_impact=['CS 25200'],
            long_term_impact=[],
            semester_delay=1, 
            graduation_delay=0,  # Can catch up
            summer_recovery_options=[],  # Not offered in summer
            fall_recovery_options=['Retake CS 25000 next fall'],
            spring_recovery_options=['Take CS 25200 after retaking CS 25000'],
            recommended_strategy="Retake CS 25000 next fall. Take CS 25200 the following spring. Start upper-level courses as planned in junior year. Minimal impact if managed well.",
            severity="Minor"
        )
        
        # CS 25100 Failure Scenarios
        scenarios['CS 25100_Fall_Sophomore'] = FailureScenario(
            failed_course='CS 25100', 
            failure_semester='Fall Sophomore',
            immediate_impact=['CS 25200', 'CS 38100'],
            long_term_impact=['All track courses', 'Most upper-level CS'],
            semester_delay=1,
            graduation_delay=1,  # Significant impact
            summer_recovery_options=['Retake CS 25100 in summer'],
            fall_recovery_options=['Retake CS 25100 next fall'],
            spring_recovery_options=['Take CS 25200 after recovery'],
            recommended_strategy="CRITICAL: Take CS 25100 in summer if at all possible. This course blocks most upper-level CS. If summer not possible, retake in fall and delay track courses by one year.",
            severity="Critical"
        )
        
        # CS 25200 Failure Scenarios
        scenarios['CS 25200_Spring_Sophomore'] = FailureScenario(
            failed_course='CS 25200',
            failure_semester='Spring Sophomore', 
            immediate_impact=[],  # Doesn't block other foundation courses
            long_term_impact=['Some upper-level CS courses'],
            semester_delay=1,
            graduation_delay=0,  # Can usually catch up
            summer_recovery_options=[],  # Not typically offered
            fall_recovery_options=['Retake CS 25200 in fall'],
            spring_recovery_options=['Continue with track courses'],
            recommended_strategy="Retake CS 25200 in fall junior year. You can start some track courses that don't require CS 25200. Manageable delay.",
            severity="Moderate"
        )
        
        # Math Course Failures
        scenarios['MA 16100_Fall_Freshman'] = FailureScenario(
            failed_course='MA 16100',
            failure_semester='Fall Freshman',
            immediate_impact=['MA 16200', 'CS 18200'],
            long_term_impact=['MA 26100', 'MA 26500', 'CS 25000', 'CS 25100'],
            semester_delay=1,
            graduation_delay=1,
            summer_recovery_options=['Retake MA 16100 in summer'],
            fall_recovery_options=['Retake MA 16100 in fall'],
            spring_recovery_options=['Take MA 16200 and CS 18200 after recovery'],
            recommended_strategy="Take MA 16100 in summer to stay on track. If not possible, retake in spring and take MA 16200 in summer or following fall. This delays math sequence significantly.",
            severity="Severe"
        )
        
        scenarios['MA 16200_Spring_Freshman'] = FailureScenario(
            failed_course='MA 16200',
            failure_semester='Spring Freshman',
            immediate_impact=['MA 26100', 'STAT 35000'],
            long_term_impact=['MA 26500'],
            semester_delay=1,
            graduation_delay=0,  # Can usually catch up
            summer_recovery_options=['Retake MA 16200 in summer'],
            fall_recovery_options=['Retake MA 16200 in fall'],
            spring_recovery_options=['Continue with MA 26100 and MA 26500'],
            recommended_strategy="Retake MA 16200 in summer. Take MA 26100 in fall sophomore as planned. Alternatively, retake in fall and take MA 26100 in spring (less ideal).",
            severity="Moderate"
        )
        
        scenarios['MA 26100_Fall_Sophomore'] = FailureScenario(
            failed_course='MA 26100',
            failure_semester='Fall Sophomore',
            immediate_impact=[],
            long_term_impact=['Some upper-level CS courses requiring multivariate calculus'],
            semester_delay=1,
            graduation_delay=0,
            summer_recovery_options=['Retake MA 26100 in summer'],
            fall_recovery_options=['Retake MA 26100 next fall'],
            spring_recovery_options=['Continue with other courses'],
            recommended_strategy="Retake MA 26100 in summer or next fall. This mainly affects some specialized CS courses. Minimal impact on graduation timeline.",
            severity="Minor"
        )
        
        scenarios['MA 26500_Spring_Sophomore'] = FailureScenario(
            failed_course='MA 26500',
            failure_semester='Spring Sophomore',
            immediate_impact=[],
            long_term_impact=['Some upper-level CS courses requiring linear algebra'],
            semester_delay=1,
            graduation_delay=0,
            summer_recovery_options=['Retake MA 26500 in summer'],
            fall_recovery_options=['Retake MA 26500 in fall'],
            spring_recovery_options=['Continue with track courses'],
            recommended_strategy="Retake MA 26500 in summer or fall. Mainly affects some specialized CS and MI track courses. Usually doesn't delay graduation.",
            severity="Minor"
        )
        
        return scenarios
        
    def normalize_course_code(self, query: str) -> List[str]:
        """Enhanced course code extraction for all courses"""
        normalized_courses = []
        query_lower = query.lower()
        
        # First check for phrase-based mappings
        for phrase, course_code in self.course_mappings.items():
            if phrase in query_lower:
                normalized_courses.append(course_code)
        
        # Enhanced patterns for all courses
        patterns = [
            r'\bcs\s*(\d{3})\b',         # CS 182, CS 240
            r'\bcs\s*(\d{5})\b',         # CS 18200, CS 24000  
            r'\bma\s*(\d{3})\b',         # MA 161, MA 162
            r'\bma\s*(\d{5})\b',         # MA 16100, MA 16200
            r'\b(\d{3})\b',              # 182, 240, 161, 162
            r'\b(\d{5})\b'               # 18200, 24000, 16100
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query_lower)
            for match in matches:
                if match in self.course_mappings:
                    normalized_courses.append(self.course_mappings[match])
                elif len(match) == 3:
                    if match.startswith('1') or match.startswith('2'):
                        # CS courses
                        if match.startswith('18') or match.startswith('24') or match.startswith('25'):
                            normalized_courses.append(f"CS {match}00")
                        # Math courses  
                        elif match.startswith('16') or match.startswith('26'):
                            normalized_courses.append(f"MA {match}00")
                elif len(match) == 5:
                    if match.startswith('1') or match.startswith('2'):
                        if match.startswith('16') or match.startswith('26'):
                            normalized_courses.append(f"MA {match}")
                        else:
                            normalized_courses.append(f"CS {match}")
                            
        return list(dict.fromkeys(normalized_courses))  # Remove duplicates
        
    def determine_failure_semester(self, query: str, course: str) -> str:
        """Determine when the course failure occurred based on context"""
        query_lower = query.lower()
        
        # Get typical semester for course
        schedule = self.course_schedules.get(course)
        if not schedule:
            return "Unknown Semester"
        
        # Check for explicit semester mentions
        if 'fall' in query_lower:
            if 'freshman' in query_lower or 'fresh' in query_lower:
                return 'Fall Freshman'
            elif 'sophomore' in query_lower or 'soph' in query_lower:
                return 'Fall Sophomore'
            else:
                # Use typical year
                if schedule.typical_year == StudentYear.FRESHMAN:
                    return 'Fall Freshman' 
                else:
                    return 'Fall Sophomore'
                    
        elif 'spring' in query_lower:
            if 'freshman' in query_lower or 'fresh' in query_lower:
                return 'Spring Freshman'
            elif 'sophomore' in query_lower or 'soph' in query_lower:
                return 'Spring Sophomore'
            else:
                if schedule.typical_year == StudentYear.FRESHMAN:
                    return 'Spring Freshman'
                else:
                    return 'Spring Sophomore'
        
        # Default to typical semester for course
        if Semester.FALL in schedule.typical_semesters:
            if schedule.typical_year == StudentYear.FRESHMAN:
                return 'Fall Freshman'
            else:
                return 'Fall Sophomore'
        else:
            if schedule.typical_year == StudentYear.FRESHMAN:
                return 'Spring Freshman'
            else:
                return 'Spring Sophomore'
                
    def get_comprehensive_failure_analysis(self, failed_course: str, query: str) -> str:
        """Get comprehensive failure analysis for any course"""
        
        failure_semester = self.determine_failure_semester(query, failed_course)
        scenario_key = f"{failed_course}_{failure_semester.replace(' ', '_')}"
        
        scenario = self.failure_scenarios.get(scenario_key)
        
        if not scenario:
            # Generate basic scenario for unknown courses
            schedule = self.course_schedules.get(failed_course)
            if schedule:
                return self._generate_basic_failure_analysis(failed_course, failure_semester, schedule)
            else:
                return f"Unable to analyze failure scenario for {failed_course}. Course not found in knowledge base."
        
        # Generate detailed response
        response = f"**If you fail {failed_course} in {failure_semester.lower()}:**\n\n"
        
        # Immediate impact
        if scenario.immediate_impact:
            response += "**Immediate Impact (Next Semester):**\n"
            for course in scenario.immediate_impact:
                response += f"❌ Cannot take {course}\n"
            response += "\n"
        
        # Long-term impact
        if scenario.long_term_impact:
            response += "**Long-term Impact:**\n"
            for course in scenario.long_term_impact:
                response += f"⚠️ Delayed: {course}\n"
            response += "\n"
        
        # Semester delay info
        response += f"**Timeline Impact:**\n"
        response += f"• Semester delay: {scenario.semester_delay} semester(s)\n"
        if scenario.graduation_delay > 0:
            response += f"• Graduation delay: {scenario.graduation_delay} semester(s)\n"
        else:
            response += f"• Graduation delay: Can potentially catch up with good planning\n"
        response += f"• Severity: {scenario.severity}\n\n"
        
        # Recovery options
        response += "**Recovery Options:**\n"
        
        if scenario.summer_recovery_options:
            response += f"🌞 **Summer Options:** {', '.join(scenario.summer_recovery_options)}\n"
        else:
            response += f"🌞 **Summer:** {failed_course} not typically offered in summer\n"
            
        if scenario.fall_recovery_options:
            response += f"🍂 **Fall Options:** {', '.join(scenario.fall_recovery_options)}\n"
            
        if scenario.spring_recovery_options:
            response += f"🌸 **Spring Options:** {', '.join(scenario.spring_recovery_options)}\n"
        
        response += f"\n**Recommended Strategy:**\n{scenario.recommended_strategy}\n"
        
        # Add course difficulty context
        schedule = self.course_schedules.get(failed_course)
        if schedule:
            response += f"\n**Course Info:**\n"
            response += f"• Difficulty: {schedule.difficulty_level}\n"
            response += f"• Time commitment: {schedule.time_commitment}\n"
            response += f"• Typical timing: {schedule.typical_year.value} year, {'/'.join([s.value for s in schedule.typical_semesters])}\n"
        
        return response
        
    def _generate_basic_failure_analysis(self, course: str, failure_semester: str, schedule: CourseSchedule) -> str:
        """Generate basic analysis for courses without specific scenarios"""
        
        response = f"**If you fail {course} in {failure_semester.lower()}:**\n\n"
        response += f"**Course Info:**\n"
        response += f"• Difficulty: {schedule.difficulty_level}\n" 
        response += f"• Time commitment: {schedule.time_commitment}\n"
        response += f"• Typical timing: {schedule.typical_year.value} year\n\n"
        
        response += "**Recovery Options:**\n"
        if schedule.summer_available:
            response += f"🌞 **Summer:** Available - recommended for faster recovery\n"
        else:
            response += f"🌞 **Summer:** Not typically offered\n"
            
        response += f"🍂 **Fall:** Available if typically offered in fall\n"
        response += f"🌸 **Spring:** Available if typically offered in spring\n"
        
        response += f"\n**Recommended Strategy:**\n"
        if schedule.summer_available:
            response += f"Take {course} in summer to minimize delays. "
        response += f"Plan course sequence carefully to minimize impact on graduation timeline."
        
        return response

    def analyze_failure_query(self, query: str) -> str:
        """Main method to analyze any course failure query"""
        
        # Extract failed courses from query
        detected_courses = self.normalize_course_code(query)
        
        if not detected_courses:
            return "I couldn't identify which course you're asking about. Please specify the course code (e.g., CS 18000, CS 182, MA 16100, Calc 1)."
        
        if len(detected_courses) == 1:
            # Single course failure
            failed_course = detected_courses[0]
            return self.get_comprehensive_failure_analysis(failed_course, query)
        else:
            # Multiple course failures
            response = f"**Multiple Course Failure Analysis:**\n\n"
            for course in detected_courses:
                response += f"{'='*50}\n"
                response += self.get_comprehensive_failure_analysis(course, query)
                response += f"\n{'='*50}\n\n"
            return response

# Test function
def test_comprehensive_analyzer():
    """Test the comprehensive failure analyzer"""
    analyzer = ComprehensiveFailureAnalyzer()
    
    test_queries = [
        "What happens if I fail CS 18000 in fall semester?",
        "I failed CS 25100, how does this affect my timeline?", 
        "If I fail calc 1 what should I do?",
        "What if I fail CS 18200 and need to retake it?",
        "I might fail MA 16200 this spring",
        "Failed CS 24000, can I take it in summer?",
        "What happens if I fail CS 25000?",
        "I failed linear algebra, what now?",
        "If I fail both CS 182 and calc 2?",
        "What if I fail CS 25200 in spring sophomore year?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print(f"{'='*80}")
        response = analyzer.analyze_failure_query(query)
        print(response)
        
if __name__ == "__main__":
    test_comprehensive_analyzer()