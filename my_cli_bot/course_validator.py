#!/usr/bin/env python3
"""
Course Validator for Purdue CS Machine Intelligence Track
Validates course selections against official requirements
"""

from typing import Dict, List, Set

class MITrackValidator:
    """Validator for Machine Intelligence track course requirements"""
    
    def __init__(self):
        # Updated to match actual requirements from official website
        self.mandatory_courses = ["CS 37300", "CS 38100"]
        self.ai_requirement = ["CS 47100", "CS 47300"]  # Choose 1
        self.stats_requirement = ["STAT 41600", "MA 41600", "STAT 51200"]  # Choose 1
        
        self.elective_options = [
            "CS 31100", "CS 41100", "CS 31400", "CS 34800", "CS 35200",
            "CS 44800", "CS 45600", "CS 45800", "CS 47100", "CS 47300", 
            "CS 48300", "CS 43900", "CS 44000", "CS 47500", "CS 57700", "CS 57800"
        ]
        
        # Special elective group - can only choose one from this group
        self.data_viz_group = ["CS 43900", "CS 44000", "CS 47500"]
        
        # Competitive programming special case
        self.competitive_programming = ["CS 31100", "CS 41100"]
    
    def validate_course_plan(self, selected_courses: List[str]) -> Dict:
        """Validate if course selection meets track requirements"""
        errors = []
        warnings = []
        
        # Check mandatory courses
        for required in self.mandatory_courses:
            if required not in selected_courses:
                errors.append(f"Missing required course: {required}")
        
        # Check AI requirement (choose 1)
        ai_selected = [c for c in selected_courses if c in self.ai_requirement]
        if len(ai_selected) == 0:
            errors.append(f"Must select 1 from AI requirement: {self.ai_requirement}")
        elif len(ai_selected) > 1:
            warnings.append("Multiple AI courses selected, only one needed for requirement")
            
        # Check stats requirement (choose 1)
        stats_selected = [c for c in selected_courses if c in self.stats_requirement]
        if len(stats_selected) == 0:
            errors.append(f"Must select 1 from statistics requirement: {self.stats_requirement}")
        elif len(stats_selected) > 1:
            warnings.append("Multiple statistics courses selected, only one needed for requirement")
        
        # Check electives
        selected_electives = [c for c in selected_courses if c in self.elective_options]
        
        # Remove courses already used for requirements to avoid double counting
        used_for_required = []
        used_for_required.extend([c for c in selected_courses if c in self.mandatory_courses])
        used_for_required.extend(ai_selected)
        used_for_required.extend(stats_selected)
        
        actual_electives = [c for c in selected_electives if c not in used_for_required]
        
        # Check for double-counting
        double_counted = set(used_for_required) & set(actual_electives)
        if double_counted:
            errors.append(f"Courses cannot count for both required and elective: {list(double_counted)}")
        
        # Check data visualization group constraint
        data_viz_selected = [c for c in actual_electives if c in self.data_viz_group]
        if len(data_viz_selected) > 1:
            errors.append(f"Can only choose ONE from data visualization group {self.data_viz_group}, but selected: {data_viz_selected}")
        
        # Check elective count
        if len(actual_electives) < 2:
            errors.append(f"Must select 2 electives, currently have {len(actual_electives)}: {actual_electives}")
        elif len(actual_electives) > 2:
            warnings.append(f"More than 2 electives selected: {actual_electives}")
            
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "summary": {
                "mandatory_completed": [c for c in self.mandatory_courses if c in selected_courses],
                "ai_requirement": ai_selected,
                "stats_requirement": stats_selected,
                "electives": actual_electives,
                "total_courses": len(used_for_required) + len(actual_electives)
            }
        }
    
    def get_available_courses(self, completed_courses: List[str]) -> Dict:
        """Get available courses based on completed prerequisites"""
        available = {
            "mandatory": [c for c in self.mandatory_courses if c not in completed_courses],
            "ai_options": [c for c in self.ai_requirement if c not in completed_courses],
            "stats_options": [c for c in self.stats_requirement if c not in completed_courses],
            "electives": [c for c in self.elective_options if c not in completed_courses]
        }
        
        return available
    
    def get_track_requirements(self) -> Dict:
        """Get complete track requirements"""
        return {
            "mandatory_courses": self.mandatory_courses,
            "ai_requirement": {
                "choose": 1,
                "options": self.ai_requirement
            },
            "stats_requirement": {
                "choose": 1,
                "options": self.stats_requirement
            },
            "electives": {
                "choose": 2,
                "options": self.elective_options,
                "special_rules": {
                    "data_viz_group": self.data_viz_group,
                    "competitive_programming": self.competitive_programming
                }
            },
            "total_courses": 6
        }