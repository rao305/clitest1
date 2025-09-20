#!/usr/bin/env python3
"""
Patch for intelligent_conversation_manager.py to use centralized course standards
"""

# PATCH: Updated normalize course code method using centralized standards
def get_fixed_normalize_course_code_method():
    """
    Returns the fixed _normalize_course_code method that should replace the existing one
    """
    code = '''
    def _normalize_course_code(self, course_code: str) -> str:
        """
        Normalize course codes to standard format using centralized course standards
        """
        # Import centralized standards
        try:
            from pure_ai_course_standards import normalize_course_code
            return normalize_course_code(course_code)
        except ImportError:
            # Fallback to local implementation if course_standards not available
            if not course_code:
                return ""

            # Handle common formats: CS 180 -> CS 18000, CS180 -> CS 18000
            course_code = course_code.upper().replace(" ", "")

            # Extract department and number
            import re
            match = re.match(r"([A-Z]+)(\\d+)", course_code)
            if not match:
                return course_code

            dept, num = match.groups()

            # Normalize CS course numbers with specific mappings for problematic courses
            if dept == "CS" and len(num) == 3:
                # Map specific old course numbers to correct current ones
                mapping = {
                    "180": "18000",  # CS 180 -> CS 18000 (Problem Solving and OOP)
                    "182": "18200",  # CS 182 -> CS 18200 (Foundations of CS)
                    "240": "24000",  # CS 240 -> CS 24000 (Programming in C)
                    "241": "25100",  # CS 241 -> CS 25100 (Data Structures, NOT CS 24100)
                    "250": "25000",  # CS 250 -> CS 25000 (Computer Architecture)
                    "251": "25100",  # CS 251 -> CS 25100 (Data Structures)
                    "252": "25200",  # CS 252 -> CS 25200 (Systems Programming)
                    "307": "30700",  # CS 307 -> CS 30700 (Database Systems)
                    "320": "35200",  # CS 320 -> CS 35200 (Operating Systems)
                }
                if num in mapping:
                    return f"{dept} {mapping[num]}"
                # Handle other 3-digit course codes using general pattern
                else:
                    return f"{dept} {num}00"

            # Normalize MA course numbers
            elif dept == "MA" and len(num) == 3:
                return f"{dept} {num}00"

            # Normalize STAT course numbers
            elif dept == "STAT" and len(num) == 3:
                return f"{dept} {num}00"

            # Return normalized format for 5-digit codes
            if len(num) == 5:
                return f"{dept} {num}"

            return f"{dept} {num}"
    '''
    return code

# PATCH: Updated course mention patterns using correct mappings
def get_fixed_course_mentions():
    """
    Returns the fixed course_mentions list with correct mappings
    """
    return [
        (r"cs\\s*180|cs180", "CS 18000"),  # CS 180 -> CS 18000
        (r"cs\\s*182|cs182", "CS 18200"),  # CS 182 -> CS 18200 (NOT CS 18000)
        (r"cs\\s*240|cs240", "CS 24000"),  # CS 240 -> CS 24000
        (r"cs\\s*241|cs241", "CS 25100"),  # CS 241 -> CS 25100 (Data Structures)
        (r"cs\\s*250|cs250", "CS 25000"),  # CS 250 -> CS 25000 (Computer Architecture)
        (r"cs\\s*251|cs251", "CS 25100"),  # CS 251 -> CS 25100 (Data Structures)
        (r"cs\\s*252|cs252", "CS 25200"),  # CS 252 -> CS 25200 (Systems Programming)
        (r"cs\\s*307|cs307", "CS 30700"),  # CS 307 -> CS 30700 (Database Systems)
        (r"cs\\s*320|cs320", "CS 35200"),  # CS 320 -> CS 35200 (Operating Systems)
        (r"ma\\s*161|ma161", "MA 16100"),
        (r"ma\\s*162|ma162", "MA 16200"),
        (r"ma\\s*261|ma261", "MA 26100"),
        (r"ma\\s*265|ma265", "MA 26500")
    ]

# PATCH: Updated to use data-only approach for difficulty ratings
def get_fixed_difficulty_approach():
    """
    Shows correct approach for difficulty queries using pure AI + KB data
    """
    code = '''
    def _handle_difficulty_query(self, course_code: str, context: ConversationContext) -> str:
        """
        CORRECT: Use pure data from KB + AI generation for difficulty explanations
        """
        try:
            from pure_ai_course_standards import get_prerequisite_data_for_ai

            # Get data-only from knowledge base
            course_data = get_prerequisite_data_for_ai(course_code)

            # Build AI prompt with data
            prompt = f"""
            Student asks about difficulty of {course_code}.

            Course data:
            - Official course: {course_data["course_code"]}
            - Title: {course_data["title"]}
            - Difficulty rating: {course_data["difficulty_rating"]}/5.0
            - Prerequisites: {course_data["prerequisites"]}
            - Foundation course: {course_data["is_foundation"]}

            Generate a helpful explanation of the course difficulty that includes:
            - The difficulty rating and what it means
            - Why the course has this difficulty level
            - Prerequisites that prepare students
            - Tips for success

            Use natural language without markdown formatting.
            """

            return self._generate_ai_response(prompt, course_data)
        except ImportError:
            return self._generate_ai_response(f"What is the difficulty of {course_code}?", {"type": "difficulty"})
    '''
    return code

# PATCH: Updated hierarchy query handling to use pure AI + KB data
def get_fixed_hierarchy_handling_method():
    """
    Returns the corrected approach for hierarchy queries using pure AI + KB data
    """
    code = '''
    def _handle_course_hierarchy_query(self, query: str, context: ConversationContext) -> str:
        """
        CORRECT: Use pure AI generation with accurate data from knowledge base
        """
        try:
            from pure_ai_course_standards import get_course_hierarchy_data

            # Get accurate data from knowledge base
            hierarchy_data = get_course_hierarchy_data()

            # Extract student context for personalization
            extracted = context.extracted_context
            current_year = extracted.get("current_year", "freshman")
            completed = extracted.get("completed_courses", [])

            # Build context for AI with accurate data
            ai_context = {
                "query": query,
                "student_year": current_year,
                "completed_courses": completed,
                "foundation_sequence": hierarchy_data["foundation_sequence"],
                "prerequisites": hierarchy_data["all_prerequisites"],
                "course_titles": hierarchy_data["course_titles"]
            }

            # Let AI generate response using accurate data
            prompt = f"""
            Student asks: {query}

            Student context: {current_year} with completed courses: {completed}

            Use this accurate course data to explain the CS hierarchy:
            Foundation sequence: {hierarchy_data["foundation_sequence"]}
            Prerequisites: {hierarchy_data["all_prerequisites"]}
            Course titles: {hierarchy_data["course_titles"]}

            Important corrections:
            - CS 18000 and CS 18200 are sequential, not alternatives
            - CS 25100 is Data Structures (not CS 24100)
            - CS 25000 and CS 25100 both require CS 18200 AND CS 24000

            Generate a helpful, personalized response explaining the course hierarchy.
            """

            return self._generate_ai_response(prompt, ai_context)
        except ImportError:
            # Fallback: Basic data retrieval without templates
            return self._generate_ai_response(query, {"type": "course_hierarchy"})
    '''
    return code

def main():
    """
    Generate patches for the intelligent conversation manager
    """
    print("Generated PURE AI + KB patches for intelligent_conversation_manager.py:")
    print("="*60)
    print("1. Fixed _normalize_course_code method (uses pure_ai_course_standards)")
    print("2. Fixed course_mentions patterns (correct mappings)")
    print("3. Added AI-based difficulty query handler (no hardcoded responses)")
    print("4. Added AI-based hierarchy query handler (no hardcoded responses)")
    print("="*60)
    print("\\nTo apply these fixes:")
    print("1. Add 'from pure_ai_course_standards import ...' to imports")
    print("2. Replace _normalize_course_code method")
    print("3. Update course_mentions list")
    print("4. Add AI-based difficulty query handler")
    print("5. Add AI-based hierarchy query handler")
    print("\\nIMPORTANT: No hardcoded responses - AI generates all responses using KB data")

    # Write the patches to a file
    with open("/Users/raoro/OneDrive/Desktop/clitest1-main/my_cli_bot/conversation_manager_patches.txt", "w") as f:
        f.write("PATCHES FOR intelligent_conversation_manager.py\\n")
        f.write("="*60 + "\\n\\n")
        f.write("1. ADD TO IMPORTS:\\n")
        f.write("from pure_ai_course_standards import (\\n")
        f.write("    normalize_course_code, get_course_difficulty, get_course_prerequisites,\\n")
        f.write("    get_prerequisite_data_for_ai, get_course_hierarchy_data, validate_prerequisites\\n")
        f.write(")\\n\\n")
        f.write("2. REPLACE _normalize_course_code METHOD:\\n")
        f.write(get_fixed_normalize_course_code_method())
        f.write("\\n\\n3. REPLACE course_mentions LIST:\\n")
        f.write(str(get_fixed_course_mentions()))
        f.write("\\n\\n4. ADD AI-based difficulty query handler:\\n")
        f.write(get_fixed_difficulty_approach())
        f.write("\\n\\n5. ADD AI-based hierarchy query handler:\\n")
        f.write(get_fixed_hierarchy_handling_method())

    print("\\nPatches written to conversation_manager_patches.txt")

if __name__ == "__main__":
    main()