#!/usr/bin/env python3
"""
Final Gaps Check - Search for any remaining hardcoded messages or gaps in the system
"""

import os
import re
import json
from pathlib import Path

def scan_for_hardcoded_messages():
    """Scan all Python files for potential hardcoded user-facing messages"""
    print("🔍 Scanning for Hardcoded Messages")
    print("=" * 50)
    
    # Patterns that might indicate hardcoded user-facing messages
    patterns = [
        r'"I\'m\s+(?:sorry|not\s+sure|having\s+trouble|unable|can\'t)"',  # I'm sorry/not sure/etc
        r'"Sorry[,\s]"',  # Sorry,
        r'"Please\s+(?:try|provide|check)"',  # Please try/provide/check
        r'"You\s+(?:need|should|can\'t|must)"',  # You need/should/etc
        r'"Error[:\s]"',  # Error:
        r'"Failed\s+to"',  # Failed to
        r'"Unable\s+to"',  # Unable to
        r'"Cannot\s+"',  # Cannot
        r'"Could\s+not"',  # Could not
        r'f".*(?:Error|Sorry|Unable|Failed).*"',  # f-strings with error words
    ]
    
    exclude_patterns = [
        r'#.*',  # Comments
        r'""".*?"""',  # Docstrings
        r'prompt.*=',  # AI prompts
        r'AI.*prompt',  # AI prompts
        r'error_prompt',  # AI error prompts
        r'welcome_prompt',  # AI welcome prompts
        r'farewell_prompt',  # AI farewell prompts
        r'test_',  # Test files
        r'log',  # Logging
    ]
    
    main_files = [
        'sql_query_handler.py',
        'simple_boiler_ai.py', 
        'intelligent_conversation_manager.py',
        'universal_purdue_advisor.py',
        'hybrid_safety_config.py',
        'intelligent_academic_advisor.py',
        'graduation_planner.py',
        'degree_progression_engine.py',
        'failure_recovery_system.py',
        'summer_acceleration_calculator.py'
    ]
    
    issues_found = []
    
    for filename in main_files:
        if not os.path.exists(filename):
            continue
            
        print(f"   📄 Checking {filename}")
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\\n')
            
            for line_num, line in enumerate(lines, 1):
                # Skip comments and docstrings
                stripped = line.strip()
                if (stripped.startswith('#') or 
                    stripped.startswith('"""') or 
                    stripped.startswith("'''") or
                    'prompt' in stripped.lower() or
                    'test_' in filename):
                    continue
                
                # Check for hardcoded patterns
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Check if it's in an excluded context
                        is_excluded = False
                        for exclude in exclude_patterns:
                            if re.search(exclude, line, re.IGNORECASE):
                                is_excluded = True
                                break
                        
                        if not is_excluded:
                            issues_found.append({
                                'file': filename,
                                'line': line_num,
                                'content': line.strip(),
                                'pattern': pattern
                            })
        
        except Exception as e:
            print(f"   ❌ Error reading {filename}: {e}")
    
    print(f"\\n📊 Hardcoded Message Scan Results:")
    print(f"   Files scanned: {len(main_files)}")
    print(f"   Potential issues found: {len(issues_found)}")
    
    if issues_found:
        print(f"\\n❌ POTENTIAL HARDCODED MESSAGES:")
        for issue in issues_found:
            print(f"   {issue['file']}:{issue['line']}")
            print(f"   Pattern: {issue['pattern']}")
            print(f"   Content: {issue['content'][:100]}...")
            print()
    else:
        print(f"   ✅ No hardcoded messages detected!")
    
    return len(issues_found) == 0

def check_api_integration_points():
    """Check key integration points for AI usage"""
    print("\\n🔗 Checking API Integration Points")
    print("=" * 50)
    
    integration_checks = [
        {
            'file': 'simple_boiler_ai.py',
            'check': 'has AI client initialization',
            'pattern': r'Gemini|Gemini|ai_client'
        },
        {
            'file': 'intelligent_conversation_manager.py', 
            'check': 'uses AI for responses',
            'pattern': r'chat_completion|get_ai_response|ai_client'
        },
        {
            'file': 'universal_purdue_advisor.py',
            'check': 'routes to AI system',
            'pattern': r'SimpleBoilerAI|ai_engine'
        },
        {
            'file': 'sql_query_handler.py',
            'check': 'returns AI-ready context',
            'pattern': r'needs_ai_response|ai_response'
        }
    ]
    
    passed_checks = 0
    
    for check in integration_checks:
        filename = check['file']
        if not os.path.exists(filename):
            print(f"   ❌ {filename} not found")
            continue
        
        try:
            with open(filename, 'r') as f:
                content = f.read()
            
            if re.search(check['pattern'], content, re.IGNORECASE):
                print(f"   ✅ {check['check']} in {filename}")
                passed_checks += 1
            else:
                print(f"   ❌ {check['check']} missing in {filename}")
                
        except Exception as e:
            print(f"   ❌ Error checking {filename}: {e}")
    
    print(f"\\n📊 Integration Check Results:")
    print(f"   Passed: {passed_checks}/{len(integration_checks)}")
    
    return passed_checks == len(integration_checks)

def check_database_completeness():
    """Check if database has sufficient data for testing"""
    print("\\n🗄️ Checking Database Completeness")
    print("=" * 50)
    
    try:
        from sql_query_handler import SQLQueryHandler
        handler = SQLQueryHandler()
        
        with handler.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check critical data
            checks = [
                ("Foundation courses", "SELECT COUNT(*) FROM courses WHERE course_type = 'foundation'", 5),
                ("Track courses", "SELECT COUNT(*) FROM courses WHERE course_type = 'track'", 5), 
                ("Prerequisites", "SELECT COUNT(*) FROM prerequisites", 50),
                ("Track requirements", "SELECT COUNT(*) FROM track_requirements", 5),
                ("CODO requirements", "SELECT COUNT(*) FROM codo_requirements", 5),
                ("Graduation timelines", "SELECT COUNT(*) FROM graduation_timelines", 3),
                ("Failure recovery data", "SELECT COUNT(*) FROM failure_recovery", 3),
            ]
            
            passed = 0
            
            for check_name, query, min_expected in checks:
                try:
                    cursor.execute(query)
                    count = cursor.fetchone()[0]
                    if count >= min_expected:
                        print(f"   ✅ {check_name}: {count} records (≥{min_expected})")
                        passed += 1
                    else:
                        print(f"   ⚠️  {check_name}: {count} records (<{min_expected})")
                except Exception as e:
                    print(f"   ❌ {check_name}: Error - {e}")
            
            print(f"\\n📊 Database Completeness:")
            print(f"   Passed: {passed}/{len(checks)}")
            
            return passed >= len(checks) * 0.8  # 80% pass rate
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def check_knowledge_gaps():
    """Check for potential knowledge gaps in query handling"""
    print("\\n🧠 Checking for Knowledge Gaps")
    print("=" * 50)
    
    try:
        from sql_query_handler import SQLQueryHandler
        handler = SQLQueryHandler()
        
        # Test queries that should work
        critical_queries = [
            ("CS 18000 info", "course_info"),
            ("CS 25100 prerequisites", "prerequisite_chain"), 
            ("Machine Intelligence track", "track_courses"),
            ("CODO requirements", "codo_requirements"),
            ("3 year graduation", "graduation_timeline"),
            ("CS 18000 failure", "failure_impact"),
        ]
        
        working_queries = 0
        
        for query, expected_type in critical_queries:
            try:
                result = handler.process_query(query)
                if result['success'] and result['count'] > 0:
                    print(f"   ✅ '{query}' -> {result['count']} results")
                    working_queries += 1
                elif not result['success'] and isinstance(result.get('user_friendly_error'), dict):
                    print(f"   ✅ '{query}' -> AI-powered error handling")
                    working_queries += 1
                else:
                    print(f"   ❌ '{query}' -> No results or hardcoded error")
            except Exception as e:
                print(f"   ❌ '{query}' -> Error: {e}")
        
        print(f"\\n📊 Knowledge Gap Check:")
        print(f"   Working queries: {working_queries}/{len(critical_queries)}")
        
        return working_queries >= len(critical_queries) * 0.9  # 90% should work
        
    except Exception as e:
        print(f"❌ Knowledge gap check failed: {e}")
        return False

def main():
    """Run final comprehensive gap check"""
    print("🎯 Final Comprehensive Gap Check")
    print("=" * 60)
    print("Searching for any remaining hardcoded messages or system gaps...\\n")
    
    tests = [
        ("Hardcoded Message Scan", scan_for_hardcoded_messages),
        ("API Integration Points", check_api_integration_points),
        ("Database Completeness", check_database_completeness),
        ("Knowledge Gap Check", check_knowledge_gaps),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results[test_name] = False
    
    # Summary
    print("\\n" + "=" * 60)
    print("📊 FINAL GAP CHECK SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if passed_test:
            passed += 1
    
    print(f"\\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\\n🎉 SYSTEM FULLY AI-POWERED!")
        print("   ✅ No hardcoded messages detected")
        print("   ✅ AI integration points working")
        print("   ✅ Database has sufficient data")
        print("   ✅ Critical queries functioning")
        print("\\n🚀 System ready for production use!")
    else:
        print("\\n⚠️  Some gaps detected - review failed checks above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)