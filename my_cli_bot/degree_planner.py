#!/usr/bin/env python3
"""
Complete Degree Planner System
Comprehensive degree planning with exact track requirements, progress tracking, and semester planning
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from knowledge_graph import PurdueCSKnowledgeGraph

class DegreeTrackDatabase:
    """Complete track requirements database with exact course specifications"""
    
    TRACK_REQUIREMENTS = {
        'machine_intelligence': {
            'total_courses': 6,
            'required_courses': 4,
            'elective_courses': 2,
            'requirements': {
                'core_required': [
                    {
                        'course': 'CS 37300',
                        'title': 'Data Mining and Machine Learning',
                        'credits': 3,
                        'description': 'Core MI course - introduction to ML algorithms, data preprocessing, model evaluation',
                        'prerequisites': ['CS 25100', 'STAT 35000'],
                        'mandatory': True
                    },
                    {
                        'course': 'CS 38100',
                        'title': 'Introduction to Algorithms',
                        'credits': 3,
                        'description': 'Algorithm design and analysis - required for all tracks',
                        'prerequisites': ['CS 25100'],
                        'mandatory': True,
                        'timing': 'Fall Junior Year'
                    }
                ],
                'foundation_choice': {
                    'description': 'Choose 1 AI foundation course',
                    'required_count': 1,
                    'options': [
                        {
                            'course': 'CS 47100',
                            'title': 'Introduction to Artificial Intelligence',
                            'credits': 3,
                            'description': 'Search algorithms, knowledge representation, machine learning basics',
                            'prerequisites': ['CS 25100']
                        },
                        {
                            'course': 'CS 47300',
                            'title': 'Web Information Search and Management',
                            'credits': 3,
                            'description': 'Information retrieval, web search, text processing',
                            'prerequisites': ['CS 25100']
                        }
                    ]
                },
                'stats_choice': {
                    'description': 'Choose 1 statistics/probability course',
                    'required_count': 1,
                    'options': [
                        {
                            'course': 'STAT 41600',
                            'title': 'Probability',
                            'credits': 3,
                            'description': 'Mathematical probability theory - more rigorous',
                            'prerequisites': ['MA 26100']
                        },
                        {
                            'course': 'MA 41600',
                            'title': 'Probability',
                            'credits': 3,
                            'description': 'Mathematical probability from math department',
                            'prerequisites': ['MA 26100']
                        },
                        {
                            'course': 'STAT 51200',
                            'title': 'Applied Regression Analysis',
                            'credits': 3,
                            'description': 'Statistical modeling and regression - practical focus',
                            'prerequisites': ['STAT 35000']
                        }
                    ]
                },
                'electives': {
                    'description': 'Choose 2 elective courses from approved list',
                    'required_count': 2,
                    'options': [
                        {
                            'course': 'CS 57700',
                            'title': 'Natural Language Processing',
                            'credits': 3,
                            'description': 'Text processing and language understanding',
                            'prerequisites': ['CS 37300']
                        },
                        {
                            'course': 'CS 57800',
                            'title': 'Statistical Machine Learning',
                            'credits': 3,
                            'description': 'Advanced machine learning theory',
                            'prerequisites': ['CS 37300']
                        },
                        {
                            'course': 'CS 43900',
                            'title': 'Introduction to Data Visualization',
                            'credits': 3,
                            'description': 'Data visualization techniques and tools',
                            'prerequisites': ['CS 25100'],
                            'note': 'Cannot take with CS 44000 or CS 47500'
                        },
                        {
                            'course': 'CS 44000',
                            'title': 'Large-Scale Data Analytics',
                            'credits': 3,
                            'description': 'Big data processing and analytics',
                            'prerequisites': ['CS 25100'],
                            'note': 'Cannot take with CS 43900 or CS 47500'
                        },
                        {
                            'course': 'CS 44800',
                            'title': 'Introduction to Relational Database Systems',
                            'credits': 3,
                            'description': 'Database design and SQL',
                            'prerequisites': ['CS 25100']
                        },
                        {
                            'course': 'CS 45600',
                            'title': 'Programming Languages',
                            'credits': 3,
                            'description': 'Programming language concepts and design',
                            'prerequisites': ['CS 25100']
                        },
                        {
                            'course': 'CS 45800',
                            'title': 'Introduction to Robotics',
                            'credits': 3,
                            'description': 'Robotics fundamentals and control',
                            'prerequisites': ['CS 25100', 'MA 26500']
                        },
                        {
                            'course': 'CS 48300',
                            'title': 'Introduction to the Theory of Computation',
                            'credits': 3,
                            'description': 'Formal languages and computability',
                            'prerequisites': ['CS 25100']
                        }
                    ]
                }
            }
        },
        
        'software_engineering': {
            'total_courses': 6,
            'required_courses': 5,
            'elective_courses': 1,
            'requirements': {
                'core_required': [
                    {
                        'course': 'CS 30700',
                        'title': 'Software Engineering I',
                        'credits': 3,
                        'description': 'Software development lifecycle and practices',
                        'prerequisites': ['CS 25200'],
                        'mandatory': True
                    },
                    {
                        'course': 'CS 38100',
                        'title': 'Introduction to Algorithms',
                        'credits': 3,
                        'description': 'Algorithm design and analysis',
                        'prerequisites': ['CS 25100'],
                        'mandatory': True,
                        'timing': 'Fall Junior Year'
                    },
                    {
                        'course': 'CS 40800',
                        'title': 'Software Testing',
                        'credits': 3,
                        'description': 'Testing methodologies and quality assurance',
                        'prerequisites': ['CS 30700'],
                        'mandatory': True
                    },
                    {
                        'course': 'CS 40700',
                        'title': 'Software Engineering Senior Project',
                        'credits': 3,
                        'description': 'Capstone software development project',
                        'prerequisites': ['CS 30700'],
                        'mandatory': True,
                        'timing': 'Senior Year'
                    }
                ],
                'systems_choice': {
                    'description': 'Choose 1 systems course',
                    'required_count': 1,
                    'options': [
                        {
                            'course': 'CS 35200',
                            'title': 'Compilers: Principles and Practice',
                            'credits': 3,
                            'description': 'Compiler design and implementation',
                            'prerequisites': ['CS 25200']
                        },
                        {
                            'course': 'CS 35400',
                            'title': 'Operating Systems',
                            'credits': 3,
                            'description': 'Operating system concepts and design',
                            'prerequisites': ['CS 25200']
                        }
                    ]
                },
                'electives': {
                    'description': 'Choose 1 elective course',
                    'required_count': 1,
                    'options': [
                        {
                            'course': 'CS 34800',
                            'title': 'Information Systems',
                            'credits': 3,
                            'description': 'Database systems and information management',
                            'prerequisites': ['CS 25100']
                        },
                        {
                            'course': 'CS 44800',
                            'title': 'Introduction to Relational Database Systems',
                            'credits': 3,
                            'description': 'Database design and SQL',
                            'prerequisites': ['CS 25100']
                        },
                        {
                            'course': 'CS 47500',
                            'title': 'Human-Computer Interactions',
                            'credits': 3,
                            'description': 'User interface design and usability',
                            'prerequisites': ['CS 25100']
                        }
                    ]
                }
            }
        }
    }

class StudentProgressTracker:
    """Track individual student progress and create personalized plans"""
    
    def __init__(self, db_path="purdue_cs_knowledge.db"):
        self.db_path = db_path
        self.setup_database()
        self.logger = self.setup_logger()
        
    def setup_logger(self):
        """Setup logging for degree planning"""
        logger = logging.getLogger('DegreePlanner')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('📋 %(levelname)s: %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def setup_database(self):
        """Setup student tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_progress (
                student_id TEXT PRIMARY KEY,
                name TEXT,
                year TEXT,
                track TEXT,
                completed_courses TEXT, -- JSON array
                in_progress_courses TEXT, -- JSON array
                planned_courses TEXT, -- JSON array
                selected_track_courses TEXT, -- JSON object
                gpa REAL,
                total_credits INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS semester_plans (
                plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                semester TEXT, -- Fall 2024, Spring 2025, etc.
                planned_courses TEXT, -- JSON array
                total_credits INTEGER,
                difficulty_score REAL,
                workload_estimate INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES student_progress(student_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS degree_requirements (
                requirement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                track TEXT,
                requirement_type TEXT, -- foundation, core, elective, choice
                requirement_name TEXT,
                required_courses TEXT, -- JSON array
                completed_courses TEXT, -- JSON array
                remaining_courses TEXT, -- JSON array
                completion_status TEXT, -- complete, in_progress, not_started
                FOREIGN KEY (student_id) REFERENCES student_progress(student_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_student_profile(self, student_id: str, name: str, year: str, 
                              completed_courses: List[str] = None, track: str = None) -> bool:
        """Create new student profile"""
        
        completed_courses = completed_courses or []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO student_progress 
                (student_id, name, year, track, completed_courses, in_progress_courses, 
                 planned_courses, selected_track_courses, total_credits, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                student_id, name, year, track, 
                json.dumps(completed_courses), json.dumps([]), json.dumps([]),
                json.dumps({}), len(completed_courses) * 3,  # Estimate 3 credits per course
                datetime.now().isoformat()
            ))
            
            conn.commit()
            self.logger.info(f"Created student profile: {name} ({student_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create student profile: {e}")
            return False
        finally:
            conn.close()
    
    def get_student_progress(self, student_id: str) -> Optional[Dict]:
        """Get comprehensive student progress"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM student_progress WHERE student_id = ?
            ''', (student_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            # Convert to dictionary
            columns = [desc[0] for desc in cursor.description]
            student_data = dict(zip(columns, result))
            
            # Parse JSON fields
            for field in ['completed_courses', 'in_progress_courses', 'planned_courses', 'selected_track_courses']:
                if student_data[field]:
                    student_data[field] = json.loads(student_data[field])
                else:
                    student_data[field] = [] if field != 'selected_track_courses' else {}
            
            return student_data
            
        except Exception as e:
            self.logger.error(f"Failed to get student progress: {e}")
            return None
        finally:
            conn.close()
    
    def analyze_degree_requirements(self, student_id: str) -> Dict:
        """Analyze what requirements the student has completed and what remains"""
        
        student = self.get_student_progress(student_id)
        if not student or not student['track']:
            return {'error': 'Student not found or track not selected'}
        
        track_name = student['track']
        completed_courses = student['completed_courses']
        
        # Get track requirements
        if track_name not in DegreeTrackDatabase.TRACK_REQUIREMENTS:
            return {'error': f'Track {track_name} not found'}
        
        track_reqs = DegreeTrackDatabase.TRACK_REQUIREMENTS[track_name]
        
        analysis = {
            'student_id': student_id,
            'track': track_name,
            'completed_courses': completed_courses,
            'foundation_status': self._analyze_foundation_requirements(completed_courses),
            'track_requirements': self._analyze_track_requirements(completed_courses, track_reqs),
            'graduation_readiness': {}
        }
        
        # Calculate graduation readiness
        analysis['graduation_readiness'] = self._calculate_graduation_readiness(analysis)
        
        return analysis
    
    def _analyze_foundation_requirements(self, completed_courses: List[str]) -> Dict:
        """Analyze foundation course completion"""
        
        foundation_courses = [
            'CS 18000', 'CS 18200', 'CS 24000', 'CS 25000', 'CS 25100', 'CS 25200',
            'MA 16100', 'MA 16200', 'MA 26100', 'STAT 35000'
        ]
        
        completed_foundation = [course for course in completed_courses if course in foundation_courses]
        remaining_foundation = [course for course in foundation_courses if course not in completed_courses]
        
        return {
            'required_courses': foundation_courses,
            'completed': completed_foundation,
            'remaining': remaining_foundation,
            'completion_percentage': len(completed_foundation) / len(foundation_courses) * 100,
            'status': 'complete' if not remaining_foundation else 'in_progress'
        }
    
    def _analyze_track_requirements(self, completed_courses: List[str], track_reqs: Dict) -> Dict:
        """Analyze track-specific requirements completion"""
        
        analysis = {}
        requirements = track_reqs['requirements']
        
        # Analyze core required courses
        if 'core_required' in requirements:
            core_courses = [course['course'] for course in requirements['core_required']]
            completed_core = [course for course in completed_courses if course in core_courses]
            remaining_core = [course for course in core_courses if course not in completed_courses]
            
            analysis['core_required'] = {
                'required': core_courses,
                'completed': completed_core,
                'remaining': remaining_core,
                'status': 'complete' if not remaining_core else 'in_progress'
            }
        
        # Analyze choice requirements (foundation, stats, systems, etc.)
        for choice_key in requirements:
            if choice_key.endswith('_choice') or choice_key == 'electives':
                choice_req = requirements[choice_key]
                if 'options' in choice_req:
                    choice_courses = [course['course'] for course in choice_req['options']]
                    completed_choice = [course for course in completed_courses if course in choice_courses]
                    required_count = choice_req.get('required_count', 1)
                    
                    analysis[choice_key] = {
                        'required_count': required_count,
                        'available_options': choice_courses,
                        'completed': completed_choice,
                        'completed_count': len(completed_choice),
                        'remaining_count': max(0, required_count - len(completed_choice)),
                        'status': 'complete' if len(completed_choice) >= required_count else 'in_progress'
                    }
        
        return analysis
    
    def _calculate_graduation_readiness(self, analysis: Dict) -> Dict:
        """Calculate overall graduation readiness"""
        
        foundation_complete = analysis['foundation_status']['status'] == 'complete'
        
        track_complete = True
        track_progress = 0
        track_total = 0
        
        for req_key, req_data in analysis['track_requirements'].items():
            if req_key == 'core_required':
                track_total += len(req_data['required'])
                track_progress += len(req_data['completed'])
                if req_data['status'] != 'complete':
                    track_complete = False
            elif 'required_count' in req_data:
                track_total += req_data['required_count']
                track_progress += min(req_data['completed_count'], req_data['required_count'])
                if req_data['status'] != 'complete':
                    track_complete = False
        
        overall_percentage = ((track_progress / track_total * 100) if track_total > 0 else 0) if foundation_complete else 0
        
        return {
            'foundation_complete': foundation_complete,
            'track_complete': track_complete,
            'overall_complete': foundation_complete and track_complete,
            'track_progress_percentage': (track_progress / track_total * 100) if track_total > 0 else 0,
            'overall_percentage': overall_percentage,
            'estimated_semesters_remaining': self._estimate_remaining_semesters(analysis)
        }
    
    def _estimate_remaining_semesters(self, analysis: Dict) -> int:
        """Estimate semesters remaining for graduation"""
        
        total_remaining = 0
        
        # Count foundation courses remaining
        total_remaining += len(analysis['foundation_status']['remaining'])
        
        # Count track courses remaining
        for req_key, req_data in analysis['track_requirements'].items():
            if req_key == 'core_required':
                total_remaining += len(req_data['remaining'])
            elif 'remaining_count' in req_data:
                total_remaining += req_data['remaining_count']
        
        # Estimate 4-5 courses per semester
        return max(1, (total_remaining + 3) // 4)  # Round up
    
    def generate_semester_plan(self, student_id: str, target_semester: str, 
                              max_credits: int = 15) -> Dict:
        """Generate optimized semester plan"""
        
        analysis = self.analyze_degree_requirements(student_id)
        if 'error' in analysis:
            return analysis
        
        student = self.get_student_progress(student_id)
        completed_courses = student['completed_courses']
        
        # Get available courses (prerequisites met)
        available_courses = self._get_available_courses(completed_courses, analysis)
        
        # Prioritize courses
        prioritized_courses = self._prioritize_courses(available_courses, analysis)
        
        # Build semester schedule
        semester_schedule = self._build_semester_schedule(prioritized_courses, max_credits)
        
        return {
            'student_id': student_id,
            'target_semester': target_semester,
            'recommended_courses': semester_schedule,
            'total_credits': sum(course['credits'] for course in semester_schedule),
            'reasoning': self._explain_course_selection(semester_schedule, analysis)
        }
    
    def _get_available_courses(self, completed_courses: List[str], analysis: Dict) -> List[Dict]:
        """Get courses available to take (prerequisites satisfied)"""
        
        available = []
        track_name = analysis['track']
        track_reqs = DegreeTrackDatabase.TRACK_REQUIREMENTS[track_name]['requirements']
        
        # Check foundation courses first
        foundation_remaining = analysis['foundation_status']['remaining']
        for course in foundation_remaining:
            # Add prerequisite checking logic here
            available.append({
                'course': course,
                'type': 'foundation',
                'priority': 'high',
                'credits': 3
            })
        
        # Check track requirements
        for req_key, req_data in analysis['track_requirements'].items():
            if req_key == 'core_required' and req_data['remaining']:
                for course in req_data['remaining']:
                    # Find course details
                    course_details = next((c for c in track_reqs['core_required'] if c['course'] == course), None)
                    if course_details:
                        available.append({
                            'course': course,
                            'type': 'core_required',
                            'priority': 'high',
                            'credits': course_details['credits'],
                            'details': course_details
                        })
            
            elif req_data.get('remaining_count', 0) > 0 and 'available_options' in req_data:
                # Add choice options
                for course in req_data['available_options']:
                    if course not in completed_courses:
                        # Find course details in track requirements
                        for choice_req in track_reqs.values():
                            if isinstance(choice_req, dict) and 'options' in choice_req:
                                course_details = next((c for c in choice_req['options'] if c['course'] == course), None)
                                if course_details:
                                    available.append({
                                        'course': course,
                                        'type': req_key,
                                        'priority': 'medium',
                                        'credits': course_details['credits'],
                                        'details': course_details
                                    })
                                    break
        
        return available
    
    def _prioritize_courses(self, available_courses: List[Dict], analysis: Dict) -> List[Dict]:
        """Prioritize courses for scheduling"""
        
        # Sort by priority and prerequisites
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        
        def course_priority(course):
            base_priority = priority_order.get(course['priority'], 1)
            
            # Boost priority for CS 38100 (critical timing)
            if course['course'] == 'CS 38100':
                base_priority += 10
            
            # Boost priority for foundation courses
            if course['type'] == 'foundation':
                base_priority += 5
            
            return base_priority
        
        return sorted(available_courses, key=course_priority, reverse=True)
    
    def _build_semester_schedule(self, prioritized_courses: List[Dict], max_credits: int) -> List[Dict]:
        """Build optimal semester schedule within credit limit"""
        
        schedule = []
        total_credits = 0
        
        for course in prioritized_courses:
            if total_credits + course['credits'] <= max_credits:
                schedule.append(course)
                total_credits += course['credits']
            
            if total_credits >= max_credits - 2:  # Leave some buffer
                break
        
        return schedule
    
    def _explain_course_selection(self, schedule: List[Dict], analysis: Dict) -> List[str]:
        """Explain why these courses were selected"""
        
        explanations = []
        
        for course in schedule:
            course_code = course['course']
            course_type = course['type']
            
            if course_code == 'CS 38100':
                explanations.append(f"{course_code}: Critical timing - must take Fall junior year")
            elif course_type == 'foundation':
                explanations.append(f"{course_code}: Foundation requirement - prerequisite for track courses")
            elif course_type == 'core_required':
                explanations.append(f"{course_code}: Core track requirement")
            else:
                explanations.append(f"{course_code}: Track elective option")
        
        return explanations

if __name__ == "__main__":
    # Test degree planner
    planner = StudentProgressTracker()
    
    # Create test student
    planner.create_student_profile(
        student_id="test_student",
        name="Test Student",
        year="sophomore",
        completed_courses=["CS 18000", "CS 18200", "CS 24000", "CS 25000", "MA 16100", "MA 16200"],
        track="machine_intelligence"
    )
    
    # Analyze requirements
    analysis = planner.analyze_degree_requirements("test_student")
    print("Degree Analysis:")
    print(json.dumps(analysis, indent=2))
    
    # Generate semester plan
    plan = planner.generate_semester_plan("test_student", "Fall 2025")
    print("\nSemester Plan:")
    print(json.dumps(plan, indent=2))