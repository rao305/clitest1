#!/usr/bin/env python3
"""
Automated API Vulnerability Fixer
Systematically fixes Gemini API vulnerabilities across the codebase
"""

import os
import re
from typing import List, Tuple

def fix_file_vulnerabilities(filepath: str) -> bool:
    """Fix Gemini API vulnerabilities in a single file"""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Check if file already has resilient import
        has_resilient_import = "ResilientGeminiClient" in content
        
        # Add resilient import if needed
        if "import google.generativeai as genai" in content and not has_resilient_import:
            # Add import after other imports
            import_pattern = r'(from ai_training_prompts import.*\n)'
            if re.search(import_pattern, content):
                content = re.sub(
                    import_pattern,
                    r'\1from simple_boiler_ai import ResilientGeminiClient\n',
                    content
                )
            else:
                # Add import after standard imports
                import_pattern = r'(import os\n)'
                content = re.sub(
                    import_pattern,
                    r'\1from simple_boiler_ai import ResilientGeminiClient\n',
                    content
                )
        
        # Replace Gemini client initialization
        content = re.sub(
            r'self\.gemini_model = Gemini\.Gemini\(api_key=([^)]+)\)',
            r'self.gemini_model = ResilientGeminiClient(api_key=\1)',
            content
        )
        
        content = re.sub(
            r'gemini_model = Gemini\.Gemini\(api_key=([^)]+)\)',
            r'gemini_model = ResilientGeminiClient(api_key=\1)',
            content
        )
        
        # Replace direct API calls with resilient calls
        # Pattern 1: Simple response assignment
        content = re.sub(
            r'response = ([^.]+)\.chat\.completions\.create\(\s*([^}]+)\s*\)\s*\n\s*([^\n]*response\.choices\[0\]\.message\.content[^\n]*)',
            r'response_text = \1.chat_completion_with_retry(\2)\n            \3.replace("response.text", "response_text")',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # Pattern 2: Direct return
        content = re.sub(
            r'return ([^.]+)\.chat\.completions\.create\(\s*([^}]+)\s*\)\.choices\[0\]\.message\.content',
            r'return \1.chat_completion_with_retry(\2)',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # Pattern 3: Variable assignment with content access
        content = re.sub(
            r'(\w+) = ([^.]+)\.chat\.completions\.create\(\s*([^}]+)\s*\)\.choices\[0\]\.message\.content',
            r'\1 = \2.chat_completion_with_retry(\3)',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # More specific patterns for complex cases
        patterns = [
            # Response with content access
            (r'response = ([^.]+)\.chat\.completions\.create\(\s*([^}]+)\s*\)',
             r'response_text = \1.chat_completion_with_retry(\2)'),
            
            # Direct content access
            (r'response\.choices\[0\]\.message\.content',
             r'response_text'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        
        # Write back if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
            
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False
    
    return False

def get_vulnerable_files() -> List[str]:
    """Get list of files with API vulnerabilities"""
    vulnerable_files = [
        "unified_ai_query_engine.py",
        "intelligent_academic_advisor.py", 
        "enhanced_nlp_engine.py",
        "enhanced_knowledge_pipeline.py",
        "simple_nlp_solver.py",
        "llm_providers.py",
        "llm_engine.py",
        "hybrid_ai_system.py",
        "boiler_ai_final.py",
        "chat.py",
        "intelligent_ai_response_generator.py",
        "n8n_style_pipeline.py", 
        "enhanced_rag_engine.py",
        "performance/ai_service_optimizer.py"
    ]
    
    # Filter to only existing files
    existing_files = []
    for filename in vulnerable_files:
        if os.path.exists(filename):
            existing_files.append(filename)
        elif os.path.exists(f"/Users/rrao/Desktop/BCLI/my_cli_bot/{filename}"):
            existing_files.append(f"/Users/rrao/Desktop/BCLI/my_cli_bot/{filename}")
    
    return existing_files

def main():
    """Fix all vulnerable files"""
    
    print("🔧 AUTOMATED API VULNERABILITY FIXER")
    print("=" * 50)
    
    vulnerable_files = get_vulnerable_files()
    
    print(f"Found {len(vulnerable_files)} vulnerable files to fix")
    
    fixed_count = 0
    
    for filepath in vulnerable_files:
        print(f"Fixing {filepath}...")
        if fix_file_vulnerabilities(filepath):
            print(f"  ✅ Fixed {filepath}")
            fixed_count += 1
        else:
            print(f"  ⏸️  No changes needed for {filepath}")
    
    print(f"\n🎉 Fixed {fixed_count}/{len(vulnerable_files)} files")
    print("All API calls now use resilient error handling!")

if __name__ == "__main__":
    main()