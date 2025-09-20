#!/usr/bin/env python3
"""
Course Failure Prediction and Graduation Impact Analysis System
Handles worst-case scenarios including multiple foundation course failures
"""

import json
import networkx as nx
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import os

@dataclass
class FailureScenario:
    """Represents a course failure scenario"""
    failed_courses: List[str]
    student_year: str
    current_gpa: float
    completed_courses: List[str]
    target_graduation: str = "4_years"

@dataclass
class GraduationImpact:
    """Represents impact of failures on graduation"""
    additional_semesters: int
    blocked_courses: List[str]
    critical_path_affected: bool
    recovery_timeline: Dict[str, List[str]]
    alternative_strategies: List[str]
    graduation_risk: str  # LOW, MEDIUM, HIGH, CRITICAL

class CourseFailurePredictor:
    def __init__(self):
        # Load knowledge base
        self.load_knowledge_base()
        
        # Foundation courses (critical early courses)
        self.foundation_courses = [
            "CS 18000",  # Problem Solving and Object-Oriented Programming
            "CS 18200",  # Foundations of Computer Science
            "CS 24000",  # Programming in C
            "CS 25000",  # Computer Architecture
            "CS 25100",  # Data Structures and Algorithms
            "CS 25200",  # Systems Programming
            "MATH 16100", # Calculus I
            "MATH 16200", # Calculus II
            "MATH 26100", # Calculus III
        ]
        
        # Required core courses
        self.required_core = [
            "CS 35100",  # Introduction to Software Engineering
            "CS 35200",  # Compilers
            "CS 38100",  # Introduction to the Analysis of Algorithms
        ]
        
        # Build prerequisite dependency graph
        self.build_dependency_graph()
        
        # Define critical failure impacts
        self.define_failure_impacts()
    
    def load_knowledge_base(self):
        """Load knowledge base from files"""
        # Load comprehensive data
        comp_path = "data/comprehensive_purdue_cs_data.json"
        if os.path.exists(comp_path):
            with open(comp_path, 'r') as f:
                self.comprehensive_data = json.load(f)
        else:
            self.comprehensive_data = {"courses": {}, "prerequisites": {}}
        
        # Load knowledge graph
        kg_path = "data/cs_knowledge_graph.json"
        if os.path.exists(kg_path):
            with open(kg_path, 'r') as f:
                self.knowledge_graph = json.load(f)
        else:
            self.knowledge_graph = {"prerequisites": {}}
    
    def build_dependency_graph(self):
        """Build NetworkX graph of course dependencies"""
        self.dependency_graph = nx.DiGraph()
        
        # Add courses as nodes
        all_courses = set(self.foundation_courses + self.required_core)
        
        # Add courses from knowledge base
        if "courses" in self.comprehensive_data:
            all_courses.update(self.comprehensive_data["courses"].keys())
        
        for course in all_courses:
            self.dependency_graph.add_node(course)
        
        # Add prerequisite edges from knowledge graph
        prerequisites = self.knowledge_graph.get("prerequisites", {})
        for course, prereqs in prerequisites.items():
            if isinstance(prereqs, list):
                for prereq in prereqs:
                    if prereq in all_courses:
                        self.dependency_graph.add_edge(prereq, course)
        
        print(f"✓ Built dependency graph with {self.dependency_graph.number_of_nodes()} courses")
        print(f"✓ {self.dependency_graph.number_of_edges()} prerequisite relationships")
    
    def define_failure_impacts(self):
        """Define impact levels for different course failures"""
        self.failure_impacts = {
            # Critical foundation courses
            "CS 18000": {
                "impact_level": "CRITICAL",
                "blocks_entire_sequence": True,
                "additional_semesters": 2,
                "affects_codo": True,
                "description": "Blocks entire CS sequence - catastrophic failure"
            },
            "CS 18200": {
                "impact_level": "CRITICAL", 
                "blocks_entire_sequence": True,
                "additional_semesters": 1.5,
                "affects_codo": False,
                "description": "Blocks all second-year CS courses"
            },
            "CS 24000": {
                "impact_level": "HIGH",
                "blocks_entire_sequence": True,
                "additional_semesters": 1.5,
                "affects_codo": False,
                "description": "Blocks systems programming sequence"
            },
            "CS 25100": {
                "impact_level": "CRITICAL",
                "blocks_entire_sequence": True,
                "additional_semesters": 2,
                "affects_codo": False,
                "description": "Blocks ALL advanced CS courses and tracks"
            },
            "CS 25000": {
                "impact_level": "HIGH",
                "blocks_entire_sequence": False,
                "additional_semesters": 1,
                "affects_codo": False,
                "description": "Blocks systems programming and architecture courses"
            },
            "CS 25200": {
                "impact_level": "MEDIUM",
                "blocks_entire_sequence": False,
                "additional_semesters": 0.5,
                "affects_codo": False,
                "description": "Blocks some advanced systems courses"
            },
            "MATH 16100": {
                "impact_level": "CRITICAL",
                "blocks_entire_sequence": True,
                "additional_semesters": 1,
                "affects_codo": True,
                "description": "Blocks all subsequent math and many CS courses"
            },
            "MATH 16200": {
                "impact_level": "HIGH",
                "blocks_entire_sequence": False,
                "additional_semesters": 1,
                "affects_codo": True,
                "description": "Blocks Calc III and advanced math requirements"
            },
            "CS 38100": {
                "impact_level": "HIGH",
                "blocks_entire_sequence": False,
                "additional_semesters": 1,
                "affects_codo": False,
                "description": "Required core course - blocks graduation and ML track"
            }
        }
    
    def analyze_failure_impact(self, scenario: FailureScenario) -> GraduationImpact:
        """Analyze comprehensive impact of course failures"""
        
        print(f"\n🔍 Analyzing failure impact for: {', '.join(scenario.failed_courses)}")
        print("=" * 70)
        
        # Calculate blocked courses
        blocked_courses = self.get_blocked_courses(scenario.failed_courses)
        
        # Calculate additional semesters needed
        additional_semesters = self.calculate_semester_delay(scenario)
        
        # Determine if critical path is affected
        critical_path_affected = self.is_critical_path_affected(scenario.failed_courses)
        
        # Generate recovery timeline
        recovery_timeline = self.generate_recovery_timeline(scenario)
        
        # Generate alternative strategies
        alternative_strategies = self.generate_alternative_strategies(scenario)
        
        # Assess overall graduation risk
        graduation_risk = self.assess_graduation_risk(scenario, additional_semesters, blocked_courses)
        
        return GraduationImpact(
            additional_semesters=additional_semesters,
            blocked_courses=blocked_courses,
            critical_path_affected=critical_path_affected,
            recovery_timeline=recovery_timeline,
            alternative_strategies=alternative_strategies,
            graduation_risk=graduation_risk
        )
    
    def get_blocked_courses(self, failed_courses: List[str]) -> List[str]:
        """Get all courses blocked by failures"""
        blocked = set()
        
        for failed_course in failed_courses:
            # Get all courses that depend on this failed course
            if failed_course in self.dependency_graph:
                descendants = nx.descendants(self.dependency_graph, failed_course)
                blocked.update(descendants)
        
        return sorted(list(blocked))
    
    def calculate_semester_delay(self, scenario: FailureScenario) -> int:
        """Calculate total semester delay from failures"""
        base_delay = 0
        
        # Individual course impacts
        for course in scenario.failed_courses:
            if course in self.failure_impacts:
                base_delay += self.failure_impacts[course]["additional_semesters"]
        
        # Compound effects for multiple failures
        if len(scenario.failed_courses) > 1:
            compound_factor = min(len(scenario.failed_courses) * 0.5, 2.0)
            base_delay += compound_factor
        
        # Critical sequence failures
        foundation_failures = [c for c in scenario.failed_courses if c in self.foundation_courses]
        if len(foundation_failures) >= 3:
            base_delay += 1  # Major sequence disruption
        
        return int(base_delay)
    
    def is_critical_path_affected(self, failed_courses: List[str]) -> bool:
        """Check if critical graduation path is affected"""
        critical_courses = ["CS 18000", "CS 18200", "CS 25100", "CS 38100", "MATH 16100"]
        return any(course in failed_courses for course in critical_courses)
    
    def generate_recovery_timeline(self, scenario: FailureScenario) -> Dict[str, List[str]]:
        """Generate semester-by-semester recovery plan"""
        timeline = {}
        
        # Current semester (immediate actions)
        timeline["Immediate"] = [
            "Meet with academic advisor urgently",
            "Understand failure reasons for each course",
            "Consider withdrawal from related courses if struggling"
        ]
        
        # Next semester (retakes)
        retake_courses = []
        for course in scenario.failed_courses:
            retake_courses.append(f"Retake {course}")
        
        timeline["Next Semester"] = retake_courses + [
            "Take lighter course load (12-13 credits)",
            "Utilize tutoring and support services",
            "Form study groups"
        ]
        
        # Following semesters (catch-up)
        blocked_courses = self.get_blocked_courses(scenario.failed_courses)
        if blocked_courses:
            timeline["Semester 2-3"] = [
                f"Resume blocked courses: {', '.join(blocked_courses[:3])}",
                "Gradually increase course load",
                "Monitor academic performance closely"
            ]
        
        # Long-term recovery
        timeline["Long-term"] = [
            "Consider summer courses to accelerate recovery",
            "Evaluate graduation timeline realistically", 
            "Explore alternative majors if pattern continues"
        ]
        
        return timeline
    
    def generate_alternative_strategies(self, scenario: FailureScenario) -> List[str]:
        """Generate alternative strategies based on failure pattern"""
        strategies = []
        
        # Multiple foundation failures
        foundation_failures = [c for c in scenario.failed_courses if c in self.foundation_courses]
        if len(foundation_failures) >= 2:
            strategies.extend([
                "🔄 Consider taking a gap semester to reassess study strategies",
                "📚 Enroll in supplemental instruction (SI) for all retaken courses",
                "🎯 Consider switching to Computer Information Technology (CIT) major",
                "💼 Explore related majors: Data Science, Information Systems",
                "📖 Take prerequisite courses at community college (if allowed)"
            ])
        
        # Math failures
        math_failures = [c for c in scenario.failed_courses if "MATH" in c]
        if math_failures:
            strategies.extend([
                "📐 Use Math Help Room extensively",
                "🧮 Consider ALEKS refresher for math fundamentals", 
                "📊 Take lighter math course load with tutoring support"
            ])
        
        # CS core failures
        cs_failures = [c for c in scenario.failed_courses if "CS" in c]
        if len(cs_failures) >= 2:
            strategies.extend([
                "💻 Join CS Help Room and form consistent study groups",
                "🔧 Practice programming extensively outside of class",
                "👥 Find upperclassman mentor in CS",
                "⏰ Consider extending graduation timeline to 5-6 years"
            ])
        
        # GPA considerations
        if scenario.current_gpa < 2.0:
            strategies.extend([
                "⚠️ Address academic probation immediately",
                "📈 Focus on GPA recovery with easier electives",
                "🆘 Utilize Academic Success Center resources"
            ])
        
        return strategies
    
    def assess_graduation_risk(self, scenario: FailureScenario, additional_semesters: int, blocked_courses: List[str]) -> str:
        """Assess overall graduation risk level"""
        
        risk_score = 0
        
        # Number of failures
        risk_score += len(scenario.failed_courses) * 2
        
        # Critical course failures
        critical_failures = [c for c in scenario.failed_courses if c in ["CS 18000", "CS 25100", "MATH 16100"]]
        risk_score += len(critical_failures) * 5
        
        # GPA impact
        if scenario.current_gpa < 2.0:
            risk_score += 10
        elif scenario.current_gpa < 2.5:
            risk_score += 5
        
        # Semester delay impact
        risk_score += additional_semesters * 3
        
        # Blocked courses impact
        risk_score += min(len(blocked_courses), 10)
        
        # Determine risk level
        if risk_score >= 25:
            return "CRITICAL"
        elif risk_score >= 15:
            return "HIGH"
        elif risk_score >= 8:
            return "MEDIUM"
        else:
            return "LOW"
    
    def predict_graduation_timeline(self, scenario: FailureScenario) -> Dict[str, Any]:
        """Predict new graduation timeline after failures"""
        
        impact = self.analyze_failure_impact(scenario)
        
        # Base timeline calculation
        current_year_map = {"freshman": 7, "sophomore": 5, "junior": 3, "senior": 1}
        base_semesters_remaining = current_year_map.get(scenario.student_year.lower(), 4)
        
        # Add failure impact
        total_semesters = base_semesters_remaining + impact.additional_semesters
        
        # Calculate new graduation date
        current_date = datetime.now()
        graduation_date = current_date + timedelta(days=total_semesters * 120)  # ~4 months per semester
        
        return {
            "original_graduation": f"{scenario.target_graduation} plan",
            "new_graduation_timeline": f"{total_semesters} semesters remaining",
            "graduation_date": graduation_date.strftime("%B %Y"),
            "delay_amount": f"{impact.additional_semesters} semesters",
            "graduation_risk": impact.graduation_risk,
            "blocked_courses_count": len(impact.blocked_courses),
            "recovery_feasible": impact.graduation_risk != "CRITICAL"
        }
    
    def generate_failure_report(self, scenario: FailureScenario) -> str:
        """Generate comprehensive failure impact report"""
        
        impact = self.analyze_failure_impact(scenario)
        timeline = self.predict_graduation_timeline(scenario)
        
        report = []
        report.append("🚨 **COURSE FAILURE IMPACT ANALYSIS**")
        report.append("=" * 60)
        
        # Scenario summary
        report.append(f"\n📊 **Failure Scenario:**")
        report.append(f"   • Failed Courses: {', '.join(scenario.failed_courses)}")
        report.append(f"   • Student Level: {scenario.student_year.title()}")
        report.append(f"   • Current GPA: {scenario.current_gpa}")
        report.append(f"   • Completed Courses: {len(scenario.completed_courses)}")
        
        # Impact assessment
        report.append(f"\n⚡ **Impact Assessment:**")
        report.append(f"   • Graduation Risk: 🔴 **{impact.graduation_risk}**")
        report.append(f"   • Additional Semesters: {impact.additional_semesters}")
        report.append(f"   • Blocked Courses: {len(impact.blocked_courses)}")
        report.append(f"   • Critical Path Affected: {'Yes' if impact.critical_path_affected else 'No'}")
        
        # New graduation timeline
        report.append(f"\n📅 **Revised Graduation Timeline:**")
        report.append(f"   • Original Plan: {timeline['original_graduation']}")
        report.append(f"   • New Timeline: {timeline['new_graduation_timeline']}")
        report.append(f"   • Expected Graduation: {timeline['graduation_date']}")
        report.append(f"   • Total Delay: {timeline['delay_amount']}")
        
        # Blocked courses
        if impact.blocked_courses:
            report.append(f"\n🚫 **Blocked Courses (Cannot Take Until Retakes Complete):**")
            for course in impact.blocked_courses[:10]:  # Show first 10
                report.append(f"   • {course}")
            if len(impact.blocked_courses) > 10:
                report.append(f"   • ... and {len(impact.blocked_courses) - 10} more courses")
        
        # Individual course impacts
        report.append(f"\n💥 **Individual Course Impact Analysis:**")
        for course in scenario.failed_courses:
            if course in self.failure_impacts:
                impact_info = self.failure_impacts[course]
                report.append(f"   • **{course}**: {impact_info['description']}")
                report.append(f"     - Impact Level: {impact_info['impact_level']}")
                report.append(f"     - Semester Delay: {impact_info['additional_semesters']}")
                if impact_info['affects_codo']:
                    report.append(f"     - ⚠️ Affects CODO eligibility")
        
        # Recovery timeline
        report.append(f"\n🛠️ **Recovery Timeline:**")
        for phase, actions in impact.recovery_timeline.items():
            report.append(f"   **{phase}:**")
            for action in actions:
                report.append(f"     • {action}")
            report.append("")
        
        # Alternative strategies
        if impact.alternative_strategies:
            report.append(f"💡 **Alternative Strategies:**")
            for strategy in impact.alternative_strategies:
                report.append(f"   {strategy}")
        
        # Risk-specific recommendations
        report.append(f"\n🎯 **Risk-Specific Recommendations:**")
        if impact.graduation_risk == "CRITICAL":
            report.append("   🔴 **CRITICAL RISK - Immediate Action Required:**")
            report.append("   • Meet with dean and academic advisor immediately")
            report.append("   • Consider academic probation procedures")
            report.append("   • Explore alternative major options")
            report.append("   • Consider taking time off to reassess")
        elif impact.graduation_risk == "HIGH":
            report.append("   🟠 **HIGH RISK - Significant Intervention Needed:**")
            report.append("   • Implement comprehensive study strategy")
            report.append("   • Use all available academic support resources")
            report.append("   • Consider extending graduation timeline")
            report.append("   • Monitor progress closely each semester")
        elif impact.graduation_risk == "MEDIUM":
            report.append("   🟡 **MEDIUM RISK - Manageable with Support:**")
            report.append("   • Focus on successful retakes")
            report.append("   • Use tutoring and study groups")
            report.append("   • Plan summer courses to catch up")
        else:
            report.append("   🟢 **LOW RISK - Recoverable:**")
            report.append("   • Retake failed courses next semester")
            report.append("   • Minor adjustment to graduation timeline")
        
        return "\n".join(report)

def test_failure_scenarios():
    """Test various failure scenarios"""
    predictor = CourseFailurePredictor()
    
    # Test scenarios
    scenarios = [
        FailureScenario(
            failed_courses=["CS 18000"],
            student_year="freshman",
            current_gpa=1.8,
            completed_courses=["MATH 16100"],
            target_graduation="4_years"
        ),
        FailureScenario(
            failed_courses=["CS 18000", "CS 18200", "MATH 16200"],
            student_year="sophomore", 
            current_gpa=2.1,
            completed_courses=["MATH 16100"],
            target_graduation="4_years"
        ),
        FailureScenario(
            failed_courses=["CS 25100", "CS 38100"],
            student_year="junior",
            current_gpa=2.5,
            completed_courses=["CS 18000", "CS 18200", "CS 24000", "MATH 16100", "MATH 16200"],
            target_graduation="4_years"
        )
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🧪 **TEST SCENARIO {i}:**")
        print(predictor.generate_failure_report(scenario))
        print("\n" + "="*80)

def main():
    """Main function"""
    predictor = CourseFailurePredictor()
    
    print("🚨 Course Failure Prediction System")
    print("=" * 50)
    
    # Example: Student fails multiple foundation courses
    worst_case = FailureScenario(
        failed_courses=["CS 18000", "CS 18200", "MATH 16100", "MATH 16200"],
        student_year="sophomore",
        current_gpa=1.5,
        completed_courses=["ENGL 10600"],
        target_graduation="4_years"
    )
    
    print("📊 **WORST-CASE SCENARIO ANALYSIS:**")
    print("Student fails most foundation courses")
    report = predictor.generate_failure_report(worst_case)
    print(report)

if __name__ == "__main__":
    main()