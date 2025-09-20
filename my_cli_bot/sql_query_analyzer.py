#!/usr/bin/env python3
"""
SQL Query Approach for Academic Advisor
Demonstrates how natural language could be converted to SQL for more efficient data retrieval
"""

import re
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class QueryPlan:
    """Represents a parsed query plan with SQL components"""
    intent: str
    entities: List[str]
    filters: Dict[str, Any]
    sql_query: str
    parameters: List[Any]
    complexity_score: float

class NaturalLanguageToSQL:
    """
    Converts natural language academic queries to SQL queries
    for more efficient and precise data retrieval
    """
    
    def __init__(self, db_path: str = "purdue_cs_knowledge.db"):
        self.db_path = db_path
        self.intent_patterns = self._initialize_intent_patterns()
        self.entity_patterns = self._initialize_entity_patterns()
        
    def _initialize_intent_patterns(self) -> Dict[str, Dict]:
        """Define query intent patterns and their SQL templates"""
        return {
            "prerequisite_chain": {
                "keywords": ["prerequisite", "prereq", "required before", "need to take"],
                "sql_template": """
                WITH RECURSIVE prereq_chain AS (
                    SELECT course_code, prerequisite_code, 1 as level
                    FROM prerequisites 
                    WHERE course_code = ?
                    UNION ALL
                    SELECT p.course_code, p.prerequisite_code, pc.level + 1
                    FROM prerequisites p
                    JOIN prereq_chain pc ON p.course_code = pc.prerequisite_code
                    WHERE pc.level < 5
                )
                SELECT DISTINCT c.code, c.title, c.credits, pc.level
                FROM prereq_chain pc
                JOIN courses c ON c.code = pc.prerequisite_code
                ORDER BY pc.level, c.code
                """,
                "complexity": 0.8
            },
            
            "track_courses": {
                "keywords": ["track courses", "machine intelligence", "software engineering", "MI track", "SE track"],
                "sql_template": """
                SELECT c.code, c.title, c.credits, tr.requirement_type, t.display_name
                FROM courses c
                JOIN track_requirements tr ON c.code = tr.course_code
                JOIN tracks t ON t.id = tr.track_id
                WHERE t.name = ? OR t.display_name LIKE ?
                ORDER BY tr.requirement_type, c.code
                """,
                "complexity": 0.4
            },
            
            "course_search": {
                "keywords": ["course", "class", "cs", "math", "ma"],
                "sql_template": """
                SELECT c.code, c.title, c.credits, c.description, c.category
                FROM courses c
                WHERE c.code LIKE ? OR c.title LIKE ?
                ORDER BY c.code
                """,
                "complexity": 0.2
            },
            
            "graduation_timeline": {
                "keywords": ["graduate", "graduation", "timeline", "how long", "semesters"],
                "sql_template": """
                SELECT 
                    t.display_name,
                    COUNT(tr.course_code) as total_courses,
                    SUM(c.credits) as total_credits,
                    SUM(CASE WHEN tr.requirement_type = 'required' THEN 1 ELSE 0 END) as required_courses,
                    SUM(CASE WHEN tr.requirement_type = 'elective' THEN 1 ELSE 0 END) as elective_courses
                FROM tracks t
                LEFT JOIN track_requirements tr ON t.id = tr.track_id
                LEFT JOIN courses c ON c.code = tr.course_code
                WHERE t.name = ? OR t.display_name LIKE ?
                GROUP BY t.id, t.display_name
                """,
                "complexity": 0.6
            },
            
            "failure_impact": {
                "keywords": ["fail", "failed", "failing", "retake", "what if"],
                "sql_template": """
                WITH affected_courses AS (
                    SELECT DISTINCT p.course_code as affected_course
                    FROM prerequisites p
                    WHERE p.prerequisite_code = ?
                    UNION ALL
                    SELECT p2.course_code
                    FROM prerequisites p1
                    JOIN prerequisites p2 ON p1.course_code = p2.prerequisite_code
                    WHERE p1.prerequisite_code = ?
                )
                SELECT c.code, c.title, c.credits, 'directly_affected' as impact_type
                FROM affected_courses ac
                JOIN courses c ON c.code = ac.affected_course
                ORDER BY c.code
                """,
                "complexity": 0.7
            }
        }
    
    def _initialize_entity_patterns(self) -> Dict[str, str]:
        """Define patterns for extracting entities from queries"""
        return {
            "course_codes": r"\b(CS|MA|ECE|PHYS|CHEM|ENGL|MATH)\s*(\d{3,5})\b",
            "track_names": r"\b(machine intelligence|software engineering|MI|SE|AI|ML)\b",
            "semester_terms": r"\b(freshman|sophomore|junior|senior|fall|spring|summer)\b",
            "years": r"\b(\d{4}|\d+\s*year)\b",
            "gpa": r"\b(\d\.\d+)\b"
        }
    
    def parse_query(self, query: str) -> QueryPlan:
        """Parse natural language query into SQL query plan"""
        
        query_lower = query.lower()
        
        # Extract entities
        entities = self._extract_entities(query)
        
        # Determine intent
        intent, intent_data = self._classify_intent(query_lower)
        
        # Build filters
        filters = self._build_filters(query_lower, entities)
        
        # Generate SQL
        sql_query, parameters = self._generate_sql(intent, intent_data, entities, filters)
        
        # Calculate complexity
        complexity = self._calculate_complexity(intent_data, entities, filters)
        
        return QueryPlan(
            intent=intent,
            entities=entities,
            filters=filters,
            sql_query=sql_query,
            parameters=parameters,
            complexity_score=complexity
        )
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract entities like course codes, tracks, etc."""
        entities = []
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    entities.append(' '.join(match))
                else:
                    entities.append(match)
        
        return list(set(entities))
    
    def _classify_intent(self, query_lower: str) -> Tuple[str, Dict]:
        """Classify query intent based on keywords"""
        
        best_match = None
        best_score = 0
        
        for intent, data in self.intent_patterns.items():
            score = sum(1 for keyword in data["keywords"] if keyword in query_lower)
            if score > best_score:
                best_score = score
                best_match = (intent, data)
        
        if best_match:
            return best_match
        else:
            return "general_search", {"sql_template": "SELECT * FROM courses LIMIT 10", "complexity": 0.1}
    
    def _build_filters(self, query_lower: str, entities: List[str]) -> Dict[str, Any]:
        """Build filter conditions based on query analysis"""
        filters = {}
        
        # Academic level filters
        if any(term in query_lower for term in ["freshman", "first year"]):
            filters["academic_level"] = 1
        elif any(term in query_lower for term in ["sophomore", "second year"]):
            filters["academic_level"] = 2
        elif any(term in query_lower for term in ["junior", "third year"]):
            filters["academic_level"] = 3
        elif any(term in query_lower for term in ["senior", "fourth year"]):
            filters["academic_level"] = 4
        
        # Course difficulty filters
        if any(term in query_lower for term in ["easy", "simple", "basic"]):
            filters["difficulty"] = "low"
        elif any(term in query_lower for term in ["hard", "difficult", "challenging"]):
            filters["difficulty"] = "high"
        
        # Credit filters
        credit_matches = re.findall(r"(\d+)\s*credit", query_lower)
        if credit_matches:
            filters["credits"] = int(credit_matches[0])
        
        return filters
    
    def _generate_sql(self, intent: str, intent_data: Dict, entities: List[str], filters: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """Generate SQL query and parameters"""
        
        sql_template = intent_data.get("sql_template", "SELECT * FROM courses LIMIT 10")
        parameters = []
        
        # Fill in parameters based on intent
        if intent == "prerequisite_chain" and entities:
            # Look for course codes in entities
            course_code = next((e for e in entities if re.match(r"\w+\s+\d+", e)), "CS 18000")
            parameters = [course_code]
        
        elif intent == "track_courses":
            track_name = "machine_intelligence"  # default
            if any("software" in str(e).lower() for e in entities):
                track_name = "software_engineering"
            parameters = [track_name, f"%{track_name.replace('_', ' ')}%"]
        
        elif intent == "course_search" and entities:
            search_term = entities[0] if entities else "CS"
            parameters = [f"%{search_term}%", f"%{search_term}%"]
        
        elif intent == "failure_impact" and entities:
            failed_course = next((e for e in entities if re.match(r"\w+\s+\d+", e)), "CS 18000")
            parameters = [failed_course, failed_course]
        
        return sql_template, parameters
    
    def _calculate_complexity(self, intent_data: Dict, entities: List[str], filters: Dict[str, Any]) -> float:
        """Calculate query complexity score"""
        base_complexity = intent_data.get("complexity", 0.1)
        
        # Adjust for entities
        entity_factor = min(len(entities) * 0.1, 0.3)
        
        # Adjust for filters
        filter_factor = min(len(filters) * 0.1, 0.2)
        
        return min(base_complexity + entity_factor + filter_factor, 1.0)
    
    def execute_query(self, query_plan: QueryPlan) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(query_plan.sql_query, query_plan.parameters)
                results = [dict(row) for row in cursor.fetchall()]
                
                return results
        
        except Exception as e:
            print(f"SQL execution error: {e}")
            return []

# Example usage and comparison
def demonstrate_sql_approach():
    """Demonstrate SQL approach with example queries"""
    
    sql_analyzer = NaturalLanguageToSQL()
    
    example_queries = [
        "What are the prerequisites for CS 25100?",
        "Show me all Machine Intelligence track courses",
        "I failed CS 18000, what courses will be affected?",
        "How long does it take to graduate with SE track?",
        "What CS courses can I take as a sophomore?"
    ]
    
    print("🔍 SQL QUERY APPROACH DEMONSTRATION")
    print("=" * 60)
    
    for i, query in enumerate(example_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        
        query_plan = sql_analyzer.parse_query(query)
        
        print(f"   Intent: {query_plan.intent}")
        print(f"   Entities: {query_plan.entities}")
        print(f"   Complexity: {query_plan.complexity_score:.2f}")
        print(f"   SQL: {query_plan.sql_query.strip()[:100]}...")
        print(f"   Parameters: {query_plan.parameters}")

if __name__ == "__main__":
    demonstrate_sql_approach()