#!/usr/bin/env python3
"""
Simple test for course parsing without Gemini dependencies
"""

import re
import json

def normalize_course_code(course_code: str) -> str:
    """Normalize course codes to standard format"""
    if not course_code:
        return ""
    
    # Handle common formats: CS 180 -> CS 18000, CS180 -> CS 18000
    course_code = course_code.upper().replace(" ", "")
    
    # Extract department and number
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

def test_intent_patterns():
    """Test if the updated intent patterns catch failure scenarios"""
    
    failure_patterns = [
        r"fail", r"failed", r"failing", r"didn.*pass", r"retake", r"recover", 
        r"delay", r"behind.*schedule", r"struggling", r"repeated.*course",
        r"failed.*cs", r"fail.*cs", r"cs.*failed", r"cs.*fail"
    ]
    
    test_queries = [
        "So im taking cs 182 during the summer and i dont think i will pass the class but i have gotten a good score in cs 240 will this impact my graduation",
        "i failed cs 182",
        "i failedcs182", 
        "I'm struggling with CS 182",
        "What if I fail CS 18200?"
    ]
    
    print("Testing Intent Pattern Recognition:")
    print("="*50)
    
    for query in test_queries:
        query_lower = query.lower()
        matches = []
        
        for pattern in failure_patterns:
            if re.search(pattern, query_lower):
                matches.append(pattern)
        
        print(f"Query: {query}")
        print(f"Matches: {matches}")
        print(f"Would trigger failure_recovery: {'YES' if matches else 'NO'}")
        print()

def test_course_extraction():
    """Test course extraction from various query formats"""
    
    test_cases = [
        "So im taking cs 182 during the summer and i dont think i will pass the class but i have gotten a good score in cs 240 will this impact my graduation",
        "i failed cs 182",
        "i failedcs182",
        "I'm taking CS 18200 and CS 24000",
        "What about cs240?",
        "Failed in cs 251"
    ]
    
    print("Testing Course Extraction:")
    print("="*50)
    
    for query in test_cases:
        query_lower = query.lower()
        extracted_courses = []
        
        # Enhanced course patterns
        course_patterns = [
            r"cs\s*(\d{3})",  # CS 180, CS 182, CS 240
            r"cs\s*(\d{5})",  # CS 18000, CS 18200
        ]
        
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
        
        # Pattern 1: Standard course patterns
        for pattern in course_patterns:
            matches = re.findall(pattern, query_lower)
            for match in matches:
                normalized = normalize_course_code(f"CS{match}")
                if normalized:
                    extracted_courses.append(normalized)
        
        # Pattern 2: Specific course mentions
        course_mentions = [
            (r"cs\s*180|cs180", "CS 18000"),
            (r"cs\s*182|cs182", "CS 18200"), 
            (r"cs\s*240|cs240", "CS 24000"),
            (r"cs\s*251|cs251", "CS 25100"),
        ]
        
        for pattern, course_code in course_mentions:
            if re.search(pattern, query_lower):
                extracted_courses.append(course_code)
        
        # Pattern 3: Handle concatenated failure mentions
        concatenated_failures = re.findall(r"fail[a-z]*cs\s*(\d{3})", query_lower)
        for match in concatenated_failures:
            normalized = normalize_course_code(f"CS{match}")
            if normalized:
                extracted_courses.append(normalized)
        
        print(f"Query: {query}")
        print(f"Extracted courses: {list(set(extracted_courses))}")
        print(f"Failure context: {is_failure_context}")
        print()

def test_normalization():
    """Test the course code normalization function"""
    
    print("Testing Course Code Normalization:")
    print("="*50)
    
    test_cases = [
        ("cs182", "CS 18200"),
        ("CS 182", "CS 18200"),
        ("cs 182", "CS 18200"),
        ("CS182", "CS 18200"),
        ("cs240", "CS 24000"),
        ("CS 240", "CS 24000"),
        ("cs250", "CS 25000"),
        ("cs251", "CS 25100"),
        ("ma161", "MA 16100"),
    ]
    
    for input_code, expected in test_cases:
        result = normalize_course_code(input_code)
        status = "✓" if result == expected else "✗"
        print(f"{status} {input_code} -> {result} (expected: {expected})")

if __name__ == "__main__":
    test_normalization()
    print()
    test_intent_patterns()
    print()
    test_course_extraction()