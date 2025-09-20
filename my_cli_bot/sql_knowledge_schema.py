#!/usr/bin/env python3
"""
SQL Knowledge Base Schema for Boiler AI
Creates and manages the relational database schema for academic advisor data
"""

import sqlite3
import json
import os
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

class SQLKnowledgeSchema:
    """
    Manages the SQL schema for the academic knowledge base
    """
    
    def __init__(self, db_path: str = "data/purdue_cs_advisor.db"):
        self.db_path = db_path
        self.ensure_directory()
    
    def ensure_directory(self):
        """Ensure the data directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column name access
        try:
            yield conn
        finally:
            conn.close()
    
    def create_schema(self):
        """Create the complete database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Courses table - Core course information
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    credits INTEGER NOT NULL,
                    description TEXT,
                    course_type TEXT, -- foundation, track, elective
                    semester TEXT,
                    is_critical BOOLEAN DEFAULT FALSE,
                    difficulty_level TEXT,
                    difficulty_rating REAL,
                    time_commitment TEXT,
                    prerequisite_knowledge TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # 2. Prerequisites table - Course dependencies
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prerequisites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_code TEXT NOT NULL,
                    prerequisite_code TEXT NOT NULL,
                    is_corequisite BOOLEAN DEFAULT FALSE,
                    requirement_type TEXT DEFAULT 'required', -- required, recommended, alternative
                    FOREIGN KEY (course_code) REFERENCES courses(code),
                    FOREIGN KEY (prerequisite_code) REFERENCES courses(code),
                    UNIQUE(course_code, prerequisite_code)
                );
            """)
            
            # 3. Tracks table - Academic tracks/specializations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    career_focus TEXT,
                    difficulty_rating REAL,
                    job_market_rating REAL,
                    research_oriented BOOLEAN DEFAULT FALSE
                );
            """)
            
            # 4. Track requirements - Courses required for each track
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS track_requirements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    track_code TEXT NOT NULL,
                    course_code TEXT NOT NULL,
                    requirement_type TEXT DEFAULT 'required', -- required, elective, recommended
                    category TEXT, -- core, advanced, project
                    FOREIGN KEY (track_code) REFERENCES tracks(code),
                    FOREIGN KEY (course_code) REFERENCES courses(code),
                    UNIQUE(track_code, course_code)
                );
            """)
            
            # 5. Academic policies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS academic_policies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    policy_name TEXT UNIQUE NOT NULL,
                    policy_type TEXT, -- graduation, enrollment, grading
                    description TEXT,
                    requirements TEXT, -- JSON array of requirements
                    exceptions TEXT,   -- JSON array of exceptions
                    effective_date TEXT
                );
            """)
            
            # 6. Course load guidelines
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS course_load_guidelines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_level TEXT NOT NULL, -- freshman, sophomore, junior, senior, summer
                    total_credits_max INTEGER,
                    cs_courses_max INTEGER,
                    cs_courses_recommended INTEGER,
                    rationale TEXT
                );
            """)
            
            # 7. Graduation timelines
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS graduation_timelines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timeline_type TEXT NOT NULL, -- early_3yr, early_3_5yr, standard_4yr, delayed_4_5yr
                    total_years REAL,
                    success_probability REAL,
                    description TEXT,
                    requirements TEXT, -- JSON array of requirements
                    semester_plan TEXT -- JSON object with semester-by-semester plan
                );
            """)
            
            # 8. Failure recovery scenarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS failure_recovery (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    failed_course_code TEXT NOT NULL,
                    semester_failed TEXT,
                    delay_semesters INTEGER,
                    affected_courses TEXT, -- JSON array of affected course codes
                    recovery_strategy TEXT,
                    summer_option BOOLEAN DEFAULT FALSE,
                    graduation_impact TEXT,
                    FOREIGN KEY (failed_course_code) REFERENCES courses(code)
                );
            """)
            
            # 9. Course difficulty factors (normalized from JSON arrays)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS course_difficulty_factors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_code TEXT NOT NULL,
                    factor_description TEXT NOT NULL,
                    FOREIGN KEY (course_code) REFERENCES courses(code)
                );
            """)
            
            # 10. Course success tips (normalized from JSON arrays)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS course_success_tips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_code TEXT NOT NULL,
                    tip_description TEXT NOT NULL,
                    FOREIGN KEY (course_code) REFERENCES courses(code)
                );
            """)
            
            # 11. Course common struggles (normalized from JSON arrays)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS course_struggles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_code TEXT NOT NULL,
                    struggle_description TEXT NOT NULL,
                    FOREIGN KEY (course_code) REFERENCES courses(code)
                );
            """)
            
            # 12. CODO requirements
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS codo_requirements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    requirement_type TEXT NOT NULL, -- gpa, course, math, general
                    requirement_key TEXT NOT NULL,
                    requirement_value TEXT,
                    description TEXT,
                    is_mandatory BOOLEAN DEFAULT TRUE
                );
            """)
            
            # Create indexes for performance
            self._create_indexes(cursor)
            
            conn.commit()
            print("✅ Database schema created successfully!")
    
    def _create_indexes(self, cursor):
        """Create performance indexes"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_courses_code ON courses(code);",
            "CREATE INDEX IF NOT EXISTS idx_courses_type ON courses(course_type);",
            "CREATE INDEX IF NOT EXISTS idx_courses_critical ON courses(is_critical);",
            "CREATE INDEX IF NOT EXISTS idx_prerequisites_course ON prerequisites(course_code);",
            "CREATE INDEX IF NOT EXISTS idx_prerequisites_prereq ON prerequisites(prerequisite_code);",
            "CREATE INDEX IF NOT EXISTS idx_track_requirements_track ON track_requirements(track_code);",
            "CREATE INDEX IF NOT EXISTS idx_track_requirements_course ON track_requirements(course_code);",
            "CREATE INDEX IF NOT EXISTS idx_failure_recovery_course ON failure_recovery(failed_course_code);",
        ]
        
        for index in indexes:
            cursor.execute(index)
    
    def migrate_from_json(self, json_path: str = "data/cs_knowledge_graph.json"):
        """Migrate data from existing JSON knowledge base to SQL"""
        print("🔄 Starting migration from JSON to SQL...")
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Clear existing data
            tables = [
                'course_struggles', 'course_success_tips', 'course_difficulty_factors',
                'failure_recovery', 'track_requirements', 'codo_requirements',
                'course_load_guidelines', 'graduation_timelines', 'academic_policies',
                'prerequisites', 'tracks', 'courses'
            ]
            
            for table in tables:
                cursor.execute(f"DELETE FROM {table};")
            
            # Migrate courses
            self._migrate_courses(cursor, data.get('courses', {}))
            
            # Migrate tracks
            self._migrate_tracks(cursor, data.get('tracks', {}))
            
            # Migrate prerequisites
            self._migrate_prerequisites(cursor, data.get('prerequisites', {}))
            
            # Migrate academic policies
            self._migrate_academic_policies(cursor, data.get('academic_policies', {}))
            
            # Migrate course load guidelines
            self._migrate_course_load_guidelines(cursor, data.get('course_load_guidelines', {}))
            
            # Migrate graduation timelines
            self._migrate_graduation_timelines(cursor, data.get('graduation_timelines', {}))
            
            # Migrate failure recovery
            self._migrate_failure_recovery(cursor, data.get('failure_recovery_scenarios', {}))
            
            # Migrate CODO requirements
            self._migrate_codo_requirements(cursor, data.get('codo_requirements', {}))
            
            conn.commit()
            print("✅ Migration completed successfully!")
    
    def _migrate_courses(self, cursor, courses_data):
        """Migrate courses data"""
        print("  📚 Migrating courses...")
        
        for course_code, course_info in courses_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO courses (
                    code, title, credits, description, course_type, semester,
                    is_critical, difficulty_level, difficulty_rating,
                    time_commitment, prerequisite_knowledge
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                course_code,
                course_info.get('title', ''),
                course_info.get('credits', 0),
                course_info.get('description', ''),
                course_info.get('course_type', ''),
                course_info.get('semester', ''),
                course_info.get('is_critical', False),
                course_info.get('difficulty_level', ''),
                course_info.get('difficulty_rating', 0.0),
                course_info.get('time_commitment', ''),
                course_info.get('prerequisite_knowledge', '')
            ))
            
            # Migrate difficulty factors
            for factor in course_info.get('difficulty_factors', []):
                cursor.execute("""
                    INSERT INTO course_difficulty_factors (course_code, factor_description)
                    VALUES (?, ?)
                """, (course_code, factor))
            
            # Migrate success tips
            for tip in course_info.get('success_tips', []):
                cursor.execute("""
                    INSERT INTO course_success_tips (course_code, tip_description)
                    VALUES (?, ?)
                """, (course_code, tip))
            
            # Migrate common struggles
            for struggle in course_info.get('common_struggles', []):
                cursor.execute("""
                    INSERT INTO course_struggles (course_code, struggle_description)
                    VALUES (?, ?)
                """, (course_code, struggle))
    
    def _migrate_tracks(self, cursor, tracks_data):
        """Migrate tracks data"""
        print("  🎯 Migrating tracks...")
        
        for track_code, track_info in tracks_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO tracks (
                    code, name, description, career_focus,
                    difficulty_rating, job_market_rating, research_oriented
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                track_code,
                track_info.get('name', ''),
                track_info.get('description', ''),
                track_info.get('career_focus', ''),
                track_info.get('difficulty_rating', 0.0),
                track_info.get('job_market_rating', 0.0),
                track_info.get('research_oriented', False)
            ))
            
            # Migrate track requirements
            for req_type, courses in track_info.get('requirements', {}).items():
                for course_code in courses:
                    cursor.execute("""
                        INSERT INTO track_requirements (track_code, course_code, requirement_type)
                        VALUES (?, ?, ?)
                    """, (track_code, course_code, req_type))
    
    def _migrate_prerequisites(self, cursor, prerequisites_data):
        """Migrate prerequisites data"""
        print("  🔗 Migrating prerequisites...")
        
        for course_code, prereq_list in prerequisites_data.items():
            if isinstance(prereq_list, list):
                for prereq in prereq_list:
                    cursor.execute("""
                        INSERT OR REPLACE INTO prerequisites (course_code, prerequisite_code)
                        VALUES (?, ?)
                    """, (course_code, prereq))
    
    def _migrate_academic_policies(self, cursor, policies_data):
        """Migrate academic policies data"""
        print("  📋 Migrating academic policies...")
        
        for policy_name, policy_info in policies_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO academic_policies (
                    policy_name, policy_type, description, requirements
                ) VALUES (?, ?, ?, ?)
            """, (
                policy_name,
                policy_info.get('type', ''),
                policy_info.get('description', ''),
                json.dumps(policy_info.get('requirements', []))
            ))
    
    def _migrate_course_load_guidelines(self, cursor, guidelines_data):
        """Migrate course load guidelines data"""
        print("  📊 Migrating course load guidelines...")
        
        for level, guidelines in guidelines_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO course_load_guidelines (
                    student_level, total_credits_max, cs_courses_max,
                    cs_courses_recommended, rationale
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                level,
                guidelines.get('total_credits_max', 0),
                guidelines.get('cs_courses_max', 0),
                guidelines.get('cs_courses_recommended', 0),
                guidelines.get('rationale', '')
            ))
    
    def _migrate_graduation_timelines(self, cursor, timelines_data):
        """Migrate graduation timelines data"""
        print("  🎓 Migrating graduation timelines...")
        
        for timeline_type, timeline_info in timelines_data.items():
            # Handle different data structures (dict vs list)
            if isinstance(timeline_info, dict):
                # Calculate years from semesters
                total_semesters = timeline_info.get('total_semesters', 8)
                total_years = total_semesters / 2.0  # 2 semesters per year
                
                cursor.execute("""
                    INSERT OR REPLACE INTO graduation_timelines (
                        timeline_type, total_years, success_probability,
                        description, requirements, semester_plan
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    timeline_type,
                    total_years,
                    timeline_info.get('success_probability', 0.0),
                    timeline_info.get('description', ''),
                    json.dumps(timeline_info.get('requirements', [])),
                    json.dumps(timeline_info)  # Store entire object as semester plan
                ))
            elif isinstance(timeline_info, list):
                # Handle list of tips/requirements
                cursor.execute("""
                    INSERT OR REPLACE INTO graduation_timelines (
                        timeline_type, total_years, success_probability,
                        description, requirements, semester_plan
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    timeline_type,
                    0.0,  # No specific timeline
                    0.0,  # No specific probability
                    f"Tips and strategies for {timeline_type}",
                    json.dumps(timeline_info),
                    json.dumps({})
                ))
    
    def _migrate_failure_recovery(self, cursor, recovery_data):
        """Migrate failure recovery scenarios data"""
        print("  🚨 Migrating failure recovery scenarios...")
        
        for scenario_key, scenario_data in recovery_data.items():
            # Extract course code from scenario key (e.g., "CS 18000_failure" -> "CS 18000")
            course_code = scenario_key.replace('_failure', '')
            
            if isinstance(scenario_data, dict):
                cursor.execute("""
                    INSERT OR REPLACE INTO failure_recovery (
                        failed_course_code, semester_failed, delay_semesters,
                        affected_courses, recovery_strategy, summer_option, graduation_impact
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    course_code,
                    'general',  # Default semester
                    scenario_data.get('delay_semesters', 0),
                    json.dumps(scenario_data.get('affected_courses', [])),
                    scenario_data.get('recovery_strategy', ''),
                    scenario_data.get('summer_option', False),
                    scenario_data.get('graduation_impact', '')
                ))
    
    def _migrate_codo_requirements(self, cursor, codo_data):
        """Migrate CODO requirements data"""
        print("  🎯 Migrating CODO requirements...")
        
        # Simple key-value requirements
        simple_reqs = {
            'minimum_gpa': ('gpa', 'minimum_gpa'),
            'minimum_semesters': ('general', 'minimum_semesters'),
            'minimum_purdue_credits': ('general', 'minimum_purdue_credits'),
            'admission_basis': ('general', 'admission_basis'),
            'space_availability': ('general', 'space_availability')
        }
        
        for req_key, (req_type, req_name) in simple_reqs.items():
            if req_key in codo_data:
                cursor.execute("""
                    INSERT OR REPLACE INTO codo_requirements (
                        requirement_type, requirement_key, requirement_value
                    ) VALUES (?, ?, ?)
                """, (req_type, req_name, str(codo_data[req_key])))
        
        # Required courses
        for course in codo_data.get('required_courses', []):
            cursor.execute("""
                INSERT OR REPLACE INTO codo_requirements (
                    requirement_type, requirement_key, requirement_value, description
                ) VALUES (?, ?, ?, ?)
            """, (
                'course',
                course.get('code', ''),
                course.get('minimum_grade', ''),
                f"{course.get('title', '')} - {course.get('credits', 0)} credits"
            ))
    
    def verify_migration(self):
        """Verify the migration was successful"""
        print("\n🔍 Verifying migration...")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count records in each table
            tables = [
                'courses', 'tracks', 'prerequisites', 'track_requirements',
                'academic_policies', 'course_load_guidelines', 'graduation_timelines',
                'failure_recovery', 'codo_requirements'
            ]
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} records")
            
            # Test a complex query
            cursor.execute("""
                SELECT c.code, c.title, COUNT(p.prerequisite_code) as prereq_count
                FROM courses c
                LEFT JOIN prerequisites p ON c.code = p.course_code
                WHERE c.is_critical = 1
                GROUP BY c.code, c.title
                ORDER BY prereq_count DESC
                LIMIT 5
            """)
            
            print("\n📚 Critical courses with most prerequisites:")
            for row in cursor.fetchall():
                print(f"  {row[0]} - {row[1]} ({row[2]} prerequisites)")

if __name__ == "__main__":
    schema = SQLKnowledgeSchema()
    schema.create_schema()
    schema.migrate_from_json()
    schema.verify_migration()