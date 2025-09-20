#!/usr/bin/env python3

import os
from simple_boiler_ai import SimpleBoilerAI

os.environ['GEMINI_API_KEY'] = 'test-key'
os.environ['ENABLE_SQL_QUERIES'] = 'true'

print('🔍 Test 6: Edge Cases and Gap Analysis')
print('-'*40)

try:
    bot = SimpleBoilerAI()
    
    # Test conversational queries (should route to JSON)
    print('💬 Conversational Queries (should route to JSON):')
    conversational_queries = [
        'Hello, I need help',
        'What should I do if I\'m confused?',
        'I\'m struggling with my classes',
        'Help me decide between MI and SE track',
        'What career options do I have?'
    ]
    
    for query in conversational_queries:
        routing = bot.classify_query_for_hybrid_routing(query)
        status = "✅" if routing == 'json' else "❌"
        print(f'{status} "{query[:40]}..." → {routing}')
    print()
    
    # Test edge case course queries
    print('🎯 Edge Case Course Queries:')
    edge_queries = [
        'Tell me about CS 99999',  # Non-existent course
        'Prerequisites for INVALID',  # Invalid course code
        'What is MA 16100?',  # Math course (should work)
        'Info about cs18000',  # Lowercase with no space
        'CS180 details'  # 3-digit course code
    ]
    
    for query in edge_queries:
        print(f'Q: {query}')
        routing = bot.classify_query_for_hybrid_routing(query)
        print(f'Routing: {routing}')
        
        if bot.sql_handler and routing == 'sql':
            sql_result = bot.sql_handler.process_query(query)
            print(f'SQL Success: {sql_result["success"]}')
            if sql_result['success']:
                print(f'Results: {sql_result["count"]} records found')
            else:
                print(f'Error: {sql_result.get("error", "Unknown error")}')
        print()
    
    # Test system health and monitoring
    print('📊 System Health Check:')
    health = bot.get_system_health_status()
    print(f'SQL Enabled: {health.get("sql_enabled", False)}')
    print(f'Emergency Rollback: {health.get("emergency_rollback_active", False)}')
    print(f'Total Queries Processed: {health.get("performance_metrics", {}).get("total_queries", 0)}')
    print(f'SQL Success Rate: {health.get("performance_metrics", {}).get("sql_success_rate", 0)}%')
    print(f'Average SQL Time: {health.get("performance_metrics", {}).get("average_sql_time_ms", 0)}ms')
    print()
    
    # Test query patterns that might confuse routing
    print('❓ Ambiguous Query Routing:')
    ambiguous_queries = [
        'Can you help me with CS 25100?',  # Help request but mentions course
        'I think CS 18000 is hard, what should I do?',  # Opinion + course mention
        'Compare MI and SE tracks',  # Comparison request
        'Is CS 25200 harder than CS 25100?'  # Comparison with courses
    ]
    
    for query in ambiguous_queries:
        routing = bot.classify_query_for_hybrid_routing(query)
        print(f'"{query[:45]}..." → {routing}')
    print()
    
    # Test malformed or unusual queries
    print('🚫 Malformed/Unusual Queries:')
    unusual_queries = [
        '',  # Empty query
        'CS',  # Just department
        '25100',  # Just course number
        'What are the prerequisites for?',  # Incomplete query
        'CS 18000 CS 25100 CS 25200'  # Multiple courses
    ]
    
    for query in unusual_queries:
        print(f'Q: "{query}"')
        routing = bot.classify_query_for_hybrid_routing(query)
        print(f'Routing: {routing}')
        
        if query and bot.sql_handler and routing == 'sql':
            try:
                sql_result = bot.sql_handler.process_query(query)
                print(f'SQL Success: {sql_result["success"]}')
                if sql_result['success']:
                    print(f'Results: {sql_result["count"]} records found')
                else:
                    print(f'Error: {sql_result.get("error", "Unknown error")}')
            except Exception as e:
                print(f'SQL Exception: {str(e)[:50]}...')
        print()
    
    print('✅ Edge case testing completed')
        
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()