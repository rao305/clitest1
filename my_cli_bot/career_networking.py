"""
Career Networking Module for Boiler AI
Integrates with Clado API for professional networking and career exploration
"""

import asyncio
import websockets
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import sqlite3
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CareerSearchResult:
    """Structure for career search results"""
    name: str
    title: str
    company: str
    location: str
    education: List[str]
    experience: List[str]
    profile_url: str
    relevance_score: float
    
@dataclass
class StudentCareerProfile:
    """Enhanced student profile for career networking"""
    student_id: str
    year: str
    track: str
    gpa_range: str
    career_interests: List[str]
    target_companies: List[str]
    preferred_locations: List[str]
    skills: List[str]
    
class CladoAPIClient:
    """WebSocket client for Clado API integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "wss://api.clado.ai/api/search/ws"
        self.websocket = None
        
    async def connect(self):
        """Establish WebSocket connection"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            self.websocket = await websockets.connect(
                self.base_url,
                extra_headers=headers,
                ping_interval=30,
                ping_timeout=10
            )
            logger.info("Connected to Clado API WebSocket")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Clado API: {e}")
            return False
            
    async def disconnect(self):
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from Clado API")
            
    async def search_professionals(self, query: str, filters: Dict = None, limit: int = 10) -> List[CareerSearchResult]:
        """Search for professionals using natural language query"""
        if not self.websocket:
            if not await self.connect():
                return []
                
        try:
            search_message = {
                "type": "search",
                "query": query,
                "limit": limit,
                "filters": filters or {}
            }
            
            await self.websocket.send(json.dumps(search_message))
            
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data.get("status") == "success":
                return self._parse_search_results(data.get("results", []))
            else:
                logger.error(f"Search failed: {data.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
            
    def _parse_search_results(self, results: List[Dict]) -> List[CareerSearchResult]:
        """Parse API results into structured format"""
        parsed_results = []
        
        for result in results:
            try:
                career_result = CareerSearchResult(
                    name=result.get("name", "Unknown"),
                    title=result.get("title", "Unknown"),
                    company=result.get("company", "Unknown"),
                    location=result.get("location", "Unknown"),
                    education=result.get("education", []),
                    experience=result.get("experience", []),
                    profile_url=result.get("profile_url", ""),
                    relevance_score=result.get("relevance_score", 0.0)
                )
                parsed_results.append(career_result)
            except Exception as e:
                logger.warning(f"Failed to parse result: {e}")
                continue
                
        return parsed_results

class CareerNetworkingEngine:
    """Main engine for career networking functionality"""
    
    def __init__(self, api_key: str, db_path: str = "purdue_cs_advisor.db"):
        self.api_client = CladoAPIClient(api_key)
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Initialize career networking database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Career search history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS career_searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                query TEXT,
                results_count INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Student career profiles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_career_profiles (
                student_id TEXT PRIMARY KEY,
                year TEXT,
                track TEXT,
                gpa_range TEXT,
                career_interests TEXT,
                target_companies TEXT,
                preferred_locations TEXT,
                skills TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Favorite professionals
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorite_professionals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                professional_name TEXT,
                company TEXT,
                title TEXT,
                profile_url TEXT,
                notes TEXT,
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def update_student_career_profile(self, student_id: str, profile_data: Dict):
        """Update student's career networking profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO student_career_profiles 
            (student_id, year, track, gpa_range, career_interests, target_companies, preferred_locations, skills)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_id,
            profile_data.get('year', ''),
            profile_data.get('track', ''),
            profile_data.get('gpa_range', ''),
            json.dumps(profile_data.get('career_interests', [])),
            json.dumps(profile_data.get('target_companies', [])),
            json.dumps(profile_data.get('preferred_locations', [])),
            json.dumps(profile_data.get('skills', []))
        ))
        
        conn.commit()
        conn.close()
        
    def get_student_career_profile(self, student_id: str) -> Optional[StudentCareerProfile]:
        """Retrieve student's career profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM student_career_profiles WHERE student_id = ?
        ''', (student_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return StudentCareerProfile(
                student_id=result[0],
                year=result[1],
                track=result[2],
                gpa_range=result[3],
                career_interests=json.loads(result[4]) if result[4] else [],
                target_companies=json.loads(result[5]) if result[5] else [],
                preferred_locations=json.loads(result[6]) if result[6] else [],
                skills=json.loads(result[7]) if result[7] else []
            )
        return None
        
    async def search_for_career_guidance(self, student_context: Dict, search_intent: str) -> Dict[str, Any]:
        """Main method for career-related searches"""
        student_id = student_context.get('session_id', 'anonymous')
        
        # Build personalized query based on student context and intent
        query = self._build_career_query(student_context, search_intent)
        
        # Add school filter for Purdue alumni
        filters = {"schools": ["Purdue University"]}
        
        # Perform search
        results = await self.api_client.search_professionals(query, filters, limit=5)
        
        # Log search
        self._log_search(student_id, query, len(results))
        
        # Format results for AI conversation
        return self._format_results_for_ai(results, search_intent, student_context)
        
    def _build_career_query(self, student_context: Dict, search_intent: str) -> str:
        """Build natural language query based on student context"""
        track = student_context.get('track', '')
        year = student_context.get('year', '')
        career_interests = student_context.get('career_interests', [])
        target_companies = student_context.get('target_companies', [])
        
        # Base query templates
        query_templates = {
            'alumni_search': "Computer science graduates from Purdue University",
            'career_exploration': "Professionals working in {domain}",
            'company_research': "People working at {companies}",
            'mentorship': "Senior {track} professionals who could mentor students",
            'industry_insights': "Professionals in {industry} with computer science background"
        }
        
        # Enhance query based on context
        if 'alumni' in search_intent.lower() or 'purdue' in search_intent.lower():
            base_query = query_templates['alumni_search']
        elif any(company in search_intent.lower() for company in ['google', 'microsoft', 'amazon', 'apple', 'meta']):
            base_query = query_templates['company_research']
        elif 'mentor' in search_intent.lower():
            base_query = query_templates['mentorship']
        else:
            base_query = query_templates['career_exploration']
            
        # Add track-specific terms
        if track == 'MI':
            domain_terms = "machine learning, artificial intelligence, data science"
        elif track == 'SE':
            domain_terms = "software engineering, software development, backend systems"
        else:
            domain_terms = "computer science, software development"
            
        # Format query with context
        if '{domain}' in base_query:
            query = base_query.format(domain=domain_terms)
        elif '{track}' in base_query:
            query = base_query.format(track=track)
        elif '{companies}' in base_query:
            companies = ', '.join(target_companies) if target_companies else 'tech companies'
            query = base_query.format(companies=companies)
        else:
            query = base_query
            
        # Add additional context
        if career_interests:
            query += f" interested in {', '.join(career_interests[:2])}"
            
        return query
        
    def _format_results_for_ai(self, results: List[CareerSearchResult], search_intent: str, student_context: Dict) -> Dict[str, Any]:
        """Format search results for AI conversation"""
        if not results:
            return {
                'success': False,
                'message': 'No professionals found matching your criteria.',
                'suggestions': self._get_search_suggestions(student_context)
            }
            
        # Format results for natural conversation
        formatted_results = []
        for result in results[:3]:  # Limit to top 3 for conversation
            formatted_results.append({
                'name': result.name,
                'title': result.title,
                'company': result.company,
                'location': result.location,
                'education_summary': self._summarize_education(result.education),
                'experience_summary': self._summarize_experience(result.experience),
                'relevance_note': self._generate_relevance_note(result, student_context)
            })
            
        return {
            'success': True,
            'results': formatted_results,
            'search_summary': f"Found {len(results)} professionals matching your interests",
            'search_intent': search_intent,
            'follow_up_suggestions': self._get_follow_up_suggestions(results, student_context)
        }
        
    def _summarize_education(self, education: List[str]) -> str:
        """Create concise education summary"""
        if not education:
            return "Education details not available"
        return education[0] if len(education) == 1 else f"{education[0]} and {len(education)-1} other degree(s)"
        
    def _summarize_experience(self, experience: List[str]) -> str:
        """Create concise experience summary"""
        if not experience:
            return "Experience details not available"
        return experience[0] if len(experience) == 1 else f"Currently: {experience[0]}"
        
    def _generate_relevance_note(self, result: CareerSearchResult, student_context: Dict) -> str:
        """Generate why this professional is relevant to the student"""
        track = student_context.get('track', '')
        notes = []
        
        if 'Purdue' in ' '.join(result.education):
            notes.append("Purdue alumnus")
        if track == 'MI' and any(term in result.title.lower() for term in ['ml', 'ai', 'data', 'machine']):
            notes.append("Machine Intelligence relevant")
        elif track == 'SE' and any(term in result.title.lower() for term in ['software', 'engineer', 'developer']):
            notes.append("Software Engineering relevant")
            
        return '; '.join(notes) if notes else "Relevant experience in CS field"
        
    def _get_search_suggestions(self, student_context: Dict) -> List[str]:
        """Provide search suggestions when no results found"""
        track = student_context.get('track', '')
        suggestions = [
            "Try searching for broader terms like 'software engineer' or 'computer science'",
            "Consider looking at professionals in related fields",
            "Search for Purdue CS alumni in general"
        ]
        
        if track == 'MI':
            suggestions.append("Try searching for 'data scientist' or 'AI researcher'")
        elif track == 'SE':
            suggestions.append("Try searching for 'backend developer' or 'systems engineer'")
            
        return suggestions
        
    def _get_follow_up_suggestions(self, results: List[CareerSearchResult], student_context: Dict) -> List[str]:
        """Suggest follow-up actions based on results"""
        suggestions = [
            "Would you like to search for professionals at specific companies?",
            "Should I look for more senior professionals who could serve as mentors?",
            "Would you like to explore different career paths in your track?"
        ]
        
        # Add specific suggestions based on results
        companies = list(set([r.company for r in results if r.company != "Unknown"]))
        if companies:
            suggestions.append(f"I found professionals at {', '.join(companies[:2])}. Want to explore more at these companies?")
            
        return suggestions
        
    def _log_search(self, student_id: str, query: str, results_count: int):
        """Log search for analytics and improvement"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO career_searches (student_id, query, results_count)
            VALUES (?, ?, ?)
        ''', (student_id, query, results_count))
        
        conn.commit()
        conn.close()
        
    async def cleanup(self):
        """Cleanup resources"""
        await self.api_client.disconnect()

# Main interface for integration with conversation manager
class CareerNetworkingInterface:
    """Simplified interface for integration with the main AI system"""
    
    def __init__(self, api_key: str):
        self.engine = CareerNetworkingEngine(api_key)
        
    async def process_career_query(self, student_context: Dict, query: str) -> Dict[str, Any]:
        """Process career-related queries and return formatted response"""
        try:
            # Determine search intent from query
            search_intent = self._classify_career_intent(query)
            
            # Perform search
            results = await self.engine.search_for_career_guidance(student_context, search_intent)
            
            return {
                'type': 'career_networking',
                'success': results['success'],
                'data': results,
                'response_type': 'conversational'
            }
            
        except Exception as e:
            logger.error(f"Career query processing error: {e}")
            return {
                'type': 'career_networking',
                'success': False,
                'error': 'Unable to process career search at this time',
                'response_type': 'error'
            }
            
    def _classify_career_intent(self, query: str) -> str:
        """Classify the type of career search intent"""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ['alumni', 'purdue graduates', 'purdue cs']):
            return 'alumni_search'
        elif any(term in query_lower for term in ['mentor', 'mentorship', 'guidance']):
            return 'mentorship'
        elif any(term in query_lower for term in ['company', 'work at', 'working at']):
            return 'company_research'
        elif any(term in query_lower for term in ['career path', 'industry', 'field']):
            return 'industry_insights'
        else:
            return 'career_exploration'
            
    async def cleanup(self):
        """Cleanup resources"""
        await self.engine.cleanup()