#!/usr/bin/env python3
"""
Universal Purdue CS AI Advisor - 100% AI-Powered
Routes all queries through intelligent AI system with no hardcoded responses.
"""

import os
from simple_boiler_ai import SimpleBoilerAI

class UniversalPurdueAdvisor:
    def __init__(self):
        """Initialize with AI-powered backend using hardcoded Gemini API key"""
        # Use the AI-powered simple boiler AI as the core engine
        # Gemini API key is hardcoded in SimpleBoilerAI class
        self.ai_engine = SimpleBoilerAI()
    
    def ask_question(self, question: str) -> str:
        """Process any question using AI intelligence"""
        return self.ai_engine.process_query(question)

def main():
    """Interactive Purdue CS Advisor with 100% AI responses"""
    try:
        advisor = UniversalPurdueAdvisor()
        
        # Generate AI-powered welcome message
        welcome_prompt = """
Generate a friendly, conversational welcome message for Boiler AI, a Purdue CS academic advisor. The message should:
1. Welcome students warmly
2. Briefly mention the types of help available (courses, graduation planning, CODO, academic guidance)
3. Be encouraging and supportive
4. Mention they can type 'quit' or 'exit' to end
Keep it natural and not too formal.
"""
        welcome_msg = advisor.ai_engine.get_ai_response(welcome_prompt)
        if not welcome_msg:
            welcome_msg = advisor.ai_engine.get_ai_response("Generate a brief welcome message for a Purdue CS academic advisor.")
        print(welcome_msg)
    except ValueError as e:
        print(f"Setup Error: {e}")
        return
    
    while True:
        try:
            user_input = input("🤖 You: ").strip()
            
            # Check for admin commands first
            if user_input.lower().startswith('clado '):
                command_parts = user_input.lower().split()
                if len(command_parts) == 2 and command_parts[1] in ['on', 'off']:
                    from feature_flags import get_feature_manager
                    feature_manager = get_feature_manager()
                    enable = command_parts[1] == 'on'
                    result = feature_manager.toggle_career_networking(enable)
                    print(f"\n🔧 {result}\n")
                    continue
                else:
                    usage_prompt = "Generate a brief usage instruction for the 'clado' command that takes 'on' or 'off' parameters."
                    usage_msg = advisor.ai_engine.get_ai_response(usage_prompt) or "Please use 'clado on' or 'clado off'."
                    print(f"\n🔧 {usage_msg}\n")
                    continue
            elif user_input.lower() == 'clado status':
                from feature_flags import get_feature_manager
                feature_manager = get_feature_manager()
                status = "ENABLED" if feature_manager.is_enabled("career_networking") else "DISABLED"
                print(f"\n🔧 Career networking (Clado API) is currently: {status}\n")
                continue
            elif user_input.lower() in ['clado help', 'clado']:
                help_prompt = """
Generate a comprehensive help guide for the 'clado' career networking feature. Include:
1. Available commands (on, off, status, help)
2. What each command does
3. Example questions users can ask when it's enabled
4. Keep it organized and user-friendly
"""
                help_msg = advisor.ai_engine.get_ai_response(help_prompt)
                print(f"\n{help_msg}\n")
                continue
            elif user_input.lower() == '/health':
                try:
                    from ai_monitoring_system import get_system_health
                    health = get_system_health()
                    print(f"\n🔍 System Health Status:")
                    print(f"   Uptime: {health.uptime_seconds/3600:.1f} hours")
                    print(f"   Success Rate: {((health.successful_requests / health.total_requests) * 100) if health.total_requests > 0 else 0:.1f}%")
                    print(f"   Avg Response Time: {health.average_response_time:.0f}ms")
                    print(f"   Tokens Used (Hour): {health.tokens_used_hour}")
                    print(f"   Primary Provider: {health.primary_provider_status}")
                    print(f"   Error Rate: {health.error_rate:.1%}")
                    print()
                except Exception as e:
                    print(f"\n⚠️ Health check failed: {str(e)}\n")
                continue
            
            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                # Generate AI farewell message
                try:
                    farewell_prompt = """
Generate a brief, encouraging farewell message for a student leaving the Boiler AI academic advisor.
It should:
1. Thank them for using the system
2. Wish them well with their CS studies
3. Be warm and supportive
4. Keep it short and friendly
"""
                    farewell_msg = advisor.ai_engine.get_ai_response(farewell_prompt)
                    if not farewell_msg:
                        farewell_msg = advisor.ai_engine.get_ai_response("Generate a brief goodbye message for a student.")
                    print(f"\n{farewell_msg}")
                except:
                    fallback_msg = advisor.ai_engine.get_ai_response("Generate a simple goodbye message.") or "Goodbye!"
                    print(f"\n{fallback_msg}")
                break
            
            if not user_input:
                continue
            
            print(f"\n🎯 Boiler AI: ", end="", flush=True)
            response = advisor.ask_question(user_input)
            print(response)
            print("\n" + "-"*60 + "\n")
            
        except KeyboardInterrupt:
            interrupt_prompt = "Generate a brief goodbye message when user interrupts the program."
            interrupt_msg = advisor.ai_engine.get_ai_response(interrupt_prompt) or "Goodbye!"
            print(f"\n\n{interrupt_msg}")
            break
        except Exception as e:
            # Generate AI response for system error
            try:
                error_prompt = """
The system encountered a technical issue while processing a user's question.
Generate a brief, friendly message that:
1. Acknowledges there was an issue without technical details
2. Encourages them to try again
3. Maintains a supportive tone
4. Keeps it short and conversational
"""
                error_response = advisor.ai_engine.get_ai_response(error_prompt)
                if not error_response:
                    error_response = advisor.ai_engine.get_ai_response("Generate a brief error message asking user to try again.")
                print(f"\n{error_response}\n")
            except:
                final_fallback = advisor.ai_engine.get_ai_response("Generate a simple error message.") or "Please try again."
                print(f"\n{final_fallback}\n")

if __name__ == "__main__":
    main()