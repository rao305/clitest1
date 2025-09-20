#!/usr/bin/env python3
"""
CLI Test Interface for BoilerAI Smart System
Simple terminal interface to test the smart AI engine
"""

import sys
import os
import uuid
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from intelligent_conversation_manager import IntelligentConversationManager

def print_banner():
    """Print the BoilerAI banner"""
    print("=" * 80)
    print("🎓 BOILERAI - PURDUE CS ACADEMIC ADVISOR")
    print("=" * 80)
    print("Smart AI-powered academic advising for Purdue Computer Science students")
    print("Type 'help' for available commands, 'quit' to exit")
    print("=" * 80)
    print()

def print_help():
    """Print help information"""
    print("\n📚 AVAILABLE COMMANDS:")
    print("-" * 40)
    print("• help                    - Show this help message")
    print("• quit / exit             - Exit the program")
    print("• clear                   - Clear the screen")
    print("• context                 - Show current conversation context")
    print("• stats                   - Show system statistics")
    print()
    print("🎯 SAMPLE QUERIES TO TEST:")
    print("-" * 40)
    print("• What courses should I take as a freshman?")
    print("• I want to graduate with both machine intelligence and software engineering tracks")
    print("• What are the prerequisites for CS 37300?")
    print("• How hard is CS 25100?")
    print("• Which track should I choose for AI careers?")
    print("• How can I graduate early?")
    print("• I'm a sophomore, what should I take next semester?")
    print("• Can I complete both tracks in 4 years?")
    print("• What's the difference between MI and SE tracks?")
    print("• Give me a dual track graduation plan")
    print()

def print_context(context):
    """Print current conversation context"""
    print("\n📋 CONVERSATION CONTEXT:")
    print("-" * 30)
    if context.extracted_context:
        for key, value in context.extracted_context.items():
            print(f"• {key}: {value}")
    else:
        print("• No context extracted yet")
    print()

def print_stats(manager):
    """Print system statistics"""
    print("\n📊 SYSTEM STATISTICS:")
    print("-" * 25)
    print(f"• Active sessions: {len(manager.conversation_contexts)}")
    print(f"• Tracking mode: {manager.tracker_mode}")
    print(f"• Smart AI engine: ✅ Active")
    print(f"• Gemini available: {'✅' if manager.Gemini_available else '❌'}")
    print(f"• Academic advisor: {'✅' if manager.academic_advisor else '❌'}")
    print(f"• Graduation planner: {'✅' if manager.graduation_planner else '❌'}")
    print()

def main():
    """Main CLI interface"""
    print_banner()
    
    # Initialize the conversation manager
    print("🚀 Initializing BoilerAI Smart System...")
    try:
        manager = IntelligentConversationManager(tracker_mode=True)
        print("✅ System initialized successfully!")
        print()
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        return
    
    # Generate a session ID for this conversation
    session_id = str(uuid.uuid4())
    print(f"📝 Session ID: {session_id[:8]}...")
    print()
    
    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = input("🎓 BoilerAI > ").strip()
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit']:
                print("\n👋 Thanks for using BoilerAI! Good luck with your CS journey!")
                break
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif user_input.lower() == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                print_banner()
                continue
            elif user_input.lower() == 'context':
                if session_id in manager.conversation_contexts:
                    print_context(manager.conversation_contexts[session_id])
                else:
                    print("No conversation context yet.")
                continue
            elif user_input.lower() == 'stats':
                print_stats(manager)
                continue
            elif not user_input:
                continue
            
            # Process the query
            print(f"\n🤔 Processing: {user_input}")
            print("-" * 50)
            
            start_time = datetime.now()
            response = manager.process_query(session_id, user_input)
            end_time = datetime.now()
            
            # Display response
            print(f"\n💡 BoilerAI Response:")
            print("=" * 50)
            print(response)
            print("=" * 50)
            
            # Show processing time
            processing_time = (end_time - start_time).total_seconds()
            print(f"\n⏱️  Processed in {processing_time:.2f} seconds")
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for using BoilerAI! Good luck with your CS journey!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'help' for assistance.")
            print()

if __name__ == "__main__":
    main() 