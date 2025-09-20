#!/usr/bin/env python3
"""
Dual Track Graduation Planner
Handles students who want to complete both Machine Intelligence and Software Engineering tracks
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

@dataclass
class CourseSchedule:
    """Represents a semester course schedule"""
    semester: str
    year: int
    courses: List[str]
    total_credits: int
    cs_credits: int

@dataclass
class DualTrackPlan:
    """Complete dual track graduation plan"""
    mi_track_courses: List[str]
    se_track_courses: List[str]
    shared_courses: List[str]
    total_semesters: int
    graduation_date: str
    schedules: List[CourseSchedule]
    warnings: List[str]
    success_probability: float
    total_credits: int
    track_credits: int

class DualTrackGraduationPlanner:
    """Planner for students completing both MI and SE tracks"""
    
    def __init__(self):
        # Track requirements from the existing system
        self.mi_track_requirements = {
            "core_required": ["CS 37300", "CS 38100"],
            "ai_choice": ["CS 47100", "CS 47300"],
            "stats_choice": ["STAT 41600", "MA 41600", "STAT 51200"],
            "electives": 2
        }
        
        self.se_track_requirements = {
            "core_required": ["CS 30700", "CS 38100", "CS 40700", "CS 40800"],
            "compiler_os_choice": ["CS 35200", "CS 35400"],
            "electives": 1
        }
        
        # Foundation courses required for both tracks
        self.foundation_courses = [
            "CS 18000", "CS 18200", "CS 24000", "CS 25000", "CS 25100", "CS 25200"
        ]
        
        # Math and science requirements
        self.math_science = [
            "MA 16100", "MA 16200", "MA 26100", "MA 26500", "STAT 35000", 
            "PHYS 17200", "PHYS 27200"
        ]
        
        # Course credit mapping
        self.course_credits = {
            # Foundation courses
            "CS 18000": 4, "CS 18200": 3, "CS 24000": 3, "CS 25000": 4,
            "CS 25100": 4, "CS 25200": 4,
            
            # Math and science
            "MA 16100": 5, "MA 16200": 5, "MA 26100": 4, "MA 26500": 3,
            "STAT 35000": 3, "PHYS 17200": 4, "PHYS 27200": 4,
            
            # MI track courses
            "CS 37300": 3, "CS 38100": 3, "CS 47100": 3, "CS 47300": 3,
            "STAT 41600": 3, "MA 41600": 3, "STAT 51200": 3,
            
            # SE track courses
            "CS 30700": 3, "CS 40700": 3, "CS 40800": 3, "CS 35200": 3, "CS 35400": 3,
            
            # Other CS courses
            "CS 35100": 3, "CS 35200": 3, "CS 44800": 3, "CS 45600": 3,
            "CS 45800": 3, "CS 48300": 3, "CS 34800": 3, "CS 47500": 3,
            
            # General courses
            "ENGL 10600": 4, "CS 19300": 1
        }
        
        # Prerequisites for track courses
        self.prerequisites = {
            "CS 37300": ["CS 25100", "STAT 35000"],
            "CS 38100": ["CS 25100"],
            "CS 47100": ["CS 37300"],
            "CS 47300": ["CS 25100"],
            "CS 30700": ["CS 25200"],
            "CS 40700": ["CS 30700"],
            "CS 40800": ["CS 30700"],
            "CS 35200": ["CS 25200"],
            "CS 35400": ["CS 25200"],
            "STAT 41600": ["MA 26100", "STAT 35000"],
            "MA 41600": ["MA 26100"],
            "STAT 51200": ["STAT 35000"]
        }
    
    def generate_dual_track_plan(self, student_year: str = "freshman", 
                                early_graduation: bool = False) -> DualTrackPlan:
        """Generate comprehensive dual track graduation plan"""
        
        # Calculate total track requirements
        mi_courses = self._get_mi_track_courses()
        se_courses = self._get_se_track_courses()
        
        # Find shared courses (CS 38100 is required in both)
        shared_courses = list(set(mi_courses) & set(se_courses))
        unique_mi_courses = [c for c in mi_courses if c not in shared_courses]
        unique_se_courses = [c for c in se_courses if c not in shared_courses]
        
        # Calculate total track credits
        track_credits = sum(self.course_credits.get(c, 3) for c in mi_courses + se_courses)
        
        # Generate semester schedules
        if early_graduation:
            schedules = self._generate_early_graduation_schedule(student_year)
            total_semesters = 7  # 3.5 years
            graduation_date = "Spring Year 4"
            success_probability = 0.45  # Lower due to dual track complexity
        else:
            schedules = self._generate_standard_graduation_schedule(student_year)
            total_semesters = 8  # 4 years
            graduation_date = "Spring Year 4"
            success_probability = 0.75
        
        # Calculate total credits
        total_credits = sum(sem.total_credits for sem in schedules)
        
        # Generate warnings
        warnings = self._generate_warnings(early_graduation, track_credits)
        
        return DualTrackPlan(
            mi_track_courses=unique_mi_courses,
            se_track_courses=unique_se_courses,
            shared_courses=shared_courses,
            total_semesters=total_semesters,
            graduation_date=graduation_date,
            schedules=schedules,
            warnings=warnings,
            success_probability=success_probability,
            total_credits=total_credits,
            track_credits=track_credits
        )
    
    def _get_mi_track_courses(self) -> List[str]:
        """Get all courses required for MI track"""
        courses = []
        
        # Core required
        courses.extend(self.mi_track_requirements["core_required"])
        
        # AI choice (assume CS 47100 for this plan)
        courses.append("CS 47100")
        
        # Stats choice (assume STAT 41600 for this plan)
        courses.append("STAT 41600")
        
        # Electives (assume CS 44800 and CS 45600)
        courses.extend(["CS 44800", "CS 45600"])
        
        return courses
    
    def _get_se_track_courses(self) -> List[str]:
        """Get all courses required for SE track"""
        courses = []
        
        # Core required
        courses.extend(self.se_track_requirements["core_required"])
        
        # Compiler/OS choice (assume CS 35200 for this plan)
        courses.append("CS 35200")
        
        # Elective (assume CS 34800)
        courses.append("CS 34800")
        
        return courses
    
    def _generate_standard_graduation_schedule(self, student_year: str) -> List[CourseSchedule]:
        """Generate standard 4-year dual track schedule"""
        schedules = []
        
        # Freshman Year
        fall_1 = CourseSchedule("Fall", 1, [
            "CS 18000", "MA 16100", "ENGL 10600", "CS 19300"
        ], 14, 5)
        
        spring_1 = CourseSchedule("Spring", 1, [
            "CS 18200", "CS 24000", "MA 16200", "General Ed"
        ], 15, 6)
        
        schedules.extend([fall_1, spring_1])
        
        # Sophomore Year
        fall_2 = CourseSchedule("Fall", 2, [
            "CS 25000", "CS 25100", "MA 26100", "General Ed"
        ], 16, 8)
        
        spring_2 = CourseSchedule("Spring", 2, [
            "CS 25200", "MA 26500", "STAT 35000", "General Ed"
        ], 15, 4)
        
        schedules.extend([fall_2, spring_2])
        
        # Junior Year
        fall_3 = CourseSchedule("Fall", 3, [
            "CS 35100", "CS 38100", "PHYS 17200", "General Ed"
        ], 16, 6)
        
        spring_3 = CourseSchedule("Spring", 3, [
            "CS 37300", "CS 30700", "PHYS 27200", "General Ed"
        ], 16, 6)
        
        schedules.extend([fall_3, spring_3])
        
        # Senior Year
        fall_4 = CourseSchedule("Fall", 4, [
            "CS 47100", "CS 40800", "CS 35200", "CS 44800"
        ], 15, 12)
        
        spring_4 = CourseSchedule("Spring", 4, [
            "CS 40700", "STAT 41600", "CS 45600", "CS 34800"
        ], 15, 12)
        
        schedules.extend([fall_4, spring_4])
        
        return schedules
    
    def _generate_early_graduation_schedule(self, student_year: str) -> List[CourseSchedule]:
        """Generate accelerated 3.5-year dual track schedule"""
        schedules = []
        
        # Freshman Year (accelerated)
        fall_1 = CourseSchedule("Fall", 1, [
            "CS 18000", "MA 16100", "ENGL 10600", "CS 19300", "General Ed"
        ], 18, 5)
        
        spring_1 = CourseSchedule("Spring", 1, [
            "CS 18200", "CS 24000", "MA 16200", "General Ed", "General Ed"
        ], 18, 6)
        
        summer_1 = CourseSchedule("Summer", 1, [
            "CS 25000", "CS 25100"
        ], 8, 8)
        
        schedules.extend([fall_1, spring_1, summer_1])
        
        # Sophomore Year (heavy load)
        fall_2 = CourseSchedule("Fall", 2, [
            "CS 25200", "CS 38100", "MA 26100", "STAT 35000", "General Ed"
        ], 18, 8)
        
        spring_2 = CourseSchedule("Spring", 2, [
            "CS 35100", "MA 26500", "PHYS 17200", "General Ed", "General Ed"
        ], 18, 3)
        
        schedules.extend([fall_2, spring_2])
        
        # Junior Year (track courses)
        fall_3 = CourseSchedule("Fall", 3, [
            "CS 37300", "CS 30700", "PHYS 27200", "CS 47100", "General Ed"
        ], 18, 12)
        
        spring_3 = CourseSchedule("Spring", 3, [
            "CS 40800", "CS 35200", "STAT 41600", "CS 44800", "General Ed"
        ], 18, 12)
        
        schedules.extend([fall_3, spring_3])
        
        # Senior Year (final semester)
        fall_4 = CourseSchedule("Fall", 4, [
            "CS 40700", "CS 45600", "CS 34800", "General Ed", "General Ed"
        ], 16, 9)
        
        schedules.append(fall_4)
        
        return schedules
    
    def _generate_warnings(self, early_graduation: bool, track_credits: int) -> List[str]:
        """Generate warnings for dual track completion"""
        warnings = [
            "Dual track completion requires advisor approval",
            "Heavy course loads may impact GPA",
            "Limited flexibility for course failures",
            "Summer courses may be necessary",
            "Consider impact on internship opportunities"
        ]
        
        if early_graduation:
            warnings.extend([
                "3.5-year timeline is extremely challenging with dual tracks",
                "Success probability is significantly lower",
                "Consider standard 4-year timeline for better success",
                "May need to reduce course loads if struggling"
            ])
        
        if track_credits > 30:
            warnings.append(f"Total track credits ({track_credits}) exceed typical limits")
        
        return warnings
    
    def format_plan_for_display(self, plan: DualTrackPlan) -> str:
        """Format the dual track plan for CLI display"""
        output = []
        
        output.append("🎓 DUAL TRACK GRADUATION PLAN")
        output.append("=" * 50)
        output.append(f"📚 Machine Intelligence + Software Engineering Tracks")
        output.append(f"⏰ Timeline: {plan.total_semesters} semesters ({plan.graduation_date})")
        output.append(f"📊 Success Probability: {plan.success_probability * 100:.0f}%")
        output.append(f"💳 Total Credits: {plan.total_credits}")
        output.append(f"🎯 Track Credits: {plan.track_credits}")
        output.append("")
        
        # Show shared courses
        output.append("🔄 SHARED COURSES (Count for both tracks):")
        for course in plan.shared_courses:
            output.append(f"  • {course} ({self.course_credits.get(course, 3)} credits)")
        output.append("")
        
        # Show MI track courses
        output.append("🤖 MACHINE INTELLIGENCE TRACK COURSES:")
        for course in plan.mi_track_courses:
            output.append(f"  • {course} ({self.course_credits.get(course, 3)} credits)")
        output.append("")
        
        # Show SE track courses
        output.append("💻 SOFTWARE ENGINEERING TRACK COURSES:")
        for course in plan.se_track_courses:
            output.append(f"  • {course} ({self.course_credits.get(course, 3)} credits)")
        output.append("")
        
        # Show semester breakdown
        output.append("📅 SEMESTER BREAKDOWN:")
        for i, schedule in enumerate(plan.schedules, 1):
            output.append(f"")
            output.append(f"Semester {i} ({schedule.semester} Year {schedule.year}):")
            output.append(f"  Total Credits: {schedule.total_credits}")
            output.append(f"  CS Credits: {schedule.cs_credits}")
            for course in schedule.courses:
                if course in plan.mi_track_courses or course in plan.se_track_courses:
                    output.append(f"  🎯 {course} (Track Course)")
                elif course in plan.shared_courses:
                    output.append(f"  🔄 {course} (Shared)")
                else:
                    output.append(f"  📚 {course}")
        
        # Show warnings
        if plan.warnings:
            output.append("")
            output.append("⚠️ IMPORTANT WARNINGS:")
            for warning in plan.warnings:
                output.append(f"  • {warning}")
        
        # Show recommendations
        output.append("")
        output.append("💡 RECOMMENDATIONS:")
        output.append("  • Meet with your academic advisor to discuss dual track feasibility")
        output.append("  • Consider starting with one track and adding the second later")
        output.append("  • Plan for summer courses to reduce semester loads")
        output.append("  • Focus on maintaining strong GPA in foundation courses")
        output.append("  • Consider research or internship opportunities in both areas")
        
        return "\n".join(output)

if __name__ == "__main__":
    # Test the dual track planner
    planner = DualTrackGraduationPlanner()
    
    # Generate standard plan
    standard_plan = planner.generate_dual_track_plan("freshman", early_graduation=False)
    print(planner.format_plan_for_display(standard_plan))
    
    print("\n" + "="*80 + "\n")
    
    # Generate early graduation plan
    early_plan = planner.generate_dual_track_plan("freshman", early_graduation=True)
    print(planner.format_plan_for_display(early_plan)) 