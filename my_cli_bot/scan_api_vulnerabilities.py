#!/usr/bin/env python3
"""
API Vulnerability Scanner
Scans the entire codebase for unprotected Gemini API calls that could cause 529 errors.
"""

import os
import re
import json
from typing import List, Dict, Tuple

def scan_file_for_api_calls(filepath: str) -> List[Dict]:
    """Scan a single file for unprotected API calls"""
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        return [{"type": "file_read_error", "message": str(e)}]
    
    # Patterns that indicate unprotected API calls
    vulnerability_patterns = [
        (r'\.chat\.completions\.create', "Direct Gemini API call without resilient wrapper"),
        (r'Gemini\..*\.create', "Direct Gemini API call"),
        (r'client\.chat\.completions', "Direct Gemini client usage"),
        (r'ChatCompletion\.create', "Legacy Gemini API call"),
        (r'requests\.post.*Gemini\.com', "Raw HTTP API call to Gemini"),
        (r'anthropic\.messages\.create', "Direct Anthropic API call"),
    ]
    
    # Pattern for resilient calls (these are OK)
    safe_patterns = [
        r'chat_completion_with_retry',
        r'ResilientGeminiClient',
        r'# Test.*mock',
        r'mock.*client',
        r'class ResilientGeminiClient',
        r'def chat_completion_with_retry'
    ]
    
    for line_num, line in enumerate(lines, 1):
        line_clean = line.strip()
        
        # Skip comments and empty lines
        if not line_clean or line_clean.startswith('#'):
            continue
            
        # Check if we're in a resilient client context
        context_start = max(0, line_num - 10)
        context_lines = lines[context_start:line_num]
        context = ' '.join(context_lines)
        
        # Check for safe patterns first (including context)
        is_safe = any(re.search(pattern, line, re.IGNORECASE) for pattern in safe_patterns)
        is_safe = is_safe or 'ResilientGeminiClient' in context or 'chat_completion_with_retry' in context
        
        if is_safe:
            continue
            
        # Check for vulnerability patterns
        for pattern, description in vulnerability_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append({
                    "type": "api_vulnerability",
                    "line_number": line_num,
                    "line_content": line_clean,
                    "pattern": pattern,
                    "description": description,
                    "severity": "HIGH" if "completions.create" in pattern else "MEDIUM"
                })
    
    return issues

def scan_codebase() -> Dict[str, List[Dict]]:
    """Scan entire codebase for API vulnerabilities"""
    results = {}
    
    # Skip these directories and files
    skip_patterns = [
        'venv/', '__pycache__/', '.git/', 'node_modules/',
        'test_', '.log', '.md', '.json', '.txt', '.sh',
        'resilient_api_client.py',  # This is our fix
        'system_analysis_report.py',  # This contains example code
        'scan_api_vulnerabilities.py'  # This file
    ]
    
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        dirs[:] = [d for d in dirs if not any(skip in d for skip in skip_patterns)]
        
        for file in files:
            if not file.endswith('.py'):
                continue
                
            filepath = os.path.join(root, file)
            
            # Skip files matching skip patterns
            if any(skip in filepath for skip in skip_patterns):
                continue
                
            issues = scan_file_for_api_calls(filepath)
            if issues:
                results[filepath] = issues
    
    return results

def analyze_system_entry_points() -> List[str]:
    """Find actual system entry points"""
    entry_points = []
    
    # Check universal_purdue_advisor.py - main entry
    if os.path.exists('universal_purdue_advisor.py'):
        entry_points.append('universal_purdue_advisor.py (PRIMARY ENTRY POINT)')
    
    # Check for other main files
    for file in ['main.py', 'app.py', 'run.py', 'start.py']:
        if os.path.exists(file):
            entry_points.append(f'{file} (potential entry point)')
    
    return entry_points

def generate_fixes(results: Dict[str, List[Dict]]) -> List[str]:
    """Generate fix recommendations"""
    fixes = []
    
    for filepath, issues in results.items():
        high_severity_issues = [i for i in issues if i.get('severity') == 'HIGH']
        
        if high_severity_issues:
            fixes.append(f"🚨 CRITICAL: {filepath}")
            fixes.append(f"   Issues: {len(high_severity_issues)} high-severity API calls")
            fixes.append(f"   Fix: Replace direct API calls with ResilientGeminiClient")
            fixes.append("")
    
    return fixes

def main():
    """Run comprehensive API vulnerability scan"""
    print("🔍 SCANNING CODEBASE FOR API VULNERABILITIES")
    print("=" * 60)
    
    # Scan for vulnerabilities
    results = scan_codebase()
    
    # Analyze entry points
    entry_points = analyze_system_entry_points()
    
    print("📍 SYSTEM ENTRY POINTS:")
    for ep in entry_points:
        print(f"   {ep}")
    print()
    
    if not results:
        print("✅ NO API VULNERABILITIES FOUND!")
        print("   All API calls appear to use resilient error handling")
        return True
    
    print("⚠️ VULNERABILITIES FOUND:")
    print(f"   Files with issues: {len(results)}")
    print()
    
    # Categorize by severity
    high_risk_files = []
    medium_risk_files = []
    
    for filepath, issues in results.items():
        high_issues = [i for i in issues if i.get('severity') == 'HIGH']
        medium_issues = [i for i in issues if i.get('severity') == 'MEDIUM']
        
        if high_issues:
            high_risk_files.append((filepath, high_issues))
        elif medium_issues:
            medium_risk_files.append((filepath, medium_issues))
    
    # Report high risk files
    if high_risk_files:
        print("🚨 HIGH RISK FILES (Direct API calls without error handling):")
        for filepath, issues in high_risk_files:
            print(f"\n📁 {filepath}")
            for issue in issues:
                print(f"   Line {issue['line_number']}: {issue['description']}")
                print(f"      Code: {issue['line_content'][:80]}...")
    
    # Report medium risk files
    if medium_risk_files:
        print(f"\n⚠️ MEDIUM RISK FILES:")
        for filepath, issues in medium_risk_files:
            print(f"   {filepath}: {len(issues)} issues")
    
    # Generate fixes
    print(f"\n🛠️ RECOMMENDED FIXES:")
    fixes = generate_fixes(results)
    for fix in fixes:
        print(f"   {fix}")
    
    # Check if main system is affected
    main_system_affected = any('universal_purdue_advisor.py' in fp or 'simple_boiler_ai.py' in fp for fp in results.keys())
    
    if main_system_affected:
        print("❌ CRITICAL: Main system is affected by API vulnerabilities!")
        return False
    else:
        print("✅ GOOD: Main system (universal_purdue_advisor.py → simple_boiler_ai.py) appears clean")
        
        if results:
            print("⚠️ However, other files have vulnerabilities that could cause 529 errors if used")
        
        return len(high_risk_files) == 0

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Main system is protected from API overload errors!")
    else:
        print("\n❌ Action required to prevent API overload errors!")