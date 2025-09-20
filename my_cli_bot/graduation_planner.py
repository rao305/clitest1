#!/usr/bin/env python3
"""
Advanced Graduation Planner for Purdue CS Students
Handles Machine Intelligence and Software Engineering tracks
Includes early graduation and delay scenarios
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class CourseSchedule:
    semester: str
    year: int
    courses: List[str]
    total_credits: int
    cs_credits: int

@dataclass
class GraduationPlan:
    track: str
    total_semesters: int
    graduation_date: str
    schedules: List[CourseSchedule]
    warnings: List[str]
    success_probability: float

class AdvancedGraduationPlanner:
    def __init__(self, knowledge_file: str, db_file: str):
        with open(knowledge_file, 'r') as f:
            self.knowledge = json.load(f)
        self.db_file = db_file
        
        # Foundation courses that cause delays if failed
        self.critical_foundation = ["CS 18000", "CS 18200", "CS 24000", "CS 25000", "CS 25100", "CS 25200"]
        self.critical_math = ["MA 16100", "MA 16200", "MA 26100", "MA 26500"]
        
        # Track-specific requirements
        self.mi_track_requirements = {
            "required": ["CS 37300", "CS 38100"],
            "ai_choice": ["CS 47100", "CS 47300"],
            "stats_choice": ["STAT 41600", "MA 41600", "STAT 51200"],
            "electives": 2
        }
        
        self.se_track_requirements = {
            "required": ["CS 30700", "CS 38100", "CS 40700", "CS 40800"],
            "compiler_os_choice": ["CS 35200", "CS 35400"],
            "electives": 1
        }

    def analyze_foundation_delay_scenario(self, failed_course: str, current_semester: int) -> Dict:
        """
        Analyzes graduation delay caused by failing a foundation course
        """
        scenarios = {
            "CS 18000": {
                "delay_semesters": 2,
                "affected_courses": ["CS 18200", "CS 24000", "CS 25000", "CS 25100", "CS 25200"],
                "recovery_strategy": "Retake immediately next semester, pushes entire sequence back",
                "summer_option": True,
                "difficulty": "High - affects entire CS sequence"
            },
            "CS 18200": {
                "delay_semesters": 1,
                "affected_courses": ["CS 25000", "CS 25100", "CS 25200"],
                "recovery_strategy": "Can retake concurrently with CS 24000 if needed",
                "summer_option": True,
                "difficulty": "Medium - some recovery possible"
            },
            "CS 24000": {
                "delay_semesters": 1,
                "affected_courses": ["CS 25000", "CS 25100", "CS 25200"],
                "recovery_strategy": "Retake next semester, minimal delay if caught early",
                "summer_option": True,
                "difficulty": "Medium - manageable with summer courses"
            },
            "CS 25000": {
                "delay_semesters": 1,
                "affected_courses": ["CS 25200"],
                "recovery_strategy": "Can still take CS 25100, retake CS 25000 next semester",
                "summer_option": True,
                "difficulty": "Low - minimal impact on sequence"
            },
            "CS 25100": {
                "delay_semesters": 1,
                "affected_courses": ["CS 25200", "CS 38100", "All track courses"],
                "recovery_strategy": "Critical course - affects all upper-level CS",
                "summer_option": True,
                "difficulty": "High - blocks most CS progression"
            },
            "CS 25200": {
                "delay_semesters": 1,
                "affected_courses": ["CS 30700", "CS 35100", "CS 35400", "CS 42200"],
                "recovery_strategy": "Affects systems track courses primarily",
                "summer_option": True,
                "difficulty": "Medium - mainly affects systems courses"
            }
        }
        
        if failed_course not in scenarios:
            return {"error": "Course not recognized as critical foundation course"}
            
        scenario = scenarios[failed_course]
        
        # Calculate graduation delay
        base_graduation = 8  # semesters
        delay = scenario["delay_semesters"]
        
        # Add summer recovery options
        if scenario["summer_option"] and current_semester <= 6:
            recovery_plan = self._generate_summer_recovery_plan(failed_course, current_semester)
            scenario["summer_recovery"] = recovery_plan
            
        scenario["new_graduation_timeline"] = base_graduation + delay
        scenario["failed_at_semester"] = current_semester
        
        return scenario

    def generate_early_graduation_plan(self, track: str, skip_cs180: bool = False) -> GraduationPlan:
        """
        Generates early graduation plan (3.5 years) with optional CS 180 skip
        """
        if track not in ["Machine Intelligence", "Software Engineering"]:
            raise ValueError("Invalid track specified")
            
        schedules = []
        warnings = []
        
        # Early graduation strategy: 18+ credits per semester, strategic summer courses
        if skip_cs180:
            warnings.append("Skipping CS 180 requires strong programming background")
            warnings.append("Must demonstrate CS 180 competency through placement exam or prior experience")
            
            # Modified first year without CS 180
            fall_1 = CourseSchedule("Fall", 1, ["CS 18200", "MA 16100", "ENGL 10600", "General Ed"], 17, 3)
            spring_1 = CourseSchedule("Spring", 1, ["CS 24000", "MA 16200", "General Ed", "General Ed"], 16, 3)
            summer_1 = CourseSchedule("Summer", 1, ["CS 25000", "CS 25100"], 7, 7)
        else:
            # Standard accelerated sequence
            fall_1 = CourseSchedule("Fall", 1, ["CS 18000", "MA 16100", "ENGL 10600", "General Ed"], 18, 4)
            spring_1 = CourseSchedule("Spring", 1, ["CS 18200", "CS 24000", "MA 16200", "General Ed"], 17, 7)
            summer_1 = CourseSchedule("Summer", 1, ["CS 25000", "CS 25100"], 7, 7)
        
        schedules.extend([fall_1, spring_1, summer_1])
        
        # Second year - heavy CS load
        fall_2 = CourseSchedule("Fall", 2, ["CS 25200", "CS 38100", "MA 26100", "STAT 35000"], 18, 7)
        spring_2 = CourseSchedule("Spring", 2, ["CS 35100", "MA 26500", "PHYS 17200", "General Ed"], 17, 3)
        
        schedules.extend([fall_2, spring_2])
        
        # Third year - track specialization
        if track == "Machine Intelligence":
            fall_3 = CourseSchedule("Fall", 3, ["CS 37300", "CS 47100", "STAT 41600", "General Ed"], 18, 6)
            spring_3 = CourseSchedule("Spring", 3, ["CS Track Elective 1", "CS Track Elective 2", "PHYS 27200", "Free Elective"], 16, 6)
        else:  # Software Engineering
            fall_3 = CourseSchedule("Fall", 3, ["CS 30700", "CS 35200", "CS 40800", "General Ed"], 18, 9)
            spring_3 = CourseSchedule("Spring", 3, ["CS 40700", "CS Track Elective", "PHYS 27200", "Free Elective"], 16, 6)
            
        schedules.extend([fall_3, spring_3])
        
        # Calculate success probability
        success_factors = {
            "high_credit_load": -0.2,  # 18+ credits is challenging
            "summer_courses": -0.1,    # Summer intensity
            "skip_cs180": -0.3 if skip_cs180 else 0,  # Skipping foundation is risky
            "track_focus": 0.1         # Focused track helps
        }
        
        base_probability = 0.7
        success_probability = base_probability + sum(success_factors.values())
        success_probability = max(0.1, min(0.9, success_probability))
        
        if success_probability < 0.5:
            warnings.append("Low success probability - consider standard 4-year plan")
            
        return GraduationPlan(
            track=track,
            total_semesters=7,
            graduation_date="Spring Year 4",
            schedules=schedules,
            warnings=warnings,
            success_probability=success_probability
        )

    def calculate_course_load_limits(self, semester_type: str, student_level: str) -> Dict:
        """
        Calculates recommended course loads with CS course limits
        """
        limits = {
            "regular_semester": {
                "freshman": {"total": 16, "cs_max": 2, "recommended_cs": 1},
                "sophomore": {"total": 18, "cs_max": 3, "recommended_cs": 2},
                "junior": {"total": 18, "cs_max": 3, "recommended_cs": 2},
                "senior": {"total": 15, "cs_max": 2, "recommended_cs": 2}
            },
            "summer": {
                "any_level": {"total": 9, "cs_max": 2, "recommended_cs": 1}
            }
        }
        
        if semester_type == "summer":
            return limits["summer"]["any_level"]
        else:
            return limits["regular_semester"].get(student_level, limits["regular_semester"]["sophomore"])

    def _generate_summer_recovery_plan(self, failed_course: str, current_semester: int) -> Dict:
        """
        Generates summer course recovery strategy
        """
        summer_strategies = {
            "CS 18000": {
                "courses": ["CS 18000"],
                "additional_prep": ["Programming bootcamp", "CS 180 equivalent online"],
                "timeline": "Retake in summer, continue sequence in fall"
            },
            "CS 18200": {
                "courses": ["CS 18200", "CS 24000"],
                "additional_prep": ["Discrete math review"],
                "timeline": "Double up in summer to catch up"
            },
            "CS 24000": {
                "courses": ["CS 24000", "Elective"],
                "additional_prep": ["C programming practice"],
                "timeline": "Retake with lighter summer load"
            },
            "CS 25000": {
                "courses": ["CS 25000", "Math requirement"],
                "additional_prep": ["Computer architecture fundamentals"],
                "timeline": "Pair with math to stay on track"
            },
            "CS 25100": {
                "courses": ["CS 25100"],
                "additional_prep": ["Data structures and algorithms review"],
                "timeline": "Focus solely on this critical course"
            },
            "CS 25200": {
                "courses": ["CS 25200", "CS 35100"],
                "additional_prep": ["Systems programming concepts"],
                "timeline": "Can accelerate with cloud computing"
            }
        }
        
        return summer_strategies.get(failed_course, {"error": "No summer strategy available"})

    def generate_comprehensive_plan(self, student_profile: Dict) -> Dict:
        """
        Generates comprehensive graduation plan based on student profile
        """
        track = student_profile.get("track", "Machine Intelligence")
        current_semester = student_profile.get("current_semester", 1)
        failed_courses = student_profile.get("failed_courses", [])
        early_graduation = student_profile.get("early_graduation", False)
        skip_cs180 = student_profile.get("skip_cs180", False)
        
        plan = {
            "student_profile": student_profile,
            "timestamp": datetime.now().isoformat(),
            "scenarios": {}
        }
        
        # Standard graduation plan
        if not early_graduation and not failed_courses:
            plan["scenarios"]["standard"] = self._generate_standard_plan(track)
        
        # Early graduation scenario
        if early_graduation:
            plan["scenarios"]["early"] = self.generate_early_graduation_plan(track, skip_cs180)
        
        # Delay scenarios for failed courses
        if failed_courses:
            plan["scenarios"]["delay"] = {}
            for course in failed_courses:
                delay_scenario = self.analyze_foundation_delay_scenario(course, current_semester)
                plan["scenarios"]["delay"][course] = delay_scenario
        
        # Course load recommendations
        plan["course_load_guidelines"] = {
            "maximum_cs_per_semester": 3,
            "recommended_cs_per_semester": 2,
            "summer_course_strategy": "1-2 courses to accelerate or recover",
            "track_course_timing": "Begin in Fall junior year"
        }
        
        # Track-specific guidance
        if track == "Machine Intelligence":
            plan["track_guidance"] = {
                "math_emphasis": "Strong statistics background crucial",
                "programming_skills": "Python, R for data analysis",
                "career_prep": "Research/industry internships in ML/AI",
                "course_recommendations": {
                    "CS 47100": "Better for research/graduate school",
                    "CS 47300": "Better for industry applications"
                }
            }
        else:  # Software Engineering
            plan["track_guidance"] = {
                "project_emphasis": "Senior project is capstone requirement",
                "programming_skills": "Large-scale software development",
                "career_prep": "Software engineering internships",
                "course_recommendations": {
                    "CS 35200": "Better for compiler/language work",
                    "CS 35400": "Better for systems programming"
                }
            }
        
        return plan

    def _generate_standard_plan(self, track: str) -> GraduationPlan:
        """
        Generates standard 4-year graduation plan
        """
        schedules = []
        
        # Standard 4-year sequence with reasonable loads
        fall_1 = CourseSchedule("Fall", 1, ["CS 18000", "MA 16100", "ENGL 10600", "General Ed"], 16, 4)
        spring_1 = CourseSchedule("Spring", 1, ["CS 18200", "CS 24000", "MA 16200", "General Ed"], 16, 7)
        
        fall_2 = CourseSchedule("Fall", 2, ["CS 25000", "CS 25100", "MA 26100", "General Ed"], 16, 7)
        spring_2 = CourseSchedule("Spring", 2, ["CS 25200", "MA 26500", "STAT 35000", "General Ed"], 16, 3)
        
        fall_3 = CourseSchedule("Fall", 3, ["CS 35100", "CS 38100", "PHYS 17200", "General Ed"], 16, 6)
        
        if track == "Machine Intelligence":
            spring_3 = CourseSchedule("Spring", 3, ["CS 37300", "CS 47100", "PHYS 27200", "Free Elective"], 16, 6)
            fall_4 = CourseSchedule("Fall", 4, ["STAT 41600", "CS Track Elective 1", "Free Elective", "General Ed"], 15, 3)
            spring_4 = CourseSchedule("Spring", 4, ["CS Track Elective 2", "Free Elective", "Free Elective", "General Ed"], 15, 3)
        else:  # Software Engineering
            spring_3 = CourseSchedule("Spring", 3, ["CS 30700", "CS 35200", "PHYS 27200", "Free Elective"], 16, 6)
            fall_4 = CourseSchedule("Fall", 4, ["CS 40800", "CS Track Elective", "Free Elective", "General Ed"], 15, 6)
            spring_4 = CourseSchedule("Spring", 4, ["CS 40700", "Free Elective", "Free Elective", "General Ed"], 15, 3)
        
        schedules = [fall_1, spring_1, fall_2, spring_2, fall_3, spring_3, fall_4, spring_4]
        
        return GraduationPlan(
            track=track,
            total_semesters=8,
            graduation_date="Spring Year 4",
            schedules=schedules,
            warnings=["Standard timeline - manageable course loads"],
            success_probability=0.85
        )

def main():
    """
    Example usage of the graduation planner
    """
    planner = AdvancedGraduationPlanner(
        "data/cs_knowledge_graph.json",
        "purdue_cs_knowledge.db"
    )
    
    # Example student profiles
    early_grad_student = {
        "track": "Machine Intelligence",
        "current_semester": 1,
        "early_graduation": True,
        "skip_cs180": False,
        "failed_courses": []
    }
    
    struggling_student = {
        "track": "Software Engineering", 
        "current_semester": 3,
        "early_graduation": False,
        "skip_cs180": False,
        "failed_courses": ["CS 25100"]
    }
    
    # Generate plans
    early_plan = planner.generate_comprehensive_plan(early_grad_student)
    delay_plan = planner.generate_comprehensive_plan(struggling_student)
    
    print("Early Graduation Plan Generated")
    print("Delay Recovery Plan Generated")

if __name__ == "__main__":
    main()