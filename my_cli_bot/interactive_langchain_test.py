#!/usr/bin/env python3
"""
Interactive LangChain Academic Advisor Tester
Type in queries and see real-time responses from the enhanced system
"""

import os
import sys
import json
import time
from typing import Dict, Any
import asyncio

# Color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_colored(text, color):
    print(f"{color}{text}{Colors.END}")

def print_header():
    print_colored("\n" + "="*70, Colors.CYAN)
    print_colored("🎓 INTERACTIVE BOILER AI LANGCHAIN TESTER", Colors.HEADER + Colors.BOLD)
    print_colored("Enhanced Academic Advisor with Function Calling & Vector Search", Colors.BLUE)
    print_colored("="*70, Colors.CYAN)

def print_help():
    help_text = """
📝 COMMANDS:
  Type any question about Purdue CS courses, graduation planning, etc.
  
🎯 EXAMPLE QUERIES:
  • "What is CS 18000?"
  • "What are the prerequisites for CS 25000?"
  • "Create a degree plan for Computer Science starting Fall 2024"
  • "Can I graduate in 3 years if I'm a sophomore?"
  • "What's the difference between MI and SE tracks?"
  
⚙️  SPECIAL COMMANDS:
  • 'help' - Show this help
  • 'tools' - List available function calling tools
  • 'stats' - Show system statistics
  • 'test' - Run sample test queries
  • 'quit' or 'exit' - Exit the program
  
💡 TIP: The system will show you the intent classification, entities extracted,
       and which method (function call vs vector search) was used!
"""
    print_colored(help_text, Colors.YELLOW)

class InteractiveTester:
    def __init__(self):
        self.pipeline = None
        self.session_id = f"interactive_session_{int(time.time())}"
        self.query_count = 0
        
    def setup_pipeline(self):
        """Initialize the LangChain pipeline"""
        print_colored("🔧 Setting up Enhanced LangChain Pipeline...", Colors.BLUE)
        
        # Check for API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print_colored("⚠️  No Gemini API key found. Using mock mode for testing...", Colors.YELLOW)
            api_key = "mock-key-for-testing"
        else:
            print_colored("✅ Gemini API key found", Colors.GREEN)
        
        try:
            # Import and initialize pipeline
            from langchain_advisor_pipeline import EnhancedLangChainPipeline
            self.pipeline = EnhancedLangChainPipeline(api_key)
            print_colored("✅ Pipeline initialized successfully!", Colors.GREEN)
            
            # Show available tools
            tools = self.pipeline.get_tool_definitions()
            print_colored(f"🛠️  Loaded {len(tools)} function calling tools", Colors.GREEN)
            
            return True
            
        except ImportError as e:
            print_colored(f"❌ Import error: {e}", Colors.RED)
            print_colored("💡 Make sure to install dependencies: pip install -r requirements_langchain.txt", Colors.YELLOW)
            return False
        except Exception as e:
            print_colored(f"❌ Setup error: {e}", Colors.RED)
            return False
    
    def show_tools(self):
        """Display available function calling tools"""
        if not self.pipeline:
            print_colored("❌ Pipeline not initialized", Colors.RED)
            return
        
        try:
            tools = self.pipeline.get_tool_definitions()
            print_colored("\n🛠️  AVAILABLE FUNCTION CALLING TOOLS:", Colors.CYAN + Colors.BOLD)
            
            for i, tool in enumerate(tools, 1):
                print_colored(f"\n{i}. {tool['name']}", Colors.GREEN + Colors.BOLD)
                print_colored(f"   📝 {tool['description']}", Colors.BLUE)
                
                if 'parameters' in tool:
                    params = tool['parameters']
                    if isinstance(params, dict) and 'properties' in params:
                        print_colored("   📋 Parameters:", Colors.YELLOW)
                        for param, details in params['properties'].items():
                            param_type = details.get('type', 'unknown')
                            print_colored(f"      • {param}: {param_type}", Colors.CYAN)
        
        except Exception as e:
            print_colored(f"❌ Error showing tools: {e}", Colors.RED)
    
    def show_stats(self):
        """Show system statistics"""
        print_colored("\n📊 SYSTEM STATISTICS:", Colors.CYAN + Colors.BOLD)
        print_colored(f"   Session ID: {self.session_id}", Colors.BLUE)
        print_colored(f"   Queries processed: {self.query_count}", Colors.BLUE)
        
        if self.pipeline:
            print_colored("   Pipeline status: ✅ Active", Colors.GREEN)
            
            # Check components
            if hasattr(self.pipeline, 'conversation_manager') and self.pipeline.conversation_manager:
                print_colored("   Conversation manager: ✅ Available", Colors.GREEN)
            
            if hasattr(self.pipeline, 'vector_store') and self.pipeline.vector_store:
                print_colored("   Vector store: ✅ Available", Colors.GREEN)
            
            if hasattr(self.pipeline, 'tools') and self.pipeline.tools:
                print_colored(f"   Tools loaded: ✅ {len(self.pipeline.tools)}", Colors.GREEN)
        else:
            print_colored("   Pipeline status: ❌ Not initialized", Colors.RED)
    
    def run_test_queries(self):
        """Run a set of test queries"""
        test_queries = [
            "What is CS 18000?",
            "What are the prerequisites for CS 25000?",
            "Create a degree plan for Computer Science starting Fall 2024",
            "Can I graduate in 3 years?",
            "What's the Machine Intelligence track about?"
        ]
        
        print_colored("\n🧪 RUNNING TEST QUERIES:", Colors.CYAN + Colors.BOLD)
        
        for i, query in enumerate(test_queries, 1):
            print_colored(f"\n📝 Test Query {i}: {query}", Colors.BLUE + Colors.BOLD)
            self.process_query(query, is_test=True)
            time.sleep(1)  # Brief pause between tests
    
    def process_query(self, query: str, is_test: bool = False):
        """Process a user query and display results"""
        if not self.pipeline:
            print_colored("❌ Pipeline not initialized. Please restart the program.", Colors.RED)
            return
        
        self.query_count += 1
        start_time = time.time()
        
        print_colored(f"\n🔍 Processing query...", Colors.BLUE)
        
        try:
            # Process the query
            result = self.pipeline.process_query(query, self.session_id)
            processing_time = (time.time() - start_time) * 1000
            
            # Display results
            print_colored("\n📊 QUERY ANALYSIS:", Colors.CYAN + Colors.BOLD)
            print_colored(f"   Intent: {result.get('intent', 'unknown')}", Colors.GREEN)
            print_colored(f"   Method: {result.get('method', 'unknown')}", Colors.GREEN)
            print_colored(f"   Processing time: {processing_time:.1f}ms", Colors.GREEN)
            
            # Show extracted entities
            entities = result.get('entities', {})
            if entities and not entities.get('requires_clarification'):
                print_colored("\n🎯 EXTRACTED ENTITIES:", Colors.YELLOW + Colors.BOLD)
                for key, value in entities.items():
                    print_colored(f"   {key}: {value}", Colors.YELLOW)
            
            # Show the response
            response = result.get('response', 'No response generated')
            print_colored("\n💬 RESPONSE:", Colors.GREEN + Colors.BOLD)
            print_colored(f"{response}", Colors.CYAN)
            
            # Show context if available
            context = result.get('context')
            if context and not is_test:
                print_colored("\n📚 CONTEXT USED:", Colors.YELLOW + Colors.BOLD)
                print_colored(f"{context[:200]}{'...' if len(context) > 200 else ''}", Colors.YELLOW)
        
        except Exception as e:
            print_colored(f"\n❌ Error processing query: {e}", Colors.RED)
            print_colored("💡 This might be due to missing Gemini API key or other dependencies", Colors.YELLOW)
    
    def run_interactive_loop(self):
        """Main interactive loop"""
        print_help()
        
        while True:
            try:
                # Get user input
                print_colored("\n" + "-"*50, Colors.BLUE)
                query = input(f"{Colors.BOLD}💬 Enter your query (or 'help' for commands): {Colors.END}").strip()
                
                if not query:
                    continue
                
                # Handle special commands
                query_lower = query.lower()
                
                if query_lower in ['quit', 'exit', 'q']:
                    print_colored("\n👋 Thanks for testing Boiler AI LangChain! Goodbye!", Colors.GREEN)
                    break
                
                elif query_lower == 'help':
                    print_help()
                    continue
                
                elif query_lower == 'tools':
                    self.show_tools()
                    continue
                
                elif query_lower == 'stats':
                    self.show_stats()
                    continue
                
                elif query_lower == 'test':
                    self.run_test_queries()
                    continue
                
                # Process regular query
                self.process_query(query)
            
            except KeyboardInterrupt:
                print_colored("\n\n👋 Interrupted by user. Goodbye!", Colors.YELLOW)
                break
            except Exception as e:
                print_colored(f"\n❌ Unexpected error: {e}", Colors.RED)

def main():
    """Main function"""
    print_header()
    
    tester = InteractiveTester()
    
    # Setup pipeline
    if not tester.setup_pipeline():
        print_colored("\n❌ Failed to initialize pipeline. Exiting...", Colors.RED)
        return
    
    # Run interactive loop
    try:
        tester.run_interactive_loop()
    except Exception as e:
        print_colored(f"\n❌ Fatal error: {e}", Colors.RED)

if __name__ == "__main__":
    main()