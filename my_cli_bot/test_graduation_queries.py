#!/usr/bin/env python3

import os
from simple_boiler_ai import SimpleBoilerAI

os.environ['GEMINI_API_KEY'] = 'test-key'
os.environ['ENABLE_SQL_QUERIES'] = 'true'

print('🎓 Test 4: Graduation Planning Queries')
print('-'*40)

try:
    bot = SimpleBoilerAI()
    
    graduation_queries = [
        'How can I graduate in 3 years?',
        'Early graduation options',
        'What does a 4 year graduation look like?',
        'Can I graduate in 3.5 years?'
    ]
    
    for query in graduation_queries:
        print(f'Q: {query}')
        routing = bot.classify_query_for_hybrid_routing(query)
        print(f'Routing: {routing}')
        
        if bot.sql_handler:
            sql_result = bot.sql_handler.process_query(query)
            print(f'SQL Success: {sql_result["success"]}')
            if sql_result['success'] and sql_result['data']:
                print(f'Graduation plans found: {len(sql_result["data"])}')
                for plan in sql_result['data']:
                    timeline_type = plan.get('timeline_type', 'N/A')
                    years = plan.get('total_years', 'N/A')
                    success_prob = plan.get('success_probability', 'N/A')
                    description = plan.get('description', 'N/A')[:60]
                    
                    if success_prob != 'N/A' and success_prob is not None:
                        success_pct = f"{success_prob*100:.1f}"
                    else:
                        success_pct = 'N/A'
                        
                    print(f'  • {timeline_type}: {years} years, {success_pct}% success')
                    print(f'    {description}...')
            else:
                print('No graduation plans found or query failed')
        print()
        
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()