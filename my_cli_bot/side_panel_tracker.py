#!/usr/bin/env python3
"""
Side Panel Real-Time Tracker
Displays query processing logs in a side panel format alongside the main chat
"""

import threading
import time
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import queue

class SidePanelTracker:
    def __init__(self, width=60):
        self.width = width
        self.log_queue = queue.Queue()
        self.active = True
        self.current_query_id = 0
        self.tracking_thread = None
        self.is_running = False
        
    def start_side_panel_display(self):
        """Start the side panel display thread"""
        if self.is_running:
            return
        
        self.active = True
        self.is_running = True
        self.tracking_thread = threading.Thread(target=self._display_side_panel, daemon=True)
        self.tracking_thread.start()
    
    def _display_side_panel(self):
        """Display logs in side panel format"""
        print(f"\n{'=' * self.width}")
        print(f"{'REAL-TIME QUERY TRACKER':^{self.width}}")
        print(f"{'=' * self.width}")
        
        while self.active:
            try:
                log_entry = self.log_queue.get(timeout=1)
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                # Format log entry for side panel
                formatted_log = f"[{timestamp}] {log_entry}"
                
                # Wrap long lines
                if len(formatted_log) > self.width:
                    formatted_log = formatted_log[:self.width-3] + "..."
                
                print(f"{formatted_log:<{self.width}}")
                sys.stdout.flush()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Tracker error: {e}")
    
    def log_query_start(self, query: str, query_id: int):
        """Log query start"""
        self.current_query_id = query_id
        short_query = query[:40] + "..." if len(query) > 40 else query
        self.log_queue.put(f"🔍 Q#{query_id:02d} START: {short_query}")
    
    def log_intent_classification(self, query_id: int, intent: str, confidence: float):
        """Log intent classification"""
        self.log_queue.put(f"🎯 Q#{query_id:02d} INTENT: {intent} ({confidence:.2f})")
    
    def log_context_extraction(self, query_id: int, context: Dict):
        """Log context extraction"""
        context_items = []
        if context.get('course_codes'):
            context_items.append(f"Courses: {', '.join(context['course_codes'])}")
        if context.get('student_year'):
            context_items.append(f"Year: {context['student_year']}")
        
        context_str = "; ".join(context_items) if context_items else "None"
        self.log_queue.put(f"🔎 Q#{query_id:02d} CONTEXT: {context_str}")
    
    def log_routing_decision(self, query_id: int, route: str):
        """Log routing decision"""
        self.log_queue.put(f"🚦 Q#{query_id:02d} ROUTE: {route}")
    
    def log_knowledge_graph_query(self, query_id: int, operation: str, result_count: int = None):
        """Log knowledge graph operations"""
        result_info = f" → {result_count} results" if result_count is not None else ""
        self.log_queue.put(f"📊 Q#{query_id:02d} GRAPH: {operation}{result_info}")
    
    def log_response_generation(self, query_id: int, response_type: str, char_count: int):
        """Log response generation"""
        self.log_queue.put(f"💬 Q#{query_id:02d} RESPONSE: {response_type} ({char_count} chars)")
    
    def log_query_complete(self, query_id: int, duration: float, success: bool):
        """Log query completion"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        self.log_queue.put(f"🏁 Q#{query_id:02d} DONE: {duration:.3f}s {status}")
        self.log_queue.put("─" * 50)
    
    def log_custom(self, message: str):
        """Log custom message"""
        self.log_queue.put(message)
    
    def stop(self):
        """Stop the side panel tracker"""
        self.active = False
        self.is_running = False

class DualPanelChat:
    """Chat interface with side panel tracking"""
    
    def __init__(self):
        self.side_tracker = SidePanelTracker()
        
    def start_dual_panel_mode(self):
        """Start the dual panel chat mode"""
        # Clear screen and setup layout
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🤖 Enhanced Boiler AI - Dual Panel Mode")
        print("=" * 80)
        print("Main Chat Interface                    | Real-Time Query Tracker")
        print("=" * 80)
        
        # Start side panel tracker
        self.side_tracker.start_side_panel_display()
        
        return self.side_tracker
    
    def format_dual_output(self, main_content: str, tracker_content: str = ""):
        """Format output for dual panel display"""
        main_lines = main_content.split('\n')
        tracker_lines = tracker_content.split('\n') if tracker_content else []
        
        max_lines = max(len(main_lines), len(tracker_lines))
        
        for i in range(max_lines):
            main_line = main_lines[i] if i < len(main_lines) else ""
            tracker_line = tracker_lines[i] if i < len(tracker_lines) else ""
            
            # Format with fixed width columns
            print(f"{main_line:<40} | {tracker_line}")