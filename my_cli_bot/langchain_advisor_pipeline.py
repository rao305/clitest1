#!/usr/bin/env python3
"""
Enhanced LangChain-based Academic Advisor Pipeline
Integrates with existing Boiler AI knowledge base and conversation management
"""

import json
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import os
from datetime import datetime
import logging

# LangChain imports
from langchain.llms import google.generativeai as genai
from langchain.embeddings import google.generativeai as genaiEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferWindowMemory

# Import existing components
from intelligent_conversation_manager import IntelligentConversationManager
from smart_ai_engine import SmartAIEngine, QueryIntent

@dataclass
class ToolDefinition:
    """Function calling tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str]

class EnhancedLangChainPipeline:
    """
    Enhanced academic advisor pipeline using LangChain with existing Boiler AI integration
    """
    
    def __init__(self, GEMINI_API_KEY: str):
        self.GEMINI_API_KEY = GEMINI_API_KEY
        os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
        
        # Initialize existing components
        self.conversation_manager = IntelligentConversationManager()
        self.smart_ai_engine = SmartAIEngine()
        
        # Initialize LangChain components
        self.llm = Gemini(, )
        self.embeddings = GeminiEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " "]
        )
        
        # Initialize vector store and tools
        self.vector_store = None
        self.tools = []
        self.agent = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize the pipeline
        self._initialize_vector_store()
        self._initialize_tools()
        self._initialize_chains()
        self._initialize_agent()
    
    def _initialize_vector_store(self):
        """Initialize FAISS vector store with existing knowledge base"""
        try:
            # Load existing knowledge base
            with open("data/cs_knowledge_graph.json", "r") as f:
                knowledge_data = json.load(f)
            
            # Create documents from knowledge base
            documents = []
            
            # Process courses
            for course_code, course_info in knowledge_data.get("courses", {}).items():
                # Create comprehensive document for each course
                content = f"""
                Course: {course_code} - {course_info.get('title', '')}
                Credits: {course_info.get('credits', 0)}
                Description: {course_info.get('description', '')}
                Course Type: {course_info.get('course_type', '')}
                Semester: {course_info.get('semester', '')}
                Difficulty: {course_info.get('difficulty_level', '')}
                """
                
                # Add additional context if available
                if 'difficulty_factors' in course_info:
                    content += f"Difficulty Factors: {', '.join(course_info['difficulty_factors'])}\n"
                if 'success_tips' in course_info:
                    content += f"Success Tips: {', '.join(course_info['success_tips'])}\n"
                
                doc = Document(
                    page_content=content,
                    metadata={
                        "course_code": course_code,
                        "course_type": course_info.get('course_type', ''),
                        "difficulty": course_info.get('difficulty_rating', 0),
                        "credits": course_info.get('credits', 0),
                        "source": "course_catalog"
                    }
                )
                documents.append(doc)
            
            # Process graduation requirements
            if "graduation_requirements" in knowledge_data:
                for track, requirements in knowledge_data["graduation_requirements"].items():
                    content = f"""
                    Track: {track}
                    Requirements: {json.dumps(requirements, indent=2)}
                    """
                    doc = Document(
                        page_content=content,
                        metadata={
                            "track": track,
                            "type": "graduation_requirements",
                            "source": "requirements"
                        }
                    )
                    documents.append(doc)
            
            # Split documents into chunks
            split_docs = self.text_splitter.split_documents(documents)
            
            # Create vector store
            self.vector_store = FAISS.from_documents(split_docs, self.embeddings)
            self.logger.info(f"Initialized vector store with {len(split_docs)} document chunks")
            
        except Exception as e:
            self.logger.error(f"Error initializing vector store: {e}")
            # Create empty vector store
            self.vector_store = FAISS.from_texts(["Empty"], self.embeddings)
    
    def _initialize_tools(self):
        """Initialize function calling tools"""
        
        # Tool definitions matching the architectural requirements
        self.tool_definitions = [
            ToolDefinition(
                name="getCourseInfo",
                description="Fetch official data for a given course code",
                parameters={
                    "type": "object",
                    "properties": {"courseCode": {"type": "string"}},
                    "required": ["courseCode"]
                },
                required=["courseCode"]
            ),
            ToolDefinition(
                name="getPrerequisites", 
                description="List prerequisites for a course",
                parameters={
                    "type": "object",
                    "properties": {"courseCode": {"type": "string"}},
                    "required": ["courseCode"]
                },
                required=["courseCode"]
            ),
            ToolDefinition(
                name="getDegreePlan",
                description="Generate a semester-by-semester degree plan",
                parameters={
                    "type": "object",
                    "properties": {
                        "major": {"type": "string"},
                        "entryTerm": {"type": "string", "enum": ["Fall", "Spring", "Summer"]},
                        "entryYear": {"type": "integer"}
                    },
                    "required": ["major", "entryTerm", "entryYear"]
                },
                required=["major", "entryTerm", "entryYear"]
            ),
            ToolDefinition(
                name="analyzeGraduationFeasibility",
                description="Analyze feasibility of early or delayed graduation",
                parameters={
                    "type": "object", 
                    "properties": {
                        "currentYear": {"type": "string"},
                        "completedCourses": {"type": "array", "items": {"type": "string"}},
                        "targetGraduation": {"type": "string"},
                        "gpa": {"type": "number"}
                    },
                    "required": ["currentYear", "targetGraduation"]
                },
                required=["currentYear", "targetGraduation"]
            )
        ]
        
        # Create LangChain tools
        self.tools = [
            Tool(
                name="getCourseInfo",
                description="Get detailed information about a specific course",
                func=self._get_course_info
            ),
            Tool(
                name="getPrerequisites",
                description="Get prerequisites for a specific course",
                func=self._get_prerequisites
            ),
            Tool(
                name="getDegreePlan", 
                description="Generate a degree plan for a student",
                func=self._get_degree_plan
            ),
            Tool(
                name="analyzeGraduationFeasibility",
                description="Analyze graduation timeline feasibility",
                func=self._analyze_graduation_feasibility
            ),
            Tool(
                name="searchKnowledgeBase",
                description="Search the knowledge base for relevant information",
                func=self._search_knowledge_base
            )
        ]
        
        self.logger.info(f"Initialized {len(self.tools)} tools")
    
    def _initialize_chains(self):
        """Initialize LangChain chains for intent classification and entity extraction"""
        
        # Intent classification chain
        intent_template = PromptTemplate(
            input_variables=["query"],
            template="""
            Classify the following query into one of these categories:
            - COURSE_INFO: asking about specific course details
            - PREREQUISITES: asking about course prerequisites  
            - DEGREE_PLAN: asking about graduation planning or course sequences
            - GRADUATION_ANALYSIS: asking about early/delayed graduation feasibility
            - TRACK_GUIDANCE: asking about track selection or requirements
            - FALLBACK: general academic questions
            
            Query: {query}
            
            Respond with only the category name.
            """
        )
        
        self.intent_chain = LLMChain(
            llm=self.llm,
            prompt=intent_template,
            output_key="intent"
        )
        
        # Entity extraction chain
        entity_template = PromptTemplate(
            input_variables=["query", "intent"],
            template="""
            Extract relevant entities from this query based on the intent.
            
            Query: {query}
            Intent: {intent}
            
            Extract and format as JSON:
            - For COURSE_INFO/PREREQUISITES: {{"courseCode": "CS12345"}}
            - For DEGREE_PLAN: {{"major": "Computer Science", "entryTerm": "Fall", "entryYear": 2024}}
            - For GRADUATION_ANALYSIS: {{"currentYear": "sophomore", "targetGraduation": "3 years", "gpa": 3.5}}
            
            If entities cannot be extracted, return {{"requires_clarification": true}}
            
            JSON:
            """
        )
        
        self.entity_chain = LLMChain(
            llm=self.llm,
            prompt=entity_template,
            output_key="entities"
        )
        
        self.logger.info("Initialized intent and entity extraction chains")
    
    def _initialize_agent(self):
        """Initialize LangChain agent with tools and memory"""
        memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            k=5,
            return_messages=True
        )
        
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=True,
            max_iterations=3
        )
        
        self.logger.info("Initialized conversational agent")
    
    def _get_course_info(self, course_code: str) -> str:
        """Get course information using existing smart AI engine"""
        try:
            # Use existing conversation manager to get course info
            session_id = "langchain_session"
            query = f"Tell me about course {course_code}"
            
            response = self.conversation_manager.process_query(session_id, query)
            return response.get("response", "Course information not found")
            
        except Exception as e:
            self.logger.error(f"Error getting course info: {e}")
            return f"Error retrieving course information for {course_code}"
    
    def _get_prerequisites(self, course_code: str) -> str:
        """Get course prerequisites"""
        try:
            # Load knowledge base and get prerequisites
            with open("data/cs_knowledge_graph.json", "r") as f:
                knowledge_data = json.load(f)
            
            course_info = knowledge_data.get("courses", {}).get(course_code.upper(), {})
            prerequisites = course_info.get("prerequisites", [])
            
            if prerequisites:
                return f"Prerequisites for {course_code}: {', '.join(prerequisites)}"
            else:
                return f"No prerequisites found for {course_code}"
                
        except Exception as e:
            self.logger.error(f"Error getting prerequisites: {e}")
            return f"Error retrieving prerequisites for {course_code}"
    
    def _get_degree_plan(self, major: str, entry_term: str = "Fall", entry_year: int = 2024) -> str:
        """Generate degree plan using existing graduation planner"""
        try:
            if self.conversation_manager.graduation_planner:
                # Create a student profile for planning
                profile = {
                    "major": major,
                    "entry_term": entry_term,
                    "entry_year": entry_year,
                    "current_year": "freshman"
                }
                
                # Use existing graduation planner
                plan = self.conversation_manager.graduation_planner.generate_comprehensive_plan(profile)
                return f"Degree plan generated for {major} starting {entry_term} {entry_year}: {plan}"
            else:
                return "Graduation planner not available"
                
        except Exception as e:
            self.logger.error(f"Error generating degree plan: {e}")
            return f"Error generating degree plan: {e}"
    
    def _analyze_graduation_feasibility(self, current_year: str, target_graduation: str, **kwargs) -> str:
        """Analyze graduation feasibility"""
        try:
            if self.conversation_manager.academic_advisor:
                # Use existing academic advisor for analysis
                student_profile = {
                    "current_year": current_year,
                    "target_graduation": target_graduation,
                    **kwargs
                }
                
                analysis = "Graduation feasibility analysis would be performed here using existing advisor"
                return analysis
            else:
                return "Academic advisor not available for feasibility analysis"
                
        except Exception as e:
            self.logger.error(f"Error analyzing graduation feasibility: {e}")
            return f"Error analyzing graduation feasibility: {e}"
    
    def _search_knowledge_base(self, query: str) -> str:
        """Search vector store for relevant information"""
        try:
            if self.vector_store:
                # Search vector store
                docs = self.vector_store.similarity_search(query, k=3)
                
                # Combine results
                results = []
                for doc in docs:
                    results.append(f"Source: {doc.metadata.get('source', 'unknown')}\nContent: {doc.page_content[:200]}...")
                
                return "\n\n".join(results)
            else:
                return "Vector store not available"
                
        except Exception as e:
            self.logger.error(f"Error searching knowledge base: {e}")
            return f"Error searching knowledge base: {e}"
    
    def process_query(self, query: str, session_id: str = None) -> Dict[str, Any]:
        """
        Main query processing pipeline with intent classification and function calling
        """
        try:
            # Step 1: Intent classification
            intent_result = self.intent_chain.run(query=query)
            intent = intent_result.strip()
            
            self.logger.info(f"Classified intent: {intent}")
            
            # Step 2: Entity extraction
            entities_result = self.entity_chain.run(query=query, intent=intent)
            
            try:
                entities = json.loads(entities_result.strip())
            except:
                entities = {"requires_clarification": True}
            
            self.logger.info(f"Extracted entities: {entities}")
            
            # Step 3: Route to appropriate handler
            if entities.get("requires_clarification"):
                # Use agent for general conversation
                response = self.agent.run(query)
                return {
                    "intent": intent,
                    "entities": entities,
                    "response": response,
                    "method": "agent_conversation"
                }
            
            elif intent in ["COURSE_INFO", "PREREQUISITES", "DEGREE_PLAN", "GRADUATION_ANALYSIS"]:
                # Use function calling
                if intent == "COURSE_INFO":
                    course_code = entities.get("courseCode", "")
                    response = self._get_course_info(course_code)
                elif intent == "PREREQUISITES":
                    course_code = entities.get("courseCode", "")
                    response = self._get_prerequisites(course_code)
                elif intent == "DEGREE_PLAN":
                    response = self._get_degree_plan(
                        entities.get("major", "Computer Science"),
                        entities.get("entryTerm", "Fall"),
                        entities.get("entryYear", 2024)
                    )
                elif intent == "GRADUATION_ANALYSIS":
                    response = self._analyze_graduation_feasibility(**entities)
                
                return {
                    "intent": intent,
                    "entities": entities,
                    "response": response,
                    "method": "function_call"
                }
            
            else:
                # FALLBACK - use vector search + agent
                search_results = self._search_knowledge_base(query)
                enhanced_query = f"Context: {search_results}\n\nQuestion: {query}"
                response = self.agent.run(enhanced_query)
                
                return {
                    "intent": intent,
                    "entities": entities,
                    "response": response,
                    "method": "rag_agent",
                    "context": search_results
                }
        
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            return {
                "intent": "ERROR",
                "entities": {},
                "response": f"Error processing query: {e}",
                "method": "error"
            }
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions for API documentation"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self.tool_definitions
        ]

if __name__ == "__main__":
    # Test the pipeline
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Please set GEMINI_API_KEY environment variable")
        exit(1)
    
    pipeline = EnhancedLangChainPipeline(api_key)
    
    # Test queries
    test_queries = [
        "What is CS 18000?",
        "What are the prerequisites for CS 25000?", 
        "Create a degree plan for Computer Science starting Fall 2024",
        "Can I graduate in 3 years if I'm a sophomore?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = pipeline.process_query(query)
        print(f"Intent: {result['intent']}")
        print(f"Response: {result['response'][:200]}...")