#!/usr/bin/env python3
"""
Dynamic Course Failure Analyzer - Knowledge Graph Based

This system analyzes course failures for ANY CS course using the knowledge graph 
to calculate exact graduation timeline impact and generate specific recovery plans.
"""

import networkx as nx
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging
import json

class DynamicCourseFailureAnalyzer:
    def __init__(self, knowledge_graph: nx.DiGraph):
        self.graph = knowledge_graph
        self.logger = self.setup_logger()
        self.degree_progression = self.load_degree_progression_from_graph()
        
    def setup_logger(self):
        """Setup logging for failure analyzer"""
        logger = logging.getLogger('FailureAnalyzer')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('🔍 %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def load_degree_progression_from_graph(self) -> Dict:
        """Extract degree progression timeline from knowledge graph"""
        self.logger.info("📊 LOADING: Degree progression from knowledge graph")
        
        progression = {
            'normal_timeline': {},
            'credit_requirements': {
                'total_credits': 120,
                'cs_major_credits': 36,
                'math_credits': 20,
                'foundation_credits': 24
            },
            'critical_path_courses': [],
            'semester_mappings': {}
        }
        
        # Extract semester mappings from graph
        for node in self.graph.nodes():
            if self.graph.nodes[node].get('type') == 'course':
                typical_sem = self.graph.nodes[node].get('typical_semester')
                if typical_sem:
                    if typical_sem not in progression['semester_mappings']:
                        progression['semester_mappings'][typical_sem] = []
                    progression['semester_mappings'][typical_sem].append(node)
        
        # Identify critical path courses (those with many dependencies)
        for node in self.graph.nodes():
            if self.graph.nodes[node].get('type') == 'course':
                dependents = list(self.graph.successors(node))
                if len(dependents) >= 2:  # Course that unlocks multiple others
                    progression['critical_path_courses'].append(node)
        
        self.logger.info(f"📊 LOADED: {len(progression['semester_mappings'])} semester mappings")
        return progression
    
    def analyze_course_failure(self, failed_course: str, failure_semester: str, 
                              student_context: Dict = None) -> Dict:
        """Analyze impact of ANY course failure using knowledge graph"""
        
        self.logger.info(f"🔍 ANALYZING: {failed_course} failure in {failure_semester}")
        
        # Validate course exists in graph
        if failed_course not in self.graph.nodes():
            return {
                'error': f"Course {failed_course} not found in knowledge graph",
                'failed_course': failed_course,
                'analysis_possible': False
            }
        
        # Get course data from graph
        course_data = self.graph.nodes[failed_course]
        
        # Calculate impact using graph relationships
        impact_analysis = {
            'failed_course': failed_course,
            'failure_semester': failure_semester,
            'course_data': course_data,
            'blocked_courses': self.find_blocked_courses(failed_course),
            'timeline_impact': self.calculate_timeline_impact(failed_course, failure_semester),
            'recovery_options': self.generate_recovery_options(failed_course, failure_semester),
            'graduation_prediction': self.predict_graduation_timeline(failed_course, failure_semester, student_context),
            'specific_recommendations': self.generate_specific_recommendations(failed_course, failure_semester)
        }
        
        return impact_analysis
    
    def find_blocked_courses(self, failed_course: str) -> List[Dict]:
        """Find all courses blocked by the failure using graph traversal"""
        self.logger.info(f"🔍 FINDING: Courses blocked by {failed_course}")
        
        blocked = []
        visited = set()
        
        def find_dependent_courses(course, depth=0):
            if course in visited or depth > 4:  # Prevent infinite loops
                return
            
            visited.add(course)
            
            # Find direct dependents (courses that require this one)
            for successor in self.graph.successors(course):
                if self.graph.nodes[successor].get('type') == 'course':
                    edge_data = self.graph.get_edge_data(course, successor, {})
                    if edge_data.get('relationship') in ['prerequisite', 'corequisite']:
                        
                        # Get course details from graph
                        successor_data = self.graph.nodes[successor]
                        
                        blocked_info = {
                            'course': successor,
                            'title': successor_data.get('title', 'Unknown Title'),
                            'credits': successor_data.get('credits', 3),
                            'typical_semester': successor_data.get('typical_semester', 'unknown'),
                            'difficulty': successor_data.get('difficulty', 3.0),
                            'dependency_type': edge_data.get('relationship', 'prerequisite'),
                            'depth': depth + 1
                        }
                        
                        blocked.append(blocked_info)
                        
                        # Recursively find courses blocked by this one
                        find_dependent_courses(successor, depth + 1)
        
        # Start the recursive search
        find_dependent_courses(failed_course)
        
        self.logger.info(f"📊 FOUND: {len(blocked)} courses blocked by {failed_course}")
        return blocked
    
    def calculate_timeline_impact(self, failed_course: str, failure_semester: str) -> Dict:
        """Calculate exact timeline impact using graph data"""
        self.logger.info(f"🔍 CALCULATING: Timeline impact for {failed_course}")
        
        course_data = self.graph.nodes[failed_course]
        
        # Determine course importance from graph
        is_foundation = course_data.get('category') == 'foundation'
        is_critical = failed_course in self.degree_progression['critical_path_courses']
        is_gateway = course_data.get('gateway_to_tracks', False)
        
        # Calculate retake timeline
        offered_semesters = course_data.get('offered_semesters', ['fall', 'spring'])
        retake_delay = self.calculate_retake_delay(failure_semester, offered_semesters)
        
        # Calculate chain delay impact
        blocked_courses = self.find_blocked_courses(failed_course)
        chain_delay = self.calculate_chain_delay(blocked_courses, retake_delay)
        
        # Determine overall graduation delay
        graduation_delay = 0
        if is_critical and chain_delay > 0:
            graduation_delay = max(retake_delay, 1)  # At least 1 semester for critical courses
        elif len(blocked_courses) > 3:  # Many dependent courses
            graduation_delay = 1
        elif retake_delay > 1:  # Course not offered frequently
            graduation_delay = retake_delay
        
        timeline_impact = {
            'retake_delay_semesters': retake_delay,
            'chain_delay_semesters': chain_delay,
            'graduation_delay_semesters': graduation_delay,
            'is_critical_course': is_critical,
            'is_foundation_course': is_foundation,
            'is_gateway_course': is_gateway,
            'blocked_courses_count': len(blocked_courses),
            'can_graduate_on_time': graduation_delay == 0,
            'earliest_retake': self.determine_earliest_retake(failure_semester, offered_semesters),
            'impact_severity': self.categorize_impact_severity(graduation_delay, len(blocked_courses))
        }
        
        return timeline_impact
    
    def calculate_retake_delay(self, failure_semester: str, offered_semesters: List[str]) -> int:
        """Calculate how many semesters until course can be retaken"""
        
        # Map failure semester to next available offering
        semester_order = ['fall', 'spring', 'summer']
        
        # Extract current semester info
        if 'fall' in failure_semester.lower():
            current_term = 'fall'
        elif 'spring' in failure_semester.lower():
            current_term = 'spring'
        else:
            current_term = 'fall'  # Default
        
        # Find next available offering
        if 'spring' in offered_semesters and current_term == 'fall':
            return 0  # Can retake next semester
        elif 'summer' in offered_semesters:
            return 0  # Can retake in summer
        elif 'fall' in offered_semesters and current_term == 'spring':
            return 0  # Can retake next semester
        else:
            return 1  # Must wait a full year
    
    def calculate_chain_delay(self, blocked_courses: List[Dict], retake_delay: int) -> int:
        """Calculate delay caused by prerequisite chain disruption"""
        
        if not blocked_courses:
            return 0
        
        # Find courses in critical sequence (foundation courses)
        critical_blocked = [c for c in blocked_courses 
                          if c['course'] in ['CS 18200', 'CS 24000', 'CS 25000', 'CS 25100', 'CS 25200', 'CS 38100']]
        
        if critical_blocked:
            return retake_delay + 1  # Additional semester for chain impact
        
        return retake_delay
    
    def categorize_impact_severity(self, graduation_delay: int, blocked_count: int) -> str:
        """Categorize the severity of the failure impact"""
        
        if graduation_delay == 0 and blocked_count <= 2:
            return 'LOW'
        elif graduation_delay <= 1 and blocked_count <= 4:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def determine_earliest_retake(self, failure_semester: str, offered_semesters: List[str]) -> str:
        """Determine when the course can earliest be retaken"""
        
        if 'fall' in failure_semester.lower():
            if 'spring' in offered_semesters:
                return 'Spring (next semester)'
            elif 'summer' in offered_semesters:
                return 'Summer (same academic year)'
            else:
                return 'Fall (next academic year)'
        
        elif 'spring' in failure_semester.lower():
            if 'summer' in offered_semesters:
                return 'Summer (same academic year)'
            elif 'fall' in offered_semesters:
                return 'Fall (next semester)'
            else:
                return 'Spring (next academic year)'
        
        return 'Next available offering'
    
    def predict_graduation_timeline(self, failed_course: str, failure_semester: str, 
                                  student_context: Dict = None) -> Dict:
        """Predict graduation timeline with various scenarios"""
        
        timeline_impact = self.calculate_timeline_impact(failed_course, failure_semester)
        base_delay = timeline_impact['graduation_delay_semesters']
        
        # Get student context or use defaults
        current_year = student_context.get('year', 'freshman') if student_context else 'freshman'
        completed_credits = student_context.get('completed_credits', 15) if student_context else 15
        
        scenarios = {
            'best_case': {
                'timeline': '4 years' if base_delay == 0 else f'4 years + {base_delay} semester(s)',
                'requirements': [
                    f'Retake {failed_course} at earliest opportunity',
                    'Take summer courses if needed',
                    'Maintain normal course load'
                ],
                'probability': 'High' if base_delay <= 1 else 'Medium'
            },
            'typical_case': {
                'timeline': '4 years' if base_delay == 0 else f'4.5 years',
                'requirements': [
                    f'Retake {failed_course} next regular semester',
                    'Adjust subsequent semester plans',
                    'May need lighter course loads'
                ],
                'probability': 'High'
            },
            'worst_case': {
                'timeline': f'4.5-5 years',
                'requirements': [
                    'Multiple course retakes needed',
                    'Significant schedule adjustments',
                    'Consider summer/winter sessions'
                ],
                'probability': 'Low' if base_delay <= 1 else 'Medium'
            }
        }
        
        return {
            'scenarios': scenarios,
            'recommended_scenario': 'best_case' if base_delay <= 1 else 'typical_case',
            'graduation_feasible': True,
            'additional_semesters_needed': base_delay
        }
    
    def generate_recovery_options(self, failed_course: str, failure_semester: str) -> List[Dict]:
        """Generate specific recovery options"""
        
        course_data = self.graph.nodes[failed_course]
        offered_semesters = course_data.get('offered_semesters', ['fall', 'spring'])
        
        recovery_options = []
        
        # Option 1: Immediate retake
        earliest_retake = self.determine_earliest_retake(failure_semester, offered_semesters)
        recovery_options.append({
            'option': 'immediate_retake',
            'title': 'Immediate Retake Strategy',
            'timeline': earliest_retake,
            'description': f'Retake {failed_course} at the earliest opportunity',
            'pros': ['Minimal delay', 'Get back on track quickly'],
            'cons': ['May conflict with planned courses', 'Added academic pressure'],
            'recommended': True
        })
        
        # Option 2: Summer/Winter session
        if 'summer' in offered_semesters:
            recovery_options.append({
                'option': 'summer_retake',
                'title': 'Summer Session Retake',
                'timeline': 'Summer session',
                'description': f'Retake {failed_course} during summer',
                'pros': ['Focused attention on single course', 'Back on track by fall'],
                'cons': ['Summer session costs', 'Intensive pace'],
                'recommended': True
            })
        
        # Option 3: Delayed retake with course substitution
        recovery_options.append({
            'option': 'delayed_with_substitution',
            'title': 'Strategic Delay with Course Substitution',
            'timeline': 'Next academic year',
            'description': 'Take other required courses while waiting to retake',
            'pros': ['Less academic pressure', 'Complete other requirements'],
            'cons': ['Delays prerequisite chain', 'May affect graduation timeline'],
            'recommended': False
        })
        
        return recovery_options
    
    def generate_specific_recommendations(self, failed_course: str, failure_semester: str) -> List[str]:
        """Generate specific actionable recommendations"""
        
        timeline_impact = self.calculate_timeline_impact(failed_course, failure_semester)
        blocked_courses = self.find_blocked_courses(failed_course)
        
        recommendations = []
        
        # Course-specific recommendations
        if failed_course == 'CS 18000':
            recommendations.extend([
                'Focus on fundamental programming concepts before retaking',
                'Consider tutoring or supplemental instruction',
                'Practice with basic Java programming exercises',
                'Meet with academic advisor to discuss study strategies'
            ])
        elif failed_course == 'CS 25100':
            recommendations.extend([
                'Review data structures concepts thoroughly',
                'Practice algorithm implementation in C',
                'Consider forming study groups with classmates',
                'Use online resources for additional practice'
            ])
        
        # General recommendations based on impact
        if timeline_impact['can_graduate_on_time']:
            recommendations.append('Good news: You can still graduate in 4 years with proper planning')
        else:
            recommendations.append(f'Plan for {timeline_impact["graduation_delay_semesters"]} additional semester(s)')
        
        # Blocked course recommendations
        if len(blocked_courses) > 0:
            recommendations.append(f'Focus on completing {len(blocked_courses)} blocked courses after retake')
            
        # Timeline-specific recommendations
        recommendations.extend([
            f'Retake {failed_course} at: {timeline_impact["earliest_retake"]}',
            'Meet with academic advisor immediately to adjust schedule',
            'Consider lighter course load during retake semester'
        ])
        
        return recommendations
    
    def generate_specific_response(self, failed_course: str, failure_semester: str, 
                                 student_context: Dict = None) -> str:
        """Generate a specific, detailed response about course failure impact"""
        
        analysis = self.analyze_course_failure(failed_course, failure_semester, student_context)
        
        if 'error' in analysis:
            return f"I'm sorry, I couldn't find information about {failed_course} in our knowledge base."
        
        timeline = analysis['timeline_impact']
        blocked = analysis['blocked_courses']
        prediction = analysis['graduation_prediction']
        
        # Build specific response
        response_parts = []
        
        # Main graduation timeline answer
        if timeline['can_graduate_on_time']:
            response_parts.append(f"**You can still graduate in 4 years** after failing {failed_course}.")
        else:
            delay = timeline['graduation_delay_semesters']
            response_parts.append(f"**You will likely need {delay} extra semester(s)** to graduate.")
        
        # Immediate impact
        response_parts.append(f"\n**Immediate Impact:**")
        response_parts.append(f"• {len(blocked)} courses are now blocked by this failure")
        if blocked:
            key_blocked = [c['course'] for c in blocked[:3]]  # Show first 3
            response_parts.append(f"• Key blocked courses: {', '.join(key_blocked)}")
        
        # Retake timeline
        response_parts.append(f"\n**Retake Timeline:**")
        response_parts.append(f"• Earliest retake: {timeline['earliest_retake']}")
        response_parts.append(f"• Impact severity: {timeline['impact_severity']}")
        
        # Specific recommendations
        recommendations = analysis['specific_recommendations']
        response_parts.append(f"\n**Immediate Next Steps:**")
        for i, rec in enumerate(recommendations[:4], 1):
            response_parts.append(f"• {rec}")
        
        # Recovery strategy
        scenarios = prediction['scenarios']
        best_case = scenarios['best_case']
        response_parts.append(f"\n**Recovery Strategy:**")
        response_parts.append(f"• Best case timeline: {best_case['timeline']}")
        response_parts.append(f"• Probability: {best_case['probability']}")
        
        return '\n'.join(response_parts)

def test_dynamic_analyzer():
    """Test the dynamic course failure analyzer"""
    
    # Load existing knowledge graph
    try:
        with open('comprehensive_knowledge_graph.json', 'r') as f:
            graph_data = json.load(f)
    except:
        print("❌ Could not load knowledge graph")
        return
    
    # Create NetworkX graph
    graph = nx.DiGraph()
    
    # Add nodes
    for node_data in graph_data.get('nodes', []):
        node_id = node_data['id']
        graph.add_node(node_id, **node_data)
    
    # Add edges
    for edge_data in graph_data.get('edges', []):
        source = edge_data['source']
        target = edge_data['target']
        graph.add_edge(source, target, **edge_data)
    
    # Test analyzer
    analyzer = DynamicCourseFailureAnalyzer(graph)
    
    # Test CS 180 failure
    print("🧪 Testing CS 180 failure analysis...")
    response = analyzer.generate_specific_response('CS 18000', 'freshman_fall')
    print("Response:", response)
    
    # Test CS 251 failure
    print("\n🧪 Testing CS 25100 failure analysis...")
    response2 = analyzer.generate_specific_response('CS 25100', 'sophomore_fall')
    print("Response:", response2)

if __name__ == "__main__":
    test_dynamic_analyzer()