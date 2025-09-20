#!/usr/bin/env python3
"""
Degree Planner CLI Interface
Interactive degree planning system with comprehensive academic guidance
"""

import os
import sys
from enhanced_smart_advisor import EnhancedSmartAdvisor
from degree_planner import StudentProgressTracker
import uuid

class DegreePlannerCLI:
    """Interactive CLI for comprehensive degree planning"""
    
    def __init__(self):
        self.advisor = EnhancedSmartAdvisor()
        self.session_id = None
        self.student_id = None
        self.setup_session()
        
    def setup_session(self):
        """Setup new interactive session"""
        self.student_id = f"student_{uuid.uuid4().hex[:8]}"
        self.session_id = self.advisor.session_manager.create_session(self.student_id)
        
    def display_welcome(self):
        """Display welcome message with degree planning features"""
        print("\n" + "="*70)
        print("🎓 ENHANCED BOILER AI - COMPREHENSIVE DEGREE PLANNER")
        print("="*70)
        print("✨ Complete academic advisor with personalized degree planning")
        print("📊 Session-based conversations with memory and context")
        print("🎯 Track-specific guidance and semester planning")
        print("📋 Real-time graduation progress tracking")
        print("💬 Natural conversation with feedback learning")
        print("="*70)
        print("\n💡 Try asking:")
        print("  • 'Help me plan my degree for Machine Intelligence'")
        print("  • 'What should I take next semester?'")
        print("  • 'Show me my graduation progress'")
        print("  • 'Compare MI and SE tracks'")
        print("  • 'What are the prerequisites for CS 37300?'")
        print("\n📝 Commands: 'help', 'profile', 'quit'")
        print(f"🔗 Session ID: {self.session_id[:8]}...")
        print("-"*70)
        
    def handle_command(self, user_input: str) -> bool:
        """Handle special commands"""
        
        command = user_input.lower().strip()
        
        if command == 'quit':
            print("Good luck with your degree planning! Boiler Up! 🚀")
            return True
        
        elif command == 'help':
            self.show_help()
            return False
        
        elif command == 'profile':
            self.show_profile()
            return False
        
        elif command.startswith('setup profile'):
            self.interactive_profile_setup()
            return False
        
        elif command == 'new session':
            self.setup_session()
            print(f"🔄 New session created: {self.session_id[:8]}...")
            return False
        
        return False
    
    def show_help(self):
        """Display help information"""
        print("\n📖 ENHANCED BOILER AI HELP")
        print("-" * 40)
        print("🎓 DEGREE PLANNING FEATURES:")
        print("  • Comprehensive track requirement analysis")
        print("  • Personalized semester planning with course recommendations")
        print("  • Real-time graduation progress tracking and timeline")
        print("  • Interactive profile setup for personalized guidance")
        print("  • Track comparison and selection assistance")
        print("")
        print("💬 CONVERSATION FEATURES:")
        print("  • Multi-turn conversations with memory")
        print("  • Context-aware responses using conversation history")
        print("  • Session management with intelligent context extraction")
        print("  • User feedback collection for continuous improvement")
        print("")
        print("📝 COMMANDS:")
        print("  • help - Show this help message")
        print("  • profile - View your current academic profile")
        print("  • setup profile - Interactive profile creation")
        print("  • new session - Start a new conversation session")
        print("  • quit - Exit the application")
        print("")
        print("🎯 EXAMPLE QUERIES:")
        print("  • 'I'm a sophomore interested in AI, help me plan my degree'")
        print("  • 'What courses do I need for the Machine Intelligence track?'")
        print("  • 'Create a semester plan for fall with 15 credits'")
        print("  • 'How close am I to graduation?'")
        print("  • 'What are the career prospects for the SE track?'")
        
    def show_profile(self):
        """Show current student profile"""
        if not self.student_id:
            print("❌ No profile found. Use 'setup profile' to create one.")
            return
        
        profile = self.advisor.degree_planner.get_student_progress(self.student_id)
        
        if not profile:
            print("❌ Profile not found. Use 'setup profile' to create one.")
            return
        
        print(f"\n👤 STUDENT PROFILE: {profile.get('name', 'Unknown')}")
        print("-" * 40)
        print(f"🎓 Academic Year: {profile.get('year', 'Not set')}")
        print(f"🎯 Track: {profile.get('track', 'Not selected').replace('_', ' ').title()}")
        print(f"📚 Completed Courses: {len(profile.get('completed_courses', []))}")
        print(f"💳 Total Credits: {profile.get('total_credits', 0)}")
        
        if profile.get('completed_courses'):
            recent_courses = profile['completed_courses'][-5:]
            print(f"📖 Recent Courses: {', '.join(recent_courses)}")
        
        # Show degree analysis if track is selected
        if profile.get('track'):
            analysis = self.advisor.degree_planner.analyze_degree_requirements(self.student_id)
            if 'graduation_readiness' in analysis:
                grad_status = analysis['graduation_readiness']
                print(f"✅ Graduation Progress: {grad_status.get('overall_percentage', 0):.1f}%")
                print(f"⏰ Estimated Remaining: {grad_status.get('estimated_semesters_remaining', 0)} semester(s)")
        
    def interactive_profile_setup(self):
        """Interactive profile setup process"""
        print("\n🔧 INTERACTIVE PROFILE SETUP")
        print("-" * 40)
        
        try:
            # Get basic information
            name = input("👤 What's your name? ").strip()
            if not name:
                name = "Student"
            
            # Academic year
            print("\n🎓 What's your current academic year?")
            print("  1. Freshman")
            print("  2. Sophomore") 
            print("  3. Junior")
            print("  4. Senior")
            
            year_choice = input("Enter number (1-4): ").strip()
            year_map = {'1': 'freshman', '2': 'sophomore', '3': 'junior', '4': 'senior'}
            year = year_map.get(year_choice, 'sophomore')
            
            # Track selection
            print("\n🎯 Which track interests you?")
            print("  1. Machine Intelligence (AI/ML)")
            print("  2. Software Engineering")
            print("  3. Other/Undecided")
            
            track_choice = input("Enter number (1-3): ").strip()
            track_map = {'1': 'machine_intelligence', '2': 'software_engineering', '3': None}
            track = track_map.get(track_choice)
            
            # Completed courses (simplified)
            print("\n📚 Have you completed CS 18000 (Introduction to Computer Science)?")
            has_cs18000 = input("(y/n): ").lower().startswith('y')
            
            completed_courses = []
            if has_cs18000:
                # Basic progression estimation
                if year in ['sophomore', 'junior', 'senior']:
                    completed_courses.extend(['CS 18000', 'CS 18200', 'CS 24000'])
                if year in ['junior', 'senior']:
                    completed_courses.extend(['CS 25000', 'CS 25100'])
                if year == 'senior':
                    completed_courses.extend(['CS 25200', 'CS 38100'])
            
            # Create profile
            success = self.advisor.degree_planner.create_student_profile(
                student_id=self.student_id,
                name=name,
                year=year,
                completed_courses=completed_courses,
                track=track
            )
            
            if success:
                print(f"\n✅ Profile created successfully!")
                print(f"👤 Name: {name}")
                print(f"🎓 Year: {year}")
                print(f"🎯 Track: {track.replace('_', ' ').title() if track else 'Undecided'}")
                print(f"📚 Estimated completed courses: {len(completed_courses)}")
                print("\nYou can now ask detailed questions about your degree planning!")
            else:
                print("❌ Failed to create profile. Please try again.")
                
        except KeyboardInterrupt:
            print("\n❌ Profile setup cancelled.")
        except Exception as e:
            print(f"❌ Error during setup: {e}")
    
    def run(self):
        """Main CLI loop"""
        
        # API key is hardcoded in the system - no need to check environment
        
        self.display_welcome()
        
        try:
            while True:
                try:
                    user_input = input("\nYou> ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle commands
                    if self.handle_command(user_input):
                        break
                    
                    # Process query with enhanced advisor
                    print("Bot> ", end="", flush=True)
                    
                    response_data = self.advisor.handle_academic_query(
                        query=user_input,
                        session_id=self.session_id,
                        student_id=self.student_id
                    )
                    
                    print(response_data['response'])
                    
                    # Show source for transparency
                    source = response_data.get('source', 'unknown')
                    if source != 'smart_ai_engine':
                        print(f"\n🔍 Source: {source.replace('_', ' ').title()}")
                    
                    # Request feedback occasionally
                    if hasattr(self.advisor.feedback_system, 'should_request_feedback'):
                        if self.advisor.feedback_system.should_request_feedback():
                            self.request_feedback(user_input, response_data['response'])
                    
                except KeyboardInterrupt:
                    print("\n\n👋 Goodbye! Good luck with your studies!")
                    break
                except Exception as e:
                    print(f"\n❌ An error occurred: {e}")
                    print("Please try again or type 'help' for assistance.")
        
        except Exception as e:
            print(f"❌ Fatal error: {e}")
    
    def request_feedback(self, query: str, response: str):
        """Request user feedback"""
        try:
            print("\n📝 Quick feedback (optional):")
            print("How helpful was this response? (1=poor, 5=excellent, or press Enter to skip)")
            
            feedback_input = input("Rating: ").strip()
            
            if feedback_input and feedback_input.isdigit():
                rating = int(feedback_input)
                if 1 <= rating <= 5:
                    # Collect feedback
                    feedback_text = ""
                    if rating <= 3:
                        feedback_text = input("How can I improve? (optional): ").strip()
                    
                    self.advisor.feedback_system.collect_feedback(
                        session_id=self.session_id,
                        query=query,
                        response=response,
                        rating=rating,
                        feedback_text=feedback_text,
                        student_id=self.student_id
                    )
                    
                    print(f"✅ Thank you for the feedback!")
        except:
            pass  # Feedback is optional, don't break the flow

if __name__ == "__main__":
    cli = DegreePlannerCLI()
    cli.run()