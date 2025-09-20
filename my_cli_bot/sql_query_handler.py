#!/usr/bin/env python3
"""
SQL Query Handler for Boiler AI
Converts natural language queries to SQL and executes them against the knowledge base
"""

import sqlite3
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager

class SQLQueryHandler:
    """
    Handles natural language to SQL query conversion and execution
    """
    
    def __init__(self, db_path: str = "data/purdue_cs_advisor.db"):
        self.db_path = db_path
        self.query_patterns = self._initialize_query_patterns()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column name access
        try:
            yield conn
        finally:
            conn.close()
    
    def _normalize_course_code(self, course_code: str) -> str:
        """Normalize course code to match database format (e.g., 'CS18000' -> 'CS 18000')"""
        if not course_code:
            return ''
        # Handle both "CS18000" and "CS 18000" formats
        import re
        return re.sub(r'([A-Z]+)(\d+)', r'\1 \2', course_code.upper().replace(' ', ''))
    
    def _initialize_query_patterns(self) -> Dict[str, Dict]:
        """Initialize query patterns for natural language parsing"""
        return {
            # Prerequisite queries
            'prerequisite_chain': {
                'patterns': [
                    r'(?:what (?:are )?(?:the )?)?(?:prerequisites?|prereqs?) (?:for |of )?([A-Z]{2} ?\d{5})',
                    r'(?:what )?(?:courses? )?(?:do i )?need (?:to take )?(?:before )?([A-Z]{2} ?\d{5})',
                    r'([A-Z]{2} ?\d{5}) (?:prerequisites?|prereqs?|requirements?)'
                ],
                'query_builder': self._build_prerequisite_query
            },
            
            # Course information queries
            'course_info': {
                'patterns': [
                    r'(?:tell me about |what is |info (?:about |on )?)([A-Z]{2} ?\d{5})',
                    r'([A-Z]{2} ?\d{5}) (?:description|info|details|information)',
                    r'describe ([A-Z]{2} ?\d{5})'
                ],
                'query_builder': self._build_course_info_query
            },
            
            # Major-specific queries (new for multi-major support)
            'major_requirements': {
                'patterns': [
                    r'(?:what (?:are )?(?:the )?)?(?:requirements?|courses?) (?:for |in )?(?:the )?(.+?) major',
                    r'(.+?) major (?:requirements?|courses?|classes?)',
                    r'show me (.+?) major (?:requirements?|courses?)',
                    r'(?:data science|computer science|cs|ds) (?:requirements?|courses?|major)',
                    r'requirements? for (.+?) degree',
                ],
                'query_builder': self._build_major_requirements_query
            },
            
            # CODO requirements queries (updated for multi-major)
            'codo_requirements': {
                'patterns': [
                    r'codo (?:requirements?|process|application)',
                    r'(?:how )?(?:to )?(?:change|switch) (?:to )?(?:cs |computer science|data science|ds)',
                    r'transfer (?:to )?(?:cs |computer science|data science|ds)',
                    r'change (?:to |from )(.+?) major'
                ],
                'query_builder': self._build_codo_requirements_query
            },
            
            # Track analysis queries
            'track_courses': {
                'patterns': [
                    r'(?:what )?(?:courses?|classes?) (?:are )?(?:in |for |required (?:for )?)?(?:the )?(.+?) track',
                    r'(.+?) track (?:courses?|classes?|requirements?)',
                    r'show me (.+?) track (?:courses?|requirements?)',
                    r'(?:show me |list )?(.+?) (?:track )?(?:requirements?|courses?|classes?)',
                    r'what (?:are )?(?:the )?(.+?) (?:track )?(?:requirements?|courses?)',
                    r'(.+?) specialization (?:courses?|requirements?)',
                    r'courses? (?:for |in |required for )?(.+?) specialization'
                ],
                'query_builder': self._build_track_courses_query
            },
            
            # Graduation timeline queries
            'graduation_timeline': {
                'patterns': [
                    r'(?:how )?(?:can i |to )?graduate (?:in )?(\d+(?:\.\d+)?) year',
                    r'(\d+(?:\.\d+)?) year graduation',
                    r'early graduation (?:in )?(\d+(?:\.\d+)?) year',
                    r'graduation (?:timeline|plan) (?:for )?(\d+(?:\.\d+)?) year',
                    r'early graduation (?:options?|choices?|paths?)',
                    r'graduation (?:options?|choices?|paths?)',
                    r'(?:fast|quick|accelerated) graduation',
                    r'graduate (?:early|faster|quickly)',
                    r'(?:can i |how to )graduate (?:in )?(?:less than |under )?(\d+) years?'
                ],
                'query_builder': self._build_graduation_timeline_query
            },
            
            # Failure impact queries
            'failure_impact': {
                'patterns': [
                    r'(?:what )?(?:happens )?(?:if )?(?:i )?fail(?:ed)? ([A-Z]{2} ?\d{5})',
                    r'([A-Z]{2} ?\d{5}) failure (?:impact|consequences?|effect)',
                    r'failing ([A-Z]{2} ?\d{5})',
                    r'(?:impact|consequences?) of failing ([A-Z]{2} ?\d{5})'
                ],
                'query_builder': self._build_failure_impact_query
            },
            
            # Course difficulty queries
            'course_difficulty': {
                'patterns': [
                    r'(?:how )?(?:hard|difficult) is ([A-Z]{2} ?\d{5})',
                    r'([A-Z]{2} ?\d{5}) difficulty',
                    r'difficulty (?:of |for )?([A-Z]{2} ?\d{5})'
                ],
                'query_builder': self._build_course_difficulty_query
            },
            
            
            # Course load queries
            'course_load': {
                'patterns': [
                    r'(?:how many )?(?:courses?|classes?) (?:can i take|should i take|per semester)',
                    r'course load (?:for )?(\w+)',
                    r'(\w+) course load',
                    r'credit (?:hour )?(?:limit|maximum|recommendations?)',
                    r'(?:how many )?(?:courses?|credits?) (?:can|should) (?:i take )?(?:as )?(?:a )?(\w+)',
                    r'(?:maximum|max) (?:courses?|credits?) (?:for )?(?:a )?(\w+)',
                    r'course (?:limits?|maximums?) (?:by|for) (?:year|level)',
                    r'credit (?:limits?|maximums?) (?:by|for) (?:year|level)'
                ],
                'query_builder': self._build_course_load_query
            },
            
            # General course search
            'course_search': {
                'patterns': [
                    r'(?:show me |list |find )?(?:all )?(\w+) (?:courses?|classes?)',
                    r'courses? (?:for |in )?(\w+)',
                    r'(\w+) (?:course|class) (?:list|options)',
                    r'what (?:courses?|classes?) (?:are available|can i take) (?:in |for )?(\w+)',
                    r'(?:available|offered) (\w+) (?:courses?|classes?)',
                    r'(\w+) (?:electives?|requirements?)',
                    r'(?:upper|lower) level (\w+) (?:courses?|classes?)'
                ],
                'query_builder': self._build_course_search_query
            },
            
            # Course comparison queries
            'course_comparison': {
                'patterns': [
                    r'(?:compare|difference between) ([A-Z]{2,4} ?\d{3,5}) (?:and|vs) ([A-Z]{2,4} ?\d{3,5})',
                    r'([A-Z]{2,4} ?\d{3,5}) (?:vs|versus) ([A-Z]{2,4} ?\d{3,5})',
                    r'which (?:is )?(?:harder|easier|better) ([A-Z]{2,4} ?\d{3,5}) or ([A-Z]{2,4} ?\d{3,5})',
                    r'should i take ([A-Z]{2,4} ?\d{3,5}) or ([A-Z]{2,4} ?\d{3,5})'
                ],
                'query_builder': self._build_course_comparison_query
            },
            
            # Course sequence queries
            'course_sequence': {
                'patterns': [
                    r'what (?:comes|is) (?:after|next) ([A-Z]{2,4} ?\d{3,5})',
                    r'(?:next|following) (?:course|class) after ([A-Z]{2,4} ?\d{3,5})',
                    r'([A-Z]{2,4} ?\d{3,5}) (?:sequence|progression|pathway)',
                    r'courses? that (?:follow|come after) ([A-Z]{2,4} ?\d{3,5})'
                ],
                'query_builder': self._build_course_sequence_query
            }
        }
    
    def classify_query(self, query: str) -> Tuple[str, Optional[str]]:
        """
        Classify the query type and extract key parameters
        Returns: (query_type, extracted_parameter)
        """
        query_lower = query.lower().strip()
        
        for query_type, config in self.query_patterns.items():
            for pattern in config['patterns']:
                match = re.search(pattern, query_lower, re.IGNORECASE)
                if match:
                    param = match.group(1) if match.groups() else None
                    return query_type, param
        
        return 'unknown', None
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query and return structured data
        """
        query_type, param = self.classify_query(query)
        
        if query_type == 'unknown':
            return {
                'type': 'unknown',
                'success': False,
                'error': 'Query pattern not recognized',
                'query_param': param,
                'data': {},
                'count': 0,
                'user_friendly_error': {
                    'query_type': 'unknown',
                    'param': param,
                    'error_msg': 'Query pattern not recognized',
                    'context': 'unknown_query',
                    'needs_ai_response': True
                }
            }
        
        try:
            # Build and execute the SQL query
            config = self.query_patterns[query_type]
            sql_query, params = config['query_builder'](param)
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql_query, params)
                results = cursor.fetchall()
                
                # Convert results to dictionaries
                data = [dict(row) for row in results] if results else []
                
                return {
                    'type': query_type,
                    'success': True,
                    'query_param': param,
                    'sql_query': sql_query,
                    'data': data,
                    'count': len(data)
                }
        
        except Exception as e:
            error_msg = str(e)
            user_friendly_error = self._generate_user_friendly_error(query_type, param, error_msg)
            
            return {
                'type': query_type,
                'success': False,
                'error': error_msg,
                'query_param': param,
                'data': {},
                'count': 0,
                'user_friendly_error': user_friendly_error
            }
    
    def _generate_user_friendly_error(self, query_type: str, param: Optional[str], error_msg: str) -> str:
        """Generate context for AI-powered error handling"""
        # Return structured context for AI to generate personalized error messages
        return {
            'query_type': query_type,
            'param': param,
            'error_msg': error_msg,
            'context': 'sql_error',
            'needs_ai_response': True
        }
    
    def _build_prerequisite_query(self, course_code: str) -> Tuple[str, List]:
        """Build SQL query for prerequisite chains"""
        normalized_course = self._normalize_course_code(course_code)
        
        # Recursive CTE for prerequisite chains
        query = """
            WITH RECURSIVE prereq_chain AS (
                -- Base case: direct prerequisites
                SELECT 
                    p.course_code,
                    p.prerequisite_code,
                    c.title as prerequisite_title,
                    c.credits as prerequisite_credits,
                    1 as level,
                    p.prerequisite_code as path
                FROM prerequisites p
                JOIN courses c ON p.prerequisite_code = c.code
                WHERE p.course_code = ?
                
                UNION ALL
                
                -- Recursive case: prerequisites of prerequisites
                SELECT 
                    pc.course_code,
                    p.prerequisite_code,
                    c.title as prerequisite_title,
                    c.credits as prerequisite_credits,
                    pc.level + 1,
                    pc.path || ' -> ' || p.prerequisite_code
                FROM prereq_chain pc
                JOIN prerequisites p ON pc.prerequisite_code = p.course_code
                JOIN courses c ON p.prerequisite_code = c.code
                WHERE pc.level < 5  -- Prevent infinite recursion
            )
            SELECT DISTINCT * FROM prereq_chain
            ORDER BY level, prerequisite_code
        """
        
        return query, [normalized_course]
    
    def _build_course_info_query(self, course_code: str) -> Tuple[str, List]:
        """Build SQL query for course information"""
        normalized_course = self._normalize_course_code(course_code)
        
        query = """
            SELECT 
                c.*,
                GROUP_CONCAT(cdf.factor_description, '|') as difficulty_factors,
                GROUP_CONCAT(cst.tip_description, '|') as success_tips,
                GROUP_CONCAT(cs.struggle_description, '|') as common_struggles
            FROM courses c
            LEFT JOIN course_difficulty_factors cdf ON c.code = cdf.course_code
            LEFT JOIN course_success_tips cst ON c.code = cst.course_code
            LEFT JOIN course_struggles cs ON c.code = cs.course_code
            WHERE c.code = ?
            GROUP BY c.id, c.code, c.title, c.credits, c.description, c.course_type, 
                     c.semester, c.is_critical, c.difficulty_level, c.difficulty_rating,
                     c.time_commitment, c.prerequisite_knowledge, c.created_at, c.updated_at
        """
        
        return query, [normalized_course]
    
    def _build_track_courses_query(self, track_name: str) -> Tuple[str, List]:
        """Build SQL query for track courses"""
        # Map common track name variations to database track codes
        track_mapping = {
            'machine intelligence': 'Machine Intelligence',
            'mi': 'Machine Intelligence',
            'artificial intelligence': 'Machine Intelligence',
            'ai': 'Machine Intelligence',
            'software engineering': 'Software Engineering',
            'se': 'Software Engineering',
            'software': 'Software Engineering'
        }
        
        track_code = track_mapping.get(track_name.lower(), track_name.title())
        
        query = """
            SELECT 
                t.name as track_name,
                tr.requirement_type,
                c.code,
                c.title,
                c.credits,
                c.description,
                c.difficulty_rating
            FROM tracks t
            JOIN track_requirements tr ON t.code = tr.track_code
            JOIN courses c ON tr.course_code = c.code
            WHERE t.code = ?
            ORDER BY tr.requirement_type, c.code
        """
        
        return query, [track_code]
    
    def _build_graduation_timeline_query(self, years: str) -> Tuple[str, List]:
        """Build SQL query for graduation timelines"""
        if years and years.isdigit():
            # Specific year mentioned
            target_years = float(years)
            query = """
                SELECT 
                    timeline_type,
                    total_years,
                    success_probability,
                    description,
                    requirements,
                    semester_plan
                FROM graduation_timelines
                WHERE total_years <= ? + 0.5 AND total_years >= ? - 0.5
                ORDER BY ABS(total_years - ?) ASC
            """
            return query, [target_years, target_years, target_years]
        else:
            # General query about graduation options/paths
            query = """
                SELECT 
                    timeline_type,
                    total_years,
                    success_probability,
                    description,
                    requirements,
                    semester_plan
                FROM graduation_timelines
                WHERE total_years > 0
                ORDER BY total_years ASC
            """
            return query, []
    
    def _build_failure_impact_query(self, course_code: str) -> Tuple[str, List]:
        """Build SQL query for failure impact analysis"""
        normalized_course = self._normalize_course_code(course_code)
        
        query = """
            SELECT 
                fr.failed_course_code,
                c.title as course_title,
                fr.delay_semesters,
                fr.affected_courses,
                fr.recovery_strategy,
                fr.summer_option,
                fr.graduation_impact
            FROM failure_recovery fr
            JOIN courses c ON fr.failed_course_code = c.code
            WHERE fr.failed_course_code = ?
        """
        
        return query, [normalized_course]
    
    def _build_course_difficulty_query(self, course_code: str) -> Tuple[str, List]:
        """Build SQL query for course difficulty information"""
        normalized_course = self._normalize_course_code(course_code)
        
        query = """
            SELECT 
                c.code,
                c.title,
                c.difficulty_level,
                c.difficulty_rating,
                c.time_commitment,
                GROUP_CONCAT(cdf.factor_description, '|') as difficulty_factors,
                GROUP_CONCAT(cst.tip_description, '|') as success_tips,
                GROUP_CONCAT(cs.struggle_description, '|') as common_struggles
            FROM courses c
            LEFT JOIN course_difficulty_factors cdf ON c.code = cdf.course_code
            LEFT JOIN course_success_tips cst ON c.code = cst.course_code
            LEFT JOIN course_struggles cs ON c.code = cs.course_code
            WHERE c.code = ?
            GROUP BY c.code
        """
        
        return query, [normalized_course]
    
    def _build_codo_requirements_query(self, param: Optional[str]) -> Tuple[str, List]:
        """Build SQL query for CODO requirements (now supports multiple majors)"""
        # Determine target major if specified
        if param:
            target_major = self._normalize_major_name(param)
        else:
            target_major = None
        
        if target_major:
            # Query for specific major CODO requirements
            query = """
                SELECT 
                    cr.requirement_type,
                    cr.requirement_key,
                    cr.requirement_value,
                    cr.description,
                    cr.is_mandatory,
                    m.name as major_name
                FROM codo_requirements cr
                LEFT JOIN majors m ON cr.major_code = m.code
                WHERE cr.major_code = ? OR cr.major_code IS NULL
                ORDER BY 
                    CASE cr.requirement_type 
                        WHEN 'gpa' THEN 1
                        WHEN 'course' THEN 2
                        WHEN 'math' THEN 3
                        ELSE 4
                    END,
                    cr.requirement_key
            """
            return query, [target_major]
        else:
            # Query for general CODO requirements (default to CS for backward compatibility)
            query = """
                SELECT 
                    cr.requirement_type,
                    cr.requirement_key,
                    cr.requirement_value,
                    cr.description,
                    cr.is_mandatory,
                    m.name as major_name
                FROM codo_requirements cr
                LEFT JOIN majors m ON cr.major_code = m.code
                WHERE cr.major_code = 'CS' OR cr.major_code IS NULL
                ORDER BY 
                    CASE cr.requirement_type 
                        WHEN 'gpa' THEN 1
                        WHEN 'course' THEN 2
                        WHEN 'math' THEN 3
                        ELSE 4
                    END,
                    cr.requirement_key
            """
            return query, []
    
    def _build_course_load_query(self, student_level: Optional[str]) -> Tuple[str, List]:
        """Build SQL query for course load guidelines"""
        if student_level:
            level_mapping = {
                'freshman': 'freshman',
                'fresh': 'freshman',
                '1st': 'freshman',
                'first': 'freshman',
                'sophomore': 'sophomore', 
                'soph': 'sophomore',
                '2nd': 'sophomore',
                'second': 'sophomore',
                'junior': 'junior',
                '3rd': 'junior',
                'third': 'junior',
                'senior': 'senior',
                '4th': 'senior',
                'fourth': 'senior',
                'summer': 'summer'
            }
            
            level = level_mapping.get(student_level.lower(), student_level.lower())
            
            query = """
                SELECT * FROM course_load_guidelines
                WHERE student_level = ?
            """
            return query, [level]
        else:
            query = """
                SELECT * FROM course_load_guidelines
                ORDER BY 
                    CASE student_level
                        WHEN 'freshman' THEN 1
                        WHEN 'sophomore' THEN 2
                        WHEN 'junior' THEN 3
                        WHEN 'senior' THEN 4
                        WHEN 'summer' THEN 5
                        ELSE 6
                    END
            """
            return query, []
    
    def _build_course_search_query(self, search_term: str) -> Tuple[str, List]:
        """Build SQL query for general course search"""
        # Map search terms to course types or other criteria
        search_mapping = {
            'foundation': ('course_type', 'foundation'),
            'core': ('course_type', 'foundation'),
            'track': ('course_type', 'track'),
            'elective': ('course_type', 'elective'),
            'critical': ('is_critical', True),
            'required': ('is_critical', True),
            'hard': ('difficulty_rating', '>= 4.0'),
            'difficult': ('difficulty_rating', '>= 4.0'),
            'easy': ('difficulty_rating', '<= 3.0'),
            'cs': ('code', 'LIKE', 'CS%')
        }
        
        search_key = search_term.lower() if search_term else ''
        
        if search_key in search_mapping:
            mapping = search_mapping[search_key]
            if len(mapping) == 3:  # Special LIKE case
                query = f"""
                    SELECT code, title, credits, description, difficulty_rating, course_type
                    FROM courses 
                    WHERE {mapping[0]} {mapping[1]} ?
                    ORDER BY code
                """
                return query, [mapping[2]]
            elif mapping[1] == '>= 4.0' or mapping[1] == '<= 3.0':
                operator = mapping[1]
                value = float(operator.split()[-1])
                op = operator.split()[0]
                query = f"""
                    SELECT code, title, credits, description, difficulty_rating, course_type
                    FROM courses 
                    WHERE {mapping[0]} {op} ?
                    ORDER BY difficulty_rating DESC
                """
                return query, [value]
            else:
                query = f"""
                    SELECT code, title, credits, description, difficulty_rating, course_type
                    FROM courses 
                    WHERE {mapping[0]} = ?
                    ORDER BY code
                """
                return query, [mapping[1]]
        else:
            # General search in title and description
            query = """
                SELECT code, title, credits, description, difficulty_rating, course_type
                FROM courses 
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY code
            """
            search_pattern = f'%{search_term}%'
            return query, [search_pattern, search_pattern]
    
    def _build_course_comparison_query(self, course1: str) -> Tuple[str, List]:
        """Build SQL query for course comparison"""
        # Extract both course codes from the pattern match - this is a simplified approach
        # In practice, we'd need to modify the pattern matching to capture both courses
        normalized_course1 = self._normalize_course_code(course1)
        
        query = """
            SELECT 
                c.code,
                c.title,
                c.credits,
                c.difficulty_rating,
                c.time_commitment,
                c.description,
                c.course_type
            FROM courses c
            WHERE c.code = ?
        """
        
        return query, [normalized_course1]
    
    def _build_course_sequence_query(self, course_code: str) -> Tuple[str, List]:
        """Build SQL query for course sequences"""
        normalized_course = self._normalize_course_code(course_code)
        
        # Find courses that have the given course as a prerequisite
        query = """
            SELECT 
                c.code,
                c.title,
                c.credits,
                c.course_type,
                c.semester
            FROM courses c
            JOIN prerequisites p ON c.code = p.course_code
            WHERE p.prerequisite_code = ?
            ORDER BY c.code
        """
        
        return query, [normalized_course]

    def get_query_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the query handler"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Table sizes
            cursor.execute("SELECT COUNT(*) FROM courses")
            course_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM prerequisites") 
            prereq_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tracks")
            track_count = cursor.fetchone()[0]
            
            return {
                'database_path': self.db_path,
                'total_courses': course_count,
                'total_prerequisites': prereq_count,
                'total_tracks': track_count,
                'supported_query_types': len(self.query_patterns),
                'query_types': list(self.query_patterns.keys())
            }
    
    def _build_major_requirements_query(self, major_name: str) -> Tuple[str, List]:
        """Build SQL query for major requirements"""
        # Map common major name variations to database major codes
        major_mapping = {
            'computer science': 'CS',
            'cs': 'CS',
            'data science': 'DS',
            'ds': 'DS',
            'artificial intelligence': 'AI',
            'ai': 'AI'
        }
        
        major_code = major_mapping.get(major_name.lower(), major_name.upper())
        
        query = """
            SELECT 
                m.name as major_name,
                mr.requirement_type,
                mr.category,
                c.code,
                c.title,
                c.credits,
                c.description,
                mr.min_grade,
                mr.notes
            FROM majors m
            JOIN major_requirements mr ON m.code = mr.major_code
            JOIN courses c ON mr.course_code = c.code
            WHERE m.code = ?
            ORDER BY 
                CASE mr.requirement_type 
                    WHEN 'required' THEN 1
                    WHEN 'elective' THEN 2
                    ELSE 3
                END,
                mr.category, c.code
        """
        
        return query, [major_code]
    
    def _normalize_major_name(self, major_input: str) -> str:
        """Normalize major name from CODO query"""
        major_mapping = {
            'cs': 'CS',
            'computer science': 'CS', 
            'data science': 'DS',
            'ds': 'DS',
            'artificial intelligence': 'AI',
            'ai': 'AI'
        }
        
        return major_mapping.get(major_input.lower(), 'CS')  # Default to CS

# Test the SQL query handler
if __name__ == "__main__":
    handler = SQLQueryHandler()
    
    # Test queries
    test_queries = [
        "What are the prerequisites for CS 25100?",
        "Tell me about CS 18000",
        "What courses are in the Machine Intelligence track?",
        "How can I graduate in 3 years?",
        "What happens if I fail CS 18000?",
        "How hard is CS 25200?",
        "What are the CODO requirements?",
        "How many courses can I take as a freshman?",
        "Show me all foundation courses"
    ]
    
    print("🧪 Testing SQL Query Handler\n")
    
    for query in test_queries:
        print(f"Query: {query}")
        result = handler.process_query(query)
        print(f"Type: {result['type']}")
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Results: {result['count']} records")
        print("---")
    
    # Performance stats
    print("\n📊 Performance Statistics:")
    stats = handler.get_query_performance_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")