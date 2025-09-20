#!/usr/bin/env python3
"""
Enhanced CLI Chat with Session Management and Feedback Collection
Integrates all new features: sessions, feedback, multi-turn conversations
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Import our enhanced components
from session_manager import SessionManager
from feedback_system import FeedbackSystem, FeedbackPromptGenerator
from smart_ai_engine import SmartAIEngine
from knowledge_graph import PurdueCSKnowledgeGraph
from enhanced_database import EnhancedDatabase

class EnhancedBoilerAI:
    def __init__(self):
        # Initialize enhanced components
        self.session_manager = SessionManager()
        self.feedback_system = FeedbackSystem()
        self.smart_ai = SmartAIEngine()
        
        # Initialize enhanced database
        enhanced_db = EnhancedDatabase()
        
        self.current_session_id = None
        self.collect_feedback = True
        self.feedback_frequency = 3  # Ask for feedback every 3 responses
        self.response_count = 0
        
        print("🤖 Enhanced BoilerAI CLI Chat")
        print("=" * 50)
        print("Enhanced features:")
        print("✓ Multi-turn conversation memory")
        print("✓ User feedback collection")
        print("✓ Session context management")
        print("✓ Smart AI with personalized responses")
        print("✓ Comprehensive academic knowledge")
        print()
    
    def start_chat(self):
        """Start the enhanced chat session"""
        
        # Create new session
        self.current_session_id = self.session_manager.create_session()
        print(f"🔗 Session started: {self.current_session_id[:8]}...")
        print()
        
        # Main chat loop
        while True:
            try:
                user_input = input("You> ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if self._handle_special_commands(user_input):
                    continue
                
                # Process query with context
                response_data = self._process_query_with_context(user_input)
                
                # Display response
                print(f"Bot> {response_data['response']}")
                print()
                
                # Update session context
                context = self.session_manager.extract_context_from_query(user_input)
                self.session_manager.update_session(
                    self.current_session_id, 
                    user_input, 
                    response_data['response'], 
                    context
                )
                
                # Collect feedback periodically
                self.response_count += 1
                if self.collect_feedback and self.response_count % self.feedback_frequency == 0:
                    self._collect_feedback(user_input, response_data)
                
            except KeyboardInterrupt:
                print("\n👋 Thanks for using Enhanced BoilerAI!")
                self._show_session_summary()
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
    
    def _process_query_with_context(self, query: str) -> Dict[str, Any]:
        """Process query with session context"""
        
        # Get conversation context
        conversation_context = self.session_manager.get_conversation_context(self.current_session_id)
        
        # Extract query context
        query_context = self.session_manager.extract_context_from_query(query)
        
        # Combine contexts for AI prompt
        full_context = {
            'conversation_history': conversation_context,
            'query_context': query_context
        }
        
        # Generate intelligent response with context
        start_time = datetime.now()
        response_data = self.smart_ai.generate_intelligent_response(query, full_context)
        end_time = datetime.now()
        
        # Add response metadata
        response_data['response_time_ms'] = int((end_time - start_time).total_seconds() * 1000)
        response_data['session_id'] = self.current_session_id
        
        return response_data
    
    def _handle_special_commands(self, user_input: str) -> bool:
        """Handle special chat commands"""
        
        input_lower = user_input.lower()
        
        # Exit commands
        if input_lower in ['exit', 'quit', 'bye']:
            print("👋 Thanks for using Enhanced BoilerAI!")
            self._show_session_summary()
            sys.exit(0)
        
        # Help command
        elif input_lower in ['help', '?']:
            self._show_help()
            return True
        
        # Feedback commands
        elif input_lower.startswith('feedback'):
            if 'on' in input_lower:
                self.collect_feedback = True
                print("✅ Feedback collection enabled")
            elif 'off' in input_lower:
                self.collect_feedback = False
                print("❌ Feedback collection disabled")
            elif 'stats' in input_lower:
                self._show_feedback_stats()
            else:
                print("Usage: feedback on/off/stats")
            return True
        
        # Session commands
        elif input_lower.startswith('session'):
            if 'new' in input_lower:
                self._start_new_session()
            elif 'info' in input_lower:
                self._show_session_info()
            else:
                print("Usage: session new/info")
            return True
        
        # Context command
        elif input_lower in ['context', 'history']:
            self._show_conversation_context()
            return True
        
        return False
    
    def _collect_feedback(self, query: str, response_data: Dict[str, Any]):
        """Collect user feedback for the response"""
        
        # Get context-appropriate prompt
        query_type = self.session_manager._classify_query_type(query)
        feedback_prompt = FeedbackPromptGenerator.get_feedback_prompt(query_type)
        
        print(f"\n📝 {feedback_prompt}")
        print("   (You can also add comments after the rating)")
        
        try:
            feedback_input = input("   Rating> ").strip()
            
            if feedback_input:
                # Process feedback
                feedback_data = self.feedback_system.process_feedback_input(feedback_input)
                
                if feedback_data:
                    # Save feedback
                    success = self.feedback_system.collect_feedback(
                        session_id=self.current_session_id,
                        query=query,
                        response=response_data['response'],
                        rating=feedback_data['rating'],
                        feedback_text=feedback_data['feedback_text'],
                        intent_classification=query_type,
                        response_time_ms=response_data.get('response_time_ms', 0)
                    )
                    
                    if success:
                        # Show follow-up prompt
                        follow_up = FeedbackPromptGenerator.get_follow_up_prompt(feedback_data['rating'])
                        print(f"   {follow_up}")
                    else:
                        print("   ❌ Error saving feedback")
                else:
                    print("   Please provide a rating from 1-5")
            
            print()  # Add spacing
            
        except KeyboardInterrupt:
            print("\n   Feedback skipped")
            print()
    
    def _show_help(self):
        """Show help information"""
        print("\n🆘 Enhanced BoilerAI Commands:")
        print("  help, ?          - Show this help")
        print("  exit, quit, bye  - Exit the chat")
        print("  feedback on/off  - Enable/disable feedback collection")
        print("  feedback stats   - Show feedback statistics")
        print("  session new      - Start a new session")
        print("  session info     - Show current session info")
        print("  context, history - Show conversation context")
        print("\n💡 You can ask about:")
        print("  • Course prerequisites and requirements")
        print("  • Track specializations (MI, SE)")
        print("  • Academic planning and scheduling")
        print("  • Professor information")
        print("  • Academic policies and procedures")
        print("  • Career guidance and internships")
        print()
    
    def _show_feedback_stats(self):
        """Show feedback statistics"""
        stats = self.feedback_system.get_feedback_stats()
        
        print("\n📊 Feedback Statistics (Last 30 Days):")
        print(f"  Total feedback: {stats['total_feedback']}")
        print(f"  Average rating: {stats['average_rating']}/5")
        print(f"  Rating range: {stats['min_rating']}-{stats['max_rating']}")
        
        if stats['rating_distribution']:
            print("  Rating distribution:")
            for rating, count in stats['rating_distribution'].items():
                print(f"    {rating} stars: {count} responses")
        
        if stats['intent_performance']:
            print("  Performance by topic:")
            for intent in stats['intent_performance']:
                print(f"    {intent['intent']}: {intent['avg_rating']}/5 ({intent['count']} responses)")
        
        # Show improvement suggestions
        suggestions = self.feedback_system.get_improvement_suggestions()
        if suggestions:
            print("  Improvement suggestions:")
            for suggestion in suggestions[:3]:  # Show top 3
                print(f"    • {suggestion['message']}")
        
        print()
    
    def _start_new_session(self):
        """Start a new chat session"""
        self.current_session_id = self.session_manager.create_session()
        self.response_count = 0
        print(f"🔗 New session started: {self.current_session_id[:8]}...")
        print()
    
    def _show_session_info(self):
        """Show current session information"""
        session = self.session_manager.get_session(self.current_session_id)
        
        if session:
            print(f"\n🔗 Session Info:")
            print(f"  Session ID: {session['session_id'][:8]}...")
            print(f"  Current topic: {session['current_topic'] or 'None'}")
            print(f"  Conversation turns: {len(session['conversation_history'])}")
            print(f"  Last activity: {session['last_activity']}")
            
            if session['extracted_context']:
                print("  Context:")
                for key, value in session['extracted_context'].items():
                    print(f"    {key}: {value}")
        else:
            print("❌ No session information available")
        
        print()
    
    def _show_conversation_context(self):
        """Show conversation context"""
        context = self.session_manager.get_conversation_context(self.current_session_id)
        
        if context:
            print("\n💬 Conversation Context:")
            print(context)
        else:
            print("💬 No conversation context available")
        
        print()
    
    def _show_session_summary(self):
        """Show session summary before exit"""
        session = self.session_manager.get_session(self.current_session_id)
        
        if session and session['conversation_history']:
            print(f"\n📋 Session Summary:")
            print(f"  Conversation turns: {len(session['conversation_history'])}")
            print(f"  Main topic: {session['current_topic'] or 'General inquiry'}")
            print(f"  Duration: Started at session creation")
            
            if self.response_count > 0:
                print(f"  Responses given: {self.response_count}")
                
                # Show feedback summary if available
                # Note: In a real implementation, you'd query feedback for this session
                print(f"  Feedback collected: Every {self.feedback_frequency} responses")

if __name__ == "__main__":
    try:
        # Check for Gemini API key
        if not os.getenv('GEMINI_API_KEY'):
            print("❌ Error: GEMINI_API_KEY environment variable not set")
            print("Please set your Gemini API key and try again.")
            sys.exit(1)
        
        # Start enhanced chat
        chat = EnhancedBoilerAI()
        chat.start_chat()
        
    except Exception as e:
        print(f"❌ Error starting Enhanced BoilerAI: {e}")
        sys.exit(1)