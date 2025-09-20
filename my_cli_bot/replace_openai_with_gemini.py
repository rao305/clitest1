#!/usr/bin/env python3
"""
Script to replace all Gemini references with Gemini throughout the project
"""

import os
import re
import glob
from pathlib import Path

# Hardcoded Gemini API key
GEMINI_API_KEY = "AIzaSyD9zDBDtIWWuPUKRdqtGb5reDoIHmDez50"

# Files to exclude from replacement
EXCLUDE_PATTERNS = [
    "venv/**",
    "path/**", 
    "**/__pycache__/**",
    "**/node_modules/**",
    "**/.git/**"
]

# Replacement mappings
REPLACEMENTS = {
    # Import statements
    r"import google.generativeai as genai": "import google.generativeai as genai",
    r"from google.generativeai import": "from google.generativeai import",
    r"import google.generativeai as genai\.": "import google.generativeai as genai",
    
    # API key references
    r"GEMINI_API_KEY": "GEMINI_API_KEY",
    r"os\.environ\.get\(\"GEMINI_API_KEY\"\)": f'"{GEMINI_API_KEY}"',
    r"os\.environ\.get\(\'GEMINI_API_KEY\'\)": f'"{GEMINI_API_KEY}"',
    
    # Client initialization
    r"Gemini\.Gemini\(api_key=api_key\)": "genai.GenerativeModel('gemini-1.5-flash')",
    r"self\.gemini_model": "self.gemini_model",
    r"gemini_model": "gemini_model",
    
    # API calls
    r"\.chat\.completions\.create\(": ".generate_content(",
    r"response\.choices\[0\]\.message\.content": "response.text",
    r"messages=\[.*?\]": "prompt",
    r"model=\"Gemini-.*?\"": "",
    r"temperature=\d+\.?\d*": "",
    r"max_tokens=\d+": "",
    
    # Comments and documentation
    r"Gemini": "Gemini",
    r"Gemini": "gemini",
    r"Gemini": "Gemini",
    r"Gemini-": "gemini-",
    
    # Error messages
    r"Gemini API key": "Gemini API key",
    r"Gemini error": "Gemini error",
    r"Gemini API key validation failed": "Gemini API key validation failed",
    r"Gemini API key validated successfully": "Gemini API key validated successfully",
}

def should_exclude_file(file_path):
    """Check if file should be excluded from processing"""
    for pattern in EXCLUDE_PATTERNS:
        if Path(file_path).match(pattern):
            return True
    return False

def replace_in_file(file_path):
    """Replace Gemini references in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all replacements
        for pattern, replacement in REPLACEMENTS.items():
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE | re.MULTILINE)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated: {file_path}")
            return True
        else:
            print(f"⏭️  No changes: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all Python files"""
    print("🔄 Starting Gemini to Gemini replacement...")
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not any(Path(os.path.join(root, d)).match(pattern) for pattern in EXCLUDE_PATTERNS)]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if not should_exclude_file(file_path):
                    python_files.append(file_path)
    
    print(f"📁 Found {len(python_files)} Python files to process")
    
    updated_count = 0
    for file_path in python_files:
        if replace_in_file(file_path):
            updated_count += 1
    
    print(f"\n🎉 Replacement complete!")
    print(f"📊 Updated {updated_count} files out of {len(python_files)} total files")

if __name__ == "__main__":
    main()

