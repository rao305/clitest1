#!/usr/bin/env python3
"""
Enhanced Database Schema Implementation
Adds missing tables for professors, feedback, sessions, and policies
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

class EnhancedDatabase:
    def __init__(self, db_path="purdue_cs_knowledge.db"):
        self.db_path = db_path
        self.create_enhanced_schema()
    
    def create_enhanced_schema(self):
        """Create enhanced database schema with new tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Professors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS professors (
                professor_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                office_location TEXT,
                office_hours TEXT,
                research_areas TEXT, -- JSON array
                courses_taught TEXT, -- JSON array of course codes
                ratemyprofessor_rating REAL DEFAULT 0.0,
                ratemyprofessor_difficulty REAL DEFAULT 0.0,
                department TEXT DEFAULT 'Computer Science',
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Academic policies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS policies (
                policy_id TEXT PRIMARY KEY,
                category TEXT, -- add_drop, transfer_credit, exemption, graduation
                title TEXT NOT NULL,
                description TEXT,
                applicable_courses TEXT, -- JSON array
                effective_date DATE,
                source_url TEXT,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Student resources table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resources (
                resource_id TEXT PRIMARY KEY,
                type TEXT, -- club, career_fair, tutoring, advising
                name TEXT NOT NULL,
                description TEXT,
                contact_info TEXT,
                meeting_times TEXT,
                location TEXT,
                website_url TEXT,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User profiles for personalization
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_profiles (
                student_id TEXT PRIMARY KEY,
                year TEXT, -- freshman, sophomore, junior, senior
                major TEXT DEFAULT 'Computer Science',
                track TEXT, -- MI, SE, Graphics, etc.
                gpa REAL,
                completed_courses TEXT, -- JSON array
                current_courses TEXT, -- JSON array
                interests TEXT, -- JSON array
                career_goals TEXT,
                preferred_difficulty TEXT, -- easy, moderate, challenging
                max_credits_per_semester INTEGER DEFAULT 15,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Feedback and learning system
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_feedback (
                feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                student_id TEXT,
                query TEXT,
                response TEXT,
                rating INTEGER, -- 1-5 scale
                feedback_text TEXT,
                intent_classification TEXT,
                response_time_ms INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Session context for multi-turn conversations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_context (
                session_id TEXT PRIMARY KEY,
                student_id TEXT,
                current_topic TEXT,
                conversation_history TEXT, -- JSON array
                extracted_context TEXT, -- JSON object
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Course relationships and dependencies
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS course_relationships (
                relationship_id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_course TEXT,
                to_course TEXT,
                relationship_type TEXT, -- prerequisite, corequisite, recommended
                strength REAL DEFAULT 1.0, -- relationship strength
                FOREIGN KEY (from_course) REFERENCES courses(code),
                FOREIGN KEY (to_course) REFERENCES courses(code)
            )
        ''')
        
        # Course sections and scheduling
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS course_sections (
                section_id TEXT PRIMARY KEY,
                course_code TEXT,
                semester TEXT,
                year INTEGER,
                instructor TEXT,
                meeting_times TEXT, -- JSON array
                location TEXT,
                capacity INTEGER,
                enrolled INTEGER,
                waitlist_size INTEGER,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_code) REFERENCES courses(code),
                FOREIGN KEY (instructor) REFERENCES professors(professor_id)
            )
        ''')
        
        # Update existing courses table with new columns (check if they exist first)
        try:
            cursor.execute('ALTER TABLE courses ADD COLUMN difficulty_rating REAL DEFAULT 0.0')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute('ALTER TABLE courses ADD COLUMN workload_hours INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute('ALTER TABLE courses ADD COLUMN grade_distribution TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute('ALTER TABLE courses ADD COLUMN semester_offered TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute('ALTER TABLE courses ADD COLUMN corequisites TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_professors_name ON professors(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_policies_category ON policies(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_resources_type ON resources(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_student_profiles_year ON student_profiles(year)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_feedback_session ON user_feedback(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_context_student ON session_context(student_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_course_relationships_from ON course_relationships(from_course)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_course_relationships_to ON course_relationships(to_course)')
        
        conn.commit()
        conn.close()
        
        print("✅ Enhanced database schema created successfully")
    
    def insert_default_data(self):
        """Insert default policies and resources"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Default policies
        policies = [
            {
                'policy_id': 'course_exemption_cs18000',
                'category': 'exemption',
                'title': 'CS 18000 Course Exemption',
                'description': 'Students can test out of CS 18000 with prior programming experience by taking a placement exam.',
                'applicable_courses': json.dumps(['CS 18000']),
                'effective_date': '2023-01-01',
                'source_url': 'https://www.cs.purdue.edu/undergraduate/curriculum/bachelor.html'
            },
            {
                'policy_id': 'transfer_credit_ap',
                'category': 'transfer_credit',
                'title': 'AP Credit for CS Courses',
                'description': 'AP Computer Science A exam score of 4 or 5 may receive credit for CS 18000.',
                'applicable_courses': json.dumps(['CS 18000']),
                'effective_date': '2023-01-01',
                'source_url': 'https://www.cs.purdue.edu/undergraduate/policies.html'
            },
            {
                'policy_id': 'graduation_requirements',
                'category': 'graduation',
                'title': 'CS Degree Requirements',
                'description': 'Students must complete foundation courses, track requirements, and electives totaling 126 credit hours.',
                'applicable_courses': json.dumps(['ALL']),
                'effective_date': '2023-01-01',
                'source_url': 'https://catalog.purdue.edu/'
            }
        ]
        
        for policy in policies:
            cursor.execute('''
                INSERT OR REPLACE INTO policies 
                (policy_id, category, title, description, applicable_courses, effective_date, source_url, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                policy['policy_id'], policy['category'], policy['title'], 
                policy['description'], policy['applicable_courses'], 
                policy['effective_date'], policy['source_url'], 
                datetime.now().isoformat()
            ))
        
        # Default resources
        resources = [
            {
                'resource_id': 'cs_help_room',
                'type': 'tutoring',
                'name': 'CS Help Room',
                'description': 'Free tutoring for CS courses with TAs and peer mentors',
                'contact_info': 'cs-helproom@purdue.edu',
                'meeting_times': 'Mon-Fri 10am-6pm',
                'location': 'LWSN B146',
                'website_url': 'https://www.cs.purdue.edu/academic-programs/help-room.html'
            },
            {
                'resource_id': 'acm_chapter',
                'type': 'club',
                'name': 'ACM Purdue Chapter',
                'description': 'Association for Computing Machinery student organization',
                'contact_info': 'acm@purdue.edu',
                'meeting_times': 'Weekly meetings announced on website',
                'location': 'Various locations',
                'website_url': 'https://acm.cs.purdue.edu/'
            },
            {
                'resource_id': 'career_fair_fall',
                'type': 'career_fair',
                'name': 'Fall Career Fair',
                'description': 'Annual career fair with tech companies recruiting CS students',
                'contact_info': 'careers@purdue.edu',
                'meeting_times': 'September (dates vary)',
                'location': 'Co-Rec',
                'website_url': 'https://www.purdue.edu/careerfair/'
            },
            {
                'resource_id': 'academic_advising',
                'type': 'advising',
                'name': 'CS Academic Advising',
                'description': 'Professional academic advisors for course planning and degree requirements',
                'contact_info': 'csadvising@purdue.edu',
                'meeting_times': 'By appointment',
                'location': 'LWSN 1205',
                'website_url': 'https://www.cs.purdue.edu/undergraduate/advising.html'
            }
        ]
        
        for resource in resources:
            cursor.execute('''
                INSERT OR REPLACE INTO resources 
                (resource_id, type, name, description, contact_info, meeting_times, location, website_url, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                resource['resource_id'], resource['type'], resource['name'],
                resource['description'], resource['contact_info'], 
                resource['meeting_times'], resource['location'],
                resource['website_url'], datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        
        print("✅ Default policies and resources inserted")

if __name__ == "__main__":
    # Initialize enhanced database
    db = EnhancedDatabase()
    db.insert_default_data()
    print("Enhanced database setup complete!")