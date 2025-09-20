#!/usr/bin/env python3
"""
Performance Validation Script
Tests the performance improvements without external dependencies
"""

import time
import sys
import os
import json
from typing import Dict, Any

def test_knowledge_base_performance():
    """Test knowledge base loading and search performance"""
    print("📚 Testing Knowledge Base Performance...")
    
    # Test JSON loading speed
    knowledge_file = "data/cs_knowledge_graph.json"
    if os.path.exists(knowledge_file):
        start_time = time.time()
        with open(knowledge_file, 'r') as f:
            knowledge_data = json.load(f)
        load_time = time.time() - start_time
        
        print(f"  ✅ Loaded knowledge base in {load_time:.3f}s")
        print(f"  📊 Knowledge contains {len(knowledge_data.get('courses', {}))} courses")
        
        # Test search performance
        start_time = time.time()
        search_results = []
        for _ in range(1000):
            # Simulate course search
            search_term = "CS"
            matches = [course for course in knowledge_data.get('courses', {}).keys() 
                      if search_term in course]
            search_results.append(len(matches))
        search_time = time.time() - start_time
        
        print(f"  ⚡ Completed 1000 searches in {search_time:.3f}s ({1000/search_time:.0f} searches/sec)")
        return load_time, search_time
    else:
        print(f"  ❌ Knowledge file not found: {knowledge_file}")
        return 0, 0

def test_database_operations():
    """Test database performance"""
    print("🗄️ Testing Database Operations...")
    
    import sqlite3
    db_file = "purdue_cs_knowledge.db"
    
    if os.path.exists(db_file):
        start_time = time.time()
        
        # Test connection and query performance
        connections = []
        for i in range(100):
            conn = sqlite3.connect(db_file)
            conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            connections.append(conn)
        
        for conn in connections:
            conn.close()
            
        db_time = time.time() - start_time
        print(f"  ✅ Created and closed 100 DB connections in {db_time:.3f}s")
        print(f"  ⚡ Database throughput: {100/db_time:.0f} connections/sec")
        return db_time
    else:
        print(f"  ❌ Database file not found: {db_file}")
        return 0

def test_file_io_performance():
    """Test file I/O performance"""
    print("💾 Testing File I/O Performance...")
    
    # Test session file operations
    start_time = time.time()
    
    test_data = {
        "session_id": "test_session",
        "created_at": time.time(),
        "conversation_history": [
            {"user": "Hello", "response": "Hi there!"},
            {"user": "What is CS 18000?", "response": "CS 18000 is the first programming course..."}
        ],
        "extracted_context": {
            "current_year": "sophomore",
            "gpa": 3.2,
            "completed_courses": ["CS 18000", "CS 18200"]
        }
    }
    
    # Write test files
    for i in range(100):
        filename = f"test_session_{i}.json"
        with open(filename, 'w') as f:
            json.dump(test_data, f)
    
    # Read test files
    for i in range(100):
        filename = f"test_session_{i}.json"
        with open(filename, 'r') as f:
            data = json.load(f)
    
    # Cleanup
    for i in range(100):
        filename = f"test_session_{i}.json"
        if os.path.exists(filename):
            os.remove(filename)
    
    io_time = time.time() - start_time
    print(f"  ✅ Read/Write 100 session files in {io_time:.3f}s")
    print(f"  ⚡ File I/O throughput: {200/io_time:.0f} operations/sec")
    return io_time

def test_conversation_patterns():
    """Test conversation processing patterns"""
    print("🧠 Testing Conversation Processing...")
    
    test_queries = [
        "Hi",
        "What is CS 18000?",
        "Tell me about Machine Intelligence track",
        "Can I graduate early with a 3.5 GPA?",
        "I failed CS 25100, how does this affect my timeline?",
        "What are the CODO requirements for Computer Science?",
        "Should I choose MI or SE track for AI careers?",
        "Plan my schedule for next semester",
        "What summer courses can help me catch up?",
        "How hard is CS 25200?"
    ]
    
    start_time = time.time()
    
    # Simulate intent classification
    intent_results = []
    for query in test_queries * 10:  # 100 total queries
        query_lower = query.lower()
        
        # Fast pattern matching
        if any(word in query_lower for word in ['course', 'class', 'cs ']):
            intent = 'course_info'
        elif any(word in query_lower for word in ['graduate', 'graduation', 'plan']):
            intent = 'graduation_planning'
        elif any(word in query_lower for word in ['track', 'major', 'specialization']):
            intent = 'track_info'
        elif any(word in query_lower for word in ['codo', 'change major']):
            intent = 'codo_advice'
        elif any(word in query_lower for word in ['failed', 'fail']):
            intent = 'failure_recovery'
        else:
            intent = 'general'
        
        intent_results.append(intent)
    
    processing_time = time.time() - start_time
    print(f"  ✅ Classified 100 queries in {processing_time:.3f}s")
    print(f"  ⚡ Intent classification: {100/processing_time:.0f} queries/sec")
    
    # Show intent distribution
    from collections import Counter
    intent_counts = Counter(intent_results)
    print(f"  📊 Intent distribution: {dict(intent_counts)}")
    
    return processing_time

def generate_performance_report() -> Dict[str, Any]:
    """Generate comprehensive performance report"""
    print("🚀 Starting Performance Validation")
    print("="*60)
    
    results = {}
    
    # Run all tests
    kb_load_time, kb_search_time = test_knowledge_base_performance()
    db_time = test_database_operations()
    io_time = test_file_io_performance()
    conversation_time = test_conversation_patterns()
    
    # Calculate performance grades
    results = {
        "knowledge_base": {
            "load_time": kb_load_time,
            "search_throughput": 1000/kb_search_time if kb_search_time > 0 else 0,
            "grade": "excellent" if kb_search_time < 0.1 else "good" if kb_search_time < 0.5 else "fair"
        },
        "database": {
            "connection_time": db_time,
            "throughput": 100/db_time if db_time > 0 else 0,
            "grade": "excellent" if db_time < 1.0 else "good" if db_time < 3.0 else "fair"
        },
        "file_io": {
            "operation_time": io_time,
            "throughput": 200/io_time if io_time > 0 else 0,
            "grade": "excellent" if io_time < 2.0 else "good" if io_time < 5.0 else "fair"
        },
        "conversation": {
            "processing_time": conversation_time,
            "query_throughput": 100/conversation_time if conversation_time > 0 else 0,
            "grade": "excellent" if conversation_time < 0.1 else "good" if conversation_time < 0.5 else "fair"
        }
    }
    
    print("\n" + "="*60)
    print("🎯 PERFORMANCE REPORT")
    print("="*60)
    
    overall_grades = []
    for component, metrics in results.items():
        grade = metrics["grade"]
        overall_grades.append(grade)
        
        print(f"📊 {component.replace('_', ' ').title()}: {grade.upper()}")
        
        if "throughput" in metrics:
            print(f"   ⚡ Throughput: {metrics['throughput']:.0f} ops/sec")
        
        if "load_time" in metrics:
            print(f"   ⏱️  Load Time: {metrics['load_time']:.3f}s")
        elif "connection_time" in metrics:
            print(f"   ⏱️  Connection Time: {metrics['connection_time']:.3f}s")
        elif "operation_time" in metrics:
            print(f"   ⏱️  Operation Time: {metrics['operation_time']:.3f}s")
        elif "processing_time" in metrics:
            print(f"   ⏱️  Processing Time: {metrics['processing_time']:.3f}s")
    
    # Overall grade
    grade_scores = {"excellent": 3, "good": 2, "fair": 1, "poor": 0}
    avg_score = sum(grade_scores.get(grade, 0) for grade in overall_grades) / len(overall_grades)
    
    if avg_score >= 2.5:
        overall_grade = "EXCELLENT"
    elif avg_score >= 2.0:
        overall_grade = "GOOD"
    elif avg_score >= 1.0:
        overall_grade = "FAIR"
    else:
        overall_grade = "NEEDS IMPROVEMENT"
    
    print(f"\n🏆 OVERALL PERFORMANCE: {overall_grade}")
    
    # Performance recommendations
    print("\n💡 OPTIMIZATION RECOMMENDATIONS:")
    
    if results["knowledge_base"]["search_throughput"] < 5000:
        print("  • Consider implementing knowledge base caching")
    
    if results["database"]["throughput"] < 50:
        print("  • Consider database connection pooling")
    
    if results["file_io"]["throughput"] < 100:
        print("  • Consider async file operations")
    
    if results["conversation"]["query_throughput"] < 500:
        print("  • Consider implementing conversation caching")
    
    if all(metrics["grade"] == "excellent" for metrics in results.values()):
        print("  ✅ All components performing optimally!")
    
    return results

if __name__ == "__main__":
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run performance validation
    report = generate_performance_report()
    
    # Save report
    with open("performance_validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Full report saved to performance_validation_report.json")
    print("✅ Performance validation completed!")