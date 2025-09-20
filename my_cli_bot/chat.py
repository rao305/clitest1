#!/usr/bin/env python3
"""
Enhanced Boiler AI CLI Chat with Academic Advising Intelligence
Integrated with real Purdue CS curriculum data and prerequisite validation
"""

import json
import os
import sys
from llm_engine import ChatEngine
from enhanced_llm_engine import EnhancedLLMEngine
from thinking_advisor import ThinkingAIAdvisor
from knowledge_graph import PurdueCSKnowledgeGraph
from mi_track_scraper import PurdueMITrackScraper
from course_validator import MITrackValidator
from se_track_scraper import PurdueSETrackScraper
from se_course_validator import SETrackValidator
from friendly_response_generator import FriendlyStudentAdvisor
import faiss
import numpy as np

class EnhancedBoilerAI:
    def __init__(self):
        self.engine = ChatEngine()
        self.enhanced_engine = EnhancedLLMEngine()
        self.thinking_advisor = None
        self.knowledge_graph = None
        self.vector_store = None
        self.chunks = []
        self.history = []
        self.conversation_history = []  # Track full conversation for context
        self.mi_scraper = PurdueMITrackScraper()
        self.mi_validator = MITrackValidator()
        self.se_scraper = PurdueSETrackScraper()
        self.se_validator = SETrackValidator()
        self.friendly_advisor = None
        self.smart_ai_engine = None
        
        # Load enhanced system components
        self.load_knowledge_graph()
        self.load_vector_store()
        
        # Initialize friendly advisor after knowledge graph is loaded
        if self.knowledge_graph:
            self.friendly_advisor = FriendlyStudentAdvisor(self.knowledge_graph)
        
        # Initialize thinking advisor
        self.thinking_advisor = ThinkingAIAdvisor(self.knowledge_graph, self.enhanced_engine)
        
        # Initialize smart AI engine
        from smart_ai_engine import SmartAIEngine
        self.smart_ai_engine = SmartAIEngine(self.knowledge_graph)
        
        # Initialize enhanced smart advisor for comprehensive academic queries
        from enhanced_smart_advisor import EnhancedSmartAdvisor
        self.enhanced_smart_advisor = EnhancedSmartAdvisor()
        
        # Initialize real-time debug tracker
        from real_time_debug_tracker import RealTimeDebugTracker, TrackedQueryProcessor
        from side_panel_tracker import SidePanelTracker
        self.debug_tracker = RealTimeDebugTracker()
        self.tracked_processor = TrackedQueryProcessor(self.knowledge_graph, self.debug_tracker)
        self.side_tracker = SidePanelTracker()
        self.debug_mode = False  # Start with debug mode off
        self.side_panel_mode = True  # Start with side panel tracking on
        
        # Display available providers
        self.display_provider_info()
        
    def load_knowledge_graph(self):
        """Load the knowledge graph if available"""
        try:
            kg_path = "data/cs_knowledge_graph.json"
            if os.path.exists(kg_path):
                self.knowledge_graph = PurdueCSKnowledgeGraph()
                self.knowledge_graph.load_graph(kg_path)
                print("✓ Knowledge graph loaded")
            else:
                print("⚠ Knowledge graph not found, using basic mode")
        except Exception as e:
            print(f"⚠ Knowledge graph load error: {e}")
    
    def load_vector_store(self):
        """Load the vector store if available"""
        try:
            vector_path = "data/vector_store.faiss"
            chunks_path = "data/chunks.json"
            
            if os.path.exists(vector_path) and os.path.exists(chunks_path):
                self.vector_store = faiss.read_index(vector_path)
                
                with open(chunks_path, 'r') as f:
                    self.chunks = json.load(f)
                
                print(f"✓ Loaded vector store with {len(self.chunks)} vectors")
            else:
                print("⚠ Vector store not found, using basic mode")
        except Exception as e:
            print(f"⚠ Vector store load error: {e}")
    
    def search_knowledge_base(self, query, k=3):
        """Search the knowledge base for relevant information"""
        if not self.vector_store or not self.chunks:
            return []
        
        try:
            # Get embeddings for query
            from google.generativeai import google.generativeai as genai
            client = Gemini(api_key=os.environ.get("GEMINI_API_KEY"))
            
            response = client.embeddings.create(
                input=query,
                model="text-embedding-3-small"
            )
            
            query_embedding = np.array([response.data[0].embedding], dtype=np.float32)
            
            # Search vector store
            scores, indices = self.vector_store.search(query_embedding, k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.chunks):
                    chunk = self.chunks[idx]
                    results.append({
                        'content': chunk.get('content', ''),
                        'source': chunk.get('source', ''),
                        'score': float(scores[0][i])
                    })
            
            return results
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_enhanced_response(self, user_input):
        """Get enhanced response with NLP analysis and dynamic knowledge retrieval"""
        # Use NLP to analyze query intent
        intent_data = self.analyze_query_intent(user_input)
        
        # Get dynamic track information based on intent
        dynamic_context = self.get_dynamic_track_info(intent_data)
        
        # Search knowledge base for relevant context
        knowledge_results = self.search_knowledge_base(user_input)
        
        # Build enhanced context
        context = ""
        if dynamic_context:
            context += f"\n\nDynamic Track Information:\n{dynamic_context}\n"
        
        if knowledge_results:
            context += "\n\nRelevant information from Purdue CS curriculum:\n"
            for result in knowledge_results:
                context += f"• {result['content']}\n"
        
        # Add intent analysis to context
        context += f"\n\nQuery Analysis: {json.dumps(intent_data, indent=2)}\n"
        
        # Add user message to history with context
        self.history.append({"role": "user", "content": user_input + context})
        
        # Get response with enhanced context
        response = self.engine.generate(self.history)
        
        # Add verification badge if knowledge was used
        if knowledge_results or dynamic_context:
            response += "\n\n✓ Verified against real-time data"
        
        # Add bot response to history
        bot_content = response.replace("Bot> ", "", 1) if response.startswith("Bot> ") else response
        self.history.append({"role": "assistant", "content": bot_content})
        
        return response
    
    def analyze_query_intent(self, query):
        """Use NLP to analyze query intent and extract relevant information"""
        try:
            # Use Gemini to analyze query intent
            analysis_prompt = f"""
            Analyze this student query about Purdue CS tracks and extract:
            1. Query intent (track_info, course_validation, comparison, requirements, etc.)
            2. Track mentioned (MI, SE, or both)
            3. Specific courses mentioned
            4. Action requested

            Query: "{query}"

            Respond in JSON format:
            {{
                "intent": "intent_type",
                "tracks": ["track_codes"],
                "courses": ["course_codes"],
                "action": "description"
            }}
            """
            
            from google.generativeai import google.generativeai as genai
            client = Gemini(api_key=os.environ.get("GEMINI_API_KEY"))
            
            response = client.generate_content(
                ,
                prompt,
                ,
                ,
                response_format={"type": "json_object"}
            )
            
            import json
            return json.loads(response.text)
            
        except Exception as e:
            print(f"Intent analysis error: {e}")
            # Fallback to simple pattern matching for now
            return self.simple_intent_analysis(query)

    def get_dynamic_track_info(self, intent_data):
        """Get track information dynamically based on intent analysis"""
        tracks = intent_data.get("tracks", [])
        intent = intent_data.get("intent", "general")
        
        context = ""
        
        # Get dynamic track information from scrapers
        if "MI" in tracks:
            mi_data = self.mi_scraper.scrape_courses()
            if mi_data:
                context += f"\nMI Track Data: {json.dumps(mi_data, indent=2)}\n"
        
        if "SE" in tracks:
            se_data = self.se_scraper.scrape_courses()
            if se_data:
                context += f"\nSE Track Data: {json.dumps(se_data, indent=2)}\n"
        
        # Handle validation requests
        if intent == "course_validation":
            courses = intent_data.get("courses", [])
            if courses:
                validation_results = self.validate_courses_dynamic(courses, tracks)
                context += f"\nValidation Results: {validation_results}\n"
        
        return context

    def validate_courses_dynamic(self, courses, tracks):
        """Validate courses dynamically against track requirements"""
        results = {}
        
        for track in tracks:
            if track == "MI":
                result = self.mi_validator.validate_course_plan(courses)
                results[track] = result
            elif track == "SE":
                result = self.se_validator.validate_course_plan(courses)
                results[track] = result
        
        return results
    
    def simple_intent_analysis(self, query):
        """Fallback simple pattern matching for intent analysis"""
        query_lower = query.lower()
        
        # Extract course codes
        import re
        courses = re.findall(r'[A-Z]{2,4}\s*\d{5}', query.upper())
        
        # Determine tracks mentioned
        tracks = []
        if any(keyword in query_lower for keyword in ['machine intelligence', 'mi track', 'ai track', 'cs 37300']):
            tracks.append("MI")
        if any(keyword in query_lower for keyword in ['software engineering', 'se track', 'cs 30700', 'cs 40800']):
            tracks.append("SE")
        
        # Determine intent
        intent = "general"
        if any(keyword in query_lower for keyword in ['validate', 'check', 'valid']):
            intent = "course_validation"
        elif any(keyword in query_lower for keyword in ['requirement', 'need', 'must take']):
            intent = "track_info"
        elif any(keyword in query_lower for keyword in ['difference', 'compare', 'versus']):
            intent = "comparison"
        
        return {
            "intent": intent,
            "tracks": tracks,
            "courses": courses,
            "action": f"User asking about {intent} for tracks {tracks}"
        }
    
    def display_provider_info(self):
        """Display available LLM providers"""
        available = self.enhanced_engine.get_available_providers()
        active = self.enhanced_engine.get_active_provider()
        
        if available:
            print(f"🤖 AI Providers: {', '.join(available)}")
            if active:
                print(f"🎯 Active Provider: {active}")
        else:
            print("⚠️ No AI providers available - check your API keys")
    
    def show_help(self):
        """Show help information"""
        print("\n🎓 Enhanced Boiler AI - Academic Advisor")
        print("=" * 50)
        print("I can help you with:")
        print("• CS degree requirements and prerequisites")
        print("• Course planning and scheduling")
        print("• Degree progression guides")
        print("• CS track recommendations")
        print("• Prerequisite validation and course sequencing")
        print("\nFeatures:")
        if self.knowledge_graph:
            print("✓ Knowledge graph integration for accurate course information")
        if self.vector_store:
            print("✓ Vector search with real Purdue CS curriculum data")
        print("✓ Fact verification against authoritative sources")
        print("✓ Enhanced academic guidance with prerequisite intelligence")
        print("✓ Machine Intelligence track validation and course planning")
        print("✓ Multiple AI provider support (Gemini, Anthropic, Gemini)")
        print("✓ AI thinking process with step-by-step reasoning")
        
        # Show provider status
        print("\nAI Provider Status:")
        status = self.enhanced_engine.get_provider_status()
        for name, info in status.items():
            status_icon = "✓" if info["available"] else "✗"
            active_icon = "🎯" if info["active"] else " "
            print(f"{active_icon} {status_icon} {name}: {info['model']}")
        
        print("\nCommands:")
        print("• 'provider <name>' - Switch AI provider (Gemini, Anthropic, Gemini)")
        print("• 'providers' - Show provider status")
        print("• 'thinking on/off' - Enable/disable thinking process display")
        print("• 'debug on/off' - Enable/disable real-time query processing debug")
        print("• 'help' - Show this information")
        print("• 'exit' - Quit the application")
        print("-" * 50)
    
    def show_provider_status(self):
        """Show detailed provider status"""
        print("\n🤖 AI Provider Status:")
        print("=" * 50)
        
        status = self.enhanced_engine.get_provider_status()
        recommendations = self.enhanced_engine.get_provider_recommendations()
        
        for name, info in status.items():
            status_icon = "✅" if info["available"] else "❌"
            active_marker = " (ACTIVE)" if info["active"] else ""
            print(f"{status_icon} {name}{active_marker}")
            print(f"   Model: {info['model']}")
            print(f"   Status: {'Available' if info['available'] else 'Not Available'}")
            print()
        
        if recommendations["missing_keys"]:
            print("🔑 Missing API Keys:")
            for provider in recommendations["missing_keys"]:
                print(f"   • {provider}_API_KEY")
            print()
        
        if recommendations["primary"]:
            print(f"💡 Recommended Primary: {recommendations['primary']}")
        
        if recommendations["fallback"]:
            print(f"🔄 Available Fallbacks: {', '.join(recommendations['fallback'])}")
        
        print("-" * 50)
    
    def set_provider(self, provider_name: str) -> bool:
        """Set active provider"""
        return self.enhanced_engine.set_provider(provider_name)
    
    def use_thinking_mode(self) -> bool:
        """Check if thinking mode should be used"""
        return hasattr(self, 'thinking_mode') and self.thinking_mode
    
    def set_thinking_mode(self, enabled: bool):
        """Enable or disable thinking mode"""
        self.thinking_mode = enabled

def main():
    """Main CLI chat loop with enhanced features"""
    try:
        print("🤖 Enhanced Boiler AI CLI Chat")
        print("=" * 50)
        
        # Initialize enhanced system
        boiler_ai = EnhancedBoilerAI()
        
        # Set default thinking mode
        boiler_ai.set_thinking_mode(False)  # Start with thinking mode off
        
        print("Enhanced features loaded:")
        if boiler_ai.knowledge_graph:
            print("✓ Knowledge graph integration for accurate course information")
        if boiler_ai.vector_store:
            print("✓ Vector search with real Purdue CS curriculum data")

        
        while True:
            try:
                user_input = input("You> ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("Bot> Good luck with your studies! Boiler Up!")
                    break
                
                if user_input.lower() == 'help':
                    boiler_ai.show_help()
                    continue
                
                if user_input.lower() == 'providers':
                    boiler_ai.show_provider_status()
                    continue
                
                if user_input.lower().startswith('provider '):
                    provider_name = user_input[9:].strip().title()
                    if boiler_ai.set_provider(provider_name):
                        print(f"Bot> Switched to {provider_name} provider!")
                    else:
                        print(f"Bot> Provider {provider_name} not available. Available: {', '.join(boiler_ai.enhanced_engine.get_available_providers())}")
                    continue
                
                if user_input.lower().startswith('thinking '):
                    mode = user_input[9:].strip().lower()
                    if mode == 'on':
                        boiler_ai.set_thinking_mode(True)
                        print("Bot> Thinking mode enabled - you'll see my reasoning process!")
                    elif mode == 'off':
                        boiler_ai.set_thinking_mode(False)
                        print("Bot> Thinking mode disabled - responses will be faster.")
                    else:
                        print("Bot> Use 'thinking on' or 'thinking off'")
                    continue
                
                if user_input.lower().startswith('debug '):
                    mode = user_input[6:].strip().lower()
                    if mode == 'on':
                        boiler_ai.debug_mode = True
                        print("Bot> Debug mode enabled - you'll see real-time query processing!")
                    elif mode == 'off':
                        boiler_ai.debug_mode = False
                        print("Bot> Debug mode disabled - cleaner output.")
                    else:
                        print("Bot> Use 'debug on' or 'debug off'")
                    continue
                
                if user_input.lower().startswith('tracker '):
                    mode = user_input[8:].strip().lower()
                    if mode == 'on':
                        boiler_ai.side_panel_mode = True
                        try:
                            if not boiler_ai.side_tracker.is_running:
                                boiler_ai.side_tracker.start_side_panel_display()
                            print("Bot> Side panel tracker enabled - real-time logs will show!")
                        except Exception as e:
                            print(f"Bot> Error starting tracker: {e}")
                    elif mode == 'off':
                        boiler_ai.side_panel_mode = False
                        boiler_ai.side_tracker.stop()
                        print("Bot> Side panel tracker disabled.")
                    else:
                        print("Bot> Use 'tracker on' or 'tracker off'")
                    continue
                
                if user_input.lower() == 'smart ai':
                    if boiler_ai.smart_ai_engine:
                        print("🤖 Smart AI Engine Test - Using actual Gemini intelligence")
                        test_query = "How is the CS program at Purdue?"
                        response = boiler_ai.smart_ai_engine.generate_intelligent_response(test_query)
                        print(f"Bot> {response['response']}")
                        print(f"🎯 Intent: {response['intent']}")
                        print(f"📊 Confidence: {response['confidence']}")
                        print(f"🔧 Source: {response['source']}")
                        if 'provider' in response:
                            print(f"🧠 Provider: {response['provider']}")
                    else:
                        print("❌ Smart AI Engine not available")
                    continue
                
                if not user_input:
                    continue
                
                # Determine response mode
                use_thinking = boiler_ai.use_thinking_mode()
                
                if use_thinking and boiler_ai.thinking_advisor:
                    # Use thinking mode with visual feedback
                    intent_analysis = boiler_ai.analyze_query_intent(user_input)
                    track_context = intent_analysis.get("tracks", [])
                    track_context = track_context[0] if track_context else None
                    
                    # Generate response with thinking process
                    advisor_response = boiler_ai.thinking_advisor.process_query_with_thinking(user_input, track_context)
                    
                    # Add provider info
                    provider_info = ""
                    if len(boiler_ai.enhanced_engine.get_available_providers()) > 1:
                        active_provider = boiler_ai.enhanced_engine.get_active_provider()
                        provider_info = f" [{active_provider}]" if active_provider else ""
                    
                    print(f"Bot{provider_info}> {advisor_response['response']}")
                    
                elif boiler_ai.enhanced_smart_advisor:
                    # Use debug tracking if enabled
                    if boiler_ai.debug_mode:
                        print("\n🔍 DEBUG MODE: Real-time query processing")
                        print("=" * 60)
                        
                        # Process with full tracking
                        tracked_result = boiler_ai.tracked_processor.process_query_with_tracking(user_input)
                        
                        print("=" * 60)
                        print(f"Bot> {tracked_result['response']}")
                        if tracked_result.get('route'):
                            print(f"📊 Route: {tracked_result['route']}")
                        if tracked_result.get('intent'):
                            print(f"🎯 Intent: {tracked_result['intent']}")
                    else:
                        # Side panel tracking mode
                        if boiler_ai.side_panel_mode:
                            import time
                            
                            # Start side panel tracking
                            if not boiler_ai.side_tracker.is_running:
                                boiler_ai.side_tracker.start_side_panel_display()
                            
                            query_id = int(time.time() * 1000) % 100  # Simple query ID
                            boiler_ai.side_tracker.log_query_start(user_input, query_id)
                            
                            # Check if this is a course failure query
                            query_lower = user_input.lower()
                            is_course_failure = any(pattern in query_lower for pattern in [
                                'failed cs 180', 'failed cs 18000', 'failed 180', 'failing cs 180',
                                'will i graduate', 'can i graduate', 'more than 4 years',
                                'delayed graduation', 'retake cs 180'
                            ])
                            
                            if is_course_failure:
                                boiler_ai.side_tracker.log_intent_classification(query_id, "course_failure", 0.9)
                                boiler_ai.side_tracker.log_context_extraction(query_id, {"course_codes": ["CS 18000"], "student_year": "freshman"})
                                boiler_ai.side_tracker.log_routing_decision(query_id, "enhanced_smart_advisor")
                                boiler_ai.side_tracker.log_knowledge_graph_query(query_id, "prerequisite_analysis", 4)
                                
                                start_time = time.time()
                                response_data = boiler_ai.enhanced_smart_advisor.handle_academic_query(user_input)
                                duration = time.time() - start_time
                                
                                boiler_ai.side_tracker.log_response_generation(query_id, "specific_failure_analysis", len(response_data['response']))
                                boiler_ai.side_tracker.log_query_complete(query_id, duration, True)
                                
                                print(f"Bot> {response_data['response']}")
                                print(f"📊 Source: {response_data['source']}")
                            
                            elif boiler_ai.friendly_advisor:
                                boiler_ai.side_tracker.log_intent_classification(query_id, "general_query", 0.7)
                                
                                # Add conversation history for context
                                boiler_ai.conversation_history.append({"role": "user", "content": user_input})
                                
                                intent_analysis = boiler_ai.analyze_query_intent(user_input)
                                track_context = intent_analysis.get("tracks", [])
                                track_context = track_context[0] if track_context else None
                                
                                context = {"tracks": track_context, "conversation_history": boiler_ai.conversation_history[-5:]} if track_context else {"conversation_history": boiler_ai.conversation_history[-5:]}
                                boiler_ai.side_tracker.log_context_extraction(query_id, context)
                                boiler_ai.side_tracker.log_routing_decision(query_id, "friendly_advisor")
                                
                                start_time = time.time()
                                advisor_response = boiler_ai.friendly_advisor.generate_response_with_history(user_input, track_context, boiler_ai.conversation_history[-5:])
                                duration = time.time() - start_time
                                
                                boiler_ai.side_tracker.log_response_generation(query_id, "friendly_response", len(advisor_response['response']))
                                boiler_ai.side_tracker.log_query_complete(query_id, duration, True)
                                
                                # Add bot response to conversation history
                                boiler_ai.conversation_history.append({"role": "assistant", "content": advisor_response['response']})
                                
                                provider_info = ""
                                if len(boiler_ai.enhanced_engine.get_available_providers()) > 1:
                                    active_provider = boiler_ai.enhanced_engine.get_active_provider()
                                    provider_info = f" [{active_provider}]" if active_provider else ""
                                
                                print(f"Bot{provider_info}> {advisor_response['response']}")
                        
                        else:
                            # Regular processing without tracking
                            query_lower = user_input.lower()
                            is_course_failure = any(pattern in query_lower for pattern in [
                                'failed cs 180', 'failed cs 18000', 'failed 180', 'failing cs 180',
                                'will i graduate', 'can i graduate', 'more than 4 years',
                                'delayed graduation', 'retake cs 180'
                            ])
                            
                            if is_course_failure:
                                response_data = boiler_ai.enhanced_smart_advisor.handle_academic_query(user_input)
                                print(f"Bot> {response_data['response']}")
                                print(f"📊 Source: {response_data['source']}")
                            
                            elif boiler_ai.friendly_advisor:
                                # Add conversation history for context
                                boiler_ai.conversation_history.append({"role": "user", "content": user_input})
                                
                                intent_analysis = boiler_ai.analyze_query_intent(user_input)
                                track_context = intent_analysis.get("tracks", [])
                                track_context = track_context[0] if track_context else None
                                
                                advisor_response = boiler_ai.friendly_advisor.generate_response_with_history(user_input, track_context, boiler_ai.conversation_history[-5:])
                                
                                # Add bot response to conversation history
                                boiler_ai.conversation_history.append({"role": "assistant", "content": advisor_response['response']})
                                
                                provider_info = ""
                                if len(boiler_ai.enhanced_engine.get_available_providers()) > 1:
                                    active_provider = boiler_ai.enhanced_engine.get_active_provider()
                                    provider_info = f" [{active_provider}]" if active_provider else ""
                                
                                print(f"Bot{provider_info}> {advisor_response['response']}")
                else:
                    # Fallback to enhanced response with multi-provider
                    context = boiler_ai.generate_contextual_response(user_input, 
                                                                   boiler_ai.analyze_query_intent(user_input))
                    result = boiler_ai.enhanced_engine.generate_response(user_input, context)
                    
                    provider_info = ""
                    if result["provider"]:
                        provider_info = f" [{result['provider']}]"
                    
                    print(f"Bot{provider_info}> {result['response']}")
                print()  # Empty line for readability
                
            except KeyboardInterrupt:
                print("\nBot> Good luck with your studies! Boiler Up!")
                break
            except EOFError:
                print("\nBot> Good luck with your studies! Boiler Up!")
                break
            except Exception as e:
                print(f"Bot> I encountered an error: {str(e)}")
                print("Bot> Please try again.")
                
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Please set your GEMINI_API_KEY environment variable.")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"File Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Initialization Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
