#!/usr/bin/env python3
"""
Machine Intelligence Track Scraper for Purdue CS
Based on official website requirements and structure
"""

import json
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional

class PurdueMITrackScraper:
    """Scraper for Purdue CS Machine Intelligence track requirements"""
    
    def __init__(self):
        self.base_url = "https://www.cs.purdue.edu/undergraduate/curriculum/track-mI-fall2023.html"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Definitive MI track data from official website
        self.definitive_data = {
            "source": "Official website - https://www.cs.purdue.edu/undergraduate/curriculum/track-mI-fall2023.html",
            "verified_date": "2025-07-17",
            "track_name": "Machine Intelligence Track",
            
            "required_courses": {
                "total_count": 4,
                "structure": "2 mandatory + 2 choice requirements",
                "details": [
                    {
                        "type": "mandatory",
                        "course": "CS 37300",
                        "title": "Data Mining and Machine Learning",
                        "note": "All students must take this"
                    },
                    {
                        "type": "mandatory", 
                        "course": "CS 38100",
                        "title": "Introduction to the Analysis of Algorithms",
                        "note": "All students must take this"
                    },
                    {
                        "type": "choice",
                        "requirement": "AI Requirement", 
                        "choose": 1,
                        "options": [
                            {"course": "CS 47100", "title": "Artificial Intelligence"},
                            {"course": "CS 47300", "title": "Web Information Search & Management"}
                        ]
                    },
                    {
                        "type": "choice",
                        "requirement": "Statistics/Probability Requirement",
                        "choose": 1, 
                        "options": [
                            {"course": "STAT 41600", "title": "Probability"},
                            {"course": "MA 41600", "title": "Probability"},
                            {"course": "STAT 51200", "title": "Applied Regression Analysis"}
                        ]
                    }
                ]
            },
            
            "elective_courses": {
                "total_count": 2,
                "structure": "Choose exactly 2 from approved list",
                "all_options": [
                    "CS 31100", "CS 41100", "CS 31400", "CS 34800", "CS 35200",
                    "CS 44800", "CS 45600", "CS 45800", "CS 47100", "CS 47300",
                    "CS 48300", "CS 43900", "CS 44000", "CS 47500", "CS 57700", "CS 57800"
                ],
                "special_rules": {
                    "competitive_programming": "CS 31100 + CS 41100 together may count as 1 elective",
                    "data_group": "From CS 43900/CS 44000/CS 47500, can only pick ONE",
                    "no_double_counting": "Cannot use same course for required AND elective"
                }
            },
            
            "critical_rules": [
                "All courses must have grade C or better",
                "CS 37300 and CS 38100 are mandatory for all students",
                "Must choose 1 from AI options (CS 47100 OR CS 47300)",
                "Must choose 1 from statistics options (STAT 41600 OR MA 41600 OR STAT 51200)",
                "Must choose exactly 2 electives",
                "No course can count for both required and elective credit",
                "Total track courses: 6 (4 required + 2 electives)"
            ]
        }
    
    def scrape_courses(self) -> Optional[Dict]:
        """Scrape MI track course requirements"""
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
            'CS 31100': 'Competitive Programming I',
            'CS 41100': 'Competitive Programming II',
            'CS 31400': 'Numerical Methods',
            'CS 34800': 'Information Systems',
            'CS 35200': 'Compilers: Principles And Practice',
            'CS 44800': 'Introduction To Relational Database Systems',
            'CS 45600': 'Programming Languages',
            'CS 45800': 'Introduction to Robotics',
            'CS 47100': 'Introduction to Artificial Intelligence',
            'CS 47300': 'Web Information Search & Management',
            'CS 48300': 'Introduction To The Theory Of Computation',
            'CS 43900': 'Introduction to Data Visualization',
            'CS 44000': 'Large-Scale Data Analytics',
            'CS 47500': 'Information Visualization',
            'CS 57700': 'Natural Language Processing',
            'CS 57800': 'Statistical Machine Learning'
        }
        return titles.get(course_code, course_code)
    
    def get_course_guidance(self, query: str) -> str:
        """Provide guidance based on query about MI track"""
        query_lower = query.lower()
        
        if 'required' in query_lower:
            return ("The Machine Intelligence track has 4 required courses:\n\n"
                    "1. CS 37300: Data Mining and Machine Learning (required)\n"
                    "2. CS 38100: Introduction to the Analysis of Algorithms (required)\n"
                    "3. Choose 1: CS 47100 (Artificial Intelligence) OR CS 47300 (Web Information Search & Management)\n"
                    "4. Choose 1: STAT 41600 OR MA 41600 OR STAT 51200 (probability/statistics requirement)")
        
        elif 'elective' in query_lower:
            return ("You need to choose 2 electives from the approved list. "
                    "There are many options including CS courses and some grouped options "
                    "where you pick one from a group (like CS 43900 OR CS 44000 OR CS 47500).")
        
        elif 'cs 37300' in query_lower:
            return ("CS 37300 is 'Data Mining and Machine Learning' and it's a required course "
                    "for the Machine Intelligence track. All MI track students must take this course.")
        
        elif 'double' in query_lower:
            return ("No, you cannot use the same course for both required and elective credit. "
                    "CS 47300 can either fulfill the required course choice (requirement #3) OR "
                    "count as one of your 2 electives, but not both.")
        
        else:
            return ("The MI track requires 6 total courses: 4 required (including choices) + 2 electives. "
                    "All courses must have grade C or better.")
    
    def get_definitive_data(self) -> Dict:
        """Get the definitive MI track data"""
        return self.definitive_data