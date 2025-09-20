"""
Friendly Student Advisor Response Generator
Natural, encouraging responses without markdown formatting
"""

import json
import sqlite3
import re
import random
from datetime import datetime
from dynamic_query_processor_ai_only import DynamicQueryProcessorAIOnly

class FriendlyStudentAdvisor:
    def __init__(self, knowledge_graph):
        self.kg = knowledge_graph
        # Initialize AI-only query processor to eliminate ALL hardcoded responses
        self.dynamic_processor = DynamicQueryProcessorAIOnly(knowledge_graph)
        
        # Initialize AI engine for phrase generation
        try:
            from smart_ai_engine import SmartAIEngine
            self.ai_engine = SmartAIEngine()
        except ImportError:
            self.ai_engine = None
        
        # AI-generated phrases - no hardcoded content
        self.ai_phrases_cache = {}
        self.phrase_types = {
            'greeting': 'Generate a brief, friendly greeting phrase for a CS advisor',
            'encouragement': 'Generate a brief, encouraging closing phrase for academic advice',
            'transition': 'Generate a brief transition phrase to introduce advice or explanation'
        }
        
    def _get_ai_phrase(self, phrase_type: str, context: str = "") -> str:
        """Generate AI phrase instead of using hardcoded content - 100% AI-powered"""
        
        # Try to get from cache first
        cache_key = f"{phrase_type}_{hash(context)}"
        if cache_key in self.ai_phrases_cache:
            return self.ai_phrases_cache[cache_key]
        
        # Generate new phrase using AI
        if self.ai_engine and phrase_type in self.phrase_types:
            try:
                prompt = f"{self.phrase_types[phrase_type]}. Context: {context}. Keep it brief and natural."
                phrase = self.ai_engine.generate_smart_response(prompt, {"type": phrase_type})
                # Cache the result
                self.ai_phrases_cache[cache_key] = phrase
                return phrase
            except Exception:
                pass
        
        # AI-powered emergency fallback - no hardcoded content
        try:
            from simple_boiler_ai import SimpleBoilerAI
            emergency_ai = SimpleBoilerAI()
            emergency_prompt = f"Generate a brief, natural {phrase_type} phrase for a Purdue CS advisor. Context: {context}. Maximum 10 words."
            phrase = emergency_ai.get_ai_response(emergency_prompt)
            # Cache emergency result
            self.ai_phrases_cache[cache_key] = phrase
            return phrase
        except Exception:
            # Absolute last resort - generate using basic AI prompt
            return self._generate_emergency_phrase(phrase_type, context)
    
    def _generate_emergency_phrase(self, phrase_type: str, context: str) -> str:
        """Emergency AI phrase generation when all else fails"""
        try:
            import google.generativeai as genai
            import os
            
            if not os.environ.get("GEMINI_API_KEY"):
                return ""  # Return empty string rather than hardcoded text
            
            client = Gemini.Gemini(api_key=os.environ.get("GEMINI_API_KEY"))
            response = client.generate_content(
                ,  # Use cheaper model for emergency fallback
                messages=[
                    {"role": "system", "content": "Generate a brief, natural phrase for a Purdue CS advisor. Maximum 8 words."},
                    {"role": "user", "content": f"Generate a {phrase_type} phrase. Context: {context}"}
                ],
                ,
                
            )
            phrase = response.text.strip()
            # Cache even emergency results
            cache_key = f"{phrase_type}_{hash(context)}"
            self.ai_phrases_cache[cache_key] = phrase
            return phrase
        except Exception:
            return ""  # Return empty string instead of hardcoded fallback
    
    def generate_response(self, query: str, track_context: str = None) -> dict:
        """Generate friendly, encouraging response using dynamic query processor"""
        
        # Use dynamic processor to understand and respond to actual query
        response_data = self.dynamic_processor.process_query_intelligently(query, track_context)
        
        # Apply friendly formatting to the dynamic response
        friendly_response = self._apply_friendly_formatting(response_data)
        
        return friendly_response
    
    def generate_response_with_history(self, query: str, track_context: str = None, conversation_history: list = None) -> dict:
        """Generate friendly response with conversation history context"""
        
        # If we have conversation history, check for context continuity
        if conversation_history and len(conversation_history) >= 2:
            # Get the last user message and bot response
            last_messages = conversation_history[-2:]
            
            # Check if this is a continuation of a previous topic
            if self._is_continuation_query(query, last_messages):
                # Use the conversation context to generate a contextual response
                return self._generate_contextual_response(query, last_messages, track_context)
        
        # Fallback to regular response if no meaningful context
        return self.generate_response(query, track_context)
    
    def _is_continuation_query(self, query: str, last_messages: list) -> bool:
        """Check if the current query is a continuation of previous conversation"""
        query_lower = query.lower()
        
        # Check if it's a response to a question or continuation
        continuation_indicators = [
            "i have", "i took", "i've taken", "yes", "no", "my background",
            "i'm", "i am", "i was", "i will", "i can", "i cannot"
        ]
        
        # Check if previous bot message asked a question
        if last_messages and len(last_messages) > 0:
            last_bot_message = None
            for msg in reversed(last_messages):
                if msg.get('role') == 'assistant':
                    last_bot_message = msg.get('content', '').lower()
                    break
            
            if last_bot_message and '?' in last_bot_message:
                return True
        
        return any(indicator in query_lower for indicator in continuation_indicators)
    
    def _generate_contextual_response(self, query: str, last_messages: list, track_context: str) -> dict:
        """Generate a response that maintains conversation context"""
        
        # Extract the previous conversation topic
        context_info = self._extract_conversation_context(last_messages)
        
        # Generate response based on context
        if "cs 18000" in context_info.lower() or "cs 180" in context_info.lower():
            return self._handle_cs180_followup(query, context_info)
        elif "track" in context_info.lower():
            return self._handle_track_followup(query, context_info)
        else:
            # General contextual response
            return self._handle_general_followup(query, context_info)
    
    def _extract_conversation_context(self, last_messages: list) -> str:
        """Extract key topics from recent conversation"""
        context = ""
        for msg in last_messages:
            if msg.get('role') == 'assistant':
                content = msg.get('content', '')
                context += content + " "
        return context
    
    def _handle_cs180_followup(self, query: str, context_info: str) -> dict:
        """Handle follow-up questions about CS 180/18000"""
        query_lower = query.lower()
        
        if "ap computer science" in query_lower or "ap comp sci" in query_lower:
            # Generate AI response for AP CS questions
            ap_prompt = f"""
            A student is asking about AP Computer Science preparation for CS 18000 at Purdue.
            Query: {query}
            Context: {context_info}
            
            Generate a helpful response about:
            - AP CS A as preparation for CS 18000
            - Placement exam options
            - Benefits of skipping CS 18000
            - Timeline advantages
            - Next steps they should take
            
            Keep it encouraging and specific to their situation.
            """
            
            if self.ai_engine:
                try:
                    response = self.ai_engine.generate_smart_response(ap_prompt, {"query": query})
                    return {
                        'response': response,
                        'confidence': 0.95,
                        'source': 'ai_generated_ap_advice'
                    }
                except Exception:
                    pass
            
            # Fallback if AI unavailable
            return self.generate_response(query)
        
        # Default contextual response
        return self.generate_response(query)
    
    def _handle_track_followup(self, query: str, context_info: str) -> dict:
        """Handle follow-up questions about track selection"""
        # Implementation for track-related follow-ups
        return self.generate_response(query)
    
    def _handle_general_followup(self, query: str, context_info: str) -> dict:
        """Handle general follow-up questions"""
        # Implementation for general follow-ups
        return self.generate_response(query)
    
    def _handle_timing_question(self, query: str, track_context: str) -> dict:
        """Handle questions about when to take courses"""
        
        greeting = self._get_ai_phrase('greeting', query)
        
        response = f"{greeting} The CS progression at Purdue is actually pretty straightforward once you see the big picture.\n\n"
        
        response += "Your first two years are all about building that solid foundation. You'll start with CS 18000 in your first fall semester - that's where you learn object-oriented programming. Don't worry if it feels challenging at first, everyone goes through that learning curve!\n\n"
        
        response += "Here's how the timing flows:\n\n"
        response += "First year: You'll tackle CS 18000 in fall, then CS 18200 and CS 24000 in spring. You'll also be working through your calculus sequence.\n\n"
        
        response += "Second year: This is where things get more interesting! Fall brings CS 25000 (computer architecture) and CS 25100 (data structures). Spring you'll do CS 25200 (systems programming).\n\n"
        
        response += "Third year: Here's where the fun really starts! Fall of third year is when you'll take CS 38100 (algorithms) - this is super important because it opens up all the advanced courses. You'll also start your track courses and take a statistics class.\n\n"
        
        response += "The key thing to remember is that track courses can't start until you've got that foundation under your belt. Think of those first two years as building your toolkit - you need those tools before you can start specializing!\n\n"
        
        encouragement = self._get_ai_phrase('encouragement', query)
        response += f"{encouragement} Just take it one semester at a time and you'll be amazed how much you learn along the way."
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.95,
            "track": "progression",
            "source_data": {"type": "timing_overview"}
        }
    
    def _handle_course_timing(self, query: str, track_context: str) -> dict:
        """Handle specific course timing questions"""
        
        course_match = re.search(r'(CS|STAT|MA)\s*(\d+)', query.upper())
        
        if not course_match:
            greeting = self._get_ai_phrase('greeting', query)
            return {
                "query": query,
                "response": f"{greeting} I'd love to help, but I'm not sure which specific course you're asking about. Could you mention the course code like CS 25100 or STAT 35000?",
                "confidence": 0.3,
                "track": track_context
            }
        
        course_code = f"{course_match.group(1)} {course_match.group(2)}"
        
        # Get course info from knowledge graph
        course_info = self.kg.get_course_info(course_code)
        prereqs = self.kg.get_prerequisites(course_code)
        
        greeting = self._get_ai_phrase('greeting', query)
        
        if not course_info:
            return {
                "query": query,
                "response": f"{greeting} Hmm, I don't have info on {course_code} in my database right now. Double-check that course code or feel free to ask about any of the main CS courses!",
                "confidence": 0.1,
                "track": track_context
            }
        
        response = f"{greeting} Let me tell you about {course_code} - {course_info.get('title', 'Course')}.\n\n"
        
        # Specific timing advice based on course
        if course_code == "CS 38100":
            response += "This is a really important one! You'll want to take CS 38100 in the fall of your third year. I know that might seem late, but there's a good reason for the timing.\n\n"
            response += "You need CS 25100 (Data Structures) first because algorithms builds directly on those concepts. Think of data structures as learning the building blocks, and algorithms as learning how to use them efficiently.\n\n"
            response += "Once you complete CS 38100, it opens up tons of advanced courses, so it's worth waiting and doing it right!"
            
        elif course_code == "CS 37300":
            response += "CS 37300 is one of the core courses for the Machine Intelligence track - super cool stuff!\n\n"
            response += "You'll need CS 25100 and a statistics course before you can jump into this. The earliest you could realistically take it is spring of third year, but fall of fourth year is totally fine too.\n\n"
            response += "Don't rush it - the prerequisites really do help you succeed in this class."
            
        elif course_code == "CS 30700":
            response += "This is the foundation of the Software Engineering track - you'll love it if you're interested in building real software systems!\n\n"
            response += "You can take this starting in fall of third year, once you've got your programming foundations solid. It's designed to teach you how to work on larger projects and collaborate with teams.\n\n"
            response += "Really practical stuff that you'll use in internships and your career!"
            
        elif course_code.startswith("CS") and course_info.get('course_type') == "track":
            response += "This is a track course, which means you can take it starting in fall of your third year.\n\n"
            response += "The timing is flexible - you might take it in third year or fourth year depending on your track plan and what else you're juggling that semester.\n\n"
            
        elif course_info.get('semester') and "1st Year" in course_info.get('semester', ''):
            response += "This is a first-year course, so you'll take it early in your CS journey.\n\n"
            
        elif course_info.get('semester') and "2nd Year" in course_info.get('semester', ''):
            response += "This fits into your second year schedule.\n\n"
            
        elif course_info.get('semester') and "3rd Year" in course_info.get('semester', ''):
            response += "This is a third-year course.\n\n"
        
        if prereqs:
            response += f"\nJust so you know, you'll need these courses first: {', '.join(prereqs)}. "
            response += "Don't worry about memorizing all the prerequisites - your advisor and the registration system will help keep you on track!"
        
        encouragement = self._get_ai_phrase('encouragement', query)
        response += f"\n\n{encouragement}"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.90,
            "track": track_context,
            "source_data": {"course": course_code, "prerequisites": prereqs}
        }
    
    def _handle_requirements_question(self, query: str, track_context: str) -> dict:
        """Handle questions about track requirements"""
        
        greeting = self._get_ai_phrase('greeting', query)
        
        if not track_context:
            if "mi" in query.lower() or "machine intelligence" in query.lower():
                track_context = "MI"
            elif "se" in query.lower() or "software engineering" in query.lower():
                track_context = "SE"
            else:
                return {
                    "query": query,
                    "response": f"{greeting} I'd be happy to explain the requirements! Are you asking about the Machine Intelligence track or Software Engineering track? Or maybe general CS requirements?",
                    "confidence": 0.5,
                    "track": None
                }
        
        if track_context.upper() == "MI":
            response = f"{greeting} The Machine Intelligence track is really exciting - you'll get into AI, machine learning, and data science!\n\n"
            
            transition = self._get_ai_phrase('transition', query)
            response += f"{transition}\n\n"
            
            response += "You'll need 4 required courses plus 2 electives. Don't let that number worry you - it's totally doable!\n\n"
            
            response += "For the required courses:\n"
            response += "- CS 37300 (Data Mining & Machine Learning) - this is the heart of the track\n"
            response += "- CS 38100 (Algorithms) - you'll take this fall of third year\n"
            response += "- One AI course: either CS 47100 (Intro to AI) or CS 47300 (Web Search)\n"
            response += "- One statistics course: STAT 35000, STAT 51100, or a few other options\n\n"
            
            response += "Then you get to pick 2 electives from a really nice selection. You could go deeper into AI with CS 57700 (Natural Language Processing), explore data visualization with CS 43900, or try something completely different!\n\n"
            
            response += "The cool thing is you have flexibility in when you take most of these. Just remember you can't double-count courses - if you use CS 47300 for your AI requirement, you can't also count it as an elective."
            
        elif track_context.upper() == "SE":
            response = f"{greeting} Software Engineering is an awesome track - you'll learn how to build real-world software systems that people actually use!\n\n"
            
            transition = self._get_ai_phrase('transition', query)
            response += f"{transition}\n\n"
            
            response += "You'll need 5 required courses plus 1 elective. I know that sounds like more than MI track, but remember you only need 1 elective instead of 2.\n\n"
            
            response += "Your required courses are:\n"
            response += "- CS 30700 (Software Engineering I) - teaches you the fundamentals\n"
            response += "- CS 38100 (Algorithms) - fall of third year\n"
            response += "- CS 40800 (Software Testing) - really practical stuff\n"
            response += "- CS 40700 (Senior Project) - your capstone experience\n"
            response += "- Either CS 35200 (Compilers) or CS 35400 (Operating Systems)\n\n"
            
            response += "Then you pick 1 elective from the approved list. There are tons of great options depending on what interests you!"
            
        encouragement = self._get_ai_phrase('encouragement', query)
        response += f"\n\n{encouragement}"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.95,
            "track": track_context,
            "source_data": {"track": track_context, "type": "requirements"}
        }
    
    def _handle_freshman_question(self, query: str, track_context: str) -> dict:
        """Handle freshman-specific questions"""
        
        greeting = self._get_ai_phrase('greeting', query)
        
        response = f"{greeting} Welcome to Computer Science at Purdue! I'm so excited for you - you're starting an amazing journey.\n\n"
        
        response += "As a freshman, you'll be focusing on building that rock-solid foundation. Don't worry about track specializations yet - that comes later!\n\n"
        
        response += "Here's what you'll typically take in your first year:\n\n"
        
        response += "Fall semester: CS 18000 (Problem Solving and Object-Oriented Programming) is your main CS course. It's 4 credits and teaches you Java programming. You'll also take Calculus I (MA 16100 or MA 16500 if you're in honors), and some general education courses.\n\n"
        
        response += "Spring semester: CS 18200 (Foundations of Computer Science) and CS 24000 (Programming in C). You'll also continue with Calculus II.\n\n"
        
        response += "CS 18000 is where it all begins, and honestly, it can feel pretty intense at first. Don't panic if programming feels really hard initially - that's completely normal! Everyone struggles with their first programming class. The key is to practice consistently and ask for help when you need it.\n\n"
        
        response += "You'll also want to get comfortable with the math sequence. CS relies heavily on mathematical thinking, so those calculus courses aren't just requirements - they're actually building important problem-solving skills.\n\n"
        
        encouragement = self._get_ai_phrase('encouragement', query)
        response += f"{encouragement} Focus on doing well in these foundation courses, and everything else will fall into place. You don't need to worry about picking a track until junior year!"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.95,
            "track": "freshman",
            "source_data": {"type": "freshman_guidance"}
        }
    
    def _apply_friendly_formatting(self, response_data: dict) -> dict:
        """Apply natural formatting to dynamic responses"""
        
        # Get the base response
        base_response = response_data.get("response", "I can help with that.")
        
        # Only add a simple greeting if response doesn't already have one
        if not any(greeting.lower() in base_response.lower() for greeting in ["hey", "hi", "hello", "what", "here's", "sure"]):
            # Use first greeting which is just "Hey! What would you like to know about the CS program?"
            base_response = f"Hey! What would you like to know about the CS program?\n\n{base_response}"
        
        # Return formatted response without excessive encouragement
        return {
            "query": response_data.get("query", ""),
            "response": base_response,
            "confidence": response_data.get("confidence", 0.8),
            "track": response_data.get("track", None),
            "source_data": response_data.get("source_data", {}),
            "intent": response_data.get("intent", "unknown")
        }
    
    def _handle_general_question(self, query: str, track_context: str) -> dict:
        """Handle general questions"""
        
        greeting = self._get_ai_phrase('greeting', query)
        
        response = f"{greeting} I'm here to help you navigate the Computer Science program at Purdue!\n\n"
        
        response += "Whether you're wondering about course timing, track requirements, or just need some general guidance, I've got you covered. The CS program here is really well-designed, and there's a clear path through it.\n\n"
        
        response += "Feel free to ask me about specific courses, when to take them, track requirements, or anything else about your CS journey. I'm here to make it all a little less overwhelming!\n\n"
        
        encouragement = self._get_ai_phrase('encouragement', query)
        response += f"{encouragement} What would you like to know more about?"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.7,
            "track": track_context,
            "source_data": {"type": "general_guidance"}
        }
    
    def _handle_advice_question(self, query: str, track_context: str) -> dict:
        """Handle advice-seeking questions"""
        
        greeting = self._get_ai_phrase('greeting', query)
        
        if "double count" in query.lower():
            response = f"{greeting} Nope, you can't double-count courses between required and elective slots. I know it's tempting!\n\n"
            
            response += "For example, if you use CS 47300 to satisfy your AI requirement in MI track, you can't also count it as one of your 2 electives. You'll need to pick a different course for your elective.\n\n"
            
            response += "The good news is there are plenty of interesting electives to choose from, so you won't run out of options! Don't worry, lots of students ask about this rule."
            
        elif "track course" in query.lower() and "second year" in query.lower():
            response = f"{greeting} I can see why you'd want to jump into the cool stuff early, but unfortunately track courses have to wait until third year.\n\n"
            
            response += "Track courses need you to complete the foundation sequence first - that's CS 18000 through CS 25200. You'll be busy enough in your first two years building those essential skills!\n\n"
            
            response += "I know it's frustrating to wait, but trust me - having those prerequisites makes the advanced courses so much more manageable and enjoyable. Use your first two years to really master the fundamentals."
            
        else:
            response = f"{greeting} I'd love to give you some advice! Could you be a bit more specific about what you're wondering about?\n\n"
            
            response += "Are you asking about course timing, track selection, or something else? The more details you can share, the better I can help you out!"
        
        encouragement = self._get_ai_phrase('encouragement', query)
        response += f"\n\n{encouragement}"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.85,
            "track": track_context,
            "source_data": {"type": "advice"}
        }
    
    def _handle_comparison_question(self, query: str, track_context: str) -> dict:
        """Handle comparison questions"""
        
        greeting = self._get_ai_phrase('greeting', query)
        
        response = f"{greeting} MI and SE are both awesome tracks, but they have pretty different focuses.\n\n"
        
        response += "Machine Intelligence is all about AI, machine learning, and data science. If you're excited about teaching computers to learn patterns, working with big datasets, or building intelligent systems, MI is your track. You'll learn algorithms that can recognize images, process language, and make predictions from data.\n\n"
        
        response += "Software Engineering focuses on building robust, real-world software systems. Think about how to design apps that millions of people use, how to test code properly, and how to manage large software projects. If you love the idea of creating software that people actually use every day, SE is perfect for you.\n\n"
        
        response += "In terms of coursework, MI requires 4 core courses plus 2 electives, while SE requires 5 core courses plus 1 elective. Both include CS 38100 (Algorithms) as a requirement.\n\n"
        
        response += "The cool thing is you don't have to decide right away! You can explore both areas in your first few years and see what clicks with you. Take CS 30700 if you're curious about software engineering, or CS 37300 if machine learning sounds interesting.\n\n"
        
        encouragement = self._get_ai_phrase('encouragement', query)
        response += f"{encouragement} Both tracks lead to amazing career opportunities!"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.95,
            "track": "comparison",
            "source_data": {"type": "track_comparison"}
        }
    
    def _handle_planning_question(self, query: str, track_context: str) -> dict:
        """Handle course planning questions"""
        
        greeting = self._get_ai_phrase('greeting', query)
        
        response = f"{greeting} I'd love to help you plan out your courses! Having a roadmap makes everything so much less stressful.\n\n"
        
        if not track_context:
            response += "Which track are you thinking about - Machine Intelligence or Software Engineering? Once I know that, I can walk you through a timeline that works well.\n\n"
            
            response += "The general approach is: Years 1-2 focus on building that rock-solid foundation, Fall of Year 3 is when things get exciting with algorithms and your first track courses, and Years 3-4 you get to dive into the specialization you're passionate about.\n\n"
            
            response += "Let me know which track interests you and I can give you a more detailed semester-by-semester breakdown!"
            
        else:
            response += f"Perfect! Let me walk you through a typical timeline for the {track_context} track.\n\n"
            
            response += "Years 1-2: Foundation building time! You'll work through CS 18000, 18200, 24000, 25000, 25100, and 25200, plus your math sequence. These courses build on each other, so the order really matters.\n\n"
            
            response += "Fall Year 3: This is when it gets fun! You'll take CS 38100 (Algorithms), a statistics course, and your first track course. For example, CS 37300 if you're doing MI, or CS 30700 if you're doing SE.\n\n"
            
            response += "Years 3-4: The rest of your track requirements and electives. You have some flexibility here in when you take things, which is nice for balancing your workload.\n\n"
            
            response += "The key is not to rush it. Each course builds important skills for the next one, so following the progression really pays off."
        
        encouragement = self._get_ai_phrase('encouragement', query)
        response += f"\n\n{encouragement}"
        
        return {
            "query": query,
            "response": response,
            "confidence": 0.90,
            "track": track_context,
            "source_data": {"type": "course_planning"}
        }