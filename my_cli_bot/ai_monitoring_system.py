#!/usr/bin/env python3
"""
AI Monitoring and Performance Tracking System for Boiler AI
Tracks token usage, API performance, error rates, and system health
"""

import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import os

@dataclass
class APIMetrics:
    """Metrics for API calls"""
    provider: str
    model: str
    tokens_used: int
    response_time_ms: float
    success: bool
    error_type: Optional[str] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class SystemHealth:
    """Overall system health metrics"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    tokens_used_hour: int
    tokens_used_total: int
    uptime_seconds: float
    error_rate: float
    primary_provider_status: str
    fallback_provider_status: str
    last_updated: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class AIMonitoringSystem:
    """Comprehensive monitoring system for AI operations"""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics_history: deque = deque(maxlen=10000)  # Keep last 10k metrics
        self.hourly_tokens = defaultdict(int)  # Track tokens per hour
        self.error_patterns = defaultdict(int)  # Track error frequencies
        self.provider_performance = defaultdict(list)  # Track provider performance
        
        # Thread-safe locks
        self._lock = threading.Lock()
        
        # Configuration from environment
        self.token_monitoring_enabled = os.getenv("ENABLE_TOKEN_MONITORING", "true").lower() == "true"
        self.max_tokens_per_hour = int(os.getenv("MAX_TOKENS_PER_HOUR", "50000"))
        self.warn_threshold = float(os.getenv("WARN_TOKEN_THRESHOLD", "80")) / 100
        self.performance_logging = os.getenv("ENABLE_PERFORMANCE_LOGGING", "true").lower() == "true"
        
        # Setup logging
        self.setup_monitoring_logger()
        
        # Cleanup old metrics periodically
        self._start_cleanup_thread()
    
    def setup_monitoring_logger(self):
        """Setup dedicated logger for monitoring"""
        self.logger = logging.getLogger("ai_monitoring")
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # File handler for monitoring logs
        handler = logging.FileHandler("logs/ai_monitoring.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Console handler for critical issues
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def record_api_call(self, provider: str, model: str, tokens_used: int, 
                       response_time_ms: float, success: bool, error_type: str = None):
        """Record API call metrics"""
        if not self.token_monitoring_enabled and not self.performance_logging:
            return
        
        metrics = APIMetrics(
            provider=provider,
            model=model,
            tokens_used=tokens_used,
            response_time_ms=response_time_ms,
            success=success,
            error_type=error_type
        )
        
        with self._lock:
            self.metrics_history.append(metrics)
            
            # Track hourly tokens
            current_hour = int(time.time() // 3600)
            self.hourly_tokens[current_hour] += tokens_used
            
            # Track error patterns
            if error_type:
                self.error_patterns[error_type] += 1
            
            # Track provider performance
            self.provider_performance[provider].append({
                'response_time': response_time_ms,
                'success': success,
                'timestamp': metrics.timestamp
            })
        
        # Log significant events
        if self.performance_logging:
            if not success:
                self.logger.warning(f"API call failed: {provider}/{model} - {error_type}")
            elif response_time_ms > 5000:  # > 5 seconds
                self.logger.warning(f"Slow API response: {provider}/{model} - {response_time_ms:.1f}ms")
        
        # Check token usage warnings
        if self.token_monitoring_enabled:
            self._check_token_usage_warnings(current_hour)
    
    def _check_token_usage_warnings(self, current_hour: int):
        """Check if token usage is approaching limits"""
        tokens_this_hour = self.hourly_tokens[current_hour]
        usage_percentage = tokens_this_hour / self.max_tokens_per_hour
        
        if usage_percentage >= self.warn_threshold:
            self.logger.warning(
                f"High token usage: {tokens_this_hour}/{self.max_tokens_per_hour} "
                f"({usage_percentage:.1%}) in current hour"
            )
        
        if tokens_this_hour >= self.max_tokens_per_hour:
            self.logger.critical(
                f"Token limit exceeded: {tokens_this_hour}/{self.max_tokens_per_hour} in current hour"
            )
    
    def get_system_health(self) -> SystemHealth:
        """Get comprehensive system health metrics"""
        with self._lock:
            if not self.metrics_history:
                return SystemHealth(
                    total_requests=0,
                    successful_requests=0,
                    failed_requests=0,
                    average_response_time=0.0,
                    tokens_used_hour=0,
                    tokens_used_total=0,
                    uptime_seconds=time.time() - self.start_time,
                    error_rate=0.0,
                    primary_provider_status="unknown",
                    fallback_provider_status="unknown",
                    last_updated=time.time()
                )
            
            # Calculate metrics from recent history
            recent_metrics = [m for m in self.metrics_history if m.timestamp > time.time() - 3600]  # Last hour
            
            total_requests = len(recent_metrics)
            successful_requests = sum(1 for m in recent_metrics if m.success)
            failed_requests = total_requests - successful_requests
            
            average_response_time = (
                sum(m.response_time_ms for m in recent_metrics) / total_requests
                if total_requests > 0 else 0.0
            )
            
            current_hour = int(time.time() // 3600)
            tokens_used_hour = self.hourly_tokens[current_hour]
            tokens_used_total = sum(m.tokens_used for m in self.metrics_history)
            
            error_rate = failed_requests / total_requests if total_requests > 0 else 0.0
            
            # Check provider status
            primary_status = self._get_provider_status("Gemini")
            fallback_status = self._get_provider_status("Anthropic")
            
            return SystemHealth(
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                average_response_time=average_response_time,
                tokens_used_hour=tokens_used_hour,
                tokens_used_total=tokens_used_total,
                uptime_seconds=time.time() - self.start_time,
                error_rate=error_rate,
                primary_provider_status=primary_status,
                fallback_provider_status=fallback_status,
                last_updated=time.time()
            )
    
    def _get_provider_status(self, provider: str) -> str:
        """Get status of a specific provider based on recent performance"""
        if provider not in self.provider_performance:
            return "unknown"
        
        recent_calls = [
            call for call in self.provider_performance[provider]
            if call['timestamp'] > time.time() - 300  # Last 5 minutes
        ]
        
        if not recent_calls:
            return "unknown"
        
        success_rate = sum(1 for call in recent_calls if call['success']) / len(recent_calls)
        avg_response_time = sum(call['response_time'] for call in recent_calls) / len(recent_calls)
        
        if success_rate >= 0.95 and avg_response_time < 3000:
            return "healthy"
        elif success_rate >= 0.80:
            return "degraded"
        else:
            return "unhealthy"
    
    def get_token_usage_report(self) -> Dict[str, Any]:
        """Get detailed token usage report"""
        if not self.token_monitoring_enabled:
            return {"enabled": False}
        
        with self._lock:
            current_hour = int(time.time() // 3600)
            
            # Get last 24 hours of data
            hourly_data = []
            for i in range(24):
                hour = current_hour - i
                tokens = self.hourly_tokens.get(hour, 0)
                hour_timestamp = hour * 3600
                hourly_data.append({
                    "hour": datetime.fromtimestamp(hour_timestamp).strftime("%Y-%m-%d %H:00"),
                    "tokens": tokens,
                    "percentage": (tokens / self.max_tokens_per_hour) * 100
                })
            
            return {
                "enabled": True,
                "current_hour_tokens": self.hourly_tokens[current_hour],
                "max_tokens_per_hour": self.max_tokens_per_hour,
                "current_hour_percentage": (self.hourly_tokens[current_hour] / self.max_tokens_per_hour) * 100,
                "hourly_breakdown": hourly_data[::-1],  # Reverse to show oldest first
                "total_tokens_all_time": sum(m.tokens_used for m in self.metrics_history)
            }
    
    def get_error_analysis(self) -> Dict[str, Any]:
        """Get detailed error analysis"""
        with self._lock:
            recent_metrics = [m for m in self.metrics_history if m.timestamp > time.time() - 3600]
            
            error_breakdown = defaultdict(int)
            provider_errors = defaultdict(lambda: defaultdict(int))
            
            for metric in recent_metrics:
                if not metric.success and metric.error_type:
                    error_breakdown[metric.error_type] += 1
                    provider_errors[metric.provider][metric.error_type] += 1
            
            return {
                "total_errors_last_hour": sum(error_breakdown.values()),
                "error_types": dict(error_breakdown),
                "errors_by_provider": {
                    provider: dict(errors) for provider, errors in provider_errors.items()
                },
                "most_common_errors": sorted(
                    error_breakdown.items(), key=lambda x: x[1], reverse=True
                )[:5]
            }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        health = self.get_system_health()
        token_report = self.get_token_usage_report()
        error_analysis = self.get_error_analysis()
        
        return {
            "system_health": health.to_dict(),
            "token_usage": token_report,
            "error_analysis": error_analysis,
            "provider_performance": self._get_provider_performance_summary(),
            "recommendations": self._generate_recommendations(health)
        }
    
    def _get_provider_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for each provider"""
        summary = {}
        
        with self._lock:
            for provider, calls in self.provider_performance.items():
                recent_calls = [
                    call for call in calls
                    if call['timestamp'] > time.time() - 3600  # Last hour
                ]
                
                if recent_calls:
                    success_rate = sum(1 for call in recent_calls if call['success']) / len(recent_calls)
                    avg_response_time = sum(call['response_time'] for call in recent_calls) / len(recent_calls)
                    
                    summary[provider] = {
                        "total_calls": len(recent_calls),
                        "success_rate": success_rate,
                        "average_response_time_ms": avg_response_time,
                        "status": self._get_provider_status(provider)
                    }
        
        return summary
    
    def _generate_recommendations(self, health: SystemHealth) -> List[str]:
        """Generate recommendations based on system health"""
        recommendations = []
        
        if health.error_rate > 0.10:  # > 10% error rate
            recommendations.append("High error rate detected. Consider checking API keys and network connectivity.")
        
        if health.average_response_time > 5000:  # > 5 seconds
            recommendations.append("Slow response times detected. Consider using a faster model or implementing caching.")
        
        if health.tokens_used_hour > self.max_tokens_per_hour * 0.8:
            recommendations.append("High token usage detected. Consider implementing response caching or using a more efficient model.")
        
        if health.primary_provider_status == "unhealthy":
            recommendations.append("Primary AI provider is unhealthy. Consider switching to fallback provider.")
        
        if health.uptime_seconds > 86400 and not recommendations:  # 24 hours uptime with no issues
            recommendations.append("System is running smoothly with good performance metrics.")
        
        return recommendations
    
    def _start_cleanup_thread(self):
        """Start background thread to clean up old metrics"""
        def cleanup_old_data():
            while True:
                time.sleep(3600)  # Run every hour
                with self._lock:
                    # Clean up hourly token data older than 7 days
                    cutoff_hour = int((time.time() - 7 * 24 * 3600) // 3600)
                    old_hours = [hour for hour in self.hourly_tokens if hour < cutoff_hour]
                    for hour in old_hours:
                        del self.hourly_tokens[hour]
                    
                    # Clean up provider performance data older than 24 hours
                    cutoff_time = time.time() - 24 * 3600
                    for provider in self.provider_performance:
                        self.provider_performance[provider] = [
                            call for call in self.provider_performance[provider]
                            if call['timestamp'] > cutoff_time
                        ]
        
        cleanup_thread = threading.Thread(target=cleanup_old_data, daemon=True)
        cleanup_thread.start()
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        with self._lock:
            export_data = {
                "export_timestamp": time.time(),
                "system_health": self.get_system_health().to_dict(),
                "token_usage": self.get_token_usage_report(),
                "error_analysis": self.get_error_analysis(),
                "performance_summary": self._get_provider_performance_summary(),
                "recent_metrics": [
                    asdict(metric) for metric in list(self.metrics_history)[-1000:]  # Last 1000 metrics
                ]
            }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        self.logger.info(f"Metrics exported to {filepath}")

# Global monitoring instance
_monitoring_instance = None

def get_monitoring_system() -> AIMonitoringSystem:
    """Get global monitoring system instance"""
    global _monitoring_instance
    if _monitoring_instance is None:
        _monitoring_instance = AIMonitoringSystem()
    return _monitoring_instance

def record_api_call(provider: str, model: str, tokens_used: int, 
                   response_time_ms: float, success: bool, error_type: str = None):
    """Convenience function to record API calls"""
    monitoring = get_monitoring_system()
    monitoring.record_api_call(provider, model, tokens_used, response_time_ms, success, error_type)

def get_system_health():
    """Convenience function to get system health"""
    monitoring = get_monitoring_system()
    return monitoring.get_system_health()

def get_performance_report():
    """Convenience function to get performance report"""
    monitoring = get_monitoring_system()
    return monitoring.get_performance_report()