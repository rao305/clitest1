#!/usr/bin/env python3
"""
Advanced Query Logger
Comprehensive logging system to track every step of query processing
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging
import traceback

@dataclass
class QueryStep:
    """Represents a step in query processing"""
    step_id: str
    step_name: str
    timestamp: str
    duration_ms: float
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

@dataclass
class QuerySession:
    """Represents a complete query processing session"""
    session_id: str
    query: str
    start_time: str
    end_time: Optional[str] = None
    total_duration_ms: float = 0.0
    steps: List[QueryStep] = None
    final_response: str = ""
    ai_method_used: str = ""
    knowledge_nodes_accessed: List[str] = None
    template_used: bool = False
    nlp_processing_used: bool = False
    graph_traversal_used: bool = False

class AdvancedQueryLogger:
    """Advanced logging system for query processing"""
    
    def __init__(self, log_file: str = "query_processing.log"):
        self.log_file = log_file
        self.logger = logging.getLogger(__name__)
        self.sessions: Dict[str, QuerySession] = {}
        
        # Set up file logging
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
    def start_session(self, query: str) -> str:
        """Start a new query processing session"""
        session_id = str(uuid.uuid4())
        session = QuerySession(
            session_id=session_id,
            query=query,
            start_time=datetime.now().isoformat(),
            steps=[],
            knowledge_nodes_accessed=[]
        )
        self.sessions[session_id] = session
        
        self.logger.info(f"🚀 SESSION_STARTED: {session_id}")
        self.logger.info(f"📝 Query: {query}")
        self.logger.info("=" * 80)
        
        return session_id
    
    def log_step(self, session_id: str, step_name: str, input_data: Dict[str, Any], 
                 output_data: Dict[str, Any], success: bool = True, 
                 error_message: Optional[str] = None) -> str:
        """Log a processing step"""
        if session_id not in self.sessions:
            self.logger.error(f"Session {session_id} not found")
            return ""
        
        step_id = str(uuid.uuid4())
        start_time = time.time()
        
        step = QueryStep(
            step_id=step_id,
            step_name=step_name,
            timestamp=datetime.now().isoformat(),
            duration_ms=0.0,  # Will be calculated when step completes
            input_data=input_data,
            output_data=output_data,
            success=success,
            error_message=error_message
        )
        
        self.sessions[session_id].steps.append(step)
        
        # Log step details
        self.logger.info(f"🔍 STEP: {step_name}")
        self.logger.info(f"📥 Input: {json.dumps(input_data, indent=2)}")
        self.logger.info(f"📤 Output: {json.dumps(output_data, indent=2)}")
        self.logger.info(f"✅ Success: {success}")
        if error_message:
            self.logger.error(f"❌ Error: {error_message}")
        self.logger.info("-" * 60)
        
        return step_id
    
    def log_knowledge_node_access(self, session_id: str, node_id: str, node_type: str, 
                                 access_type: str, data_retrieved: Dict[str, Any]):
        """Log when knowledge nodes are accessed"""
        if session_id not in self.sessions:
            return
        
        self.sessions[session_id].knowledge_nodes_accessed.append(node_id)
        
        self.logger.info(f"🧠 KNOWLEDGE_NODE_ACCESS: {node_id}")
        self.logger.info(f"📊 Type: {node_type}")
        self.logger.info(f"🔗 Access: {access_type}")
        self.logger.info(f"📄 Data: {json.dumps(data_retrieved, indent=2)}")
        self.logger.info("-" * 40)
    
    def log_graph_traversal(self, session_id: str, start_node: str, end_node: str, 
                           path: List[str], traversal_type: str):
        """Log graph traversal operations"""
        self.logger.info(f"🕸️ GRAPH_TRAVERSAL: {start_node} -> {end_node}")
        self.logger.info(f"📈 Type: {traversal_type}")
        self.logger.info(f"🛤️ Path: {' -> '.join(path)}")
        self.logger.info(f"📏 Path length: {len(path)}")
        self.logger.info("-" * 40)
        
        if session_id in self.sessions:
            self.sessions[session_id].graph_traversal_used = True
    
    def log_nlp_processing(self, session_id: str, nlp_method: str, entities: List[str], 
                          concepts: List[str], intent: str):
        """Log NLP processing operations"""
        self.logger.info(f"🧠 NLP_PROCESSING: {nlp_method}")
        self.logger.info(f"🏷️ Entities: {entities}")
        self.logger.info(f"💡 Concepts: {concepts}")
        self.logger.info(f"🎯 Intent: {intent}")
        self.logger.info("-" * 40)
        
        if session_id in self.sessions:
            self.sessions[session_id].nlp_processing_used = True
    
    def log_template_detection(self, session_id: str, template_name: str, 
                              template_content: str):
        """Log when templates are used"""
        self.logger.warning(f"⚠️ TEMPLATE_DETECTED: {template_name}")
        self.logger.warning(f"📋 Content: {template_content[:100]}...")
        self.logger.warning("-" * 40)
        
        if session_id in self.sessions:
            self.sessions[session_id].template_used = True
    
    def log_ai_method_used(self, session_id: str, method_name: str, 
                          method_details: Dict[str, Any]):
        """Log which AI method was used"""
        self.logger.info(f"🤖 AI_METHOD: {method_name}")
        self.logger.info(f"📋 Details: {json.dumps(method_details, indent=2)}")
        self.logger.info("-" * 40)
        
        if session_id in self.sessions:
            self.sessions[session_id].ai_method_used = method_name
    
    def end_session(self, session_id: str, final_response: str):
        """End a query processing session"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        session.end_time = datetime.now().isoformat()
        session.final_response = final_response
        
        # Calculate total duration
        start_time = datetime.fromisoformat(session.start_time)
        end_time = datetime.fromisoformat(session.end_time)
        session.total_duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Log session summary
        self.logger.info("=" * 80)
        self.logger.info(f"🏁 SESSION_COMPLETED: {session_id}")
        self.logger.info(f"⏱️ Total duration: {session.total_duration_ms:.2f}ms")
        self.logger.info(f"📊 Steps completed: {len(session.steps)}")
        self.logger.info(f"🧠 Knowledge nodes accessed: {len(session.knowledge_nodes_accessed)}")
        self.logger.info(f"🤖 AI method used: {session.ai_method_used}")
        self.logger.info(f"🧠 NLP processing: {session.nlp_processing_used}")
        self.logger.info(f"🕸️ Graph traversal: {session.graph_traversal_used}")
        self.logger.info(f"⚠️ Template used: {session.template_used}")
        self.logger.info(f"📝 Final response length: {len(final_response)}")
        self.logger.info("=" * 80)
        
        # Log detailed analysis
        self._log_session_analysis(session)
    
    def _log_session_analysis(self, session: QuerySession):
        """Log detailed analysis of the session"""
        self.logger.info("📊 DETAILED SESSION ANALYSIS:")
        
        # Analyze steps
        successful_steps = [s for s in session.steps if s.success]
        failed_steps = [s for s in session.steps if not s.success]
        
        self.logger.info(f"✅ Successful steps: {len(successful_steps)}")
        self.logger.info(f"❌ Failed steps: {len(failed_steps)}")
        
        # Analyze knowledge node usage
        if session.knowledge_nodes_accessed:
            self.logger.info(f"🧠 Knowledge nodes accessed: {session.knowledge_nodes_accessed}")
        else:
            self.logger.warning("⚠️ No knowledge nodes were accessed!")
        
        # Analyze AI method effectiveness
        if session.template_used:
            self.logger.warning("⚠️ TEMPLATE WAS USED - This indicates hardcoded response!")
        else:
            self.logger.info("✅ No templates used - Dynamic processing detected")
        
        if session.nlp_processing_used:
            self.logger.info("✅ NLP processing was used")
        else:
            self.logger.warning("⚠️ No NLP processing detected")
        
        if session.graph_traversal_used:
            self.logger.info("✅ Graph traversal was used")
        else:
            self.logger.warning("⚠️ No graph traversal detected")
        
        # Log step details
        self.logger.info("📋 STEP DETAILS:")
        for i, step in enumerate(session.steps, 1):
            self.logger.info(f"  {i}. {step.step_name} ({step.duration_ms:.2f}ms)")
            if not step.success:
                self.logger.error(f"     ❌ Failed: {step.error_message}")
        
        self.logger.info("=" * 80)
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of a session"""
        if session_id not in self.sessions:
            return {}
        
        session = self.sessions[session_id]
        return {
            "session_id": session.session_id,
            "query": session.query,
            "duration_ms": session.total_duration_ms,
            "steps_count": len(session.steps),
            "knowledge_nodes_accessed": session.knowledge_nodes_accessed,
            "ai_method_used": session.ai_method_used,
            "nlp_processing_used": session.nlp_processing_used,
            "graph_traversal_used": session.graph_traversal_used,
            "template_used": session.template_used,
            "response_length": len(session.final_response)
        }
    
    def get_all_sessions_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all sessions"""
        return [self.get_session_summary(session_id) for session_id in self.sessions.keys()]
    
    def export_session_details(self, session_id: str, filename: str = None):
        """Export detailed session information to JSON"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        if not filename:
            filename = f"session_{session_id}.json"
        
        with open(filename, 'w') as f:
            json.dump(asdict(session), f, indent=2)
        
        self.logger.info(f"📄 Session exported to {filename}")
    
    def clear_sessions(self):
        """Clear all sessions"""
        self.sessions.clear()
        self.logger.info("🗑️ All sessions cleared") 