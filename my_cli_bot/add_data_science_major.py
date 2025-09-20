#!/usr/bin/env python3
"""
Add Data Science Major to Knowledge Base
Creates separate major structure while maintaining shared courses
"""

import sqlite3
import json
from datetime import datetime

def create_multi_major_schema(db_path="data/purdue_cs_advisor.db"):
    """Create tables to support multiple majors"""
    print("🏗️ Creating Multi-Major Database Schema")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create majors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS majors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                school TEXT NOT NULL,
                description TEXT,
                total_credits INTEGER,
                major_credits INTEGER,
                gpa_requirement REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create major requirements table (replaces and extends track_requirements)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS major_requirements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                major_code TEXT NOT NULL,
                course_code TEXT NOT NULL,
                requirement_type TEXT NOT NULL,  -- 'required', 'elective', 'foundation'
                category TEXT,  -- 'core', 'math', 'statistics', etc.
                credits INTEGER,
                min_grade TEXT,  -- 'C', 'B', etc.
                notes TEXT,
                FOREIGN KEY (major_code) REFERENCES majors(code)
            )
        """)
        
        # Add major_code to existing courses table if not exists
        cursor.execute("PRAGMA table_info(courses)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'major_code' not in columns:
            cursor.execute("ALTER TABLE courses ADD COLUMN major_code TEXT")
        
        # Create cross-major relationships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cross_major_courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_code TEXT NOT NULL,
                major_code TEXT NOT NULL,
                applies_to_major BOOLEAN DEFAULT TRUE,
                transfer_credits INTEGER,
                notes TEXT
            )
        """)
        
        # Update graduation timelines to support multiple majors
        cursor.execute("PRAGMA table_info(graduation_timelines)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'major_code' not in columns:
            cursor.execute("ALTER TABLE graduation_timelines ADD COLUMN major_code TEXT DEFAULT 'CS'")
        
        # Update CODO requirements for multiple majors
        cursor.execute("PRAGMA table_info(codo_requirements)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'major_code' not in columns:
            cursor.execute("ALTER TABLE codo_requirements ADD COLUMN major_code TEXT DEFAULT 'CS'")
        
        conn.commit()
        print("✅ Multi-major schema created successfully")
        
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def add_majors_data(db_path="data/purdue_cs_advisor.db"):
    """Add Computer Science and Data Science major information"""
    print("\n📚 Adding Major Information")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add Computer Science major
        cursor.execute("""
            INSERT OR REPLACE INTO majors (code, name, school, description, total_credits, major_credits, gpa_requirement)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'CS',
            'Computer Science',
            'College of Science',
            'The Computer Science program provides a strong foundation in programming, algorithms, and system design with specialization tracks in various areas.',
            120,
            45,  # Approximate based on typical CS requirements
            2.0
        ))
        
        # Add Data Science major
        cursor.execute("""
            INSERT OR REPLACE INTO majors (code, name, school, description, total_credits, major_credits, gpa_requirement)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'DS',
            'Data Science',
            'College of Science',
            'The Data Science program combines computer science, statistics, and domain expertise to extract insights from data and build predictive models.',
            120,
            52,  # 51-52 credits as specified
            2.0
        ))
        
        conn.commit()
        print("✅ Major information added")
        
    except Exception as e:
        print(f"❌ Error adding majors: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def add_data_science_courses(db_path="data/purdue_cs_advisor.db"):
    """Add Data Science specific courses and requirements"""
    print("\n📖 Adding Data Science Courses")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Data Science specific courses (not shared with CS)
        ds_courses = [
            {
                'code': 'CS 25300',
                'title': 'Data Structures And Algorithms For DS/AI',
                'credits': 3,
                'description': 'Data structures and algorithms specifically designed for data science and AI applications. Covers advanced data structures for big data processing and machine learning algorithms.',
                'course_type': 'required',
                'difficulty_level': 'intermediate',
                'difficulty_rating': 3.5,
                'time_commitment': '8-10 hours per week',
                'major_code': 'DS'
            },
            {
                'code': 'CS 37300',
                'title': 'Data Mining And Machine Learning',
                'credits': 3,
                'description': 'Introduction to data mining techniques and machine learning algorithms. Covers supervised and unsupervised learning, classification, clustering, and neural networks.',
                'course_type': 'required',
                'difficulty_level': 'advanced',
                'difficulty_rating': 4.0,
                'time_commitment': '10-12 hours per week',
                'major_code': 'DS'
            },
            {
                'code': 'CS 38003',
                'title': 'Python Programming',
                'credits': 1,
                'description': 'Focused course on Python programming for data science applications. Covers libraries like NumPy, Pandas, and Matplotlib.',
                'course_type': 'required',
                'difficulty_level': 'beginner',
                'difficulty_rating': 2.5,
                'time_commitment': '3-4 hours per week',
                'major_code': 'DS'
            },
            {
                'code': 'CS 44000',
                'title': 'Large Scale Data Analytics',
                'credits': 3,
                'description': 'Techniques for processing and analyzing large datasets. Covers distributed computing, MapReduce, Spark, and cloud-based analytics platforms.',
                'course_type': 'required',
                'difficulty_level': 'advanced',
                'difficulty_rating': 4.2,
                'time_commitment': '10-12 hours per week',
                'major_code': 'DS'
            },
            {
                'code': 'CS 24200',
                'title': 'Introduction To Data Science',
                'credits': 3,
                'description': 'Introduction to data science concepts, tools, and methodologies. Covers data collection, cleaning, analysis, and visualization.',
                'course_type': 'required',
                'difficulty_level': 'intermediate',
                'difficulty_rating': 3.0,
                'time_commitment': '6-8 hours per week',
                'major_code': 'DS'
            },
            {
                'code': 'MA 35100',
                'title': 'Elementary Linear Algebra',
                'credits': 3,
                'description': 'Linear algebra concepts essential for data science and machine learning. Covers matrices, vector spaces, eigenvalues, and applications.',
                'course_type': 'required',
                'difficulty_level': 'intermediate',
                'difficulty_rating': 3.8,
                'time_commitment': '8-10 hours per week',
                'major_code': 'DS'
            },
            {
                'code': 'STAT 35500',
                'title': 'Statistics For Data Science',
                'credits': 3,
                'description': 'Statistical methods and concepts for data science applications. Covers descriptive statistics, hypothesis testing, and regression analysis.',
                'course_type': 'required',
                'difficulty_level': 'intermediate',
                'difficulty_rating': 3.5,
                'time_commitment': '8-9 hours per week',
                'major_code': 'DS'
            },
            {
                'code': 'STAT 41600',
                'title': 'Probability',
                'credits': 3,
                'description': 'Probability theory foundations for statistical analysis and machine learning. Covers probability distributions, random variables, and statistical inference.',
                'course_type': 'required',
                'difficulty_level': 'advanced',
                'difficulty_rating': 4.0,
                'time_commitment': '10-11 hours per week',
                'major_code': 'DS'
            },
            {
                'code': 'STAT 41700',
                'title': 'Statistical Theory',
                'credits': 3,
                'description': 'Advanced statistical theory including estimation, hypothesis testing, and asymptotic theory. Essential for understanding machine learning algorithms.',
                'course_type': 'required',
                'difficulty_level': 'advanced',
                'difficulty_rating': 4.3,
                'time_commitment': '12-14 hours per week',
                'major_code': 'DS'
            },
            {
                'code': 'STAT 24200',
                'title': 'Introduction To Data Science',
                'credits': 3,
                'description': 'Statistics department version of introduction to data science. Emphasizes statistical modeling and inference for data analysis.',
                'course_type': 'elective',
                'difficulty_level': 'intermediate',
                'difficulty_rating': 3.0,
                'time_commitment': '6-8 hours per week',
                'major_code': 'DS'
            }
        ]
        
        # Add courses to database
        for course in ds_courses:
            # Check if course already exists
            cursor.execute("SELECT id FROM courses WHERE code = ?", (course['code'],))
            if cursor.fetchone():
                print(f"   📚 Updating existing course: {course['code']}")
                cursor.execute("""
                    UPDATE courses SET 
                        title = ?, credits = ?, description = ?, course_type = ?,
                        difficulty_level = ?, difficulty_rating = ?, time_commitment = ?, major_code = ?
                    WHERE code = ?
                """, (
                    course['title'], course['credits'], course['description'], course['course_type'],
                    course['difficulty_level'], course['difficulty_rating'], course['time_commitment'], 
                    course['major_code'], course['code']
                ))
            else:
                print(f"   📚 Adding new course: {course['code']} - {course['title']}")
                cursor.execute("""
                    INSERT INTO courses (code, title, credits, description, course_type, difficulty_level, 
                                       difficulty_rating, time_commitment, major_code, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    course['code'], course['title'], course['credits'], course['description'], 
                    course['course_type'], course['difficulty_level'], course['difficulty_rating'], 
                    course['time_commitment'], course['major_code'], datetime.now(), datetime.now()
                ))
        
        conn.commit()
        print("✅ Data Science courses added")
        
    except Exception as e:
        print(f"❌ Error adding courses: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def add_data_science_requirements(db_path="data/purdue_cs_advisor.db"):
    """Add Data Science major requirements"""
    print("\n📋 Adding Data Science Requirements")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Data Science required courses (36-37 credits)
        ds_requirements = [
            # Shared foundation courses
            {'course_code': 'CS 18000', 'requirement_type': 'required', 'category': 'foundation', 'credits': 4, 'min_grade': 'C'},
            {'course_code': 'CS 18200', 'requirement_type': 'required', 'category': 'foundation', 'credits': 3, 'min_grade': 'C'},
            
            # DS-specific core courses
            {'course_code': 'CS 25300', 'requirement_type': 'required', 'category': 'core', 'credits': 3, 'min_grade': 'C'},
            {'course_code': 'CS 37300', 'requirement_type': 'required', 'category': 'core', 'credits': 3, 'min_grade': 'C', 'notes': 'Must be completed with grade of C or better prior to Capstone'},
            {'course_code': 'CS 38003', 'requirement_type': 'required', 'category': 'programming', 'credits': 1, 'min_grade': 'C'},
            {'course_code': 'CS 44000', 'requirement_type': 'required', 'category': 'core', 'credits': 3, 'min_grade': 'C'},
            
            # Math requirements
            {'course_code': 'MA 35100', 'requirement_type': 'required', 'category': 'math', 'credits': 3, 'min_grade': 'C'},
            {'course_code': 'MA 26100', 'requirement_type': 'required', 'category': 'math', 'credits': 4, 'min_grade': 'C', 'notes': 'Alternative: MA 27101 (5 credits)'},
            
            # Statistics requirements
            {'course_code': 'STAT 35500', 'requirement_type': 'required', 'category': 'statistics', 'credits': 3, 'min_grade': 'C'},
            {'course_code': 'STAT 41600', 'requirement_type': 'required', 'category': 'statistics', 'credits': 3, 'min_grade': 'C'},
            {'course_code': 'STAT 41700', 'requirement_type': 'required', 'category': 'statistics', 'credits': 3, 'min_grade': 'C'},
            
            # Elective choice
            {'course_code': 'CS 24200', 'requirement_type': 'elective', 'category': 'introduction', 'credits': 3, 'min_grade': 'C', 'notes': 'Alternative: STAT 24200'},
            {'course_code': 'STAT 24200', 'requirement_type': 'elective', 'category': 'introduction', 'credits': 3, 'min_grade': 'C', 'notes': 'Alternative: CS 24200'},
        ]
        
        # Add requirements to database
        for req in ds_requirements:
            cursor.execute("""
                INSERT OR REPLACE INTO major_requirements 
                (major_code, course_code, requirement_type, category, credits, min_grade, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                'DS', req['course_code'], req['requirement_type'], req['category'], 
                req['credits'], req['min_grade'], req.get('notes', '')
            ))
            print(f"   📋 Added requirement: {req['course_code']} ({req['requirement_type']})")
        
        conn.commit()
        print("✅ Data Science requirements added")
        
    except Exception as e:
        print(f"❌ Error adding requirements: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def add_shared_courses_mapping(db_path="data/purdue_cs_advisor.db"):
    """Map shared courses between CS and DS majors"""
    print("\n🔗 Adding Shared Course Mappings")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Courses shared between CS and DS
        shared_courses = [
            {'course_code': 'CS 18000', 'major_code': 'CS', 'transfer_credits': 4},
            {'course_code': 'CS 18000', 'major_code': 'DS', 'transfer_credits': 4},
            {'course_code': 'CS 18200', 'major_code': 'CS', 'transfer_credits': 3},
            {'course_code': 'CS 18200', 'major_code': 'DS', 'transfer_credits': 3},
            {'course_code': 'MA 26100', 'major_code': 'CS', 'transfer_credits': 4},
            {'course_code': 'MA 26100', 'major_code': 'DS', 'transfer_credits': 4},
        ]
        
        for mapping in shared_courses:
            cursor.execute("""
                INSERT OR REPLACE INTO cross_major_courses 
                (course_code, major_code, applies_to_major, transfer_credits, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (
                mapping['course_code'], mapping['major_code'], True, 
                mapping['transfer_credits'], 'Foundation course shared across majors'
            ))
            print(f"   🔗 Mapped {mapping['course_code']} to {mapping['major_code']}")
        
        conn.commit()
        print("✅ Shared course mappings added")
        
    except Exception as e:
        print(f"❌ Error adding mappings: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def add_data_science_prerequisites(db_path="data/purdue_cs_advisor.db"):
    """Add prerequisites for Data Science courses"""
    print("\n🔗 Adding Data Science Prerequisites")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Prerequisites for DS courses
        ds_prerequisites = [
            # CS 25300 prerequisites
            {'course_code': 'CS 25300', 'prerequisite_code': 'CS 18000', 'requirement_type': 'prerequisite'},
            {'course_code': 'CS 25300', 'prerequisite_code': 'CS 18200', 'requirement_type': 'prerequisite'},
            
            # CS 37300 prerequisites  
            {'course_code': 'CS 37300', 'prerequisite_code': 'CS 25300', 'requirement_type': 'prerequisite'},
            {'course_code': 'CS 37300', 'prerequisite_code': 'STAT 35500', 'requirement_type': 'prerequisite'},
            {'course_code': 'CS 37300', 'prerequisite_code': 'MA 35100', 'requirement_type': 'prerequisite'},
            
            # CS 44000 prerequisites
            {'course_code': 'CS 44000', 'prerequisite_code': 'CS 25300', 'requirement_type': 'prerequisite'},
            {'course_code': 'CS 44000', 'prerequisite_code': 'CS 37300', 'requirement_type': 'prerequisite'},
            
            # Math prerequisites
            {'course_code': 'MA 35100', 'prerequisite_code': 'MA 26100', 'requirement_type': 'prerequisite'},
            
            # Statistics prerequisites
            {'course_code': 'STAT 41600', 'prerequisite_code': 'MA 26100', 'requirement_type': 'prerequisite'},
            {'course_code': 'STAT 41700', 'prerequisite_code': 'STAT 41600', 'requirement_type': 'prerequisite'},
            
            # Introduction courses
            {'course_code': 'CS 24200', 'prerequisite_code': 'CS 18000', 'requirement_type': 'prerequisite'},
            {'course_code': 'STAT 24200', 'prerequisite_code': 'STAT 35500', 'requirement_type': 'prerequisite'},
        ]
        
        for prereq in ds_prerequisites:
            # Check if prerequisite already exists
            cursor.execute("""
                SELECT id FROM prerequisites 
                WHERE course_code = ? AND prerequisite_code = ?
            """, (prereq['course_code'], prereq['prerequisite_code']))
            
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO prerequisites (course_code, prerequisite_code, requirement_type)
                    VALUES (?, ?, ?)
                """, (prereq['course_code'], prereq['prerequisite_code'], prereq['requirement_type']))
                print(f"   🔗 Added prerequisite: {prereq['prerequisite_code']} → {prereq['course_code']}")
        
        conn.commit()
        print("✅ Data Science prerequisites added")
        
    except Exception as e:
        print(f"❌ Error adding prerequisites: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def update_existing_cs_data(db_path="data/purdue_cs_advisor.db"):
    """Update existing CS data to include major_code"""
    print("\n🔄 Updating Existing CS Data")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Update CS courses to have major_code
        cursor.execute("""
            UPDATE courses SET major_code = 'CS' 
            WHERE major_code IS NULL AND (
                code LIKE 'CS %' OR 
                course_type IN ('foundation', 'track', 'core')
            )
        """)
        
        # Update graduation timelines
        cursor.execute("UPDATE graduation_timelines SET major_code = 'CS' WHERE major_code IS NULL")
        
        # Update CODO requirements
        cursor.execute("UPDATE codo_requirements SET major_code = 'CS' WHERE major_code IS NULL")
        
        conn.commit()
        print("✅ Existing CS data updated with major codes")
        
    except Exception as e:
        print(f"❌ Error updating CS data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def main():
    """Main function to add Data Science major to knowledge base"""
    print("🎓 Adding Data Science Major to Knowledge Base")
    print("=" * 60)
    
    try:
        # Step 1: Create multi-major schema
        create_multi_major_schema()
        
        # Step 2: Add major information
        add_majors_data()
        
        # Step 3: Add DS courses
        add_data_science_courses()
        
        # Step 4: Add DS requirements
        add_data_science_requirements()
        
        # Step 5: Add shared course mappings
        add_shared_courses_mapping()
        
        # Step 6: Add DS prerequisites
        add_data_science_prerequisites()
        
        # Step 7: Update existing CS data
        update_existing_cs_data()
        
        print("\n" + "=" * 60)
        print("🎉 DATA SCIENCE MAJOR SUCCESSFULLY ADDED!")
        print("=" * 60)
        print("✅ Multi-major database schema created")
        print("✅ Data Science courses and requirements added")
        print("✅ Prerequisites and dependencies mapped")
        print("✅ Shared courses identified and linked")
        print("✅ Existing CS data preserved and updated")
        print("\n🚀 System ready for Data Science academic advising!")
        
    except Exception as e:
        print(f"\n❌ Error adding Data Science major: {e}")
        raise

if __name__ == "__main__":
    main()