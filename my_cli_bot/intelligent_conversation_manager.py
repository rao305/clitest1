#!/usr/bin/env python3
"""
Intelligent Conversation Manager for Purdue CS Academic Advisor
Manages conversation context, memory, and provides personalized responses
Uses all implemented knowledge schemas and graduation planning systems
"""

import json
import re
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import uuid
import os

# Import the smart AI engine
from smart_ai_engine import SmartAIEngine, QueryIntent
# Import AI training prompts
from ai_training_prompts import get_comprehensive_system_prompt
# Import resilient Gemini client
from simple_boiler_ai import ResilientGeminiClient

@dataclass
class StudentProfile:
    """Student profile information"""
    student_id: str
    name: str = ""
    current_year: str = ""
    target_track: str = ""
    completed_courses: List[str] = None
    gpa: float = 0.0
    graduation_goals: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.completed_courses is None:
            self.completed_courses = []
        if self.graduation_goals is None:
            self.graduation_goals = {}

@dataclass
class ConversationContext:
    """Manages conversation memory and student context"""
    session_id: str
    student_profile: Optional[StudentProfile] = None
    conversation_history: List[Dict[str, str]] = None
    extracted_context: Dict[str, Any] = None
    current_topic: str = "general"
    last_queries: List[str] = None
    personalization_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.extracted_context is None:
            self.extracted_context = {}
        if self.last_queries is None:
            self.last_queries = []
        if self.personalization_data is None:
            self.personalization_data = {}

class IntelligentConversationManager:
    """Enhanced conversation manager with smart AI integration"""
    
    def __init__(self, tracker_mode=False):
        # Universal query tracker mode
        self.tracker_mode = tracker_mode
        self.tracking_data = []
        
        # Initialize smart AI engine
        self.smart_ai_engine = SmartAIEngine()
        
        # Load conversation contexts
        self.conversation_contexts = {}
        self.context_persistence_file = "conversation_contexts.json"
        self._load_persistent_contexts()
        
        # Initialize patterns and templates
        self.intent_patterns = self._initialize_intent_patterns()
        self.response_templates = self._initialize_response_templates()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize academic advisor (if available)
        try:
            from enhanced_smart_advisor import EnhancedSmartAdvisor
            self.academic_advisor = EnhancedSmartAdvisor()
        except ImportError:
            self.academic_advisor = None
            self.logger.warning("EnhancedSmartAdvisor not available")
        
        # Initialize graduation planner (if available)
        try:
            from graduation_planner import AdvancedGraduationPlanner
            self.graduation_planner = AdvancedGraduationPlanner(
                knowledge_file="data/cs_knowledge_graph.json",
                db_file="purdue_cs_knowledge.db"
            )
        except ImportError:
            self.graduation_planner = None
            self.logger.warning("AdvancedGraduationPlanner not available")
        
        # Initialize personalized graduation planner
        try:
            from personalized_graduation_planner import PersonalizedGraduationPlanner
            self.personalized_planner = PersonalizedGraduationPlanner(
                knowledge_file="data/cs_knowledge_graph.json",
                db_file="purdue_cs_knowledge.db"
            )
        except ImportError:
            self.personalized_planner = None
            self.logger.warning("PersonalizedGraduationPlanner not available")
        
        # Initialize AI response generator
        try:
            from ai_response_generator import AIResponseGenerator
            self.ai_response_generator = AIResponseGenerator(
                knowledge_file="data/cs_knowledge_graph.json"
            )
        except ImportError:
            self.ai_response_generator = None
            self.logger.warning("AIResponseGenerator not available")
        
        # Initialize career networking (if available and enabled)
        self.career_networking = None
        self.clado_ai_client = None
        try:
            from feature_flags import is_career_networking_enabled
            if is_career_networking_enabled():
                # Try new AI-powered Clado client first
                try:
                    from clado_ai_client import create_clado_client
                    self.clado_ai_client = create_clado_client()
                    if self.clado_ai_client:
                        self.logger.info("AI-powered Clado client initialized successfully")
                    else:
                        self.logger.warning("Could not initialize AI-powered Clado client - missing Gemini key")
                except ImportError:
                    self.logger.warning("AI-powered Clado client not available")
                
                # Fallback to legacy career networking
                try:
                    from career_networking import CareerNetworkingInterface
                    clado_api_key = os.environ.get("CLADO_API_KEY")
                    if clado_api_key:
                        self.career_networking = CareerNetworkingInterface(clado_api_key)
                        self.logger.info("Legacy career networking initialized as fallback")
                    else:
                        self.logger.warning("CLADO_API_KEY not set - career networking unavailable")
                except ImportError:
                    self.logger.warning("Legacy career networking not available")
            else:
                self.logger.info("Career networking disabled by feature flag")
        except ImportError:
            self.career_networking = None
            self.logger.warning("Feature flags not available")
        
        # Initialize Gemini client (if available)
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                self.gemini_model = ResilientGeminiClient(api_key=api_key)
                self.Gemini_available = True
            else:
                self.gemini_model = None
                self.Gemini_available = False
                self.logger.warning("Gemini API key not found in environment")
        except Exception as e:
            self.gemini_model = None
            self.Gemini_available = False
            self.logger.warning(f"Gemini client initialization failed: {e}")
        
        # Load knowledge base
        with open("data/cs_knowledge_graph.json", 'r') as f:
            self.knowledge_base = json.load(f)
        
        # Intent patterns for better understanding
        self.intent_patterns = self._initialize_intent_patterns()
        
        # Personalized response templates
        self.response_templates = self._initialize_response_templates()
        
    def refresh_career_networking(self):
        """Refresh career networking based on current feature flag state"""
        try:
            from feature_flags import is_career_networking_enabled
            
            should_be_enabled = is_career_networking_enabled()
            is_currently_enabled = self.career_networking is not None or self.clado_ai_client is not None
            
            if should_be_enabled and not is_currently_enabled:
                # Enable career networking - try AI-powered client first
                try:
                    from clado_ai_client import create_clado_client
                    self.clado_ai_client = create_clado_client()
                    if self.clado_ai_client:
                        self.logger.info("AI-powered Clado client enabled dynamically")
                    else:
                        self.logger.warning("Could not enable AI-powered Clado client - missing Gemini key")
                except ImportError:
                    self.logger.warning("AI-powered Clado client not available for dynamic enable")
                
                # Fallback to legacy career networking
                if not self.clado_ai_client:
                    try:
                        from career_networking import CareerNetworkingInterface
                        clado_api_key = os.environ.get("CLADO_API_KEY")
                        if clado_api_key:
                            self.career_networking = CareerNetworkingInterface(clado_api_key)
                            self.logger.info("Legacy career networking enabled dynamically as fallback")
                        else:
                            self.logger.warning("CLADO_API_KEY not set - cannot enable legacy career networking")
                    except ImportError:
                        self.logger.warning("Legacy career networking not available for dynamic enable")
                    
            elif not should_be_enabled and is_currently_enabled:
                # Disable career networking
                self.career_networking = None
                self.clado_ai_client = None
                self.logger.info("Career networking disabled dynamically")
                
        except Exception as e:
            self.logger.error(f"Error refreshing career networking: {e}")
    
    def _is_career_networking_query(self, query: str) -> bool:
        """Check if query is related to career networking"""
        import re
        query_lower = query.lower()
        
        # Check against career networking patterns
        for pattern in self.intent_patterns.get("career_networking", []):
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def _format_career_networking_response(self, career_response: Dict, original_query: str) -> str:
        """Format career networking API response for natural conversation"""
        if not career_response.get('success', False):
            # Generate AI response for career networking failure
            error_context = {
                "query": original_query,
                "error_type": "networking_search_failed",
                "suggestions": ["try broader terms", "check back later", "refine search criteria"]
            }
            
            prompt = f"""
            Generate a helpful response when career networking search fails.
            Original query: {original_query}
            Context: Unable to find professionals matching criteria
            
            Provide encouraging response with actionable suggestions.
            Keep it natural and supportive.
            """
            
            try:
                return self.smart_ai_engine.generate_smart_response(prompt, error_context)
            except:
                # Generate AI response for no search results
                try:
                    return self.smart_ai_engine.generate_smart_response(
                        "Generate a helpful response when no professionals are found in a career search. Suggest trying broader terms or checking back later.",
                        {"context": "career_search_no_results"}
                    )
                except:
                    return self._get_emergency_ai_response("No professionals found in search. Suggest broader search terms.")
        
        data = career_response.get('data', {})
        results = data.get('results', [])
        
        if not results:
            suggestions = data.get('suggestions', [])
            response = "I couldn't find any professionals matching your specific criteria. "
            if suggestions:
                response += "Here are some suggestions to try: " + "; ".join(suggestions[:2])
            return response
        
        # Build natural response
        response_parts = []
        response_parts.append(f"I found some great professionals who might interest you:")
        
        for i, professional in enumerate(results, 1):
            name = professional.get('name', 'Unknown')
            title = professional.get('title', 'Unknown')
            company = professional.get('company', 'Unknown')
            location = professional.get('location', '')
            relevance_note = professional.get('relevance_note', '')
            
            professional_info = f"{i}. {name} is a {title} at {company}"
            if location:
                professional_info += f" in {location}"
            if relevance_note:
                professional_info += f" ({relevance_note})"
            
            response_parts.append(professional_info)
        
        # Add follow-up suggestions
        follow_ups = data.get('follow_up_suggestions', [])
        if follow_ups:
            response_parts.append("")
            response_parts.append("Would you like me to help you with anything else? " + follow_ups[0])
        
        return "\n".join(response_parts)
    
    def _track_query(self, stage: str, data: Any, description: str = ""):
        """Track query processing when tracker mode is enabled"""
        if self.tracker_mode:
            print(f"\n🔍 [TRACKER] {stage.upper()}")
            print(f"    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            if description:
                print(f"    📋 {description}")
            
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (list, dict)) and len(str(value)) > 100:
                        print(f"    📊 {key}: {type(value).__name__} with {len(value)} items")
                    else:
                        print(f"    📊 {key}: {value}")
            elif isinstance(data, str):
                print(f"    📝 {data}")
            else:
                print(f"    📊 {type(data).__name__}: {data}")
            print(f"    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def _get_emergency_ai_response(self, prompt: str) -> str:
        """Emergency AI response when all else fails - no hardcoded text"""
        try:
            from simple_boiler_ai import SimpleBoilerAI
            emergency_ai = SimpleBoilerAI()
            return emergency_ai.get_ai_response(prompt)
        except:
            return ""  # Return empty instead of hardcoded fallback

    def _load_persistent_contexts(self):
        """Load persistent conversation contexts from file"""
        try:
            if os.path.exists(self.context_persistence_file):
                with open(self.context_persistence_file, 'r') as f:
                    data = json.load(f)
                    for session_id, context_data in data.items():
                        # Reconstruct ConversationContext objects
                        context = ConversationContext(
                            session_id=session_id,
                            student_profile=context_data.get("student_profile"),
                            conversation_history=context_data.get("conversation_history", []),
                            extracted_context=context_data.get("extracted_context", {}),
                            current_topic=context_data.get("current_topic", "general"),
                            last_queries=context_data.get("last_queries", []),
                            personalization_data=context_data.get("personalization_data", {})
                        )
                        self.conversation_contexts[session_id] = context
        except Exception as e:
            print(f"Error loading persistent contexts: {e}")

    def _save_persistent_contexts(self):
        """Save conversation contexts to file for persistence"""
        try:
            # Convert contexts to serializable format
            serializable_contexts = {}
            for session_id, context in self.conversation_contexts.items():
                serializable_contexts[session_id] = {
                    "student_profile": context.student_profile,
                    "conversation_history": context.conversation_history,
                    "extracted_context": context.extracted_context,
                    "current_topic": context.current_topic,
                    "last_queries": context.last_queries,
                    "personalization_data": context.personalization_data
                }
            
            with open(self.context_persistence_file, 'w') as f:
                json.dump(serializable_contexts, f, indent=2)
        except Exception as e:
            print(f"Error saving persistent contexts: {e}")

    def _validate_and_clean_context(self, context: ConversationContext):
        """Validate and clean context data for consistency"""
        
        # Validate extracted courses
        completed_courses = context.extracted_context.get("completed_courses", [])
        validated_courses = []
        for course in completed_courses:
            # Normalize course codes (CS 180 -> CS 18000)
            normalized = self._normalize_course_code(course)
            if normalized and normalized in self.knowledge_base["courses"]:
                validated_courses.append(normalized)
        
        context.extracted_context["completed_courses"] = list(set(validated_courses))
        
        # Validate track selection
        target_track = context.extracted_context.get("target_track", "")
        if target_track and target_track not in self.knowledge_base["tracks"]:
            # Try to match partial names
            for track_name in self.knowledge_base["tracks"]:
                if target_track.lower() in track_name.lower():
                    context.extracted_context["target_track"] = track_name
                    break
        
        # Validate year progression
        current_year = context.extracted_context.get("current_year", "")
        completed = len(context.extracted_context.get("completed_courses", []))
        if completed >= 6 and current_year == "freshman":
            context.extracted_context["current_year"] = "sophomore"
        elif completed >= 12 and current_year == "sophomore":
            context.extracted_context["current_year"] = "junior"

    def _normalize_course_code(self, course_code: str) -> str:
        """Normalize course codes to standard format"""
        if not course_code:
            return ""
        
        # Handle common formats: CS 180 -> CS 18000, CS180 -> CS 18000
        course_code = course_code.upper().replace(" ", "")
        
        # Extract department and number
        import re
        match = re.match(r"([A-Z]+)(\d+)", course_code)
        if not match:
            return course_code
        
        dept, num = match.groups()
        
        # Normalize CS course numbers
        if dept == "CS" and len(num) == 3:
            # Handle 3-digit course codes: 180 -> 18000, 182 -> 18200, 240 -> 24000
            if num.startswith("18") or num.startswith("24") or num.startswith("25"):
                return f"{dept} {num}00"
            # Handle other 3-digit codes
            elif num.startswith("31") or num.startswith("34") or num.startswith("35"):
                return f"{dept} {num}00"
            elif num.startswith("37") or num.startswith("38") or num.startswith("39"):
                return f"{dept} {num}00"
            elif num.startswith("41") or num.startswith("44") or num.startswith("45"):
                return f"{dept} {num}00"
            elif num.startswith("47") or num.startswith("48") or num.startswith("49"):
                return f"{dept} {num}00"
        elif dept == "MA" and len(num) == 3:
            if num.startswith("16") or num.startswith("26"):
                return f"{dept} {num}00"
        elif dept == "STAT" and len(num) == 3:
            if num.startswith("35") or num.startswith("41") or num.startswith("51"):
                return f"{dept} {num}00"
        
        return f"{dept} {num}"

    def _is_greeting(self, query: str) -> bool:
        """Universal greeting detection that adapts to ANY greeting pattern"""
        
        query_lower = query.lower().strip()
        words = query_lower.split()
        
        # Method 1: Universal greeting words (core greeting vocabulary)
        greeting_roots = {
            # Core greetings
            "hi", "hello", "hey", "hiya", "howdy", "yo", "sup", "greetings", "salutations",
            # What's up family
            "wassup", "whassup", "wazzup", "whazzup", "wsup", "wussup",
            # International greetings
            "hola", "bonjour", "guten", "ciao", "namaste", "shalom", "aloha",
            # Casual/slang
            "whaddup", "ayy", "yooo", "heyo", "heyy", "hiiii", "suuup",
            # Internet/gaming
            "o/", "heya", "hai", "harro", "henlo"
        }
        
        # Method 2: Greeting patterns (any variation)
        greeting_patterns = [
            # Basic patterns with any repetition
            r"^(hi|hello|hey|yo|sup|hiya|howdy|greetings)+[y!s]*[\s!?]*$",
            # What's up variations (unlimited flexibility)
            r"^w(hat|h|as|azzup|assup|ussup).*up[\s!?]*$",
            r"^what[\s']*(s|is|z)\s*(up|good|new|poppin|crackin|happenin)[\s!?]*$",
            # Time-based greetings
            r"^good\s*(morning|afternoon|evening|night|day)[\s!?]*$",
            # How questions that are greetings
            r"^how[\s']*(s|is|are)?\s*(you|it|things|everything|life|stuff).*$",
            r"^how.*going[\s!?]*$",
            r"^how.*doing[\s!?]*$",
            r"^how.*been[\s!?]*$",
            # Conversational starters
            r"^what.*going.*on[\s!?]*$",
            r"^what.*happening[\s!?]*$",
            r"^what.*new[\s!?]*$",
            r"^what.*good[\s!?]*$",
            # Any greeting word with casual additions
            r"^(hi|hello|hey|yo)\s+(there|man|dude|friend|buddy|bro|sis|fam)[\s!?]*$",
            # Single word greetings with variations
            r"^(ayy|yooo+|heyyy+|hiii+|supp+|wassup+)[\s!?]*$"
        ]
        
        import re
        for pattern in greeting_patterns:
            if re.match(pattern, query_lower):
                return True
        
        # Method 3: Intelligent word analysis for ANY greeting combination
        if len(words) <= 5:  # Keep it to short phrases
            # Check for any greeting root words
            has_greeting = False
            for word in words:
                # Direct match
                if word in greeting_roots:
                    has_greeting = True
                    break
                # Partial match for extended versions (heyyy, yooo, etc.)
                for root in greeting_roots:
                    if word.startswith(root) and len(word) <= len(root) + 4:
                        has_greeting = True
                        break
                if has_greeting:
                    break
            
            if has_greeting:
                # Make sure it's not a complex academic question
                academic_words = {
                    "course", "class", "credit", "semester", "graduation", "track", 
                    "requirement", "prerequisite", "codo", "gpa", "grade", "major",
                    "computer", "science", "cs", "programming", "algorithm"
                }
                
                # If it has academic words, it's probably not just a greeting
                academic_count = sum(1 for word in words if word in academic_words)
                if academic_count == 0:  # No academic context
                    return True
                elif academic_count == 1 and len(words) <= 3:  # Minimal academic context
                    return True
        
        # Method 4: Semantic greeting detection using context clues
        greeting_indicators = {
            # Question words that indicate social interaction
            "how", "what", "whats", "how's", "hows",
            # Social state words
            "doing", "going", "happening", "new", "good", "up", "poppin", "crackin"
        }
        
        if len(words) <= 4 and len(words) >= 2:
            # Check if it follows greeting question patterns
            has_question_starter = words[0] in {"how", "what", "whats", "how's", "hows"}
            has_social_word = any(word in greeting_indicators for word in words[1:])
            
            if has_question_starter and has_social_word:
                # Additional filter: make sure it's not an academic question
                if not any(word in words for word in ["course", "class", "cs", "purdue", "semester", "credit"]):
                    return True
        
        # Method 5: Universal fallback - extremely short informal queries
        if len(query_lower) <= 10 and len(words) <= 2:
            # Common informal expressions that are essentially greetings
            informal_greetings = {
                "ayy", "ey", "eyyy", "yep", "yup", "yooo", "oy", "oiii", 
                "wagwan", "wsgood", "aye", "ayee", "yoyo", "halo", "haloo"
            }
            
            if any(word in informal_greetings for word in words):
                return True
        
        return False

    def _initialize_intent_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for intent recognition"""
        return {
            "graduation_planning": [
                r"graduation.*plan", r"when.*graduate", r"graduate.*early", 
                r"early.*graduation", r"delay.*graduation", r"timeline.*graduate"
            ],
            "greeting": [
                r"^hi$", r"^hello$", r"^hey$", r"^yo$", r"^sup$", r"^hiya$", r"^howdy$",
                r"^hi there$", r"^hello there$", r"^hey there$", r"^yo wassup$",
                r"^what.*up", r"^wassup", r"^wazzup", r"^what up",
                r"^good morning$", r"^good afternoon$", r"^good evening$",
                r"^heyyy*$", r"^heyy*$", r"^hellooo*$", r"^hiiii*$"
            ],
            "track_selection": [
                r"machine.*intelligence", r"software.*engineering", r"track.*choose",
                r"concentration", r"specialization", r"MI.*track", r"SE.*track"
            ],
            "course_planning": [
                # Basic course planning queries
                r"next.*semester", r"course.*schedule", r"prerequisite", r"prereq",
                r"what.*take", r"course.*order", r"sequence", r"classes.*available",
                r"machine.*intelligence.*classes", r"mi.*classes", r"track.*classes",
                r"software.*engineering.*classes", r"se.*classes", r"se.*track.*classes",
                r"options.*select", r"course.*options",
                
                # Multi-year planning queries
                r"courses.*from.*freshman.*to.*senior", r"courses.*from.*freshman.*year.*to.*senior",
                r"4.*year.*plan", r"four.*year.*plan", r"all.*years", r"entire.*degree",
                r"courses.*i.*will.*be.*taking", r"courses.*i.*will.*take", r"classes.*i.*will.*take",
                r"see.*courses", r"show.*courses", r"list.*courses", r"course.*list",
                r"cs.*courses.*and.*math.*courses", r"cs.*and.*math.*courses",
                r"what.*courses.*each.*year", r"courses.*per.*year", r"year.*by.*year",
                r"sophomore.*to.*senior", r"after.*freshman", r"years.*after",
                
                # Year-specific planning
                r"freshman.*should.*take", r"freshman.*should.*taking", r"freshman.*courses",
                r"sophomore.*should.*take", r"sophomore.*should.*taking", r"sophomore.*courses",
                r"junior.*should.*take", r"junior.*should.*taking", r"junior.*courses",
                r"senior.*should.*take", r"senior.*should.*taking", r"senior.*courses",
                r"compulsory.*courses.*(freshman|sophomore|junior|senior)",
                r"required.*courses.*(freshman|sophomore|junior|senior)",
                r"(freshman|sophomore|junior|senior).*computer.*science",
                r"first.*year.*courses", r"second.*year.*courses", r"third.*year.*courses", r"fourth.*year.*courses",
                r"start.*off.*with", r"courses.*for.*(freshman|sophomore|junior|senior)",
                r"what.*courses.*(freshman|sophomore|junior|senior).*take",
                
                # Course type specific
                r"cs.*courses", r"math.*courses", r"computer.*science.*courses",
                r"core.*courses", r"elective.*courses", r"required.*courses",
                r"mathematics.*courses", r"programming.*courses",
                
                # ML/Track specific course planning
                r"machine.*learning.*courses", r"ml.*courses", r"ai.*courses",
                r"specializ.*ml", r"specializ.*machine.*learning",
                r"track.*courses", r"concentration.*courses"
            ],
            "course_difficulty": [
                r"how.*hard", r"difficult", r"difficulty", r"tough", r"challenging",
                r"time.*commitment", r"workload", r"easy.*hard", r"manageable",
                r"cs.*180.*hard", r"cs.*18000.*hard", r"struggle", r"tips.*success"
            ],
            "failure_recovery": [
                r"fail", r"failed", r"failing", r"didn.*pass", r"retake", r"recover", 
                r"delay", r"behind.*schedule", r"struggling", r"repeated.*course",
                r"failed.*cs", r"fail.*cs", r"cs.*failed", r"cs.*fail"
            ],
            "codo_advice": [
                r"change.*major", r"codo", r"switch.*cs", r"transfer.*cs", 
                r"requirements.*cs"
            ],
            "cs_minor_planning": [
                r"minor.*computer.*science", r"cs.*minor", r"computer.*science.*minor",
                r"minor.*in.*cs", r"minor.*cs", r"cs.*5.*courses",
                r"off.*peak.*courses", r"peak.*off.*peak", r"minor.*requirements",
                r"when.*can.*take.*cs", r"cs.*courses.*minor", r"minor.*course.*access",
                r"cs.*minor.*complete", r"how.*many.*cs.*courses.*minor",
                r"cs.*minor.*planning", r"minor.*scheduling", r"cs.*minor.*schedule"
            ],
            "career_guidance": [
                r"career", r"job", r"internship", r"industry", r"graduate.*school",
                r"research", r"work.*experience"
            ],
            "career_networking": [
                r"alumni", r"professionals", r"mentor", r"mentorship", r"network", r"networking",
                r"purdue.*graduates", r"purdue.*grad", r"cs.*alumni", r"people.*working", 
                r"find.*professionals", r"find.*me.*grad", r"find.*me.*alumni",
                r"connect.*with", r"working.*at.*", r"landed.*role.*at", r"role.*at.*",
                r"career.*connections", r"industry.*contacts",
                r"professionals.*in", r"people.*in.*field", r"alumni.*network"
            ],
            "academic_standing": [
                r"gpa", r"grade", r"academic.*standing", r"probation", r"performance"
            ]
        }

    def _initialize_response_templates(self) -> Dict[str, Dict[str, str]]:
        """Initialize personalized response templates"""
        return {
            "graduation_planning": {
                "early_graduation": "Based on your {track} track and current progress, here's your early graduation analysis:",
                "standard_timeline": "For your {track} concentration, here's the recommended graduation timeline:",
                "delay_recovery": "I see you're dealing with course setbacks. Let me help you create a recovery plan:"
            },
            "track_guidance": {
                "machine_intelligence": "For Machine Intelligence track, focusing on your {career_goal} goal:",
                "software_engineering": "For Software Engineering track, considering your {career_goal} interests:",
                "track_comparison": "Comparing tracks based on your {background} and {goals}:"
            },
            "course_planning": {
                "next_semester": "For your {year} {semester} schedule, considering your {track} track:",
                "prerequisite_help": "Based on your completed courses {completed}, here are your options:",
                "heavy_load": "Given your {gpa} GPA, I recommend this course load strategy:"
            }
        }

    def process_query(self, session_id: str, user_query: str) -> str:
        """Main method to process user queries with smart AI integration"""
        
        try:
            # Refresh career networking state based on feature flags
            self.refresh_career_networking()
            
            # Validate query
            validated_query = self._validate_query(user_query)
            if validated_query != user_query:
                return validated_query
            
            # Get or create conversation context
            if session_id not in self.conversation_contexts:
                self.conversation_contexts[session_id] = ConversationContext(session_id=session_id)
                self._track_query("SESSION_CREATED", {"session_id": session_id}, "Created new conversation session")
            
            context = self.conversation_contexts[session_id]
            
            # Add to conversation history
            context.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user": user_query,
                "system": None
            })
            
            # Update context from query
            self._update_context_from_query(context, user_query)
            
            # Check for career networking queries first
            if self._is_career_networking_query(user_query) and (self.clado_ai_client or self.career_networking):
                try:
                    # Use AI-powered Clado client if available
                    if self.clado_ai_client:
                        import asyncio
                        career_response = asyncio.run(
                            self.clado_ai_client.search_professionals(user_query)
                        )
                        
                        # Update conversation context and return response
                        context.conversation_history[-1]["system"] = career_response
                        self._track_query("CAREER_NETWORKING_AI", 
                                        {"session_id": session_id, "query_type": "ai_powered"}, 
                                        "Processed career networking query with AI-powered Clado client")
                        return career_response
                    
                    # Fallback to legacy career networking
                    elif self.career_networking:
                        # Prepare student context for legacy career search
                        student_context = {
                            'session_id': session_id,
                            'year': context.extracted_context.get("current_year", ""),
                            'track': context.extracted_context.get("target_track", ""),
                            'gpa_range': context.extracted_context.get("gpa_range", ""),
                            'career_interests': context.extracted_context.get("career_interests", []),
                            'target_companies': context.extracted_context.get("target_companies", []),
                            'completed_courses': context.extracted_context.get("completed_courses", [])
                        }
                        
                        # Process career networking query asynchronously
                        import asyncio
                        career_response = asyncio.run(
                            self.career_networking.process_career_query(student_context, user_query)
                        )
                        
                        if career_response.get('success', False):
                            # Format career networking response for natural conversation
                            formatted_response = self._format_career_networking_response(career_response, user_query)
                            
                            # Update conversation history
                            if context.conversation_history:
                                context.conversation_history[-1]["system"] = formatted_response
                            
                            # Update last queries
                            context.last_queries.append(user_query)
                            if len(context.last_queries) > 10:
                                context.last_queries = context.last_queries[-10:]
                                
                            # Save context
                            self._save_persistent_contexts()
                            
                            self._track_query("CAREER_NETWORKING_LEGACY", {
                                "session_id": session_id,
                                "query_length": len(user_query),
                                "response_length": len(formatted_response),
                                "method": "legacy_career_networking"
                            }, "Career networking query processed with legacy system")
                            
                            return formatted_response
                        
                except Exception as e:
                    self.logger.error(f"Career networking error: {e}")
                    # Fall through to smart AI engine if career networking fails
            
            # Use smart AI engine for primary processing
            self.logger.info(f"Processing query with smart AI engine: {user_query[:50]}...")
            
            # Convert context to format expected by smart AI engine
            ai_context = {
                "current_year": context.extracted_context.get("current_year"),
                "target_track": context.extracted_context.get("target_track"),
                "completed_courses": context.extracted_context.get("completed_courses", []),
                "last_queries": context.last_queries[-3:] if context.last_queries else [],
                "graduation_timeline_goals": context.extracted_context.get("graduation_timeline_goals"),
                "session_id": session_id
            }
            
            # Process with smart AI engine
            response = self.smart_ai_engine.process_query(user_query, ai_context)
            
            # Update conversation history with response
            if context.conversation_history:
                context.conversation_history[-1]["system"] = response
            
            # Update last queries
            context.last_queries.append(user_query)
            if len(context.last_queries) > 10:
                context.last_queries = context.last_queries[-10:]
            
            # Save context
            self._save_persistent_contexts()
            
            self._track_query("QUERY_PROCESSED", {
                "session_id": session_id,
                "query_length": len(user_query),
                "response_length": len(response),
                "method": "smart_ai_engine"
            }, "Query processed successfully with smart AI engine")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            
            # Fallback to original method if smart AI fails
            try:
                self.logger.info("Falling back to original conversation manager")
                return self._fallback_process_query(session_id, user_query)
            except Exception as fallback_error:
                self.logger.error(f"Fallback also failed: {fallback_error}")
                # Generate AI response for processing error
                error_prompt = f"""
The user asked: "{user_query}"
I encountered a technical issue while processing their request.
Please provide a helpful, conversational response that:
1. Acknowledges there was an issue naturally
2. Suggests they try rephrasing their question
3. Offers alternative ways to ask about Purdue CS topics
4. Maintains a supportive, helpful tone
Don't mention technical errors - focus on helping them get their academic information.
"""
                return self.ai_client.chat_completion_with_retry(
                    ,
                    prompt,
                    ,
                    
                ) or "I'm experiencing some difficulties right now. Could you try asking your question in a different way?"
    
    def _fallback_process_query(self, session_id: str, user_query: str) -> str:
        """Fallback method using original conversation manager logic"""
        
        # Get or create conversation context
        if session_id not in self.conversation_contexts:
            self.conversation_contexts[session_id] = ConversationContext(session_id=session_id)
        
        context = self.conversation_contexts[session_id]
        
        # Check if this is a greeting
        if self._is_greeting(user_query):
            self._track_query("GREETING_DETECTED", {"query": user_query}, "Processing greeting")
            return self._handle_greeting(context)
        
        # Analyze intent using original method
        intent_analysis = self._analyze_intent(user_query, context)
        
        # Generate clarification if needed
        if intent_analysis.get("requires_clarification", False):
            return self._generate_clarification_response(user_query, context, intent_analysis)
        
        # Generate intelligent response using original method
        response = self._generate_intelligent_response(user_query, context, intent_analysis)
        
        # Update conversation history
        if context.conversation_history:
            context.conversation_history[-1]["system"] = response
        
        return response

    def _validate_query(self, query: str) -> str:
        """Validate and clean user query"""
        if not query or not query.strip():
            return ""
        
        # Clean the query
        cleaned = query.strip()
        
        # Check for minimum length
        if len(cleaned) < 2:
            return ""
        
        # Basic validation only - greeting detection happens in intent analysis
        
        # Check for offensive content (basic)
        offensive_patterns = ["fuck", "shit", "damn", "bitch"]
        if any(pattern in cleaned.lower() for pattern in offensive_patterns):
            return ""
        
        return cleaned

    def _generate_clarification_response(self, query: str, context: ConversationContext, intent_analysis: Dict[str, Any]) -> str:
        """Generate clarification questions for ambiguous queries"""
        
        confidence = intent_analysis.get("confidence", 0.0)
        detected_intents = intent_analysis.get("all_intents", {})
        
        if confidence < 0.4:
            # Generate AI response for unclear query
            unclear_prompt = f"""
The user asked: "{user_query}"
I couldn't determine what they're asking about clearly. Please provide a helpful response that:
1. Acknowledges their question naturally
2. Asks for clarification in a friendly way
3. Suggests specific Purdue CS topics they might be asking about (courses, graduation planning, tracks, etc.)
4. Maintains a supportive tone
"""
            return self.ai_client.chat_completion_with_retry(
                ,
                prompt,
                ,
                
            ) or "Could you tell me more about what you'd like to know? I can help with courses, graduation planning, or track requirements."
        
        elif confidence < 0.7 and len(detected_intents) > 1:
            # Multiple possible intents
            top_intents = sorted(detected_intents.items(), key=lambda x: x[1], reverse=True)[:2]
            intent_names = [intent.replace("_", " ").title() for intent, _ in top_intents]
            
            return f"I think you're asking about {intent_names[0]} or {intent_names[1]}. Could you clarify which one you'd like help with?"
        
        else:
            # Specific topic needs more info - generate AI response
            clarify_prompt = f"""
The user asked: "{user_query}"
I need more specific information to help them effectively. Please provide a conversational response that:
1. Acknowledges their question
2. Asks for more details in a friendly way
3. Suggests what specific information would be helpful
4. Maintains a supportive, encouraging tone
"""
            return self.ai_client.chat_completion_with_retry(
                ,
                prompt,
                ,
                
            ) or "Could you provide a bit more detail about your situation? That would help me give you better guidance."

    def _update_context_from_query(self, context: ConversationContext, query: str):
        """Extract and update student context from query"""
        
        # Use Gemini to extract structured information
        extraction_prompt = f"""
        Extract student information from this query: "{query}"
        
        Previous context: {json.dumps(context.extracted_context, indent=2)}
        
        Extract and update:
        - Current year (freshman, sophomore, junior, senior)
        - Current semester (fall, spring, summer)
        - GPA (if mentioned)
        - Completed courses (course codes like CS 18000)
        - Current courses
        - Failed courses
        - Target track (Machine Intelligence, Software Engineering)
        - Career goals
        - Graduation timeline goals
        - Specific concerns or problems
        
        Return ONLY a JSON object with extracted information. Use null for unknown values.
        Only include fields that are explicitly mentioned or can be inferred.
        """
        
        try:
            # Use comprehensive system prompt for better context understanding
            system_prompt = get_comprehensive_system_prompt()
            
            response_text = self.gemini_model.chat_completion_with_retry(
                ,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": extraction_prompt}
                ],
                ,
                
            )
            
            extracted = json.loads(response_text)
            
            # Update context with extracted information
            for key, value in extracted.items():
                if value is not None:
                    context.extracted_context[key] = value
                    
        except Exception as e:
            print(f"Context extraction error: {e}")
            # Fallback to pattern-based extraction
            self._fallback_context_extraction(context, query)

    def _fallback_context_extraction(self, context: ConversationContext, query: str):
        """Enhanced pattern-based context extraction as fallback"""
        query_lower = query.lower()
        
        # Extract year information with more variations
        year_patterns = {
            "freshman": ["freshman", "fresh", "first year", "1st year", "new student"],
            "sophomore": ["sophomore", "soph", "second year", "2nd year", "rising sophomore"],
            "junior": ["junior", "third year", "3rd year", "rising junior"],
            "senior": ["senior", "fourth year", "4th year", "rising senior", "final year"]
        }
        
        for year, patterns in year_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                context.extracted_context["current_year"] = year
                break
        
        # Extract semester information
        semester_patterns = {
            "fall": ["fall", "autumn", "fall semester", "fall term"],
            "spring": ["spring", "spring semester", "spring term"],
            "summer": ["summer", "summer semester", "summer term", "summer session"]
        }
        
        for semester, patterns in semester_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                context.extracted_context["current_semester"] = semester
                break
        
        # Extract progress indicators
        if any(phrase in query_lower for phrase in ["ahead of schedule", "taken summer", "accelerated", "early"]):
            context.extracted_context["advanced_progress"] = True
        
        if any(phrase in query_lower for phrase in ["behind", "delayed", "struggling", "failed"]):
            context.extracted_context["delayed_progress"] = True
        
        # Extract course information with failure context
        import re
        
        # Enhanced course patterns to catch more variations
        course_patterns = [
            r"cs\s*(\d{3})",  # CS 180, CS 182, CS 240
            r"cs\s*(\d{5})",  # CS 18000, CS 18200
            r"math?\s*(\d{3})",  # MATH 161, MA 161
            r"ma\s*(\d{5})",  # MA 16100
        ]
        
        completed_courses = context.extracted_context.get("completed_courses", [])
        failed_courses = context.extracted_context.get("failed_courses", [])
        
        # Check for failure context in the query
        failure_indicators = [
            "fail", "failed", "failing", "didn't pass", "didn't think", "don't think", "won't pass",
            "dont think", "wont pass", "might not pass", "probably won't pass", "unlikely to pass",
            "struggling", "having trouble", "not doing well"
        ]
        
        # More sophisticated failure context detection
        is_failure_context = any(indicator in query_lower for indicator in failure_indicators)
        
        # Also check for phrases that indicate potential failure
        failure_phrases = [
            r"don'?t think.*pass", r"won'?t pass", r"might not pass", 
            r"probably.*not.*pass", r"unlikely.*pass", r"not.*pass",
            r"having trouble.*", r"struggling.*", r"not doing well"
        ]
        
        for phrase_pattern in failure_phrases:
            if re.search(phrase_pattern, query_lower):
                is_failure_context = True
                break
        
        # Look for course mentions with enhanced patterns
        extracted_courses = []
        
        # Pattern 1: Standard course patterns
        for pattern in course_patterns:
            matches = re.findall(pattern, query_lower)
            for match in matches:
                normalized = self._normalize_course_code(f"CS{match}" if "cs" in pattern else f"MA{match}")
                if normalized:
                    extracted_courses.append(normalized)
        
        # Pattern 2: Specific course mentions (handle concatenated words like "failedcs182")
        course_mentions = [
            (r"cs\s*180|cs180", "CS 18000"),
            (r"cs\s*182|cs182", "CS 18200"), 
            (r"cs\s*240|cs240", "CS 24000"),
            (r"cs\s*250|cs250", "CS 25000"),
            (r"cs\s*251|cs251", "CS 25100"),
            (r"cs\s*252|cs252", "CS 25200"),
            (r"ma\s*161|ma161", "MA 16100"),
            (r"ma\s*162|ma162", "MA 16200"),
            (r"ma\s*261|ma261", "MA 26100"),
            (r"ma\s*265|ma265", "MA 26500")
        ]
        
        for pattern, course_code in course_mentions:
            if re.search(pattern, query_lower):
                extracted_courses.append(course_code)
        
        # Pattern 3: Handle concatenated failure mentions like "failedcs182"
        concatenated_failures = re.findall(r"fail[a-z]*cs\s*(\d{3})", query_lower)
        for match in concatenated_failures:
            normalized = self._normalize_course_code(f"CS{match}")
            if normalized:
                extracted_courses.append(normalized)
                is_failure_context = True
        
        # Add courses to appropriate lists based on context
        for course in extracted_courses:
            if is_failure_context:
                if course not in failed_courses:
                    failed_courses.append(course)
            else:
                if course not in completed_courses:
                    completed_courses.append(course)
        
        # Special context clues for course status
        if "good score" in query_lower or "did well" in query_lower:
            # If they mention doing well in a course, it's completed
            for course in extracted_courses:
                if course not in completed_courses:
                    completed_courses.append(course)
                # Remove from failed if it was there
                if course in failed_courses:
                    failed_courses.remove(course)
        
        # Remove duplicates and update context
        context.extracted_context["completed_courses"] = list(set(completed_courses))
        context.extracted_context["failed_courses"] = list(set(failed_courses))
        
        # Extract track information (use word boundaries to avoid false matches)
        import re
        if "machine intelligence" in query_lower or "mi track" in query_lower or re.search(r'\bmi\b', query_lower):
            context.extracted_context["target_track"] = "Machine Intelligence"
        elif "software engineering" in query_lower or "se track" in query_lower or re.search(r'\bse\b', query_lower):
            context.extracted_context["target_track"] = "Software Engineering"
        
        # Extract impact on graduation timeline
        if any(phrase in query_lower for phrase in ["impact", "affect", "graduation", "timeline"]):
            context.extracted_context["asking_about_impact"] = True
        
        # Extract course selections for MI track
        if any(choice in query_lower for choice in ["option a", "option b", "option c", "numerical methods", "intro to ai"]):
            selections = context.extracted_context.get("mi_track_selections", {})
            
            # AI course selection
            if "option b" in query_lower and ("47300" in query_lower or "web information" in query_lower):
                selections["ai_course"] = "CS 47300 - Web Information Search and Management"
            elif "option a" in query_lower and ("47100" in query_lower or "intro to ai" in query_lower):
                selections["ai_course"] = "CS 47100 - Introduction to Artificial Intelligence"
            
            # Stats course selection  
            if "option a" in query_lower and ("41600" in query_lower or "probability" in query_lower):
                selections["stats_course"] = "STAT 41600 - Probability"
            elif "option c" in query_lower and "51200" in query_lower:
                selections["stats_course"] = "STAT 51200 - Applied Regression Analysis"
                
            # Elective selections
            if "numerical methods" in query_lower or "31400" in query_lower:
                if "electives" not in selections:
                    selections["electives"] = []
                if "CS 31400 - Numerical Methods" not in selections["electives"]:
                    selections["electives"].append("CS 31400 - Numerical Methods")
            
            if ("intro to ai" in query_lower or "47100" in query_lower) and selections.get("ai_course") != "CS 47100 - Introduction to Artificial Intelligence":
                if "electives" not in selections:
                    selections["electives"] = []
                if "CS 47100 - Introduction to Artificial Intelligence" not in selections["electives"]:
                    selections["electives"].append("CS 47100 - Introduction to Artificial Intelligence")
            
            if selections:
                context.extracted_context["mi_track_selections"] = selections
        
        # Extract graduation timeline
        if "early" in query_lower and "grad" in query_lower:
            context.extracted_context["graduation_timeline"] = "early"

    def _apply_context_boost(self, pattern_intents: Dict[str, float], context: ConversationContext, query: str) -> Dict[str, float]:
        """Apply context-aware boosts to intent confidence"""
        boosted_intents = pattern_intents.copy()
        
        # Boost track-related intents if user has mentioned a track
        target_track = context.extracted_context.get("target_track", "").lower()
        if target_track:
            if "machine intelligence" in target_track and "course_planning" in boosted_intents:
                boosted_intents["course_planning"] += 0.2
            elif "software engineering" in target_track and "course_planning" in boosted_intents:
                boosted_intents["course_planning"] += 0.2
        
        # Boost graduation planning if user has mentioned early graduation
        if context.extracted_context.get("graduation_timeline") == "early":
            if "graduation_planning" in boosted_intents:
                boosted_intents["graduation_planning"] += 0.2
        
        # Boost course planning for sophomores/juniors asking about courses
        current_year = context.extracted_context.get("current_year", "").lower()
        if current_year in ["sophomore", "junior"] and any(word in query.lower() for word in ["course", "class", "take"]):
            if "course_planning" in boosted_intents:
                boosted_intents["course_planning"] += 0.1
        
        return boosted_intents

    def _detect_multi_intent_queries(self, query: str, pattern_intents: Dict[str, float]) -> Dict[str, Any]:
        """Detect and handle multi-intent queries"""
        query_lower = query.lower()
        
        # Common multi-intent patterns
        multi_intent_signals = {
            "graduation_and_courses": ["graduate", "course", "plan"],
            "track_and_courses": ["track", "course", "take"],
            "failure_and_recovery": ["failed", "plan", "recover"],
            "career_and_courses": ["career", "course", "prepare"]
        }
        
        detected_multi = []
        for pattern_name, keywords in multi_intent_signals.items():
            if all(keyword in query_lower for keyword in keywords):
                detected_multi.append(pattern_name)
        
        return {
            "multi_intent_detected": len(detected_multi) > 0,
            "multi_intent_patterns": detected_multi,
            "primary_intent_confidence": max(pattern_intents.values()) if pattern_intents else 0.0
        }

    def _calculate_intent_confidence(self, pattern_intents: Dict[str, float], context_boost: Dict[str, float], multi_intents: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final intent with confidence scoring"""
        
        # Combine pattern and context confidence
        final_intents = {}
        for intent, confidence in pattern_intents.items():
            boosted_confidence = context_boost.get(intent, confidence)
            final_intents[intent] = min(0.95, boosted_confidence)  # Cap at 95%
        
        # Determine primary intent
        if final_intents:
            primary_intent = max(final_intents, key=final_intents.get)
            confidence = final_intents[primary_intent]
        else:
            primary_intent = "general"
            confidence = 0.3  # Low confidence fallback
        
        # Adjust confidence for multi-intent queries
        if multi_intents["multi_intent_detected"]:
            confidence = max(0.6, confidence)  # Boost confidence for complex queries
        
        return {
            "primary_intent": primary_intent,
            "confidence": confidence,
            "all_intents": final_intents,
            "multi_intent_info": multi_intents,
            "requires_clarification": confidence < 0.7,
            "specific_topics": []
        }

    def _analyze_intent(self, query: str, context: ConversationContext) -> Dict[str, Any]:
        """Enhanced multi-layer intent analysis with confidence scoring"""
        
        # Layer 1: Smart greeting detection first
        if self._is_greeting(query):
            return {
                "primary_intent": "greeting",
                "confidence": 0.95,
                "all_intents": {"greeting": 0.95},
                "multi_intent_info": {"multi_intent_detected": False, "multi_intent_patterns": []},
                "requires_clarification": False,
                "specific_topics": []
            }
        
        # Layer 2: Pattern-based intent detection with confidence
        pattern_intents = {}
        for intent, patterns in self.intent_patterns.items():
            confidence = 0.0
            for pattern in patterns:
                if re.search(pattern, query.lower()):
                    confidence = max(confidence, 0.8)  # High confidence for pattern match
                    break
            if confidence > 0:
                pattern_intents[intent] = confidence
        
        # Layer 2: Context-aware intent refinement
        context_boost = self._apply_context_boost(pattern_intents, context, query)
        
        # Layer 3: Multi-intent detection for complex queries
        multi_intents = self._detect_multi_intent_queries(query, pattern_intents)
        
        # Layer 4: Calculate final intent with confidence
        final_analysis = self._calculate_intent_confidence(pattern_intents, context_boost, multi_intents)
        
        # Layer 5: Use Gemini for complex cases with low confidence
        if final_analysis["confidence"] < 0.7 or final_analysis["multi_intent_info"]["multi_intent_detected"]:
            Gemini_analysis = self._Gemini_intent_analysis(query, context, final_analysis)
            # Merge Gemini analysis with pattern-based analysis
            if Gemini_analysis and Gemini_analysis.get("confidence", 0) > final_analysis["confidence"]:
                final_analysis.update(Gemini_analysis)
            else:
                # Enhanced local fallback when Gemini fails
                final_analysis = self._enhanced_local_analysis(query, context, final_analysis)
        
        return final_analysis

    def _Gemini_intent_analysis(self, query: str, context: ConversationContext, pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Use Gemini for complex intent analysis (with fallback)"""
        
        # Skip Gemini if not available
        if not self.Gemini_available or not self.gemini_model:
            return None
        
        intent_prompt = f"""
        Analyze this academic advising query: "{query}"
        
        Context:
        - Student: {json.dumps(context.extracted_context)}
        - Pattern analysis found: {pattern_analysis.get("primary_intent", "none")} (confidence: {pattern_analysis.get("confidence", 0):.2f})
        
        Possible intents: graduation_planning, track_selection, course_planning, 
        failure_recovery, codo_advice, cs_minor_planning, career_guidance, academic_standing
        
        Return JSON:
        {{
            "primary_intent": "intent",
            "confidence": 0.85,
            "requires_clarification": false,
            "specific_topics": ["topics"]
        }}
        """
        
        try:
            # Get comprehensive system prompt for better understanding
            system_prompt = get_comprehensive_system_prompt()
            
            response_text = self.gemini_model.chat_completion_with_retry(
                ,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": intent_prompt}
                ],
                ,
                
            )
            
            return json.loads(response_text)
        except Exception as e:
            print(f"Gemini intent analysis error: {e}")
            return None

    def _enhanced_local_analysis(self, query: str, context: ConversationContext, current_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced local semantic analysis for when Gemini fails"""
        
        query_lower = query.lower()
        
        # Semantic keyword analysis for better intent detection
        semantic_indicators = {
            "course_planning": [
                "course", "courses", "class", "classes", "take", "taking", "schedule", 
                "cs", "math", "computer science", "freshman", "sophomore", "junior", "senior",
                "year", "years", "semester", "plan", "planning", "will be taking",
                "show", "see", "list", "tell me", "what"
            ],
            "graduation_planning": [
                "graduate", "graduation", "timeline", "plan", "early", "delay", 
                "4 year", "four year", "when", "finish", "complete degree"
            ],
            "track_selection": [
                "track", "specialization", "concentration", "machine intelligence", 
                "software engineering", "mi", "se", "choose", "select", "which"
            ],
            "career_guidance": [
                "career", "job", "internship", "industry", "work", "employment",
                "research", "graduate school", "future"
            ]
        }
        
        # Count semantic matches for each intent
        intent_scores = {}
        for intent, keywords in semantic_indicators.items():
            score = 0
            for keyword in keywords:
                if keyword in query_lower:
                    score += 1
            
            # Normalize score based on keyword count
            if score > 0:
                intent_scores[intent] = min(0.9, score / len(keywords) * 3)  # Scale up but cap at 90%
        
        # Special patterns for complex queries
        if any(word in query_lower for word in ["courses", "cs", "math"]) and any(word in query_lower for word in ["freshman", "senior", "year", "years"]):
            intent_scores["course_planning"] = max(intent_scores.get("course_planning", 0), 0.85)
            
        if "machine learning" in query_lower or "ml" in query_lower or "ai" in query_lower:
            if "course" in query_lower or "classes" in query_lower:
                intent_scores["course_planning"] = max(intent_scores.get("course_planning", 0), 0.8)
            else:
                intent_scores["track_selection"] = max(intent_scores.get("track_selection", 0), 0.8)
        
        # Determine best intent
        if intent_scores:
            primary_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[primary_intent]
            
            # Extract specific topics based on detected intent and query content
            specific_topics = []
            if primary_intent == "course_planning":
                if "machine learning" in query_lower or "ml" in query_lower:
                    specific_topics.append("Machine Learning")
                if any(year in query_lower for year in ["freshman", "sophomore", "junior", "senior"]):
                    specific_topics.append("multi-year planning")
                if "cs" in query_lower:
                    specific_topics.append("CS courses")
                if "math" in query_lower:
                    specific_topics.append("Math courses")
            
            return {
                "primary_intent": primary_intent,
                "confidence": confidence,
                "all_intents": intent_scores,
                "multi_intent_info": {"multi_intent_detected": len(intent_scores) > 1, "multi_intent_patterns": [], "primary_intent_confidence": confidence},
                "requires_clarification": confidence < 0.6,
                "specific_topics": specific_topics
            }
        
        # If no strong patterns found, return improved current analysis
        return current_analysis

    def _generate_intelligent_response(self, query: str, context: ConversationContext, intent: Dict[str, Any]) -> str:
        """Generate intelligent, personalized response using all knowledge systems"""
        
        primary_intent = intent["primary_intent"]
        
        self._track_query("INTENT_ROUTING", {
            "primary_intent": primary_intent,
            "available_handlers": [
                "greeting", "graduation_planning", "course_planning", "track_selection", 
                "course_difficulty", "failure_recovery", "codo_advice", "cs_minor_planning",
                "career_guidance", "academic_standing"
            ],
            "routing_decision": f"_handle_{primary_intent}"
        }, f"Routing to {primary_intent} handler")
        
        # Handle greetings specially
        if primary_intent == "greeting":
            self._track_query("GREETING_HANDLER", {"query": query}, "Processing greeting")
            return self._handle_greeting(context)
        
        # Route to appropriate specialized handler
        if primary_intent == "graduation_planning":
            self._track_query("GRADUATION_PLANNING_HANDLER", {"extracted_context": context.extracted_context}, "Processing graduation planning query")
            return self._handle_graduation_planning(query, context, intent)
        elif primary_intent == "track_selection":
            self._track_query("TRACK_SELECTION_HANDLER", {"extracted_context": context.extracted_context}, "Processing track selection query")
            return self._handle_track_selection(query, context, intent)
        elif primary_intent == "course_planning":
            self._track_query("COURSE_PLANNING_HANDLER", {"extracted_context": context.extracted_context}, "Processing course planning query")
            return self._handle_course_planning(query, context, intent)
        elif primary_intent == "course_difficulty":
            self._track_query("COURSE_DIFFICULTY_HANDLER", {"extracted_context": context.extracted_context}, "Processing course difficulty query")
            return self._handle_course_difficulty(query, context, intent)
        elif primary_intent == "failure_recovery":
            self._track_query("FAILURE_RECOVERY_HANDLER", {"extracted_context": context.extracted_context}, "Processing failure recovery query")
            return self._handle_failure_recovery(query, context, intent)
        elif primary_intent == "codo_advice":
            self._track_query("CODO_ADVICE_HANDLER", {"extracted_context": context.extracted_context}, "Processing CODO advice query")
            return self._handle_codo_advice(query, context, intent)
        elif primary_intent == "cs_minor_planning":
            self._track_query("CS_MINOR_PLANNING_HANDLER", {"extracted_context": context.extracted_context}, "Processing CS minor planning query")
            return self._handle_cs_minor_planning(query, context, intent)
        elif primary_intent == "career_guidance":
            self._track_query("CAREER_GUIDANCE_HANDLER", {"extracted_context": context.extracted_context}, "Processing career guidance query")
            return self._handle_career_guidance(query, context, intent)
        else:
            self._track_query("GENERAL_HANDLER", {"primary_intent": primary_intent}, "Processing general/unknown query")
            return self._handle_general_query(query, context, intent)

    def _handle_greeting(self, context: ConversationContext) -> str:
        """Handle greeting messages with AI-generated personalized response"""
        
        extracted = context.extracted_context
        
        # Use AI response generator if available
        if self.ai_response_generator:
            greeting_context = {
                "current_year": extracted.get("current_year"),
                "target_track": extracted.get("target_track"),
                "completed_courses": extracted.get("completed_courses", []),
                "conversation_history": len(context.conversation_history),
                "returning_user": len(context.conversation_history) > 0
            }
            
            return self.ai_response_generator.generate_greeting_response(greeting_context)
        
        # Fallback greeting when AI is not available
        current_year = extracted.get("current_year")
        target_track = extracted.get("target_track")
        completed_courses = extracted.get("completed_courses", [])
        
        if current_year or target_track or completed_courses:
            # Personalized greeting for returning student
            response = f"Hello again! "
            
            if current_year:
                response += f"As a {current_year} "
                
            if target_track:
                response += f"in the {target_track} track, "
                
            if completed_courses:
                response += f"with {len(completed_courses)} courses completed, "
                
            response += "I'm here to help with your CS journey. What would you like to know?"
            
        else:
            # First-time greeting - fallback
            try:
                if self.Gemini_available and self.gemini_model:
                    system_prompt = get_comprehensive_system_prompt()
                    ai_response = self.gemini_model.chat_completion_with_retry(
                        ,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Hello there! This is my first time talking to you. Please give me a friendly greeting and tell me how you can help with Purdue CS."}
                        ],
                        ,
                        
                    )
                    if ai_response and len(ai_response) > 20:
                        return ai_response
            except:
                pass  # Fall back to dynamic response
            
            # Dynamic fallback - not hardcoded
            import random
            greeting_start = random.choice(casual_greetings)
            response = f"{greeting_start} I'm your Purdue CS academic advisor. I can help you with course planning, graduation timelines, track selection, CODO requirements, and pretty much anything CS-related. What's on your mind?"
        
        return response

    def _handle_graduation_planning(self, query: str, context: ConversationContext, intent: Dict[str, Any]) -> str:
        """Handle graduation planning queries with personalized approach"""
        
        extracted = context.extracted_context
        query_lower = query.lower()
        
        # DUAL TRACK DETECTION: Check if user wants both tracks
        dual_track_indicators = [
            "both tracks", "both machine intelligence and software engineering",
            "machine intelligence and software engineering", "mi and se",
            "both mi and se", "dual track", "multiple tracks",
            "machine intelligence track and the software engineering track"
        ]
        
        is_dual_track_request = any(indicator in query_lower for indicator in dual_track_indicators)
        
        if is_dual_track_request:
            # Handle dual track planning
            return self._handle_dual_track_planning(query, context, intent)
        
        # Use personalized planner if available
        if self.personalized_planner:
            return self._handle_personalized_graduation_planning(query, context, intent)
        
        # Fallback to original logic if personalized planner not available
        return self._handle_basic_graduation_planning(query, context, intent)

    def _handle_personalized_graduation_planning(self, query: str, context: ConversationContext, intent: Dict[str, Any]) -> str:
        """Handle graduation planning with full personalization and interactivity"""
        
        extracted = context.extracted_context
        query_lower = query.lower()
        
        # Build student profile from extracted context
        student_profile = self._build_student_profile_from_context(extracted, query_lower)
        
        # Check if user is responding to course choices
        if hasattr(context, 'awaiting_course_choices') and context.awaiting_course_choices:
            return self._handle_course_selection_response(query, context, student_profile)
        
        # Check if we have enough information to generate a plan
        missing_info = self._identify_missing_info(student_profile)
        
        if missing_info:
            # Use AI to generate clarifying questions
            if self.ai_response_generator:
                questions = self.personalized_planner.ask_clarifying_questions(student_profile)
                return self.ai_response_generator.generate_followup_response(
                    query, extracted, questions[:3]
                )
            else:
                # Fallback to basic questions
                return self._generate_basic_clarifying_questions(student_profile, missing_info)
        
        # Generate personalized plan
        try:
            plan = self.personalized_planner.create_personalized_plan(student_profile)
            
            # Check if plan requires course choices
            if hasattr(plan, 'choice_request') and plan.choice_request:
                # Mark context as awaiting choices
                context.awaiting_course_choices = True
                context.pending_choices = plan.choice_request
                context.student_profile = student_profile
                
                # Generate interactive choice request
                if self.ai_response_generator:
                    return self.ai_response_generator.generate_course_choice_request(
                        plan.choice_request, student_profile
                    )
                else:
                    return self._format_course_choices_fallback(plan.choice_request, student_profile)
            
            # Format complete plan
            return self._format_personalized_plan(plan, query_lower)
            
        except Exception as e:
            self.logger.error(f"Error generating personalized plan: {e}")
            if self.ai_response_generator:
                return self.ai_response_generator.generate_error_response(
                    "graduation plan generation", 
                    ["Tell me your current year and completed courses", "Ask about specific course requirements"]
                )
            else:
                # Generate AI response for plan creation error
                error_prompt = "Generate a helpful response when graduation plan creation fails. Ask for current year and completed courses in a friendly way."
                try:
                    return self.smart_ai_engine.generate_smart_response(error_prompt, {"error_type": "plan_creation_failed"})
                except:
                    # Use basic AI for emergency fallback instead of hardcoded text
                    try:
                        from simple_boiler_ai import SimpleBoilerAI
                        emergency_ai = SimpleBoilerAI()
                        return emergency_ai.get_ai_response("I had trouble creating your graduation plan. Ask the student for their current year and completed courses to help them better.")
                    except:
                        return ""  # Return empty instead of hardcoded text

    def _handle_course_selection_response(self, query: str, context: ConversationContext, student_profile: Dict) -> str:
        """Handle user's response to course selection choices"""
        
        if not hasattr(context, 'pending_choices') or not context.pending_choices:
            # Generate AI response for no pending choices
            prompt = "Generate a helpful response when there are no pending course choices to process. Offer to help with graduation planning."
            try:
                return self.smart_ai_engine.generate_smart_response(prompt, {"context": "no_pending_choices"})
            except:
                return self._get_emergency_ai_response("I don't have pending course choices to process. Offer to help with graduation planning.")
        
        # Parse user selections
        try:
            selected_choices = self.personalized_planner.parse_user_course_selections(
                query, context.pending_choices
            )
            
            if not selected_choices:
                # User didn't make clear selections
                if self.ai_response_generator:
                    return self.ai_response_generator.generate_followup_response(
                        query, context.extracted_context,
                        ["Please specify which courses you prefer from the options I provided"]
                    )
                else:
                    # Generate AI response for unclear course preferences
                    unclear_prompt = f"Generate a helpful response when unable to understand course preferences from user input: '{query}'. Ask for clarification about specific course choices."
                    try:
                        return self.smart_ai_engine.generate_smart_response(unclear_prompt, {"query": query, "context": "unclear_preferences"})
                    except:
                        return self._get_emergency_ai_response("I couldn't understand your course preferences. Ask which specific courses they'd like to choose from the provided options.")
            
            # Generate final personalized plan with selections
            final_plan = self.personalized_planner.create_personalized_plan(
                student_profile, selected_choices
            )
            
            # Clear awaiting choices state
            context.awaiting_course_choices = False
            context.pending_choices = None
            
            # Generate AI response about their plan
            if self.ai_response_generator:
                plan_summary = self._create_plan_summary(final_plan, selected_choices)
                return self.ai_response_generator.generate_graduation_planning_response(
                    student_profile, "personalized_with_choices"
                ) + "\n\n" + plan_summary
            else:
                return self._format_personalized_plan(final_plan, query.lower())
                
        except Exception as e:
            self.logger.error(f"Error processing course selections: {e}")
            # Clear state and ask for clarification
            context.awaiting_course_choices = False
            if self.ai_response_generator:
                return self.ai_response_generator.generate_error_response(
                    "course selection processing",
                    ["Let me present the course options again", "Start over with graduation planning"]
                )
            else:
                # Generate AI response for course selection processing error
                error_prompt = "Generate a helpful response when course selection processing fails. Offer to present options again or restart graduation planning."
                try:
                    return self.smart_ai_engine.generate_smart_response(error_prompt, {"error_type": "course_selection_processing_failed"})
                except:
                    return self._get_emergency_ai_response("I had trouble processing your course selections. Ask if they'd like me to present the options again.")

    def _build_student_profile_from_context(self, extracted: Dict, query_lower: str) -> Dict:
        """Build student profile from conversation context"""
        
        # Determine major
        major = "Computer Science"  # Default
        if "data science" in query_lower:
            major = "Data Science"
        
        # Extract graduation goal from query
        graduation_goal = "4_year"  # Default
        if any(term in query_lower for term in ["3 year", "three year", "graduate early", "fastest"]):
            graduation_goal = "3_year"
        elif any(term in query_lower for term in ["3.5 year", "three and half", "7 semester"]):
            graduation_goal = "3.5_year"
        elif "flexible" in query_lower:
            graduation_goal = "flexible"
        
        # Extract credit load preference
        credit_load = "standard"
        if any(term in query_lower for term in ["light load", "easy", "manageable", "12-15 credit"]):
            credit_load = "light"
        elif any(term in query_lower for term in ["heavy load", "maximum", "18+ credit", "intensive"]):
            credit_load = "heavy"
        
        # Extract summer course availability
        summer_courses = True  # Default assume available
        if any(term in query_lower for term in ["no summer", "skip summer", "summer not available"]):
            summer_courses = False
        elif any(term in query_lower for term in ["summer course", "summer available", "accelerate"]):
            summer_courses = True
        
        # Map current year from different formats
        current_year_mapping = {
            "freshman": 1, "fresh": 1, "first year": 1, "1st year": 1,
            "sophomore": 2, "soph": 2, "second year": 2, "2nd year": 2,
            "junior": 3, "third year": 3, "3rd year": 3,
            "senior": 4, "fourth year": 4, "4th year": 4
        }
        
        current_year_str = extracted.get("current_year", "freshman").lower()
        current_year = current_year_mapping.get(current_year_str, 1)
        
        # Determine current semester
        current_semester = "Fall"  # Default
        if any(term in query_lower for term in ["spring semester", "spring term", "this spring"]):
            current_semester = "Spring"
        elif any(term in query_lower for term in ["summer semester", "summer term", "this summer"]):
            current_semester = "Summer"
        
        profile = {
            "major": major,
            "track": extracted.get("target_track", "Machine Intelligence"),
            "completed_courses": extracted.get("completed_courses", []),
            "current_year": current_year,
            "current_semester": current_semester,
            "graduation_goal": graduation_goal,
            "credit_load": credit_load,
            "summer_courses": summer_courses
        }
        
        return profile

    def _identify_missing_info(self, student_profile: Dict) -> List[str]:
        """Identify what information is missing for personalized planning"""
        missing = []
        
        if not student_profile.get("completed_courses"):
            missing.append("completed_courses")
        
        if not student_profile.get("track") and student_profile.get("major") == "Computer Science":
            missing.append("track")
        
        if not student_profile.get("current_year"):
            missing.append("current_year")
        
        return missing

    def _format_personalized_plan(self, plan: 'PersonalizedGraduationPlan', query_lower: str) -> str:
        """Format the personalized graduation plan for display"""
        
        response = f"Here's your personalized {plan.major}"
        if plan.track and plan.major == "Computer Science":
            response += f" ({plan.track} track)"
        response += " graduation plan!\n\n"
        
        # Add customization summary
        if plan.customization_notes:
            response += "**Customized For You:**\n"
            for note in plan.customization_notes[:3]:  # Show top 3 customizations
                response += f"• {note}\n"
            response += "\n"
        
        # Add graduation timeline
        response += f"**Graduation Timeline:** {plan.graduation_date} ({plan.total_semesters} semesters)\n"
        response += f"**Success Probability:** {plan.success_probability:.0%}\n\n"
        
        # Show semester-by-semester plan
        response += "**Your Semester-by-Semester Plan:**\n\n"
        
        for schedule in plan.schedules:
            response += f"**{schedule.semester} Year {schedule.year}** ({schedule.total_credits} credits):\n"
            
            for course in schedule.courses:
                course_code = course.get("code", "")
                course_title = course.get("title", course_code)
                credits = course.get("credits", 3)
                
                # Show course with credits
                if course_title != course_code:
                    response += f"• {course_code}: {course_title} ({credits} cr)\n"
                else:
                    response += f"• {course_code} ({credits} cr)\n"
            
            # Add warnings if any
            if schedule.warnings:
                response += "\n  ⚠️ Considerations:\n"
                for warning in schedule.warnings[:2]:  # Limit warnings
                    response += f"    • {warning}\n"
            
            # Add recommendations if any
            if schedule.recommendations:
                response += "\n  💡 Tips:\n"
                for rec in schedule.recommendations[:2]:  # Limit recommendations
                    response += f"    • {rec}\n"
            
            response += "\n"
        
        # Add overall warnings and recommendations
        if plan.warnings:
            response += "**Important Considerations:**\n"
            for warning in plan.warnings[:3]:
                response += f"⚠️ {warning}\n"
            response += "\n"
        
        if plan.recommendations:
            response += "**Recommendations:**\n"
            for rec in plan.recommendations[:3]:
                response += f"💡 {rec}\n"
            response += "\n"
        
        # Add interactive follow-up
        response += "This plan is tailored specifically to your situation! If you'd like me to:\n"
        response += "• Adjust the timeline or course load\n"
        response += "• Explain any specific course or semester\n"
        response += "• Show alternative options\n"
        response += "• Plan for specific scenarios (like course failures)\n\n"
        response += "Just let me know what you'd like to explore further!"
        
        return response

    def _generate_basic_clarifying_questions(self, student_profile: Dict, missing_info: List[str]) -> str:
        """Generate basic clarifying questions when AI is not available"""
        questions = []
        
        if "completed_courses" in missing_info:
            questions.append("What CS and math courses have you completed so far?")
        
        if "track" in missing_info and student_profile.get("major") == "Computer Science":
            questions.append("Which CS track interests you - Machine Intelligence or Software Engineering?")
        
        if "current_year" in missing_info:
            questions.append("What's your current academic year (freshman, sophomore, junior, senior)?")
        
        response = "I'd love to help create your personalized graduation plan! I need a few details:\n\n"
        for i, question in enumerate(questions[:3], 1):
            response += f"{i}. {question}\n"
        
        response += "\nOnce I have this information, I can create a detailed plan just for you!"
        return response
    
    def _format_course_choices_fallback(self, choice_request: Dict, student_profile: Dict) -> str:
        """Format course choices when AI generator is not available"""
        major = student_profile.get('major', 'Computer Science')
        track = student_profile.get('track', '')
        
        response = f"I need your help to complete your {major}"
        if track:
            response += f" ({track} track)"
        response += " graduation plan! You have some course options to choose from:\n\n"
        
        for choice_key, choice_info in choice_request.items():
            response += f"**{choice_info['category']}** ({choice_info['requirement_type']}):\n"
            
            for option in choice_info['options']:
                response += f"• {option['code']}: {option['title']}\n"
                response += f"  {option['description']}\n"
                if 'best_for' in option:
                    response += f"  Best for: {', '.join(option['best_for'])}\n"
            response += "\n"
        
        response += "Please let me know your preferences, and I'll create your complete personalized plan!"
        return response
    
    def _create_plan_summary(self, plan, selected_choices: Dict) -> str:
        """Create a summary of the final plan with user's choices"""
        summary_parts = []
        
        summary_parts.append(f"Perfect! Here's your personalized {plan.major} graduation plan:")
        
        if selected_choices:
            summary_parts.append("\nYour Course Selections:")
            for choice_key, courses in selected_choices.items():
                if isinstance(courses, list):
                    summary_parts.append(f"• {', '.join(courses)}")
        
        summary_parts.append(f"\nGraduation Timeline: {plan.graduation_date}")
        summary_parts.append(f"Success Probability: {plan.success_probability:.0%}")
        
        if plan.schedules:
            summary_parts.append(f"\nNext Steps: Begin with {plan.schedules[0].semester} Year {plan.schedules[0].year}")
        
        return "\n".join(summary_parts)

    def _handle_dual_track_planning(self, query: str, context: ConversationContext, intent: Dict[str, Any]) -> str:
        """Handle dual track graduation planning"""
        
        extracted = context.extracted_context
        query_lower = query.lower()
        
        self._track_query("DUAL_TRACK_DETECTED", {
            "query": query_lower,
            "extracted_context": extracted
        }, "Dual track graduation planning request detected")
        
        # Try to use dual track planner if available
        try:
            from dual_track_planner import DualTrackGraduationPlanner
            planner = DualTrackGraduationPlanner()
            
            # Determine if early graduation is requested
            early_graduation = any(word in query_lower for word in ["fastest", "early", "accelerate", "quick", "3.5", "3.5 year"])
            
            # Get student year from context
            student_year = extracted.get("current_year", extracted.get("Current year", "freshman"))
            
            # Generate dual track plan
            plan = planner.generate_dual_track_plan(student_year, early_graduation)
            
            return planner.format_plan_for_display(plan)
            
        except ImportError:
            # Fallback response for dual track
            response = "Excellent question! You can actually complete both Machine Intelligence and Software Engineering tracks simultaneously. This is called a dual track completion and it's definitely possible with proper planning.\n\n"
            response += "Here's what you need to know about dual track completion:\n\n"
            response += "**Requirements for Both Tracks:**\n"
            response += "• Machine Intelligence: CS 37300, CS 38100, CS 47100/47300, STAT 41600/MA 41600/STAT 51200, + 2 electives\n"
            response += "• Software Engineering: CS 30700, CS 38100, CS 40700, CS 40800, CS 35200/35400, + 1 elective\n"
            response += "• Shared course: CS 38100 counts for both tracks\n\n"
            response += "**Total Additional Courses:** About 8-9 extra courses beyond the shared requirements\n\n"
            response += "**Timeline:** Typically requires 4.5-5 years with standard course loads, or 4 years with heavy loads and summer courses\n\n"
            response += "Would you like me to create a detailed semester-by-semester plan for dual track completion? I'll need to know your current progress and timeline preferences."
            return response

    def _handle_basic_graduation_planning(self, query: str, context: ConversationContext, intent: Dict[str, Any]) -> str:
        """Basic graduation planning fallback"""
        
        extracted = context.extracted_context
        query_lower = query.lower()
        
        # Check if this is an early graduation request
        if "early" in query_lower or "accelerate" in query_lower:
            # Check if we already have their track preference
            target_track = extracted.get("target_track")
            
            if not target_track:
                # Ask about track preference first
                response = "Great! I'd love to help you plan early graduation. First, let me understand your track preference.\n\n"
                response += "Are you planning for Machine Intelligence or Software Engineering track? This will affect your course planning significantly.\n\n"
                response += "Also, what's your current year and have you completed any CS courses yet?"
                return response
        
        # Standard graduation planning
        response = "I can help you create a graduation plan! Let me understand your situation better.\n\n"
        response += "What's your current year, which track are you interested in (Machine Intelligence or Software Engineering), and are you looking for early graduation or standard timeline?\n\n"
        response += "Also, have you completed any CS courses already?"
        
        return response

    def _handle_track_selection(self, query: str, context: ConversationContext, intent: Dict[str, Any]) -> str:
        """Handle track selection queries"""
        
        extracted = context.extracted_context
        query_lower = query.lower()
        
        # DUAL TRACK DETECTION: Check if user wants both tracks
        dual_track_indicators = [
            "both tracks", "both machine intelligence and software engineering",
            "machine intelligence and software engineering", "mi and se",
            "both mi and se", "dual track", "multiple tracks",
            "machine intelligence track and the software engineering track"
        ]
        
        is_dual_track_request = any(indicator in query_lower for indicator in dual_track_indicators)
        
        if is_dual_track_request:
            self._track_query("DUAL_TRACK_SELECTION_DETECTED", {
                "query": query_lower,
                "indicators_matched": [ind for ind in dual_track_indicators if ind in query_lower],
                "extracted_context": extracted
            }, "Dual track selection request detected")
            
            response = "Excellent question! You can actually complete both Machine Intelligence and Software Engineering tracks simultaneously. This is called a dual track completion and it's definitely possible with proper planning.\n\n"
            response += "Here's what you need to know about dual track completion:\n\n"
            response += "🎯 **Requirements for Both Tracks:**\n"
            response += "• Machine Intelligence: CS 37300, CS 38100, CS 47100/47300, STAT 41600/MA 41600/STAT 51200, + 2 electives\n"
            response += "• Software Engineering: CS 30700, CS 38100, CS 40700, CS 40800, CS 35200/35400, + 1 elective\n"
            response += "• Shared course: CS 38100 counts for both tracks\n\n"
            response += "⏰ **Timeline Options:**\n"
            response += "• Standard 4-year plan: 75% success probability\n"
            response += "• Accelerated 3.5-year plan: 45% success probability (very challenging)\n\n"
            response += "⚠️ **Important Considerations:**\n"
            response += "• Requires advisor approval\n"
            response += "• Heavy course loads (18+ credits per semester)\n"
            response += "• Summer courses may be necessary\n"
            response += "• Limited flexibility for course failures\n\n"
            response += "Would you like me to create a detailed dual track graduation plan showing exactly which courses to take each semester?"
            
            return response
        
        # Get track guidance for single track selection
        mi_guidance = self.academic_advisor.get_track_specific_guidance("Machine Intelligence", "junior")
        se_guidance = self.academic_advisor.get_track_specific_guidance("Software Engineering", "junior")
        
        response = "Let me help you understand both CS tracks.\n\n"
        
        # Machine Intelligence Track
        response += f"Machine Intelligence Track focuses on {mi_guidance['core_focus'].lower()}. "
        response += f"Your key courses would be {', '.join(mi_guidance['key_courses'])}, and you'd primarily work with {', '.join(mi_guidance['programming_languages'])}. "
        response += f"For career preparation, {mi_guidance['career_preparation']['internships'].lower()}.\n\n"
        
        # Software Engineering Track  
        response += f"Software Engineering Track centers on {se_guidance['core_focus'].lower()}. "
        response += f"You'd take courses like {', '.join(se_guidance['key_courses'])}, working mainly with {', '.join(se_guidance['programming_languages'])}. "
        response += f"Career-wise, {se_guidance['career_preparation']['internships'].lower()}.\n\n"
        
        # Personalized recommendation based on context
        career_goal = extracted.get("career_goal", "").lower()
        if "ai" in career_goal or "machine learning" in career_goal or "data" in career_goal:
            response += "Based on your interest in AI and machine learning, the Machine Intelligence track would align perfectly with your goals."
        elif "software" in career_goal or "development" in career_goal or "engineering" in career_goal:
            response += "Given your interest in software development, the Software Engineering track would be an excellent fit for your career aspirations."
        else:
            response += "Both tracks offer excellent career opportunities. I'd suggest considering whether you prefer theoretical research or applied development work to help decide."
        
        return response

    def _handle_course_planning(self, query: str, context: ConversationContext, intent: Dict[str, Any]) -> str:
        """Handle course planning and scheduling queries"""
        
        extracted = context.extracted_context
        completed = extracted.get("completed_courses", [])
        # FIXED: Use extracted context year first, then default to sophomore
        current_year = extracted.get("current_year") or extracted.get("Current year", "sophomore")
        target_track = extracted.get("target_track", "")
        
        # SMART MULTI-YEAR DETECTION: Check if this is a multi-year planning request
        query_lower = query.lower()
        multi_year_indicators = [
            "from freshman to senior", "from freshman year to senior", "freshman to senior",
            "4 year plan", "four year plan", "all years", "entire degree",
            "courses i will be taking", "courses i will take", "years after",
            "sophomore to senior", "after freshman", "each year", "per year",
            "year by year", "complete plan", "all courses", "entire program"
        ]
        
        is_multi_year = any(indicator in query_lower for indicator in multi_year_indicators)
        
        # Additional smart detection: CS + Math + multiple years mentioned
        if (("cs" in query_lower or "computer science" in query_lower) and 
            ("math" in query_lower) and 
            any(year in query_lower for year in ["freshman", "sophomore", "junior", "senior", "years"])):
            is_multi_year = True
        
        if is_multi_year:
            self._track_query("MULTI_YEAR_PLANNING_DETECTED", {
                "query": query_lower,
                "current_year": current_year,
                "target_track": target_track,
                "indicators_matched": [ind for ind in multi_year_indicators if ind in query_lower]
            }, "Multi-year course planning request detected")
            return self._handle_multi_year_course_planning(query, context, intent)
        
        # Check if this is a year-level specific course planning query
        query_lower = query.lower()
        year_indicators = {
            "freshman": ["freshman", "first year", "frehman"],  # Include common typo
            "sophomore": ["sophomore", "second year"],
            "junior": ["junior", "third year"],
            "senior": ["senior", "fourth year"]
        }
        
        detected_year = None
        
        # Method 1: Check query text for year indicators
        for year, indicators in year_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                if any(word in query_lower for word in ["compulsory", "required", "should take", "courses", "start", "begin", "take", "classes"]):
                    detected_year = year
                    break
        
        # Method 2: Check extracted context for year level (FIXED - use context when available for course planning)
        if not detected_year:
            context_year = extracted.get("Current year", extracted.get("current_year", "")).lower()
            if context_year in year_indicators.keys():
                # For course planning queries, always use context year when available
                if any(word in query_lower for word in ["compulsory", "required", "should take", "courses", "start", "begin", "take", "classes", "this year", "semester", "plan", "schedule", "what should", "which"]):
                    detected_year = context_year
                    self._track_query("YEAR_LEVEL_FROM_CONTEXT", {
                        "detected_year": detected_year,
                        "source": "extracted_context",
                        "context_year": context_year,
                        "query": query_lower,
                        "fix_applied": "context_year_detection_improved"
                    }, f"Year-level detected from context: {detected_year} (FIXED BUG)")
        
        # Method 3: Final safety net - use context year for any course planning query (NEVER FAIL AGAIN!)
        if not detected_year:
            context_year = extracted.get("Current year", extracted.get("current_year", "")).lower()
            if context_year in year_indicators.keys():
                # If this looks like a course planning query at all, use the context year
                if any(word in query_lower for word in ["course", "class", "take", "should", "what", "which", "how", "when", "help"]):
                    detected_year = context_year
                    self._track_query("YEAR_LEVEL_SAFETY_NET", {
                        "detected_year": detected_year,
                        "source": "extracted_context_fallback",
                        "context_year": context_year,
                        "query": query_lower,
                        "fix_applied": "never_ignore_context_year_again"
                    }, f"Year-level safety net triggered: using {detected_year} from context")
        
        if detected_year:
            self._track_query("YEAR_LEVEL_DETECTED", {
                "detected_year": detected_year,
                "query": query_lower,
                "detection_method": "query_pattern" if detected_year in query_lower else "context_extraction"
            }, f"Year-level course planning detected: {detected_year}")
            return self._handle_year_level_course_planning(query, context, intent, detected_year)
        
        # Check if this is a track-specific query (use word boundaries to avoid false matches)
        import re
        mi_match = "machine intelligence" in query.lower() or re.search(r'\bmi\b', query.lower())
        se_match = "software engineering" in query.lower() or re.search(r'\bse\b', query.lower())
        
        if mi_match:
            self._track_query("TRACK_ROUTING", {
                "detected_track": "Machine Intelligence",
                "query": query.lower(),
                "mi_pattern_match": mi_match,
                "se_pattern_match": se_match
            }, "Routing to Machine Intelligence track handler")
            return self._handle_mi_track_courses(query, context, intent)
        elif se_match:
            self._track_query("TRACK_ROUTING", {
                "detected_track": "Software Engineering", 
                "query": query.lower(),
                "mi_pattern_match": mi_match,
                "se_pattern_match": se_match
            }, "Routing to Software Engineering track handler")
            return self._handle_se_track_courses(query, context, intent)
        
        # Get available courses based on prerequisites  
        self._track_query("KNOWLEDGE_GRAPH_ACCESS", {
            "data_accessed": "course catalog and prerequisites",
            "courses_checked": len(self.knowledge_base.get("courses", {})),
            "prerequisites_analyzed": len(self.knowledge_base.get("prerequisites", {})),
            "student_completed": completed
        }, "Analyzing available courses from knowledge base")
        
        available_courses = []
        for course_code, course_data in self.knowledge_base["courses"].items():
            prereqs = self.knowledge_base["prerequisites"].get(course_code, [])
            if all(prereq in completed for prereq in prereqs):
                available_courses.append((course_code, course_data))
        
        response = f"Let me help with your course planning as a {current_year}.\n\n"
        
        if completed:
            response += f"I see you've completed {', '.join(completed)}. "
        
        # Check if junior/senior needs track declaration
        if current_year in ["junior", "senior"] and not target_track:
            response += "🚨 IMPORTANT: As a " + current_year + ", you need to declare your track specialization!\n\n"
            response += "Ask me about:\n"
            response += "• \"Tell me about Machine Intelligence track\"\n"
            response += "• \"Tell me about Software Engineering track\"\n"
            response += "• \"Help me choose between MI and SE tracks\"\n\n"
            response += "Once you declare your track, I can give you specific course recommendations for your specialization.\n\n"
        elif current_year in ["junior", "senior"] and target_track:
            track_name = "Machine Intelligence" if "machine intelligence" in target_track.lower() or "mi" in target_track.lower() else "Software Engineering"
            response += f"I see you're in the {track_name} track. Let me give you track-specific course recommendations.\n\n"
        
        # Get course load guidelines
        load_guidelines = self.knowledge_base.get("course_load_guidelines", {}).get(current_year.lower(), {})
        if load_guidelines:
            max_total = load_guidelines.get('total_credits_max', 18)
            max_cs = load_guidelines.get('cs_courses_max', 3)
            rec_cs = load_guidelines.get('cs_courses_recommended', 2)
            response += f"For course load planning, you can take up to {max_total} total credits with a maximum of {max_cs} CS courses per semester. I'd recommend {rec_cs} CS courses for optimal balance.\n\n"
        
        # Filter available courses by type
        foundation_courses = [(c, d) for c, d in available_courses if d.get("course_type") == "foundation"]
        
        # Filter track courses based on student's declared track (TRACK-SPECIFIC FILTERING)
        if target_track:
            if "machine intelligence" in target_track.lower() or "mi" in target_track.lower():
                track_courses = [(c, d) for c, d in available_courses if d.get("course_type") == "track_mi"]
                track_name = "Machine Intelligence"
            elif "software engineering" in target_track.lower() or "se" in target_track.lower():
                track_courses = [(c, d) for c, d in available_courses if d.get("course_type") == "track_se"]
                track_name = "Software Engineering"
            else:
                track_courses = [(c, d) for c, d in available_courses if "track" in d.get("course_type", "")]
                track_name = "your track"
        else:
            track_courses = []
        
        if foundation_courses:
            response += "Available foundation courses you can take:\n"
            for course_code, course_data in foundation_courses[:5]:
                response += f"{course_code}: {course_data['title']} ({course_data['credits']} credits)\n"
            response += "\n"
        
        if track_courses and target_track:
            response += f"{track_name} track courses available to you:\n"
            for course_code, course_data in track_courses[:5]:
                response += f"{course_code}: {course_data['title']} ({course_data['credits']} credits)\n"
            response += "\n"
        elif not target_track and current_year in ["junior", "senior"]:
            response += "Declare your track to see track-specific course recommendations!\n\n"
        
        # Add semester-specific recommendations
        current_semester = extracted.get("current_semester", "fall")
        if current_semester.lower() == "fall":
            response += "Since this is fall semester, you can typically handle heavier course loads and it's a good time for challenging CS courses."
        else:
            response += "For spring semester, consider balancing your schedule for internship preparation and include some lighter electives."
        
        return response

    def _handle_mi_track_courses(self, query: str, context: ConversationContext, intent: Dict[str, Any]) -> str:
        """Handle Machine Intelligence track specific course queries with interactive selection"""
        
        extracted = context.extracted_context
        
        # Check if user is making course selections
        if any(choice in query.lower() for choice in ["option a", "option b", "option c", "numerical methods", "intro to ai", "47100", "47300", "31400", "41600"]):
            return self._process_mi_course_selection(query, context)
        
        # Present course options for selection
        response = "Perfect! Yes, you need to choose your Machine Intelligence track courses. Let me present your options and we'll build your plan together.\n\n"
        response += "For Machine Intelligence track, you need to make these selections:\n\n"
        
        response += "REQUIRED COURSES (Must take both):\n"
        response += "• CS 37300 - Data Mining and Machine Learning\n"
        response += "• CS 38100 - Introduction to Analysis of Algorithms\n\n"
        
        response += "AI COURSE (Choose 1):\n"
        response += "Option A: CS 47100 - Introduction to Artificial Intelligence\n"
        response += "  - More theoretical approach, covers search algorithms, knowledge representation\n"
        response += "  - Best for: Graduate school preparation, research focus\n\n"
        response += "Option B: CS 47300 - Web Information Search and Management\n"
        response += "  - More applied approach, covers search engines, web data processing\n"
        response += "  - Best for: Industry positions, practical applications\n\n"
        
        response += "STATISTICS COURSE (Choose 1):\n"
        response += "Option A: STAT 41600 - Probability\n"
        response += "  - Core probability theory, mathematical foundations\n\n"
        response += "Option B: MA 41600 - Probability\n"
        response += "  - Same content as STAT 41600, taught by math department\n\n"
        response += "Option C: STAT 51200 - Applied Regression Analysis\n"
        response += "  - More applied statistics, useful for data science\n\n"
        
        response += "TRACK ELECTIVES (Choose 2):\n"
        response += "• CS 31100 and CS 41100 - Competitive Programming 2 and 3 (counts as 1 elective together)\n"
        response += "• CS 31400 - Numerical Methods\n"
        response += "• CS 34800 - Information Systems\n"
        response += "• CS 35200 - Compilers Principles and Practice\n"
        response += "• CS 44800 - Introduction to Relational Database Systems\n"
        response += "• CS 45600 - Programming Languages\n"
        response += "• CS 45800 - Introduction to Robotics\n"
        response += "• CS 47100 - Introduction to Artificial Intelligence (if not chosen above)\n"
        response += "• CS 47300 - Web Information Search and Management (if not chosen above)\n"
        response += "• CS 48300 - Introduction to Theory of Computation\n"
        response += "• CS 43900 - Introduction to Data Visualization\n"
        response += "• CS 44000 - Large-Scale Data Analytics\n"
        response += "• CS 47500 - Human-Computer Interactions\n"
        response += "• CS 57700 - Natural Language Processing\n"
        response += "• CS 57800 - Statistical Machine Learning\n\n"
        
        response += "What are your career interests? Are you more interested in research/graduate school or industry work? This will help me recommend the best choices for you."
        
        return response
    
    def _process_mi_course_selection(self, query: str, context: ConversationContext) -> str:
        """Process user's MI track course selections and generate personalized plan"""
        
        # Parse selections from query
        selections = {
            "ai_course": "",
            "stats_course": "", 
            "electives": []
        }
        
        # AI course selection
        if "option b" in query.lower() or "47300" in query or "web information" in query.lower():
            selections["ai_course"] = "CS 47300 - Web Information Search and Management"
        elif "option a" in query.lower() or "47100" in query or "intro to ai" in query.lower():
            selections["ai_course"] = "CS 47100 - Introduction to Artificial Intelligence"
        
        # Stats course selection  
        if "option a" in query.lower() or "41600" in query or "stat 41600" in query.lower():
            selections["stats_course"] = "STAT 41600 - Probability"
        elif "option b" in query.lower() or "ma 41600" in query.lower():
            selections["stats_course"] = "MA 41600 - Probability"
        elif "option c" in query.lower() or "51200" in query:
            selections["stats_course"] = "STAT 51200 - Applied Regression Analysis"
            
        # Elective selections
        if "numerical methods" in query.lower() or "31400" in query:
            selections["electives"].append("CS 31400 - Numerical Methods")
        if "intro to ai" in query.lower() and selections["ai_course"] != "CS 47100 - Introduction to Artificial Intelligence":
            selections["electives"].append("CS 47100 - Introduction to Artificial Intelligence")
        
        # Generate response with selections and full plan
        response = "Excellent choices! Here's your Machine Intelligence track selection:\n\n"
        
        response += "YOUR MI TRACK COURSES:\n"
        response += "• CS 37300 - Data Mining and Machine Learning (required)\n"
        response += "• CS 38100 - Introduction to Analysis of Algorithms (required)\n"
        if selections["ai_course"]:
            response += f"• {selections['ai_course']} (AI choice)\n"
        if selections["stats_course"]:
            response += f"• {selections['stats_course']} (statistics choice)\n"
        for elective in selections["electives"]:
            response += f"• {elective} (elective)\n"
        
        response += "\nNow let me create your complete early graduation plan from freshman year:\n\n"
        response += self._generate_early_graduation_plan(selections)
        
        # Save selections to context
        context.extracted_context["mi_track_selections"] = selections
        context.extracted_context["target_track"] = "Machine Intelligence"
        
        return response
    
    def _generate_early_graduation_plan(self, track_selections: dict) -> str:
        """Generate detailed early graduation plan"""
        
        plan = "EARLY GRADUATION PLAN (7 semesters - Spring of Year 4):\n\n"
        
        plan += "FRESHMAN YEAR:\n"
        plan += "Fall Year 1 (16 credits):\n"
        plan += "• CS 18000 - Problem Solving and Object-Oriented Programming (4 cr)\n"
        plan += "• MA 16100 - Plane Analytic Geometry and Calculus I (5 cr)\n"
        plan += "• ENGL 10600 - First-Year Composition (4 cr)\n"
        plan += "• General Education course (3 cr)\n\n"
        
        plan += "Spring Year 1 (17 credits):\n"
        plan += "• CS 18200 - Foundations of Computer Science (4 cr)\n"
        plan += "• CS 24000 - Programming in C (3 cr)\n"
        plan += "• MA 16200 - Plane Analytic Geometry and Calculus II (5 cr)\n"
        plan += "• PHYS 17200 - Modern Mechanics (4 cr)\n"
        plan += "• Free elective (1 cr)\n\n"
        
        plan += "Summer Year 1 (7 credits):\n"
        plan += "• CS 25000 - Computer Architecture (4 cr)\n"
        plan += "• CS 25100 - Data Structures and Algorithms (3 cr)\n\n"
        
        plan += "SOPHOMORE YEAR:\n"
        plan += "Fall Year 2 (18 credits):\n"
        plan += "• CS 25200 - Systems Programming (4 cr)\n"
        plan += "• CS 38100 - Introduction to Analysis of Algorithms (3 cr)\n"
        plan += "• MA 26100 - Multivariate Calculus (4 cr)\n"
        plan += "• STAT 35000 - Introduction to Statistics (3 cr)\n"
        plan += "• General Education course (4 cr)\n\n"
        
        plan += "Spring Year 2 (17 credits):\n"
        plan += "• CS 35100 - Cloud Computing (3 cr)\n"
        plan += "• MA 26500 - Linear Algebra (3 cr)\n"
        plan += "• PHYS 27200 - Electric and Magnetic Interactions (4 cr)\n"
        if track_selections.get("stats_course"):
            plan += f"• {track_selections['stats_course']} (3 cr)\n"
        plan += "• General Education course (4 cr)\n\n"
        
        plan += "JUNIOR YEAR:\n"
        plan += "Fall Year 3 (18 credits):\n"
        plan += "• CS 37300 - Data Mining and Machine Learning (3 cr)\n"
        if track_selections.get("ai_course"):
            plan += f"• {track_selections['ai_course']} (3 cr)\n"
        if track_selections.get("electives") and len(track_selections["electives"]) > 0:
            plan += f"• {track_selections['electives'][0]} (3 cr)\n"
        plan += "• General Education courses (9 cr)\n\n"
        
        plan += "Spring Year 3 (16 credits):\n"
        if track_selections.get("electives") and len(track_selections["electives"]) > 1:
            plan += f"• {track_selections['electives'][1]} (3 cr)\n"
        plan += "• General Education courses (10 cr)\n"
        plan += "• Free electives (3 cr)\n\n"
        
        plan += "Total: 109 credits by Spring Year 3\n"
        plan += "Success probability: Approximately 50-60% (challenging but achievable)\n\n"
        
        plan += "Key considerations for your plan:\n"
        plan += "• Summer after freshman year is critical - don't fail CS 25000 or 25100\n"
        plan += "• Your track electives are well-balanced between theory and application\n"
        plan += "• You'll have strong preparation for AI/data science careers\n"
        if "numerical methods" in str(track_selections.get("electives", [])).lower():
            plan += "• The numerical methods course pairs well with your probability background\n"
        
        plan += "\nDoes this timeline work for you? Any concerns about the summer coursework or course load?"
        
        return plan

    def _handle_course_difficulty(self, query: str, context: ConversationContext, intent: Dict[str, Any]) -> str:
        """Handle course difficulty and study tips queries"""
        
        extracted = context.extracted_context
        current_year = extracted.get("current_year", "freshman")
        
        # Extract specific course mentioned
        import re
        course_patterns = [
            r"cs\s*180", r"cs\s*18000", r"cs\s*182", r"cs\s*18200",
            r"cs\s*240", r"cs\s*24000", r"cs\s*250", r"cs\s*25000",
            r"cs\s*251", r"cs\s*25100", r"cs\s*252", r"cs\s*25200"
        ]
        
        mentioned_course = None
        for pattern in course_patterns:
            matches = re.findall(pattern, query.lower())
            if matches:
                # Normalize to full course code
                course_num = matches[0].replace("cs", "").replace(" ", "")
                if len(course_num) == 3:
                    course_num += "00"
                mentioned_course = f"CS {course_num}"
                break
        
        # If no specific course mentioned, provide general difficulty overview
        if not mentioned_course:
            return self._provide_general_difficulty_overview(current_year)
        
        # Provide specific course difficulty analysis
        return self._provide_specific_course_difficulty(mentioned_course, current_year)

    def _provide_specific_course_difficulty(self, course_code: str, student_year: str) -> str:
        """Provide detailed difficulty analysis for a specific course"""
        
        course_info = self.knowledge_base["courses"].get(course_code)
        if not course_info:
            return f"I don't have detailed information about {course_code} in my database. Could you double-check the course code?"
        
        response = f"Let me give you the real scoop on {course_code} - {course_info['title']}.\n\n"
        
        # Difficulty rating and level
        difficulty_level = course_info.get("difficulty_level", "Moderate")
        difficulty_rating = course_info.get("difficulty_rating", 3.0)
        response += f"This is a {difficulty_level.lower()} course, rated {difficulty_rating}/5.0 by students. "
        
        # Time commitment
        time_commitment = course_info.get("time_commitment", "10-15 hours per week")
        response += f"Most students spend {time_commitment} on this course.\n\n"
        
        # Why it's challenging
        difficulty_factors = course_info.get("difficulty_factors", [])
        if difficulty_factors:
            response += "What makes it challenging:\n"
            for factor in difficulty_factors:
                response += f"- {factor}\n"
            response += "\n"
        
        # Success tips
        success_tips = course_info.get("success_tips", [])
        if success_tips:
            response += "Tips for success:\n"
            for tip in success_tips:
                response += f"- {tip}\n"
            response += "\n"
        
        # Common struggles
        common_struggles = course_info.get("common_struggles", [])
        if common_struggles:
            response += "Common student struggles:\n"
            for struggle in common_struggles:
                response += f"- {struggle}\n"
            response += "\n"
        
        # Personalized advice based on student year
        if student_year == "freshman" and course_code == "CS 18000":
            response += "Since you're a freshman, this is probably your first real programming course. Don't panic if it feels overwhelming at first - everyone struggles initially. That's completely normal. The key is consistency and starting assignments early."
        elif course_code in ["CS 25100", "CS 25200"]:
            response += "Important note: This is considered one of the hardest courses in the CS curriculum. Many students find it extremely challenging, but it's also where you'll learn the most. Plan accordingly and consider taking fewer electives this semester."
        
        return response

    def _provide_general_difficulty_overview(self, student_year: str) -> str:
        """Provide overview of course difficulties by level"""
        
        response = f"Here's a breakdown of CS course difficulty levels for {student_year} students:\n\n"
        
        # Foundation courses difficulty ranking
        response += "Foundation Courses (18000-25200 level):\n"
        foundation_difficulties = [
            ("CS 18000", "Hard (4.2/5)", "First programming course - steep learning curve"),
            ("CS 18200", "Hard (4.0/5)", "Mathematical proofs and abstract thinking"),
            ("CS 24000", "Moderate-Hard (3.8/5)", "Pointers and memory management"),
            ("CS 25000", "Hard (4.1/5)", "Assembly programming and computer architecture"),
            ("CS 25100", "Very Hard (4.5/5)", "Data structures and algorithms - most challenging"),
            ("CS 25200", "Very Hard (4.4/5)", "System programming and large projects")
        ]
        
        for course, difficulty, reason in foundation_difficulties:
            response += f"- {course}: {difficulty} - {reason}\n"
        
        response += "\nUpper-Level Courses (30000+ level):\n"
        response += "- Generally range from Moderate (3.0/5) to Hard (4.0/5)\n"
        response += "- Difficulty depends on your track and interests\n"
        response += "- More specialized but often more engaging\n\n"
        
        # General advice by year
        if student_year == "freshman":
            response += "Advice for freshmen: Focus on CS 18000 and 18200. These set the foundation for everything else. Don't take more than 2 CS courses per semester."
        elif student_year == "sophomore":
            response += "Advice for sophomores: CS 25100 and 25200 are the hardest you'll face. Consider your course load carefully and use summer sessions strategically."
        
        return response

    def _handle_se_track_courses(self, query: str, context: ConversationContext, intent: Dict[str, Any]) -> str:
        """Handle Software Engineering track specific course queries"""
        
        extracted = context.extracted_context
        completed = extracted.get("completed_courses", [])
        
        # Get SE track information
        se_track = self.knowledge_base["tracks"]["Software Engineering"]
        
        response = "Here are your Software Engineering track course options:\n\n"
        
        # Core Required Courses
        response += "**Required Core Courses (Must take all 4):**\n"
        for course_option in se_track["core_required"]:
            course_code = course_option["code"]
            prereqs = self.knowledge_base["prerequisites"].get(course_code, [])
            status = "✓ Completed" if course_code in completed else "○ Available" if all(p in completed for p in prereqs) else "✗ Prerequisites needed"
            response += f"• {course_code}: {course_option['title']} - {status}\n"
            response += f"  Purpose: {course_option['recommended_for']}\n"
        
        response += "\n**Systems Choice (Choose one):**\n"
        for course_option in se_track["choose_one_systems"]:
            course_code = course_option["code"]
            prereqs = self.knowledge_base["prerequisites"].get(course_code, [])
            status = "✓ Completed" if course_code in completed else "○ Available" if all(p in completed for p in prereqs) else "✗ Prerequisites needed"
            response += f"• {course_code}: {course_option['title']} - {status}\n"
            response += f"  Best for: {course_option['recommended_for']}\n"
        
        
        response += "\n**Track Elective (Choose one):**\n"
        for course_option in se_track["choose_one_elective"]:
            course_code = course_option["code"]
            prereqs = self.knowledge_base["prerequisites"].get(course_code, [])
            status = "✓ Completed" if course_code in completed else "○ Available" if all(p in completed for p in prereqs) else "✗ Prerequisites needed"
            response += f"• {course_code}: {course_option['title']} - {status}\n"
            response += f"  Best for: {course_option['recommended_for']}\n"
        
        # Add next steps based on current progress
        response += "\n**Your Next Steps:**\n"
        
        # Check prerequisites for core courses
        next_foundation = []
        for course_option in se_track["core_required"]:
            course_code = course_option["code"]
            if course_code not in completed:
                prereqs = self.knowledge_base["prerequisites"].get(course_code, [])
                missing_prereqs = [p for p in prereqs if p not in completed]
                if missing_prereqs:
                    next_foundation.extend(missing_prereqs)
        
        if next_foundation:
            response += f"First complete these prerequisites: {', '.join(set(next_foundation))}\n"
        else:
            available_track_courses = []
            for course_option in se_track["core_required"]:
                course_code = course_option["code"]
                if course_code not in completed:
                    prereqs = self.knowledge_base["prerequisites"].get(course_code, [])
                    if all(p in completed for p in prereqs):
                        available_track_courses.append(course_code)
            
            if available_track_courses:
                response += f"You can start with: {', '.join(available_track_courses)}\n"
        
        response += f"\nTotal track credits needed: {se_track['total_credits']} credits"
        
        return response

    def _handle_failure_recovery(self, query: str, context: ConversationContext, intent: Dict[str, Any]) -> str:
        """Handle course failure recovery queries"""
        
        extracted = context.extracted_context
        failed_courses = extracted.get("failed_courses", [])
        
        # Enhanced course extraction from query if not already in context
        if not failed_courses:
            import re
            
            # Try multiple patterns to extract failed courses
            patterns = [
                r"(CS\s?\d{5}|MA\s?\d{5}|STAT\s?\d{5})",  # Full format
                r"cs\s*(\d{3})",  # 3-digit format
                r"fail[a-z]*cs\s*(\d{3})",  # Concatenated failures
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, query.lower())
                for match in matches:
                    if len(match) == 3:  # 3-digit format
                        normalized = self._normalize_course_code(f"CS{match}")
                    else:  # Full format
                        normalized = match.upper().replace(" ", " ")
                    
                    if normalized and normalized not in failed_courses:
                        failed_courses.append(normalized)
        
        # Check for specific course mentions in the query text  
        query_lower = query.lower()
        if not failed_courses:
            if "cs 182" in query_lower or "cs182" in query_lower or "failedcs182" in query_lower:
                failed_courses.append("CS 18200")
            elif "cs 180" in query_lower or "cs180" in query_lower:
                failed_courses.append("CS 18000")
            elif "cs 240" in query_lower or "cs240" in query_lower:
                failed_courses.append("CS 24000")
            elif "cs 250" in query_lower or "cs250" in query_lower:
                failed_courses.append("CS 25000")
            elif "cs 251" in query_lower or "cs251" in query_lower:
                failed_courses.append("CS 25100")
            elif "cs 252" in query_lower or "cs252" in query_lower:
                failed_courses.append("CS 25200")
        
        response = ""
        
        if failed_courses:
            # Update context with discovered failed courses
            context.extracted_context["failed_courses"] = failed_courses
            
            response += f"I see you're dealing with failure in {', '.join(failed_courses)}. Let me help you create a recovery strategy.\n\n"
            
            for course in failed_courses:
                # Get course info from knowledge base
                course_info = self.knowledge_base["courses"].get(course, {})
                course_title = course_info.get("title", "Unknown Course")
                
                response += f"**{course} - {course_title}**\n"
                
                # Get failure scenario analysis
                try:
                    scenario = self.graduation_planner.analyze_foundation_delay_scenario(course, 3)
                    
                    graduation_impact = scenario.get('graduation_impact', 'delay your graduation by 1-2 semesters')
                    difficulty = scenario.get('difficulty', 'Moderate')
                    strategy = scenario.get('recovery_strategy', 'Retake the course next semester')
                    
                    response += f"Impact: {graduation_impact}\n"
                    response += f"Recovery difficulty: {difficulty}\n"
                    response += f"Strategy: {strategy}\n"
                    
                    # Summer recovery options
                    if scenario.get("summer_option"):
                        response += "\nGood news! Summer recovery is available. "
                        if scenario.get("summer_recovery"):
                            summer = scenario["summer_recovery"]
                            courses = summer.get('courses', [])
                            timeline = summer.get('timeline', 'Check summer course offerings')
                            response += f"You can take {', '.join(courses)} over summer. Timeline: {timeline}\n"
                    
                    # Affected downstream courses
                    affected = scenario.get("affected_courses", [])
                    if affected:
                        response += f"\nThis failure affects these future courses: {', '.join(affected)}\n"
                        response += "You'll need to plan your course sequence carefully to minimize further delays.\n"
                    
                except Exception as e:
                    # Fallback if graduation planner fails
                    response += f"This is a foundation course that may delay your graduation timeline. I recommend retaking it as soon as possible.\n"
                
                response += "\n"
            
            # Personalized advice based on user's situation
            completed_courses = extracted.get("completed_courses", [])
            if "CS 24000" in completed_courses and "CS 18200" in failed_courses:
                response += "Since you've done well in CS 24000, you have the programming foundation. Focus on the theoretical aspects when retaking CS 18200.\n\n"
            
        else:
            response += "I can help you create a recovery strategy for failed courses. "
            response += "Which specific course are you having trouble with? "
            response += "Please let me know the course code (like CS 18200, CS 25100, etc.) so I can give you detailed guidance.\n\n"
        
        # Enhanced recovery tips
        response += "**Recovery Tips:**\n"
        response += "• Meet with your academic advisor immediately to adjust your plan\n"
        response += "• Identify why the course was challenging and address those issues\n"
        response += "• Consider CS tutoring services or study groups\n"
        response += "• Plan lighter course loads while retaking failed courses\n"
        response += "• Use summer courses strategically to get back on track\n"
        response += "• Don't panic - many students face setbacks and still graduate successfully"
        
        return response

    def _handle_codo_advice(self, query: str, context: ConversationContext, intent: Dict[str, Any]) -> str:
        """Handle CODO (Change of Degree Objective) advice"""
        
        self._track_query("KNOWLEDGE_GRAPH_ACCESS", {
            "data_accessed": "CODO requirements",
            "requirements_checked": ["GPA", "CS 18000", "Math requirement", "Space availability"],
            "student_context": context.extracted_context
        }, "Accessing CODO requirements from knowledge base")
        
        codo_reqs = self.knowledge_base.get("codo_requirements", {})
        
        min_gpa = codo_reqs.get('minimum_gpa', 2.75)
        min_credits = codo_reqs.get('minimum_purdue_credits', 12)
        
        response = f"To change your major to Computer Science, you need a minimum {min_gpa} GPA and {min_credits} Purdue credits.\n\n"
        
        response += "Required courses:\n"
        for req_course in codo_reqs.get("required_courses", []):
            response += f"{req_course['code']}: {req_course['title']} with {req_course['minimum_grade']} or better\n"
        
        response += "\nMath requirement - you need B or better in ONE of these:\n"
        for math_option in codo_reqs.get("math_requirement", {}).get("options", []):
            response += f"{math_option['code']}: {math_option['title']}\n"
        
        app_terms = ', '.join(codo_reqs.get('application_terms', []))
        admission_basis = codo_reqs.get('admission_basis', 'Space available')
        response += f"\nYou can apply during {app_terms} terms. Admission is on {admission_basis.lower()}.\n\n"
        
        # Personalized advice based on context
        extracted = context.extracted_context
        current_gpa = extracted.get("gpa")
        if current_gpa:
            min_required = codo_reqs.get("minimum_gpa", 2.75)
            if current_gpa >= min_required:
                response += f"Good news - your {current_gpa} GPA meets the minimum requirement.\n"
            else:
                needed = min_required - current_gpa
                response += f"Your {current_gpa} GPA is {needed:.2f} points below the minimum. You'll need to focus on improving your grades before applying.\n"
        
        contact_email = codo_reqs.get('contact_info', {}).get('email', 'csug@purdue.edu')
        space_info = codo_reqs.get('space_availability', 'Space is limited')
        response += f"\nContact {contact_email} for questions. Important note: {space_info.lower()}."
        
        return response

    def _handle_career_guidance(self, query: str, context: ConversationContext, intent: Dict[str, Any]) -> str:
        """Handle career guidance queries"""
        
        extracted = context.extracted_context
        track = extracted.get("target_track", "Machine Intelligence")
        
        guidance = self.academic_advisor.get_track_specific_guidance(track, "junior")
        
        response = f"## Career Guidance for {track} Track\n\n"
        
        career_prep = guidance.get("career_preparation", {})
        response += f"**Internship Focus:** {career_prep.get('internships', 'General software development')}\n"
        response += f"**Project Recommendations:** {career_prep.get('projects', 'Build portfolio projects')}\n"
        
        if "graduate_school" in career_prep:
            response += f"**Graduate School:** {career_prep['graduate_school']}\n"
        
        response += f"\n**Key Programming Languages:** {', '.join(guidance.get('programming_languages', ['Python', 'Java']))}\n"
        
        # Course sequence tips
        sequence_tips = guidance.get("course_sequence_tips", {})
        if sequence_tips:
            response += "\n**Course Timing Strategy:**\n"
            for phase, tip in sequence_tips.items():
                response += f"- **{phase.title()}:** {tip}\n"
        
        # Industry-specific advice
        career_goal = extracted.get("career_goal", "").lower()
        if "research" in career_goal:
            response += "\n**Research Path:**\n- Consider CS 49700 (Honors Research)\n- Build relationships with faculty\n- Look into graduate school preparation\n"
        elif "startup" in career_goal:
            response += "\n**Startup Path:**\n- Focus on full-stack development\n- Build complete projects\n- Consider entrepreneurship courses\n"
        
        return response

    def _handle_general_query(self, query: str, context: ConversationContext, intent: Dict[str, Any]) -> str:
        """Handle general queries using comprehensive knowledge"""
        
        # Use Gemini to generate response using all knowledge
        system_prompt = f"""
        You are an expert Purdue Computer Science academic advisor with access to comprehensive knowledge.
        
        Student Context: {json.dumps(context.extracted_context)}
        Conversation History: {context.conversation_history[-3:] if len(context.conversation_history) > 3 else context.conversation_history}
        
        Knowledge Base Summary:
        - Complete course catalog with prerequisites
        - Graduation planning systems
        - Track specialization guidance (MI/SE)
        - CODO requirements
        - Failure recovery strategies
        - Career guidance
        
        Provide a helpful, personalized response to: "{query}"
        
        Guidelines:
        - Use specific course codes and requirements
        - Reference student's context when relevant
        - Provide actionable advice
        - Be encouraging but realistic
        - Include relevant deadlines or timelines
        """
        
        try:
            return self.gemini_model.chat_completion_with_retry(
                ,
                prompt,
                ,
                
            )
            
        except Exception as e:
            return f"I'd be happy to help with your question. Could you provide more specific details about what you're looking for? I can assist with course planning, graduation timelines, track selection, or any other CS academic questions."

    def _get_semester_number(self, extracted_context: Dict[str, Any]) -> int:
        """Convert student context to semester number"""
        year = extracted_context.get("current_year", "sophomore").lower()
        semester = extracted_context.get("current_semester", "fall").lower()
        
        year_map = {"freshman": 0, "sophomore": 2, "junior": 4, "senior": 6}
        base = year_map.get(year, 2)
        
        if semester == "spring":
            return base + 1
        else:
            return base + 2

    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of conversation context"""
        if session_id not in self.conversation_contexts:
            return {"error": "Session not found"}
        
        context = self.conversation_contexts[session_id]
        return {
            "session_id": session_id,
            "extracted_context": context.extracted_context,
            "conversation_length": len(context.conversation_history),
            "current_topic": context.current_topic,
            "last_queries": context.last_queries
        }

    def _handle_multi_year_course_planning(self, query: str, context: ConversationContext, intent: Dict[str, Any]) -> str:
        """Handle comprehensive multi-year course planning requests"""
        
        extracted = context.extracted_context
        target_track = extracted.get("target_track", "")
        current_year = extracted.get("current_year", "freshman")
        
        # Check if user mentioned machine learning/AI interest in query
        query_lower = query.lower()
        if ("machine learning" in query_lower or "ml" in query_lower or "ai" in query_lower or 
            "specializ" in query_lower and ("ml" in query_lower or "machine" in query_lower)):
            target_track = "Machine Intelligence"
        
        response = "Here's your complete 4-year CS course plan"
        if target_track:
            response += f" for the {target_track} track"
        response += ":\n\n"
        
        # Freshman Year
        response += "**FRESHMAN YEAR (Year 1)**\n"
        response += "**Fall Semester:**\n"
        response += "• CS 18000 - Problem Solving and Object-Oriented Programming (4 credits)\n"
        response += "• MA 16100 - Plane Analytic Geometry and Calculus I (5 credits)\n"
        response += "• CS 19300 - Tools (1 credit)\n"
        response += "• General Education courses (5-6 credits)\n\n"
        
        response += "**Spring Semester:**\n"
        response += "• CS 18200 - Foundations of Computer Science (3 credits)\n"
        response += "• CS 24000 - Programming in C (3 credits)\n"
        response += "• MA 16200 - Plane Analytic Geometry and Calculus II (5 credits)\n"
        response += "• General Education courses (5-6 credits)\n\n"
        
        # Sophomore Year
        response += "**SOPHOMORE YEAR (Year 2)**\n"
        response += "**Fall Semester:**\n"
        response += "• CS 25100 - Data Structures and Algorithms (4 credits)\n"
        response += "• CS 25000 - Computer Architecture (4 credits)\n"
        response += "• MA 26100 - Multivariate Calculus (4 credits)\n"
        response += "• General Education courses (3-4 credits)\n\n"
        
        response += "**Spring Semester:**\n"
        response += "• CS 25200 - Systems Programming (4 credits)\n"
        response += "• MA 26500 - Linear Algebra (3 credits)\n"
        response += "• STAT 35000 - Statistics (3 credits)\n"
        response += "• General Education courses (6 credits)\n\n"
        
        # Junior Year - Track specific
        response += "**JUNIOR YEAR (Year 3)**\n"
        if "Machine Intelligence" in target_track or "ml" in query_lower or "machine learning" in query_lower:
            response += "**Fall Semester (Machine Intelligence Track):**\n"
            response += "• CS 30100 - Computing for Science and Engineering (3 credits)\n"
            response += "• CS 38100 - Introduction to Analysis of Algorithms (3 credits)\n"
            response += "• CS 37300 - Data Mining and Machine Learning (3 credits)\n"
            response += "• Technical Elective (3 credits)\n"
            response += "• General Education (3 credits)\n\n"
            
            response += "**Spring Semester:**\n"
            response += "• CS 48900 - Machine Learning (3 credits)\n"
            response += "• CS 47100 - Introduction to Artificial Intelligence (3 credits)\n"
            response += "• CS Track Elective (3 credits)\n"
            response += "• Technical Elective (3 credits)\n"
            response += "• Free Elective (3 credits)\n\n"
        else:
            response += "**Fall Semester:**\n"
            response += "• CS 30100 - Computing for Science and Engineering (3 credits)\n"
            response += "• CS 38100 - Introduction to Analysis of Algorithms (3 credits)\n"
            response += "• CS Track Course (3 credits)\n"
            response += "• Technical Elective (3 credits)\n"
            response += "• General Education (3 credits)\n\n"
            
            response += "**Spring Semester:**\n"
            response += "• CS Track Course (3 credits)\n"
            response += "• CS Track Course (3 credits)\n"
            response += "• Technical Elective (3 credits)\n"
            response += "• Free Elective (3 credits)\n"
            response += "• Free Elective (3 credits)\n\n"
        
        # Senior Year
        response += "**SENIOR YEAR (Year 4)**\n"
        response += "**Fall Semester:**\n"
        response += "• CS 40800 - Software Testing (3 credits)\n"
        response += "• CS Senior Design I (3 credits)\n"
        response += "• CS Track Course (3 credits)\n"
        response += "• Free Elective (3 credits)\n"
        response += "• Free Elective (3 credits)\n\n"
        
        response += "**Spring Semester:**\n"
        response += "• CS Senior Design II (3 credits)\n"
        response += "• CS Track Course (3 credits)\n"
        response += "• Free Elective (3 credits)\n"
        response += "• Free Elective (3 credits)\n"
        response += "• Free Elective (3 credits)\n\n"
        
        # Important guidelines
        response += "**IMPORTANT GUIDELINES:**\n"
        response += "• Total: 120+ credits for graduation\n"
        response += "• CS Core: 29 credits (CS 18000, 18200, 19300, 24000, 25000, 25100, 25200, 30100, 38100, 40800)\n"
        response += "• CS Track: 12 credits (4 courses in your chosen track)\n"
        response += "• Math: MA 16100, 16200, 26100, 26500 + STAT 35000\n"
        response += "• General Education: 30 credits across different categories\n"
        response += "• Technical Electives: Must be science/engineering courses\n\n"
        
        if "Machine Intelligence" in target_track or "ml" in query_lower or "machine learning" in query_lower:
            response += "**MACHINE LEARNING FOCUS:**\n"
            response += "Since you're interested in ML, this plan emphasizes:\n"
            response += "• Strong mathematical foundation (calculus, linear algebra, statistics)\n"
            response += "• Core ML courses (CS 37300, 48900, 47100)\n"
            response += "• Programming skills (Python, R, data analysis tools)\n"
            response += "• Optional: Consider CS 54701 (Information Retrieval), CS 57800 (Statistical Machine Learning)\n\n"
        
        response += "**SUCCESS TIPS:**\n"
        response += "• Take CS 18000 seriously - everything builds on it\n"
        response += "• Don't skip math courses - they're crucial for advanced CS\n"
        response += "• Start thinking about your track by sophomore year\n"
        response += "• Consider internships between junior and senior year\n"
        response += "• Join CS organizations and research groups"
        
        return response

    def _handle_year_level_course_planning(self, query: str, context: ConversationContext, intent: Dict[str, Any], year_level: str) -> str:
        """Handle comprehensive year-level course planning queries for all years"""
        
        if year_level == "freshman":
            return self._get_freshman_course_plan()
        elif year_level == "sophomore":
            return self._get_sophomore_course_plan()
        elif year_level == "junior":
            # Check if student has declared a track
            declared_track = context.extracted_context.get("target_track", "").lower()
            if "machine intelligence" in declared_track or "mi" in declared_track:
                return self._get_junior_mi_course_plan()
            elif "software engineering" in declared_track or "se" in declared_track:
                return self._get_junior_se_course_plan()
            else:
                return self._get_junior_course_plan()
        elif year_level == "senior":
            # Check if student has declared a track
            declared_track = context.extracted_context.get("target_track", "").lower()
            if "machine intelligence" in declared_track or "mi" in declared_track:
                return self._get_senior_mi_course_plan()
            elif "software engineering" in declared_track or "se" in declared_track:
                return self._get_senior_se_course_plan()
            else:
                return self._get_senior_course_plan()
        else:
            # Generate AI response for unclear year specification
            year_prompt = "Generate a helpful response when course planning is requested but academic year is unclear. Ask user to specify freshman, sophomore, junior, or senior year."
            try:
                return self.smart_ai_engine.generate_smart_response(year_prompt, {"context": "unclear_academic_year"})
            except:
                try:
                    return self._get_emergency_ai_response("Generate a brief response asking the student to specify which academic year (freshman, sophomore, junior, senior) they need course planning help for")
                except:
                    return ""
    
    def _get_freshman_course_plan(self) -> str:
        """AI-generated freshman course planning using knowledge base"""
        
        # Create comprehensive context for AI generation
        freshman_context = {
            "academic_year": "freshman",
            "key_courses": ["CS 18000", "CS 18200", "CS 24000", "MA 16100", "MA 16200", "CS 19300"],
            "critical_requirements": ["CS 18000 prerequisite for all CS courses", "Math sequence importance"],
            "guidelines": ["15-17 credits per semester", "Focus on foundation", "Get help early"],
            "warnings": ["Don't overload", "Pass CS 18000 with C or better", "Don't skip prerequisites"]
        }
        
        # Generate AI response for freshman course planning
        freshman_prompt = f"""
        Generate a comprehensive freshman course plan for Purdue Computer Science students.
        
        Include:
        1. Fall semester course recommendations with descriptions
        2. Spring semester course recommendations with descriptions  
        3. Important guidelines and warnings
        4. Why these courses matter for CS progression
        5. Credit load recommendations
        6. Study tips and resources
        
        Context: {freshman_context}
        
        Make it encouraging, specific to Purdue CS, and emphasize building a strong foundation.
        Focus on CS 18000, 18200, 24000 and math sequence as critical courses.
        """
        
        try:
            return self.smart_ai_engine.generate_smart_response(freshman_prompt, freshman_context)
        except Exception as e:
            self.logger.error(f"Error generating freshman course plan: {e}")
            # AI-powered emergency fallback
            try:
                return self._get_emergency_ai_response("Generate a brief response about freshman CS course planning mentioning CS 18000, CS 18200, CS 24000, and calculus courses")
            except:
                return ""
    
    def _get_sophomore_course_plan(self) -> str:
        """Comprehensive sophomore course planning - CORRECTED SEQUENCE"""
        response = "Here are the essential courses for computer science sophomores at Purdue:\n\n"
        
        response += "**Prerequisites Check:**\n"
        response += "Before sophomore courses, you should have completed:\n"
        response += "• CS 18000 (Problem Solving and Object-Oriented Programming)\n"
        response += "• CS 18200 (Foundations of Computer Science)\n"
        response += "• CS 24000 (Programming in C)\n"
        response += "• MA 16100 and MA 16200 (Calculus I & II)\n\n"
        
        response += "**Fall Semester (Sophomore Year):**\n"
        response += "• CS 25000 - Computer Architecture (4 credits)\n"
        response += "  - Computer organization and processor design\n"
        response += "  - Assembly language programming\n"
        response += "  - Hardware-software interface\n\n"
        
        response += "• CS 25100 - Data Structures and Algorithms (3 credits)\n"
        response += "  - Core CS course - algorithms and data structures\n"
        response += "  - CRITICAL: Gateway to all upper-level CS courses\n"
        response += "  - Very challenging - plan accordingly\n\n"
        
        response += "• MA 26100 - Multivariate Calculus (4 credits)\n"
        response += "  - Required for many upper-level CS courses\n\n"
        
        response += "• General Education courses (4-5 credits)\n\n"
        
        response += "**Spring Semester (Sophomore Year):**\n"
        response += "• CS 25200 - Systems Programming (4 credits)\n"
        response += "  - Most challenging CS course in the curriculum\n"
        response += "  - Unix/Linux system programming, processes, threads\n"
        response += "  - Plan for heavy workload\n\n"
        
        response += "• CS 38100 - Introduction to Analysis of Algorithms (3 credits)\n"
        response += "  - Mathematical analysis of algorithms\n"
        response += "  - Required core course\n\n"
        
        response += "• MA 26500 - Linear Algebra (3 credits)\n"
        response += "  - Essential for machine learning and graphics\n\n"
        
        response += "• General Education courses (5-6 credits)\n\n"
        
        response += "**Important Guidelines for Sophomores:**\n"
        response += "• Take a MAXIMUM of 3 CS courses per semester\n"
        response += "• CS 25000, 25100, and 25200 are all challenging\n"
        response += "• Consider summer courses to lighten regular semester load\n"
        response += "• Use office hours extensively for all core courses\n"
        response += "• Form study groups for challenging courses\n\n"
        
        response += "**Success Tips:**\n"
        response += "• Start assignments early (especially CS 25200)\n"
        response += "• Master debugging and system programming\n"
        response += "• Build strong relationship with TAs and professors\n"
        response += "• CS 38100 is typically taken in spring sophomore year\n"
        response += "• Prepare for track selection in junior year"
        
        return response
    
    def _get_junior_course_plan(self) -> str:
        """Comprehensive junior course planning - TRACK-SPECIFIC"""
        response = "Here are the course planning guidelines for computer science juniors at Purdue:\n\n"
        
        response += "**Prerequisites Check:**\n"
        response += "Before junior-level courses, you should have completed:\n"
        response += "• CS 25000 (Computer Architecture)\n"
        response += "• CS 25100 (Data Structures and Algorithms)\n"
        response += "• CS 25200 (Systems Programming)\n"
        response += "• CS 38100 (Introduction to Analysis of Algorithms)\n"
        response += "• Math sequence through MA 26100 and MA 26500\n\n"
        
        response += "**Fall Semester (Junior Year):**\n"
        response += "• STAT 35000 - Elementary Statistics (3 credits)\n"
        response += "  - Required for degree\n"
        response += "  - Mathematical foundation for data analysis\n\n"
        
        response += "**CRITICAL: Track Declaration Required**\n"
        response += "Junior year is when you must declare your track specialization.\n"
        response += "Choose either Machine Intelligence OR Software Engineering track.\n\n"
        
        response += "**If you haven't declared a track yet, ask me:**\n"
        response += "• \"Tell me about Machine Intelligence track\"\n"
        response += "• \"Tell me about Software Engineering track\"\n"
        response += "• \"Help me choose between MI and SE tracks\"\n\n"
        
        response += "**Additional Junior Requirements:**\n"
        response += "• Science sequence completion (Physics or Chemistry)\n"
        response += "• Upper-level math elective\n"
        response += "• Communication requirement (COM 20400 or equivalent)\n"
        response += "• General education electives\n\n"
        
        response += "**Important Guidelines for Juniors:**\n"
        response += "• Can handle 3-4 CS courses per semester\n"
        response += "• Focus on track specialization\n"
        response += "• Start internship applications (fall for summer positions)\n"
        response += "• Consider research opportunities\n"
        response += "• Plan senior capstone project\n\n"
        
        response += "**Career Preparation:**\n"
        response += "• Technical interview practice\n"
        response += "• Build portfolio projects\n"
        response += "• Attend career fairs\n"
        response += "• Network with alumni and industry professionals"
        
        return response
    
    def _get_junior_mi_course_plan(self) -> str:
        """Machine Intelligence track junior course planning"""
        response = "Here's your Machine Intelligence track course plan for junior year:\n\n"
        
        response += "**Prerequisites Check:**\n"
        response += "You should have completed all foundation courses through CS 38100.\n\n"
        
        response += "**Fall Semester (Junior Year):**\n"
        response += "• STAT 35000 - Elementary Statistics (3 credits)\n"
        response += "  - Required for degree and prerequisite for CS 37300\n\n"
        
        response += "• CS 37300 - Data Mining and Machine Learning (3 credits)\n"
        response += "  - CORE MI track requirement\n"
        response += "  - Introduction to ML algorithms and data mining\n"
        response += "  - Prerequisites: CS 25100, STAT 35000\n\n"
        
        response += "• Science sequence completion (3-4 credits)\n"
        response += "• General education courses (6-7 credits)\n\n"
        
        response += "**Spring Semester (Junior Year):**\n"
        response += "• Choose ONE AI foundation course (REQUIRED):\n"
        response += "  ◦ CS 47100 - Introduction to Artificial Intelligence (3 credits)\n"
        response += "    - Recommended for: theoretical ML, research, graduate school\n"
        response += "    - Covers: search algorithms, knowledge representation, reasoning\n"
        response += "  ◦ CS 47300 - Web Information Search & Management (3 credits)\n"
        response += "    - Recommended for: web applications, industry, applied data mining\n"
        response += "    - Covers: web crawling, information retrieval, search engines\n\n"
        
        response += "• Upper-level math elective (3 credits)\n"
        response += "• General education courses (6-9 credits)\n\n"
        
        response += "**MI Track Electives (Choose 2-3 more courses over junior/senior years):**\n"
        response += "• CS 57700 - Natural Language Processing\n"
        response += "• CS 57800 - Statistical Machine Learning\n"
        response += "• CS 43900 - Introduction to Data Visualization\n"
        response += "• CS 44000 - Large-Scale Data Analytics\n"
        response += "• CS 47800 - Introduction to Bioinformatics\n\n"
        
        response += "**Total MI Track Requirements: 15 credits**\n"
        response += "• CS 37300 (required)\n"
        response += "• CS 47100 OR CS 47300 (required choice)\n"
        response += "• 3 additional MI electives (9 credits)\n\n"
        
        response += "**Career Preparation:**\n"
        response += "• Build ML/AI portfolio projects\n"
        response += "• Learn Python libraries: scikit-learn, TensorFlow, PyTorch\n"
        response += "• Consider research opportunities in AI labs\n"
        response += "• Apply for AI/ML internships"
        
        return response
    
    def _get_junior_se_course_plan(self) -> str:
        """Software Engineering track junior course planning"""
        response = "Here's your Software Engineering track course plan for junior year:\n\n"
        
        response += "**Prerequisites Check:**\n"
        response += "You should have completed all foundation courses through CS 38100.\n\n"
        
        response += "**Fall Semester (Junior Year):**\n"
        response += "• STAT 35000 - Elementary Statistics (3 credits)\n"
        response += "  - Required for degree\n\n"
        
        response += "• CS 30700 - Software Engineering I (3 credits)\n"
        response += "  - CORE SE track requirement\n"
        response += "  - Software development processes and methodologies\n"
        response += "  - Prerequisites: CS 25200\n\n"
        
        response += "• Science sequence completion (3-4 credits)\n"
        response += "• General education courses (6-7 credits)\n\n"
        
        response += "**Spring Semester (Junior Year):**\n"
        response += "• CS 40800 - Software Testing (3 credits)\n"
        response += "  - CORE SE track requirement\n"
        response += "  - Essential for quality assurance\n"
        response += "  - Prerequisites: CS 30700\n\n"
        
        response += "• Choose ONE systems course (REQUIRED):\n"
        response += "  ◦ CS 35200 - Compilers (3 credits)\n"
        response += "    - Recommended for: language development, tool building\n"
        response += "    - Covers: parsing, code generation, optimization\n"
        response += "  ◦ CS 35400 - Operating Systems (3 credits)\n"
        response += "    - Recommended for: system programming, performance optimization\n"
        response += "    - Covers: process management, memory, file systems\n\n"
        
        response += "• Upper-level math elective (3 credits)\n"
        response += "• General education courses (6-9 credits)\n\n"
        
        response += "**SE Track Electives (Choose 1 more course over junior/senior years):**\n"
        response += "• CS 35300 - Principles of Concurrency and Parallelism\n"
        response += "• CS 42200 - Computer Networks\n"
        response += "• CS 42600 - Computer Security\n"
        response += "• CS 44800 - Introduction to Relational Databases\n"
        response += "• CS 47500 - Human-Computer Interaction\n"
        response += "• CS 51000 - Software Engineering (advanced)\n\n"
        
        response += "**Total SE Track Requirements: 15 credits**\n"
        response += "• CS 30700 (required)\n"
        response += "• CS 40800 (required)\n"
        response += "• CS 35200 OR CS 35400 (required choice)\n"
        response += "• 2 additional SE electives (6 credits)\n\n"
        
        response += "**Career Preparation:**\n"
        response += "• Build software engineering portfolio projects\n"
        response += "• Learn industry tools: Git, Docker, CI/CD\n"
        response += "• Practice system design interviews\n"
        response += "• Apply for software engineering internships"
        
        return response
    
    def _get_senior_course_plan(self) -> str:
        """Comprehensive senior course planning"""
        response = "Here are the course planning guidelines for computer science seniors at Purdue:\n\n"
        
        response += "**Graduation Requirements Check:**\n"
        response += "Ensure you've completed:\n"
        response += "• All CS core courses (CS 18000, 18200, 24000, 25000, 25100, 25200, 38100)\n"
        response += "• Track requirements (15 credits in chosen specialization)\n"
        response += "• Math requirements (MA 16100, 16200, 26100, 26500)\n"
        response += "• Statistics requirement (STAT 35000)\n"
        response += "• Science requirements (2-course sequence in Physics or Chemistry)\n"
        response += "• Communication and general education requirements\n\n"
        
        response += "**Required Senior Courses:**\n"
        response += "• CS 49X00 - Senior Capstone/Project (3 credits)\n"
        response += "  - Capstone experience in your track\n"
        response += "  - Team-based project or individual research\n"
        response += "  - Demonstrates mastery of CS concepts\n\n"
        
        response += "**Track Completion:**\n\n"
        
        response += "**Machine Intelligence Track Seniors:**\n"
        response += "• Complete remaining MI electives\n"
        response += "• Consider advanced courses: CS 58000+ level\n"
        response += "• Potential courses: Computer Vision, NLP, Advanced ML\n"
        response += "• Research opportunities in AI labs\n\n"
        
        response += "**Software Engineering Track Seniors:**\n"
        response += "• CS 40700 - Software Engineering Senior Project\n"
        response += "• Complete remaining SE electives\n"
        response += "• Advanced systems courses\n"
        response += "• Industry collaboration projects\n\n"
        
        response += "**Electives and Specialization:**\n"
        response += "• Advanced CS electives in areas of interest\n"
        response += "• Cross-disciplinary courses (Business, Design, etc.)\n"
        response += "• Graduate-level courses (if GPA > 3.0)\n"
        response += "• Independent study or research credit\n\n"
        
        response += "**Important Guidelines for Seniors:**\n"
        response += "• Focus on graduation requirements completion\n"
        response += "• Build substantial portfolio projects\n"
        response += "• Complete internships or co-ops\n"
        response += "• Network for full-time job opportunities\n"
        response += "• Consider graduate school applications\n\n"
        
        response += "**Career Transition:**\n"
        response += "• Job search and interview preparation\n"
        response += "• Professional development and certifications\n"
        response += "• Alumni network engagement\n"
        response += "• Industry conference attendance\n"
        response += "• Graduate school preparation (if applicable)\n\n"
        
        response += "**Final Semester Recommendations:**\n"
        response += "• Light course load (12-14 credits)\n"
        response += "• Focus on job search and interviews\n"
        response += "• Complete any missing requirements early\n"
        response += "• Prepare for post-graduation transition"
        
        return response
    
    def _get_senior_mi_course_plan(self) -> str:
        """Machine Intelligence track senior course planning"""
        response = "Here's your Machine Intelligence track course plan for senior year:\n\n"
        
        response += "**Graduation Requirements Check:**\n"
        response += "Ensure you've completed:\n"
        response += "• All CS core courses (CS 18000, 18200, 24000, 25000, 25100, 25200, 38100)\n"
        response += "• MI core requirements: CS 37300, CS 47100 OR CS 47300\n"
        response += "• Math requirements (MA 16100, 16200, 26100, 26500)\n"
        response += "• Statistics requirement (STAT 35000)\n"
        response += "• Science requirements (2-course sequence)\n\n"
        
        response += "**Fall Semester (Senior Year):**\n"
        response += "• Complete remaining MI track electives (6-9 credits needed):\n"
        response += "  ◦ CS 57700 - Natural Language Processing\n"
        response += "    - Text analysis, language models, NLP applications\n"
        response += "  ◦ CS 57800 - Statistical Machine Learning\n"
        response += "    - Advanced ML algorithms, statistical learning theory\n"
        response += "  ◦ CS 43900 - Introduction to Data Visualization\n"
        response += "    - Visual analytics, interactive visualization\n"
        response += "  ◦ CS 44000 - Large-Scale Data Analytics\n"
        response += "    - Big data processing, distributed computing\n"
        response += "  ◦ CS 47800 - Introduction to Bioinformatics\n"
        response += "    - Computational biology, genomics\n\n"
        
        response += "• General education completion (3-6 credits)\n"
        response += "• Free electives (3-6 credits)\n\n"
        
        response += "**Spring Semester (Senior Year):**\n"
        response += "• MI Capstone/Senior Project (3 credits)\n"
        response += "  - Research project in AI/ML\n"
        response += "  - Industry collaboration project\n"
        response += "  - Independent study under faculty supervision\n\n"
        
        response += "• Complete any remaining MI electives (3-6 credits)\n"
        response += "• Free electives or graduate courses (6-9 credits)\n\n"
        
        response += "**MI Track Total: 15 credits**\n"
        response += "✅ CS 37300 - Data Mining & Machine Learning (required)\n"
        response += "✅ CS 47100 OR CS 47300 - AI foundation (required choice)\n"
        response += "✅ 9 additional credits from MI electives above\n\n"
        
        response += "**Career Opportunities:**\n"
        response += "• Machine Learning Engineer\n"
        response += "• Data Scientist\n"
        response += "• AI Research Scientist\n"
        response += "• Computer Vision Engineer\n"
        response += "• NLP Engineer\n"
        response += "• Graduate school in AI/ML\n\n"
        
        response += "**Final Preparation:**\n"
        response += "• Build comprehensive AI/ML portfolio\n"
        response += "• Contribute to open-source ML projects\n"
        response += "• Consider internships at AI companies\n"
        response += "• Prepare for technical interviews in ML"
        
        return response
    
    def _get_senior_se_course_plan(self) -> str:
        """Software Engineering track senior course planning"""
        response = "Here's your Software Engineering track course plan for senior year:\n\n"
        
        response += "**Graduation Requirements Check:**\n"
        response += "Ensure you've completed:\n"
        response += "• All CS core courses (CS 18000, 18200, 24000, 25000, 25100, 25200, 38100)\n"
        response += "• SE core requirements: CS 30700, CS 40800, CS 35200 OR CS 35400\n"
        response += "• Math requirements (MA 16100, 16200, 26100, 26500)\n"
        response += "• Statistics requirement (STAT 35000)\n"
        response += "• Science requirements (2-course sequence)\n\n"
        
        response += "**Fall Semester (Senior Year):**\n"
        response += "• CS 40700 - Software Engineering Senior Project (3 credits)\n"
        response += "  - REQUIRED SE capstone course\n"
        response += "  - Large-scale team software project\n"
        response += "  - Industry-standard development practices\n\n"
        
        response += "• Complete remaining SE track electives (3-6 credits needed):\n"
        response += "  ◦ CS 35300 - Principles of Concurrency and Parallelism\n"
        response += "    - Multi-threaded programming, parallel algorithms\n"
        response += "  ◦ CS 42200 - Computer Networks\n"
        response += "    - Network protocols, distributed systems\n"
        response += "  ◦ CS 42600 - Computer Security\n"
        response += "    - Cybersecurity, secure software development\n"
        response += "  ◦ CS 44800 - Introduction to Relational Databases\n"
        response += "    - Database design, SQL, data management\n"
        response += "  ◦ CS 47500 - Human-Computer Interaction\n"
        response += "    - UI/UX design, user-centered development\n"
        response += "  ◦ CS 51000 - Software Engineering (advanced)\n"
        response += "    - Advanced SE methodologies and practices\n\n"
        
        response += "• General education completion (3-6 credits)\n\n"
        
        response += "**Spring Semester (Senior Year):**\n"
        response += "• Continue CS 40700 - Software Engineering Senior Project\n"
        response += "  - Project completion and presentation\n"
        response += "  - Industry collaboration or open source contribution\n\n"
        
        response += "• Complete any remaining SE electives (3-6 credits)\n"
        response += "• Free electives or graduate courses (6-9 credits)\n\n"
        
        response += "**SE Track Total: 15 credits**\n"
        response += "✅ CS 30700 - Software Engineering I (required)\n"
        response += "✅ CS 40800 - Software Testing (required)\n"
        response += "✅ CS 40700 - Software Engineering Senior Project (required)\n"
        response += "✅ CS 35200 OR CS 35400 - Systems choice (required)\n"
        response += "✅ 3 additional credits from SE electives above\n\n"
        
        response += "**Career Opportunities:**\n"
        response += "• Software Engineer\n"
        response += "• Senior Software Developer\n"
        response += "• Software Architect\n"
        response += "• DevOps Engineer\n"
        response += "• Technical Lead\n"
        response += "• Product Manager (technical)\n\n"
        
        response += "**Final Preparation:**\n"
        response += "• Build comprehensive software portfolio\n"
        response += "• Contribute to large open-source projects\n"
        response += "• Master system design interviews\n"
        response += "• Learn industry tools and practices"
        
        return response

    def _handle_data_science_course_query(self, course_code: str, query: str) -> str:
        """Handle Data Science course queries with description first, then optional learning outcomes"""
        
        # Load knowledge graph to get course details
        knowledge_graph = self.smart_ai_engine.knowledge_graph
        
        # All Data Science courses to check against
        ds_courses = {}
        
        # Add courses from different DS sections
        if "tracks" in knowledge_graph and "Data Science" in knowledge_graph["tracks"]:
            ds_track = knowledge_graph["tracks"]["Data Science"]
            
            # Ethics selective courses
            if "ethics_selective" in ds_track:
                for course in ds_track["ethics_selective"]["available_courses"]:
                    ds_courses[course["code"]] = course
            
            # Statistics selective courses  
            if "statistics_selective" in ds_track:
                for course in ds_track["statistics_selective"]["available_courses"]:
                    ds_courses[course["code"]] = course
            
            # Capstone courses
            if "capstone_experience" in ds_track:
                for course in ds_track["capstone_experience"]["available_courses"]:
                    ds_courses[course["code"]] = course
            
            # CS electives
            if "cs_electives_requirement" in ds_track:
                for course in ds_track["cs_electives_requirement"]["available_courses"]:
                    ds_courses[course["code"]] = course
        
        # Also check main courses section for DS core courses
        if "courses" in knowledge_graph:
            ds_core_codes = ["CS 25300", "STAT 24200", "CS 37300", "CS 44000", "CS 38003", "STAT 35500", "STAT 41600", "STAT 41700"]
            for code in ds_core_codes:
                normalized_code = code.replace(" ", "")
                for course_key, course_data in knowledge_graph["courses"].items():
                    if course_key == normalized_code or course_data.get("title", "").replace(" ", "").upper() == code.replace(" ", "").upper():
                        ds_courses[code] = course_data
                        break
        
        # Normalize the input course code
        normalized_code = course_code.upper().replace(" ", "")
        
        # Find matching course
        found_course = None
        found_code = None
        
        for code, course_data in ds_courses.items():
            if code.replace(" ", "").upper() == normalized_code:
                found_course = course_data
                found_code = code
                break
        
        if not found_course:
            return f"I don't have information about {course_code} in the Data Science curriculum. Could you check the course code?"
        
        # Check if user is asking specifically about learning outcomes
        learning_query_keywords = ["learn", "outcome", "objectives", "goals", "skills", "what you learn", "what do you learn"]
        wants_learning_outcomes = any(keyword in query.lower() for keyword in learning_query_keywords)
        
        # Build response starting with description
        response = f"**{found_code} - {found_course.get('title', 'Course Title')}** ({found_course.get('credits', 3)} credits)\n\n"
        
        if "description" in found_course:
            response += f"{found_course['description']}\n\n"
        
        # Add any special notes
        if "satisfies" in found_course:
            response += f"*This course satisfies: {found_course['satisfies']}*\n\n"
        
        if "prerequisite_note" in found_course:
            response += f"*Prerequisite: {found_course['prerequisite_note']}*\n\n"
        
        if "requirements" in found_course:
            response += f"*Requirements:*\n"
            for req in found_course["requirements"]:
                response += f"• {req}\n"
            response += "\n"
        
        # If user specifically asked about learning outcomes OR what they learn, show them immediately
        if wants_learning_outcomes and "learning_outcomes" in found_course:
            response += f"**Learning Outcomes:**\n"
            for outcome in found_course["learning_outcomes"]:
                response += f"• {outcome}\n"
        
        # If user didn't specifically ask about learning outcomes, offer to show them
        elif "learning_outcomes" in found_course and not wants_learning_outcomes:
            response += "Would you like to know the learning outcomes for this course?"
        
        return response

    def _handle_cs_minor_planning(self, query: str, context: ConversationContext, intent: Dict[str, Any]) -> str:
        """Handle CS minor planning queries using AI and knowledge base"""
        
        try:
            # Extract student context
            extracted = context.extracted_context
            
            # Load CS minor knowledge from the knowledge base
            cs_minor_data = None
            try:
                if hasattr(self, 'knowledge_graph') and self.knowledge_graph:
                    cs_minor_data = self.knowledge_graph.get("cs_minor", {})
            except Exception as e:
                self.logger.error(f"Error loading CS minor data: {e}")
            
            # Build comprehensive context for AI response
            minor_context = {
                "query": query,
                "student_year": extracted.get("current_year", "unknown"),
                "completed_courses": extracted.get("completed_courses", []),
                "current_courses": extracted.get("current_courses", []),
                "major": extracted.get("major", "unknown"),
                "concerns": extracted.get("concerns", []),
                "conversation_history": context.conversation_history[-3:] if context.conversation_history else []
            }
            
            # Use AI response generator if available
            if self.ai_response_generator:
                return self.ai_response_generator.generate_cs_minor_response(query, minor_context, cs_minor_data)
            
            # Fallback to direct Gemini if available
            if self.Gemini_available and self.gemini_model:
                return self._generate_ai_cs_minor_response(query, minor_context, cs_minor_data)
            
            # Ultimate fallback - basic response using knowledge base
            return self._fallback_cs_minor_response(query, minor_context, cs_minor_data)
            
        except Exception as e:
            self.logger.error(f"Error in CS minor planning handler: {e}")
            return "I can help you with CS minor planning, but I'm having trouble accessing the complete information right now. For CS minor requirements, you need to complete 5 CS courses with minimum C grades, taking courses only in off-peak terms. Please consult with your academic advisor for detailed planning."
    
    def _generate_ai_cs_minor_response(self, query: str, minor_context: Dict, cs_minor_data: Dict) -> str:
        """Generate AI response for CS minor queries"""
        
        # Get comprehensive system prompt
        system_prompt = get_comprehensive_system_prompt()
        
        user_prompt = f"""
        Student Query: "{query}"
        
        Student Context:
        {json.dumps(minor_context, indent=2)}
        
        CS Minor Knowledge Available:
        {json.dumps(cs_minor_data, indent=2) if cs_minor_data else "Basic CS minor information available"}
        
        Provide a comprehensive, personalized response about CS minor planning that:
        1. Addresses the student's specific question
        2. Uses their academic context (year, completed courses, major)
        3. Explains peak/off-peak scheduling constraints
        4. Provides specific course recommendations based on their situation
        5. Includes realistic timeline planning
        6. Mentions important policies and restrictions
        7. Uses natural conversational language without markdown formatting
        8. Encourages follow-up questions
        """
        
        try:
            response = self.gemini_model.chat_completion_with_retry(
                ,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                ,
                
            )
            return response
        except Exception as e:
            self.logger.error(f"Error generating AI CS minor response: {e}")
            return self._fallback_cs_minor_response(query, minor_context, cs_minor_data)
    
    def _fallback_cs_minor_response(self, query: str, minor_context: Dict, cs_minor_data: Dict) -> str:
        """Fallback CS minor response when AI is not available"""
        
        response = f"For CS minor planning, here are the key requirements:\n\n"
        
        if cs_minor_data and 'course_structure' in cs_minor_data:
            structure = cs_minor_data['course_structure']
            
            # Course structure
            response += f"• Total required: {structure.get('total_required', 5)} CS courses exactly\n"
            response += f"• Minimum grade: {cs_minor_data.get('minimum_grade', 'C')} in all courses (C- not accepted)\n"
            response += f"• CRITICAL: Taking more than 5 courses means NO minor awarded\n\n"
            
            # Compulsory courses
            if 'compulsory_courses' in structure:
                comp = structure['compulsory_courses']
                response += f"COMPULSORY COURSES ({comp.get('count', 3)} required):\n"
                for course in comp.get('required', []):
                    response += f"• {course.get('code', 'Unknown')}: {course.get('title', 'Unknown Title')}\n"
                response += "\n"
            
            # Electives
            if 'elective_courses' in structure:
                elec = structure['elective_courses']
                response += f"ELECTIVE COURSES ({elec.get('count', 2)} required):\n"
                response += f"• {elec.get('selection_rule', 'Choose additional courses')}\n"
                
                # Strong recommendation
                if 'strong_recommendation' in elec:
                    rec = elec['strong_recommendation']
                    response += f"• STRONGLY RECOMMEND: {rec.get('course', 'CS 25100')} - {rec.get('note', 'Builds foundation for advanced courses')}\n"
                response += "\n"
            
            # Course access
            response += f"• Course access: OFF-PEAK terms only\n"
            response += f"• Registration: CS majors have priority, minors get space-available access\n\n"
            
            if 'peak_off_peak_schedule' in cs_minor_data:
                schedule = cs_minor_data['peak_off_peak_schedule'].get('schedule', {})
                response += "Peak/Off-Peak Schedule:\n"
                for semester, courses in schedule.items():
                    response += f"• {semester.title()}: "
                    off_peak_courses = [course for course, status in courses.items() if status == "OFF-PEAK"]
                    if off_peak_courses:
                        response += f"Available - {', '.join(off_peak_courses)}\n"
                    else:
                        response += "Limited availability\n"
                response += "\n"
        else:
            # Basic fallback
            response += "• 5 CS courses required with minimum C grade\n"
            response += "• Must take courses in off-peak terms only\n"
            response += "• Summer semester: all CS courses available\n"
            response += "• Fall/Spring: limited course availability\n\n"
        
        # Add personalized advice based on context
        student_year = minor_context.get("student_year", "unknown")
        if student_year != "unknown":
            response += f"As a {student_year}, I recommend starting with foundation courses like CS 18000 if you haven't taken it yet.\n\n"
        
        response += "Important: Work closely with your academic advisor to plan your minor and ensure you understand the off-peak scheduling constraints. Space is not guaranteed even in off-peak terms."
        
        return response

def main():
    """Test the intelligent conversation manager"""
    manager = IntelligentConversationManager()
    
    # Test conversations
    test_queries = [
        "I'm a sophomore in CS, completed CS 18000 and CS 18200, want to graduate early",
        "What track should I choose if I want to work in AI?",
        "I failed CS 25100, how does this affect my graduation?",
        "What courses should I take next semester?",
        "I want to CODO into CS, what are the requirements?"
    ]
    
    session_id = "test_session"
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print(f"{'='*50}")
        response = manager.process_query(session_id, query)
        print(response)

if __name__ == "__main__":
    main()