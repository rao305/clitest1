"""
Summer Acceleration Calculator - Strategic summer course planning for CS students
"""
from typing import Dict, List, Tuple, Optional
from degree_progression_engine import DegreeProgressionEngine

class SummerAccelerationCalculator:
    def __init__(self):
        self.engine = DegreeProgressionEngine()
        
        # Summer course offering patterns (based on typical Purdue schedule)
        self.summer_offerings = {
            "commonly_offered": [
                "CS 18000", "CS 18200", "CS 24000", "CS 25100",
                "MA 16100", "MA 16200", "MA 26100", "MA 26500",
                "STAT 35000"
            ],
            "sometimes_offered": [
                "CS 25000", "CS 25200", "CS 38100", "CS 37300"
            ],
            "rarely_offered": [
                "CS 30700", "CS 40800", "Most track electives"
            ]
        }
        
        # Summer course intensity ratings
        self.intensity_ratings = {
            "CS 18000": "very_high",  # First programming course
            "CS 18200": "high",       # Mathematical foundations  
            "CS 24000": "medium",     # C programming
            "CS 25000": "high",       # Computer architecture
            "CS 25100": "very_high",  # Data structures - most critical
            "CS 25200": "very_high",  # Systems programming
            "CS 38100": "high",       # Algorithms
            "CS 37300": "high",       # Machine learning
            "MA 16100": "high",       # Calculus I
            "MA 16200": "high",       # Calculus II  
            "MA 26100": "medium",     # Multivariable calculus
            "MA 26500": "medium",     # Linear algebra
            "STAT 35000": "low"       # Statistics
        }
        
    def calculate_acceleration_plan(self, student_profile: Dict) -> Dict:
        """Calculate optimal summer acceleration strategy"""
        current_year = student_profile.get("year_level", "freshman")
        current_semester = student_profile.get("current_semester", "spring")
        completed_courses = student_profile.get("completed_courses", [])
        gpa = student_profile.get("gpa", 3.0)
        goal = student_profile.get("graduation_goal", "4_year")  # 3_year, 3.5_year, 4_year
        
        plan = {
            "student_profile": student_profile,
            "acceleration_feasible": True,
            "recommended_strategy": "",
            "summer_options": [],
            "risks": [],
            "alternative_plans": [],
            "success_probability": 0.0
        }
        
        # Determine acceleration strategy based on goal
        if goal == "3_year":
            plan = self._calculate_3_year_plan(current_year, completed_courses, gpa)
        elif goal == "3.5_year":
            plan = self._calculate_3_5_year_plan(current_year, completed_courses, gpa)
        else:
            plan = self._calculate_standard_acceleration(current_year, completed_courses, gpa)
            
        return plan
    
    def _calculate_3_year_plan(self, current_year: str, completed_courses: List[str], gpa: float) -> Dict:
        """Calculate 3-year graduation plan (very aggressive)"""
        plan = {
            "acceleration_feasible": False,
            "success_probability": 0.4,
            "recommended_strategy": "3-year graduation (NOT RECOMMENDED for most students)",
            "summer_options": [],
            "risks": [
                "Extremely high course load (20+ credits per semester)",
                "Limited time for internships and practical experience", 
                "High stress and burnout risk",
                "Minimal flexibility for course failures",
                "May require skipping CS 18000 (very risky)"
            ],
            "requirements": [
                "Exceptional programming background before college",
                "Ability to skip CS 18000 with demonstrated competency",
                "20+ credits per semester consistently", 
                "Mandatory summer courses every summer",
                "GPA above 3.5 to handle the load"
            ]
        }
        
        if gpa >= 3.5 and "CS 18000" in completed_courses:
            plan["acceleration_feasible"] = True
            plan["summer_options"] = [
                {
                    "courses": ["CS 18200", "CS 24000", "MA 16200"],
                    "credits": 11,
                    "rationale": "Accelerate foundation sequence",
                    "intensity": "very_high",
                    "summer": "after_freshman_year"
                },
                {
                    "courses": ["CS 25000", "CS 25100", "MA 26100"], 
                    "credits": 11,
                    "rationale": "Complete core sequence early",
                    "intensity": "extremely_high",
                    "summer": "after_sophomore_year"
                }
            ]
        
        return plan
    
    def _calculate_3_5_year_plan(self, current_year: str, completed_courses: List[str], gpa: float) -> Dict:
        """Calculate 3.5-year graduation plan (moderately aggressive)"""
        plan = {
            "acceleration_feasible": True,
            "success_probability": 0.65,
            "recommended_strategy": "3.5-year graduation with strategic summer courses",
            "summer_options": [],
            "risks": [
                "High credit loads (17-18 per semester)",
                "Limited flexibility for setbacks",
                "Reduced time for internships"
            ],
            "requirements": [
                "Strong academic performance (GPA 3.0+)",
                "18+ credits per semester",
                "Summer courses recommended",
                "Efficient track selection"
            ]
        }
        
        if current_year == "freshman":
            plan["summer_options"] = [
                {
                    "courses": ["CS 18200", "MA 16200"],
                    "credits": 8,
                    "rationale": "Get ahead on foundation sequence",
                    "intensity": "high",
                    "summer": "after_freshman_spring"
                }
            ]
        elif current_year == "sophomore":
            plan["summer_options"] = [
                {
                    "courses": ["CS 25100", "STAT 35000"],
                    "credits": 6, 
                    "rationale": "Critical course + statistics requirement",
                    "intensity": "high",
                    "summer": "after_sophomore_spring"
                }
            ]
        elif current_year == "junior":
            plan["summer_options"] = [
                {
                    "courses": ["CS 38100", "Track elective"],
                    "credits": 6,
                    "rationale": "Complete track requirements early",
                    "intensity": "medium",
                    "summer": "after_junior_spring"
                }
            ]
            
        return plan
    
    def _calculate_standard_acceleration(self, current_year: str, completed_courses: List[str], gpa: float) -> Dict:
        """Calculate standard acceleration for catch-up or getting ahead"""
        plan = {
            "acceleration_feasible": True,
            "success_probability": 0.85,
            "recommended_strategy": "Strategic summer courses for flexibility",
            "summer_options": [],
            "risks": ["Intensive summer format may be challenging"],
            "benefits": [
                "Lighter course loads during regular semesters",
                "Flexibility for failures or schedule changes",
                "More time for internships and research",
                "Better work-life balance"
            ]
        }
        
        # Get recommended summer courses based on year
        summer_recs = self.engine.get_summer_acceleration_options(current_year)
        
        for rec in summer_recs:
            course_code = rec["code"]
            
            # Skip if already completed
            if course_code in completed_courses:
                continue
                
            # Check if course is typically offered in summer
            availability = self._get_summer_availability(course_code)
            if availability == "rarely_offered":
                continue
                
            plan["summer_options"].append({
                "course": course_code,
                "reason": rec["reason"],
                "intensity": rec["intensity"],
                "availability": availability,
                "credits": self._get_course_credits(course_code),
                "prerequisites_met": self._check_prerequisites(course_code, completed_courses)
            })
        
        return plan
    
    def _get_summer_availability(self, course_code: str) -> str:
        """Check if course is typically available in summer"""
        if course_code in self.summer_offerings["commonly_offered"]:
            return "commonly_offered"
        elif course_code in self.summer_offerings["sometimes_offered"]:
            return "sometimes_offered"
        else:
            return "rarely_offered"
    
    def _get_course_credits(self, course_code: str) -> int:
        """Get credit hours for course"""
        course_credits = {
            "CS 18000": 4, "CS 18200": 3, "CS 24000": 3,
            "CS 25000": 4, "CS 25100": 3, "CS 25200": 4,
            "CS 38100": 3, "CS 37300": 3,
            "MA 16100": 5, "MA 16200": 5, "MA 26100": 4,
            "MA 26500": 3, "STAT 35000": 3
        }
        return course_credits.get(course_code, 3)
    
    def _check_prerequisites(self, course_code: str, completed_courses: List[str]) -> bool:
        """Check if prerequisites are met for course"""
        prerequisites = self.engine.knowledge.get("prerequisites", {})
        course_prereqs = prerequisites.get(course_code, [])
        
        return all(prereq in completed_courses for prereq in course_prereqs)
    
    def calculate_failure_recovery_summer_plan(self, failed_course: str, student_profile: Dict) -> Dict:
        """Calculate summer recovery plan after course failure"""
        recovery_plan = {
            "failed_course": failed_course,
            "summer_recovery_feasible": False,
            "recovery_options": [],
            "timeline_impact": "",
            "alternative_strategies": []
        }
        
        # Get failure impact data
        failure_impact = self.engine.calculate_failure_impact(failed_course, "current")
        
        if failure_impact.get("summer_recovery_possible", False):
            recovery_plan["summer_recovery_feasible"] = True
            recovery_plan["recovery_options"] = [
                {
                    "strategy": "Immediate Summer Retake",
                    "courses": [failed_course],
                    "timeline": "Next summer session",
                    "benefits": ["Minimize graduation delay", "Fresh start with course material"],
                    "challenges": ["Intensive format", "Limited time to improve weak areas"]
                }
            ]
            
            # Add supplementary courses if possible
            affected_courses = failure_impact.get("affected_courses", [])
            
            # Suggest alternative courses that can be taken while waiting
            alternative_courses = self._get_alternative_summer_courses(failed_course, student_profile)
            if alternative_courses:
                recovery_plan["recovery_options"].append({
                    "strategy": "Parallel Progress Strategy",
                    "courses": alternative_courses,
                    "timeline": "While retaking failed course",
                    "benefits": ["Make progress in other areas", "Maintain full course load"],
                    "challenges": ["May be overwhelming", "Need to balance priorities"]
                })
        
        recovery_plan["timeline_impact"] = failure_impact.get("graduation_impact", "Impact varies")
        recovery_plan["alternative_strategies"] = failure_impact.get("next_steps", [])
        
        return recovery_plan
    
    def _get_alternative_summer_courses(self, failed_course: str, student_profile: Dict) -> List[str]:
        """Get courses that can be taken in summer while recovering from failure"""
        completed = student_profile.get("completed_courses", [])
        
        # Courses that don't depend on the failed course
        independent_courses = {
            "CS 18000": ["MA 16200", "STAT 35000", "Science electives"],
            "CS 18200": ["CS 24000", "MA 26100", "Science electives"], 
            "CS 24000": ["CS 18200", "MA 26500", "Science electives"],
            "CS 25100": ["STAT 35000", "MA 26500", "Science electives"],
            "CS 25000": ["STAT 35000", "Science electives"]
        }
        
        alternatives = independent_courses.get(failed_course, ["Science electives", "General education"])
        
        # Filter out already completed courses
        return [course for course in alternatives if course not in completed]

def generate_summer_acceleration_recommendation(student_profile: Dict) -> str:
    """Generate summer acceleration recommendations"""
    calculator = SummerAccelerationCalculator()
    plan = calculator.calculate_acceleration_plan(student_profile)
    
    response = []
    
    # Header with strategy
    response.append(f"Summer Acceleration Plan: {plan['recommended_strategy']}")
    response.append(f"Success Probability: {plan['success_probability']:.0%}")
    
    if plan["summer_options"]:
        response.append("\n**Recommended Summer Courses:**")
        for option in plan["summer_options"]:
            if isinstance(option, dict):
                if "courses" in option:  # Plan format
                    courses_str = ", ".join(option["courses"])
                    response.append(f"• {courses_str} ({option['credits']} credits)")
                    response.append(f"  - {option['rationale']}")
                    response.append(f"  - Intensity: {option['intensity']}")
                else:  # Individual course format
                    response.append(f"• {option['course']} ({option['credits']} credits)")
                    response.append(f"  - {option['reason']}")
                    response.append(f"  - Availability: {option['availability']}")
                    prereq_status = "✅" if option["prerequisites_met"] else "❌"
                    response.append(f"  - Prerequisites met: {prereq_status}")
    
    if plan["risks"]:
        response.append("\n**⚠️ Risks to Consider:**")
        for risk in plan["risks"]:
            response.append(f"• {risk}")
    
    if "benefits" in plan:
        response.append("\n**✅ Benefits:**")
        for benefit in plan["benefits"]:
            response.append(f"• {benefit}")
    
    if not plan["acceleration_feasible"]:
        response.append("\n❌ **Not recommended for your profile.** Consider standard 4-year path.")
    
    return "\n".join(response)

# Test the system
if __name__ == "__main__":
    test_profile = {
        "year_level": "sophomore",
        "current_semester": "spring", 
        "completed_courses": ["CS 18000", "CS 18200", "CS 24000", "MA 16100", "MA 16200"],
        "gpa": 3.2,
        "graduation_goal": "3.5_year"
    }
    
    result = generate_summer_acceleration_recommendation(test_profile)
    print("Summer Acceleration Test:")
    print(result)