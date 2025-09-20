#!/usr/bin/env python3
"""
Boiler AI Networking Module - Connect students with upperclassmen mentors
Separate module that integrates with existing Boiler AI system without affecting core functionality.
"""

import json
import os
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import hashlib
import random

@dataclass
class StudentProfile:
    """Student profile for networking"""
    user_id: str
    year_level: str  # freshman, sophomore, junior, senior
    track: Optional[str]  # MI, SE, or None
    completed_courses: List[str]
    gpa_range: str  # "3.0-3.5", "3.5-4.0", etc. for privacy
    career_interests: List[str]
    is_mentor: bool = False
    availability: str = "weekends"  # when they're available to help
    contact_method: str = "platform"  # how they prefer to be contacted

@dataclass
class NetworkingRequest:
    """Request for connecting with upperclassmen"""
    request_id: str
    requester_id: str
    topic: str
    description: str
    urgency: str  # low, medium, high
    preferred_mentor_criteria: Dict[str, Any]
    created_at: datetime
    status: str = "pending"  # pending, matched, closed

class BoilerNetworking:
    """Main networking system for connecting CS students"""
    
    def __init__(self, db_path: str = "boiler_networking.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for networking data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Student profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_profiles (
                user_id TEXT PRIMARY KEY,
                year_level TEXT NOT NULL,
                track TEXT,
                completed_courses TEXT,  -- JSON string
                gpa_range TEXT,
                career_interests TEXT,   -- JSON string
                is_mentor BOOLEAN DEFAULT FALSE,
                availability TEXT,
                contact_method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Networking requests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS networking_requests (
                request_id TEXT PRIMARY KEY,
                requester_id TEXT,
                topic TEXT NOT NULL,
                description TEXT,
                urgency TEXT DEFAULT 'medium',
                preferred_criteria TEXT,  -- JSON string
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                matched_mentor_id TEXT,
                FOREIGN KEY (requester_id) REFERENCES student_profiles (user_id)
            )
        ''')
        
        # Mentor-mentee connections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS connections (
                connection_id TEXT PRIMARY KEY,
                mentor_id TEXT,
                mentee_id TEXT,
                topic TEXT,
                status TEXT DEFAULT 'active',  -- active, completed, inactive
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_interaction TIMESTAMP,
                rating INTEGER,  -- 1-5 star rating from mentee
                feedback TEXT,
                FOREIGN KEY (mentor_id) REFERENCES student_profiles (user_id),
                FOREIGN KEY (mentee_id) REFERENCES student_profiles (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_student_profile(self, profile_data: Dict[str, Any]) -> StudentProfile:
        """Create a new student profile"""
        user_id = self._generate_user_id()
        
        profile = StudentProfile(
            user_id=user_id,
            year_level=profile_data.get('year_level', 'sophomore'),
            track=profile_data.get('track'),
            completed_courses=profile_data.get('completed_courses', []),
            gpa_range=profile_data.get('gpa_range', '3.0-3.5'),
            career_interests=profile_data.get('career_interests', []),
            is_mentor=profile_data.get('is_mentor', False),
            availability=profile_data.get('availability', 'weekends'),
            contact_method=profile_data.get('contact_method', 'platform')
        )
        
        self._save_profile(profile)
        return profile
    
    def register_as_mentor(self, user_id: str, mentor_info: Dict[str, Any]) -> bool:
        """Register existing user as a mentor"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE student_profiles 
                SET is_mentor = TRUE, availability = ?, last_active = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (mentor_info.get('availability', 'weekends'), user_id))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error registering mentor: {e}")
            return False
        finally:
            conn.close()
    
    def find_mentors(self, criteria: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """Find available mentors based on criteria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        base_query = '''
            SELECT user_id, year_level, track, completed_courses, career_interests, availability
            FROM student_profiles 
            WHERE is_mentor = TRUE
        '''
        params = []
        
        # Add criteria filters
        if criteria.get('track'):
            base_query += ' AND track = ?'
            params.append(criteria['track'])
            
        if criteria.get('min_year_level'):
            year_order = {'freshman': 1, 'sophomore': 2, 'junior': 3, 'senior': 4}
            min_level = year_order.get(criteria['min_year_level'], 2)
            base_query += ' AND CASE year_level WHEN "freshman" THEN 1 WHEN "sophomore" THEN 2 WHEN "junior" THEN 3 WHEN "senior" THEN 4 END >= ?'
            params.append(min_level)
        
        base_query += ' ORDER BY last_active DESC LIMIT ?'
        params.append(limit)
        
        try:
            cursor.execute(base_query, params)
            results = cursor.fetchall()
            
            mentors = []
            for row in results:
                mentors.append({
                    'user_id': row[0],
                    'year_level': row[1],
                    'track': row[2],
                    'completed_courses': json.loads(row[3]) if row[3] else [],
                    'career_interests': json.loads(row[4]) if row[4] else [],
                    'availability': row[5]
                })
            
            return mentors
            
        except Exception as e:
            print(f"Error finding mentors: {e}")
            return []
        finally:
            conn.close()
    
    def create_networking_request(self, requester_id: str, topic: str, description: str, 
                                criteria: Dict[str, Any], urgency: str = "medium") -> str:
        """Create a new networking request"""
        request_id = self._generate_request_id()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO networking_requests 
                (request_id, requester_id, topic, description, urgency, preferred_criteria)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (request_id, requester_id, topic, description, urgency, json.dumps(criteria)))
            
            conn.commit()
            return request_id
            
        except Exception as e:
            print(f"Error creating networking request: {e}")
            return None
        finally:
            conn.close()
    
    def match_request_with_mentor(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Try to match a networking request with available mentors"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get request details
            cursor.execute('''
                SELECT requester_id, topic, preferred_criteria 
                FROM networking_requests 
                WHERE request_id = ? AND status = 'pending'
            ''', (request_id,))
            
            request_data = cursor.fetchone()
            if not request_data:
                return None
            
            requester_id, topic, criteria_json = request_data
            criteria = json.loads(criteria_json) if criteria_json else {}
            
            # Find suitable mentors
            mentors = self.find_mentors(criteria)
            
            if mentors:
                # Simple matching - pick the most recently active mentor
                chosen_mentor = mentors[0]
                
                # Update request status
                cursor.execute('''
                    UPDATE networking_requests 
                    SET status = 'matched', matched_mentor_id = ?
                    WHERE request_id = ?
                ''', (chosen_mentor['user_id'], request_id))
                
                # Create connection record
                connection_id = self._generate_connection_id()
                cursor.execute('''
                    INSERT INTO connections 
                    (connection_id, mentor_id, mentee_id, topic, last_interaction)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (connection_id, chosen_mentor['user_id'], requester_id, topic))
                
                conn.commit()
                
                return {
                    'connection_id': connection_id,
                    'mentor': chosen_mentor,
                    'topic': topic
                }
            
            return None
            
        except Exception as e:
            print(f"Error matching request: {e}")
            return None
        finally:
            conn.close()
    
    def get_user_connections(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all connections for a user (as mentor or mentee)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT c.connection_id, c.mentor_id, c.mentee_id, c.topic, c.status, 
                       c.created_at, c.last_interaction, c.rating,
                       m.year_level as mentor_year, m.track as mentor_track,
                       n.year_level as mentee_year, n.track as mentee_track
                FROM connections c
                JOIN student_profiles m ON c.mentor_id = m.user_id
                JOIN student_profiles n ON c.mentee_id = n.user_id
                WHERE c.mentor_id = ? OR c.mentee_id = ?
                ORDER BY c.last_interaction DESC
            ''', (user_id, user_id))
            
            results = cursor.fetchall()
            connections = []
            
            for row in results:
                connections.append({
                    'connection_id': row[0],
                    'mentor_id': row[1],
                    'mentee_id': row[2],
                    'topic': row[3],
                    'status': row[4],
                    'created_at': row[5],
                    'last_interaction': row[6],
                    'rating': row[7],
                    'mentor_info': {'year_level': row[8], 'track': row[9]},
                    'mentee_info': {'year_level': row[10], 'track': row[11]},
                    'role': 'mentor' if row[1] == user_id else 'mentee'
                })
            
            return connections
            
        except Exception as e:
            print(f"Error getting connections: {e}")
            return []
        finally:
            conn.close()
    
    def process_networking_query(self, query: str, user_context: Dict[str, Any] = None) -> str:
        """Process networking-related queries and provide helpful responses"""
        query_lower = query.lower()
        
        # Detect networking-related queries
        if any(keyword in query_lower for keyword in [
            'connect', 'mentor', 'upperclassman', 'networking', 'help from student',
            'talk to someone', 'advice from student', 'student mentor'
        ]):
            
            # Extract what they're looking for help with
            if 'course' in query_lower or any(course in query_lower for course in [
                'cs 180', 'cs 182', 'cs 240', 'cs 251', 'cs 252', 'cs 25100'
            ]):
                return self._generate_course_help_response(query, user_context)
            
            elif any(keyword in query_lower for keyword in [
                'internship', 'job', 'career', 'interview', 'resume'
            ]):
                return self._generate_career_help_response(query, user_context)
            
            elif any(keyword in query_lower for keyword in [
                'track', 'machine intelligence', 'software engineering', 'mi', 'se'
            ]):
                return self._generate_track_help_response(query, user_context)
            
            else:
                return self._generate_general_networking_response(query, user_context)
        
        return None  # Not a networking query
    
    def _generate_course_help_response(self, query: str, user_context: Dict[str, Any]) -> str:
        """Generate response for course-related networking requests"""
        return """I can help you connect with upperclassmen who have experience with specific CS courses! 

Here's how our student networking works:

**Course Mentoring Available:**
- Get advice from students who've successfully completed challenging courses
- Learn study strategies and time management tips
- Understand what to expect and how to prepare
- Get recommendations for professors and sections

**To connect with a course mentor:**
1. Tell me which specific course you need help with
2. I'll find upperclassmen who've taken and done well in that course
3. You can ask questions about difficulty, study tips, project advice, etc.

**Popular mentoring topics:**
- CS 25100 (Data Structures) - study strategies and project help
- CS 18000 (Java Programming) - programming concepts and debugging
- Foundation course sequence planning and success tips
- Math courses (Calculus series) study groups

Would you like me to help you connect with someone about a specific course? Just let me know which one and what kind of advice you're looking for!"""
    
    def _generate_career_help_response(self, query: str, user_context: Dict[str, Any]) -> str:
        """Generate response for career-related networking requests"""
        return """Great question! Connecting with upperclassmen about career topics is one of our most popular networking features.

**Career Mentoring Available:**
- Internship application strategies and timeline planning  
- Resume review and interview preparation
- Industry insights from students with internship experience
- Career path guidance for different CS tracks
- Company culture insights and application tips

**What our student mentors can help with:**
- **Internship Success**: Students who've landed internships at major tech companies
- **Interview Prep**: Mock interviews and technical question practice
- **Resume Building**: What projects and experiences to highlight
- **Track Selection**: Career alignment with MI vs SE tracks
- **Networking**: How to build professional connections

**Connection Process:**
1. Specify your career interests (web dev, AI/ML, cybersecurity, etc.)
2. I'll match you with upperclassmen in related fields
3. Set up informal conversations about their experiences
4. Get practical advice from students who've been through the process

**Popular mentor backgrounds:**
- Students with FAANG internships (Google, Microsoft, Amazon, etc.)
- Startup experience and entrepreneurship
- Research and graduate school preparation
- Different industry sectors (fintech, healthcare tech, gaming)

What specific career aspect would you like guidance on? I can help you find the right student mentor!"""
    
    def _generate_track_help_response(self, query: str, user_context: Dict[str, Any]) -> str:
        """Generate response for track selection networking requests"""
        return """Track selection is a crucial decision, and talking to upperclassmen in each track is incredibly valuable!

**Track Mentoring Available:**

**Machine Intelligence (MI) Track Mentors:**
- Students currently in AI/ML courses and research
- Career insights: data science, AI research, ML engineering
- Course experiences: CS 37300 (Data Mining), CS 47100 (AI)
- Industry applications and internship experiences
- Graduate school and research opportunities

**Software Engineering (SE) Track Mentors:**  
- Students with industry development experience
- Large-scale project management and team collaboration
- Course experiences: CS 30700, CS 40800 (Testing), CS 40700 (Senior Project)
- Career paths: full-stack development, systems engineering, technical leadership
- Startup vs. big tech company experiences

**What Track Mentors Can Share:**
- Real course workload and difficulty comparisons
- Career trajectory differences and job market insights
- Daily work experiences in internships and co-ops
- How track choice affected their opportunities
- Pros and cons they wish they'd known earlier

**Typical Mentor Conversations:**
- "What's CS 37300 really like?" (MI track)
- "How team-intensive is the SE track?"
- "Which track better prepares for [specific career goal]?"
- "Can you switch tracks if you change your mind?"

**To Connect:**
Just tell me which track(s) you're considering and what specific questions you have. I'll find upperclassmen who can share their real experiences and help you make an informed decision.

Are you leaning toward MI, SE, or still exploring both options?"""
    
    def _generate_general_networking_response(self, query: str, user_context: Dict[str, Any]) -> str:
        """Generate response for general networking requests"""
        return """I'd love to help you connect with upperclassmen! Our student networking system helps you get real advice from peers who've been through similar experiences.

**Available Mentor Categories:**

**Academic Support:**
- Course-specific help and study strategies
- Foundation sequence navigation (CS 18000 through CS 25200)
- Time management and course load balancing
- Academic recovery and improvement strategies

**Career Guidance:**
- Internship hunting and application strategies
- Resume review and interview preparation  
- Industry insights and company culture
- Technical skill development priorities

**Track & Planning:**
- MI vs SE track decision support
- Graduation timeline planning and optimization
- CODO preparation and requirements
- Course scheduling and prerequisite management

**Personal Development:**
- Overcoming challenges and setbacks
- Building confidence in technical skills
- Campus involvement and leadership opportunities
- Work-life balance in demanding CS coursework

**How It Works:**
1. **Tell me what you need help with** - be specific about your situation
2. **I'll find relevant mentors** - upperclassmen with matching experiences
3. **Connect safely** - structured conversations through our platform
4. **Get practical advice** - real insights from students who've been there

**Example Connections:**
- "I'm struggling with CS 25100 and need study tips"
- "Should I choose MI or SE track for data science career?"
- "How do I prepare for technical interviews?"
- "I failed CS 18000 - how do I recover and stay on track?"

What specific area would you like help with? The more details you share, the better I can match you with the right mentor!"""
    
    # Utility methods
    def _generate_user_id(self) -> str:
        """Generate unique user ID"""
        return f"user_{int(time.time())}_{random.randint(1000, 9999)}"
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        return f"req_{int(time.time())}_{random.randint(1000, 9999)}"
    
    def _generate_connection_id(self) -> str:
        """Generate unique connection ID"""
        return f"conn_{int(time.time())}_{random.randint(1000, 9999)}"
    
    def _save_profile(self, profile: StudentProfile):
        """Save student profile to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO student_profiles
                (user_id, year_level, track, completed_courses, gpa_range, 
                 career_interests, is_mentor, availability, contact_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                profile.user_id, profile.year_level, profile.track,
                json.dumps(profile.completed_courses), profile.gpa_range,
                json.dumps(profile.career_interests), profile.is_mentor,
                profile.availability, profile.contact_method
            ))
            
            conn.commit()
        except Exception as e:
            print(f"Error saving profile: {e}")
        finally:
            conn.close()

# Demo/Test functionality
def demo_networking_system():
    """Demo the networking system functionality"""
    print("🔗 Boiler AI Networking System Demo")
    print("=" * 50)
    
    # Initialize system
    networking = BoilerNetworking("demo_networking.db")
    
    # Create some sample mentor profiles
    mentor1 = networking.create_student_profile({
        'year_level': 'senior',
        'track': 'SE',
        'completed_courses': ['CS 18000', 'CS 18200', 'CS 24000', 'CS 25000', 'CS 25100', 'CS 25200', 'CS 30700'],
        'gpa_range': '3.5-4.0',
        'career_interests': ['full-stack development', 'software engineering', 'tech leadership'],
        'is_mentor': True,
        'availability': 'weekends'
    })
    
    mentor2 = networking.create_student_profile({
        'year_level': 'junior',
        'track': 'MI',
        'completed_courses': ['CS 18000', 'CS 18200', 'CS 24000', 'CS 25000', 'CS 25100', 'CS 37300'],
        'gpa_range': '3.0-3.5',
        'career_interests': ['machine learning', 'data science', 'AI research'],
        'is_mentor': True,
        'availability': 'evenings'
    })
    
    print(f"✅ Created mentor profiles: {mentor1.user_id}, {mentor2.user_id}")
    
    # Create a mentee profile
    mentee = networking.create_student_profile({
        'year_level': 'sophomore',
        'track': None,
        'completed_courses': ['CS 18000', 'CS 18200', 'CS 24000'],
        'gpa_range': '2.5-3.0',
        'career_interests': ['web development', 'internships'],
        'is_mentor': False
    })
    
    print(f"✅ Created mentee profile: {mentee.user_id}")
    
    # Test networking query processing
    print("\n📝 Testing networking query responses:")
    print("-" * 40)
    
    queries = [
        "I need help with CS 25100, can I talk to someone who's taken it?",
        "How do I prepare for internship interviews?",
        "Should I choose MI or SE track for a career in AI?",
        "I'm struggling and need advice from an upperclassman"
    ]
    
    for query in queries:
        print(f"\n🤖 Query: {query}")
        response = networking.process_networking_query(query)
        print(f"💬 Response: {response[:200]}...")
    
    # Test mentor matching
    print(f"\n🎯 Testing mentor matching:")
    request_id = networking.create_networking_request(
        requester_id=mentee.user_id,
        topic="CS 25100 help",
        description="Need study strategies and project advice",
        criteria={'track': 'SE', 'min_year_level': 'junior'},
        urgency="medium"
    )
    
    if request_id:
        print(f"✅ Created networking request: {request_id}")
        
        match = networking.match_request_with_mentor(request_id)
        if match:
            print(f"🎉 Successfully matched with mentor: {match['mentor']['user_id']}")
            print(f"📋 Connection ID: {match['connection_id']}")
        else:
            print("❌ No suitable mentors found")
    
    print(f"\n📊 System Statistics:")
    print(f"Total connections for mentee: {len(networking.get_user_connections(mentee.user_id))}")

if __name__ == "__main__":
    demo_networking_system()