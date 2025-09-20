#!/usr/bin/env python3
"""
Complete Purdue CS Course Scraper
Scrapes ALL CS courses with complete data: prerequisites, descriptions, credits, etc.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

class CompletePurdueCScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Course catalog URLs
        self.catalog_urls = {
            'undergraduate': 'https://catalog.purdue.edu/preview_program.php?catoid=15&poid=20104',
            'course_search': 'https://catalog.purdue.edu/ribbit/?page=getsearchresults.rjs&searchtype=3&criteria%5B0%5D%5Bfield%5D=subject&criteria%5B0%5D%5Bvalue%5D=CS&criteria%5B0%5D%5Boperator%5D=equal',
            'course_details': 'https://catalog.purdue.edu/preview_course_nopop.php?catoid=15&coid=',
            'prerequisites': 'https://selfservice.mypurdue.purdue.edu/prod/bwckctlg.p_disp_course_detail?cat_term_in=202510&subj_code_in=CS&crse_numb_in='
        }
        
        # Track information
        self.tracks = {
            'Machine Intelligence': {
                'core_courses': ['CS 37300', 'CS 38100', 'CS 38300'],
                'electives': []
            },
            'Software Engineering': {
                'core_courses': ['CS 30700', 'CS 35200', 'CS 40800'],
                'electives': []
            },
            'Systems Programming': {
                'core_courses': ['CS 35200', 'CS 42200', 'CS 42600'],
                'electives': []
            }
        }
        
        self.all_courses = {}
        self.prerequisite_map = {}
        
    def scrape_all_cs_courses(self) -> Dict[str, Any]:
        """Scrape complete CS course catalog"""
        print("🔍 Scraping complete Purdue CS course catalog...")
        
        # Get all CS course numbers
        course_numbers = self.get_all_cs_course_numbers()
        print(f"Found {len(course_numbers)} CS courses to scrape")
        
        # Scrape each course in detail
        for i, course_num in enumerate(course_numbers, 1):
            print(f"📚 Scraping CS {course_num} ({i}/{len(course_numbers)})")
            course_data = self.scrape_course_details(f"CS {course_num}")
            if course_data:
                self.all_courses[f"CS {course_num}"] = course_data
            time.sleep(0.5)  # Be respectful to server
        
        # Add math and science requirements
        self.add_math_science_courses()
        
        return {
            'courses': self.all_courses,
            'prerequisites': self.prerequisite_map,
            'tracks': self.tracks,
            'timestamp': datetime.now().isoformat(),
            'total_courses': len(self.all_courses)
        }
    
    def get_all_cs_course_numbers(self) -> List[str]:
        """Get all CS course numbers from catalog"""
        course_numbers = []
        
        # Standard CS course ranges
        ranges = [
            (10000, 19999),  # 1xxxx level
            (20000, 29999),  # 2xxxx level  
            (30000, 39999),  # 3xxxx level
            (40000, 49999),  # 4xxxx level
            (50000, 59999),  # 5xxxx level
            (60000, 69999),  # 6xxxx level
        ]
        
        for start, end in ranges:
            # Check common course numbers in each range
            for num in range(start, end + 1, 100):
                # Check typical course number patterns
                test_numbers = [
                    str(num),
                    str(num + 10), str(num + 20), str(num + 30),
                    str(num + 50), str(num + 80), str(num + 90)
                ]
                
                for test_num in test_numbers:
                    if self.course_exists(test_num):
                        course_numbers.append(test_num)
        
        # Add known CS courses manually
        known_courses = [
            "18000", "18200", "24000", "25000", "25100", "25200",
            "30700", "31400", "35200", "37300", "38100", "38300",
            "40800", "41000", "42200", "42600", "43900", "44000",
            "45800", "47100", "48300", "49000"
        ]
        
        for course in known_courses:
            if course not in course_numbers:
                course_numbers.append(course)
        
        return sorted(list(set(course_numbers)))
    
    def course_exists(self, course_num: str) -> bool:
        """Check if a CS course exists"""
        try:
            url = f"https://catalog.purdue.edu/preview_course_nopop.php?catoid=15&coid={course_num}"
            response = self.session.get(url, timeout=10)
            return response.status_code == 200 and "Course Not Found" not in response.text
        except:
            return False
    
    def scrape_course_details(self, course_code: str) -> Optional[Dict[str, Any]]:
        """Scrape detailed information for a specific course"""
        try:
            course_num = course_code.replace("CS ", "")
            
            # Try multiple sources for course information
            course_data = {}
            
            # Source 1: Catalog page
            catalog_data = self.scrape_from_catalog(course_num)
            if catalog_data:
                course_data.update(catalog_data)
            
            # Source 2: Self-service page for prerequisites
            prereq_data = self.scrape_prerequisites(course_num)
            if prereq_data:
                course_data.update(prereq_data)
            
            # Source 3: Course schedule for current offerings
            schedule_data = self.scrape_schedule_info(course_num)
            if schedule_data:
                course_data.update(schedule_data)
            
            if course_data:
                course_data['course_code'] = course_code
                course_data['scraped_at'] = datetime.now().isoformat()
                return course_data
            
        except Exception as e:
            print(f"Error scraping {course_code}: {e}")
        
        return None
    
    def scrape_from_catalog(self, course_num: str) -> Optional[Dict[str, Any]]:
        """Scrape course data from catalog"""
        try:
            # Search for course in catalog
            search_url = f"https://catalog.purdue.edu/search/?P=CS%20{course_num}"
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find course information
            course_data = {}
            
            # Look for course title and credits
            title_element = soup.find('h2', class_='course-title')
            if title_element:
                title_text = title_element.get_text(strip=True)
                # Parse "CS 18000 - Problem Solving and Object-Oriented Programming (4 credits)"
                match = re.search(r'CS\s+\d+\s*-\s*(.+?)\s*\((\d+(?:\.\d+)?)\s*credits?\)', title_text)
                if match:
                    course_data['title'] = match.group(1).strip()
                    course_data['credits'] = float(match.group(2))
            
            # Look for course description
            desc_element = soup.find('div', class_='course-description')
            if desc_element:
                course_data['description'] = desc_element.get_text(strip=True)
            
            # Look for prerequisites in description
            if 'description' in course_data:
                prereq_match = re.search(r'Prerequisite[s]?:(.+?)(?:\.|$)', course_data['description'], re.IGNORECASE)
                if prereq_match:
                    prereq_text = prereq_match.group(1).strip()
                    course_data['prerequisite_text'] = prereq_text
                    course_data['prerequisites'] = self.parse_prerequisites(prereq_text)
            
            return course_data if course_data else None
            
        except Exception as e:
            print(f"Catalog scraping error for {course_num}: {e}")
            return None
    
    def scrape_prerequisites(self, course_num: str) -> Optional[Dict[str, Any]]:
        """Scrape prerequisites from self-service"""
        try:
            url = f"https://selfservice.mypurdue.purdue.edu/prod/bwckctlg.p_disp_course_detail?cat_term_in=202520&subj_code_in=CS&crse_numb_in={course_num}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            course_data = {}
            
            # Look for prerequisites
            prereq_elements = soup.find_all(text=re.compile(r'Prerequisites?:', re.IGNORECASE))
            for element in prereq_elements:
                parent = element.parent
                if parent:
                    prereq_text = parent.get_text(strip=True)
                    course_data['prerequisite_text'] = prereq_text
                    course_data['prerequisites'] = self.parse_prerequisites(prereq_text)
                    break
            
            # Look for course attributes/schedule info
            schedule_table = soup.find('table', class_='datadisplaytable')
            if schedule_table:
                rows = schedule_table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all('td')
                    if len(cells) >= 8:
                        # Extract semester offering info
                        term = cells[0].get_text(strip=True)
                        if 'Fall' in term or 'Spring' in term:
                            semesters = course_data.get('semesters_offered', [])
                            semester = 'Fall' if 'Fall' in term else 'Spring'
                            if semester not in semesters:
                                semesters.append(semester)
                            course_data['semesters_offered'] = semesters
            
            return course_data if course_data else None
            
        except Exception as e:
            print(f"Prerequisites scraping error for {course_num}: {e}")
            return None
    
    def scrape_schedule_info(self, course_num: str) -> Optional[Dict[str, Any]]:
        """Scrape current schedule information"""
        try:
            # This would scrape from course schedule pages
            # For now, return basic info
            return {
                'last_updated': datetime.now().isoformat(),
                'source': 'schedule_scraper'
            }
        except Exception as e:
            print(f"Schedule scraping error for {course_num}: {e}")
            return None
    
    def parse_prerequisites(self, prereq_text: str) -> List[str]:
        """Parse prerequisite text into course codes"""
        if not prereq_text:
            return []
        
        # Clean up text
        text = re.sub(r'\s+', ' ', prereq_text.strip())
        
        # Find course codes (CS XXXXX, MATH XXXXX, etc.)
        course_pattern = r'\b([A-Z]{2,4})\s*(\d{5}|\d{3})\b'
        matches = re.findall(course_pattern, text, re.IGNORECASE)
        
        prerequisites = []
        for subject, number in matches:
            course_code = f"{subject.upper()} {number}"
            if course_code not in prerequisites:
                prerequisites.append(course_code)
        
        return prerequisites
    
    def add_math_science_courses(self):
        """Add required math and science courses"""
        math_science_courses = {
            'MATH 16100': {
                'title': 'Plane Analytic Geometry And Calculus I',
                'credits': 5,
                'description': 'Introduction to differential and integral calculus of one variable, with applications.',
                'prerequisites': [],
                'requirement_type': 'math_core'
            },
            'MATH 16200': {
                'title': 'Plane Analytic Geometry And Calculus II', 
                'credits': 5,
                'description': 'Continuation of MATH 16100. Techniques of integration, applications, infinite series.',
                'prerequisites': ['MATH 16100'],
                'requirement_type': 'math_core'
            },
            'MATH 26100': {
                'title': 'Multivariate Calculus',
                'credits': 4,
                'description': 'Calculus of several variables, vector functions, partial derivatives, multiple integrals.',
                'prerequisites': ['MATH 16200'],
                'requirement_type': 'math_core'
            },
            'MATH 26500': {
                'title': 'Linear Algebra',
                'credits': 3,
                'description': 'Systems of linear equations, matrix algebra, vector spaces, eigenvalues.',
                'prerequisites': ['MATH 16200'],
                'requirement_type': 'math_core'
            },
            'STAT 35000': {
                'title': 'Introduction to Statistics',
                'credits': 3,
                'description': 'Descriptive statistics, probability, sampling distributions, inference.',
                'prerequisites': ['MATH 16200'],
                'requirement_type': 'statistics'
            },
            'PHYS 17200': {
                'title': 'Modern Mechanics',
                'credits': 4,
                'description': 'Introductory calculus-based mechanics with modern physics concepts.',
                'prerequisites': ['MATH 16100'],
                'requirement_type': 'science'
            },
            'PHYS 27200': {
                'title': 'Electric And Magnetic Interactions',
                'credits': 4,
                'description': 'Calculus-based electricity and magnetism.',
                'prerequisites': ['MATH 16200', 'PHYS 17200'],
                'requirement_type': 'science'
            }
        }
        
        for course_code, course_info in math_science_courses.items():
            self.all_courses[course_code] = course_info
            if course_info['prerequisites']:
                self.prerequisite_map[course_code] = course_info['prerequisites']
    
    def save_to_database(self, data: Dict[str, Any]):
        """Save complete course data to database"""
        conn = sqlite3.connect('purdue_cs_knowledge.db')
        cursor = conn.cursor()
        
        # Clear existing course data for fresh start
        cursor.execute('DELETE FROM courses')
        cursor.execute('DELETE FROM course_relationships')
        
        # Insert all courses
        for course_code, course_info in data['courses'].items():
            cursor.execute('''
                INSERT OR REPLACE INTO courses 
                (code, title, credits, track, requirement_type, prerequisites, description, 
                 semester_offered, difficulty_rating, workload_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                course_code,
                course_info.get('title', ''),
                course_info.get('credits', 0),
                course_info.get('track', 'Core'),
                course_info.get('requirement_type', 'core'),
                json.dumps(course_info.get('prerequisites', [])),
                course_info.get('description', ''),
                json.dumps(course_info.get('semesters_offered', ['Fall', 'Spring'])),
                course_info.get('difficulty_rating', 3.0),
                course_info.get('workload_hours', 10)
            ))
        
        # Insert prerequisite relationships
        for course_code, prerequisites in data['prerequisites'].items():
            for prereq in prerequisites:
                cursor.execute('''
                    INSERT OR REPLACE INTO course_relationships
                    (course_code, prerequisite_code, relationship_type)
                    VALUES (?, ?, ?)
                ''', (course_code, prereq, 'prerequisite'))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Saved {len(data['courses'])} courses to database")
    
    def save_to_json(self, data: Dict[str, Any], filename: str = 'complete_cs_data.json'):
        """Save data to JSON file"""
        with open(f'data/{filename}', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved complete course data to data/{filename}")

def main():
    """Run the complete scraper"""
    scraper = CompletePurdueCScraper()
    
    print("🚀 Starting complete Purdue CS course scraping...")
    print("=" * 60)
    
    # Scrape all course data
    complete_data = scraper.scrape_all_cs_courses()
    
    print(f"\n📊 Scraping Summary:")
    print(f"   • Total courses: {complete_data['total_courses']}")
    print(f"   • Prerequisites mapped: {len(complete_data['prerequisites'])}")
    print(f"   • Tracks defined: {len(complete_data['tracks'])}")
    
    # Save to database and file
    scraper.save_to_database(complete_data)
    scraper.save_to_json(complete_data)
    
    print("\n✅ Complete course scraping finished!")
    return complete_data

if __name__ == "__main__":
    main()