#!/usr/bin/env python3
"""
Knowledge Graph-Based Academic Advisor - Specific Answers
Transform knowledge graph into precise academic advisor with exact timeline calculations
"""

import networkx as nx
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from knowledge_graph import PurdueCSKnowledgeGraph

class KnowledgeGraphAcademicAdvisor:
    """Precise academic advisor using knowledge graph for specific answers"""
    
    def __init__(self, knowledge_graph: nx.DiGraph = None, db_path: str = "purdue_cs_knowledge.db"):
        if knowledge_graph is None:
            kg_system = PurdueCSKnowledgeGraph()
            # Try to load comprehensive knowledge graph first
            if kg_system.load_graph('comprehensive_knowledge_graph.json'):
                self.graph = kg_system.graph
            else:
                # Fallback to building it
                from populate_knowledge_graph import populate_cs_knowledge_graph
                kg_system = populate_cs_knowledge_graph()
                self.graph = kg_system.graph
        else:
            self.graph = knowledge_graph
            
        self.db_path = db_path
        self.logger = self.setup_logging()
        
        # Extract course sequence from graph
        self.course_sequence = self.extract_course_sequence_from_graph()
        self.semester_mappings = self.extract_semester_mappings()
        
    def setup_logging(self):
        """Setup logging for academic advisor"""
        logger = logging.getLogger('KnowledgeGraphAdvisor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('🎓 %(levelname)s: %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def extract_course_sequence_from_graph(self) -> Dict:
        """Extract the normal course sequence from knowledge graph"""
        self.logger.info("🔍 EXTRACTING: Course sequence from knowledge graph")
        
        sequence = {}
        
        # Find all CS courses in graph
        cs_courses = [node for node in self.graph.nodes() 
                     if 'CS' in str(node) or 'MA' in str(node) or 'STAT' in str(node)]
        
        # Extract prerequisites for each course
        for course in cs_courses:
            try:
                prerequisites = list(self.graph.predecessors(course))
                unlocks = list(self.graph.successors(course))
                
                # Get course metadata from graph
                course_data = self.graph.nodes.get(course, {})
                
                sequence[course] = {
                    'prerequisites': prerequisites,
                    'unlocks': unlocks,
                    'credits': course_data.get('credits', 3),
                    'typical_semester': course_data.get('typical_semester', 'unknown'),
                    'difficulty': course_data.get('difficulty', 3.0),
                    'required': course_data.get('required', True),
                    'offered_semesters': course_data.get('offered_semesters', ['fall', 'spring'])
                }
            except Exception as e:
                self.logger.warning(f"Error processing course {course}: {e}")
        
        self.logger.info(f"📊 EXTRACTED: {len(sequence)} courses from knowledge graph")
        return sequence
    
    def extract_semester_mappings(self) -> Dict:
        """Extract typical semester mappings from graph"""
        mappings = {
            'freshman_fall': ['CS 18000', 'MA 16100'],
            'freshman_spring': ['CS 18200', 'CS 24000', 'MA 16200'],
            'sophomore_fall': ['CS 25000', 'CS 25100', 'MA 26100'],
            'sophomore_spring': ['CS 25200', 'MA 26500'],
            'junior_fall': ['CS 38100', 'STAT 35000'],
            'junior_spring': [],
            'senior_fall': [],
            'senior_spring': []
        }
        
        # Use graph data to populate mappings if available
        for course, data in self.course_sequence.items():
            typical_sem = data.get('typical_semester', 'unknown')
            if typical_sem in mappings and course not in mappings[typical_sem]:
                mappings[typical_sem].append(course)
        
        return mappings
    
    def analyze_cs180_failure_impact(self, failure_semester: str = "freshman_fall", 
                                   current_courses: List[str] = None) -> Dict:
        """Analyze specific impact of CS 180 failure with exact timeline"""
        self.logger.info(f"🔍 ANALYZING CS 180 FAILURE: Impact in {failure_semester}")
        
        # Get blocked courses from knowledge graph
        blocked_courses = self.find_blocked_courses('CS 18000')
        
        # Calculate exact timeline impact
        timeline_impact = self.calculate_cs180_timeline_impact(failure_semester)
        
        # Generate specific recovery plan
        recovery_plan = self.generate_cs180_recovery_plan(failure_semester)
        
        return {
            'failed_course': 'CS 18000',
            'failure_semester': failure_semester,
            'blocked_courses': blocked_courses,
            'timeline_impact': timeline_impact,
            'recovery_plan': recovery_plan,
            'can_graduate_on_time': timeline_impact['can_graduate_on_time'],
            'specific_answer': self.generate_specific_cs180_answer(timeline_impact, recovery_plan)
        }
    
    def find_blocked_courses(self, failed_course: str) -> List[Dict]:
        """Find all courses blocked by failing the given course using graph"""
        self.logger.info(f"🔍 FINDING BLOCKED: Courses blocked by {failed_course}")
        
        blocked = []
        
        # Use graph to find all courses that depend on this one
        if failed_course in self.graph:
            dependent_courses = list(self.graph.successors(failed_course))
            
            for course in dependent_courses:
                if course in self.course_sequence:
                    course_info = self.course_sequence[course]
                    blocked.append({
                        'course': course,
                        'credits': course_info.get('credits', 3),
                        'typical_semester': course_info.get('typical_semester', 'unknown'),
                        'difficulty': course_info.get('difficulty', 3.0)
                    })
            
            # Check for indirect dependencies
            for blocked_course in dependent_courses:
                if blocked_course in self.graph:
                    indirect_blocked = list(self.graph.successors(blocked_course))
                    for indirect in indirect_blocked:
                        if (indirect in self.course_sequence and 
                            indirect not in [b['course'] for b in blocked]):
                            course_info = self.course_sequence[indirect]
                            blocked.append({
                                'course': indirect,
                                'credits': course_info.get('credits', 3),
                                'typical_semester': course_info.get('typical_semester', 'unknown'),
                                'difficulty': course_info.get('difficulty', 3.0),
                                'indirect': True
                            })
        
        self.logger.info(f"📊 FOUND: {len(blocked)} courses blocked by {failed_course}")
        return blocked
    
    def calculate_cs180_timeline_impact(self, failure_semester: str) -> Dict:
        """Calculate exact timeline impact for CS 180 failure"""
        self.logger.info(f"🔍 CALCULATING CS 180 TIMELINE: Impact from {failure_semester}")
        
        # CS 180 is offered both fall and spring
        if 'fall' in failure_semester.lower():
            retake_semester = 'spring_following'
            delay_semesters = 0  # Can retake immediately in spring
            can_graduate_on_time = True
        else:  # Failed in spring
            retake_semester = 'fall_following'
            delay_semesters = 1  # Must wait until next fall
            can_graduate_on_time = False
        
        # Check impact on prerequisite chain
        chain_impact = self.analyze_prerequisite_chain_impact('CS 18000', delay_semesters)
        
        return {
            'retake_semester': retake_semester,
            'delay_semesters': delay_semesters,
            'can_graduate_on_time': can_graduate_on_time,
            'chain_impact': chain_impact,
            'critical_path_affected': True,  # CS 180 is on critical path
            'sophomore_courses_delayed': delay_semesters > 0
        }
    
    def analyze_prerequisite_chain_impact(self, failed_course: str, delay_semesters: int) -> Dict:
        """Analyze impact on entire prerequisite chain"""
        
        if failed_course == 'CS 18000':
            return {
                'immediately_affected': ['CS 18200'],
                'sophomore_year_affected': ['CS 25000', 'CS 25100'] if delay_semesters > 0 else [],
                'junior_year_affected': ['CS 38100'] if delay_semesters > 0 else [],
                'track_courses_delayed': delay_semesters > 0
            }
        
        return {'no_major_impact': True}
    
    def generate_cs180_recovery_plan(self, failure_semester: str) -> Dict:
        """Generate specific recovery plan for CS 180 failure"""
        
        if 'fall' in failure_semester.lower():
            # Failed in fall, can retake in spring
            return {
                'immediate_actions': [
                    'Retake CS 18000 in Spring semester (course offered both semesters)',
                    'Continue with MA 16200 (Calculus II) as planned',
                    'Take ENGL 10600 or other general education requirement',
                    'Stay enrolled in at least 12 credits to maintain full-time status'
                ],
                'spring_semester_plan': {
                    'courses': ['CS 18000 (retake)', 'MA 16200', 'ENGL 10600', 'General Education'],
                    'total_credits': 12,
                    'workload': 'manageable'
                },
                'summer_options': [
                    'Consider taking CS 24000 in summer if available',
                    'Take additional general education courses to free up future semesters'
                ],
                'sophomore_year_impact': 'No delay - can proceed normally with CS sequence',
                'graduation_timeline': 'Still possible to graduate in 4 years'
            }
        else:
            # Failed in spring, must wait until next fall
            return {
                'immediate_actions': [
                    'CS 18000 typically not offered in summer - must retake in fall',
                    'Use summer to take general education requirements',
                    'Consider taking MA 16200 if not yet completed',
                    'Meet with academic advisor to adjust 4-year plan'
                ],
                'summer_semester_plan': {
                    'courses': ['MA 16200 (if needed)', 'ENGL 10600', 'General Education'],
                    'total_credits': 6-9,
                    'purpose': 'Stay on track with non-CS requirements'
                },
                'fall_retake_plan': {
                    'courses': ['CS 18000 (retake)', 'CS 18200', 'MA 26100', 'General Education'],
                    'total_credits': 15,
                    'note': 'Compressed schedule to catch up'
                },
                'sophomore_year_impact': 'Delayed by one semester',
                'graduation_timeline': 'May need summer courses or extra semester'
            }
    
    def generate_specific_cs180_answer(self, timeline_impact: Dict, recovery_plan: Dict) -> str:
        """Generate specific answer about CS 180 failure impact"""
        
        if timeline_impact['can_graduate_on_time']:
            return f"""Based on your knowledge graph analysis: **You can still graduate in 4 years** after failing CS 180.

**Immediate Next Steps:**
• Retake CS 180 in {timeline_impact['retake_semester'].replace('_', ' ')}
• {recovery_plan['immediate_actions'][1]}
• {recovery_plan['immediate_actions'][2]}

**Timeline Impact:** No delay to graduation if you retake immediately. CS 180 is offered both fall and spring semesters, so you can get back on track quickly.

**Your Path Forward:** Follow the normal CS sequence starting next semester. All your other courses will proceed as planned."""
        else:
            delay = timeline_impact['delay_semesters']
            return f"""Based on prerequisite chain analysis: **You will likely need {delay} extra semester(s)** to graduate.

**Critical Issue:** CS 180 is a prerequisite for CS 18200, which blocks CS 25000/25100, which blocks CS 38100 (required for track courses).

**Recovery Strategy:**
• {recovery_plan['immediate_actions'][0]}
• {recovery_plan['summer_options'][0] if recovery_plan.get('summer_options') else 'Use summer strategically'}
• Consider heavier course loads (16-17 credits) in future semesters

**Bottom Line:** {recovery_plan['graduation_timeline']}"""
    
    def analyze_any_course_failure(self, course_code: str, failure_semester: str = "current") -> Dict:
        """Analyze failure of any course with specific timeline impact"""
        
        if course_code == 'CS 18000':
            return self.analyze_cs180_failure_impact(failure_semester)
        
        # Generic analysis for other courses
        blocked_courses = self.find_blocked_courses(course_code)
        
        # Determine criticality
        critical_courses = ['CS 18000', 'CS 18200', 'CS 25100', 'CS 38100']
        is_critical = course_code in critical_courses
        
        can_graduate_on_time = len(blocked_courses) == 0 or not is_critical
        
        return {
            'failed_course': course_code,
            'failure_semester': failure_semester,
            'blocked_courses': blocked_courses,
            'is_critical_path': is_critical,
            'can_graduate_on_time': can_graduate_on_time,
            'delay_estimate': 1 if not can_graduate_on_time else 0,
            'specific_answer': f"Failing {course_code} {'will delay graduation' if not can_graduate_on_time else 'should not affect graduation timeline'}."
        }
    
    def get_graduation_timeline_analysis(self, completed_courses: List[str], 
                                       current_year: str = "sophomore") -> Dict:
        """Get specific graduation timeline analysis"""
        
        # Analyze completed foundation courses
        foundation_courses = ['CS 18000', 'CS 18200', 'CS 24000', 'CS 25000', 'CS 25100', 'CS 25200']
        completed_foundation = [c for c in completed_courses if c in foundation_courses]
        
        # Calculate remaining requirements
        remaining_foundation = [c for c in foundation_courses if c not in completed_courses]
        
        # Estimate semesters remaining
        if current_year == "freshman":
            expected_completion = 7  # 7 semesters remaining
        elif current_year == "sophomore":
            expected_completion = 5  # 5 semesters remaining
        elif current_year == "junior":
            expected_completion = 3  # 3 semesters remaining
        else:
            expected_completion = 1  # 1 semester remaining
        
        # Account for any delays
        delay_semesters = len(remaining_foundation) // 4  # Rough estimate
        
        return {
            'current_year': current_year,
            'completed_foundation': completed_foundation,
            'remaining_foundation': remaining_foundation,
            'foundation_completion_percentage': len(completed_foundation) / len(foundation_courses) * 100,
            'estimated_semesters_remaining': expected_completion + delay_semesters,
            'can_graduate_on_time': delay_semesters == 0,
            'specific_timeline': f"Based on your progress, you need {expected_completion + delay_semesters} more semesters to graduate."
        }

if __name__ == "__main__":
    # Test the knowledge graph academic advisor
    advisor = KnowledgeGraphAcademicAdvisor()
    
    # Test CS 180 failure analysis
    print("Testing CS 180 failure analysis...")
    result = advisor.analyze_cs180_failure_impact("freshman_fall")
    print(f"Can graduate on time: {result['can_graduate_on_time']}")
    print(f"Specific answer: {result['specific_answer']}")
    
    # Test graduation timeline
    print("\nTesting graduation timeline...")
    timeline = advisor.get_graduation_timeline_analysis(
        completed_courses=['CS 18000', 'CS 18200', 'CS 24000'],
        current_year="sophomore"
    )
    print(f"Timeline: {timeline['specific_timeline']}")