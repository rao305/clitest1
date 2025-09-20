"""
Failure Recovery System - Comprehensive analysis and recovery planning for failed CS courses
"""
from typing import Dict, List, Optional, Tuple
from degree_progression_engine import DegreeProgressionEngine
from summer_acceleration_calculator import SummerAccelerationCalculator

class FailureRecoverySystem:
    def __init__(self):
        self.engine = DegreeProgressionEngine()
        self.summer_calc = SummerAccelerationCalculator()
        
        # Critical course failure patterns and recovery strategies
        self.critical_failure_impacts = {
            "CS 18000": {
                "severity": "critical",
                "cascade_effect": "blocks_all_cs",
                "typical_delay": "2 semesters",
                "recovery_difficulty": "high",
                "common_causes": [
                    "First exposure to programming",
                    "Object-oriented concepts confusion",
                    "Time management issues",
                    "Math background gaps"
                ],
                "recovery_strategies": [
                    "Retake immediately next semester",
                    "Get tutoring/supplemental instruction",
                    "Practice programming fundamentals over break",
                    "Consider CS 17700 as preparation if allowed"
                ]
            },
            "CS 25100": {
                "severity": "critical", 
                "cascade_effect": "blocks_upper_level",
                "typical_delay": "1-2 semesters",
                "recovery_difficulty": "very_high",
                "common_causes": [
                    "Algorithm design and analysis complexity",
                    "Recursive thinking challenges", 
                    "Heavy programming workload",
                    "Mathematical proofs difficulty"
                ],
                "recovery_strategies": [
                    "Summer retake strongly recommended",
                    "Master recursion before retaking",
                    "Practice algorithm implementation daily",
                    "Form study groups with successful students"
                ]
            },
            "CS 18200": {
                "severity": "medium",
                "cascade_effect": "delays_core_sequence", 
                "typical_delay": "1 semester",
                "recovery_difficulty": "medium",
                "common_causes": [
                    "Proof writing difficulties",
                    "Abstract mathematical concepts",
                    "Logic and formal reasoning gaps"
                ],
                "recovery_strategies": [
                    "Retake with additional proof practice",
                    "Take MA courses to strengthen math background",
                    "Use discrete math resources for self-study"
                ]
            },
            "CS 24000": {
                "severity": "medium",
                "cascade_effect": "delays_architecture_systems",
                "typical_delay": "1 semester", 
                "recovery_difficulty": "medium",
                "common_causes": [
                    "Pointer and memory management confusion",
                    "Transition from Java to C",
                    "Debugging segmentation faults"
                ],
                "recovery_strategies": [
                    "Focus on pointer concepts before retaking",
                    "Practice with Valgrind and debugging tools",
                    "Work through C programming exercises"
                ]
            }
        }
        
    def analyze_failure_comprehensive(self, failed_course: str, student_profile: Dict) -> Dict:
        """Comprehensive failure analysis with personalized recovery plan"""
        current_year = student_profile.get("year_level", "unknown")
        current_semester = student_profile.get("current_semester", "unknown")
        completed_courses = student_profile.get("completed_courses", [])
        gpa = student_profile.get("gpa", 0.0)
        
        analysis = {
            "failed_course": failed_course,
            "failure_severity": "unknown",
            "immediate_impact": {},
            "long_term_impact": {},
            "recovery_options": [],
            "recommended_strategy": "",
            "timeline_scenarios": [],
            "support_resources": [],
            "prevention_advice": []
        }
        
        # Get basic failure data from knowledge base
        basic_impact = self.engine.calculate_failure_impact(failed_course, current_semester)
        analysis["immediate_impact"] = basic_impact
        
        # Add detailed analysis if it's a critical course
        if failed_course in self.critical_failure_impacts:
            critical_data = self.critical_failure_impacts[failed_course]
            analysis["failure_severity"] = critical_data["severity"]
            analysis["recovery_options"] = self._generate_detailed_recovery_options(
                failed_course, critical_data, student_profile
            )
            analysis["recommended_strategy"] = self._determine_best_strategy(
                failed_course, critical_data, student_profile
            )
            analysis["timeline_scenarios"] = self._calculate_timeline_scenarios(
                failed_course, critical_data, student_profile
            )
        else:
            analysis["failure_severity"] = "moderate"
            analysis["recovery_options"] = basic_impact.get("next_steps", [])
        
        # Add support resources
        analysis["support_resources"] = self._get_support_resources(failed_course)
        
        # Add prevention advice for retaking
        analysis["prevention_advice"] = self._generate_prevention_advice(failed_course, student_profile)
        
        return analysis
    
    def _generate_detailed_recovery_options(self, failed_course: str, critical_data: Dict, student_profile: Dict) -> List[Dict]:
        """Generate detailed recovery options with pros/cons analysis"""
        options = []
        gpa = student_profile.get("gpa", 0.0)
        
        # Option 1: Immediate retake next semester
        immediate_retake = {
            "strategy": "Immediate Retake Next Semester",
            "timeline": "Next available semester",
            "pros": [
                "Material still fresh in memory",
                "Minimizes delay in degree progression", 
                "Shows commitment to recovery"
            ],
            "cons": [
                "May not have time to address root causes",
                "Risk of repeating same mistakes",
                "Pressure to succeed immediately"
            ],
            "requirements": [
                "Available space in course",
                "Meet retake policies",
                "Address study strategies"
            ],
            "success_probability": 0.6 if gpa >= 2.5 else 0.4
        }
        options.append(immediate_retake)
        
        # Option 2: Summer retake (if available)
        if self.summer_calc._get_summer_availability(failed_course) in ["commonly_offered", "sometimes_offered"]:
            summer_retake = {
                "strategy": "Summer Session Retake",
                "timeline": "Next summer",
                "pros": [
                    "Intensive focus on single subject",
                    "Smaller class sizes often available",
                    "Can prepare thoroughly during spring break"
                ],
                "cons": [
                    "Intensive pace may be challenging",
                    "Limited time for other activities",
                    "May not address fundamental gaps"
                ],
                "requirements": [
                    "Course offered in summer",
                    "Financial consideration",
                    "Intensive study preparation"
                ],
                "success_probability": 0.7 if gpa >= 2.5 else 0.5
            }
            options.append(summer_retake)
        
        # Option 3: Gap semester with preparation
        if critical_data["recovery_difficulty"] == "very_high":
            gap_preparation = {
                "strategy": "Preparation Semester + Retake",
                "timeline": "Skip one semester, retake following semester",
                "pros": [
                    "Time to thoroughly address weak areas",
                    "Can take prerequisite refreshers",
                    "Reduced course load when retaking"
                ],
                "cons": [
                    "Delays graduation by full semester",
                    "May lose momentum in CS sequence",
                    "Financial and time cost"
                ],
                "requirements": [
                    "Academic advisor approval",
                    "Plan for gap semester activities",
                    "Strong commitment to preparation"
                ],
                "success_probability": 0.8 if gpa >= 2.0 else 0.6
            }
            options.append(gap_preparation)
        
        return options
    
    def _determine_best_strategy(self, failed_course: str, critical_data: Dict, student_profile: Dict) -> str:
        """Determine recommended strategy based on student profile"""
        gpa = student_profile.get("gpa", 0.0)
        attempt_number = student_profile.get("attempt_number", 1)
        
        # High-performing student who failed due to specific issue
        if gpa >= 3.0:
            return "Immediate retake with targeted support - you have strong fundamentals"
        
        # Multiple failures or very low GPA
        elif gpa < 2.0 or attempt_number > 1:
            return "Preparation semester recommended - address fundamental gaps before retaking"
        
        # Average student - depends on course difficulty
        elif critical_data["recovery_difficulty"] == "very_high":
            return "Summer retake with intensive preparation - gives focused time for mastery"
        
        else:
            return "Immediate retake with additional support resources"
    
    def _calculate_timeline_scenarios(self, failed_course: str, critical_data: Dict, student_profile: Dict) -> List[Dict]:
        """Calculate different timeline scenarios based on recovery strategy"""
        scenarios = []
        
        # Best case: successful immediate retake
        best_case = {
            "scenario": "Best Case - Immediate Success",
            "strategy": "Immediate retake next semester",
            "graduation_delay": "0 semesters",
            "timeline": self._calculate_graduation_timeline(failed_course, 0),
            "probability": "60%" if student_profile.get("gpa", 0) >= 2.5 else "40%",
            "requirements": ["Pass course on next attempt", "Keep up with subsequent courses"]
        }
        scenarios.append(best_case)
        
        # Realistic case: retake with minor delay
        realistic_case = {
            "scenario": "Realistic Case - Minor Delay",
            "strategy": "Summer retake or gap semester",
            "graduation_delay": critical_data["typical_delay"],
            "timeline": self._calculate_graduation_timeline(failed_course, 1),
            "probability": "70-80%",
            "requirements": ["Additional preparation", "Strategic course planning"]
        }
        scenarios.append(realistic_case)
        
        # Worst case: multiple retakes needed
        worst_case = {
            "scenario": "Worst Case - Multiple Attempts",
            "strategy": "Multiple retakes or major change consideration",
            "graduation_delay": "2-3 semesters",
            "timeline": self._calculate_graduation_timeline(failed_course, 2),
            "probability": "15-20%",
            "requirements": ["Major remediation", "Possible major reconsideration"]
        }
        scenarios.append(worst_case)
        
        return scenarios
    
    def _calculate_graduation_timeline(self, failed_course: str, delay_semesters: int) -> Dict:
        """Calculate new graduation timeline after failure"""
        base_graduation = "Spring 4th Year"  # Assume standard 4-year plan
        
        if delay_semesters == 0:
            return {"expected_graduation": base_graduation, "total_time": "4 years"}
        elif delay_semesters == 1:
            return {"expected_graduation": "Fall 4th Year or Spring 5th Year", "total_time": "4.5 years"}
        elif delay_semesters == 2:
            return {"expected_graduation": "Spring 5th Year", "total_time": "5 years"}
        else:
            return {"expected_graduation": f"Delayed by {delay_semesters} semesters", "total_time": f"{4 + delay_semesters/2} years"}
    
    def _get_support_resources(self, failed_course: str) -> List[Dict]:
        """Get relevant support resources for course"""
        general_resources = [
            {
                "resource": "Academic Success Center",
                "type": "tutoring",
                "description": "Free tutoring for CS courses"
            },
            {
                "resource": "CS Department Office Hours",
                "type": "instructor_support", 
                "description": "Professor and TA office hours for direct help"
            },
            {
                "resource": "Study Groups",
                "type": "peer_support",
                "description": "Form study groups with successful students"
            }
        ]
        
        # Course-specific resources
        course_specific = {
            "CS 18000": [
                {
                    "resource": "PASS (Peer-Assisted Study Sessions)",
                    "type": "structured_study",
                    "description": "Collaborative study sessions for CS 18000"
                },
                {
                    "resource": "Java Programming Practice",
                    "type": "skill_building", 
                    "description": "Additional Java exercises and projects"
                }
            ],
            "CS 25100": [
                {
                    "resource": "Algorithm Visualization Tools",
                    "type": "learning_aid",
                    "description": "VisuAlgo, Algorithm Visualizer for understanding"
                },
                {
                    "resource": "Data Structures Workbook",
                    "type": "practice",
                    "description": "Additional practice problems for data structures"
                }
            ]
        }
        
        specific_resources = course_specific.get(failed_course, [])
        return general_resources + specific_resources
    
    def _generate_prevention_advice(self, failed_course: str, student_profile: Dict) -> List[str]:
        """Generate advice to prevent future failures"""
        general_advice = [
            "Start assignments early - they typically take longer than expected",
            "Attend all office hours when struggling with concepts",
            "Form study groups with successful students",
            "Practice consistently rather than cramming before exams",
            "Seek help at first sign of confusion, not when failing"
        ]
        
        course_specific_advice = {
            "CS 18000": [
                "Focus on understanding object-oriented concepts, not just syntax",
                "Debug code systematically - learn to read error messages",
                "Practice coding every day, even if just for 30 minutes"
            ],
            "CS 25100": [
                "Master recursion early - it's fundamental to the course", 
                "Implement algorithms by hand before coding them",
                "Understand Big-O notation thoroughly",
                "Visualize data structures to understand their operations"
            ],
            "CS 18200": [
                "Practice proof techniques daily, not just before assignments",
                "Work through examples step-by-step to understand logic",
                "Don't fall behind - mathematical concepts build on each other"
            ]
        }
        
        specific_advice = course_specific_advice.get(failed_course, [])
        return general_advice + specific_advice

def generate_failure_recovery_plan(failed_course: str, student_profile: Dict) -> str:
    """Generate comprehensive failure recovery plan"""
    recovery_system = FailureRecoverySystem()
    analysis = recovery_system.analyze_failure_comprehensive(failed_course, student_profile)
    
    response = []
    
    # Header with severity assessment
    response.append(f"📚 Failure Recovery Plan for {failed_course}")
    response.append(f"Severity: {analysis['failure_severity'].upper()}")
    
    # Immediate impact
    immediate = analysis["immediate_impact"]
    if immediate and "delay_semesters" in immediate:
        response.append(f"Expected delay: {immediate['delay_semesters']} semester(s)")
        response.append(f"Affected courses: {', '.join(immediate.get('affected_courses', []))}")
    
    # Recommended strategy
    if analysis["recommended_strategy"]:
        response.append(f"\n🎯 **Recommended Strategy:** {analysis['recommended_strategy']}")
    
    # Recovery options
    if analysis["recovery_options"] and isinstance(analysis["recovery_options"][0], dict):
        response.append("\n**📋 Recovery Options:**")
        for i, option in enumerate(analysis["recovery_options"][:2], 1):  # Show top 2 options
            response.append(f"\n**Option {i}: {option['strategy']}**")
            response.append(f"Success probability: {option.get('success_probability', 'Unknown')}")
            response.append("Pros: " + ", ".join(option.get("pros", [])))
            response.append("Cons: " + ", ".join(option.get("cons", [])))
    
    # Timeline scenarios
    if analysis["timeline_scenarios"]:
        response.append("\n**⏰ Timeline Scenarios:**")
        for scenario in analysis["timeline_scenarios"]:
            response.append(f"• {scenario['scenario']}: {scenario['graduation_delay']} delay ({scenario['probability']})")
    
    # Support resources
    if analysis["support_resources"]:
        response.append("\n**🆘 Support Resources:**")
        for resource in analysis["support_resources"][:3]:  # Show top 3 resources
            response.append(f"• {resource['resource']}: {resource['description']}")
    
    # Prevention advice for retake
    if analysis["prevention_advice"]:
        response.append("\n**💡 Success Tips for Retaking:**")
        for tip in analysis["prevention_advice"][:4]:  # Show top 4 tips
            response.append(f"• {tip}")
    
    response.append("\n⚠️ **Remember**: Meet with your academic advisor to discuss the best path forward for your specific situation.")
    
    return "\n".join(response)

# Test the system
if __name__ == "__main__":
    test_profile = {
        "year_level": "sophomore",
        "current_semester": "fall",
        "completed_courses": ["CS 18000", "CS 18200", "CS 24000"],
        "gpa": 2.3,
        "attempt_number": 1
    }
    
    result = generate_failure_recovery_plan("CS 25100", test_profile)
    print("Failure Recovery Test:")
    print(result)