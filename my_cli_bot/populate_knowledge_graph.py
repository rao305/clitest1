#!/usr/bin/env python3
"""
Complete Knowledge Graph Population System
Populate NetworkX knowledge graph with comprehensive Purdue CS program data
"""

import networkx as nx
import json
import sqlite3
from datetime import datetime
import logging
from knowledge_graph import PurdueCSKnowledgeGraph

class PurdueCSKnowledgeGraphBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.logger = self.setup_logger()
        self.cs_program_data = self.load_complete_program_data()
        
    def setup_logger(self):
        """Setup logging for graph building"""
        logger = logging.getLogger('GraphBuilder')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('🔧 %(levelname)s: %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def load_complete_program_data(self) -> dict:
        """Load complete Purdue CS program data"""
        return {
            'foundation_courses': {
                'CS 18000': {
                    'title': 'Problem Solving and Object-Oriented Programming',
                    'credits': 4,
                    'description': 'Introduction to Java programming, object-oriented concepts, and problem-solving techniques.',
                    'prerequisites': [],
                    'corequisites': ['MA 16100'],
                    'typical_semester': 'freshman_fall',
                    'offered_semesters': ['fall', 'spring', 'summer'],
                    'difficulty': 3.2,
                    'workload_hours': 12,
                    'required': True,
                    'course_type': 'foundation'
                },
                'CS 18200': {
                    'title': 'Foundations of Computer Science',
                    'credits': 3,
                    'description': 'Mathematical foundations including discrete mathematics, logic, and proof techniques.',
                    'prerequisites': ['CS 18000'],
                    'corequisites': [],
                    'typical_semester': 'freshman_spring',
                    'offered_semesters': ['fall', 'spring'],
                    'difficulty': 3.8,
                    'workload_hours': 10,
                    'required': True,
                    'course_type': 'foundation'
                },
                'CS 24000': {
                    'title': 'Programming in C',
                    'credits': 3,
                    'description': 'Introduction to C programming, memory management, and systems programming concepts.',
                    'prerequisites': ['CS 18000'],
                    'corequisites': [],
                    'typical_semester': 'freshman_spring',
                    'offered_semesters': ['fall', 'spring'],
                    'difficulty': 3.5,
                    'workload_hours': 11,
                    'required': True,
                    'course_type': 'foundation'
                },
                'CS 25000': {
                    'title': 'Computer Architecture',
                    'credits': 4,
                    'description': 'Computer organization, instruction sets, assembly language, and digital logic.',
                    'prerequisites': ['CS 18200', 'CS 24000'],
                    'corequisites': [],
                    'typical_semester': 'sophomore_fall',
                    'offered_semesters': ['fall', 'spring'],
                    'difficulty': 4.0,
                    'workload_hours': 13,
                    'required': True,
                    'course_type': 'foundation'
                },
                'CS 25100': {
                    'title': 'Data Structures',
                    'credits': 3,
                    'description': 'Linear and nonlinear data structures, algorithm analysis, and implementation.',
                    'prerequisites': ['CS 18200', 'CS 24000'],
                    'corequisites': [],
                    'typical_semester': 'sophomore_fall',
                    'offered_semesters': ['fall', 'spring'],
                    'difficulty': 4.1,
                    'workload_hours': 14,
                    'required': True,
                    'course_type': 'foundation'
                },
                'CS 25200': {
                    'title': 'Systems Programming',
                    'credits': 4,
                    'description': 'System-level programming, processes, memory management, and UNIX environment.',
                    'prerequisites': ['CS 25000', 'CS 25100'],
                    'corequisites': [],
                    'typical_semester': 'sophomore_spring',
                    'offered_semesters': ['fall', 'spring'],
                    'difficulty': 4.3,
                    'workload_hours': 15,
                    'required': True,
                    'course_type': 'foundation'
                },
                'CS 38100': {
                    'title': 'Introduction to Algorithms',
                    'credits': 3,
                    'description': 'Design and analysis of algorithms, complexity theory, and algorithmic problem solving.',
                    'prerequisites': ['CS 25100'],
                    'corequisites': [],
                    'typical_semester': 'junior_fall',
                    'offered_semesters': ['fall', 'spring'],
                    'difficulty': 4.5,
                    'workload_hours': 16,
                    'required': True,
                    'course_type': 'core',
                    'mandatory_timing': 'Fall junior year'
                }
            },
            
            'math_requirements': {
                'MA 16100': {
                    'title': 'Calculus I',
                    'credits': 5,
                    'description': 'Limits, derivatives, and applications of derivatives.',
                    'prerequisites': [],
                    'corequisites': [],
                    'typical_semester': 'freshman_fall',
                    'offered_semesters': ['fall', 'spring', 'summer'],
                    'difficulty': 3.0,
                    'required': True,
                    'course_type': 'math'
                },
                'MA 16200': {
                    'title': 'Calculus II',
                    'credits': 5,
                    'description': 'Integration techniques, infinite series, and applications.',
                    'prerequisites': ['MA 16100'],
                    'corequisites': [],
                    'typical_semester': 'freshman_spring',
                    'offered_semesters': ['fall', 'spring', 'summer'],
                    'difficulty': 3.2,
                    'required': True,
                    'course_type': 'math'
                },
                'MA 26100': {
                    'title': 'Multivariate Calculus',
                    'credits': 4,
                    'description': 'Partial derivatives, multiple integrals, and vector calculus.',
                    'prerequisites': ['MA 16200'],
                    'corequisites': [],
                    'typical_semester': 'sophomore_fall',
                    'offered_semesters': ['fall', 'spring'],
                    'difficulty': 3.4,
                    'required': True,
                    'course_type': 'math'
                },
                'MA 26500': {
                    'title': 'Linear Algebra',
                    'credits': 3,
                    'description': 'Vector spaces, matrices, eigenvalues, and linear transformations.',
                    'prerequisites': ['MA 16200'],
                    'corequisites': ['MA 26100'],
                    'typical_semester': 'sophomore_spring',
                    'offered_semesters': ['fall', 'spring'],
                    'difficulty': 3.6,
                    'required': True,
                    'course_type': 'math'
                },
                'STAT 35000': {
                    'title': 'Elementary Statistics',
                    'credits': 3,
                    'description': 'Basic statistical concepts, probability distributions, and hypothesis testing.',
                    'prerequisites': ['MA 16200'],
                    'corequisites': [],
                    'typical_semester': 'junior_fall',
                    'offered_semesters': ['fall', 'spring', 'summer'],
                    'difficulty': 2.8,
                    'required': True,
                    'course_type': 'math'
                }
            },
            
            'track_courses': {
                'machine_intelligence': {
                    'track_name': 'Machine Intelligence',
                    'track_code': 'MI',
                    'total_courses': 6,
                    'required_courses': 4,
                    'elective_courses': 2,
                    'courses': {
                        'CS 37300': {
                            'title': 'Data Mining and Machine Learning',
                            'credits': 3,
                            'description': 'Machine learning algorithms, data preprocessing, and model evaluation.',
                            'prerequisites': ['CS 25100', 'STAT 35000'],
                            'typical_semester': 'junior_fall',
                            'offered_semesters': ['fall', 'spring'],
                            'difficulty': 4.2,
                            'workload_hours': 14,
                            'required_for_track': True,
                            'course_type': 'track_required'
                        },
                        'CS 47100': {
                            'title': 'Introduction to Artificial Intelligence',
                            'credits': 3,
                            'description': 'Search algorithms, knowledge representation, and AI problem-solving.',
                            'prerequisites': ['CS 25100'],
                            'typical_semester': 'junior_spring',
                            'offered_semesters': ['fall', 'spring'],
                            'difficulty': 4.0,
                            'workload_hours': 13,
                            'required_for_track': False,
                            'course_type': 'track_choice',
                            'choice_group': 'ai_foundation'
                        },
                        'CS 47300': {
                            'title': 'Web Information Search and Management',
                            'credits': 3,
                            'description': 'Information retrieval, web search engines, and text processing.',
                            'prerequisites': ['CS 25100'],
                            'typical_semester': 'junior_spring',
                            'offered_semesters': ['fall', 'spring'],
                            'difficulty': 3.8,
                            'workload_hours': 12,
                            'required_for_track': False,
                            'course_type': 'track_choice',
                            'choice_group': 'ai_foundation'
                        },
                        'STAT 41600': {
                            'title': 'Probability',
                            'credits': 3,
                            'description': 'Mathematical probability theory and applications.',
                            'prerequisites': ['MA 26100'],
                            'typical_semester': 'junior_spring',
                            'offered_semesters': ['fall', 'spring'],
                            'difficulty': 4.1,
                            'workload_hours': 12,
                            'required_for_track': False,
                            'course_type': 'track_choice',
                            'choice_group': 'statistics'
                        },
                        'MA 41600': {
                            'title': 'Probability',
                            'credits': 3,
                            'description': 'Mathematical probability from mathematics department.',
                            'prerequisites': ['MA 26100'],
                            'typical_semester': 'junior_spring',
                            'offered_semesters': ['fall', 'spring'],
                            'difficulty': 4.2,
                            'workload_hours': 12,
                            'required_for_track': False,
                            'course_type': 'track_choice',
                            'choice_group': 'statistics'
                        },
                        'STAT 51200': {
                            'title': 'Applied Regression Analysis',
                            'credits': 3,
                            'description': 'Regression modeling and statistical analysis.',
                            'prerequisites': ['STAT 35000'],
                            'typical_semester': 'senior_fall',
                            'offered_semesters': ['fall', 'spring'],
                            'difficulty': 4.0,
                            'workload_hours': 12,
                            'required_for_track': False,
                            'course_type': 'track_choice',
                            'choice_group': 'statistics'
                        }
                    },
                    'choice_requirements': {
                        'ai_foundation': {
                            'required_count': 1,
                            'description': 'Choose one AI foundation course',
                            'options': ['CS 47100', 'CS 47300']
                        },
                        'statistics': {
                            'required_count': 1,
                            'description': 'Choose one statistics course',
                            'options': ['STAT 41600', 'MA 41600', 'STAT 51200']
                        }
                    },
                    'elective_courses': [
                        'CS 42600', 'CS 54100', 'CS 57300', 'CS 57700'
                    ]
                },
                'software_engineering': {
                    'track_name': 'Software Engineering',
                    'track_code': 'SE',
                    'total_courses': 6,
                    'required_courses': 5,
                    'elective_courses': 1,
                    'courses': {
                        'CS 30700': {
                            'title': 'Software Engineering I',
                            'credits': 3,
                            'description': 'Software development lifecycle, requirements analysis, and design principles.',
                            'prerequisites': ['CS 25200'],
                            'typical_semester': 'junior_spring',
                            'offered_semesters': ['fall', 'spring'],
                            'difficulty': 3.5,
                            'workload_hours': 12,
                            'required_for_track': True,
                            'course_type': 'track_required'
                        },
                        'CS 40700': {
                            'title': 'Software Engineering II',
                            'credits': 3,
                            'description': 'Advanced software engineering topics, project management, and team development.',
                            'prerequisites': ['CS 30700'],
                            'typical_semester': 'senior_fall',
                            'offered_semesters': ['fall', 'spring'],
                            'difficulty': 3.8,
                            'workload_hours': 14,
                            'required_for_track': True,
                            'course_type': 'track_required'
                        },
                        'CS 40800': {
                            'title': 'Software Testing',
                            'credits': 3,
                            'description': 'Testing methodologies, test automation, and quality assurance.',
                            'prerequisites': ['CS 30700'],
                            'typical_semester': 'senior_fall',
                            'offered_semesters': ['fall', 'spring'],
                            'difficulty': 3.2,
                            'workload_hours': 11,
                            'required_for_track': True,
                            'course_type': 'track_required'
                        },
                        'CS 35200': {
                            'title': 'Compilers',
                            'credits': 3,
                            'description': 'Compiler design, parsing techniques, and code generation.',
                            'prerequisites': ['CS 25200'],
                            'typical_semester': 'junior_spring',
                            'offered_semesters': ['fall', 'spring'],
                            'difficulty': 4.3,
                            'workload_hours': 15,
                            'required_for_track': False,
                            'course_type': 'track_choice',
                            'choice_group': 'systems'
                        },
                        'CS 35400': {
                            'title': 'Operating Systems',
                            'credits': 3,
                            'description': 'Operating system concepts, process management, and memory management.',
                            'prerequisites': ['CS 25200'],
                            'typical_semester': 'junior_spring',
                            'offered_semesters': ['fall', 'spring'],
                            'difficulty': 4.1,
                            'workload_hours': 14,
                            'required_for_track': False,
                            'course_type': 'track_choice',
                            'choice_group': 'systems'
                        }
                    },
                    'choice_requirements': {
                        'systems': {
                            'required_count': 1,
                            'description': 'Choose either Compilers or Operating Systems',
                            'options': ['CS 35200', 'CS 35400']
                        }
                    },
                    'elective_courses': [
                        'CS 42600', 'CS 34800', 'CS 42200', 'CS 51400'
                    ]
                }
            }
        }
    
    def build_comprehensive_graph(self):
        """Build comprehensive knowledge graph with all CS program data"""
        self.logger.info("🔧 BUILDING: Comprehensive knowledge graph")
        
        # Build graph using existing knowledge graph system
        kg = PurdueCSKnowledgeGraph()
        
        # Add all foundation courses
        for course_id, course_data in self.cs_program_data['foundation_courses'].items():
            kg.add_course(course_id, course_data)
            
            # Add prerequisite relationships
            for prereq in course_data.get('prerequisites', []):
                kg.add_prerequisite(course_id, prereq)
        
        # Add all math requirements
        for course_id, course_data in self.cs_program_data['math_requirements'].items():
            kg.add_course(course_id, course_data)
            
            # Add prerequisite relationships
            for prereq in course_data.get('prerequisites', []):
                kg.add_prerequisite(course_id, prereq)
        
        # Add track courses
        for track_name, track_data in self.cs_program_data['track_courses'].items():
            for course_id, course_data in track_data['courses'].items():
                kg.add_course(course_id, course_data)
                
                # Add prerequisite relationships
                for prereq in course_data.get('prerequisites', []):
                    kg.add_prerequisite(course_id, prereq)
        
        # Save the comprehensive graph
        kg.save_graph('comprehensive_knowledge_graph.json')
        
        self.logger.info(f"✅ BUILT: Comprehensive knowledge graph with {kg.graph.number_of_nodes()} nodes and {kg.graph.number_of_edges()} edges")
        
        return kg
    
    def populate_database_from_graph(self, kg):
        """Populate database with graph data for enhanced querying"""
        self.logger.info("🔧 POPULATING: Database from knowledge graph")
        
        try:
            conn = sqlite3.connect('purdue_cs_knowledge.db')
            cursor = conn.cursor()
            
            # Create courses table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS comprehensive_courses (
                    course_id TEXT PRIMARY KEY,
                    title TEXT,
                    credits INTEGER,
                    description TEXT,
                    typical_semester TEXT,
                    offered_semesters TEXT,
                    difficulty REAL,
                    workload_hours INTEGER,
                    required BOOLEAN,
                    course_type TEXT,
                    prerequisites TEXT,
                    corequisites TEXT
                )
            ''')
            
            # Insert course data
            for course_id in kg.graph.nodes():
                course_data = kg.graph.nodes[course_id]
                
                cursor.execute('''
                    INSERT OR REPLACE INTO comprehensive_courses VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                ''', (
                    course_id,
                    course_data.get('title', ''),
                    course_data.get('credits', 3),
                    course_data.get('description', ''),
                    course_data.get('typical_semester', ''),
                    json.dumps(course_data.get('offered_semesters', [])),
                    course_data.get('difficulty', 3.0),
                    course_data.get('workload_hours', 10),
                    course_data.get('required', True),
                    course_data.get('course_type', ''),
                    json.dumps(list(kg.graph.predecessors(course_id))),
                    json.dumps(course_data.get('corequisites', []))
                ))
            
            conn.commit()
            conn.close()
            
            self.logger.info("✅ POPULATED: Database with comprehensive course data")
            
        except Exception as e:
            self.logger.error(f"❌ DATABASE ERROR: {e}")

def populate_cs_knowledge_graph():
    """Main function to populate comprehensive knowledge graph"""
    
    builder = PurdueCSKnowledgeGraphBuilder()
    
    # Build comprehensive knowledge graph
    kg = builder.build_comprehensive_graph()
    
    # Populate database
    builder.populate_database_from_graph(kg)
    
    return kg

# Legacy function maintained for compatibility
def populate_legacy_format():
    """Legacy format for basic courses"""
    
    kg = PurdueCSKnowledgeGraph()
    
    # Define basic CS courses with metadata
    courses = {
        'CS 18000': {
            'title': 'Problem Solving And Object-Oriented Programming',
            'credits': 4,
            'typical_semester': 'freshman_fall',
            'difficulty': 3.5,
            'required': True,
            'offered_semesters': ['fall', 'spring']
        },
        'CS 18200': {
            'title': 'Foundations of Computer Science',
            'credits': 3,
            'typical_semester': 'freshman_spring',
            'difficulty': 4.0,
            'required': True,
            'offered_semesters': ['fall', 'spring']
        },
        'CS 24000': {
            'title': 'Programming in C',
            'credits': 3,
            'typical_semester': 'freshman_spring',
            'difficulty': 3.0,
            'required': True,
            'offered_semesters': ['fall', 'spring']
        },
        'CS 25000': {
            'title': 'Computer Architecture',
            'credits': 4,
            'typical_semester': 'sophomore_fall',
            'difficulty': 4.0,
            'required': True,
            'offered_semesters': ['fall', 'spring']
        },
        'CS 25100': {
            'title': 'Data Structures and Algorithms',
            'credits': 3,
            'typical_semester': 'sophomore_fall',
            'difficulty': 4.5,
            'required': True,
            'offered_semesters': ['fall', 'spring']
        },
        'CS 25200': {
            'title': 'Systems Programming',
            'credits': 4,
            'typical_semester': 'sophomore_spring',
            'difficulty': 4.0,
            'required': True,
            'offered_semesters': ['fall', 'spring']
        },
        'CS 38100': {
            'title': 'Introduction to Algorithms',
            'credits': 3,
            'typical_semester': 'junior_fall',
            'difficulty': 4.5,
            'required': True,
            'offered_semesters': ['fall', 'spring']
        },
        'CS 37300': {
            'title': 'Data Mining and Machine Learning',
            'credits': 3,
            'typical_semester': 'junior_spring',
            'difficulty': 4.0,
            'required': False,
            'offered_semesters': ['fall', 'spring']
        },
        'CS 30700': {
            'title': 'Software Engineering I',
            'credits': 3,
            'typical_semester': 'junior_spring',
            'difficulty': 3.5,
            'required': False,
            'offered_semesters': ['fall', 'spring']
        },
        'CS 40800': {
            'title': 'Software Testing',
            'credits': 3,
            'typical_semester': 'senior_fall',
            'difficulty': 3.0,
            'required': False,
            'offered_semesters': ['fall', 'spring']
        },
        'CS 47100': {
            'title': 'Introduction to Artificial Intelligence',
            'credits': 3,
            'typical_semester': 'junior_spring',
            'difficulty': 4.0,
            'required': False,
            'offered_semesters': ['fall', 'spring']
        },
        'CS 47300': {
            'title': 'Web Information Search and Management',
            'credits': 3,
            'typical_semester': 'junior_spring',
            'difficulty': 3.5,
            'required': False,
            'offered_semesters': ['fall', 'spring']
        },
        'MA 16100': {
            'title': 'Plane Analytic Geometry And Calculus I',
            'credits': 5,
            'typical_semester': 'freshman_fall',
            'difficulty': 3.5,
            'required': True,
            'offered_semesters': ['fall', 'spring', 'summer']
        },
        'MA 16200': {
            'title': 'Plane Analytic Geometry And Calculus II',
            'credits': 5,
            'typical_semester': 'freshman_spring',
            'difficulty': 4.0,
            'required': True,
            'offered_semesters': ['fall', 'spring', 'summer']
        },
        'MA 26100': {
            'title': 'Multivariate Calculus',
            'credits': 4,
            'typical_semester': 'sophomore_fall',
            'difficulty': 4.0,
            'required': True,
            'offered_semesters': ['fall', 'spring']
        },
        'STAT 35000': {
            'title': 'Introduction to Statistics',
            'credits': 3,
            'typical_semester': 'junior_fall',
            'difficulty': 3.0,
            'required': True,
            'offered_semesters': ['fall', 'spring']
        }
    }
    
    # Define prerequisite relationships
    prerequisites = {
        'CS 18200': ['CS 18000'],
        'CS 24000': ['CS 18000'],
        'CS 25000': ['CS 18200', 'CS 24000'],
        'CS 25100': ['CS 18200', 'CS 24000'],
        'CS 25200': ['CS 25000', 'CS 25100'],
        'CS 38100': ['CS 25100'],
        'CS 37300': ['CS 25100', 'STAT 35000'],
        'CS 30700': ['CS 25200'],
        'CS 40800': ['CS 30700'],
        'CS 47100': ['CS 25100'],
        'CS 47300': ['CS 25100'],
        'MA 16200': ['MA 16100'],
        'MA 26100': ['MA 16200'],
        'STAT 35000': ['MA 16200']
    }
    
    # Add courses to knowledge graph
    print("📚 Adding courses to knowledge graph...")
    for course_id, course_data in courses.items():
        kg.add_course(course_id, course_data)
    
    # Add prerequisite relationships
    print("🔗 Adding prerequisite relationships...")
    for course_id, prereqs in prerequisites.items():
        for prereq in prereqs:
            kg.add_prerequisite(course_id, prereq)
    
    # Save the knowledge graph
    kg.save_graph('knowledge_graph.json')
    
    print(f"✅ Knowledge graph populated with {len(courses)} courses and {sum(len(prereqs) for prereqs in prerequisites.values())} prerequisite relationships")
    
    return kg

if __name__ == "__main__":
    kg = populate_cs_knowledge_graph()
    
    # Test the graph
    print("\n🔍 Testing knowledge graph...")
    print(f"Nodes: {kg.graph.number_of_nodes()}")
    print(f"Edges: {kg.graph.number_of_edges()}")
    
    # Test prerequisite lookup
    cs180_successors = list(kg.graph.successors('CS 18000'))
    print(f"CS 18000 unlocks: {cs180_successors}")