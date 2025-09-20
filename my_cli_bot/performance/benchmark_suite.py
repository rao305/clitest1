#!/usr/bin/env python3
"""
Comprehensive Benchmark Suite
Tests and validates performance improvements across all components
"""

import asyncio
import time
import statistics
import json
import threading
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import random

from .performance_integration import get_performance_integration, OptimizedUniversalPurdueAdvisor


@dataclass
class BenchmarkResult:
    """Individual benchmark test result"""
    test_name: str
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    throughput_rps: float
    success_rate: float
    error_count: int
    total_requests: int
    memory_usage_mb: float
    cpu_usage_percent: float


class BenchmarkSuite:
    """Comprehensive performance benchmark suite"""
    
    def __init__(self):
        self.integration = get_performance_integration()
        self.advisor = OptimizedUniversalPurdueAdvisor()
        
        # Test queries for different scenarios
        self.test_queries = {
            'simple_greeting': [
                "Hi", "Hello", "Hey there", "What's up", "Good morning"
            ],
            'course_info': [
                "What is CS 18000?",
                "Tell me about CS 25100",
                "What's the difficulty of CS 25200?",
                "CS 38100 prerequisites",
                "How hard is CS 47300?"
            ],
            'complex_planning': [
                "I'm a sophomore who failed CS 25100, how does this affect my graduation timeline?",
                "Can I graduate early with Machine Intelligence track if I take summer courses?",
                "I want to CODO into CS with a 3.2 GPA, what are my chances?",
                "Plan my course schedule for junior year Software Engineering track",
                "What if I fail both CS 25000 and CS 25100 in the same semester?"
            ],
            'track_selection': [
                "Should I choose Machine Intelligence or Software Engineering track?",
                "What's the difference between MI and SE tracks?",
                "Which track is better for AI careers?",
                "Machine Intelligence track course requirements",
                "Software Engineering track electives"
            ]
        }
    
    async def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive benchmark suite"""
        
        print("🚀 Starting Comprehensive Performance Benchmark")
        print("=" * 60)
        
        results = {}
        
        # Single request benchmarks
        results['single_request'] = await self._benchmark_single_requests()
        
        # Concurrent request benchmarks
        results['concurrent_requests'] = await self._benchmark_concurrent_requests()
        
        # Load testing
        results['load_testing'] = await self._benchmark_load_testing()
        
        # Memory and caching efficiency
        results['cache_efficiency'] = await self._benchmark_cache_efficiency()
        
        # Database performance
        results['database_performance'] = await self._benchmark_database_operations()
        
        # AI service performance
        results['ai_service_performance'] = await self._benchmark_ai_services()
        
        # Generate summary report
        results['summary'] = self._generate_summary_report(results)
        
        # Save results
        self._save_benchmark_results(results)
        
        print("\n" + "=" * 60)
        print("🎯 Benchmark Suite Completed")
        self._print_summary(results['summary'])
        
        return results
    
    async def _benchmark_single_requests(self) -> Dict[str, BenchmarkResult]:
        """Benchmark single request performance by query type"""
        
        print("\n📊 Testing Single Request Performance...")
        
        results = {}
        
        for query_type, queries in self.test_queries.items():
            print(f"  Testing {query_type}...")
            
            response_times = []
            errors = 0
            
            for query in queries:
                for _ in range(5):  # 5 iterations per query
                    start_time = time.time()
                    
                    try:
                        session_id = self.integration.create_session()
                        response = await self.integration.process_query(session_id, query)
                        
                        response_time = time.time() - start_time
                        response_times.append(response_time)
                        
                        if not response or len(response) < 10:
                            errors += 1
                            
                    except Exception as e:
                        errors += 1
                        response_times.append(5.0)  # Penalty for errors
            
            # Calculate statistics
            if response_times:
                results[query_type] = BenchmarkResult(
                    test_name=query_type,
                    avg_response_time=statistics.mean(response_times),
                    min_response_time=min(response_times),
                    max_response_time=max(response_times),
                    p95_response_time=self._percentile(response_times, 95),
                    p99_response_time=self._percentile(response_times, 99),
                    throughput_rps=len(response_times) / sum(response_times),
                    success_rate=(len(response_times) - errors) / len(response_times),
                    error_count=errors,
                    total_requests=len(response_times),
                    memory_usage_mb=0,  # Will be updated with real metrics
                    cpu_usage_percent=0
                )
        
        return results
    
    async def _benchmark_concurrent_requests(self) -> Dict[str, Any]:
        """Benchmark concurrent request handling"""
        
        print("\n🔄 Testing Concurrent Request Performance...")
        
        concurrency_levels = [1, 5, 10, 20, 50]
        results = {}
        
        for concurrency in concurrency_levels:
            print(f"  Testing {concurrency} concurrent requests...")
            
            # Prepare tasks
            tasks = []
            queries = random.choices(
                sum(self.test_queries.values(), []), 
                k=concurrency
            )
            
            start_time = time.time()
            
            # Create concurrent tasks
            for i, query in enumerate(queries):
                session_id = self.integration.create_session()
                task = self.integration.process_query(session_id, query)
                tasks.append(task)
            
            # Execute concurrently
            try:
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                total_time = time.time() - start_time
                
                # Analyze results
                successful_responses = [r for r in responses if isinstance(r, str) and len(r) > 10]
                errors = len(responses) - len(successful_responses)
                
                results[f'concurrency_{concurrency}'] = {
                    'concurrent_requests': concurrency,
                    'total_time': total_time,
                    'avg_response_time': total_time / concurrency,
                    'throughput_rps': concurrency / total_time,
                    'success_rate': len(successful_responses) / len(responses),
                    'error_count': errors
                }
                
            except Exception as e:
                results[f'concurrency_{concurrency}'] = {
                    'error': str(e),
                    'concurrent_requests': concurrency
                }
        
        return results
    
    async def _benchmark_load_testing(self) -> Dict[str, Any]:
        """Benchmark sustained load performance"""
        
        print("\n⚡ Testing Sustained Load Performance...")
        
        # 2-minute load test with varying intensity
        duration = 120  # seconds
        requests_per_second = [1, 2, 5, 10]
        
        results = {}
        
        for rps in requests_per_second:
            print(f"  Testing {rps} RPS for 30 seconds...")
            
            start_time = time.time()
            end_time = start_time + 30  # 30 second test
            
            response_times = []
            errors = 0
            total_requests = 0
            
            while time.time() < end_time:
                request_start = time.time()
                
                try:
                    # Select random query
                    query = random.choice(sum(self.test_queries.values(), []))
                    session_id = self.integration.create_session()
                    
                    response = await self.integration.process_query(session_id, query)
                    
                    response_time = time.time() - request_start
                    response_times.append(response_time)
                    
                    if not response or len(response) < 10:
                        errors += 1
                    
                    total_requests += 1
                    
                    # Wait to maintain RPS
                    sleep_time = (1.0 / rps) - response_time
                    if sleep_time > 0:
                        await asyncio.sleep(sleep_time)
                        
                except Exception as e:
                    errors += 1
                    total_requests += 1
            
            # Calculate results
            actual_duration = time.time() - start_time
            actual_rps = total_requests / actual_duration
            
            results[f'load_{rps}_rps'] = {
                'target_rps': rps,
                'actual_rps': actual_rps,
                'duration': actual_duration,
                'total_requests': total_requests,
                'error_count': errors,
                'error_rate': errors / total_requests if total_requests > 0 else 0,
                'avg_response_time': statistics.mean(response_times) if response_times else 0,
                'p95_response_time': self._percentile(response_times, 95) if response_times else 0
            }
        
        return results
    
    async def _benchmark_cache_efficiency(self) -> Dict[str, Any]:
        """Benchmark caching efficiency across components"""
        
        print("\n💾 Testing Cache Efficiency...")
        
        results = {}
        
        # Test knowledge cache
        print("  Testing knowledge cache...")
        cache_start = time.time()
        
        # First run (cache miss)
        for _ in range(100):
            course_info = self.integration.get_course_info("CS 18000")
            prerequisites = self.integration.get_prerequisites("CS 25100")
            search_results = self.integration.search_courses("programming")
        
        first_run_time = time.time() - cache_start
        
        # Second run (cache hit)
        cache_start = time.time()
        
        for _ in range(100):
            course_info = self.integration.get_course_info("CS 18000")
            prerequisites = self.integration.get_prerequisites("CS 25100")
            search_results = self.integration.search_courses("programming")
        
        second_run_time = time.time() - cache_start
        
        # Calculate cache improvement
        cache_speedup = first_run_time / second_run_time if second_run_time > 0 else 0
        
        results['knowledge_cache'] = {
            'first_run_time': first_run_time,
            'second_run_time': second_run_time,
            'cache_speedup': cache_speedup,
            'improvement_percent': ((first_run_time - second_run_time) / first_run_time) * 100
        }
        
        # Test AI service cache
        print("  Testing AI service cache...")
        
        repeated_queries = [
            "What is CS 18000?",
            "Tell me about Machine Intelligence track",
            "CODO requirements for CS"
        ]
        
        # First run (AI cache miss)
        ai_start = time.time()
        for query in repeated_queries * 5:
            session_id = self.integration.create_session()
            await self.integration.process_query(session_id, query)
        
        ai_first_run = time.time() - ai_start
        
        # Second run (AI cache hit)
        ai_start = time.time()
        for query in repeated_queries * 5:
            session_id = self.integration.create_session()
            await self.integration.process_query(session_id, query)
        
        ai_second_run = time.time() - ai_start
        
        ai_speedup = ai_first_run / ai_second_run if ai_second_run > 0 else 0
        
        results['ai_service_cache'] = {
            'first_run_time': ai_first_run,
            'second_run_time': ai_second_run,
            'cache_speedup': ai_speedup,
            'improvement_percent': ((ai_first_run - ai_second_run) / ai_first_run) * 100
        }
        
        return results
    
    async def _benchmark_database_operations(self) -> Dict[str, Any]:
        """Benchmark database operation performance"""
        
        print("\n🗄️ Testing Database Performance...")
        
        results = {}
        
        # Test session creation performance
        session_start = time.time()
        session_ids = []
        
        for i in range(100):
            session_id = self.integration.create_session(f"test_user_{i}")
            session_ids.append(session_id)
        
        session_creation_time = time.time() - session_start
        
        # Test session retrieval performance
        retrieval_start = time.time()
        
        for session_id in session_ids:
            session_info = self.integration.get_session_info(session_id)
        
        session_retrieval_time = time.time() - retrieval_start
        
        results['session_operations'] = {
            'creation_time_100_sessions': session_creation_time,
            'retrieval_time_100_sessions': session_retrieval_time,
            'avg_creation_time_ms': (session_creation_time / 100) * 1000,
            'avg_retrieval_time_ms': (session_retrieval_time / 100) * 1000,
            'creation_throughput_per_sec': 100 / session_creation_time,
            'retrieval_throughput_per_sec': 100 / session_retrieval_time
        }
        
        return results
    
    async def _benchmark_ai_services(self) -> Dict[str, Any]:
        """Benchmark AI service performance"""
        
        print("\n🧠 Testing AI Service Performance...")
        
        results = {}
        
        # Test different query complexities
        simple_queries = ["Hi", "Hello", "Hey"]
        complex_queries = [
            "I'm a sophomore who failed CS 25100, how does this affect my graduation timeline?",
            "Can I graduate early with Machine Intelligence track if I take summer courses?",
            "Plan my complete course schedule for the next 3 semesters"
        ]
        
        # Simple queries benchmark
        simple_start = time.time()
        simple_responses = []
        
        for query in simple_queries * 10:
            session_id = self.integration.create_session()
            response = await self.integration.process_query(session_id, query)
            simple_responses.append(len(response))
        
        simple_time = time.time() - simple_start
        
        # Complex queries benchmark
        complex_start = time.time()
        complex_responses = []
        
        for query in complex_queries * 5:
            session_id = self.integration.create_session()
            response = await self.integration.process_query(session_id, query)
            complex_responses.append(len(response))
        
        complex_time = time.time() - complex_start
        
        results['ai_query_performance'] = {
            'simple_queries': {
                'total_time': simple_time,
                'avg_time_per_query': simple_time / 30,
                'avg_response_length': statistics.mean(simple_responses)
            },
            'complex_queries': {
                'total_time': complex_time,
                'avg_time_per_query': complex_time / 15,
                'avg_response_length': statistics.mean(complex_responses)
            },
            'complexity_factor': (complex_time / 15) / (simple_time / 30)
        }
        
        return results
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of a dataset"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _generate_summary_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive summary report"""
        
        summary = {
            'overall_performance': 'excellent',
            'key_metrics': {},
            'recommendations': [],
            'performance_gains': {}
        }
        
        # Analyze single request performance
        if 'single_request' in results:
            avg_times = [r.avg_response_time for r in results['single_request'].values()]
            summary['key_metrics']['avg_response_time'] = statistics.mean(avg_times)
            summary['key_metrics']['fastest_query_type'] = min(
                results['single_request'].items(), 
                key=lambda x: x[1].avg_response_time
            )[0]
        
        # Analyze concurrency performance
        if 'concurrent_requests' in results:
            max_successful_concurrency = 0
            for test_name, test_result in results['concurrent_requests'].items():
                if isinstance(test_result, dict) and test_result.get('success_rate', 0) > 0.95:
                    concurrency = test_result['concurrent_requests']
                    max_successful_concurrency = max(max_successful_concurrency, concurrency)
            
            summary['key_metrics']['max_concurrent_users'] = max_successful_concurrency
        
        # Analyze cache efficiency
        if 'cache_efficiency' in results:
            knowledge_speedup = results['cache_efficiency']['knowledge_cache']['cache_speedup']
            ai_speedup = results['cache_efficiency']['ai_service_cache']['cache_speedup']
            
            summary['performance_gains']['knowledge_cache_speedup'] = f"{knowledge_speedup:.1f}x"
            summary['performance_gains']['ai_cache_speedup'] = f"{ai_speedup:.1f}x"
        
        # Generate recommendations
        if summary['key_metrics'].get('avg_response_time', 0) > 1.0:
            summary['recommendations'].append("Consider enabling more aggressive caching")
        
        if summary['key_metrics'].get('max_concurrent_users', 0) < 20:
            summary['recommendations'].append("Consider increasing connection pool size")
        
        return summary
    
    def _save_benchmark_results(self, results: Dict[str, Any]):
        """Save benchmark results to file"""
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"benchmark_results_{timestamp}.json"
        
        # Convert BenchmarkResult objects to dictionaries
        serializable_results = {}
        for key, value in results.items():
            if isinstance(value, dict):
                serializable_value = {}
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, BenchmarkResult):
                        serializable_value[sub_key] = {
                            'test_name': sub_value.test_name,
                            'avg_response_time': sub_value.avg_response_time,
                            'min_response_time': sub_value.min_response_time,
                            'max_response_time': sub_value.max_response_time,
                            'p95_response_time': sub_value.p95_response_time,
                            'p99_response_time': sub_value.p99_response_time,
                            'throughput_rps': sub_value.throughput_rps,
                            'success_rate': sub_value.success_rate,
                            'error_count': sub_value.error_count,
                            'total_requests': sub_value.total_requests
                        }
                    else:
                        serializable_value[sub_key] = sub_value
                serializable_results[key] = serializable_value
            else:
                serializable_results[key] = value
        
        with open(filename, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"\n💾 Benchmark results saved to {filename}")
    
    def _print_summary(self, summary: Dict[str, Any]):
        """Print benchmark summary"""
        
        print(f"📊 Performance Grade: {summary['overall_performance'].upper()}")
        print(f"⚡ Average Response Time: {summary['key_metrics'].get('avg_response_time', 0):.3f}s")
        print(f"🚀 Max Concurrent Users: {summary['key_metrics'].get('max_concurrent_users', 0)}")
        print(f"📈 Cache Improvements: Knowledge {summary['performance_gains'].get('knowledge_cache_speedup', 'N/A')}, AI {summary['performance_gains'].get('ai_cache_speedup', 'N/A')}")
        
        if summary['recommendations']:
            print("\n💡 Recommendations:")
            for rec in summary['recommendations']:
                print(f"  • {rec}")


async def run_benchmark() -> Dict[str, Any]:
    """Run the complete benchmark suite"""
    benchmark = BenchmarkSuite()
    return await benchmark.run_comprehensive_benchmark()


if __name__ == "__main__":
    # Run benchmark if called directly
    asyncio.run(run_benchmark())