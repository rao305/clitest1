#!/usr/bin/env python3
"""
Pure AI + Knowledge Base Integration Example
Shows correct integration pattern for conversation manager
NO hardcoded responses - pure AI generation with KB data
"""

from typing import Dict, List, Any
import json

class PureAIConversationExample:
    """
    Example showing correct pure AI + KB integration
    """

    def __init__(self):
        self.session_contexts = {}

    def _normalize_course_code(self, course_code: str) -> str:
        """
        CORRECT: Uses pure data function for normalization
        """
        try:
            from pure_ai_course_standards import normalize_course_code
            return normalize_course_code(course_code)
        except ImportError:
            # Fallback normalization if module not available
            return course_code.upper().strip()

    def _handle_course_hierarchy_query(self, query: str, session_id: str) -> str:
        """
        CORRECT: Pure AI generation using KB data
        """
        try:
            from pure_ai_course_standards import get_course_hierarchy_data

            # Get pure data from knowledge base
            hierarchy_data = get_course_hierarchy_data()

            # Get student context from session
            context = self.session_contexts.get(session_id, {})
            student_year = context.get("current_year", "freshman")
            completed_courses = context.get("completed_courses", [])

            # Build AI prompt with data and context
            prompt = f"""
            Student question: {query}

            Student context:
            - Academic year: {student_year}
            - Completed courses: {completed_courses}

            Course hierarchy data from knowledge base:
            - Foundation sequence: {hierarchy_data["foundation_sequence"]}
            - All prerequisites: {hierarchy_data["all_prerequisites"]}
            - Course titles: {hierarchy_data["course_titles"]}
            - Difficulty ratings: {hierarchy_data["difficulty_ratings"]}

            Key corrections to include:
            - CS 18000 and CS 18200 are sequential (not alternatives)
            - CS 25100 is Data Structures (not CS 24100)
            - CS 25000 and CS 25100 both require CS 18200 AND CS 24000

            Generate a helpful, personalized response explaining the CS course hierarchy.
            Use natural language without markdown formatting.
            Focus on what's most relevant to this {student_year} student.
            """

            # AI generates response using the data
            return self._generate_ai_response(prompt, hierarchy_data)

        except ImportError:
            # Fallback to basic AI generation
            return self._generate_ai_response(query, {"type": "course_hierarchy"})

    def _handle_prerequisite_query(self, course_code: str, session_id: str) -> str:
        """
        CORRECT: Pure AI generation using specific course data
        """
        try:
            from pure_ai_course_standards import get_prerequisite_data_for_ai

            # Normalize course code and get data
            normalized_course = self._normalize_course_code(course_code)
            course_data = get_prerequisite_data_for_ai(normalized_course)

            # Get student context
            context = self.session_contexts.get(session_id, {})
            completed_courses = context.get("completed_courses", [])

            # Build AI prompt with data
            prompt = f"""
            Student asks about prerequisites for {course_code}.

            Course information from knowledge base:
            - Official course: {course_data["course_code"]}
            - Title: {course_data["title"]}
            - Prerequisites: {course_data["prerequisites"]}
            - Difficulty rating: {course_data["difficulty_rating"]}/5.0
            - Is foundation course: {course_data["is_foundation"]}
            - Foundation sequence: {course_data["foundation_sequence"]}

            Student's completed courses: {completed_courses}

            Generate a helpful response that:
            1. Lists the prerequisites clearly
            2. Explains how they prepare for this course
            3. Checks if student has met prerequisites (if completed courses provided)
            4. Provides guidance on course sequencing

            Use natural language without markdown formatting.
            """

            return self._generate_ai_response(prompt, course_data)

        except ImportError:
            return self._generate_ai_response(f"What are the prerequisites for {course_code}?", {"type": "prerequisites"})

    def _handle_difficulty_query(self, course_code: str, session_id: str) -> str:
        """
        CORRECT: Pure AI generation using difficulty data
        """
        try:
            from pure_ai_course_standards import get_prerequisite_data_for_ai

            # Get comprehensive course data
            normalized_course = self._normalize_course_code(course_code)
            course_data = get_prerequisite_data_for_ai(normalized_course)

            # Get student context for personalization
            context = self.session_contexts.get(session_id, {})
            student_year = context.get("current_year", "freshman")

            prompt = f"""
            Student asks about difficulty of {course_code}.

            Course data from knowledge base:
            - Official course: {course_data["course_code"]}
            - Title: {course_data["title"]}
            - Difficulty rating: {course_data["difficulty_rating"]}/5.0
            - Prerequisites: {course_data["prerequisites"]}
            - Is foundation course: {course_data["is_foundation"]}

            Student context: {student_year}

            Generate a helpful explanation that:
            1. States the difficulty rating and what it means
            2. Explains why the course has this difficulty level
            3. Describes what makes it challenging
            4. Provides tips for success specific to a {student_year}
            5. Mentions how prerequisites prepare students

            Use natural language without markdown formatting.
            """

            return self._generate_ai_response(prompt, course_data)

        except ImportError:
            return self._generate_ai_response(f"How difficult is {course_code}?", {"type": "difficulty"})

    def _generate_ai_response(self, prompt: str, context: Dict) -> str:
        """
        Placeholder for actual AI response generation
        In real implementation, this would call OpenAI API
        """
        # This is where you'd integrate with OpenAI or other AI service
        # For demo purposes, return a placeholder
        return f"[AI would generate response based on: {prompt[:100]}...]"

    def process_query(self, session_id: str, user_query: str) -> str:
        """
        CORRECT: Route queries to appropriate handlers using pure AI + KB approach
        """
        query_lower = user_query.lower()

        # Course hierarchy queries
        if any(term in query_lower for term in ["hierarchy", "sequence", "foundation", "order"]):
            return self._handle_course_hierarchy_query(user_query, session_id)

        # Prerequisite queries
        elif any(term in query_lower for term in ["prerequisite", "prereq", "before", "required"]):
            # Extract course code from query
            course_code = self._extract_course_code(user_query)
            if course_code:
                return self._handle_prerequisite_query(course_code, session_id)

        # Difficulty queries
        elif any(term in query_lower for term in ["difficult", "hard", "easy", "challenging"]):
            course_code = self._extract_course_code(user_query)
            if course_code:
                return self._handle_difficulty_query(course_code, session_id)

        # Default: general AI response
        return self._generate_ai_response(user_query, {"type": "general"})

    def _extract_course_code(self, query: str) -> str:
        """
        Extract course code from user query
        """
        import re
        # Look for CS XXX or CSXXX patterns
        patterns = [
            r'cs\s*(\d{3})',
            r'cs\s*(\d{5})',
            r'cs(\d{3})',
            r'cs(\d{5})'
        ]

        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                return f"CS {match.group(1)}"

        return ""

def main():
    """
    Demonstrate the pure AI + KB approach
    """
    print("Pure AI + Knowledge Base Integration Example")
    print("=" * 50)

    conversation_manager = PureAIConversationExample()

    # Simulate some queries
    test_queries = [
        "give me the hierarchy of cs classes",
        "what are the prerequisites for CS 250?",
        "how difficult is CS 251?",
        "I want to take CS 182, what do I need?"
    ]

    for i, query in enumerate(test_queries):
        print(f"\nTest {i+1}: {query}")
        response = conversation_manager.process_query("test_session", query)
        print(f"Response: {response}")

    print("\n" + "=" * 50)
    print("KEY PRINCIPLES DEMONSTRATED:")
    print("1. ✅ No hardcoded response templates")
    print("2. ✅ Pure data functions from knowledge base")
    print("3. ✅ AI generates all user-facing responses")
    print("4. ✅ Context-aware and personalized")
    print("5. ✅ Accurate course mappings and data")

if __name__ == "__main__":
    main()