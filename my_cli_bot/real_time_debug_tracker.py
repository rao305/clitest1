#!/usr/bin/env python3
"""
Real-Time Debug Tracker for Query Processing
Provides real-time logging and tracking of every step in the query processing pipeline
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Any
import threading
import queue
import sys
import re

class RealTimeDebugTracker:
    def __init__(self):
        self.query_id = 0
        self.active_queries = {}
        self.log_queue = queue.Queue()
        self.setup_logging()
        self.start_log_display_thread()
        
    def setup_logging(self):
        """Setup comprehensive logging system"""
        
        # Create formatters for different log levels
        self.formatters = {
            'QUERY': logging.Formatter('🔍 QUERY #{query_id}: {message}', style='{'),
            'GRAPH': logging.Formatter('📊 GRAPH #{query_id}: {message}', style='{'),
            'PROCESS': logging.Formatter('⚙️  PROCESS #{query_id}: {message}', style='{'),
            'RESULT': logging.Formatter('✅ RESULT #{query_id}: {message}', style='{'),
            'ERROR': logging.Formatter('❌ ERROR #{query_id}: {message}', style='{'),
            'DEBUG': logging.Formatter('🔧 DEBUG #{query_id}: {message}', style='{')
        }
        
        # Setup main logger
        self.logger = logging.getLogger('QueryTracker')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Add custom handler that feeds our queue
        self.handler = QueueHandler(self.log_queue)
        self.logger.addHandler(self.handler)
    
    def start_log_display_thread(self):
        """Start background thread to display logs in real-time"""
        self.log_thread = threading.Thread(target=self.display_logs, daemon=True)
        self.log_thread.start()
    
    def display_logs(self):
        """Display logs in real-time on terminal"""
        while True:
            try:
                log_record = self.log_queue.get(timeout=1)
                print(log_record)
                sys.stdout.flush()
            except queue.Empty:
                continue
    
    def start_query_tracking(self, query: str) -> int:
        """Start tracking a new query"""
        self.query_id += 1
        current_id = self.query_id
        
        self.active_queries[current_id] = {
            'query': query,
            'start_time': time.time(),
            'steps': [],
            'status': 'PROCESSING'
        }
        
        self.log_step(current_id, 'QUERY', f"Starting query: '{query}'")
        return current_id
    
    def log_step(self, query_id: int, step_type: str, message: str, data: Any = None):
        """Log a processing step"""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        
        if query_id in self.active_queries:
            self.active_queries[query_id]['steps'].append({
                'timestamp': timestamp,
                'type': step_type,
                'message': message,
                'data': data
            })
        
        # Format message with emoji and color
        emoji_map = {
            'QUERY': '🔍',
            'GRAPH': '📊', 
            'PROCESS': '⚙️',
            'RESULT': '✅',
            'ERROR': '❌',
            'DEBUG': '🔧',
            'CLASSIFY': '🎯',
            'EXTRACT': '🔎',
            'LOOKUP': '📋',
            'GENERATE': '💬',
            'ROUTE': '🚦'
        }
        
        emoji = emoji_map.get(step_type, '📌')
        formatted_message = f"{emoji} [{timestamp}] Q#{query_id:02d} {step_type}: {message}"
        
        if data:
            formatted_message += f" | Data: {str(data)[:100]}{'...' if len(str(data)) > 100 else ''}"
        
        self.log_queue.put(formatted_message)
    
    def log_graph_query(self, query_id: int, operation: str, result_count: int = None, details: str = None):
        """Log knowledge graph operations"""
        message = f"Graph {operation}"
        if result_count is not None:
            message += f" → {result_count} results"
        if details:
            message += f" | {details}"
        
        self.log_step(query_id, 'GRAPH', message)
    
    def log_classification(self, query_id: int, intent: str, confidence: float = None):
        """Log query classification results"""
        message = f"Classified as '{intent}'"
        if confidence:
            message += f" (confidence: {confidence:.2f})"
        
        self.log_step(query_id, 'CLASSIFY', message)
    
    def log_context_extraction(self, query_id: int, context: Dict):
        """Log context extraction results"""
        context_summary = []
        if context.get('course_codes'):
            context_summary.append(f"Courses: {', '.join(context['course_codes'])}")
        if context.get('student_year'):
            context_summary.append(f"Year: {context['student_year']}")
        if context.get('track_interest'):
            context_summary.append(f"Track: {context['track_interest']}")
        
        message = f"Extracted context: {'; '.join(context_summary) if context_summary else 'None'}"
        self.log_step(query_id, 'EXTRACT', message, context)
    
    def log_response_generation(self, query_id: int, response_length: int, response_type: str):
        """Log response generation"""
        message = f"Generated {response_type} response ({response_length} chars)"
        self.log_step(query_id, 'GENERATE', message)
    
    def log_routing_decision(self, query_id: int, route: str, reason: str):
        """Log routing decisions"""
        message = f"Routed to {route}: {reason}"
        self.log_step(query_id, 'ROUTE', message)
    
    def finish_query_tracking(self, query_id: int, success: bool = True):
        """Finish tracking a query"""
        if query_id in self.active_queries:
            end_time = time.time()
            duration = end_time - self.active_queries[query_id]['start_time']
            
            self.active_queries[query_id]['status'] = 'COMPLETED' if success else 'FAILED'
            self.active_queries[query_id]['duration'] = duration
            
            status_emoji = '✅' if success else '❌'
            self.log_step(query_id, 'RESULT', f"Query completed in {duration:.3f}s {status_emoji}")
            
            # Print separator for next query
            self.log_queue.put("─" * 80)

class QueueHandler(logging.Handler):
    """Custom logging handler that feeds a queue"""
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue
    
    def emit(self, record):
        self.log_queue.put(self.format(record))

class TrackedQueryProcessor:
    """Query processor with complete tracking capabilities"""
    
    def __init__(self, knowledge_graph, tracker: RealTimeDebugTracker):
        self.graph = knowledge_graph
        self.tracker = tracker
    
    def process_query_with_tracking(self, query: str) -> Dict[str, Any]:
        """Process query with complete tracking"""
        
        # Start tracking
        query_id = self.tracker.start_query_tracking(query)
        
        try:
            # Step 1: Query preprocessing
            self.tracker.log_step(query_id, 'PROCESS', 'Starting query preprocessing')
            cleaned_query = self.preprocess_query(query)
            self.tracker.log_step(query_id, 'PROCESS', f'Query cleaned: "{cleaned_query}"')
            
            # Step 2: Intent classification
            self.tracker.log_step(query_id, 'PROCESS', 'Classifying query intent')
            intent = self.classify_query_intent(query_id, cleaned_query)
            
            # Step 3: Context extraction
            self.tracker.log_step(query_id, 'PROCESS', 'Extracting context from query')
            context = self.extract_query_context(query_id, cleaned_query)
            
            # Step 4: Routing decision
            self.tracker.log_step(query_id, 'PROCESS', 'Determining processing route')
            route = self.determine_processing_route(query_id, intent, context, query)
            
            # Step 5: Knowledge graph lookup
            self.tracker.log_step(query_id, 'PROCESS', 'Querying knowledge graph')
            knowledge_data = self.query_knowledge_graph(query_id, intent, context)
            
            # Step 6: Response generation
            self.tracker.log_step(query_id, 'PROCESS', 'Generating response')
            response = self.generate_tracked_response(query_id, intent, context, knowledge_data, route)
            
            # Log completion
            self.tracker.log_response_generation(query_id, len(response), intent)
            self.tracker.finish_query_tracking(query_id, success=True)
            
            return {
                'response': response,
                'query_id': query_id,
                'intent': intent,
                'route': route,
                'success': True
            }
            
        except Exception as e:
            self.tracker.log_step(query_id, 'ERROR', f'Processing failed: {str(e)}')
            self.tracker.finish_query_tracking(query_id, success=False)
            return {
                'response': f"Error processing query: {str(e)}",
                'query_id': query_id,
                'success': False
            }
    
    def preprocess_query(self, query: str) -> str:
        """Preprocess query with tracking"""
        cleaned = query.strip()
        return cleaned
    
    def classify_query_intent(self, query_id: int, query: str) -> str:
        """Classify query intent with detailed tracking"""
        
        self.tracker.log_step(query_id, 'CLASSIFY', 'Starting intent classification')
        query_lower = query.lower()
        
        # Check for course failure patterns
        failure_patterns = ['fail', 'failed', 'failing', 'retake', 'will i graduate', 'can i graduate']
        if any(pattern in query_lower for pattern in failure_patterns):
            self.tracker.log_classification(query_id, 'course_failure', 0.9)
            return 'course_failure'
        
        # Check for track questions
        track_patterns = ['machine intelligence', 'software engineering', 'track', 'mi track', 'se track']
        if any(pattern in query_lower for pattern in track_patterns):
            self.tracker.log_classification(query_id, 'track_inquiry', 0.8)
            return 'track_inquiry'
        
        # Check for course info
        cs_pattern = r'cs\s*\d{3,5}'
        if re.search(cs_pattern, query_lower):
            self.tracker.log_classification(query_id, 'course_info', 0.85)
            return 'course_info'
        
        # Check for graduation timeline
        if 'graduate' in query_lower and ('4 years' in query_lower or 'time' in query_lower):
            self.tracker.log_classification(query_id, 'graduation_timeline', 0.8)
            return 'graduation_timeline'
        
        # Default
        self.tracker.log_classification(query_id, 'general', 0.3)
        return 'general'
    
    def extract_query_context(self, query_id: int, query: str) -> Dict:
        """Extract context with detailed tracking"""
        
        self.tracker.log_step(query_id, 'EXTRACT', 'Parsing query for context clues')
        query_lower = query.lower()
        
        context = {
            'course_codes': [],
            'student_year': None,
            'track_interest': None,
            'semester': None,
            'failure_context': False
        }
        
        # Extract course codes
        course_pattern = r'cs\s*(\d{3,5})'
        matches = re.findall(course_pattern, query_lower)
        
        for match in matches:
            if len(match) == 3:
                course_code = f'CS {match}00'
            else:
                course_code = f'CS {match}'
            context['course_codes'].append(course_code)
        
        # Extract student year
        year_patterns = {
            'freshman': ['freshman', 'fresh', 'first year', '1st year'],
            'sophomore': ['sophomore', 'soph', 'second year', '2nd year'],
            'junior': ['junior', 'third year', '3rd year'],
            'senior': ['senior', 'fourth year', '4th year']
        }
        
        for year, patterns in year_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                context['student_year'] = year
                break
        
        # Extract semester context
        if 'fall' in query_lower:
            context['semester'] = 'fall'
        elif 'spring' in query_lower:
            context['semester'] = 'spring'
        elif 'summer' in query_lower:
            context['semester'] = 'summer'
        
        # Check for failure context
        context['failure_context'] = any(word in query_lower for word in ['fail', 'failed', 'failing'])
        
        self.tracker.log_context_extraction(query_id, context)
        return context
    
    def determine_processing_route(self, query_id: int, intent: str, context: Dict, query: str) -> str:
        """Determine which processing route to use"""
        
        query_lower = query.lower()
        
        # Check for CS 180 failure specifically
        if ('cs 180' in query_lower or 'cs 18000' in query_lower) and context['failure_context']:
            route = 'knowledge_graph_advisor'
            reason = 'CS 180 failure detected - needs specific timeline analysis'
            self.tracker.log_routing_decision(query_id, route, reason)
            return route
        
        # Check for other course failures
        if intent == 'course_failure' and context['course_codes']:
            route = 'enhanced_smart_advisor'
            reason = f"Course failure for {context['course_codes']} - needs enhanced analysis"
            self.tracker.log_routing_decision(query_id, route, reason)
            return route
        
        # Default to friendly advisor
        route = 'friendly_advisor'
        reason = 'General query - using friendly advisor'
        self.tracker.log_routing_decision(query_id, route, reason)
        return route
    
    def query_knowledge_graph(self, query_id: int, intent: str, context: Dict) -> Dict:
        """Query knowledge graph with detailed tracking"""
        
        knowledge_data = {}
        
        # Query for course information
        if context['course_codes']:
            self.tracker.log_graph_query(query_id, 'course_lookup', len(context['course_codes']))
            for course in context['course_codes']:
                if hasattr(self.graph, 'get_course_info'):
                    course_info = self.graph.get_course_info(course)
                    knowledge_data[course] = course_info
        
        # Query for prerequisite chains
        if intent == 'course_failure':
            self.tracker.log_graph_query(query_id, 'prerequisite_analysis')
            # Add prerequisite analysis here
        
        return knowledge_data
    
    def generate_tracked_response(self, query_id: int, intent: str, context: Dict, knowledge_data: Dict, route: str) -> str:
        """Generate response with tracking"""
        
        self.tracker.log_step(query_id, 'GENERATE', f'Generating {intent} response via {route}')
        
        # Simple response generation for demonstration
        if route == 'knowledge_graph_advisor':
            response = "Based on knowledge graph analysis: You can still graduate in 4 years after failing CS 180."
        elif route == 'enhanced_smart_advisor':
            response = "Enhanced analysis shows specific course failure impact and recovery timeline."
        else:
            response = "General academic guidance provided."
        
        return response