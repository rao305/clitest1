import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify
import networkx as nx
import sqlite3
import os

@dataclass
class Course:
    code: str
    title: str
    credits: int
    track: str
    requirement_type: str  # 'mandatory', 'choice', 'elective'
    group_id: Optional[str] = None
    prerequisites: List[str] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []

@dataclass
class Track:
    name: str
    code: str
    required_courses: int
    elective_courses: int
    mandatory_courses: List[str]
    choice_groups: Dict[str, Dict]
    elective_options: List[str]
    special_rules: Dict[str, str]
    last_updated: str

@dataclass
class TrainingData:
    id: str
    query: str
    response: str
    track: str
    confidence: float
    source_data: Dict
    created_at: str

class KnowledgeGraph:
    def __init__(self, db_path: str = "purdue_cs_knowledge.db"):
        self.db_path = db_path
        self.graph = nx.DiGraph()
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else '.', exist_ok=True)
        self.init_database()
        self.load_graph()
        
    def init_database(self):
        """Initialize SQLite database for persistent storage"""
        conn = sqlite3.connect(self.db_path, timeout=60)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=60000")
        cursor = conn.cursor()
        
        # Courses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                code TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                credits INTEGER,
                track TEXT,
                requirement_type TEXT,
                group_id TEXT,
                prerequisites TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tracks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracks (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                required_courses INTEGER,
                elective_courses INTEGER,
                mandatory_courses TEXT,
                choice_groups TEXT,
                elective_options TEXT,
                special_rules TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Training data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_data (
                id TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                track TEXT,
                confidence REAL,
                source_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Knowledge graph edges
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_edges (
                id TEXT PRIMARY KEY,
                source_node TEXT,
                target_node TEXT,
                relationship TEXT,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_graph(self):
        """Load existing data from database into graph"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=60)
            cursor = conn.cursor()
            
            # Load courses
            cursor.execute("SELECT * FROM courses")
            for row in cursor.fetchall():
                course_data = {
                    'code': row[0],
                    'title': row[1],
                    'credits': row[2],
                    'track': row[3],
                    'requirement_type': row[4],
                    'group_id': row[5],
                    'prerequisites': json.loads(row[6]) if row[6] else [],
                    'description': row[7]
                }
                self.graph.add_node(row[0], **course_data)
            
            # Load knowledge edges
            cursor.execute("SELECT source_node, target_node, relationship FROM knowledge_edges")
            for row in cursor.fetchall():
                self.graph.add_edge(row[0], row[1], relationship=row[2])
            
            conn.close()
            print(f"✅ Loaded {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges from database")
            
        except Exception as e:
            print(f"Note: Could not load existing graph data: {e}")
            # This is expected on first run
    
    def add_course(self, course: Course) -> bool:
        """Add course to knowledge graph and database"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=60)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO courses 
                (code, title, credits, track, requirement_type, group_id, prerequisites, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                course.code, course.title, course.credits, course.track,
                course.requirement_type, course.group_id, 
                json.dumps(course.prerequisites), course.description
            ))
            
            # Add to graph
            self.graph.add_node(course.code, **asdict(course))
            
            # Add prerequisite edges
            for prereq in course.prerequisites:
                self.graph.add_edge(prereq, course.code, relationship="prerequisite")
                self._add_knowledge_edge_safe(conn, prereq, course.code, "prerequisite", {})
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding course {course.code}: {e}")
            return False
    
    def add_track(self, track: Track) -> bool:
        """Add track to knowledge graph and database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO tracks 
                (code, name, required_courses, elective_courses, mandatory_courses, 
                 choice_groups, elective_options, special_rules)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                track.code, track.name, track.required_courses, track.elective_courses,
                json.dumps(track.mandatory_courses), json.dumps(track.choice_groups),
                json.dumps(track.elective_options), json.dumps(track.special_rules)
            ))
            
            # Add to graph
            self.graph.add_node(f"track_{track.code}", **asdict(track))
            
            # Connect track to courses
            for course_code in track.mandatory_courses:
                self.graph.add_edge(f"track_{track.code}", course_code, relationship="requires")
                self._add_knowledge_edge(f"track_{track.code}", course_code, "requires", {"type": "mandatory"})
            
            for course_code in track.elective_options:
                self.graph.add_edge(f"track_{track.code}", course_code, relationship="allows")
                self._add_knowledge_edge(f"track_{track.code}", course_code, "allows", {"type": "elective"})
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding track {track.code}: {e}")
            return False
    
    def _add_knowledge_edge_safe(self, conn, source: str, target: str, relationship: str, properties: Dict):
        """Add edge to knowledge graph database using existing connection"""
        cursor = conn.cursor()
        
        edge_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT OR IGNORE INTO knowledge_edges (id, source_node, target_node, relationship, properties)
            VALUES (?, ?, ?, ?, ?)
        ''', (edge_id, source, target, relationship, json.dumps(properties)))
    
    def _add_knowledge_edge(self, source: str, target: str, relationship: str, properties: Dict):
        """Add edge to knowledge graph database"""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        
        edge_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT OR IGNORE INTO knowledge_edges (id, source_node, target_node, relationship, properties)
            VALUES (?, ?, ?, ?, ?)
        ''', (edge_id, source, target, relationship, json.dumps(properties)))
        
        conn.commit()
        conn.close()
    
    def query_courses_by_track(self, track_code: str) -> Dict[str, List[Course]]:
        """Query all courses for a specific track"""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT code, title, credits, track, requirement_type, group_id, prerequisites, description
            FROM courses WHERE track = ?
        ''', (track_code,))
        
        rows = cursor.fetchall()
        conn.close()
        
        courses = {
            "mandatory": [],
            "choice": [],
            "elective": []
        }
        
        for row in rows:
            prereqs = json.loads(row[6]) if row[6] else []
            course = Course(
                code=row[0], title=row[1], credits=row[2], track=row[3],
                requirement_type=row[4], group_id=row[5], 
                prerequisites=prereqs, description=row[7]
            )
            courses[course.requirement_type].append(course)
        
        return courses
    
    def get_track_info(self, track_code: str) -> Optional[Track]:
        """Get complete track information"""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT code, name, required_courses, elective_courses, mandatory_courses,
                   choice_groups, elective_options, special_rules, last_updated
            FROM tracks WHERE code = ?
        ''', (track_code,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return Track(
            code=row[0], name=row[1], required_courses=row[2], elective_courses=row[3],
            mandatory_courses=json.loads(row[4]), choice_groups=json.loads(row[5]),
            elective_options=json.loads(row[6]), special_rules=json.loads(row[7]),
            last_updated=row[8]
        )
    
    def find_course_relationships(self, course_code: str) -> Dict[str, List[str]]:
        """Find all relationships for a course"""
        relationships = {
            "prerequisites": [],
            "dependent_courses": [],
            "tracks_requiring": [],
            "tracks_allowing": []
        }
        
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        
        # Find prerequisites
        cursor.execute('''
            SELECT source_node FROM knowledge_edges 
            WHERE target_node = ? AND relationship = "prerequisite"
        ''', (course_code,))
        relationships["prerequisites"] = [row[0] for row in cursor.fetchall()]
        
        # Find dependent courses
        cursor.execute('''
            SELECT target_node FROM knowledge_edges 
            WHERE source_node = ? AND relationship = "prerequisite"
        ''', (course_code,))
        relationships["dependent_courses"] = [row[0] for row in cursor.fetchall()]
        
        # Find tracks requiring this course
        cursor.execute('''
            SELECT source_node FROM knowledge_edges 
            WHERE target_node = ? AND relationship = "requires"
        ''', (course_code,))
        relationships["tracks_requiring"] = [row[0] for row in cursor.fetchall()]
        
        # Find tracks allowing this course as elective
        cursor.execute('''
            SELECT source_node FROM knowledge_edges 
            WHERE target_node = ? AND relationship = "allows"
        ''', (course_code,))
        relationships["tracks_allowing"] = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return relationships

class PurdueDataLoader:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph
        
    def load_machine_intelligence_track(self):
        """Load MI track data from scrapers into knowledge graph"""
        try:
            from mi_track_scraper import PurdueMITrackScraper
            
            scraper = PurdueMITrackScraper()
            data = scraper.scrape_courses()
            
            if not data:
                return False
            
            # Create MI track
            mi_track = Track(
                name="Machine Intelligence Track",
                code="MI",
                required_courses=4,
                elective_courses=2,
                mandatory_courses=["CS 37300", "CS 38100"],
                choice_groups={
                    "ai_requirement": {
                        "options": ["CS 47100", "CS 47300"],
                        "choose": 1,
                        "description": "AI Requirement"
                    },
                    "stats_requirement": {
                        "options": ["STAT 41600", "MA 41600", "STAT 51200"],
                        "choose": 1,
                        "description": "Statistics/Probability Requirement"
                    }
                },
                elective_options=[
                    "CS 31100", "CS 41100", "CS 31400", "CS 34800", "CS 35200",
                    "CS 44800", "CS 45600", "CS 45800", "CS 47100", "CS 47300",
                    "CS 48300", "CS 43900", "CS 44000", "CS 47500", "CS 57700", "CS 57800"
                ],
                special_rules={
                    "competitive_programming": "CS 31100 + CS 41100 together may count as 1 elective",
                    "data_group": "From CS 43900/CS 44000/CS 47500, can only pick ONE",
                    "no_double_counting": "Cannot use same course for required AND elective"
                },
                last_updated=datetime.now().isoformat()
            )
            
            self.kg.add_track(mi_track)
            
            # Add courses
            courses_to_add = [
                Course("CS 37300", "Data Mining and Machine Learning", 3, "MI", "mandatory"),
                Course("CS 38100", "Introduction to the Analysis of Algorithms", 3, "MI", "mandatory"),
                Course("CS 47100", "Artificial Intelligence", 3, "MI", "choice", "ai_requirement"),
                Course("CS 47300", "Web Information Search & Management", 3, "MI", "choice", "ai_requirement"),
                Course("STAT 41600", "Probability", 3, "MI", "choice", "stats_requirement"),
                Course("MA 41600", "Probability", 3, "MI", "choice", "stats_requirement"),
                Course("STAT 51200", "Applied Regression Analysis", 3, "MI", "choice", "stats_requirement"),
                Course("CS 31100", "Competitive Programming I", 3, "MI", "elective"),
                Course("CS 41100", "Competitive Programming II", 3, "MI", "elective"),
                Course("CS 31400", "Numerical Methods", 3, "MI", "elective"),
                Course("CS 34800", "Information Systems", 3, "MI", "elective"),
                Course("CS 35200", "Compilers: Principles And Practice", 3, "MI", "elective"),
                Course("CS 44800", "Introduction To Relational Database Systems", 3, "MI", "elective"),
                Course("CS 45600", "Programming Languages", 3, "MI", "elective"),
                Course("CS 45800", "Introduction to Robotics", 3, "MI", "elective"),
                Course("CS 48300", "Introduction To The Theory Of Computation", 3, "MI", "elective"),
                Course("CS 43900", "Introduction to Data Visualization", 3, "MI", "elective"),
                Course("CS 44000", "Large-Scale Data Analytics", 3, "MI", "elective"),
                Course("CS 47500", "Information Visualization", 3, "MI", "elective"),
                Course("CS 57700", "Natural Language Processing", 3, "MI", "elective"),
                Course("CS 57800", "Statistical Machine Learning", 3, "MI", "elective")
            ]
            
            for course in courses_to_add:
                self.kg.add_course(course)
            
            return True
            
        except Exception as e:
            print(f"Error loading MI track: {e}")
            return False
    
    def load_software_engineering_track(self):
        """Load SE track data from scrapers into knowledge graph"""
        try:
            from se_track_scraper import PurdueSETrackScraper
            
            scraper = PurdueSETrackScraper()
            data = scraper.scrape_courses()
            
            if not data:
                return False
            
            # Create SE track
            se_track = Track(
                name="Software Engineering Track",
                code="SE",
                required_courses=5,
                elective_courses=1,
                mandatory_courses=["CS 30700", "CS 38100", "CS 40800", "CS 40700"],
                choice_groups={
                    "compilers_os_requirement": {
                        "options": ["CS 35200", "CS 35400"],
                        "choose": 1,
                        "description": "Compilers/Operating Systems Requirement"
                    }
                },
                elective_options=[
                    "CS 31100", "CS 41100", "CS 34800", "CS 35100", "CS 35200",
                    "CS 35300", "CS 35400", "CS 37300", "CS 42200", "CS 42600", 
                    "CS 44800", "CS 45600", "CS 47100", "CS 47300", "CS 48900", 
                    "CS 49000-DSO", "CS 49000-SWS", "CS 51000", "CS 59000-SRS"
                ],
                special_rules={
                    "competitive_programming": "CS 31100 + CS 41100 together satisfy one elective",
                    "senior_project_substitute": "EPICS/VIP can replace CS 40700 with track chair approval",
                    "epics_requirement": "EPICS must be EPCS 41100+41200 (Senior Design)",
                    "no_double_counting": "Cannot use same course for required AND elective"
                },
                last_updated=datetime.now().isoformat()
            )
            
            self.kg.add_track(se_track)
            
            # Add courses
            courses_to_add = [
                Course("CS 30700", "Software Engineering I", 3, "SE", "mandatory"),
                Course("CS 38100", "Introduction to the Analysis of Algorithms", 3, "SE", "mandatory"),
                Course("CS 40800", "Software Testing", 3, "SE", "mandatory"),
                Course("CS 40700", "Software Engineering Senior Project", 3, "SE", "mandatory"),
                Course("CS 35200", "Compilers: Principles and Practice", 3, "SE", "choice", "compilers_os_requirement"),
                Course("CS 35400", "Operating Systems", 3, "SE", "choice", "compilers_os_requirement"),
                Course("CS 31100", "Competitive Programming 2 and 3", 3, "SE", "elective"),
                Course("CS 41100", "Competitive Programming continuation", 3, "SE", "elective"),
                Course("CS 34800", "Information Systems", 3, "SE", "elective"),
                Course("CS 35100", "Cloud Computing", 3, "SE", "elective"),
                Course("CS 35300", "Principles of Concurrency and Parallelism", 3, "SE", "elective"),
                Course("CS 37300", "Data Mining and Machine Learning", 3, "SE", "elective"),
                Course("CS 42200", "Computer Networks", 3, "SE", "elective"),
                Course("CS 42600", "Computer Security", 3, "SE", "elective"),
                Course("CS 44800", "Introduction to Relational Database Systems", 3, "SE", "elective"),
                Course("CS 45600", "Programming Languages", 3, "SE", "elective"),
                Course("CS 47100", "Introduction to Artificial Intelligence", 3, "SE", "elective"),
                Course("CS 47300", "Web Information Search And Management", 3, "SE", "elective"),
                Course("CS 48900", "Embedded Systems", 3, "SE", "elective"),
                Course("CS 49000-DSO", "Distributed Systems", 3, "SE", "elective"),
                Course("CS 49000-SWS", "Software Security", 3, "SE", "elective"),
                Course("CS 51000", "Software Engineering", 3, "SE", "elective"),
                Course("CS 59000-SRS", "Software Reliability and Security", 3, "SE", "elective")
            ]
            
            for course in courses_to_add:
                self.kg.add_course(course)
            
            return True
            
        except Exception as e:
            print(f"Error loading SE track: {e}")
            return False

class DynamicResponseGenerator:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph
        
    def generate_response(self, query: str, track_context: Optional[str] = None) -> Dict:
        """Generate response based on knowledge graph data"""
        try:
            query_lower = query.lower()
            
            # Determine track context if not provided
            if not track_context:
                track_context = self._determine_track_context(query_lower)
            
            # Generate response based on query type
            if "required" in query_lower and "course" in query_lower:
                return self._generate_required_courses_response(track_context)
            elif "elective" in query_lower:
                return self._generate_elective_response(track_context)
            elif "difference" in query_lower:
                return self._generate_track_comparison_response()
            elif "validate" in query_lower or "check" in query_lower:
                return self._generate_validation_response(query, track_context)
            else:
                return self._generate_general_response(query, track_context)
                
        except Exception as e:
            return {
                "query": query,
                "response": f"Error generating response: {str(e)}",
                "confidence": 0.1,
                "track": track_context,
                "source": "error",
                "timestamp": datetime.now().isoformat()
            }
    
    def _determine_track_context(self, query_lower: str) -> str:
        """Determine track context from query"""
        mi_keywords = ['machine intelligence', 'mi track', 'cs 37300', 'data mining', 'machine learning']
        se_keywords = ['software engineering', 'se track', 'cs 30700', 'cs 40800', 'software testing']
        
        if any(keyword in query_lower for keyword in mi_keywords):
            return "MI"
        elif any(keyword in query_lower for keyword in se_keywords):
            return "SE"
        else:
            return None
    
    def _generate_required_courses_response(self, track_context: str) -> Dict:
        """Generate response for required courses query"""
        if not track_context:
            return {
                "query": "required courses",
                "response": "Please specify which track (MI or SE) you're asking about.",
                "confidence": 0.5,
                "track": None,
                "source": "knowledge_graph",
                "timestamp": datetime.now().isoformat()
            }
        
        track_info = self.kg.get_track_info(track_context)
        if not track_info:
            return {
                "query": "required courses",
                "response": f"Track information not found for {track_context}",
                "confidence": 0.3,
                "track": track_context,
                "source": "knowledge_graph",
                "timestamp": datetime.now().isoformat()
            }
        
        courses = self.kg.query_courses_by_track(track_context)
        
        response = f"The {track_info.name} has {track_info.required_courses} required courses:\n\n"
        
        # Add mandatory courses
        for course in courses["mandatory"]:
            response += f"• {course.code}: {course.title} (required)\n"
        
        # Add choice requirements
        for group_name, group_info in track_info.choice_groups.items():
            response += f"• Choose {group_info['choose']} from: {', '.join(group_info['options'])}\n"
        
        return {
            "query": "required courses",
            "response": response,
            "confidence": 0.95,
            "track": track_context,
            "source": "knowledge_graph",
            "source_data": {
                "track_info": asdict(track_info),
                "courses": {k: [asdict(c) for c in v] for k, v in courses.items()}
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_elective_response(self, track_context: str) -> Dict:
        """Generate response for elective courses query"""
        if not track_context:
            return {
                "query": "elective courses",
                "response": "Please specify which track (MI or SE) you're asking about.",
                "confidence": 0.5,
                "track": None,
                "source": "knowledge_graph",
                "timestamp": datetime.now().isoformat()
            }
        
        track_info = self.kg.get_track_info(track_context)
        if not track_info:
            return {
                "query": "elective courses",
                "response": f"Track information not found for {track_context}",
                "confidence": 0.3,
                "track": track_context,
                "source": "knowledge_graph",
                "timestamp": datetime.now().isoformat()
            }
        
        response = f"The {track_info.name} requires {track_info.elective_courses} elective course(s) from the approved list:\n\n"
        
        courses = self.kg.query_courses_by_track(track_context)
        for course in courses["elective"]:
            response += f"• {course.code}: {course.title}\n"
        
        # Add special rules
        if track_info.special_rules:
            response += "\nSpecial Rules:\n"
            for rule, description in track_info.special_rules.items():
                response += f"• {description}\n"
        
        return {
            "query": "elective courses",
            "response": response,
            "confidence": 0.95,
            "track": track_context,
            "source": "knowledge_graph",
            "source_data": {
                "track_info": asdict(track_info),
                "courses": {k: [asdict(c) for c in v] for k, v in courses.items()}
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_track_comparison_response(self) -> Dict:
        """Generate response for track comparison"""
        mi_info = self.kg.get_track_info("MI")
        se_info = self.kg.get_track_info("SE")
        
        if not mi_info or not se_info:
            return {
                "query": "track comparison",
                "response": "Unable to compare tracks - missing track information",
                "confidence": 0.3,
                "track": "comparison",
                "source": "knowledge_graph",
                "timestamp": datetime.now().isoformat()
            }
        
        response = f"Track Comparison:\n\n"
        response += f"Machine Intelligence Track:\n"
        response += f"• Structure: {mi_info.required_courses} required + {mi_info.elective_courses} electives\n"
        response += f"• Focus: AI, Machine Learning, Data Mining\n"
        response += f"• Mandatory: {', '.join(mi_info.mandatory_courses)}\n\n"
        
        response += f"Software Engineering Track:\n"
        response += f"• Structure: {se_info.required_courses} required + {se_info.elective_courses} electives\n"
        response += f"• Focus: Software Development, Testing, Project Management\n"
        response += f"• Mandatory: {', '.join(se_info.mandatory_courses)}\n\n"
        
        response += f"Common Requirements: Both tracks require CS 38100"
        
        return {
            "query": "track comparison",
            "response": response,
            "confidence": 0.95,
            "track": "comparison",
            "source": "knowledge_graph",
            "source_data": {
                "mi_track": asdict(mi_info),
                "se_track": asdict(se_info)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_validation_response(self, query: str, track_context: str) -> Dict:
        """Generate course validation response"""
        # This would integrate with the existing validators
        return {
            "query": query,
            "response": "Course validation requires specific course codes. Please provide a list of courses to validate.",
            "confidence": 0.6,
            "track": track_context,
            "source": "knowledge_graph",
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_general_response(self, query: str, track_context: str) -> Dict:
        """Generate general response"""
        return {
            "query": query,
            "response": "I can help you with Purdue CS track requirements. Ask about required courses, electives, or track comparisons.",
            "confidence": 0.7,
            "track": track_context,
            "source": "knowledge_graph",
            "timestamp": datetime.now().isoformat()
        }

class N8NIntegration:
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
        
    def send_webhook(self, data: Dict) -> bool:
        """Send data to n8n webhook"""
        if not self.webhook_url:
            return False
        
        try:
            response = requests.post(
                self.webhook_url,
                json=data,
                timeout=30
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending webhook: {e}")
            return False
    
    def trigger_data_refresh(self) -> bool:
        """Trigger data refresh in n8n"""
        return self.send_webhook({"action": "refresh_data"})
    
    def trigger_ai_training(self) -> bool:
        """Trigger AI training in n8n"""
        return self.send_webhook({"action": "train_ai"})

def initialize_system():
    """Initialize the complete knowledge graph system"""
    kg = KnowledgeGraph()
    rg = DynamicResponseGenerator(kg)
    n8n = N8NIntegration()
    
    return kg, rg, n8n