#!/usr/bin/env python3
"""
Comprehensive fix script for all course mapping and prerequisite issues across the codebase
"""

import os
import re
import json
from typing import Dict, List, Tuple

def get_correct_course_mappings() -> Dict[str, str]:
    """Return the correct course number mappings"""
    return {
        "CS 180": "CS 18000",
        "CS180": "CS 18000",
        "cs180": "CS 18000",
        "CS 182": "CS 18200",
        "CS182": "CS 18200",
        "cs182": "CS 18200",
        "CS 240": "CS 24000",
        "CS240": "CS 24000",
        "cs240": "CS 24000",
        "CS 241": "CS 25100",  # Data Structures
        "CS241": "CS 25100",
        "cs241": "CS 25100",
        "CS 250": "CS 25000",  # Computer Architecture
        "CS250": "CS 25000",
        "cs250": "CS 25000",
        "CS 251": "CS 25100",  # Data Structures
        "CS251": "CS 25100",
        "cs251": "CS 25100",
        "CS 252": "CS 25200",  # Systems Programming
        "CS252": "CS 25200",
        "cs252": "CS 25200",
        "CS 307": "CS 30700",  # Database Systems
        "CS307": "CS 30700",
        "cs307": "CS 30700",
        "CS 320": "CS 35200",  # Operating Systems
        "CS320": "CS 35200",
        "cs320": "CS 35200",
    }

def get_correct_difficulty_ratings() -> Dict[str, float]:
    """Return the correct difficulty ratings from knowledge base"""
    return {
        "CS 18000": 4.2,  # Hard - Problem Solving and OOP
        "CS 18200": 4.0,  # Hard - Foundations of CS
        "CS 24000": 3.8,  # Moderate-Hard - Programming in C
        "CS 25000": 4.1,  # Hard - Computer Architecture
        "CS 25100": 4.5,  # Very Hard - Data Structures
        "CS 25200": 4.4,  # Very Hard - Systems Programming
    }

def get_correct_prerequisites() -> Dict[str, List[str]]:
    """Return the correct prerequisite relationships"""
    return {
        "CS 18000": [],  # Starting course
        "CS 18200": ["CS 18000", "MA 16100"],  # Requires CS 18000 AND Calc I
        "CS 24000": ["CS 18000"],  # Requires CS 18000
        "CS 25000": ["CS 18200", "CS 24000"],  # Requires BOTH
        "CS 25100": ["CS 18200", "CS 24000"],  # Requires BOTH
        "CS 25200": ["CS 25000", "CS 25100"],  # Requires BOTH
        "CS 30700": ["CS 25200"],  # Database Systems
        "CS 35200": ["CS 25100"],  # Operating Systems
        "CS 37300": ["CS 25100", "STAT 35000"],  # Data Mining
        "CS 38100": ["CS 25100"],  # Algorithms
    }

def identify_problematic_files() -> List[str]:
    """Identify files that might have course mapping or prerequisite issues"""
    codebase_dir = "/Users/raoro/OneDrive/Desktop/clitest1-main/my_cli_bot"

    problematic_files = []

    # Patterns that indicate potential issues
    issue_patterns = [
        r"CS\s*180(?!\d)",  # CS 180 but not CS 18000+
        r"CS\s*182(?!\d)",  # CS 182 but not CS 18200+
        r"CS\s*240(?!\d)",  # CS 240 but not CS 24000+
        r"CS\s*241(?!\d)",  # CS 241 (often wrongly mapped)
        r"CS\s*250(?!\d)",  # CS 250 but not CS 25000+
        r"CS\s*251(?!\d)",  # CS 251 but not CS 25100+
        r"CS\s*252(?!\d)",  # CS 252 but not CS 25200+
        r"CS\s*307(?!\d)",  # CS 307 but not CS 30700+
        r"CS\s*320(?!\d)",  # CS 320 but not CS 35200+
        r"skip_cs180",      # Old reference
        r"difficulty.*3\.5.*18000",  # Wrong difficulty for CS 18000
        r"difficulty.*3\.5.*25100",  # Wrong difficulty for CS 25100
    ]

    try:
        for root, dirs, files in os.walk(codebase_dir):
            # Skip test files, backup files, and our fix files
            if any(skip in root for skip in ['test_', '.backup', 'fix_', '__pycache__']):
                continue

            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                            # Check for problematic patterns
                            for pattern in issue_patterns:
                                if re.search(pattern, content, re.IGNORECASE):
                                    problematic_files.append(file_path)
                                    break
                    except (UnicodeDecodeError, PermissionError):
                        continue
    except Exception as e:
        print(f"Error scanning files: {e}")

    return list(set(problematic_files))  # Remove duplicates

def generate_fixes_summary() -> str:
    """Generate a summary of all the fixes needed"""

    summary = """# Comprehensive Course Issue Fixes Summary

## Issues Identified Across Codebase:

### 1. Course Number Mapping Issues
- **CS 180 → CS 18000**: Problem Solving and Object-Oriented Programming
- **CS 182 → CS 18200**: Foundations of Computer Science (NOT alternative to CS 18000)
- **CS 240 → CS 24000**: Programming in C
- **CS 241 → CS 25100**: Data Structures (NOT CS 24100)
- **CS 250 → CS 25000**: Computer Architecture
- **CS 251 → CS 25100**: Data Structures
- **CS 252 → CS 25200**: Systems Programming
- **CS 307 → CS 30700**: Database Systems
- **CS 320 → CS 35200**: Operating Systems (NOT CS 32000)

### 2. Difficulty Rating Issues
- **CS 18000**: Should be 4.2 (Hard), not 3.5
- **CS 25100**: Should be 4.5 (Very Hard), not 3.5
- **CS 25000**: Should be 4.1 (Hard), not 4.5
- **CS 24000**: Should be 3.8 (Moderate-Hard)
- **CS 25200**: Should be 4.4 (Very Hard)

### 3. Prerequisite Logic Issues
- **CS 18000 → CS 18200**: Sequential requirement, not alternatives
- **CS 25000**: Requires BOTH CS 18200 AND CS 24000
- **CS 25100**: Requires BOTH CS 18200 AND CS 24000
- **CS 25200**: Requires BOTH CS 25000 AND CS 25100

### 4. Naming Convention Issues
- References to "skip_cs180" should be "skip_cs18000"
- Old 3-digit course references in comments and documentation

## Files Requiring Fixes:
"""

    # Add list of problematic files
    problematic_files = identify_problematic_files()
    for i, file_path in enumerate(problematic_files[:20], 1):  # Show first 20
        relative_path = file_path.replace("/Users/raoro/OneDrive/Desktop/clitest1-main/my_cli_bot/", "")
        summary += f"{i}. {relative_path}\n"

    if len(problematic_files) > 20:
        summary += f"... and {len(problematic_files) - 20} more files\n"

    summary += f"\n**Total Files Identified**: {len(problematic_files)}\n"

    summary += """
## Priority Fixes Needed:

### High Priority:
1. **intelligent_conversation_manager.py**: Course normalization function
2. **intelligent_academic_advisor.py**: Difficulty ratings and prerequisites
3. **ai_training_prompts.py**: Course sequence documentation
4. **graduation_planner.py**: Course planning logic

### Medium Priority:
5. **hybrid_ai_system.py**: Prerequisite mappings
6. **degree_progression_engine.py**: Course sequences
7. **failure_recovery_system.py**: Course failure scenarios

### Low Priority:
8. Test files and demo scripts (for consistency)
9. Documentation files
10. Backup files (cleanup only)

## Recommended Fix Approach:

1. **Create centralized course mapping module**
2. **Update all imports to use centralized mappings**
3. **Fix difficulty ratings to match knowledge base**
4. **Update prerequisite logic throughout**
5. **Test all changes with conversation examples**
6. **Update documentation and comments**

## Test Cases to Verify:

1. "give me the hierarchy of cs classes" → Correct sequence
2. "If i want to take CS250 what prerequisites do i need" → CS 18200 + CS 24000
3. "i dont need to take cs180 to take cs182?" → Explain sequential requirement
4. Course difficulty queries → Match knowledge base ratings
5. Prerequisite validation → Proper blocking of invalid sequences
"""

    return summary

def main():
    """Generate comprehensive analysis and fix recommendations"""

    print("Scanning codebase for course mapping and prerequisite issues...\n")

    # Generate the fixes summary
    summary = generate_fixes_summary()

    # Write to file
    output_file = "/Users/raoro/OneDrive/Desktop/clitest1-main/my_cli_bot/COMPREHENSIVE_COURSE_FIXES_NEEDED.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"Comprehensive analysis written to: {output_file}")

    # Print key findings
    problematic_files = identify_problematic_files()
    print(f"\n🔍 SCAN RESULTS:")
    print(f"├── Files with potential issues: {len(problematic_files)}")
    print(f"├── Course mappings to fix: {len(get_correct_course_mappings())}")
    print(f"├── Difficulty ratings to update: {len(get_correct_difficulty_ratings())}")
    print(f"└── Prerequisite relationships to verify: {len(get_correct_prerequisites())}")

    print(f"\n📋 NEXT STEPS:")
    print(f"1. Review the comprehensive analysis: {output_file}")
    print(f"2. Apply fixes to high-priority files first")
    print(f"3. Test with original conversation examples")
    print(f"4. Verify all course sequences are correct")
    print(f"5. Update documentation and comments")

if __name__ == "__main__":
    main()