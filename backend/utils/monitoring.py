from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
import logging
from functools import wraps

# Create loggers
logger = logging.getLogger(__name__)

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status_code'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'Duration of HTTP requests in seconds', ['method', 'endpoint'])
ACTIVE_TASKS = Gauge('active_tasks_count', 'Number of active tasks')
TASK_EVENTS_PROCESSED = Counter('task_events_processed_total', 'Total task events processed', ['event_type'])

class MonitoringMiddleware:
    """Custom middleware to collect metrics for FastAPI application"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record request metrics"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

        self.logger.info(f"Request metrics recorded: {method} {endpoint} {status_code} {duration}s")

def monitor_task_event(event_type: str):
    """Decorator to monitor task event processing"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                TASK_EVENTS_PROCESSED.labels(event_type=event_type).inc()
                duration = time.time() - start_time
                logger.info(f"Task event {event_type} processed in {duration:.2f}s")
                return result
            except Exception as e:
                logger.error(f"Error processing task event {event_type}: {str(e)}")
                raise
        return wrapper
    return decorator

def start_monitoring_server(port: int = 8001):
    """Start the Prometheus metrics server"""
    try:
        start_http_server(port)
        logger.info(f"Monitoring server started on port {port}")
    except Exception as e:
        logger.error(f"Failed to start monitoring server: {str(e)}")

# Predefined metrics for common operations
TASK_CREATED_COUNTER = Counter('tasks_created_total', 'Total tasks created')
TASK_COMPLETED_COUNTER = Counter('tasks_completed_total', 'Total tasks completed')
TASK_ERRORS_COUNTER = Counter('task_errors_total', 'Total task-related errors')