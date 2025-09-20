#!/usr/bin/env python3
"""
Hybrid SQL Safety Configuration
Advanced feature flags and safety mechanisms for production deployment
"""

import os
import json
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class HybridSafetyConfig:
    """Configuration class for hybrid SQL safety mechanisms"""
    
    # Core feature flags
    enable_sql_queries: bool = True
    enable_fallback_validation: bool = True
    enable_performance_monitoring: bool = True
    enable_query_logging: bool = False
    
    # Safety thresholds
    max_sql_query_time_ms: float = 100.0  # Max SQL query time before fallback
    max_sql_retries: int = 2  # Max retries on SQL failure
    sql_timeout_seconds: float = 5.0  # SQL query timeout
    
    # Performance monitoring
    enable_performance_alerts: bool = False
    performance_threshold_ms: float = 50.0  # Alert if queries take longer
    
    # Rollback mechanisms
    enable_emergency_rollback: bool = True
    max_consecutive_failures: int = 5  # Disable SQL after N failures
    failure_rate_threshold: float = 0.3  # Disable if failure rate > 30%
    
    # Validation settings
    validate_sql_results: bool = False  # Compare SQL vs JSON results
    validation_sample_rate: float = 0.1  # Validate 10% of queries
    
    @classmethod
    def from_environment(cls) -> 'HybridSafetyConfig':
        """Create configuration from environment variables"""
        return cls(
            enable_sql_queries=os.getenv("ENABLE_SQL_QUERIES", "true").lower() == "true",
            enable_fallback_validation=os.getenv("ENABLE_FALLBACK_VALIDATION", "true").lower() == "true",
            enable_performance_monitoring=os.getenv("ENABLE_PERFORMANCE_MONITORING", "true").lower() == "true",
            enable_query_logging=os.getenv("ENABLE_QUERY_LOGGING", "false").lower() == "true",
            
            max_sql_query_time_ms=float(os.getenv("MAX_SQL_QUERY_TIME_MS", "100")),
            max_sql_retries=int(os.getenv("MAX_SQL_RETRIES", "2")),
            sql_timeout_seconds=float(os.getenv("SQL_TIMEOUT_SECONDS", "5")),
            
            enable_performance_alerts=os.getenv("ENABLE_PERFORMANCE_ALERTS", "false").lower() == "true",
            performance_threshold_ms=float(os.getenv("PERFORMANCE_THRESHOLD_MS", "50")),
            
            enable_emergency_rollback=os.getenv("ENABLE_EMERGENCY_ROLLBACK", "true").lower() == "true",
            max_consecutive_failures=int(os.getenv("MAX_CONSECUTIVE_FAILURES", "5")),
            failure_rate_threshold=float(os.getenv("FAILURE_RATE_THRESHOLD", "0.3")),
            
            validate_sql_results=os.getenv("VALIDATE_SQL_RESULTS", "false").lower() == "true",
            validation_sample_rate=float(os.getenv("VALIDATION_SAMPLE_RATE", "0.1"))
        )

class HybridSafetyManager:
    """Manages safety mechanisms and monitoring for hybrid SQL system"""
    
    def __init__(self, config: Optional[HybridSafetyConfig] = None):
        self.config = config or HybridSafetyConfig.from_environment()
        
        # Performance tracking
        self.query_stats = {
            'total_queries': 0,
            'sql_queries': 0,
            'json_queries': 0,
            'sql_failures': 0,
            'consecutive_failures': 0,
            'total_sql_time_ms': 0,
            'average_sql_time_ms': 0,
            'emergency_rollback_active': False
        }
        
        # Query log
        self.query_log = []
        
        # Circuit breaker state
        self.sql_disabled_until = None
    
    def should_use_sql(self, query: str) -> bool:
        """Determine if SQL should be used based on safety checks"""
        
        # Check if SQL is globally disabled
        if not self.config.enable_sql_queries:
            return False
        
        # Check emergency rollback
        if self.config.enable_emergency_rollback and self.query_stats['emergency_rollback_active']:
            return False
        
        # Check circuit breaker
        if self.sql_disabled_until and time.time() < self.sql_disabled_until:
            return False
        
        # Check failure rate
        if (self.query_stats['total_queries'] > 10 and 
            self.query_stats['sql_failures'] / max(self.query_stats['sql_queries'], 1) > self.config.failure_rate_threshold):
            self._trigger_emergency_rollback("High failure rate")
            return False
        
        # Check consecutive failures
        if self.query_stats['consecutive_failures'] >= self.config.max_consecutive_failures:
            self._trigger_emergency_rollback("Max consecutive failures")
            return False
        
        return True
    
    def record_sql_success(self, query: str, execution_time_ms: float, result_count: int = 0):
        """Record a successful SQL query"""
        self.query_stats['total_queries'] += 1
        self.query_stats['sql_queries'] += 1
        self.query_stats['consecutive_failures'] = 0  # Reset failure counter
        self.query_stats['total_sql_time_ms'] += execution_time_ms
        self.query_stats['average_sql_time_ms'] = (
            self.query_stats['total_sql_time_ms'] / max(self.query_stats['sql_queries'], 1)
        )
        
        # Log query if enabled
        if self.config.enable_query_logging:
            self.query_log.append({
                'timestamp': time.time(),
                'query': query[:100] + "..." if len(query) > 100 else query,
                'type': 'sql_success',
                'execution_time_ms': execution_time_ms,
                'result_count': result_count
            })
        
        # Performance alerts
        if (self.config.enable_performance_alerts and 
            execution_time_ms > self.config.performance_threshold_ms):
            self._log_performance_alert(query, execution_time_ms)
    
    def record_sql_failure(self, query: str, error: str, execution_time_ms: float = 0):
        """Record a failed SQL query"""
        self.query_stats['total_queries'] += 1
        self.query_stats['sql_queries'] += 1
        self.query_stats['sql_failures'] += 1
        self.query_stats['consecutive_failures'] += 1
        
        # Log failure if enabled
        if self.config.enable_query_logging:
            self.query_log.append({
                'timestamp': time.time(),
                'query': query[:100] + "..." if len(query) > 100 else query,
                'type': 'sql_failure',
                'error': error,
                'execution_time_ms': execution_time_ms
            })
        
        # SQL failures are handled by AI system - no hardcoded messages
    
    def record_json_fallback(self, query: str, reason: str):
        """Record when JSON fallback was used"""
        self.query_stats['total_queries'] += 1
        self.query_stats['json_queries'] += 1
        
        # Log fallback if enabled
        if self.config.enable_query_logging:
            self.query_log.append({
                'timestamp': time.time(),
                'query': query[:100] + "..." if len(query) > 100 else query,
                'type': 'json_fallback',
                'reason': reason
            })
    
    def _trigger_emergency_rollback(self, reason: str):
        """Trigger emergency rollback to JSON-only mode"""
        if not self.config.enable_emergency_rollback:
            return
        
        self.query_stats['emergency_rollback_active'] = True
        # Emergency rollback handled by AI system - no hardcoded messages
        
        # Log emergency rollback
        if self.config.enable_query_logging:
            self.query_log.append({
                'timestamp': time.time(),
                'query': 'SYSTEM',
                'type': 'emergency_rollback',
                'reason': reason
            })
    
    def _log_performance_alert(self, query: str, execution_time_ms: float):
        """Log performance alerts"""
        # Performance alerts handled by AI system - no hardcoded messages
        pass
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        if self.query_stats['sql_queries'] == 0:
            sql_failure_rate = 0
            sql_success_rate = 0
        else:
            sql_failure_rate = self.query_stats['sql_failures'] / self.query_stats['sql_queries']
            sql_success_rate = 1 - sql_failure_rate
        
        return {
            'sql_enabled': self.config.enable_sql_queries and self.should_use_sql("test"),
            'emergency_rollback_active': self.query_stats['emergency_rollback_active'],
            'circuit_breaker_active': self.sql_disabled_until is not None and time.time() < self.sql_disabled_until,
            'performance_metrics': {
                'total_queries': self.query_stats['total_queries'],
                'sql_queries': self.query_stats['sql_queries'],
                'json_queries': self.query_stats['json_queries'],
                'sql_success_rate': round(sql_success_rate * 100, 1),
                'sql_failure_rate': round(sql_failure_rate * 100, 1),
                'average_sql_time_ms': round(self.query_stats['average_sql_time_ms'], 2),
                'consecutive_failures': self.query_stats['consecutive_failures']
            },
            'config': {
                'max_sql_query_time_ms': self.config.max_sql_query_time_ms,
                'max_consecutive_failures': self.config.max_consecutive_failures,
                'failure_rate_threshold': round(self.config.failure_rate_threshold * 100, 1)
            }
        }
    
    def reset_emergency_rollback(self):
        """Reset emergency rollback (admin function)"""
        self.query_stats['emergency_rollback_active'] = False
        self.query_stats['consecutive_failures'] = 0
        self.sql_disabled_until = None
        # Reset confirmation handled by AI system - no hardcoded messages
    
    def export_query_log(self, filename: str = "hybrid_query_log.json"):
        """Export query log to file"""
        if not self.config.enable_query_logging:
            return
        
        with open(filename, 'w') as f:
            json.dump(self.query_log, f, indent=2)
        # Export confirmation handled by AI system - no hardcoded messages

# Global safety manager instance
safety_manager = HybridSafetyManager()

def get_safety_manager() -> HybridSafetyManager:
    """Get the global safety manager instance"""
    return safety_manager

# Example usage and configuration
if __name__ == "__main__":
    print("🛡️  Hybrid SQL Safety Configuration")
    print("=====================================")
    
    # Create configuration from environment
    config = HybridSafetyConfig.from_environment()
    print(f"SQL Queries Enabled: {config.enable_sql_queries}")
    print(f"Emergency Rollback: {config.enable_emergency_rollback}")
    print(f"Performance Monitoring: {config.enable_performance_monitoring}")
    print(f"Max SQL Query Time: {config.max_sql_query_time_ms}ms")
    print(f"Max Consecutive Failures: {config.max_consecutive_failures}")
    
    # Test safety manager
    manager = HybridSafetyManager(config)
    print(f"\nShould use SQL: {manager.should_use_sql('test query')}")
    
    # Simulate some queries
    manager.record_sql_success("What are the prerequisites?", 2.5, 5)
    manager.record_sql_success("Tell me about CS 18000", 1.8, 1)
    manager.record_sql_failure("Bad query", "Table not found", 0.5)
    
    # Show health status
    health = manager.get_health_status()
    print(f"\n📊 System Health Status:")
    for key, value in health['performance_metrics'].items():
        print(f"   {key}: {value}")