#!/usr/bin/env python3
"""
Comprehensive Performance Monitoring System
Tracks all performance metrics and provides real-time monitoring
"""

import time
import psutil
import threading
import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import deque, defaultdict
import asyncio


@dataclass
class SystemMetrics:
    """System-level performance metrics"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_bytes_sent: float
    network_bytes_recv: float
    open_files: int
    threads: int
    timestamp: float


@dataclass
class ApplicationMetrics:
    """Application-level performance metrics"""
    active_requests: int
    total_requests: int
    avg_response_time: float
    error_rate: float
    cache_hit_ratio: float
    database_connections: int
    ai_api_calls: int
    memory_usage_mb: float
    timestamp: float


class PerformanceMonitor:
    """Comprehensive performance monitoring with real-time tracking"""
    
    def __init__(self, monitoring_interval: int = 5, history_size: int = 1000):
        self.monitoring_interval = monitoring_interval
        self.history_size = history_size
        
        # Metrics storage
        self.system_metrics_history: deque = deque(maxlen=history_size)
        self.app_metrics_history: deque = deque(maxlen=history_size)
        
        # Real-time tracking
        self.request_times: deque = deque(maxlen=1000)
        self.error_count = 0
        self.total_requests = 0
        self.active_requests = 0
        
        # System process
        self.process = psutil.Process()
        
        # Alert thresholds
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'avg_response_time': 2.0,  # seconds
            'error_rate': 0.05,  # 5%
            'cache_hit_ratio': 0.6  # 60% minimum
        }
        
        # Alert handlers
        self.alert_handlers = []
        
        # Monitoring thread
        self._monitoring = False
        self._monitor_thread = None
        
        # Performance stats file
        self.stats_file = "performance_stats.json"
        
        # Start monitoring
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start background performance monitoring"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        
        print("📊 Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self._monitoring:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                self.system_metrics_history.append(system_metrics)
                
                # Collect application metrics
                app_metrics = self._collect_app_metrics()
                self.app_metrics_history.append(app_metrics)
                
                # Check alerts
                self._check_alerts(system_metrics, app_metrics)
                
                # Save stats periodically
                if len(self.system_metrics_history) % 12 == 0:  # Every minute
                    self._save_stats()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system-level performance metrics"""
        
        # CPU and memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Process-specific metrics
        process_memory = self.process.memory_info()
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        disk_read_mb = disk_io.read_bytes / (1024 * 1024) if disk_io else 0
        disk_write_mb = disk_io.write_bytes / (1024 * 1024) if disk_io else 0
        
        # Network I/O
        network_io = psutil.net_io_counters()
        
        # File descriptors and threads
        try:
            open_files = len(self.process.open_files())
            threads = self.process.num_threads()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            open_files = 0
            threads = 0
        
        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=process_memory.rss / (1024 * 1024),
            disk_io_read_mb=disk_read_mb,
            disk_io_write_mb=disk_write_mb,
            network_bytes_sent=network_io.bytes_sent,
            network_bytes_recv=network_io.bytes_recv,
            open_files=open_files,
            threads=threads,
            timestamp=time.time()
        )
    
    def _collect_app_metrics(self) -> ApplicationMetrics:
        """Collect application-level performance metrics"""
        
        # Calculate average response time
        avg_response_time = 0.0
        if self.request_times:
            avg_response_time = sum(self.request_times) / len(self.request_times)
        
        # Calculate error rate
        error_rate = 0.0
        if self.total_requests > 0:
            error_rate = self.error_count / self.total_requests
        
        # Get cache hit ratio from components
        cache_hit_ratio = self._get_cache_hit_ratio()
        
        # Get database connections
        db_connections = self._get_database_connections()
        
        # Get AI API calls
        ai_api_calls = self._get_ai_api_calls()
        
        return ApplicationMetrics(
            active_requests=self.active_requests,
            total_requests=self.total_requests,
            avg_response_time=avg_response_time,
            error_rate=error_rate,
            cache_hit_ratio=cache_hit_ratio,
            database_connections=db_connections,
            ai_api_calls=ai_api_calls,
            memory_usage_mb=self.process.memory_info().rss / (1024 * 1024),
            timestamp=time.time()
        )
    
    def _get_cache_hit_ratio(self) -> float:
        """Get overall cache hit ratio from all components"""
        try:
            from .optimized_session_manager import get_pool_stats
            from .knowledge_cache import get_knowledge_cache
            from .ai_service_optimizer import get_ai_optimizer
            
            # Combine cache stats
            total_hits = 0
            total_requests = 0
            
            # Session manager cache
            session_stats = get_pool_stats()
            
            # Knowledge cache
            knowledge_cache = get_knowledge_cache()
            knowledge_stats = knowledge_cache.get_performance_stats()
            total_hits += knowledge_stats.get('total_hits', 0)
            total_requests += knowledge_stats.get('total_hits', 0) + knowledge_stats.get('total_misses', 0)
            
            # AI service cache
            ai_optimizer = get_ai_optimizer()
            ai_stats = ai_optimizer.get_performance_stats()
            total_hits += ai_stats.get('cache_hits', 0)
            total_requests += ai_stats.get('cache_hits', 0) + ai_stats.get('cache_misses', 0)
            
            return total_hits / total_requests if total_requests > 0 else 0.0
            
        except Exception:
            return 0.0
    
    def _get_database_connections(self) -> int:
        """Get active database connections"""
        try:
            from .connection_pool import get_pool_stats
            stats = get_pool_stats()
            return stats.active_connections
        except Exception:
            return 0
    
    def _get_ai_api_calls(self) -> int:
        """Get total AI API calls"""
        try:
            from .ai_service_optimizer import get_ai_optimizer
            ai_optimizer = get_ai_optimizer()
            stats = ai_optimizer.get_performance_stats()
            return stats.get('total_calls', 0)
        except Exception:
            return 0
    
    def _check_alerts(self, system_metrics: SystemMetrics, app_metrics: ApplicationMetrics):
        """Check for performance alerts"""
        
        alerts = []
        
        # System alerts
        if system_metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            alerts.append(f"High CPU usage: {system_metrics.cpu_percent:.1f}%")
        
        if system_metrics.memory_percent > self.alert_thresholds['memory_percent']:
            alerts.append(f"High memory usage: {system_metrics.memory_percent:.1f}%")
        
        # Application alerts
        if app_metrics.avg_response_time > self.alert_thresholds['avg_response_time']:
            alerts.append(f"Slow response time: {app_metrics.avg_response_time:.2f}s")
        
        if app_metrics.error_rate > self.alert_thresholds['error_rate']:
            alerts.append(f"High error rate: {app_metrics.error_rate:.1%}")
        
        if app_metrics.cache_hit_ratio < self.alert_thresholds['cache_hit_ratio']:
            alerts.append(f"Low cache hit ratio: {app_metrics.cache_hit_ratio:.1%}")
        
        # Trigger alert handlers
        if alerts:
            for handler in self.alert_handlers:
                try:
                    handler(alerts, system_metrics, app_metrics)
                except Exception as e:
                    print(f"Alert handler error: {e}")
    
    def _save_stats(self):
        """Save performance statistics to file"""
        try:
            stats = {
                'timestamp': datetime.now().isoformat(),
                'system_metrics': [asdict(m) for m in list(self.system_metrics_history)[-60:]],  # Last hour
                'app_metrics': [asdict(m) for m in list(self.app_metrics_history)[-60:]],
                'summary': self.get_performance_summary()
            }
            
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save stats: {e}")
    
    def track_request(self, response_time: float, success: bool = True):
        """Track a request for performance monitoring"""
        self.total_requests += 1
        self.request_times.append(response_time)
        
        if not success:
            self.error_count += 1
    
    def start_request(self) -> str:
        """Start tracking a request"""
        self.active_requests += 1
        return str(time.time())
    
    def end_request(self, request_id: str, success: bool = True):
        """End tracking a request"""
        self.active_requests = max(0, self.active_requests - 1)
        
        try:
            start_time = float(request_id)
            response_time = time.time() - start_time
            self.track_request(response_time, success)
        except ValueError:
            pass
    
    def add_alert_handler(self, handler):
        """Add alert handler function"""
        self.alert_handlers.append(handler)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics"""
        
        if not self.system_metrics_history or not self.app_metrics_history:
            return {}
        
        # Recent metrics (last 10 minutes)
        recent_system = list(self.system_metrics_history)[-120:]
        recent_app = list(self.app_metrics_history)[-120:]
        
        # Calculate averages
        avg_cpu = sum(m.cpu_percent for m in recent_system) / len(recent_system)
        avg_memory = sum(m.memory_percent for m in recent_system) / len(recent_system)
        avg_response_time = sum(m.avg_response_time for m in recent_app) / len(recent_app)
        
        # Calculate peaks
        peak_cpu = max(m.cpu_percent for m in recent_system)
        peak_memory = max(m.memory_percent for m in recent_system)
        peak_response_time = max(m.avg_response_time for m in recent_app)
        
        # Current values
        current_system = recent_system[-1] if recent_system else None
        current_app = recent_app[-1] if recent_app else None
        
        return {
            'averages': {
                'cpu_percent': avg_cpu,
                'memory_percent': avg_memory,
                'response_time_ms': avg_response_time * 1000
            },
            'peaks': {
                'cpu_percent': peak_cpu,
                'memory_percent': peak_memory,
                'response_time_ms': peak_response_time * 1000
            },
            'current': {
                'cpu_percent': current_system.cpu_percent if current_system else 0,
                'memory_percent': current_system.memory_percent if current_system else 0,
                'active_requests': current_app.active_requests if current_app else 0,
                'cache_hit_ratio': current_app.cache_hit_ratio if current_app else 0,
                'error_rate': current_app.error_rate if current_app else 0
            },
            'totals': {
                'total_requests': self.total_requests,
                'total_errors': self.error_count,
                'uptime_hours': (time.time() - (recent_system[0].timestamp if recent_system else time.time())) / 3600
            }
        }
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time performance statistics"""
        
        current_system = list(self.system_metrics_history)[-1] if self.system_metrics_history else None
        current_app = list(self.app_metrics_history)[-1] if self.app_metrics_history else None
        
        return {
            'system': asdict(current_system) if current_system else {},
            'application': asdict(current_app) if current_app else {},
            'requests': {
                'active': self.active_requests,
                'total': self.total_requests,
                'errors': self.error_count,
                'recent_response_times': list(self.request_times)[-10:]
            }
        }


# Global monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get or create global performance monitor"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def performance_tracking(func):
    """Decorator for automatic performance tracking"""
    def wrapper(*args, **kwargs):
        monitor = get_performance_monitor()
        request_id = monitor.start_request()
        
        try:
            result = func(*args, **kwargs)
            monitor.end_request(request_id, success=True)
            return result
        except Exception as e:
            monitor.end_request(request_id, success=False)
            raise e
    
    return wrapper


def async_performance_tracking(func):
    """Decorator for async function performance tracking"""
    async def wrapper(*args, **kwargs):
        monitor = get_performance_monitor()
        request_id = monitor.start_request()
        
        try:
            result = await func(*args, **kwargs)
            monitor.end_request(request_id, success=True)
            return result
        except Exception as e:
            monitor.end_request(request_id, success=False)
            raise e
    
    return wrapper