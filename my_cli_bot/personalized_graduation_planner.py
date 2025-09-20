#!/usr/bin/env python3
"""
Personalized Graduation Planner for Purdue CS and Data Science Students
Creates truly customized degree progressions based on individual student progress
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from copy import deepcopy

@dataclass
class PersonalizedCourseSchedule:
    semester: str
    year: int
    courses: List[Dict[str, any]]  # Now includes course details
    total_credits: int
    cs_credits: int
    warnings: List[str] = None
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.recommendations is None:
            self.recommendations = []

@dataclass
class PersonalizedGraduationPlan:
    major: str  # "Computer Science" or "Data Science"
    track: str  # For CS: "Machine Intelligence", "Software Engineering", etc.
    total_semesters: int
    graduation_date: str
    schedules: List[PersonalizedCourseSchedule]
    completed_courses: List[str]
    remaining_requirements: Dict[str, List[str]]
    warnings: List[str]
    recommendations: List[str]
    success_probability: float
    customization_notes: List[str]
    choice_request: Dict = None  # For interactive course selection

class PersonalizedGraduationPlanner:
    def __init__(self, knowledge_file: str, db_file: str):
        with open(knowledge_file, 'r') as f:
            self.knowledge = json.load(f)
        self.db_file = db_file
        
        # Course prerequisites and dependencies
        self.prerequisites = self._build_prerequisite_graph()
        
        # Standard semester templates for all majors
        self.cs_semester_templates = self._load_cs_templates()
        self.ds_semester_templates = self._load_ds_templates()
        self.ai_semester_templates = self._load_ai_templates()
        
        # Course offering patterns (which courses offered when)
        self.course_offerings = self._initialize_course_offerings()

    def create_personalized_plan(self, student_profile: Dict, selected_choices: Dict = None) -> PersonalizedGraduationPlan:
        """
        Create a fully personalized graduation plan based on student's specific situation
        """
        major = student_profile.get("major", "Computer Science")
        track = student_profile.get("track", "Machine Intelligence")
        completed_courses = student_profile.get("completed_courses", [])
        current_semester = student_profile.get("current_semester", "Fall")
        current_year = student_profile.get("current_year", 1)
        summer_availability = student_profile.get("summer_courses", True)
        credit_load_preference = student_profile.get("credit_load", "standard")  # light, standard, heavy
        graduation_goal = student_profile.get("graduation_goal", "4_year")  # 3_year, 3.5_year, 4_year, flexible
        
        # Include user's course selections if provided
        if selected_choices:
            student_profile.update(selected_choices)
        
        # Validate and normalize completed courses
        completed_courses = self._validate_completed_courses(completed_courses)
        
        # Check if we need user choices for electives/options
        course_choices_needed = self._identify_course_choices_needed(major, track, completed_courses)
        
        if course_choices_needed and not selected_choices:
            # Return a special plan indicating choices are needed
            return self._create_choice_request_plan(course_choices_needed, student_profile)
        
        # Determine remaining requirements
        remaining_requirements = self._calculate_remaining_requirements(
            major, track, completed_courses, selected_choices
        )
        
        # Create semester-by-semester plan
        schedules = self._generate_personalized_schedules(
            major=major,
            track=track,
            completed_courses=completed_courses,
            remaining_requirements=remaining_requirements,
            current_semester=current_semester,
            current_year=current_year,
            summer_availability=summer_availability,
            credit_load_preference=credit_load_preference,
            graduation_goal=graduation_goal,
            selected_choices=selected_choices or {}
        )
        
        # Calculate success probability and warnings
        success_probability, warnings, recommendations = self._analyze_plan_feasibility(
            schedules, graduation_goal, credit_load_preference
        )
        
        # Generate customization notes
        customization_notes = self._generate_customization_notes(
            student_profile, completed_courses, schedules
        )
        
        return PersonalizedGraduationPlan(
            major=major,
            track=track,
            total_semesters=len(schedules),
            graduation_date=self._calculate_graduation_date(schedules),
            schedules=schedules,
            completed_courses=completed_courses,
            remaining_requirements=remaining_requirements,
            warnings=warnings,
            recommendations=recommendations,
            success_probability=success_probability,
            customization_notes=customization_notes
        )

    def _generate_personalized_schedules(self, major: str, track: str, completed_courses: List[str],
                                       remaining_requirements: Dict, current_semester: str,
                                       current_year: int, summer_availability: bool,
                                       credit_load_preference: str, graduation_goal: str, 
                                       selected_choices: Dict = None) -> List[PersonalizedCourseSchedule]:
        """
        Generate semester-by-semester schedules based on student's specific situation
        """
        schedules = []
        
        # Start from current position
        semester_sequence = self._get_semester_sequence(current_semester, current_year, graduation_goal)
        
        # Track what courses are still needed
        needed_courses = self._flatten_requirements(remaining_requirements)
        planned_courses = set()
        
        # Credit load limits based on preference
        credit_limits = self._get_credit_limits(credit_load_preference)
        
        for semester_info in semester_sequence:
            semester, year = semester_info["semester"], semester_info["year"]
            
            # Determine available courses for this semester
            available_courses = self._get_available_courses(
                needed_courses, planned_courses, semester, major, track
            )
            
            # Select courses for this semester
            selected_courses, semester_credits, cs_credits = self._select_courses_for_semester(
                available_courses, semester, year, credit_limits[semester.lower()], 
                remaining_requirements, major, track
            )
            
            # Add to planned courses
            planned_courses.update([course["code"] for course in selected_courses])
            
            # Generate warnings and recommendations for this semester
            warnings, recommendations = self._generate_semester_feedback(
                selected_courses, semester, year, major, track
            )
            
            schedule = PersonalizedCourseSchedule(
                semester=semester,
                year=year,
                courses=selected_courses,
                total_credits=semester_credits,
                cs_credits=cs_credits,
                warnings=warnings,
                recommendations=recommendations
            )
            
            schedules.append(schedule)
            
            # Update needed courses
            needed_courses = [course for course in needed_courses 
                            if course not in planned_courses]
            
            # Break if all requirements met
            if not needed_courses:
                break
        
        return schedules

    def _identify_course_choices_needed(self, major: str, track: str, completed_courses: List[str]) -> Dict:
        """
        Identify which course choices the user needs to make for their plan
        """
        choices_needed = {}
        
        if major == "Computer Science":
            if track == "Machine Intelligence":
                # Check AI course choice
                ai_courses = ["CS 47100", "CS 47300"]
                if not any(course in completed_courses for course in ai_courses):
                    choices_needed["ai_course"] = {
                        "category": "AI/ML Course Selection",
                        "options": [
                            {
                                "code": "CS 47100",
                                "title": "Artificial Intelligence",
                                "description": "Traditional AI approaches, search algorithms, knowledge representation. Better for research/graduate school preparation.",
                                "best_for": ["Graduate school", "Research", "Traditional AI"]
                            },
                            {
                                "code": "CS 47300", 
                                "title": "Web Information Search And Management",
                                "description": "Modern web-based AI, machine learning applications. Better for industry applications.",
                                "best_for": ["Industry", "Web development", "Applied ML"]
                            }
                        ],
                        "requirement_type": "Choose 1"
                    }
                
                # Check statistics course choice
                stats_courses = ["STAT 41600", "MA 41600", "STAT 51200"]
                if not any(course in completed_courses for course in stats_courses):
                    choices_needed["stats_course"] = {
                        "category": "Statistics Course Selection",
                        "options": [
                            {
                                "code": "STAT 41600",
                                "title": "Probability",
                                "description": "Pure probability theory. Best foundation for advanced ML.",
                                "best_for": ["Graduate school", "Research", "Theoretical ML"]
                            },
                            {
                                "code": "MA 41600",
                                "title": "Probability",
                                "description": "Mathematical approach to probability. Strong theoretical foundation.",
                                "best_for": ["Mathematics focus", "Theory", "Graduate school"]
                            },
                            {
                                "code": "STAT 51200",
                                "title": "Applied Regression Analysis", 
                                "description": "Applied statistics and data analysis. More practical approach.",
                                "best_for": ["Industry", "Data science", "Applied work"]
                            }
                        ],
                        "requirement_type": "Choose 1"
                    }
                    
                # Check for MI track electives
                elective_options = self._get_mi_elective_options(completed_courses)
                if elective_options:
                    choices_needed["mi_electives"] = {
                        "category": "MI Track Electives",
                        "options": elective_options,
                        "requirement_type": "Choose 2"
                    }
                    
            elif track == "Software Engineering":
                # Check compiler/OS choice
                compiler_os_courses = ["CS 35200", "CS 35400"]
                if not any(course in completed_courses for course in compiler_os_courses):
                    choices_needed["compiler_os_course"] = {
                        "category": "Systems Course Selection",
                        "options": [
                            {
                                "code": "CS 35200",
                                "title": "Compilers Front End",
                                "description": "Compiler design and language processing. Better for language/compiler work.",
                                "best_for": ["Language design", "Compiler development", "Programming languages"]
                            },
                            {
                                "code": "CS 35400",
                                "title": "Operating Systems",
                                "description": "OS internals, system programming. Better for systems programming.",
                                "best_for": ["Systems programming", "OS development", "Low-level work"]
                            }
                        ],
                        "requirement_type": "Choose 1"
                    }
                
                # Check for SE track elective
                se_elective_options = self._get_se_elective_options(completed_courses)
                if se_elective_options:
                    choices_needed["se_elective"] = {
                        "category": "SE Track Elective",
                        "options": se_elective_options,
                        "requirement_type": "Choose 1"
                    }
        
        elif major == "Data Science":
            # Data Science elective choices
            ds_elective_options = self._get_ds_elective_options(completed_courses)
            if ds_elective_options:
                choices_needed["ds_electives"] = {
                    "category": "Data Science Electives",
                    "options": ds_elective_options,
                    "requirement_type": "Choose based on interests"
                }
        
        elif major == "Artificial Intelligence":
            # AI major CS selectives choices
            ai_cs_elective_options = self._get_ai_cs_elective_options(completed_courses)
            if ai_cs_elective_options:
                choices_needed["ai_cs_selectives"] = {
                    "category": "AI CS Selective Courses",
                    "options": ai_cs_elective_options,
                    "requirement_type": "Choose 3 (2 CS Selective I, 1 CS Selective II)"
                }
            
            # AI major philosophy selective choices
            ai_phil_elective_options = self._get_ai_philosophy_elective_options(completed_courses)
            if ai_phil_elective_options:
                choices_needed["ai_philosophy_selective"] = {
                    "category": "AI Philosophy Selective",
                    "options": ai_phil_elective_options,
                    "requirement_type": "Choose 1"
                }
        
        return choices_needed

    def _create_choice_request_plan(self, course_choices_needed: Dict, student_profile: Dict) -> PersonalizedGraduationPlan:
        """
        Create a special plan that requests user choices before continuing
        """
        from smart_ai_engine import SmartAIEngine
        
        # Use AI to generate choice request
        ai_engine = SmartAIEngine()
        
        choice_prompt = f"""
        Generate a friendly, conversational message asking the student to make course choices for their {student_profile.get('major', 'Computer Science')} degree plan.
        
        Student Context:
        - Major: {student_profile.get('major')}
        - Track: {student_profile.get('track', '')}
        - Current Year: {student_profile.get('current_year', 1)}
        - Completed Courses: {len(student_profile.get('completed_courses', []))} courses
        
        Course Choices Needed:
        {course_choices_needed}
        
        Guidelines:
        - Be encouraging and helpful
        - Explain why these choices matter for their career goals
        - Present options clearly with benefits of each
        - Ask them to respond with their selections
        - Keep it conversational and not overwhelming
        """
        
        try:
            ai_response = ai_engine.generate_smart_response(choice_prompt, student_profile)
        except:
            ai_response = self._generate_fallback_choice_message(course_choices_needed, student_profile)
        
        # Create a special plan that indicates choices are needed
        return PersonalizedGraduationPlan(
            major=student_profile.get('major', 'Computer Science'),
            track=student_profile.get('track', ''),
            total_semesters=0,
            graduation_date="Pending Course Selections",
            schedules=[],
            completed_courses=student_profile.get('completed_courses', []),
            remaining_requirements={},
            warnings=[],
            recommendations=[],
            success_probability=0.0,
            customization_notes=[ai_response],
            choice_request=course_choices_needed
        )

    def _generate_fallback_choice_message(self, course_choices_needed: Dict, student_profile: Dict) -> str:
        """
        Generate a fallback choice message when AI is not available
        """
        major = student_profile.get('major', 'Computer Science')
        track = student_profile.get('track', '')
        
        message_parts = [
            f"I need your input to create the perfect {major}"
        ]
        
        if track:
            message_parts.append(f"({track} track)")
            
        message_parts.append("graduation plan for you! You have some course options to choose from:")
        
        for choice_key, choice_info in course_choices_needed.items():
            message_parts.append(f"\n**{choice_info['category']}** ({choice_info['requirement_type']}):")
            
            for option in choice_info['options']:
                message_parts.append(f"• {option['code']}: {option['title']}")
                message_parts.append(f"  {option['description']}")
                if 'best_for' in option:
                    message_parts.append(f"  Best for: {', '.join(option['best_for'])}")
        
        message_parts.append("\nPlease let me know your preferences, and I'll create your complete personalized graduation plan!")
        
        return " ".join(message_parts)

    def _get_mi_elective_options(self, completed_courses: List[str]) -> List[Dict]:
        """Get Machine Intelligence elective options"""
        elective_options = [
            {
                "code": "CS 57300",
                "title": "Data Mining",
                "description": "Advanced data analysis and pattern recognition techniques.",
                "best_for": ["Data science", "Industry analytics", "Big data"]
            },
            {
                "code": "CS 54701", 
                "title": "Information Retrieval",
                "description": "Search engines, text processing, and information systems.",
                "best_for": ["Search technology", "NLP", "Web development"]
            },
            {
                "code": "CS 52500",
                "title": "Computational Linguistics",
                "description": "Natural language processing and computational linguistics.",
                "best_for": ["NLP", "Language technology", "Research"]
            }
        ]
        
        # Filter out already completed courses
        return [opt for opt in elective_options if opt["code"] not in completed_courses]

    def _get_se_elective_options(self, completed_courses: List[str]) -> List[Dict]:
        """Get Software Engineering elective options"""
        elective_options = [
            {
                "code": "CS 42200",
                "title": "Computer Networks",
                "description": "Network protocols, distributed systems, and network programming.",
                "best_for": ["Network programming", "Distributed systems", "Backend development"]
            },
            {
                "code": "CS 54200",
                "title": "Database Systems",
                "description": "Database design, implementation, and optimization.",
                "best_for": ["Database development", "Backend systems", "Data management"]
            },
            {
                "code": "CS 50300",
                "title": "Software Engineering",
                "description": "Advanced software engineering practices and methodologies.",
                "best_for": ["Software architecture", "Team development", "Project management"]
            }
        ]
        
        return [opt for opt in elective_options if opt["code"] not in completed_courses]

    def _get_ds_elective_options(self, completed_courses: List[str]) -> List[Dict]:
        """Get Data Science elective options"""
        elective_options = [
            {
                "code": "CS 57300",
                "title": "Data Mining", 
                "description": "Advanced techniques for extracting insights from large datasets.",
                "best_for": ["Analytics", "Big data", "Machine learning"]
            },
            {
                "code": "STAT 51400",
                "title": "Design of Experiments",
                "description": "Statistical experimental design and analysis methods.",
                "best_for": ["Research", "A/B testing", "Scientific analysis"]
            },
            {
                "code": "CS 54100",
                "title": "Database Systems",
                "description": "Database design and management for data science applications.",
                "best_for": ["Data engineering", "Database design", "Data management"]
            }
        ]
        
        return [opt for opt in elective_options if opt["code"] not in completed_courses]

    def _get_ai_cs_elective_options(self, completed_courses: List[str]) -> List[Dict]:
        """Get AI major CS elective options"""
        elective_options = [
            {
                "code": "CS 52600",
                "title": "Computer Graphics",
                "description": "Computer graphics algorithms, 3D modeling, and visualization techniques.",
                "best_for": ["Computer vision", "Gaming", "Visualization", "VR/AR"]
            },
            {
                "code": "CS 52700", 
                "title": "Computational Neuroscience",
                "description": "Mathematical models of neural systems and brain function.",
                "best_for": ["Brain-computer interfaces", "Neural networks", "Cognitive modeling"]
            },
            {
                "code": "CS 54000",
                "title": "Database Systems",
                "description": "Database design, implementation, and optimization for AI applications.",
                "best_for": ["Data management", "Big data", "Information retrieval"]
            },
            {
                "code": "CS 58000",
                "title": "Algorithm Design and Analysis",
                "description": "Advanced algorithms and complexity analysis for AI systems.",
                "best_for": ["Research", "Optimization", "Theoretical AI"]
            },
            {
                "code": "CS 59000",
                "title": "Natural Language Processing",
                "description": "Computational techniques for understanding and generating human language.",
                "best_for": ["NLP", "Chatbots", "Language technology"]
            },
            {
                "code": "CS 53600",
                "title": "Robotics",
                "description": "Robot control, perception, and autonomous navigation systems.",
                "best_for": ["Robotics", "Autonomous systems", "Control systems"]
            }
        ]
        
        return [opt for opt in elective_options if opt["code"] not in completed_courses]

    def _get_ai_philosophy_elective_options(self, completed_courses: List[str]) -> List[Dict]:
        """Get AI major philosophy elective options"""
        elective_options = [
            {
                "code": "PHIL 32500",
                "title": "Philosophy of Mind",
                "description": "Explores consciousness, mental states, and the mind-body problem.",
                "best_for": ["Cognitive AI", "Consciousness research", "Philosophy of AI"]
            },
            {
                "code": "PHIL 32600",
                "title": "Philosophy of Language",
                "description": "Nature of language, meaning, and communication in natural and artificial systems.",
                "best_for": ["Natural language processing", "Computational linguistics", "AI communication"]
            },
            {
                "code": "PHIL 27000",
                "title": "Symbolic Logic",
                "description": "Formal logic systems and reasoning methods.",
                "best_for": ["Knowledge representation", "Automated reasoning", "Logic programming"]
            },
            {
                "code": "PHIL 32300",
                "title": "Philosophy of Cognitive Science",
                "description": "Philosophical foundations of cognitive science and artificial intelligence.",
                "best_for": ["Cognitive modeling", "AI theory", "Interdisciplinary AI research"]
            }
        ]
        
        return [opt for opt in elective_options if opt["code"] not in completed_courses]

    def parse_user_course_selections(self, user_response: str, course_choices_needed: Dict) -> Dict:
        """
        Parse user's course selection response and return structured selections
        """
        selections = {}
        user_response_lower = user_response.lower()
        
        # Parse each choice category
        for choice_key, choice_info in course_choices_needed.items():
            for option in choice_info['options']:
                course_code = option['code']
                course_title = option['title'].lower()
                
                # Check if user mentioned this course
                if (course_code.lower() in user_response_lower or 
                    course_title in user_response_lower or
                    any(keyword.lower() in user_response_lower for keyword in option.get('best_for', []))):
                    
                    if choice_key not in selections:
                        selections[choice_key] = []
                    selections[choice_key].append(course_code)
        
        return selections

    def _select_courses_for_semester(self, available_courses: List[Dict], semester: str, 
                                   year: int, credit_limit: int, remaining_requirements: Dict,
                                   major: str, track: str) -> Tuple[List[Dict], int, int]:
        """
        Intelligent course selection for a specific semester
        """
        selected = []
        total_credits = 0
        cs_credits = 0
        
        # Priority system for course selection
        prioritized_courses = self._prioritize_courses(
            available_courses, semester, year, remaining_requirements, major, track
        )
        
        for course_info in prioritized_courses:
            course_credits = course_info.get("credits", 3)
            
            # Check if adding this course exceeds limits
            if total_credits + course_credits <= credit_limit:
                # Special logic for CS course limits
                if course_info["code"].startswith("CS"):
                    cs_limit = self._get_cs_course_limit(year, semester)
                    if cs_credits + course_credits <= cs_limit * 3:  # Assuming 3 credits per CS course average
                        selected.append(course_info)
                        total_credits += course_credits
                        cs_credits += course_credits
                else:
                    selected.append(course_info)
                    total_credits += course_credits
        
        # Fill remaining credits with electives if under minimum
        min_credits = 12 if semester != "Summer" else 6
        if total_credits < min_credits:
            electives = self._get_elective_options(major, track, min_credits - total_credits)
            for elective in electives:
                if total_credits + elective["credits"] <= credit_limit:
                    selected.append(elective)
                    total_credits += elective["credits"]
                    break
        
        return selected, total_credits, cs_credits

    def _prioritize_courses(self, available_courses: List[Dict], semester: str, 
                          year: int, remaining_requirements: Dict, major: str, track: str) -> List[Dict]:
        """
        Prioritize courses based on multiple factors
        """
        priority_scores = {}
        
        for course in available_courses:
            code = course["code"]
            score = 0
            
            # Foundation courses get highest priority
            if self._is_foundation_course(code, major):
                score += 100
            
            # Prerequisites for other courses
            if self._is_prerequisite_for_many(code, remaining_requirements):
                score += 50
            
            # Track-specific requirements
            if self._is_track_requirement(code, track, major):
                score += 40
            
            # Courses offered only in specific semesters
            if self._is_limited_offering(code, semester):
                score += 30
            
            # Year-appropriate courses
            if self._is_year_appropriate(code, year, major):
                score += 20
            
            priority_scores[code] = score
        
        # Sort by priority score (highest first)
        return sorted(available_courses, 
                     key=lambda x: priority_scores.get(x["code"], 0), 
                     reverse=True)

    def ask_clarifying_questions(self, student_profile: Dict) -> List[str]:
        """
        Generate intelligent questions to gather missing information for personalization
        """
        questions = []
        
        # Check for missing basic information
        if not student_profile.get("completed_courses"):
            questions.append("What CS and math courses have you already completed? Please list them with course codes (e.g., CS 18000, MA 16100).")
        
        if not student_profile.get("current_year"):
            questions.append("What's your current academic year? (freshman, sophomore, junior, senior)")
        
        if not student_profile.get("major"):
            questions.append("Which major are you in? (Computer Science, Data Science, or Artificial Intelligence)")
        
        # Only Computer Science major has tracks - the other two are standalone majors
        if student_profile.get("major") == "Computer Science" and not student_profile.get("track"):
            questions.append("Which CS track interests you? (Machine Intelligence or Software Engineering)")
            
        if student_profile.get("major") == "Data Science":
            questions.append("Data Science is an interdisciplinary major combining computer science, statistics, and domain expertise. Are you ready for this analytical focus?")
            
        if student_profile.get("major") == "Artificial Intelligence":
            questions.append("AI major combines computer science, psychology, philosophy, and mathematics. Are you comfortable with this interdisciplinary approach?")
        
        if "summer_courses" not in student_profile:
            questions.append("Are you willing/able to take summer courses to accelerate your progress?")
        
        if not student_profile.get("graduation_goal"):
            questions.append("What's your graduation timeline goal? (3 years, 3.5 years, standard 4 years, or flexible)")
        
        if not student_profile.get("credit_load"):
            questions.append("Do you prefer a lighter course load (12-15 credits), standard load (15-18 credits), or can you handle a heavy load (18+ credits)?")
        
        # Ask about specific circumstances
        completed = student_profile.get("completed_courses", [])
        if completed:
            # Check for unusual course combinations
            if "CS 24000" in completed and "CS 18200" not in completed:
                questions.append("I notice you've taken CS 24000 but not CS 18200 - did you skip it or take it somewhere else?")
            
            # Check for summer courses taken
            advanced_courses = [c for c in completed if c.startswith("CS 3") or c.startswith("CS 4")]
            if advanced_courses:
                questions.append("Have you taken any summer courses or are you ahead of the typical schedule?")
        
        return questions

    def _calculate_remaining_requirements(self, major: str, track: str, completed_courses: List[str], selected_choices: Dict = None) -> Dict[str, List[str]]:
        """
        Calculate what requirements are still needed
        """
        if major == "Computer Science":
            return self._calculate_cs_remaining_requirements(track, completed_courses, selected_choices)
        elif major == "Data Science":
            return self._calculate_ds_remaining_requirements(completed_courses, selected_choices)
        elif major == "Artificial Intelligence":
            return self._calculate_ai_remaining_requirements(completed_courses, selected_choices)
        else:
            raise ValueError(f"Unknown major: {major}")

    def _calculate_cs_remaining_requirements(self, track: str, completed_courses: List[str], selected_choices: Dict = None) -> Dict[str, List[str]]:
        """
        Calculate remaining CS requirements with user selections
        """
        # Core CS requirements
        core_foundation = ["CS 18000", "CS 18200", "CS 24000", "CS 25000", "CS 25100", "CS 25200"]
        core_intermediate = ["CS 35100", "CS 38100"]
        
        # Math requirements
        math_required = ["MA 16100", "MA 16200", "MA 26100", "MA 26500", "STAT 35000"]
        
        # Track-specific requirements with user selections
        track_requirements = self._get_track_requirements_with_choices(track, selected_choices)
        
        # Science requirements
        science_required = ["PHYS 17200", "PHYS 27200"]
        
        # Calculate remaining
        remaining = {
            "core_foundation": [c for c in core_foundation if c not in completed_courses],
            "core_intermediate": [c for c in core_intermediate if c not in completed_courses],
            "math": [c for c in math_required if c not in completed_courses],
            "track_specific": [c for c in track_requirements if c not in completed_courses],
            "science": [c for c in science_required if c not in completed_courses],
            "general_education": self._calculate_gen_ed_remaining(completed_courses),
            "free_electives": self._calculate_free_electives_remaining(completed_courses)
        }
        
        return remaining

    def _calculate_ds_remaining_requirements(self, completed_courses: List[str], selected_choices: Dict = None) -> Dict[str, List[str]]:
        """
        Calculate remaining Data Science requirements with user selections
        """
        # Get Data Science sample 4-year plan from knowledge base
        ds_info = self.knowledge.get("Data Science", {})
        sample_plan = ds_info.get("sample_4_year_plan", {})
        
        # Extract all required courses from the sample plan
        all_required_courses = []
        for semester_key, semester_info in sample_plan.items():
            if isinstance(semester_info, dict) and "courses" in semester_info:
                for course in semester_info["courses"]:
                    if isinstance(course, dict) and "code" in course:
                        course_code = course["code"]
                        # Handle alternative courses (e.g., "MA 16100 or MA 16500")
                        if " or " in course_code:
                            # For now, take the first option
                            course_code = course_code.split(" or ")[0]
                        all_required_courses.append(course_code)
        
        # Add user-selected electives if provided
        if selected_choices:
            for choice_key, choice_courses in selected_choices.items():
                if choice_key == "ds_electives" and isinstance(choice_courses, list):
                    all_required_courses.extend(choice_courses)
        
        # Categorize requirements
        cs_courses = [c for c in all_required_courses if c.startswith("CS")]
        math_courses = [c for c in all_required_courses if c.startswith("MA")]
        stat_courses = [c for c in all_required_courses if c.startswith("STAT")]
        science_courses = [c for c in all_required_courses if c.startswith("PHYS") or c.startswith("CHEM") or c.startswith("BIOL")]
        other_courses = [c for c in all_required_courses if not any(c.startswith(prefix) for prefix in ["CS", "MA", "STAT", "PHYS", "CHEM", "BIOL"])]
        
        remaining = {
            "cs_foundation": [c for c in cs_courses if c not in completed_courses and (c.startswith("CS 1") or c.startswith("CS 2"))],
            "cs_advanced": [c for c in cs_courses if c not in completed_courses and (c.startswith("CS 3") or c.startswith("CS 4"))],
            "math": [c for c in math_courses if c not in completed_courses],
            "statistics": [c for c in stat_courses if c not in completed_courses],
            "science": [c for c in science_courses if c not in completed_courses],
            "other_requirements": [c for c in other_courses if c not in completed_courses],
            "general_education": self._calculate_gen_ed_remaining(completed_courses),
            "electives": []  # Data Science typically has fewer free electives
        }
        
        return remaining

    def _calculate_ai_remaining_requirements(self, completed_courses: List[str], selected_choices: Dict = None) -> Dict[str, List[str]]:
        """
        Calculate remaining Artificial Intelligence major requirements with user selections
        """
        # Get AI major sample 4-year plan from knowledge base
        ai_info = self.knowledge.get("Artificial Intelligence", {})
        sample_plan = ai_info.get("sample_4_year_plan", {})
        
        # Extract all required courses from the sample plan
        all_required_courses = []
        for semester_key, semester_info in sample_plan.items():
            if isinstance(semester_info, dict) and "courses" in semester_info:
                for course in semester_info["courses"]:
                    if isinstance(course, dict) and "code" in course:
                        course_code = course["code"]
                        # Handle alternative courses (e.g., "MA 16100 or MA 16500")
                        if " or " in course_code:
                            # For now, take the first option
                            course_code = course_code.split(" or ")[0]
                        # Skip generic course selections for now
                        if course_code not in ["Science Core Selection", "Elective", "CS Selective I", "CS Selective II", "Philosophy Selective"]:
                            all_required_courses.append(course_code)
        
        # Add user-selected electives if provided
        if selected_choices:
            for choice_key, choice_courses in selected_choices.items():
                if choice_key in ["ai_cs_selectives", "ai_philosophy_selective"] and isinstance(choice_courses, list):
                    all_required_courses.extend(choice_courses)
        
        # Categorize AI major requirements
        cs_courses = [c for c in all_required_courses if c.startswith("CS")]
        math_courses = [c for c in all_required_courses if c.startswith("MA")]
        stat_courses = [c for c in all_required_courses if c.startswith("STAT")]
        psych_courses = [c for c in all_required_courses if c.startswith("PSY")]
        phil_courses = [c for c in all_required_courses if c.startswith("PHIL")]
        other_courses = [c for c in all_required_courses if not any(c.startswith(prefix) for prefix in ["CS", "MA", "STAT", "PSY", "PHIL"])]
        
        remaining = {
            "cs_foundation": [c for c in cs_courses if c not in completed_courses and (c.startswith("CS 1") or c.startswith("CS 2"))],
            "cs_advanced": [c for c in cs_courses if c not in completed_courses and (c.startswith("CS 3") or c.startswith("CS 4"))],
            "math": [c for c in math_courses if c not in completed_courses],
            "statistics": [c for c in stat_courses if c not in completed_courses],
            "psychology": [c for c in psych_courses if c not in completed_courses],
            "philosophy": [c for c in phil_courses if c not in completed_courses],
            "other_requirements": [c for c in other_courses if c not in completed_courses],
            "cs_selectives": self._calculate_ai_cs_selectives_remaining(completed_courses, selected_choices),
            "science_core": self._calculate_ai_science_core_remaining(completed_courses),
            "electives": self._calculate_ai_electives_remaining(completed_courses)
        }
        
        return remaining

    def _calculate_ai_cs_selectives_remaining(self, completed_courses: List[str], selected_choices: Dict = None) -> List[str]:
        """Calculate remaining CS selective requirements for AI major"""
        # AI major requires 3 CS selectives total (2 CS Selective I, 1 CS Selective II)
        needed_selectives = 3
        
        # Count completed CS electives (courses beyond core requirements)
        ai_core_cs = ["CS 17600", "CS 18000", "CS 18200", "CS 24300", "CS 25300", "CS 37300", "CS 38100", "CS 47100"]
        completed_selectives = [c for c in completed_courses if c.startswith("CS") and c not in ai_core_cs]
        
        # Add user-selected selectives
        if selected_choices and "ai_cs_selectives" in selected_choices:
            completed_selectives.extend(selected_choices["ai_cs_selectives"])
        
        remaining_count = max(0, needed_selectives - len(set(completed_selectives)))
        return [f"CS Selective {i+1}" for i in range(remaining_count)]

    def _calculate_ai_science_core_remaining(self, completed_courses: List[str]) -> List[str]:
        """Calculate remaining science core requirements for AI major"""
        # AI major requires 8 science core courses (24 credits)
        needed_science_courses = 8
        
        # Count completed science courses (simplified - would need more detailed tracking)
        science_prefixes = ["PHYS", "CHEM", "BIOL", "EAPS", "ENGL"]
        completed_science = [c for c in completed_courses if any(c.startswith(prefix) for prefix in science_prefixes)]
        
        remaining_count = max(0, needed_science_courses - len(completed_science))
        return [f"Science Core Selection {i+1}" for i in range(remaining_count)]

    def _calculate_ai_electives_remaining(self, completed_courses: List[str]) -> List[str]:
        """Calculate remaining free electives for AI major"""
        # AI major requires 3 elective courses (9 credits)
        needed_electives = 3
        
        # This would need more sophisticated tracking in a real implementation
        # For now, assume all electives are still needed
        return [f"Elective {i+1}" for i in range(needed_electives)]

    def _get_semester_sequence(self, current_semester: str, current_year: int, graduation_goal: str) -> List[Dict]:
        """
        Generate the sequence of semesters until graduation
        """
        sequences = {
            "3_year": 6,    # 6 semesters
            "3.5_year": 7,  # 7 semesters
            "4_year": 8,    # 8 semesters
            "flexible": 10  # Up to 10 semesters
        }
        
        total_semesters = sequences.get(graduation_goal, 8)
        semester_list = []
        
        semester_names = ["Fall", "Spring", "Summer"] if graduation_goal in ["3_year", "3.5_year"] else ["Fall", "Spring"]
        semester_idx = 0 if current_semester == "Fall" else 1
        year = current_year
        
        for i in range(total_semesters):
            semester_name = semester_names[semester_idx % len(semester_names)]
            
            semester_list.append({
                "semester": semester_name,
                "year": year
            })
            
            semester_idx += 1
            
            # Increment year after Spring semester (or after Summer if including summers)
            if semester_name == "Spring" or (semester_name == "Summer" and len(semester_names) == 3):
                year += 1
        
        return semester_list

    def _get_available_courses(self, needed_courses: List[str], planned_courses: Set[str], 
                             semester: str, major: str, track: str) -> List[Dict]:
        """
        Get courses that can be taken in this semester based on prerequisites
        """
        available = []
        
        for course_code in needed_courses:
            if course_code in planned_courses:
                continue
                
            # Check prerequisites
            if self._check_prerequisites_met(course_code, planned_courses):
                # Check if course is offered this semester
                if self._is_course_offered(course_code, semester):
                    course_info = self._get_course_info(course_code, major)
                    if course_info:
                        available.append(course_info)
        
        return available

    def _check_prerequisites_met(self, course_code: str, completed_and_planned: Set[str]) -> bool:
        """
        Check if prerequisites for a course are met
        """
        prerequisites = self.prerequisites.get(course_code, [])
        
        for prereq in prerequisites:
            if isinstance(prereq, list):  # OR condition (any one of these)
                if not any(p in completed_and_planned for p in prereq):
                    return False
            else:  # Single prerequisite
                if prereq not in completed_and_planned:
                    return False
        
        return True

    def _build_prerequisite_graph(self) -> Dict[str, List]:
        """
        Build prerequisite relationships from knowledge base
        """
        prerequisites = {}
        
        # CS Foundation sequence
        prerequisites["CS 18200"] = ["CS 18000"]
        prerequisites["CS 24000"] = ["CS 18200"]
        prerequisites["CS 25000"] = ["CS 24000"]
        prerequisites["CS 25100"] = ["CS 24000"]
        prerequisites["CS 25200"] = ["CS 25000", "CS 25100"]
        
        # AI Major specific prerequisites
        prerequisites["CS 24300"] = ["CS 18200"]  # AI Basics after Foundations of CS
        prerequisites["CS 25300"] = ["CS 18200"]  # Data Structures for DS/AI after Foundations
        
        # Intermediate courses
        prerequisites["CS 35100"] = ["CS 25200"]
        prerequisites["CS 38100"] = ["CS 25100"]
        
        # Advanced courses
        prerequisites["CS 37300"] = ["CS 25100", "STAT 35000"]
        prerequisites["CS 47100"] = ["CS 37300"]
        prerequisites["CS 47300"] = ["CS 37300"]
        prerequisites["CS 30700"] = ["CS 25200"]
        prerequisites["CS 40700"] = ["CS 30700"]
        prerequisites["CS 40800"] = ["CS 38100"]
        prerequisites["CS 35200"] = ["CS 25200"]
        prerequisites["CS 35400"] = ["CS 25200"]
        
        # Math sequence
        prerequisites["MA 16200"] = ["MA 16100"]
        prerequisites["MA 26100"] = ["MA 16200"]
        prerequisites["MA 26500"] = ["MA 16200"]
        
        # Statistics
        prerequisites["STAT 35000"] = ["MA 16200"]
        prerequisites["STAT 41600"] = ["STAT 35000", "MA 26100"]
        
        # Physics
        prerequisites["PHYS 27200"] = ["PHYS 17200", "MA 16200"]
        
        return prerequisites

    def _load_cs_templates(self) -> Dict:
        """Load CS semester templates"""
        return {
            "standard_4_year": {
                "fall_1": ["CS 18000", "MA 16100", "ENGL 10600", "General Ed"],
                "spring_1": ["CS 18200", "CS 24000", "MA 16200", "General Ed"],
                "fall_2": ["CS 25000", "CS 25100", "MA 26100", "General Ed"],
                "spring_2": ["CS 25200", "MA 26500", "STAT 35000", "General Ed"],
                "fall_3": ["CS 35100", "CS 38100", "PHYS 17200", "General Ed"],
                "spring_3": ["Track Courses", "PHYS 27200", "Free Elective"],
                "fall_4": ["Track Courses", "Free Electives", "General Ed"],
                "spring_4": ["Track Courses", "Free Electives", "General Ed"]
            }
        }

    def _load_ds_templates(self) -> Dict:
        """Load Data Science semester templates from knowledge base"""
        ds_info = self.knowledge.get("Data Science", {})
        sample_plan = ds_info.get("sample_4_year_plan", {})
        
        templates = {}
        for semester_key, semester_info in sample_plan.items():
            if isinstance(semester_info, dict):
                courses = []
                if "courses" in semester_info:
                    for course in semester_info["courses"]:
                        if isinstance(course, dict) and "code" in course:
                            courses.append(course["code"])
                        else:
                            courses.append(str(course))
                templates[semester_key] = courses
        
        return {"standard_4_year": templates}

    def _load_ai_templates(self) -> Dict:
        """Load AI semester templates from knowledge base"""
        ai_info = self.knowledge.get("Artificial Intelligence", {})
        sample_plan = ai_info.get("sample_4_year_plan", {})
        
        templates = {}
        for semester_key, semester_info in sample_plan.items():
            if isinstance(semester_info, dict):
                courses = []
                if "courses" in semester_info:
                    for course in semester_info["courses"]:
                        if isinstance(course, dict) and "code" in course:
                            courses.append(course["code"])
                        else:
                            courses.append(str(course))
                templates[semester_key] = courses
        
        return {"standard_4_year": templates}

    def _initialize_course_offerings(self) -> Dict:
        """Initialize when courses are typically offered"""
        return {
            # Fall only courses
            "fall_only": ["CS 47100", "CS 40800"],
            # Spring only courses  
            "spring_only": ["CS 47300", "CS 40700"],
            # Fall and Spring
            "both_semesters": ["CS 18000", "CS 18200", "CS 24000", "CS 25000", "CS 25100", 
                              "CS 25200", "CS 35100", "CS 38100", "CS 37300", "CS 30700"],
            # Summer offerings (limited)
            "summer_available": ["CS 18000", "CS 18200", "CS 24000", "CS 25000", "CS 25100"]
        }

    def _is_course_offered(self, course_code: str, semester: str) -> bool:
        """Check if a course is offered in a given semester"""
        if semester == "Summer":
            return course_code in self.course_offerings["summer_available"]
        elif semester == "Fall":
            return (course_code in self.course_offerings["fall_only"] or 
                   course_code in self.course_offerings["both_semesters"])
        elif semester == "Spring":
            return (course_code in self.course_offerings["spring_only"] or 
                   course_code in self.course_offerings["both_semesters"])
        return True  # Default to available

    def _get_course_info(self, course_code: str, major: str) -> Dict:
        """Get detailed course information"""
        # Try to find course in knowledge base
        courses = self.knowledge.get("courses", {})
        if course_code in courses:
            course_info = courses[course_code].copy()
            course_info["code"] = course_code
            return course_info
        
        # Default course info
        return {
            "code": course_code,
            "title": course_code,  # Fallback
            "credits": 3,
            "description": f"Course {course_code}"
        }

    def _validate_completed_courses(self, completed_courses: List[str]) -> List[str]:
        """Validate and normalize completed course codes"""
        validated = []
        for course in completed_courses:
            normalized = self._normalize_course_code(course)
            if normalized:
                validated.append(normalized)
        return list(set(validated))  # Remove duplicates

    def _normalize_course_code(self, course_code: str) -> str:
        """Normalize course code to standard format"""
        if not course_code:
            return ""
        
        # Handle common formats: CS 180 -> CS 18000, CS180 -> CS 18000
        course_code = course_code.upper().replace(" ", "")
        
        # Extract department and number
        import re
        match = re.match(r"([A-Z]+)(\d+)", course_code)
        if not match:
            return course_code
        
        dept, num = match.groups()
        
        # Normalize CS course numbers
        if dept == "CS" and len(num) == 3:
            return f"{dept} {num}00"
        elif dept in ["MA", "STAT"] and len(num) == 3:
            return f"{dept} {num}00"
        
        return f"{dept} {num}"

    def _flatten_requirements(self, requirements: Dict[str, List[str]]) -> List[str]:
        """Flatten requirements dictionary into a single list"""
        all_courses = []
        for req_type, courses in requirements.items():
            if isinstance(courses, list):
                all_courses.extend(courses)
        return all_courses

    def _get_credit_limits(self, preference: str) -> Dict[str, int]:
        """Get credit limits based on student preference"""
        limits = {
            "light": {"fall": 15, "spring": 15, "summer": 6},
            "standard": {"fall": 18, "spring": 18, "summer": 9},
            "heavy": {"fall": 21, "spring": 21, "summer": 12}
        }
        return limits.get(preference, limits["standard"])

    def _get_cs_course_limit(self, year: int, semester: str) -> int:
        """Get CS course limit based on year"""
        if year == 1:  # Freshman
            return 2
        elif semester == "Summer":
            return 2
        else:
            return 3

    def _is_foundation_course(self, course_code: str, major: str) -> bool:
        """Check if course is a foundation course"""
        if major == "Computer Science":
            foundation = ["CS 18000", "CS 18200", "CS 24000", "CS 25000", "CS 25100", "CS 25200"]
            return course_code in foundation
        elif major == "Data Science":
            foundation = ["CS 18000", "CS 18200", "CS 24200", "STAT 35500"]
            return course_code in foundation
        elif major == "Artificial Intelligence":
            foundation = ["CS 17600", "CS 18000", "CS 18200", "CS 24300", "CS 25300"]
            return course_code in foundation
        return False

    def _is_prerequisite_for_many(self, course_code: str, remaining_requirements: Dict) -> bool:
        """Check if course is a prerequisite for many other courses"""
        prereq_count = 0
        all_remaining = self._flatten_requirements(remaining_requirements)
        
        for remaining_course in all_remaining:
            if course_code in self.prerequisites.get(remaining_course, []):
                prereq_count += 1
        
        return prereq_count >= 2

    def _is_track_requirement(self, course_code: str, track: str, major: str) -> bool:
        """Check if course is a track requirement"""
        if major == "Computer Science":
            track_courses = self._get_track_requirements(track)
            return course_code in track_courses
        return False

    def _is_limited_offering(self, course_code: str, semester: str) -> bool:
        """Check if course has limited semester offerings"""
        if semester == "Fall":
            return course_code in self.course_offerings["fall_only"]
        elif semester == "Spring":
            return course_code in self.course_offerings["spring_only"]
        return False

    def _is_year_appropriate(self, course_code: str, year: int, major: str) -> bool:
        """Check if course is appropriate for the student's year"""
        course_level = self._get_course_level(course_code)
        
        if year == 1:  # Freshman
            return course_level in [1, 2]
        elif year == 2:  # Sophomore
            return course_level in [1, 2, 3]
        elif year == 3:  # Junior
            return course_level in [2, 3, 4]
        else:  # Senior
            return course_level in [3, 4]

    def _get_course_level(self, course_code: str) -> int:
        """Get course level (1=freshman, 2=sophomore, etc.)"""
        if course_code.startswith("CS 1") or course_code.startswith("MA 1"):
            return 1
        elif course_code.startswith("CS 2") or course_code.startswith("MA 2") or course_code.startswith("STAT 3"):
            return 2
        elif course_code.startswith("CS 3"):
            return 3
        elif course_code.startswith("CS 4"):
            return 4
        else:
            return 2  # Default to sophomore level

    def _get_track_requirements_with_choices(self, track: str, selected_choices: Dict = None) -> List[str]:
        """Get track-specific requirements incorporating user choices"""
        base_requirements = {
            "Machine Intelligence": ["CS 37300", "CS 38100"],
            "Software Engineering": ["CS 30700", "CS 38100", "CS 40700", "CS 40800"]
        }
        
        requirements = base_requirements.get(track, [])
        
        # Add user-selected courses
        if selected_choices:
            if track == "Machine Intelligence":
                # Add AI course choice
                if "ai_course" in selected_choices:
                    requirements.extend(selected_choices["ai_course"])
                
                # Add statistics course choice
                if "stats_course" in selected_choices:
                    requirements.extend(selected_choices["stats_course"])
                
                # Add MI electives
                if "mi_electives" in selected_choices:
                    requirements.extend(selected_choices["mi_electives"])
                    
            elif track == "Software Engineering":
                # Add compiler/OS choice
                if "compiler_os_course" in selected_choices:
                    requirements.extend(selected_choices["compiler_os_course"])
                
                # Add SE elective
                if "se_elective" in selected_choices:
                    requirements.extend(selected_choices["se_elective"])
        
        return requirements

    def _get_track_requirements(self, track: str) -> List[str]:
        """Get track-specific requirements (fallback for compatibility)"""
        tracks = {
            "Machine Intelligence": ["CS 37300", "CS 38100", "CS 47100", "STAT 41600"],
            "Software Engineering": ["CS 30700", "CS 38100", "CS 40700", "CS 40800", "CS 35200"]
        }
        return tracks.get(track, [])

    def _calculate_gen_ed_remaining(self, completed_courses: List[str]) -> List[str]:
        """Calculate remaining general education requirements"""
        # Simplified - would need more detailed tracking in real implementation
        gen_ed_categories = [
            "ENGL 10600",  # Written Communication
            "COMM 11400",  # Oral Communication  
            "General Ed Science",
            "General Ed Humanities",
            "General Ed Social Sciences"
        ]
        
        # Filter out what's already completed (simplified check)
        remaining = []
        for req in gen_ed_categories:
            if not any(req in course for course in completed_courses):
                remaining.append(req)
        
        return remaining

    def _calculate_free_electives_remaining(self, completed_courses: List[str]) -> List[str]:
        """Calculate remaining free electives needed"""
        # Simplified calculation - would need credit hour tracking
        return ["Free Elective 1", "Free Elective 2", "Free Elective 3"]

    def _get_elective_options(self, major: str, track: str, credits_needed: int) -> List[Dict]:
        """Get elective course options"""
        electives = [
            {"code": "Free Elective", "title": "Free Elective", "credits": 3},
            {"code": "General Education", "title": "General Education", "credits": 3},
            {"code": "Technical Elective", "title": "Technical Elective", "credits": 3}
        ]
        
        return electives[:max(1, credits_needed // 3)]

    def _generate_semester_feedback(self, selected_courses: List[Dict], semester: str, 
                                  year: int, major: str, track: str) -> Tuple[List[str], List[str]]:
        """Generate warnings and recommendations for a semester"""
        warnings = []
        recommendations = []
        
        cs_courses = [c for c in selected_courses if c["code"].startswith("CS")]
        total_credits = sum(c.get("credits", 3) for c in selected_courses)
        
        # Check course load
        if len(cs_courses) > 3:
            warnings.append(f"Heavy CS course load ({len(cs_courses)} CS courses) - consider reducing if struggling")
        
        if total_credits > 18:
            warnings.append(f"High credit load ({total_credits} credits) - ensure you can handle the workload")
        elif total_credits < 12 and semester != "Summer":
            warnings.append(f"Low credit load ({total_credits} credits) - may delay graduation")
        
        # Check for difficult course combinations
        difficult_combos = [
            (["CS 25000", "CS 25100"], "CS 25000 and CS 25100 together is challenging"),
            (["CS 38100", "CS 37300"], "Two algorithm-heavy courses in one semester")
        ]
        
        for combo, warning in difficult_combos:
            if all(any(c["code"] == course for c in selected_courses) for course in combo):
                warnings.append(warning)
        
        # Generate recommendations
        if year == 1 and len(cs_courses) == 1:
            recommendations.append("Good balance for freshman year - focus on building strong foundations")
        
        if semester == "Fall" and any(c["code"] in ["CS 47100", "CS 40800"] for c in selected_courses):
            recommendations.append("Taking advantage of fall-only course offerings - good planning!")
        
        return warnings, recommendations

    def _analyze_plan_feasibility(self, schedules: List[PersonalizedCourseSchedule], 
                                graduation_goal: str, credit_load_preference: str) -> Tuple[float, List[str], List[str]]:
        """Analyze the feasibility of the generated plan"""
        warnings = []
        recommendations = []
        success_factors = []
        
        # Calculate average credits per semester
        total_credits = sum(s.total_credits for s in schedules if s.semester != "Summer")
        regular_semesters = len([s for s in schedules if s.semester != "Summer"])
        avg_credits = total_credits / regular_semesters if regular_semesters > 0 else 0
        
        # Analyze credit load
        if avg_credits > 18:
            success_factors.append(-0.2)  # High credit load reduces success probability
            warnings.append("High average credit load may be challenging to maintain")
        elif avg_credits < 15:
            success_factors.append(-0.1)  # Low credit load might indicate problems meeting requirements
            warnings.append("Low credit load - plan may not meet graduation requirements")
        else:
            success_factors.append(0.1)  # Reasonable credit load
        
        # Analyze CS course distribution
        cs_heavy_semesters = sum(1 for s in schedules if s.cs_credits > 9)
        if cs_heavy_semesters > len(schedules) * 0.5:
            success_factors.append(-0.15)
            warnings.append("Many semesters with heavy CS course loads")
        
        # Analyze graduation timeline
        if graduation_goal == "3_year" and len(schedules) > 6:
            success_factors.append(-0.3)
            warnings.append("3-year graduation goal may not be achievable with current progress")
        elif graduation_goal == "4_year" and len(schedules) > 8:
            success_factors.append(-0.1)
            warnings.append("May need extra semester to complete requirements")
        
        # Generate recommendations
        if graduation_goal in ["3_year", "3.5_year"]:
            recommendations.append("Consider summer courses to lighten regular semester loads")
        
        recommendations.append("Meet with academic advisor to validate this plan")
        recommendations.append("Monitor your progress each semester and adjust as needed")
        
        # Calculate overall success probability
        base_probability = 0.75
        adjustment = sum(success_factors)
        success_probability = max(0.1, min(0.95, base_probability + adjustment))
        
        return success_probability, warnings, recommendations

    def _generate_customization_notes(self, student_profile: Dict, completed_courses: List[str], 
                                    schedules: List[PersonalizedCourseSchedule]) -> List[str]:
        """Generate notes about how the plan was customized"""
        notes = []
        
        # Note about completed courses
        if completed_courses:
            notes.append(f"Plan customized based on {len(completed_courses)} completed courses: {', '.join(completed_courses[:5])}{'...' if len(completed_courses) > 5 else ''}")
        
        # Note about graduation goal
        goal = student_profile.get("graduation_goal", "4_year")
        if goal != "4_year":
            notes.append(f"Accelerated timeline for {goal.replace('_', ' ')} graduation")
        
        # Note about course load preference
        load_pref = student_profile.get("credit_load", "standard")
        if load_pref != "standard":
            notes.append(f"Adjusted for {load_pref} course load preference")
        
        # Note about summer courses
        if student_profile.get("summer_courses", True):
            summer_semesters = [s for s in schedules if s.semester == "Summer"]
            if summer_semesters:
                notes.append(f"Includes {len(summer_semesters)} summer semester(s) for acceleration")
        
        # Note about track selection
        track = student_profile.get("track")
        if track:
            notes.append(f"Optimized for {track} track requirements")
        
        return notes

    def _calculate_graduation_date(self, schedules: List[PersonalizedCourseSchedule]) -> str:
        """Calculate graduation date from schedule"""
        if not schedules:
            # Generate AI response for unknown graduation date
            try:
                if hasattr(self, 'ai_response_generator') and self.ai_response_generator:
                    return self.ai_response_generator.ai_engine.generate_smart_response(
                        "Generate a brief phrase to indicate graduation date cannot be determined due to missing schedule data.",
                        {"context": "graduation_date_unknown"}
                    ) or "To be determined"
                else:
                    return "To be determined"
            except:
                return "To be determined"
        
        last_schedule = schedules[-1]
        return f"{last_schedule.semester} {last_schedule.year}"

def main():
    """Example usage"""
    planner = PersonalizedGraduationPlanner(
        "data/cs_knowledge_graph.json",
        "purdue_cs_knowledge.db"
    )
    
    # Example: Student who has taken some summer courses and wants to graduate early
    student_profile = {
        "major": "Computer Science",
        "track": "Machine Intelligence",
        "completed_courses": ["CS 18000", "CS 18200", "CS 24000", "MA 16100", "MA 16200", "ENGL 10600"],
        "current_semester": "Fall",
        "current_year": 2,
        "summer_courses": True,
        "credit_load": "standard",
        "graduation_goal": "3.5_year"
    }
    
    # Generate personalized plan
    plan = planner.create_personalized_plan(student_profile)
    
    # Generate AI-powered presentation instead of hardcoded format
    try:
        from smart_ai_engine import SmartAIEngine
        ai_engine = SmartAIEngine()
        
        # Create context for AI to generate plan presentation
        plan_context = {
            "major": plan.major,
            "track": plan.track,
            "graduation_date": plan.graduation_date,
            "success_probability": f"{plan.success_probability:.1%}",
            "customization_notes": plan.customization_notes,
            "schedules": []
        }
        
        for schedule in plan.schedules:
            schedule_info = {
                "semester": schedule.semester,
                "year": schedule.year,
                "credits": schedule.total_credits,
                "courses": [f"{course['code']} - {course.get('title', course['code'])}" for course in schedule.courses],
                "warnings": schedule.warnings,
                "recommendations": schedule.recommendations
            }
            plan_context["schedules"].append(schedule_info)
        
        prompt = f"""
        Present this personalized graduation plan in a clear, organized, and encouraging way:
        {plan_context}
        
        Format it to be easy to read and motivating for the student. Include all the important details like graduation timeline, course sequences, and any warnings or recommendations.
        """
        
        ai_presentation = ai_engine.generate_smart_response(prompt, {"context": "graduation_plan_presentation"})
        print(ai_presentation or f"Personalized {plan.major} Graduation Plan")
        
    except Exception as e:
        # Fallback to basic display if AI fails
        print(f"Personalized {plan.major} Graduation Plan")
        print(f"Track: {plan.track}")
        print(f"Expected Graduation: {plan.graduation_date}")
        print(f"Success Probability: {plan.success_probability:.1%}")

if __name__ == "__main__":
    main()