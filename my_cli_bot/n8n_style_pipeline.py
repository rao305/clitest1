#!/usr/bin/env python3
"""
N8N-Style Knowledge Pipeline
Visual workflow: Query → Parse → Knowledge → AI → Format → Response
Each step is isolated and debuggable like N8N nodes
"""

import json
import os
import google.generativeai as genai
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import re
from dataclasses import dataclass
from enum import Enum

class NodeStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class WorkflowData:
    """Data passed between workflow nodes"""
    query: str
    entities: Dict[str, Any] = None
    knowledge: Dict[str, Any] = None
    ai_context: str = ""
    response: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = {}
        if self.knowledge is None:
            self.knowledge = {}
        if self.metadata is None:
            self.metadata = {"timestamp": datetime.now().isoformat()}

class WorkflowNode:
    """Base class for N8N-style workflow nodes"""
    
    def __init__(self, name: str):
        self.name = name
        self.status = NodeStatus.PENDING
        self.error_message = None
    
    def execute(self, data: WorkflowData) -> WorkflowData:
        """Execute the node and return modified data"""
        try:
            self.status = NodeStatus.PROCESSING
            print(f"🔄 [{self.name}] Processing...")
            
            result = self._process(data)
            
            self.status = NodeStatus.COMPLETED
            print(f"✅ [{self.name}] Completed")
            return result
            
        except Exception as e:
            self.status = NodeStatus.FAILED
            self.error_message = str(e)
            print(f"❌ [{self.name}] Failed: {e}")
            raise
    
    def _process(self, data: WorkflowData) -> WorkflowData:
        """Override this method in subclasses"""
        return data

class QueryParseNode(WorkflowNode):
    """Node 1: Parse query and extract entities"""
    
    def __init__(self):
        super().__init__("Query Parser")
    
    def _process(self, data: WorkflowData) -> WorkflowData:
        query = data.query.lower()
        
        entities = {
            "course_codes": self._extract_course_codes(data.query),
            "track_names": self._extract_tracks(query),
            "intent": self._classify_intent(query),
            "student_context": self._extract_student_context(query),
            "keywords": self._extract_keywords(query)
        }
        
        data.entities = entities
        data.metadata["parsing_completed"] = True
        
        print(f"   📊 Extracted entities: {entities}")
        return data
    
    def _extract_course_codes(self, query: str) -> List[str]:
        course_pattern = re.compile(r'(cs|ma|math|stat|phys|engr)\s*(\d{5}|\d{3,4})', re.IGNORECASE)
        matches = course_pattern.findall(query)
        return [f"{match[0].upper()} {match[1]}" for match in matches]
    
    def _extract_tracks(self, query_lower: str) -> List[str]:
        tracks = []
        if any(term in query_lower for term in ["machine intelligence", "mi", "ai", "ml"]):
            tracks.append("Machine Intelligence")
        if any(term in query_lower for term in ["software engineering", "se", "software"]):
            tracks.append("Software Engineering")
        return tracks
    
    def _classify_intent(self, query_lower: str) -> str:
        if any(term in query_lower for term in ["what is", "tell me about", "describe"]):
            return "information_request"
        elif any(term in query_lower for term in ["prerequisite", "before taking"]):
            return "prerequisite_query"
        elif any(term in query_lower for term in ["graduation", "timeline", "plan"]):
            return "graduation_planning"
        elif any(term in query_lower for term in ["codo", "change major"]):
            return "codo_inquiry"
        elif any(term in query_lower for term in ["failed", "retake", "failing"]):
            return "failure_recovery"
        else:
            return "general_inquiry"
    
    def _extract_student_context(self, query_lower: str) -> Dict[str, Any]:
        context = {}
        
        # Extract year
        year_patterns = {
            "freshman": ["freshman", "1st year"],
            "sophomore": ["sophomore", "2nd year"], 
            "junior": ["junior", "3rd year"],
            "senior": ["senior", "4th year"]
        }
        
        for year, patterns in year_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                context["year"] = year
                break
        
        # Extract GPA
        gpa_match = re.search(r'(\d\.\d+)\s*gpa|gpa\s*(\d\.\d+)', query_lower)
        if gpa_match:
            context["gpa"] = float(gpa_match.group(1) or gpa_match.group(2))
        
        return context
    
    def _extract_keywords(self, query_lower: str) -> List[str]:
        keywords = []
        keyword_map = {
            "difficulty": ["hard", "difficult", "easy", "challenging"],
            "requirements": ["requirement", "need", "must take"],
            "timing": ["when", "semester", "year", "schedule"],
            "career": ["job", "career", "internship", "work"]
        }
        
        for category, terms in keyword_map.items():
            if any(term in query_lower for term in terms):
                keywords.append(category)
        
        return keywords

class KnowledgeRetrievalNode(WorkflowNode):
    """Node 2: Retrieve relevant knowledge from database"""
    
    def __init__(self, knowledge_file: str = "data/cs_knowledge_graph.json"):
        super().__init__("Knowledge Retrieval")
        self.knowledge_base = self._load_knowledge_base(knowledge_file)
    
    def _load_knowledge_base(self, knowledge_file: str) -> Dict[str, Any]:
        try:
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Could not load knowledge base: {e}")
            return {}
    
    def _process(self, data: WorkflowData) -> WorkflowData:
        entities = data.entities
        relevant_knowledge = {}
        
        # Retrieve course information
        if entities.get("course_codes"):
            relevant_knowledge["courses"] = {}
            for course_code in entities["course_codes"]:
                if course_code in self.knowledge_base.get("courses", {}):
                    relevant_knowledge["courses"][course_code] = self.knowledge_base["courses"][course_code]
                    print(f"   📚 Retrieved: {course_code}")
        
        # Retrieve track information
        if entities.get("track_names"):
            relevant_knowledge["tracks"] = {}
            for track in entities["track_names"]:
                if track in self.knowledge_base.get("tracks", {}):
                    relevant_knowledge["tracks"][track] = self.knowledge_base["tracks"][track]
                    print(f"   🎯 Retrieved: {track} track")
        
        # Retrieve based on intent
        intent = entities.get("intent")
        if intent == "prerequisite_query":
            relevant_knowledge["prerequisites"] = self.knowledge_base.get("prerequisites", {})
            print(f"   📋 Retrieved: Prerequisites data")
        elif intent == "codo_inquiry":
            relevant_knowledge["codo"] = self.knowledge_base.get("codo_requirements", {})
            print(f"   🔄 Retrieved: CODO requirements")
        elif intent == "graduation_planning":
            relevant_knowledge["graduation"] = self.knowledge_base.get("graduation_timelines", {})
            relevant_knowledge["requirements"] = self.knowledge_base.get("degree_requirements", {})
            print(f"   🎓 Retrieved: Graduation data")
        elif intent == "failure_recovery":
            relevant_knowledge["failure"] = self.knowledge_base.get("failure_recovery", {})
            print(f"   🚨 Retrieved: Failure recovery data")
        
        # Always include academic policies for context
        if self.knowledge_base.get("academic_policies"):
            relevant_knowledge["policies"] = self.knowledge_base["academic_policies"]
        
        data.knowledge = relevant_knowledge
        data.metadata["knowledge_retrieved"] = len(relevant_knowledge)
        
        print(f"   📚 Total knowledge sections: {len(relevant_knowledge)}")
        return data

class ContextBuilderNode(WorkflowNode):
    """Node 3: Build AI context from knowledge"""
    
    def __init__(self):
        super().__init__("Context Builder")
    
    def _process(self, data: WorkflowData) -> WorkflowData:
        context_parts = []
        
        # Add query context
        context_parts.append(f"STUDENT QUERY: {data.query}")
        context_parts.append("")
        
        # Add entity context
        if data.entities:
            context_parts.append(f"EXTRACTED INFORMATION:")
            for key, value in data.entities.items():
                if value:
                    context_parts.append(f"  {key}: {value}")
            context_parts.append("")
        
        # Add knowledge context
        if data.knowledge:
            context_parts.append("RELEVANT KNOWLEDGE BASE DATA:")
            
            for section_name, section_data in data.knowledge.items():
                context_parts.append(f"\n{section_name.upper()}:")
                
                if isinstance(section_data, dict):
                    for key, value in section_data.items():
                        if isinstance(value, dict):
                            context_parts.append(f"  {key}:")
                            for subkey, subvalue in value.items():
                                context_parts.append(f"    {subkey}: {str(subvalue)[:200]}")
                        else:
                            context_parts.append(f"  {key}: {str(value)[:300]}")
                else:
                    context_parts.append(f"  {str(section_data)[:500]}")
                
                context_parts.append("")
        
        data.ai_context = "\n".join(context_parts)
        data.metadata["context_built"] = True
        
        print(f"   📝 Context built: {len(data.ai_context)} characters")
        return data

class AIResponseNode(WorkflowNode):
    """Node 4: Generate AI response"""
    
    def __init__(self):
        super().__init__("AI Response Generator")
        
        # Initialize Gemini client
        self.gemini_model = None
        self.use_ai = False
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                self.gemini_model = genai.GenerativeModel('models/gemini-2.5-flash')
                self.use_ai = True
                print(f"   🤖 AI enabled")
            except Exception as e:
                print(f"   ⚠️ AI disabled: {e}")
    
    def _process(self, data: WorkflowData) -> WorkflowData:
        if self.use_ai and data.knowledge:
            response = self._generate_ai_response(data)
        else:
            response = self._generate_knowledge_response(data)
        
        data.response = response
        data.metadata["response_generated"] = True
        
        print(f"   💬 Response generated: {len(response)} characters")
        return data
    
    def _generate_ai_response(self, data: WorkflowData) -> str:
        prompt = f"""{data.ai_context}

INSTRUCTIONS:
1. You are BoilerAI, a knowledgeable Purdue CS academic advisor
2. Use ONLY the provided knowledge base information to answer
3. Be specific with course codes, requirements, and details
4. If information is missing, say so clearly
5. Write in a helpful, conversational tone
6. Include specific details like credits, prerequisites, timelines
7. Organize complex answers with clear sections

Provide a comprehensive, accurate response to the student's query:"""

        try:
            response = self.gemini_model.generate_content(
                ,
                prompt,
                ,
                
            )
            
            return response.text.strip()
            
        except Exception as e:
            print(f"   ⚠️ AI generation failed: {e}, using knowledge fallback")
            return self._generate_knowledge_response(data)
    
    def _generate_knowledge_response(self, data: WorkflowData) -> str:
        """Generate response using only knowledge base"""
        
        # Course information response
        if data.entities.get("course_codes") and "courses" in data.knowledge:
            response_parts = []
            for course_code in data.entities["course_codes"]:
                if course_code in data.knowledge["courses"]:
                    course_info = data.knowledge["courses"][course_code]
                    response_parts.append(f"{course_code} - {course_info.get('title', 'No title')}")
                    response_parts.append(f"Credits: {course_info.get('credits', 'N/A')}")
                    response_parts.append(f"Description: {course_info.get('description', 'No description available')}")
                    
                    if course_info.get('difficulty_rating'):
                        response_parts.append(f"Difficulty: {course_info['difficulty_rating']}/5.0")
                    
                    response_parts.append("")
            
            return "\n".join(response_parts) if response_parts else "Course information not found."
        
        # Track information response
        if data.entities.get("track_names") and "tracks" in data.knowledge:
            response_parts = []
            for track in data.entities["track_names"]:
                if track in data.knowledge["tracks"]:
                    track_info = data.knowledge["tracks"][track]
                    response_parts.append(f"{track} Track Information:")
                    response_parts.append(f"Description: {track_info.get('description', 'No description')}")
                    
                    if track_info.get("required_courses"):
                        response_parts.append("Required Courses:")
                        for course in track_info["required_courses"][:5]:  # Limit to 5
                            response_parts.append(f"  • {course}")
                    
                    response_parts.append("")
            
            return "\n".join(response_parts) if response_parts else "Track information not found."
        
        # General response
        available_info = list(data.knowledge.keys())
        if available_info:
            return f"I have information about: {', '.join(available_info)}. Please be more specific about what you'd like to know about Purdue CS."
        else:
            return "I have access to Purdue CS information but couldn't find specific data for your query. Please try rephrasing your question."

class ResponseFormatterNode(WorkflowNode):
    """Node 5: Format final response"""
    
    def __init__(self):
        super().__init__("Response Formatter")
    
    def _process(self, data: WorkflowData) -> WorkflowData:
        # Clean up response formatting
        response = data.response.strip()
        
        # Ensure proper spacing
        response = re.sub(r'\n{3,}', '\n\n', response)
        
        # Add timestamp to metadata
        data.metadata["response_formatted"] = True
        data.metadata["final_length"] = len(response)
        
        data.response = response
        
        print(f"   ✨ Response formatted: {len(response)} characters")
        return data

class N8NStylePipeline:
    """Main N8N-style pipeline orchestrator"""
    
    def __init__(self, knowledge_file: str = "data/cs_knowledge_graph.json"):
        # Initialize workflow nodes
        self.nodes = [
            QueryParseNode(),
            KnowledgeRetrievalNode(knowledge_file),
            ContextBuilderNode(),
            AIResponseNode(),
            ResponseFormatterNode()
        ]
        
        print(f"🚀 N8N-Style Pipeline initialized with {len(self.nodes)} nodes")
    
    def execute_workflow(self, query: str) -> Dict[str, Any]:
        """Execute the complete workflow"""
        
        print(f"\n🎯 Starting workflow for: {query}")
        print("=" * 60)
        
        # Initialize workflow data
        data = WorkflowData(query=query)
        
        try:
            # Execute each node in sequence
            for i, node in enumerate(self.nodes, 1):
                print(f"\nStep {i}/{len(self.nodes)}:")
                data = node.execute(data)
            
            # Return complete results
            return {
                "response": data.response,
                "entities": data.entities,
                "knowledge_sections": list(data.knowledge.keys()),
                "metadata": data.metadata,
                "success": True
            }
            
        except Exception as e:
            return {
                "response": f"Pipeline error: {str(e)}",
                "entities": {},
                "knowledge_sections": [],
                "metadata": {"error": str(e)},
                "success": False
            }
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get status of all nodes"""
        return {
            node.name: {
                "status": node.status.value,
                "error": node.error_message
            }
            for node in self.nodes
        }

def main():
    """Test the N8N-style pipeline"""
    pipeline = N8NStylePipeline()
    
    # Test queries
    test_queries = [
        "What is CS 18000?",
        "Tell me about the Machine Intelligence track", 
        "What are the CODO requirements?",
        "I'm a sophomore, what courses should I take next?",
        "What are the prerequisites for CS 25100?"
    ]
    
    print("🧪 Testing N8N-Style Knowledge Pipeline")
    print("=" * 60)
    
    for query in test_queries:
        result = pipeline.execute_workflow(query)
        print(f"\n💬 Final Response:\n{result['response']}")
        print(f"\n📊 Pipeline Status: {result['success']}")
        print("=" * 60)
    
    # Show pipeline status
    print("\n🔍 Final Pipeline Status:")
    for node_name, status in pipeline.get_pipeline_status().items():
        status_icon = "✅" if status['status'] == 'completed' else "❌"
        print(f"{status_icon} {node_name}: {status['status']}")

if __name__ == "__main__":
    main()