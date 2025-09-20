#!/usr/bin/env python3
"""
Purdue CS Degree Progression Parser
Parses the 2025-2026 degree progression guide and updates knowledge graph
"""

import json
import sqlite3
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import re

@dataclass
class Course:
    code: str
    title: str
    credits: int
    semester: str  # "Fall 1st Year", "Spring 2nd Year", etc.
    course_type: str  # "foundation", "math", "statistics", "track", "elective", "science_core"
    prerequisites: List[str]
    corequisites: List[str]
    is_critical: bool = False
    track_applicable: Optional[str] = None  # Which track this applies to
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []
        if self.corequisites is None:
            self.corequisites = []

@dataclass
class DegreeProgression:
    foundation_courses: List[Course]
    math_courses: List[Course]
    statistics_courses: List[Course]
    science_core_requirements: Dict[str, List[str]]
    track_course_slots: Dict[str, List[str]]  # When track courses can be taken
    all_available_courses: List[Course]
    track_definitions: Dict[str, Dict]

class PurdueProgressionParser:
    def __init__(self):
        self.progression = DegreeProgression(
            foundation_courses=[],
            math_courses=[],
            statistics_courses=[],
            science_core_requirements={},
            track_course_slots={},
            all_available_courses=[],
            track_definitions={}
        )
        
    def parse_pdf_data(self):
        """Parse the degree progression data from the PDF"""
        
        # Foundation Courses (required for all CS majors)
        foundation_courses = [
            Course("CS 18000", "Problem Solving and Object-Oriented Programming", 4, 
                   "Fall 1st Year", "foundation", [], ["MA 16100"], True),
            Course("CS 18200", "Foundations of Computer Science", 3, 
                   "Spring 1st Year", "foundation", ["CS 18000", "MA 16100"], [], True),
            Course("CS 24000", "Programming in C", 3, 
                   "Spring 1st Year", "foundation", ["CS 18000"], [], True),
            Course("CS 25000", "Computer Architecture", 4, 
                   "Fall 2nd Year", "foundation", ["CS 18200", "CS 24000"], [], True),
            Course("CS 25100", "Data Structures", 3, 
                   "Fall 2nd Year", "foundation", ["CS 18200", "CS 24000"], [], True),
            Course("CS 25200", "Systems Programming", 4, 
                   "Spring 2nd Year", "foundation", ["CS 25000", "CS 25100"], [], True),
        ]
        
        # Math Requirements
        math_courses = [
            Course("MA 16100", "Calculus I", 5, "Fall 1st Year", "math", ["ALEKS 85+"], [], True),
            Course("MA 16500", "Calculus I (Honors)", 5, "Fall 1st Year", "math", ["ALEKS 85+"], [], True),
            Course("MA 16200", "Calculus II", 5, "Spring 1st Year", "math", ["MA 16100"], [], True),
            Course("MA 16600", "Calculus II (Honors)", 5, "Spring 1st Year", "math", ["MA 16500"], [], True),
            Course("MA 26100", "Multivariate Calculus", 4, "Fall 2nd Year", "math", ["MA 16200"], [], True),
            Course("MA 27101", "Multivariate Calculus (Honors)", 5, "Fall 2nd Year", "math", ["MA 16600"], [], True),
            Course("MA 26500", "Linear Algebra", 3, "Spring 2nd Year", "math", ["MA 16200"], ["MA 26100"], True),
            Course("MA 35100", "Linear Algebra (Advanced)", 3, "Spring 2nd Year", "math", ["MA 16200"], ["MA 26100"], True),
        ]
        
        # Statistics Requirement
        statistics_courses = [
            Course("STAT 35000", "Elementary Statistics", 3, "Fall 3rd Year", "statistics", ["MA 16200"], []),
            Course("STAT 51100", "Statistical Methods", 3, "Fall 3rd Year", "statistics", ["MA 16200"], []),
        ]
        
        # Track Course Timing Slots
        track_course_slots = {
            "Fall 3rd Year": ["CS track requirement"],
            "Spring 3rd Year": ["CS track requirement/elective"],
            "Fall 4th Year": ["CS track elective"],
            "Spring 4th Year": ["CS track elective"]
        }
        
        # All Available CS Courses (from PDF pages 3-4)
        all_cs_courses = [
            Course("CS 30700", "Software Engineering I", 3, "track_course", "track", ["CS 25200"], []),
            Course("CS 31400", "Numerical Methods", 3, "track_course", "track", ["MA 26100", "CS 25100"], []),
            Course("CS 33400", "Fundamentals of Computer Graphics", 3, "track_course", "track", ["CS 25100", "MA 26500"], []),
            Course("CS 34800", "Information Systems", 3, "track_course", "track", ["CS 25100"], []),
            Course("CS 35100", "Cloud Computing", 3, "track_course", "track", ["CS 25200"], []),
            Course("CS 35200", "Compilers", 3, "track_course", "track", ["CS 25100"], []),
            Course("CS 35300", "Principles Of Concurrency and Parallelism", 3, "track_course", "track", ["CS 25200"], []),
            Course("CS 35400", "Operating Systems", 3, "track_course", "track", ["CS 25200"], []),
            Course("CS 35500", "Introduction to Cryptography", 3, "track_course", "track", ["CS 25100", "MA 26500"], []),
            Course("CS 37300", "Data Mining & Machine Learning", 3, "track_course", "track", ["CS 25100", "STAT 35000"], []),
            Course("CS 38100", "Introduction to Algorithms", 3, "Fall 3rd Year", "foundation", ["CS 25100"], []),  # Note: This is actually foundation but taken later
            Course("CS 40700", "Software Engineering Senior Project", 3, "track_course", "track", ["CS 30700"], []),
            Course("CS 40800", "Software Testing", 3, "track_course", "track", ["CS 30700"], []),
            Course("CS 42200", "Computer Networks", 3, "track_course", "track", ["CS 25200"], []),
            Course("CS 42600", "Computer Security", 3, "track_course", "track", ["CS 25200"], []),
            Course("CS 43400", "Advanced Computer Graphics", 3, "track_course", "track", ["CS 33400"], []),
            Course("CS 43900", "Introduction to Data Visualization", 3, "track_course", "track", ["CS 25100"], []),
            Course("CS 44000", "Large-Scale Data Analytics", 3, "track_course", "track", ["CS 25100"], []),
            Course("CS 44800", "Introduction to Relational Databases", 3, "track_course", "track", ["CS 25100"], []),
            Course("CS 45600", "Programming Languages", 3, "track_course", "track", ["CS 25100"], []),
            Course("CS 45800", "Introduction to Robotics", 3, "track_course", "track", ["CS 25100", "MA 26500"], []),
            Course("CS 47100", "Introduction to Artificial Intelligence", 3, "track_course", "track", ["CS 25100"], []),
            Course("CS 47300", "Web Information Search & Management", 3, "track_course", "track", ["CS 25100"], []),
            Course("CS 47500", "Human-Computer Interaction", 3, "track_course", "track", ["CS 25100"], []),
            Course("CS 47800", "Introduction to Bioinformatics", 3, "track_course", "track", ["CS 25100"], []),
            Course("CS 48300", "Introduction to the Theory of Computation", 3, "track_course", "track", ["CS 25100"], []),
            Course("CS 48900", "Embedded Systems", 3, "track_course", "track", ["CS 25200"], []),
            Course("CS 49000-DSO", "Distributed Systems", 3, "track_course", "track", ["CS 25200"], []),
            Course("CS 49000-SWS", "Software Security", 3, "track_course", "track", ["CS 25200"], []),
            Course("CS 49700", "Honors Research Project", 3, "track_course", "track", ["CS 25100"], []),
            Course("CS 51000", "Software Engineering", 3, "track_course", "track", ["CS 30700"], []),
            Course("CS 51400", "Numerical Analysis", 3, "track_course", "track", ["CS 31400"], []),
            Course("CS 51500", "Numerical Linear Algebra", 3, "track_course", "track", ["CS 31400"], []),
            Course("CS 52000", "Computational Methods In Optimization", 3, "track_course", "track", ["CS 31400"], []),
            Course("CS 52500", "Parallel Computing", 3, "track_course", "track", ["CS 35300"], []),
            Course("CS 56000", "Reasoning About Programs", 3, "track_course", "track", ["CS 35200"], []),
            Course("CS 57700", "Natural Language Processing", 3, "track_course", "track", ["CS 37300"], []),
            Course("CS 57800", "Statistical Machine Learning", 3, "track_course", "track", ["CS 37300"], []),
            Course("CS 59000-SRS", "Software Reliability and Security", 3, "track_course", "track", ["CS 30700"], []),
        ]
        
        # Track Definitions (from PDF)
        track_definitions = {
            "computational_science_engineering": {
                "name": "Computational Science and Engineering",
                "code": "CSE",
                "focus_areas": ["numerical_methods", "optimization", "scientific_computing"]
            },
            "computer_graphics_visualization": {
                "name": "Computer Graphics and Visualization", 
                "code": "CGV",
                "focus_areas": ["graphics", "visualization", "human_computer_interaction"]
            },
            "database_information_systems": {
                "name": "Database and Information Systems",
                "code": "DIS", 
                "focus_areas": ["databases", "information_systems", "data_analytics"]
            },
            "algorithmic_foundations": {
                "name": "Algorithmic Foundations",
                "code": "AF",
                "focus_areas": ["algorithms", "theory", "computational_complexity"]
            },
            "machine_intelligence": {
                "name": "Machine Intelligence",
                "code": "MI",
                "focus_areas": ["machine_learning", "artificial_intelligence", "data_mining"]
            },
            "programming_language": {
                "name": "Programming Language",
                "code": "PL",
                "focus_areas": ["compilers", "programming_languages", "language_design"]
            },
            "security": {
                "name": "Security",
                "code": "SEC",
                "focus_areas": ["cybersecurity", "cryptography", "network_security"]
            },
            "software_engineering": {
                "name": "Software Engineering",
                "code": "SE", 
                "focus_areas": ["software_development", "testing", "project_management"]
            },
            "systems_software": {
                "name": "Systems Software",
                "code": "SS",
                "focus_areas": ["operating_systems", "distributed_systems", "computer_architecture"]
            }
        }
        
        # Science Core Requirements
        science_core_requirements = {
            "written_communication": ["ENGL 10600", "ENGL 10800"],
            "technical_writing": ["COM 21700"],  # Recommended
            "computing": ["CS 18000"],  # Satisfied by major
            "foreign_language": ["varies"],  # 0-9 credits
            "general_education": ["varies"],  # 3 courses needed
            "lab_science": ["varies"],  # 2 courses needed
            "science_technology_society": ["varies"],
            "great_issues": ["varies"]
        }
        
        # Update the progression object
        self.progression.foundation_courses = foundation_courses
        self.progression.math_courses = math_courses
        self.progression.statistics_courses = statistics_courses
        self.progression.track_course_slots = track_course_slots
        self.progression.all_available_courses = all_cs_courses
        self.progression.track_definitions = track_definitions
        self.progression.science_core_requirements = science_core_requirements
        
        return self.progression
    
    def update_track_requirements(self):
        """Update track-specific requirements based on corrected information"""
        
        # Machine Intelligence Track - CORRECTED
        mi_track_requirements = {
            "name": "Machine Intelligence Track",
            "code": "MI",
            "foundation_courses": [
                "CS 18000", "CS 18200", "CS 24000", "CS 25000", "CS 25100", "CS 25200"
            ],
            "required_courses": {
                "cs_38100": {
                    "course": "CS 38100",
                    "title": "Introduction to Algorithms",
                    "timing": "Fall 3rd Year",
                    "note": "Required foundation course taken in 3rd year"
                },
                "data_mining_ml": {
                    "course": "CS 37300",
                    "title": "Data Mining & Machine Learning",
                    "timing": "Fall 3rd Year or later",
                    "note": "Core MI requirement"
                },
                "ai_choice": {
                    "description": "AI Requirement",
                    "choose": 1,
                    "options": ["CS 47100", "CS 47300"],
                    "note": "Choose CS 47100 (AI) OR CS 47300 (Web Info Search)"
                },
                "stats_choice": {
                    "description": "Statistics Requirement", 
                    "choose": 1,
                    "options": ["STAT 41600", "MA 41600", "STAT 51200"],
                    "note": "Advanced statistics requirement"
                }
            },
            "elective_requirements": {
                "count": 2,
                "constraint": "Exactly 2 electives from approved list",
                "data_viz_group": "At most 1 from data visualization group"
            }
        }
        
        # Software Engineering Track - CORRECTED
        se_track_requirements = {
            "name": "Software Engineering Track",
            "code": "SE",
            "foundation_courses": [
                "CS 18000", "CS 18200", "CS 24000", "CS 25000", "CS 25100", "CS 25200"
            ],
            "required_courses": {
                "cs_38100": {
                    "course": "CS 38100",
                    "title": "Introduction to Algorithms",
                    "timing": "Fall 3rd Year",
                    "note": "Required foundation course taken in 3rd year"
                },
                "software_eng_1": {
                    "course": "CS 30700",
                    "title": "Software Engineering I",
                    "timing": "Fall 3rd Year or later",
                    "note": "Core SE requirement"
                },
                "software_testing": {
                    "course": "CS 40800",
                    "title": "Software Testing",
                    "timing": "After CS 30700",
                    "note": "Core SE requirement"
                },
                "senior_project": {
                    "course": "CS 40700",
                    "title": "Software Engineering Senior Project",
                    "timing": "Senior year",
                    "note": "Capstone project"
                },
                "compiler_os_choice": {
                    "description": "Compilers OR Operating Systems",
                    "choose": 1,
                    "options": ["CS 35200", "CS 35400"],
                    "note": "Choose CS 35200 (Compilers) OR CS 35400 (Operating Systems)"
                }
            },
            "elective_requirements": {
                "count": 1,
                "constraint": "Exactly 1 elective from approved list",
                "epics_substitution": "EPICS participation can substitute for elective"
            }
        }
        
        return {
            "machine_intelligence": mi_track_requirements,
            "software_engineering": se_track_requirements
        }

class ProgressionKnowledgeGraphUpdater:
    def __init__(self):
        self.parser = PurdueProgressionParser()
        self.db_path = "data/purdue_cs_knowledge.db"
        
    def update_knowledge_graph(self):
        """Update the knowledge graph with corrected progression data"""
        
        # Parse the progression data
        progression = self.parser.parse_pdf_data()
        track_requirements = self.parser.update_track_requirements()
        
        # Update the JSON knowledge graph
        self.update_json_knowledge_graph(progression, track_requirements)
        
        # Update the vector store with new data
        self.update_vector_store(progression)
        
        return {
            "status": "success",
            "foundation_courses_added": len(progression.foundation_courses),
            "total_courses_added": len(progression.all_available_courses),
            "tracks_updated": len(track_requirements)
        }
    
    def update_json_knowledge_graph(self, progression, track_requirements):
        """Update the JSON knowledge graph file"""
        
        # Build comprehensive course data
        courses = {}
        prerequisites = {}
        
        # Add foundation courses
        for course in progression.foundation_courses:
            courses[course.code] = {
                "title": course.title,
                "credits": course.credits,
                "description": f"{course.title} - {course.semester}",
                "course_type": course.course_type,
                "semester": course.semester,
                "is_critical": course.is_critical
            }
            if course.prerequisites:
                prerequisites[course.code] = course.prerequisites
        
        # Add math courses
        for course in progression.math_courses:
            courses[course.code] = {
                "title": course.title,
                "credits": course.credits,
                "description": f"{course.title} - {course.semester}",
                "course_type": course.course_type,
                "semester": course.semester,
                "is_critical": course.is_critical
            }
            if course.prerequisites:
                prerequisites[course.code] = course.prerequisites
        
        # Add statistics courses
        for course in progression.statistics_courses:
            courses[course.code] = {
                "title": course.title,
                "credits": course.credits,
                "description": f"{course.title} - {course.semester}",
                "course_type": course.course_type,
                "semester": course.semester
            }
            if course.prerequisites:
                prerequisites[course.code] = course.prerequisites
        
        # Add all available CS courses
        for course in progression.all_available_courses:
            courses[course.code] = {
                "title": course.title,
                "credits": course.credits,
                "description": f"{course.title} - Track course",
                "course_type": course.course_type,
                "semester": course.semester
            }
            if course.prerequisites:
                prerequisites[course.code] = course.prerequisites
        
        # Build track definitions
        tracks = {}
        for track_key, track_data in track_requirements.items():
            tracks[track_data["name"]] = {
                "required_courses": [req["course"] for req in track_data["required_courses"].values() if "course" in req],
                "choice_requirements": {k: v for k, v in track_data["required_courses"].items() if "options" in v},
                "elective_requirements": track_data["elective_requirements"],
                "foundation_courses": track_data["foundation_courses"]
            }
        
        # Save updated knowledge graph
        knowledge_graph_data = {
            "courses": courses,
            "tracks": tracks,
            "prerequisites": prerequisites,
            "progression_data": {
                "foundation_sequence": [course.code for course in progression.foundation_courses],
                "math_sequence": [course.code for course in progression.math_courses],
                "statistics_options": [course.code for course in progression.statistics_courses],
                "track_timing": progression.track_course_slots
            },
            "updated": datetime.now().isoformat()
        }
        
        with open("data/cs_knowledge_graph.json", "w") as f:
            json.dump(knowledge_graph_data, f, indent=2)
        
        print("✓ Updated knowledge graph with corrected progression data")
    
    def update_vector_store(self, progression):
        """Update vector store with new progression data"""
        
        # Import here to avoid circular imports
        from setup_vector_store import create_vector_store
        
        # Recreate vector store with updated data
        create_vector_store()
        
        print("✓ Updated vector store with corrected progression data")

def generate_training_data_from_progression():
    """Generate training data from the corrected progression"""
    
    parser = PurdueProgressionParser()
    progression = parser.parse_pdf_data()
    track_requirements = parser.update_track_requirements()
    
    training_data = []
    
    # Generate progression timing questions
    training_data.extend([
        {
            "query": "When should I take CS 38100?",
            "response": "CS 38100 (Introduction to Algorithms) should be taken in Fall 3rd Year. This is a critical course that requires CS 25100 as a prerequisite and must be completed before taking advanced track courses.",
            "confidence": 0.95,
            "source": "progression_timing"
        },
        {
            "query": "Can I take track courses in my second year?",
            "response": "No, track courses cannot be taken until Fall 3rd Year. You must complete the foundation sequence (CS 18000, 18200, 24000, 25000, 25100, 25200) first, which takes the first two years.",
            "confidence": 0.95,
            "source": "progression_timing"
        },
        {
            "query": "What's the correct course sequence for CS majors?",
            "response": "Years 1-2: Foundation courses (CS 18000→18200→24000→25000→25100→25200). Fall 3rd Year: CS 38100 + track courses begin. This sequence ensures proper prerequisite completion.",
            "confidence": 0.95,
            "source": "progression_sequence"
        }
    ])
    
    # Generate track-specific questions
    for track_key, track_data in track_requirements.items():
        training_data.extend([
            {
                "query": f"What are the requirements for {track_data['name']}?",
                "response": f"{track_data['name']} requires: CS 38100 (Fall 3rd Year), core track courses, and {track_data['elective_requirements']['count']} electives. Complete foundation sequence first.",
                "confidence": 0.90,
                "source": f"track_requirements_{track_key}"
            }
        ])
    
    return training_data

if __name__ == "__main__":
    # Update the system with corrected data
    updater = ProgressionKnowledgeGraphUpdater()
    result = updater.update_knowledge_graph()
    
    if result["status"] == "success":
        print("✅ Knowledge graph updated successfully")
        print(f"📊 Summary: {result['foundation_courses_added']} foundation courses, {result['total_courses_added']} total courses, {result['tracks_updated']} tracks")
    else:
        print("❌ Update failed")