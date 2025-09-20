#!/usr/bin/env python3
"""
Course Validator for Purdue CS Software Engineering Track
Validates course selections against official requirements
"""

from typing import Dict, List, Set

class SETrackValidator:
    """Validator for Software Engineering track course requirements"""
    
    def __init__(self):
        # SE Track structure based on official website screenshots
        self.mandatory_courses = ["CS 30700", "CS 38100", "CS 40800", "CS 40700"]
        self.compilers_os_requirement = ["CS 35200", "CS 35400"]  # Choose 1
        
        self.elective_options = [
            "CS 31100", "CS 41100", "CS 34800", "CS 35100", "CS 35200",
            "CS 35300", "CS 35400", "CS 37300", "CS 42200", "CS 42600", 
            "CS 44800", "CS 45600", "CS 47100", "CS 47300", "CS 48900", 
            "CS 49000-DSO", "CS 49000-SWS", "CS 51000", "CS 59000-SRS"
        ]
        
        # Competitive programming special case
        self.competitive_programming = ["CS 31100", "CS 41100"]
    
    def validate_course_plan(self, selected_courses: List[str]) -> Dict:
        """Validate if course selection meets SE track requirements"""
        errors = []
        warnings = []
        
        # Check mandatory courses
        for required in self.mandatory_courses:
            if required not in selected_courses:
                errors.append(f"Missing required course: {required}")
        
        # Check compilers/OS requirement (choose 1)
        compilers_os_selected = [c for c in selected_courses if c in self.compilers_os_requirement]
        if len(compilers_os_selected) == 0:
            errors.append(f"Must select 1 from Compilers/OS requirement: {self.compilers_os_requirement}")
        elif len(compilers_os_selected) > 1:
            warnings.append("Multiple Compilers/OS courses selected, only one needed for requirement")
            
        # Check electives
        selected_electives = [c for c in selected_courses if c in self.elective_options]
        
        # Remove courses already used for requirements to avoid double counting
        used_for_required = []
        used_for_required.extend([c for c in selected_courses if c in self.mandatory_courses])
        used_for_required.extend(compilers_os_selected)
        
        actual_electives = [c for c in selected_electives if c not in used_for_required]
        
        # Check for double-counting
        double_counted = set(used_for_required) & set(actual_electives)
        if double_counted:
            errors.append(f"Courses cannot count for both required and elective: {list(double_counted)}")
        
        # Check elective count
        if len(actual_electives) < 1:
            errors.append(f"Must select 1 elective, currently have {len(actual_electives)}: {actual_electives}")
        elif len(actual_electives) > 1:
            warnings.append(f"More than 1 elective selected: {actual_electives}")
            
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "summary": {
                "mandatory_completed": [c for c in self.mandatory_courses if c in selected_courses],
                "compilers_os_requirement": compilers_os_selected,
                "electives": actual_electives,
                "total_courses": len(used_for_required) + len(actual_electives)
            }
        }
    
    def get_available_courses(self, completed_courses: List[str]) -> Dict:
        """Get available courses based on completed prerequisites"""
        available = {
            "mandatory": [c for c in self.mandatory_courses if c not in completed_courses],
            "compilers_os_options": [c for c in self.compilers_os_requirement if c not in completed_courses],
            "electives": [c for c in self.elective_options if c not in completed_courses]
        }
        
        return available
    
    def get_track_requirements(self) -> Dict:
        """Get complete track requirements"""
        return {
            "mandatory_courses": self.mandatory_courses,
            "compilers_os_requirement": {
                "choose": 1,
                "options": self.compilers_os_requirement
            },
            "electives": {
                "choose": 1,
                "options": self.elective_options,
                "special_rules": {
                    "competitive_programming": self.competitive_programming,
                    "epics_substitution": "EPICS can replace CS 40700 with approval"
                }
            },
            "total_courses": 6
        }
    
    def get_elective_recommendations(self, interests: List[str]) -> List[str]:
        """Recommend SE electives based on student interests"""
        recommendations = {
            "security": ["CS 42600", "CS 49000-SWS", "CS 59000-SRS"],
            "ai": ["CS 47100", "CS 37300", "CS 47300"],
            "systems": ["CS 35400", "CS 48900", "CS 49000-DSO"],
            "databases": ["CS 44800"],
            "networking": ["CS 42200"],
            "cloud": ["CS 35100"],
            "languages": ["CS 45600", "CS 35200"],
            "advanced_se": ["CS 51000"],
            "parallel": ["CS 35300"]
        }
        
        suggested = []
        for interest in interests:
            if interest.lower() in recommendations:
                suggested.extend(recommendations[interest.lower()])
        
        # Remove duplicates and return
        return list(set(suggested))