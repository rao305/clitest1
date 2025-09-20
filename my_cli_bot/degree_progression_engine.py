"""
Degree Progression Engine - Provides accurate semester-by-semester course recommendations
Based on official Purdue CS 2025-2026 Degree Progression Guide
"""
import json
import logging
from typing import Dict, List, Optional, Tuple

class DegreeProgressionEngine:
    def __init__(self, knowledge_path: str = "data/cs_knowledge_graph.json"):
        """Initialize with knowledge base and progression guide data"""
        try:
            with open(knowledge_path, 'r') as f:
                self.knowledge = json.load(f)
        except FileNotFoundError:
            logging.error(f"Knowledge base not found at {knowledge_path}")
            self.knowledge = {}
        
        # Official Purdue CS Progression Guide (2025-2026)
        self.progression_guide = {
            "freshman_fall": {
                "semester": "Fall 1st Year",
                "year_level": "freshman",
                "courses": [
                    {"code": "CS 18000", "credits": 4, "type": "foundation", "critical": True},
                    {"code": "CS 19300", "credits": 1, "type": "optional", "note": "Tools - recommended"},
                    {"code": "MA 16100", "credits": 5, "type": "math", "alternative": "MA 16500", "critical": True},
                    {"code": "SCIENCE_CORE", "credits": 3, "type": "science_core", "flexible": True},
                    {"code": "FREE_ELECTIVE", "credits": 1, "type": "elective", "flexible": True}
                ],
                "total_credits": "14-16",
                "cs_course_limit": 2,
                "focus": "Foundation building and adjustment to university"
            },
            "freshman_spring": {
                "semester": "Spring 1st Year", 
                "year_level": "freshman",
                "courses": [
                    {"code": "CS 18200", "credits": 3, "type": "foundation", "critical": True, "prereq": ["CS 18000", "MA 16100"]},
                    {"code": "CS 24000", "credits": 3, "type": "foundation", "critical": True, "prereq": ["CS 18000"]},
                    {"code": "MA 16200", "credits": 5, "type": "math", "alternative": "MA 16600", "critical": True, "prereq": ["MA 16100"]},
                    {"code": "SCIENCE_CORE", "credits": 3, "type": "science_core", "flexible": True},
                    {"code": "FREE_ELECTIVE", "credits": 1, "type": "elective", "flexible": True}
                ],
                "total_credits": "15-16",
                "cs_course_limit": 2,
                "focus": "Continue foundation sequence, parallel math progression"
            },
            "sophomore_fall": {
                "semester": "Fall 2nd Year",
                "year_level": "sophomore", 
                "courses": [
                    {"code": "CS 25000", "credits": 4, "type": "foundation", "critical": True, "prereq": ["CS 18200", "CS 24000"]},
                    {"code": "CS 25100", "credits": 3, "type": "foundation", "critical": True, "prereq": ["CS 18200", "CS 24000"]},
                    {"code": "MA 26100", "credits": 4, "type": "math", "alternative": "MA 27101", "critical": True, "prereq": ["MA 16200"]},
                    {"code": "SCIENCE_CORE", "credits": 3, "type": "science_core", "flexible": True},
                    {"code": "CS 29100", "credits": 1, "type": "optional", "note": "Sophomore seminar - recommended"}
                ],
                "total_credits": "15-16", 
                "cs_course_limit": 3,
                "focus": "Core CS architecture and algorithms, critical for upper-level courses"
            },
            "sophomore_spring": {
                "semester": "Spring 2nd Year",
                "year_level": "sophomore",
                "courses": [
                    {"code": "CS 25200", "credits": 4, "type": "foundation", "critical": True, "prereq": ["CS 25000", "CS 25100"]},
                    {"code": "MA 26500", "credits": 3, "type": "math", "alternative": "MA 35100", "critical": True, "prereq": ["MA 16200"]},
                    {"code": "SCIENCE_CORE", "credits": 3, "type": "science_core", "note": "COM 21700 recommended"},
                    {"code": "SCIENCE_CORE", "credits": 3, "type": "science_core", "flexible": True},
                    {"code": "FREE_ELECTIVE", "credits": 3, "type": "elective", "flexible": True}
                ],
                "total_credits": "16-17",
                "cs_course_limit": 3,
                "focus": "Systems programming - completes core foundation sequence"
            },
            "junior_fall": {
                "semester": "Fall 3rd Year",
                "year_level": "junior",
                "courses": [
                    {"code": "CS_TRACK_REQ", "credits": 3, "type": "track_requirement", "note": "First track requirement (e.g., CS 38100 for MI/SE)"},
                    {"code": "CS_TRACK_REQ", "credits": 3, "type": "track_requirement", "note": "Second track requirement"},
                    {"code": "STAT 35000", "credits": 3, "type": "statistics", "alternative": "STAT 51100", "prereq": ["MA 16200"]},
                    {"code": "SCIENCE_CORE", "credits": 3, "type": "science_core", "flexible": True},
                    {"code": "FREE_ELECTIVE", "credits": 3, "type": "elective", "flexible": True},
                    {"code": "CS 39100", "credits": 1, "type": "optional", "note": "Junior seminar - recommended"}
                ],
                "total_credits": "16-17",
                "cs_course_limit": 3,
                "focus": "Track specialization begins - choose MI, SE, or other track"
            },
            "junior_spring": {
                "semester": "Spring 3rd Year", 
                "year_level": "junior",
                "courses": [
                    {"code": "CS_TRACK_REQ", "credits": 3, "type": "track_requirement", "note": "Track requirement or elective"},
                    {"code": "CS_TRACK_REQ", "credits": 3, "type": "track_requirement", "note": "Track requirement or elective"},
                    {"code": "SCIENCE_CORE", "credits": 3, "type": "science_core", "flexible": True},
                    {"code": "SCIENCE_CORE", "credits": 3, "type": "science_core", "flexible": True},
                    {"code": "FREE_ELECTIVE", "credits": 3, "type": "elective", "flexible": True}
                ],
                "total_credits": "15-17",
                "cs_course_limit": 3,
                "focus": "Continue track specialization, complete science requirements"
            },
            "senior_fall": {
                "semester": "Fall 4th Year",
                "year_level": "senior",
                "courses": [
                    {"code": "CS_TRACK_ELECTIVE", "credits": 3, "type": "track_elective", "note": "Track elective course"},
                    {"code": "SCIENCE_CORE", "credits": 3, "type": "science_core", "flexible": True},
                    {"code": "SCIENCE_CORE", "credits": 3, "type": "science_core", "flexible": True},
                    {"code": "FREE_ELECTIVE", "credits": 3, "type": "elective", "flexible": True},
                    {"code": "FREE_ELECTIVE", "credits": 3, "type": "elective", "flexible": True}
                ],
                "total_credits": "15-17",
                "cs_course_limit": 2,
                "focus": "Complete track requirements, finish general requirements"
            },
            "senior_spring": {
                "semester": "Spring 4th Year",
                "year_level": "senior", 
                "courses": [
                    {"code": "CS_TRACK_ELECTIVE", "credits": 3, "type": "track_elective", "note": "Track elective course"},
                    {"code": "SCIENCE_CORE", "credits": 3, "type": "science_core", "flexible": True},
                    {"code": "SCIENCE_CORE", "credits": 3, "type": "science_core", "flexible": True},
                    {"code": "FREE_ELECTIVE", "credits": 3, "type": "elective", "flexible": True},
                    {"code": "FREE_ELECTIVE", "credits": 3, "type": "elective", "flexible": True}
                ],
                "total_credits": "15-17",
                "cs_course_limit": 2,
                "focus": "Final track requirements, graduation preparation"
            }
        }

    def get_semester_courses(self, student_year: str, semester: str) -> Dict:
        """Get recommended courses for specific semester based on official progression guide"""
        semester_key = f"{student_year}_{semester.lower()}"
        
        if semester_key not in self.progression_guide:
            return {"error": "Invalid semester combination"}
        
        return self.progression_guide[semester_key]
    
    def get_foundation_courses_by_semester(self, student_year: str, semester: str) -> List[Dict]:
        """Get foundation CS courses for specific semester"""
        semester_data = self.get_semester_courses(student_year, semester)
        
        if "error" in semester_data:
            return []
        
        foundation_courses = []
        for course in semester_data["courses"]:
            if course["type"] == "foundation":
                # Get detailed course info from knowledge base
                course_code = course["code"]
                if course_code in self.knowledge.get("courses", {}):
                    course_info = self.knowledge["courses"][course_code].copy()
                    course_info.update(course)
                    foundation_courses.append(course_info)
                else:
                    foundation_courses.append(course)
        
        return foundation_courses
    
    def analyze_student_progress(self, current_year: str, current_semester: str, completed_courses: List[str] = None) -> Dict:
        """Analyze student's current progress and recommend next courses"""
        if completed_courses is None:
            completed_courses = []
        
        current_semester_data = self.get_semester_courses(current_year, current_semester)
        if "error" in current_semester_data:
            return {"error": "Invalid semester"}
        
        recommendations = {
            "current_semester": current_semester_data["semester"],
            "year_level": current_semester_data["year_level"], 
            "foundation_courses": [],
            "other_courses": [],
            "course_load_guidance": {
                "max_credits": current_semester_data["total_credits"],
                "cs_course_limit": current_semester_data["cs_course_limit"],
                "focus": current_semester_data["focus"]
            },
            "prerequisites_needed": [],
            "warnings": []
        }
        
        # Analyze each recommended course
        for course in current_semester_data["courses"]:
            course_code = course["code"]
            
            # Skip if already completed
            if course_code in completed_courses:
                continue
                
            # Check prerequisites if specified
            if "prereq" in course and course["prereq"]:
                missing_prereqs = [p for p in course["prereq"] if p not in completed_courses]
                if missing_prereqs:
                    recommendations["prerequisites_needed"].append({
                        "course": course_code,
                        "missing_prereqs": missing_prereqs
                    })
                    continue
            
            # Add to appropriate category
            if course["type"] == "foundation":
                recommendations["foundation_courses"].append(course)
            else:
                recommendations["other_courses"].append(course)
        
        return recommendations
    
    def get_summer_acceleration_options(self, student_year: str) -> List[Dict]:
        """Recommend summer courses for acceleration or catch-up"""
        summer_options = {
            "freshman": [
                {"code": "CS 18000", "reason": "Get ahead on foundation sequence", "intensity": "high"},
                {"code": "CS 18200", "reason": "Accelerate theoretical foundations", "intensity": "medium", "prereq": ["CS 18000"]},
                {"code": "MA 16200", "reason": "Advance in math sequence", "intensity": "high", "prereq": ["MA 16100"]}
            ],
            "sophomore": [
                {"code": "CS 24000", "reason": "Catch up on C programming", "intensity": "medium", "prereq": ["CS 18000"]},
                {"code": "CS 25000", "reason": "Accelerate architecture course", "intensity": "high", "prereq": ["CS 18200", "CS 24000"]},
                {"code": "CS 25100", "reason": "Critical for upper-level courses", "intensity": "very_high", "prereq": ["CS 18200", "CS 24000"]},
                {"code": "MA 26100", "reason": "Complete multivariate calculus", "intensity": "high", "prereq": ["MA 16200"]}
            ],
            "junior": [
                {"code": "CS 38100", "reason": "Track requirement for MI/SE", "intensity": "high", "prereq": ["CS 25100"]},
                {"code": "CS 37300", "reason": "MI track requirement", "intensity": "high", "prereq": ["CS 25100", "STAT 35000"]},
                {"code": "STAT 35000", "reason": "Required for many track courses", "intensity": "medium", "prereq": ["MA 16200"]}
            ],
            "senior": [
                {"code": "CS_TRACK_ELECTIVES", "reason": "Complete track requirements", "intensity": "medium"},
                {"code": "CAPSTONE", "reason": "Senior project or thesis", "intensity": "high"}
            ]
        }
        
        return summer_options.get(student_year, [])
    
    def calculate_failure_impact(self, failed_course: str, current_semester: str) -> Dict:
        """Calculate impact of course failure on graduation timeline"""
        if failed_course not in self.knowledge.get("failure_recovery_scenarios", {}):
            return {"error": f"No failure data available for {failed_course}"}
        
        failure_data = self.knowledge["failure_recovery_scenarios"][failed_course]
        
        return {
            "failed_course": failed_course,
            "delay_semesters": failure_data.get("delay_semesters", 0),
            "affected_courses": failure_data.get("affected_courses", []),
            "recovery_strategy": failure_data.get("recovery_strategy", ""),
            "summer_recovery_possible": failure_data.get("summer_option", False),
            "difficulty_level": failure_data.get("difficulty", "Unknown"),
            "graduation_impact": failure_data.get("graduation_impact", "Impact unknown"),
            "next_steps": self._generate_recovery_plan(failed_course, failure_data)
        }
    
    def _generate_recovery_plan(self, failed_course: str, failure_data: Dict) -> List[str]:
        """Generate specific recovery steps for failed course"""
        steps = []
        
        if failure_data.get("summer_option"):
            steps.append(f"Retake {failed_course} in summer to minimize delay")
            
        if failure_data.get("delay_semesters", 0) > 0:
            steps.append(f"Expect {failure_data['delay_semesters']} semester delay in progression")
            
        affected_courses = failure_data.get("affected_courses", [])
        if affected_courses:
            steps.append(f"Plan alternative courses while waiting to retake prerequisites")
            steps.append("Focus on math, science core, and general education requirements")
            
        if failed_course in ["CS 25100", "CS 18000"]:
            steps.append("Consider tutoring or supplemental instruction before retaking")
            steps.append("This course is critical for CS progression - ensure mastery")
            
        return steps
    
    def get_track_specific_guidance(self, track: str, student_year: str) -> Dict:
        """Get track-specific course recommendations"""
        if track not in self.knowledge.get("tracks", {}):
            return {"error": f"Track '{track}' not found"}
        
        track_data = self.knowledge["tracks"][track]
        
        guidance = {
            "track_name": track,
            "track_code": track_data.get("track_code", ""),
            "description": track_data.get("description", ""),
            "total_credits": track_data.get("total_credits", 0),
            "core_requirements": track_data.get("core_required", []),
            "recommended_sequence": [],
            "career_preparation": [],
            "course_structure": {}
        }
        
        # Add specific course structure for each track
        if track == "Software Engineering":
            core_count = len(track_data.get("core_required", []))
            systems_options = len(track_data.get("choose_one_systems", []))
            elective_options = len(track_data.get("choose_one_elective", []))
            
            guidance["course_structure"] = {
                "core_courses": f"{core_count} required courses",
                "systems_course": f"Choose 1 from {systems_options} options",
                "elective_course": f"Choose 1 from {elective_options} options",
                "total_courses": core_count + 1 + 1,
                "structure_note": "4 core + 1 systems choice + 1 elective choice = 6 total courses"
            }
        elif track == "Machine Intelligence":
            core_count = len(track_data.get("core_required", []))
            elective_count = track_data.get("electives_required", 2)
            
            guidance["course_structure"] = {
                "core_courses": f"{core_count} required courses",
                "elective_courses": f"Choose {elective_count} electives",
                "ai_course": "Choose 1 AI course option",
                "probability_course": "Choose 1 probability/statistics course",
                "total_courses": core_count + elective_count + 2,
                "structure_note": f"{core_count} core + {elective_count} electives + AI + stats = 6 total courses"
            }
        
        # Add year-specific recommendations
        if student_year == "junior":
            guidance["recommended_sequence"] = [
                "Start with core track requirements (e.g., CS 38100 for MI/SE)",
                "Take fundamental track courses first",
                "Plan electives for senior year"
            ]
        elif student_year == "senior":
            guidance["recommended_sequence"] = [
                "Complete remaining track requirements", 
                "Choose specialized electives",
                "Consider capstone or research project"
            ]
        
        return guidance

def get_accurate_semester_recommendation(student_year: str, semester: str, completed_courses: List[str] = None) -> str:
    """Generate accurate semester recommendations using official progression guide"""
    engine = DegreeProgressionEngine()
    
    # Get official progression data
    analysis = engine.analyze_student_progress(student_year, semester, completed_courses or [])
    
    if "error" in analysis:
        return f"I need to know your current year level to provide accurate course recommendations. Are you a freshman, sophomore, junior, or senior?"
    
    # Build response using actual data
    response_parts = []
    
    # Semester context
    response_parts.append(f"For {analysis['current_semester']} as a {analysis['year_level']}, here are your recommended courses based on the official Purdue CS progression guide:")
    
    # Foundation courses (most important)
    if analysis["foundation_courses"]:
        response_parts.append("\n**Foundation CS Courses (Priority):**")
        for course in analysis["foundation_courses"]:
            course_details = f"• {course['code']} - {course.get('title', 'Course')} ({course['credits']} credits)"
            if course.get("critical"):
                course_details += " [CRITICAL]"
            if "note" in course:
                course_details += f" - {course['note']}"
            response_parts.append(course_details)
    
    # Other required courses
    if analysis["other_courses"]:
        response_parts.append("\n**Other Required Courses:**")
        for course in analysis["other_courses"]:
            course_details = f"• {course['code']}"
            if course["code"] != "SCIENCE_CORE" and course["code"] != "FREE_ELECTIVE":
                course_details += f" ({course['credits']} credits)"
            if "note" in course:
                course_details += f" - {course['note']}"
            response_parts.append(course_details)
    
    # Course load guidance
    guidance = analysis["course_load_guidance"]
    response_parts.append(f"\n**Course Load Guidelines:**")
    response_parts.append(f"• Maximum recommended credits: {guidance['max_credits']}")
    response_parts.append(f"• Maximum CS courses: {guidance['cs_course_limit']}")
    response_parts.append(f"• Semester focus: {guidance['focus']}")
    
    # Prerequisites warnings
    if analysis["prerequisites_needed"]:
        response_parts.append("\n**[WARNING] Prerequisites Needed:**")
        for prereq_info in analysis["prerequisites_needed"]:
            response_parts.append(f"• For {prereq_info['course']}: Need {', '.join(prereq_info['missing_prereqs'])}")
    
    return "\n".join(response_parts)

# Test the system
if __name__ == "__main__":
    # Test sophomore spring scenario
    result = get_accurate_semester_recommendation("sophomore", "spring", ["CS 18000", "CS 18200", "CS 24000", "CS 25000", "CS 25100", "MA 16100", "MA 16200"])
    print("Test Result:")
    print(result)