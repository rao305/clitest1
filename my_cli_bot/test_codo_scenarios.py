#!/usr/bin/env python3

import os
from simple_boiler_ai import SimpleBoilerAI

os.environ['GEMINI_API_KEY'] = 'test-key'
os.environ['ENABLE_SQL_QUERIES'] = 'true'

print('🚨 Test 5: CODO and Failure Scenarios')
print('-'*40)

try:
    bot = SimpleBoilerAI()
    
    # Test CODO requirements
    print('📋 CODO Requirements:')
    codo_queries = [
        'What are the CODO requirements?',
        'How to change to CS major?',
        'CODO application process'
    ]
    
    for query in codo_queries:
        print(f'Q: {query}')
        routing = bot.classify_query_for_hybrid_routing(query)
        print(f'Routing: {routing}')
        
        if bot.sql_handler:
            sql_result = bot.sql_handler.process_query(query)
            print(f'SQL Success: {sql_result["success"]}')
            if sql_result['success'] and sql_result['data']:
                print(f'CODO requirements found: {len(sql_result["data"])}')
                for req in sql_result['data']:
                    req_type = req.get('requirement_type', 'N/A')
                    req_key = req.get('requirement_key', 'N/A')
                    req_value = req.get('requirement_value', 'N/A')
                    print(f'  • {req_type}: {req_key} = {req_value}')
            else:
                print('No CODO requirements found')
        print()
    
    # Test failure scenarios
    print('💥 Failure Impact Analysis:')
    failure_queries = [
        'What happens if I fail CS 18000?',
        'Impact of failing CS 18200',
        'What if I fail CS 25100?'
    ]
    
    for query in failure_queries:
        print(f'Q: {query}')
        routing = bot.classify_query_for_hybrid_routing(query)
        print(f'Routing: {routing}')
        
        if bot.sql_handler:
            sql_result = bot.sql_handler.process_query(query)
            print(f'SQL Success: {sql_result["success"]}')
            if sql_result['success'] and sql_result['data']:
                print(f'Failure scenarios found: {len(sql_result["data"])}')
                for scenario in sql_result['data']:
                    course = scenario.get('failed_course_code', 'N/A')
                    delay = scenario.get('delay_semesters', 'N/A')
                    impact = scenario.get('graduation_impact', 'N/A')[:50]
                    summer_option = scenario.get('summer_option', False)
                    print(f'  • {course}: {delay} semester delay')
                    print(f'    Impact: {impact}...')
                    print(f'    Summer recovery: {"Yes" if summer_option else "No"}')
            else:
                print('No failure scenarios found')
        print()
        
    # Test course load questions
    print('📊 Course Load Guidelines:')
    load_queries = [
        'How many courses can I take as a freshman?',
        'Course load for sophomores',
        'Credit limits by year'
    ]
    
    for query in load_queries:
        print(f'Q: {query}')
        routing = bot.classify_query_for_hybrid_routing(query)
        print(f'Routing: {routing}')
        
        if bot.sql_handler:
            sql_result = bot.sql_handler.process_query(query)
            print(f'SQL Success: {sql_result["success"]}')
            if sql_result['success'] and sql_result['data']:
                print(f'Course load guidelines found: {len(sql_result["data"])}')
                for guideline in sql_result['data']:
                    level = guideline.get('student_level', 'N/A')
                    max_credits = guideline.get('total_credits_max', 'N/A')
                    max_cs = guideline.get('cs_courses_max', 'N/A')
                    recommended_cs = guideline.get('cs_courses_recommended', 'N/A')
                    rationale = guideline.get('rationale', 'N/A')[:40]
                    print(f'  • {level}: {max_credits} credits max, {max_cs} CS max, {recommended_cs} CS recommended')
                    print(f'    {rationale}...')
            else:
                print('No course load guidelines found')
        print()
        
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()