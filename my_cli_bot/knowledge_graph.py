#!/usr/bin/env python3
"""
Purdue CS Knowledge Graph Implementation
Real-time knowledge graph with course and prerequisite information
"""

import json
import networkx as nx
from datetime import datetime
import os

class PurdueCSKnowledgeGraph:
    def __init__(self):
        """Initialize the knowledge graph"""
        self.graph = nx.DiGraph()
        self.courses = {}
        self.tracks = {}
        self.prerequisites = {}
        
    def load_graph(self, graph_path):
        """Load knowledge graph from file"""
        if os.path.exists(graph_path):
            with open(graph_path, 'r') as f:
                data = json.load(f)
                
            # Load courses
            self.courses = data.get('courses', {})
            
            # Load tracks
            self.tracks = data.get('tracks', {})
            
            # Load prerequisites
            self.prerequisites = data.get('prerequisites', {})
            
            # Build NetworkX graph
            for course_id, course_data in self.courses.items():
                self.graph.add_node(course_id, **course_data)
                
            for course_id, prereqs in self.prerequisites.items():
                for prereq in prereqs:
                    self.graph.add_edge(prereq, course_id, relation='prerequisite')
                    
            print(f"✓ Loaded {len(self.courses)} courses and {len(self.prerequisites)} prerequisite relationships")
            return True
        else:
            print(f"⚠ Knowledge graph file not found: {graph_path}")
            return False
    
    def save_graph(self, graph_path):
        """Save knowledge graph to file"""
        data = {
            'courses': self.courses,
            'tracks': self.tracks,
            'prerequisites': self.prerequisites,
            'updated': datetime.now().isoformat()
        }
        
        with open(graph_path, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"✓ Saved knowledge graph to {graph_path}")
        
    def add_course(self, course_id, course_data):
        """Add a course to the knowledge graph"""
        self.courses[course_id] = course_data
        self.graph.add_node(course_id, **course_data)
        
    def add_prerequisite(self, course_id, prerequisite_id):
        """Add a prerequisite relationship"""
        if course_id not in self.prerequisites:
            self.prerequisites[course_id] = []
        
        if prerequisite_id not in self.prerequisites[course_id]:
            self.prerequisites[course_id].append(prerequisite_id)
            self.graph.add_edge(prerequisite_id, course_id, relation='prerequisite')
            
    def get_course_info(self, course_id):
        """Get course information"""
        return self.courses.get(course_id, {})
        
    def get_prerequisites(self, course_id):
        """Get prerequisites for a course"""
        return self.prerequisites.get(course_id, [])
        
    def get_track_requirements(self, track_name):
        """Get track requirements"""
        return self.tracks.get(track_name, {})
        
    def validate_course_sequence(self, course_list):
        """Validate if courses can be taken in sequence"""
        results = []
        
        for course in course_list:
            prereqs = self.get_prerequisites(course)
            missing_prereqs = []
            
            for prereq in prereqs:
                if prereq not in course_list[:course_list.index(course)]:
                    missing_prereqs.append(prereq)
                    
            results.append({
                'course': course,
                'valid': len(missing_prereqs) == 0,
                'missing_prerequisites': missing_prereqs
            })
            
        return results