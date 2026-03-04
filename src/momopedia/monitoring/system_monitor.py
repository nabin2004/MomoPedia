"""
MomoPedia Monitoring and Logging System
Comprehensive monitoring for AI agents, performance metrics, and content quality
"""

import logging
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
from functools import wraps
import threading
from collections import defaultdict, deque


@dataclass
class AgentMetrics:
    """Metrics for individual AI agents"""
    agent_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    quality_scores: List[float] = None
    
    def __post_init__(self):
        if self.quality_scores is None:
            self.quality_scores = []
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @property
    def average_quality(self) -> float:
        if not self.quality_scores:
            return 0.0
        return sum(self.quality_scores) / len(self.quality_scores)

@dataclass  
class ContentMetrics:
    """Metrics for content generation and quality"""
    total_articles: int = 0
    approved_articles: int = 0
    rejected_articles: int = 0
    revision_cycles: List[int] = None
    citation_counts: List[int] = None
    word_counts: List[int] = None
    
    def __post_init__(self):
        if self.revision_cycles is None:
            self.revision_cycles = []
        if self.citation_counts is None:
            self.citation_counts = []
        if self.word_counts is None:
            self.word_counts = []
    
    @property
    def approval_rate(self) -> float:
        if self.total_articles == 0:
            return 0.0
        return self.approved_articles / self.total_articles
    
    @property
    def average_revisions(self) -> float:
        if not self.revision_cycles:
            return 0.0
        return sum(self.revision_cycles) / len(self.revision_cycles)

class MomoLogger:
    """Enhanced logging system for MomoPedia"""
    
    def __init__(self, name: str = "MomoPedia", log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler for all logs
        file_handler = logging.FileHandler(log_dir / f"{name.lower()}.log")
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        # Separate handler for AI agent activities
        agent_handler = logging.FileHandler(log_dir / "agents.log")
        agent_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - [%(extra_data)s] - %(message)s'
        )
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(levelname)s - %(name)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Agent-specific logger
        self.agent_logger = logging.getLogger(f"{name}.agents")
        self.agent_logger.addHandler(agent_handler)
    
    def log_agent_activity(self, agent_name: str, activity: str, data: Dict[str, Any] = None):
        """Log AI agent activities with structured data"""
        extra_data = {
            "agent": agent_name,
            "activity": activity,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
        
        # Use a custom adapter to include extra data
        class LoggerAdapter(logging.LoggerAdapter):
            def process(self, msg, kwargs):
                kwargs['extra'] = {'extra_data': json.dumps(extra_data)}
                return msg, kwargs
        
        adapter = LoggerAdapter(self.agent_logger, extra_data)
        adapter.info(f"{agent_name}: {activity}")
    
    def log_content_generation(self, topic: str, status: str, metrics: Dict[str, Any]):
        """Log content generation events"""
        self.logger.info(
            f"Content Generation - Topic: {topic}, Status: {status}, "
            f"Metrics: {json.dumps(metrics)}"
        )
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log errors with context"""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        self.logger.error(f"Error occurred: {json.dumps(error_data)}")
    
    def log_performance(self, operation: str, duration: float, success: bool = True):
        """Log performance metrics"""
        self.logger.info(
            f"Performance - Operation: {operation}, Duration: {duration:.2f}s, "
            f"Success: {success}"
        )

class MetricsCollector:
    """Collect and analyze system metrics"""
    
    def __init__(self):
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.content_metrics = ContentMetrics()
        self.performance_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.lock = threading.Lock()
    
    def record_agent_request(self, agent_name: str, success: bool, 
                           response_time: float, quality_score: Optional[float] = None):
        """Record metrics for an agent request"""
        with self.lock:
            if agent_name not in self.agent_metrics:
                self.agent_metrics[agent_name] = AgentMetrics(agent_name)
            
            metrics = self.agent_metrics[agent_name]
            metrics.total_requests += 1
            
            if success:
                metrics.successful_requests += 1
                if quality_score is not None:
                    metrics.quality_scores.append(quality_score)
            else:
                metrics.failed_requests += 1
            
            # Update average response time
            total_time = metrics.average_response_time * (metrics.total_requests - 1)
            metrics.average_response_time = (total_time + response_time) / metrics.total_requests
    
    def record_content_event(self, event_type: str, **kwargs):
        """Record content-related events"""
        with self.lock:
            if event_type == "article_created":
                self.content_metrics.total_articles += 1
            elif event_type == "article_approved":
                self.content_metrics.approved_articles += 1
                if 'revisions' in kwargs:
                    self.content_metrics.revision_cycles.append(kwargs['revisions'])
            elif event_type == "article_rejected":
                self.content_metrics.rejected_articles += 1
            
            if 'citations' in kwargs:
                self.content_metrics.citation_counts.append(kwargs['citations'])
            if 'word_count' in kwargs:
                self.content_metrics.word_counts.append(kwargs['word_count'])
    
    def record_performance(self, operation: str, duration: float):
        """Record performance data"""
        with self.lock:
            self.performance_data[operation].append({
                'duration': duration,
                'timestamp': datetime.now().timestamp()
            })
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics"""
        with self.lock:
            summary = {
                'agents': {name: asdict(metrics) for name, metrics in self.agent_metrics.items()},
                'content': asdict(self.content_metrics),
                'performance': {}
            }
            
            # Calculate performance summaries
            for operation, data in self.performance_data.items():
                if data:
                    durations = [d['duration'] for d in data]
                    summary['performance'][operation] = {
                        'count': len(durations),
                        'average': sum(durations) / len(durations),
                        'min': min(durations),
                        'max': max(durations)
                    }
            
            return summary
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        metrics = self.get_metrics_summary()
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)

def performance_monitor(operation_name: str):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error = e
                raise
            finally:
                duration = time.time() - start_time
                
                # Log performance
                logger.log_performance(operation_name, duration, success)
                
                # Record metrics
                metrics_collector.record_performance(operation_name, duration)
                
                if error:
                    logger.log_error(error, {'operation': operation_name, 'duration': duration})
        
        return wrapper
    return decorator

def agent_monitor(agent_name: str):
    """Decorator to monitor AI agent activities"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            quality_score = None
            
            # Log start of activity
            logger.log_agent_activity(agent_name, f"Starting {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                
                # Extract quality score if available in result
                if isinstance(result, dict) and 'quality_score' in result:
                    quality_score = result['quality_score']
                
                return result
                
            except Exception as e:
                success = False
                logger.log_error(e, {'agent': agent_name, 'function': func.__name__})
                raise
            
            finally:
                duration = time.time() - start_time
                
                # Record agent metrics
                metrics_collector.record_agent_request(
                    agent_name, success, duration, quality_score
                )
                
                # Log completion
                status = "completed successfully" if success else "failed"
                logger.log_agent_activity(
                    agent_name, 
                    f"Finished {func.__name__} - {status}",
                    {'duration': duration, 'quality_score': quality_score}
                )
        
        return wrapper
    return decorator

# Global instances
logger = MomoLogger()
metrics_collector = MetricsCollector()

def get_logger() -> MomoLogger:
    """Get the global logger instance"""
    return logger

def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector"""
    return metrics_collector

def generate_monitoring_report() -> str:
    """Generate a comprehensive monitoring report"""
    metrics = metrics_collector.get_metrics_summary()
    
    report_lines = [
        "=== MomoPedia System Monitoring Report ===",
        f"Generated: {datetime.now().isoformat()}",
        "",
        "Agent Performance:",
    ]
    
    for agent_name, agent_data in metrics['agents'].items():
        report_lines.extend([
            f"  {agent_name}:",
            f"    Total Requests: {agent_data['total_requests']}",
            f"    Success Rate: {agent_data['success_rate']:.2%}",
            f"    Avg Response Time: {agent_data['average_response_time']:.2f}s",
            f"    Avg Quality Score: {agent_data['average_quality']:.2f}",
        ])
    
    report_lines.extend([
        "",
        "Content Metrics:",
        f"  Total Articles: {metrics['content']['total_articles']}",
        f"  Approval Rate: {metrics['content']['approval_rate']:.2%}",
        f"  Average Revisions: {metrics['content']['average_revisions']:.1f}",
    ])
    
    if metrics['performance']:
        report_lines.extend(["", "Performance Summary:"])
        for operation, perf_data in metrics['performance'].items():
            report_lines.append(
                f"  {operation}: {perf_data['average']:.2f}s avg "
                f"({perf_data['count']} calls)"
            )
    
    return "\n".join(report_lines)