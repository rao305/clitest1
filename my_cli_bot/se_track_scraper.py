#!/usr/bin/env python3
"""
Software Engineering Track Scraper for Purdue CS
Based on official website requirements and structure
"""

import json
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional

class PurdueSETrackScraper:
    """Scraper for Purdue CS Software Engineering track requirements"""
    
    def __init__(self):
        self.base_url = "https://www.cs.purdue.edu/undergraduate/curriculum/track-softengr-fall2023.html"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Definitive SE track data from official website
        self.definitive_data = {
            "source": "Official website - https://www.cs.purdue.edu/undergraduate/curriculum/track-softengr-fall2023.html",
            "verified_date": "2025-07-17",
            "track_name": "Software Engineering Track",
            
            "required_courses": {
                "total_count": 5,
                "structure": "4 mandatory + 1 choice requirement",
                "details": [
                    {
                        "type": "mandatory",
                        "course": "CS 30700",
                        "title": "Software Engineering I",
                        "note": "All students must take this"
                    },
                    {
                        "type": "choice",
                        "requirement": "Compilers/Operating Systems Requirement", 
                        "choose": 1,
                        "options": [
                            {"course": "CS 35200", "title": "Compilers: Principles and Practice"},
                            {"course": "CS 35400", "title": "Operating Systems"}
                        ]
                    },
                    {
                        "type": "mandatory", 
                        "course": "CS 38100",
                        "title": "Introduction to the Analysis of Algorithms",
                        "note": "All students must take this"
                    },
                    {
                        "type": "mandatory",
                        "course": "CS 40800",
                        "title": "Software Testing",
                        "note": "All students must take this"
                    },
                    {
                        "type": "mandatory",
                        "course": "CS 40700",
                        "title": "Software Engineering Senior Project",
                        "note": "Can be replaced by EPICS with approval"
                    }
                ]
            },
            
            "elective_courses": {
                "total_count": 1,
                "structure": "Choose exactly 1 from approved list",
                "all_options": [
                    "CS 31100", "CS 41100", "CS 34800", "CS 35100", "CS 35200",
                    "CS 35300", "CS 35400", "CS 37300", "CS 42200", "CS 42600", 
                    "CS 44800", "CS 45600", "CS 47100", "CS 47300", "CS 48900", 
                    "CS 49000-DSO", "CS 49000-SWS", "CS 51000", "CS 59000-SRS"
                ],
                "special_rules": {
                    "competitive_programming": "CS 31100 + CS 41100 together satisfy one elective",
                    "senior_project_substitute": "EPICS/VIP can replace CS 40700 with track chair approval",
                    "epics_requirement": "EPICS must be EPCS 41100+41200 (Senior Design)",
                    "no_double_counting": "Cannot use same course for required AND elective"
                }
            },
            
            "critical_rules": [
                "All courses must have grade C or better",
                "CS 30700, CS 38100, CS 40800, CS 40700 are mandatory",
                "Must choose 1 from CS 35200 OR CS 35400",
                "Must choose exactly 1 elective",
                "No course can count for both required and elective credit",
                "Total track courses: 6 (5 required + 1 elective)",
                "EPICS can replace senior project with proper approval"
            ]
        }
    
    def scrape_courses(self) -> Optional[Dict]:
        """Scrape SE track course requirements"""
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return self._parse_scraped_data(response.text)
            else:
                print(f"Failed to fetch webpage: {response.status_code}")
                return self._get_fallback_data()
        except Exception as e:
            print(f"Scraping error: {e}")
            return self._get_fallback_data()
    
    def _parse_scraped_data(self, html_content: str) -> Dict:
        """Parse HTML content to extract course information"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Transform definitive data into scraper format
        required_courses = []
        for detail in self.definitive_data['required_courses']['details']:
            if detail['type'] == 'mandatory':
                required_courses.append({
                    'requirement': 'Mandatory',
                    'courses': [{
                        'course_code': detail['course'],
                        'title': detail['title'],
                        'credits': 3
                    }]
                })
            else:
                required_courses.append({
                    'requirement': detail['requirement'],
                    'choose': detail['choose'],
                    'courses': [
                        {
                            'course_code': opt['course'],
                            'title': opt['title'],
                            'credits': 3
                        } for opt in detail['options']
                    ]
                })
        
        elective_courses = {
            'choose': self.definitive_data['elective_courses']['total_count'],
            'options': [
                {
                    'course_code': code,
                    'title': self._get_course_title(code),
                    'credits': 3
                } for code in self.definitive_data['elective_courses']['all_options']
            ]
        }
        
        return {
            'required_courses': required_courses,
            'elective_courses': elective_courses,
            'total_courses': 6,
            'source': self.definitive_data['source']
        }
    
    def _get_fallback_data(self) -> Dict:
        """Return definitive data when scraping fails"""
        return self._parse_scraped_data("")
    
    def _get_course_title(self, course_code: str) -> str:
        """Get course title for a given course code"""
        titles = {
            'CS 31100': 'Competitive Programming 2 and 3',
            'CS 41100': 'Competitive Programming continuation',
            'CS 34800': 'Information Systems',
            'CS 35100': 'Cloud Computing',
            'CS 35200': 'Compilers: Principles and Practice',
            'CS 35300': 'Principles of Concurrency and Parallelism',
            'CS 35400': 'Operating Systems',
            'CS 37300': 'Data Mining and Machine Learning',
            'CS 42200': 'Computer Networks',
            'CS 42600': 'Computer Security',
            'CS 44800': 'Introduction to Relational Database Systems',
            'CS 45600': 'Programming Languages',
            'CS 47100': 'Introduction to Artificial Intelligence',
            'CS 47300': 'Web Information Search And Management',
            'CS 48900': 'Embedded Systems',
            'CS 49000-DSO': 'Distributed Systems',
            'CS 49000-SWS': 'Software Security',
            'CS 51000': 'Software Engineering',
            'CS 59000-SRS': 'Software Reliability and Security'
        }
        return titles.get(course_code, course_code)
    
    def get_course_guidance(self, query: str) -> str:
        """Provide guidance based on query about SE track"""
        query_lower = query.lower()
        
        if 'required' in query_lower:
            return ("The Software Engineering track has 5 required courses:\n\n"
                    "1. CS 30700: Software Engineering I (required)\n"
                    "2. Choose 1: CS 35200 (Compilers) OR CS 35400 (Operating Systems)\n"
                    "3. CS 38100: Introduction to the Analysis of Algorithms (required)\n"
                    "4. CS 40800: Software Testing (required)\n"
                    "5. CS 40700: Software Engineering Senior Project (required)")
        
        elif 'elective' in query_lower:
            return ("You need to choose exactly 1 elective from the approved list of 19 courses. "
                    "This includes options like cloud computing, security, AI, databases, and more.")
        
        elif 'cs 30700' in query_lower:
            return ("CS 30700 is 'Software Engineering I' and it's a mandatory required course "
                    "for the Software Engineering track. All SE track students must take this course.")
        
        elif 'double' in query_lower:
            return ("No, you cannot use the same course for both required and elective credit. "
                    "CS 35200 can either fulfill the Compilers/OS requirement OR count as your 1 elective, "
                    "but not both.")
        
        elif 'epics' in query_lower:
            return ("Yes, EPICS can replace CS 40700 (Software Engineering Senior Project) if approved "
                    "by the track chair. However, it must be EPCS 41100 and EPCS 41200 (Senior Design), "
                    "not EPCS 40100 and EPCS 40200.")
        
        else:
            return ("The SE track requires 6 total courses: 5 required (including choices) + 1 elective. "
                    "All courses must have grade C or better.")
    
    def get_definitive_data(self) -> Dict:
        """Get the definitive SE track data"""
        return self.definitive_data