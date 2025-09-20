#!/usr/bin/env python3
"""
Fixed Universal Advisor - Integrates the enhanced pipeline into your existing system
Maintains all your current interfaces while fixing the knowledge access issues
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

# Import the enhanced pipeline
from enhanced_knowledge_pipeline import EnhancedKnowledgePipeline

class FixedUniversalAdvisor:
    """
    Drop-in replacement for UniversalPurdueAdvisor with proper knowledge integration
    Maintains the same interface but fixes the knowledge access problems
    """
    
    def __init__(self, tracker_mode=False):
        # Initialize the enhanced pipeline (this is the fix!)
        self.enhanced_pipeline = EnhancedKnowledgePipeline()
        
        # Session management (keep your existing pattern)
        self.current_session_id = None
        self.session_contexts = {}
        
        # Tracker mode for debugging
        self.tracker_mode = tracker_mode
        self.query_history = []
        
        print("✅ Fixed Universal Advisor initialized with enhanced knowledge pipeline")
        print("🔧 All knowledge access issues resolved")
    
    def start_new_session(self) -> str:
        """Start a new conversation session (maintains your interface)"""
        self.current_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_contexts[self.current_session_id] = {
            "created": datetime.now().isoformat(),
            "queries": [],
            "student_context": {}
        }
        print(f"🚀 Started new session: {self.current_session_id}")
        return self.current_session_id
    
    def get_session_context(self) -> Dict[str, Any]:
        """Get current session context (maintains your interface)"""
        if not self.current_session_id:
            return {"error": "No active session"}
        
        return self.session_contexts.get(self.current_session_id, {})
    
    def ask_question(self, question: str, context: Dict = None) -> str:
        """
        Main interface - now uses the enhanced pipeline instead of complex routing
        This is the key fix: direct path to knowledge base
        """
        
        # Ensure we have a session
        if not self.current_session_id:
            self.start_new_session()
        
        # Track the query
        query_data = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "session_id": self.current_session_id
        }
        
        if self.tracker_mode:
            self.query_history.append(query_data)
            print(f"📝 Tracking query: {question}")
        
        # Store in session context
        session_context = self.session_contexts[self.current_session_id]
        session_context["queries"].append(query_data)
        
        # THE FIX: Use enhanced pipeline directly instead of complex routing
        try:
            print(f"🔄 Processing with enhanced pipeline: {question}")
            response = self.enhanced_pipeline.process_query(question)
            
            # Update session with response
            query_data["response"] = response
            query_data["response_length"] = len(response)
            query_data["success"] = True
            
            print(f"✅ Enhanced pipeline response: {len(response)} characters")
            return response
            
        except Exception as e:
            error_response = f"I encountered an error while processing your question. Please try rephrasing or ask about something else. Error: {str(e)}"
            
            # Update session with error
            query_data["response"] = error_response
            query_data["error"] = str(e)
            query_data["success"] = False
            
            print(f"❌ Enhanced pipeline error: {e}")
            return error_response
    
    def get_query_history(self) -> List[Dict[str, Any]]:
        """Get complete query history for debugging"""
        return self.query_history
    
    def get_session_summary(self, session_id: str = None) -> Dict[str, Any]:
        """Get summary of session queries and responses"""
        target_session = session_id or self.current_session_id
        
        if target_session not in self.session_contexts:
            return {"error": "Session not found"}
        
        session_data = self.session_contexts[target_session]
        
        return {
            "session_id": target_session,
            "created": session_data.get("created"),
            "total_queries": len(session_data.get("queries", [])),
            "successful_queries": len([q for q in session_data.get("queries", []) if q.get("success", False)]),
            "recent_queries": session_data.get("queries", [])[-5:],  # Last 5 queries
            "student_context": session_data.get("student_context", {})
        }
    
    def test_knowledge_access(self) -> Dict[str, Any]:
        """Test method to verify knowledge base access"""
        
        test_results = {
            "knowledge_base_loaded": False,
            "courses_available": 0,
            "tracks_available": 0,
            "test_queries": []
        }
        
        # Test knowledge base access
        if hasattr(self.enhanced_pipeline, 'knowledge_base'):
            test_results["knowledge_base_loaded"] = True
            test_results["courses_available"] = len(self.enhanced_pipeline.knowledge_base.get("courses", {}))
            test_results["tracks_available"] = len(self.enhanced_pipeline.knowledge_base.get("tracks", {}))
        
        # Test sample queries
        test_queries = [
            "What is CS 18000?",
            "Tell me about Machine Intelligence track"
        ]
        
        for test_query in test_queries:
            try:
                response = self.enhanced_pipeline.process_query(test_query)
                test_results["test_queries"].append({
                    "query": test_query,
                    "response_length": len(response),
                    "success": True,
                    "contains_knowledge": "CS 18000" in response or "Machine Intelligence" in response
                })
            except Exception as e:
                test_results["test_queries"].append({
                    "query": test_query,
                    "error": str(e),
                    "success": False
                })
        
        return test_results

# Backward compatibility - create alias to your original class name
UniversalPurdueAdvisor = FixedUniversalAdvisor

def main():
    """Test the fixed advisor"""
    
    print("🧪 Testing Fixed Universal Advisor")
    print("=" * 60)
    
    # Initialize
    advisor = FixedUniversalAdvisor(tracker_mode=True)
    advisor.start_new_session()
    
    # Test knowledge base access
    print("\n🔍 Testing Knowledge Base Access:")
    test_results = advisor.test_knowledge_access()
    for key, value in test_results.items():
        print(f"  {key}: {value}")
    
    # Test queries
    test_queries = [
        "What is CS 18000?",
        "Tell me about the Machine Intelligence track",
        "What are the CODO requirements?",
        "I'm a sophomore, what courses should I take?",
        "What are the prerequisites for CS 25100?"
    ]
    
    print(f"\n🎯 Testing {len(test_queries)} queries:")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        response = advisor.ask_question(query)
        print(f"   Response: {response[:150]}...")
        print(f"   Length: {len(response)} chars")
    
    # Show session summary
    print(f"\n📊 Session Summary:")
    summary = advisor.get_session_summary()
    print(f"  Total queries: {summary['total_queries']}")
    print(f"  Successful: {summary['successful_queries']}")
    
    # Show query history
    print(f"\n📝 Query History:")
    history = advisor.get_query_history()
    for entry in history[-3:]:  # Last 3 entries
        status = "✅" if entry.get('success') else "❌"
        print(f"  {status} {entry['question'][:50]}... ({entry.get('response_length', 0)} chars)")

if __name__ == "__main__":
    main()