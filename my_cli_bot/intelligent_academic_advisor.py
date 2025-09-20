#!/usr/bin/env python3
"""
Intelligent Academic Advisor with Prerequisite Chain Prediction and Graduation Analysis
Handles complex academic planning, CODO eligibility, and graduation delay prediction
"""

import json
import os
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import networkx as nx
import google.generativeai as genai
from dataclasses import dataclass
import re
from graduation_planner import AdvancedGraduationPlanner

@dataclass
class StudentProfile:
    """Student profile for personalized planning"""
    student_id: str
    current_year: str  # freshman, sophomore, junior, senior
    current_gpa: float
    completed_courses: List[str]
    current_courses: List[str]
    failed_courses: List[str]
    career_goal: str  # AI, Systems, Cybersecurity, etc.
    preferred_track: str
    max_credits_per_semester: int = 18
    graduation_target: str = "4_years"

@dataclass
class CourseInfo:
    """Detailed course information"""
    code: str
    title: str
    credits: int
    prerequisites: List[str]
    corequisites: List[str]
    description: str
    difficulty_rating: float
    typical_semester: str  # fall, spring, both
    track_relevance: Dict[str, float]

class IntelligentAcademicAdvisor:
    def __init__(self, comprehensive_data_path: str = "data/comprehensive_purdue_cs_data.json"):
        self.comprehensive_data = {}
        self.prerequisite_graph = nx.DiGraph()
        self.course_catalog = {}
        self.graduation_requirements = {}
        self.codo_requirements = {}
        
        # Initialize graduation planner
        self.graduation_planner = AdvancedGraduationPlanner(
            knowledge_file="data/cs_knowledge_graph.json",
            db_file="purdue_cs_knowledge.db"
        )
        
        # Load comprehensive data
        self.load_comprehensive_data(comprehensive_data_path)
        self.build_prerequisite_graph()
        self.initialize_Gemini()
        
    def load_comprehensive_data(self, filepath: str):
        """Load comprehensive Purdue CS data"""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                self.comprehensive_data = json.load(f)
            print(f"✓ Loaded comprehensive data from {filepath}")
        else:
            print(f"⚠ Comprehensive data file not found: {filepath}")
            # Load fallback data from existing files
            self.load_fallback_data()
    
    def load_fallback_data(self):
        """Load data from existing files if comprehensive data unavailable"""
        # Load from existing knowledge graph
        kg_path = "data/cs_knowledge_graph.json"
        if os.path.exists(kg_path):
            with open(kg_path, 'r') as f:
                kg_data = json.load(f)
                # Convert knowledge graph data to comprehensive format
                self.comprehensive_data = {
                    "courses": kg_data.get("courses", {}),
                    "prerequisites": kg_data.get("prerequisites", {}),
                    "tracks": kg_data.get("tracks", {}),
                    "graduation_requirements": {},
                    "codo_requirements": {},
                    "gpa_requirements": {}
                }
    
    def initialize_Gemini(self):
        """Initialize Gemini client"""
        Gemini.api_key = os.environ.get("GEMINI_API_KEY")
        if not Gemini.api_key:
            print("⚠ Gemini API key not found")
    
    def build_prerequisite_graph(self):
        """Build NetworkX graph of prerequisite relationships"""
        self.prerequisite_graph = nx.DiGraph()
        
        # Add courses as nodes
        for course_code, course_info in self.comprehensive_data.get("courses", {}).items():
            self.prerequisite_graph.add_node(course_code, **course_info)
        
        # Add prerequisite edges
        for course_code, prereq_info in self.comprehensive_data.get("prerequisites", {}).items():
            if isinstance(prereq_info, dict) and "required" in prereq_info:
                prerequisites = prereq_info["required"]
            elif isinstance(prereq_info, list):
                prerequisites = prereq_info
            else:
                continue
                
            for prereq in prerequisites:
                self.prerequisite_graph.add_edge(prereq, course_code, relationship="prerequisite")
        
        print(f"✓ Built prerequisite graph with {self.prerequisite_graph.number_of_nodes()} courses and {self.prerequisite_graph.number_of_edges()} relationships")
    
    def get_complete_prerequisite_chain(self, course_code: str) -> List[str]:
        """Get complete prerequisite chain for a course using topological sort"""
        if course_code not in self.prerequisite_graph:
            return []
        
        # Get all predecessors (prerequisites)
        predecessors = list(nx.ancestors(self.prerequisite_graph, course_code))
        
        if not predecessors:
            return []
        
        # Create subgraph with prerequisites
        subgraph = self.prerequisite_graph.subgraph(predecessors + [course_code])
        
        # Get topological order
        try:
            topo_order = list(nx.topological_sort(subgraph))
            # Remove the target course from the chain
            return [course for course in topo_order if course != course_code]
        except nx.NetworkXError:
            # Handle cycles by using simple predecessor list
            return predecessors
    
    def predict_graduation_timeline(self, student: StudentProfile) -> Dict[str, Any]:
        """Predict graduation timeline and identify potential delays"""
        
        # Get all required courses
        required_courses = self.get_required_courses_for_graduation(student.preferred_track)
        
        # Remove already completed courses
        remaining_courses = [course for course in required_courses if course not in student.completed_courses]
        
        # Calculate prerequisite dependencies
        course_dependencies = {}
        for course in remaining_courses:
            prereq_chain = self.get_complete_prerequisite_chain(course)
            course_dependencies[course] = [p for p in prereq_chain if p in remaining_courses]
        
        # Simulate semester-by-semester progression
        semesters_plan = self.plan_semester_schedule(
            remaining_courses, 
            course_dependencies, 
            student.max_credits_per_semester,
            student.failed_courses
        )
        
        # Calculate graduation date
        current_semester = self.get_current_semester()
        graduation_semester = len(semesters_plan)
        
        # Detect delays
        expected_semesters = self.get_expected_semesters_remaining(student.current_year)
        delay_semesters = max(0, graduation_semester - expected_semesters)
        
        return {
            "graduation_plan": semesters_plan,
            "total_semesters": graduation_semester,
            "expected_semesters": expected_semesters,
            "delay_semesters": delay_semesters,
            "graduation_date": self.calculate_graduation_date(graduation_semester),
            "on_track": delay_semesters == 0,
            "risk_factors": self.identify_risk_factors(student, semesters_plan)
        }
    
    def plan_semester_schedule(self, courses: List[str], dependencies: Dict[str, List[str]], 
                             max_credits: int, failed_courses: List[str]) -> List[Dict[str, Any]]:
        """Plan optimal semester schedule considering prerequisites and credit limits"""
        
        remaining_courses = courses.copy()
        semester_plan = []
        semester_num = 1
        
        while remaining_courses:
            semester_courses = []
            semester_credits = 0
            
            # Find courses with satisfied prerequisites
            available_courses = []
            for course in remaining_courses:
                prereqs = dependencies.get(course, [])
                if all(prereq not in remaining_courses for prereq in prereqs):
                    available_courses.append(course)
            
            if not available_courses:
                # No available courses - possible circular dependency
                break
            
            # Prioritize courses based on:
            # 1. Failed courses (need to retake)
            # 2. Core requirements
            # 3. Track requirements
            # 4. Credit load optimization
            
            prioritized_courses = self.prioritize_courses(available_courses, failed_courses, semester_num)
            
            for course in prioritized_courses:
                course_credits = self.get_course_credits(course)
                if semester_credits + course_credits <= max_credits:
                    semester_courses.append(course)
                    semester_credits += course_credits
                    remaining_courses.remove(course)
            
            if semester_courses:
                semester_plan.append({
                    "semester": semester_num,
                    "courses": semester_courses,
                    "total_credits": semester_credits,
                    "semester_type": "fall" if semester_num % 2 == 1 else "spring"
                })
                semester_num += 1
            else:
                # No courses could be scheduled - break to avoid infinite loop
                break
        
        return semester_plan
    
    def prioritize_courses(self, available_courses: List[str], failed_courses: List[str], semester_num: int) -> List[str]:
        """Prioritize courses for optimal scheduling"""
        priority_scores = {}
        
        for course in available_courses:
            score = 0
            
            # High priority for failed courses (must retake)
            if course in failed_courses:
                score += 1000
            
            # Priority for core courses
            if self.is_core_course(course):
                score += 100
            
            # Priority for courses that unlock many others
            unlocked_count = len(list(nx.descendants(self.prerequisite_graph, course)))
            score += unlocked_count * 10
            
            # Earlier semesters prioritize foundational courses
            if semester_num <= 4 and self.is_foundational_course(course):
                score += 50
            
            priority_scores[course] = score
        
        return sorted(available_courses, key=lambda x: priority_scores.get(x, 0), reverse=True)
    
    def check_codo_eligibility(self, student: StudentProfile) -> Dict[str, Any]:
        """Check CODO (Change of Degree Objective) eligibility"""
        
        codo_requirements = self.comprehensive_data.get("codo_requirements", {})
        
        # Standard CODO requirements for CS
        min_gpa = 3.2  # Typical requirement
        required_courses = ["MATH 16100", "MATH 16200", "CS 18000"]  # Common prerequisites
        max_attempts = {"CS 18000": 2}  # Maximum attempts for key courses
        
        eligibility_check = {
            "eligible": True,
            "requirements_met": {},
            "missing_requirements": [],
            "recommendations": []
        }
        
        # Check GPA requirement
        gpa_met = student.current_gpa >= min_gpa
        eligibility_check["requirements_met"]["minimum_gpa"] = gpa_met
        if not gpa_met:
            eligibility_check["eligible"] = False
            eligibility_check["missing_requirements"].append(f"GPA must be at least {min_gpa} (current: {student.current_gpa})")
        
        # Check required courses
        for course in required_courses:
            completed = course in student.completed_courses
            eligibility_check["requirements_met"][course] = completed
            if not completed:
                eligibility_check["eligible"] = False
                eligibility_check["missing_requirements"].append(f"Must complete {course}")
        
        # Check course attempt limits
        for course, max_att in max_attempts.items():
            attempts = student.failed_courses.count(course) + (1 if course in student.completed_courses else 0)
            if attempts >= max_att and course not in student.completed_courses:
                eligibility_check["eligible"] = False
                eligibility_check["missing_requirements"].append(f"Exceeded maximum attempts for {course}")
        
        # Generate recommendations
        if not eligibility_check["eligible"]:
            if not gpa_met:
                eligibility_check["recommendations"].append("Focus on improving GPA through retaking courses or taking easier electives")
            
            missing_courses = [req for req in eligibility_check["missing_requirements"] if "Must complete" in req]
            if missing_courses:
                eligibility_check["recommendations"].append("Complete missing prerequisite courses")
        
        return eligibility_check
    
    def analyze_course_failure_impact(self, failed_course: str, student: StudentProfile) -> Dict[str, Any]:
        """Analyze impact of failing a course on graduation timeline"""
        
        # Get courses that depend on this failed course
        dependent_courses = list(nx.descendants(self.prerequisite_graph, failed_course))
        
        # Calculate delay impact
        if failed_course in ["CS 18000", "MATH 16100", "MATH 16200"]:  # Critical foundation courses
            delay_impact = "HIGH"
            additional_semesters = 1-2
        elif len(dependent_courses) > 5:
            delay_impact = "MEDIUM"
            additional_semesters = 1
        else:
            delay_impact = "LOW"
            additional_semesters = 0.5
        
        # Get retake strategy
        retake_strategy = self.generate_retake_strategy(failed_course, student)
        
        return {
            "failed_course": failed_course,
            "delay_impact": delay_impact,
            "dependent_courses": dependent_courses,
            "additional_semesters": additional_semesters,
            "retake_strategy": retake_strategy,
            "alternative_paths": self.find_alternative_paths(failed_course, student.preferred_track)
        }
    
    def generate_retake_strategy(self, failed_course: str, student: StudentProfile) -> Dict[str, Any]:
        """Generate optimal retake strategy"""
        
        strategy = {
            "immediate_retake": True,
            "preparation_recommendations": [],
            "support_resources": [],
            "timing": "next_semester"
        }
        
        # Course-specific strategies
        if failed_course == "CS 18000":
            strategy["preparation_recommendations"] = [
                "Complete programming fundamentals review",
                "Practice basic Java programming",
                "Form study groups",
                "Attend SI sessions"
            ]
            strategy["support_resources"] = [
                "CS Help Room",
                "Tutoring Center",
                "Professor office hours",
                "Online programming resources"
            ]
        
        elif "MATH" in failed_course:
            strategy["preparation_recommendations"] = [
                "Review prerequisite math concepts",
                "Practice problem-solving techniques",
                "Use online math resources"
            ]
            strategy["support_resources"] = [
                "Math Help Room",
                "Tutoring services",
                "Study groups"
            ]
        
        return strategy
    
    def get_intelligent_course_recommendations(self, student: StudentProfile, semester_type: str) -> List[Dict[str, Any]]:
        """Get intelligent course recommendations based on student profile and goals"""
        
        # Use Gemini for intelligent recommendations
        prompt = f"""
        As an expert Purdue CS academic advisor, recommend courses for a {student.current_year} student with:
        - Current GPA: {student.current_gpa}
        - Career Goal: {student.career_goal}
        - Preferred Track: {student.preferred_track}
        - Completed Courses: {', '.join(student.completed_courses)}
        - Failed Courses: {', '.join(student.failed_courses)}
        
        Recommend 4-5 courses for {semester_type} semester considering:
        1. Prerequisites satisfaction
        2. Career goal alignment
        3. Workload balance
        4. GPA improvement potential
        
        Format as JSON with course codes, reasoning, and priority level.
        """
        
        try:
            response = Gemini.ChatCompletion.create(
                ,
                prompt,
                
            )
            
            recommendations = json.loads(response.text)
            return recommendations
            
        except Exception as e:
            print(f"Error getting AI recommendations: {e}")
            return self.get_fallback_recommendations(student, semester_type)
    
    def get_fallback_recommendations(self, student: StudentProfile, semester_type: str) -> List[Dict[str, Any]]:
        """Fallback course recommendations if AI unavailable"""
        
        # Get available courses based on completed prerequisites
        available_courses = []
        for course_code in self.comprehensive_data.get("courses", {}):
            if course_code not in student.completed_courses:
                prereqs = self.get_complete_prerequisite_chain(course_code)
                if all(prereq in student.completed_courses for prereq in prereqs):
                    available_courses.append(course_code)
        
        # Filter by track relevance and semester availability
        recommendations = []
        for course in available_courses[:5]:  # Limit to top 5
            recommendations.append({
                "course_code": course,
                "reasoning": f"Available based on completed prerequisites",
                "priority": "medium"
            })
        
        return recommendations
    
    def predict_gpa_impact(self, planned_courses: List[str], current_gpa: float) -> float:
        """Predict GPA impact of planned courses"""
        
        # Use historical difficulty data and student performance to predict grades
        # This is a simplified model - could be enhanced with ML
        
        total_grade_points = 0
        total_credits = 0
        
        for course in planned_courses:
            credits = self.get_course_credits(course)
            difficulty = self.get_course_difficulty(course)
            
            # Predict grade based on current GPA and course difficulty
            predicted_grade = max(0.0, min(4.0, current_gpa - (difficulty - 2.5) * 0.5))
            
            total_grade_points += predicted_grade * credits
            total_credits += credits
        
        if total_credits > 0:
            semester_gpa = total_grade_points / total_credits
            return semester_gpa
        
        return current_gpa
    
    # Helper methods
    def get_required_courses_for_graduation(self, track: str) -> List[str]:
        """Get all required courses for graduation in a specific track"""
        required = []
        
        # Core CS requirements
        core_courses = self.comprehensive_data.get("degree_requirements", {}).get("core_courses", [])
        required.extend(core_courses)
        
        # Track-specific requirements
        track_info = self.comprehensive_data.get("tracks", {}).get(track, {})
        track_courses = track_info.get("required_courses", [])
        required.extend(track_courses)
        
        # Add common requirements if not in comprehensive data
        if not required:
            # Fallback to known core courses
            required = [
                "CS 18000", "CS 18200", "CS 25000", "CS 25100", "CS 35100",
                "CS 38100", "CS 24000", "CS 25200", "CS 35200", "CS 37300",
                "MATH 16100", "MATH 16200", "MATH 26100", "STAT 35000"
            ]
        
        return required
    
    def get_course_credits(self, course_code: str) -> int:
        """Get credit hours for a course"""
        course_info = self.comprehensive_data.get("courses", {}).get(course_code, {})
        return course_info.get("credits", 3)  # Default to 3 credits
    
    def get_course_difficulty(self, course_code: str) -> float:
        """Get difficulty rating for a course (1-5 scale)"""
        # This could be enhanced with real data
        difficulty_map = {
            "CS 18000": 3.5,
            "CS 18200": 4.0,
            "CS 25000": 4.5,
            "CS 25100": 3.5,
            "MATH 16100": 3.0,
            "MATH 16200": 3.5
        }
        return difficulty_map.get(course_code, 3.0)  # Default to medium difficulty
    
    def is_core_course(self, course_code: str) -> bool:
        """Check if course is a core requirement"""
        core_courses = self.comprehensive_data.get("degree_requirements", {}).get("core_courses", [])
        return course_code in core_courses
    
    def is_foundational_course(self, course_code: str) -> bool:
        """Check if course is foundational (should be taken early)"""
        foundational = ["CS 18000", "CS 18200", "MATH 16100", "MATH 16200", "CS 24000"]
        return course_code in foundational
    
    def get_current_semester(self) -> str:
        """Get current semester type"""
        month = datetime.now().month
        if month in [8, 9, 10, 11, 12]:
            return "fall"
        elif month in [1, 2, 3, 4, 5]:
            return "spring"
        else:
            return "summer"
    
    def get_expected_semesters_remaining(self, current_year: str) -> int:
        """Get expected semesters remaining for graduation"""
        year_map = {
            "freshman": 8,
            "sophomore": 6,
            "junior": 4,
            "senior": 2
        }
        return year_map.get(current_year.lower(), 4)
    
    def calculate_graduation_date(self, semesters_remaining: int) -> str:
        """Calculate expected graduation date"""
        current_date = datetime.now()
        months_to_add = semesters_remaining * 4  # Approximate 4 months per semester
        graduation_date = current_date + timedelta(days=months_to_add * 30)
        return graduation_date.strftime("%B %Y")
    
    def generate_graduation_plan(self, student_profile: Dict) -> Dict:
        """
        Generate comprehensive graduation plan using advanced planner
        Handles early graduation, delays, and track specialization
        """
        return self.graduation_planner.generate_comprehensive_plan(student_profile)
    
    def analyze_early_graduation_feasibility(self, student: StudentProfile) -> Dict:
        """
        Analyze if early graduation is feasible for student
        """
        profile = {
            "track": student.preferred_track,
            "current_semester": self._get_current_semester_number(student),
            "early_graduation": True,
            "skip_cs180": "CS 18000" not in student.completed_courses,
            "failed_courses": student.failed_courses,
            "current_gpa": student.current_gpa
        }
        
        plan = self.graduation_planner.generate_early_graduation_plan(
            student.preferred_track, 
            profile["skip_cs180"]
        )
        
        # Add feasibility analysis
        feasibility = {
            "recommended": plan.success_probability > 0.6,
            "success_probability": plan.success_probability,
            "major_risks": plan.warnings,
            "course_load_analysis": self._analyze_course_loads(plan.schedules),
            "alternative_timeline": "Consider 3.5 year plan if 3 year seems too aggressive"
        }
        
        return {
            "graduation_plan": plan,
            "feasibility_analysis": feasibility,
            "recommendations": self._generate_early_grad_recommendations(student, plan)
        }
    
    def analyze_graduation_delay_recovery(self, student: StudentProfile) -> Dict:
        """
        Analyze recovery strategies for graduation delays
        """
        recovery_plans = {}
        
        for failed_course in student.failed_courses:
            scenario = self.graduation_planner.analyze_foundation_delay_scenario(
                failed_course, 
                self._get_current_semester_number(student)
            )
            recovery_plans[failed_course] = scenario
        
        # Generate comprehensive recovery strategy
        overall_strategy = {
            "total_delay_estimate": max([s.get("delay_semesters", 0) for s in recovery_plans.values()]),
            "summer_recovery_options": [s.get("summer_recovery") for s in recovery_plans.values() if s.get("summer_recovery")],
            "critical_courses_to_prioritize": [course for course, scenario in recovery_plans.items() if scenario.get("difficulty") == "High"],
            "graduation_timeline_adjustment": self._calculate_adjusted_timeline(recovery_plans)
        }
        
        return {
            "individual_recovery_plans": recovery_plans,
            "overall_strategy": overall_strategy,
            "recommendations": self._generate_recovery_recommendations(student, recovery_plans)
        }
    
    def get_track_specific_guidance(self, track: str, student_level: str) -> Dict:
        """
        Get detailed guidance for Machine Intelligence or Software Engineering tracks
        """
        if track == "Machine Intelligence":
            return {
                "core_focus": "Data science, machine learning, artificial intelligence",
                "key_courses": ["CS 37300", "CS 47100", "CS 47300", "STAT 41600"],
                "programming_languages": ["Python", "R", "MATLAB"],
                "career_preparation": {
                    "internships": "Look for ML/AI research positions or data science roles",
                    "projects": "Kaggle competitions, research projects, ML applications",
                    "graduate_school": "Strong foundation for ML/AI graduate programs"
                },
                "course_sequence_tips": {
                    "early": "Focus on strong math foundation (statistics, linear algebra)",
                    "mid": "Take CS 37300 as soon as prerequisites met",
                    "late": "Choose between CS 47100 (theory) vs CS 47300 (applied) based on career goals"
                }
            }
        elif track == "Software Engineering":
            return {
                "core_focus": "Large-scale software development, project management, testing",
                "key_courses": ["CS 30700", "CS 40700", "CS 40800", "CS 35200/35400"],
                "programming_languages": ["Java", "C++", "Python", "JavaScript"],
                "career_preparation": {
                    "internships": "Software engineering roles at companies of various sizes",
                    "projects": "Contribute to open source, build portfolio applications",
                    "certifications": "Consider Agile/Scrum certifications"
                },
                "course_sequence_tips": {
                    "early": "Strong foundation in CS 25200 (Systems Programming)",
                    "mid": "CS 30700 is prerequisite for senior project - take junior year",
                    "late": "Senior project (CS 40700) should align with career goals"
                }
            }
        else:
            return {"error": "Track not recognized"}
    
    def _get_current_semester_number(self, student: StudentProfile) -> int:
        """Convert student year to semester number"""
        year_map = {
            "freshman": 2,
            "sophomore": 4, 
            "junior": 6,
            "senior": 8
        }
        return year_map.get(student.current_year.lower(), 2)
    
    def _analyze_course_loads(self, schedules: List) -> Dict:
        """Analyze course load feasibility"""
        analysis = {
            "heavy_semesters": [],
            "cs_intensive_semesters": [],
            "manageable_semesters": [],
            "recommendations": []
        }
        
        for schedule in schedules:
            if schedule.total_credits > 18:
                analysis["heavy_semesters"].append(f"{schedule.semester} {schedule.year}: {schedule.total_credits} credits")
            if schedule.cs_credits > 9:
                analysis["cs_intensive_semesters"].append(f"{schedule.semester} {schedule.year}: {schedule.cs_credits} CS credits")
            if schedule.total_credits <= 16 and schedule.cs_credits <= 6:
                analysis["manageable_semesters"].append(f"{schedule.semester} {schedule.year}")
        
        if analysis["heavy_semesters"]:
            analysis["recommendations"].append("Consider reducing course load in heavy semesters")
        if analysis["cs_intensive_semesters"]:
            analysis["recommendations"].append("Balance CS-heavy semesters with lighter non-CS courses")
            
        return analysis
    
    def _generate_early_grad_recommendations(self, student: StudentProfile, plan) -> List[str]:
        """Generate specific recommendations for early graduation"""
        recommendations = []
        
        if student.current_gpa < 3.5:
            recommendations.append("Focus on improving GPA before attempting accelerated timeline")
        
        if plan.success_probability < 0.5:
            recommendations.append("Consider 3.5-year timeline instead of 3-year")
        
        recommendations.extend([
            "Meet with academic advisor every semester for plan adjustment",
            "Consider summer courses to reduce regular semester loads",
            "Maintain strong performance in foundation courses",
            "Build relationships with faculty for research opportunities"
        ])
        
        return recommendations
    
    def _generate_recovery_recommendations(self, student: StudentProfile, recovery_plans: Dict) -> List[str]:
        """Generate specific recommendations for graduation delay recovery"""
        recommendations = []
        
        critical_failures = [course for course, plan in recovery_plans.items() if plan.get("difficulty") == "High"]
        
        if critical_failures:
            recommendations.append(f"Prioritize retaking critical courses: {', '.join(critical_failures)}")
        
        if any(plan.get("summer_option") for plan in recovery_plans.values()):
            recommendations.append("Strongly consider summer courses to minimize delay")
        
        recommendations.extend([
            "Meet with academic advisor to adjust graduation timeline",
            "Focus on understanding why courses were failed to prevent repeat failures",
            "Consider tutoring or study groups for challenging subjects",
            "Maintain realistic expectations about graduation timeline"
        ])
        
        return recommendations
    
    def _calculate_adjusted_timeline(self, recovery_plans: Dict) -> str:
        """Calculate new graduation timeline based on recovery plans"""
        max_delay = max([plan.get("delay_semesters", 0) for plan in recovery_plans.values()])
        
        if max_delay == 0:
            return "No significant delay expected"
        elif max_delay == 1:
            return "1 semester delay likely - consider December graduation"
        elif max_delay == 2:
            return "1 year delay likely - adjust expectations accordingly"
        else:
            return f"{max_delay} semester delay - significant timeline adjustment needed"
    
    def identify_risk_factors(self, student: StudentProfile, semester_plan: List[Dict]) -> List[str]:
        """Identify potential risk factors for graduation"""
        risks = []
        
        if student.current_gpa < 2.0:
            risks.append("Low GPA - at risk of academic probation")
        
        if len(student.failed_courses) > 2:
            risks.append("Multiple course failures - consider academic support")
        
        if any(sem["total_credits"] > 18 for sem in semester_plan):
            risks.append("Heavy course load planned - may impact performance")
        
        critical_courses = ["CS 18000", "CS 25000", "MATH 16100"]
        if any(course in student.failed_courses for course in critical_courses):
            risks.append("Failed critical foundation course - significant impact on progression")
        
        return risks
    
    def find_alternative_paths(self, failed_course: str, track: str) -> List[str]:
        """Find alternative academic paths if a course cannot be completed"""
        alternatives = []
        
        if failed_course == "CS 18000":
            alternatives = [
                "Consider Data Science major",
                "Explore Information Technology track",
                "Look into Computer Graphics Technology"
            ]
        elif failed_course in ["MATH 16100", "MATH 16200"]:
            alternatives = [
                "Consider Applied Statistics major",
                "Explore Information Systems track",
                "Look into Computational Biology"
            ]
        
        return alternatives

def main():
    """Test the intelligent academic advisor"""
    advisor = IntelligentAcademicAdvisor()
    
    # Test student profile
    student = StudentProfile(
        student_id="test123",
        current_year="sophomore",
        current_gpa=2.8,
        completed_courses=["CS 18000", "MATH 16100", "ENGL 10600"],
        current_courses=["CS 18200", "MATH 16200"],
        failed_courses=["CS 18000"],  # Failed once, retaking
        career_goal="Artificial Intelligence",
        preferred_track="Machine Intelligence",
        max_credits_per_semester=15
    )
    
    print("🎓 Intelligent Academic Advisor Test")
    print("=" * 50)
    
    # Test CODO eligibility
    codo_result = advisor.check_codo_eligibility(student)
    print(f"\n📋 CODO Eligibility: {'✅ Eligible' if codo_result['eligible'] else '❌ Not Eligible'}")
    
    # Test graduation timeline
    timeline = advisor.predict_graduation_timeline(student)
    print(f"\n📅 Graduation Timeline:")
    print(f"   • Expected graduation: {timeline['graduation_date']}")
    print(f"   • Delay: {timeline['delay_semesters']} semesters")
    print(f"   • On track: {'Yes' if timeline['on_track'] else 'No'}")
    
    # Test course failure analysis
    if student.failed_courses:
        failure_analysis = advisor.analyze_course_failure_impact(student.failed_courses[0], student)
        print(f"\n⚠️ Course Failure Impact:")
        print(f"   • Impact level: {failure_analysis['delay_impact']}")
        print(f"   • Additional semesters: {failure_analysis['additional_semesters']}")
    
    print("\n✅ Testing completed!")

if __name__ == "__main__":
    main()