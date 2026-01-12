# API Endpoint Response Time Verification Guide

This document provides comprehensive instructions for testing and verifying that all API endpoints in the Full-Stack Todo Application respond within 500ms, ensuring optimal performance and user experience.

## Overview

API response time is a critical performance metric that directly impacts user experience. This guide covers tools, methodologies, and best practices for measuring, monitoring, and optimizing API endpoint response times to meet the 500ms target.

## Response Time Benchmarks

### Target Benchmarks

- **Excellent**: < 100ms
- **Good**: 100-250ms
- **Acceptable**: 250-500ms
- **Needs Improvement**: 500-1000ms
- **Poor**: > 1000ms

### Critical Endpoints Performance Targets

| Endpoint | Method | Target Response Time | Priority |
|----------|--------|---------------------|----------|
| `/api/auth/login` | POST | < 300ms | High |
| `/api/auth/register` | POST | < 400ms | High |
| `/api/tasks` | GET | < 200ms | High |
| `/api/tasks` | POST | < 300ms | High |
| `/api/tasks/{id}` | GET | < 150ms | High |
| `/api/tasks/{id}` | PUT | < 250ms | High |
| `/api/tasks/{id}` | DELETE | < 200ms | High |
| `/api/tasks/{id}` | PATCH | < 200ms | High |

## Testing Methodologies

### 1. Single Endpoint Testing

Test individual endpoints with controlled parameters:

```python
# api_response_time_test.py
import time
import requests
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime

class APIResponseTimeTester:
    def __init__(self, base_url, auth_token=None):
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json'
        }
        if auth_token:
            self.headers['Authorization'] = f'Bearer {auth_token}'

        self.results = {}

    def time_endpoint(self, method, endpoint, data=None, headers=None):
        """Time a single API endpoint call"""
        if headers is None:
            headers = self.headers

        start_time = time.time()

        try:
            if method.upper() == 'GET':
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(f"{self.base_url}{endpoint}", headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(f"{self.base_url}{endpoint}", headers=headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(f"{self.base_url}{endpoint}", headers=headers)
            elif method.upper() == 'PATCH':
                response = requests.patch(f"{self.base_url}{endpoint}", headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds

            return {
                'method': method,
                'endpoint': endpoint,
                'status_code': response.status_code,
                'response_time': response_time,
                'success': 200 <= response.status_code < 300,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            return {
                'method': method,
                'endpoint': endpoint,
                'status_code': 500,
                'response_time': response_time,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def test_single_endpoint_multiple_times(self, method, endpoint, data=None, iterations=10):
        """Test a single endpoint multiple times to get statistical data"""
        results = []

        print(f"Testing {method} {endpoint} {iterations} times...")

        for i in range(iterations):
            result = self.time_endpoint(method, endpoint, data)
            results.append(result)

            if (i + 1) % 5 == 0:
                print(f"  Completed {i + 1}/{iterations} requests")

        # Calculate statistics
        response_times = [r['response_time'] for r in results]
        success_rate = sum(1 for r in results if r['success']) / len(results) * 100

        stats = {
            'method': method,
            'endpoint': endpoint,
            'total_requests': len(results),
            'successful_requests': sum(1 for r in results if r['success']),
            'success_rate': success_rate,
            'avg_response_time': statistics.mean(response_times),
            'median_response_time': statistics.median(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'std_deviation': statistics.stdev(response_times) if len(response_times) > 1 else 0,
            'percentile_95': sorted(response_times)[int(0.95 * len(response_times))] if response_times else 0,
            'under_500ms': sum(1 for r in response_times if r < 500),
            'under_500ms_percentage': sum(1 for r in response_times if r < 500) / len(response_times) * 100,
            'results': results
        }

        self.results[f"{method}_{endpoint}"] = stats
        return stats

    def run_comprehensive_test(self):
        """Run comprehensive tests on all API endpoints"""
        endpoints_to_test = [
            ('GET', '/api/tasks'),
            ('POST', '/api/tasks', {'title': 'Test Task', 'description': 'Test description', 'status': 'pending'}),
            ('GET', '/api/tasks/1'),  # Assuming task ID 1 exists
            ('PUT', '/api/tasks/1', {'title': 'Updated Test Task', 'status': 'completed'}),
            ('DELETE', '/api/tasks/999'),  # Testing with non-existent ID to check error handling
            ('PATCH', '/api/tasks/1', {'status': 'in-progress'}),
            ('POST', '/api/auth/register', {'email': 'test@example.com', 'password': 'password123', 'name': 'Test User'}),
            ('POST', '/api/auth/login', {'email': 'test@example.com', 'password': 'password123'}),
        ]

        print("Starting comprehensive API response time testing...\n")

        all_stats = []
        for method, endpoint in endpoints_to_test[:-2]:  # Skip auth endpoints for now
            try:
                stats = self.test_single_endpoint_multiple_times(method, endpoint, iterations=10)
                all_stats.append(stats)

                print(f"\n{method} {endpoint} Results:")
                print(f"  Avg: {stats['avg_response_time']:.2f}ms")
                print(f"  Median: {stats['median_response_time']:.2f}ms")
                print(f"  95th percentile: {stats['percentile_95']:.2f}ms")
                print(f"  Success rate: {stats['success_rate']:.1f}%")
                print(f"  Under 500ms: {stats['under_500ms_percentage']:.1f}%")

                # Check if endpoint meets 500ms requirement
                if stats['percentile_95'] > 500:
                    print(f"  ⚠️  WARNING: 95th percentile exceeds 500ms ({stats['percentile_95']:.2f}ms)")
                else:
                    print(f"  ✅ OK: Meets 500ms requirement")

            except Exception as e:
                print(f"  ❌ ERROR testing {method} {endpoint}: {str(e)}")

            print()  # Empty line for readability

        return all_stats

    def export_results_to_csv(self, filename='api_response_times.csv'):
        """Export test results to CSV file"""
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'method', 'endpoint', 'total_requests', 'successful_requests',
                'success_rate', 'avg_response_time', 'median_response_time',
                'min_response_time', 'max_response_time', 'percentile_95',
                'under_500ms_percentage', 'passed_500ms_threshold'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for key, stats in self.results.items():
                row = {
                    'method': stats['method'],
                    'endpoint': stats['endpoint'],
                    'total_requests': stats['total_requests'],
                    'successful_requests': stats['successful_requests'],
                    'success_rate': round(stats['success_rate'], 2),
                    'avg_response_time': round(stats['avg_response_time'], 2),
                    'median_response_time': round(stats['median_response_time'], 2),
                    'min_response_time': round(stats['min_response_time'], 2),
                    'max_response_time': round(stats['max_response_time'], 2),
                    'percentile_95': round(stats['percentile_95'], 2),
                    'under_500ms_percentage': round(stats['under_500ms_percentage'], 2),
                    'passed_500ms_threshold': stats['percentile_95'] < 500
                }
                writer.writerow(row)

        print(f"Results exported to {filename}")

# Usage example
if __name__ == "__main__":
    tester = APIResponseTimeTester("http://localhost:8000", "your_auth_token_here")
    results = tester.run_comprehensive_test()
    tester.export_results_to_csv()
```

### 2. Concurrent Load Testing

Test endpoints under concurrent load to identify performance bottlenecks:

```python
# concurrent_load_test.py
import time
import requests
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import matplotlib.pyplot as plt

class ConcurrentAPITester:
    def __init__(self, base_url, auth_token=None):
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json'
        }
        if auth_token:
            self.headers['Authorization'] = f'Bearer {auth_token}'

    def time_request(self, method, endpoint, data=None):
        """Time a single request"""
        start_time = time.time()

        try:
            if method.upper() == 'GET':
                response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(f"{self.base_url}{endpoint}", headers=self.headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(f"{self.base_url}{endpoint}", headers=self.headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(f"{self.base_url}{endpoint}", headers=self.headers)

            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            return {
                'response_time': response_time,
                'status_code': response.status_code,
                'success': 200 <= response.status_code < 300,
                'thread_id': threading.current_thread().ident
            }
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            return {
                'response_time': response_time,
                'status_code': 500,
                'success': False,
                'error': str(e),
                'thread_id': threading.current_thread().ident
            }

    def test_concurrent_requests(self, method, endpoint, data=None, num_threads=10, requests_per_thread=5):
        """Test endpoint with concurrent requests"""
        print(f"Testing {method} {endpoint} with {num_threads} threads, {requests_per_thread} requests each...")

        all_results = []

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Create futures for all requests
            futures = []
            for thread_num in range(num_threads):
                for req_num in range(requests_per_thread):
                    future = executor.submit(self.time_request, method, endpoint, data)
                    futures.append(future)

            # Collect results as they complete
            for future in as_completed(futures):
                result = future.result()
                all_results.append(result)

        # Calculate statistics
        response_times = [r['response_time'] for r in all_results]
        successful_requests = sum(1 for r in all_results if r['success'])
        success_rate = successful_requests / len(all_results) * 100

        stats = {
            'method': method,
            'endpoint': endpoint,
            'total_requests': len(all_results),
            'successful_requests': successful_requests,
            'success_rate': success_rate,
            'avg_response_time': statistics.mean(response_times),
            'median_response_time': statistics.median(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'percentile_95': sorted(response_times)[int(0.95 * len(response_times))],
            'percentile_99': sorted(response_times)[int(0.99 * len(response_times))],
            'under_500ms': sum(1 for rt in response_times if rt < 500),
            'under_500ms_percentage': sum(1 for rt in response_times if rt < 500) / len(response_times) * 100,
            'results': all_results
        }

        return stats

    def run_load_tests(self):
        """Run load tests on all endpoints"""
        endpoints = [
            ('GET', '/api/tasks'),
            ('POST', '/api/tasks', {'title': 'Load Test Task', 'description': 'Created during load test', 'status': 'pending'}),
            ('GET', '/api/tasks/1'),
        ]

        results = []

        for method, endpoint, data in endpoints:
            stats = self.test_concurrent_requests(method, endpoint, data, num_threads=5, requests_per_thread=10)
            results.append(stats)

            print(f"\n{method} {endpoint} Load Test Results:")
            print(f"  Total requests: {stats['total_requests']}")
            print(f"  Success rate: {stats['success_rate']:.1f}%")
            print(f"  Avg response: {stats['avg_response_time']:.2f}ms")
            print(f"  95th percentile: {stats['percentile_95']:.2f}ms")
            print(f"  99th percentile: {stats['percentile_99']:.2f}ms")
            print(f"  Under 500ms: {stats['under_500ms_percentage']:.1f}%")

            if stats['percentile_95'] > 500:
                print(f"  ⚠️  FAILED: 95th percentile exceeds 500ms")
            else:
                print(f"  ✅ PASSED: Meets 500ms requirement")

        return results

if __name__ == "__main__":
    tester = ConcurrentAPITester("http://localhost:8000", "your_auth_token_here")
    results = tester.run_load_tests()
```

### 3. Continuous Monitoring Script

Create a script for ongoing monitoring of API response times:

```python
# api_monitor.py
import time
import requests
import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import json
import sqlite3
from pathlib import Path

class APIResponseMonitor:
    def __init__(self, base_url, db_path="api_monitor.db", threshold_ms=500):
        self.base_url = base_url
        self.threshold_ms = threshold_ms
        self.db_path = db_path
        self.setup_logging()
        self.init_database()

    def setup_logging(self):
        """Setup logging for monitoring"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('api_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def init_database(self):
        """Initialize SQLite database for storing metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS response_times (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                method TEXT,
                endpoint TEXT,
                response_time REAL,
                status_code INTEGER,
                success BOOLEAN
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                method TEXT,
                endpoint TEXT,
                response_time REAL,
                message TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def time_endpoint(self, method, endpoint, data=None, headers=None):
        """Time an endpoint and store results"""
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        start_time = time.time()

        try:
            if method.upper() == 'GET':
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(f"{self.base_url}{endpoint}", headers=headers, json=data, timeout=10)
            elif method.upper() == 'PUT':
                response = requests.put(f"{self.base_url}{endpoint}", headers=headers, json=data, timeout=10)
            elif method.upper() == 'DELETE':
                response = requests.delete(f"{self.base_url}{endpoint}", headers=headers, timeout=10)

            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds

            # Store in database
            self.store_metric(method, endpoint, response_time, response.status_code, response.ok)

            # Check if response time exceeds threshold
            if response_time > self.threshold_ms:
                self.logger.warning(f"SLOW RESPONSE: {method} {endpoint} took {response_time:.2f}ms")
                self.create_alert(method, endpoint, response_time, f"Response time exceeded {self.threshold_ms}ms threshold")

            return response_time, response.status_code, response.ok

        except requests.exceptions.Timeout:
            response_time = (time.time() - start_time) * 1000
            self.store_metric(method, endpoint, response_time, 408, False)
            self.logger.error(f"TIMEOUT: {method} {endpoint} timed out")
            self.create_alert(method, endpoint, response_time, "Request timed out")
            return response_time, 408, False
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.store_metric(method, endpoint, response_time, 500, False)
            self.logger.error(f"ERROR: {method} {endpoint} failed with {str(e)}")
            self.create_alert(method, endpoint, response_time, f"Request failed: {str(e)}")
            return response_time, 500, False

    def store_metric(self, method, endpoint, response_time, status_code, success):
        """Store response time metric in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO response_times (method, endpoint, response_time, status_code, success)
            VALUES (?, ?, ?, ?, ?)
        ''', (method, endpoint, response_time, status_code, success))

        conn.commit()
        conn.close()

    def create_alert(self, method, endpoint, response_time, message):
        """Create alert for slow response"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO alerts (method, endpoint, response_time, message)
            VALUES (?, ?, ?, ?)
        ''', (method, endpoint, response_time, message))

        conn.commit()
        conn.close()

    def get_statistics(self, hours_back=24):
        """Get statistics for the last specified hours"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                method,
                endpoint,
                COUNT(*) as total_requests,
                AVG(response_time) as avg_response_time,
                MAX(response_time) as max_response_time,
                MIN(response_time) as min_response_time,
                SUM(CASE WHEN response_time > ? THEN 1 ELSE 0 END) as slow_requests
            FROM response_times
            WHERE timestamp >= datetime('now', '-{} hours')
            GROUP BY method, endpoint
        ''', (self.threshold_ms, hours_back))

        results = cursor.fetchall()
        conn.close()

        return results

    def monitor_continuously(self, endpoints, interval_seconds=30, duration_hours=None):
        """Monitor endpoints continuously"""
        start_time = time.time()
        duration_seconds = duration_hours * 3600 if duration_hours else None

        self.logger.info(f"Starting continuous monitoring of {len(endpoints)} endpoints")

        while True:
            for method, endpoint, data in endpoints:
                response_time, status_code, success = self.time_endpoint(method, endpoint, data)

                status = "✅" if success and response_time < self.threshold_ms else "❌"
                self.logger.info(f"{status} {method} {endpoint}: {response_time:.2f}ms (Status: {status_code})")

            # Check if duration limit reached
            if duration_seconds and (time.time() - start_time) >= duration_seconds:
                self.logger.info("Monitoring duration reached, stopping...")
                break

            time.sleep(interval_seconds)

    def generate_report(self):
        """Generate a performance report"""
        stats = self.get_statistics(hours_back=24)

        print("\n" + "="*80)
        print("API PERFORMANCE REPORT (Last 24 Hours)")
        print("="*80)

        for stat in stats:
            method, endpoint, total, avg, max_rt, min_rt, slow = stat
            slow_percentage = (slow / total) * 100 if total > 0 else 0

            status = "⚠️" if slow_percentage > 5 else "✅"

            print(f"\n{status} {method} {endpoint}")
            print(f"  Total Requests: {total}")
            print(f"  Avg Response: {avg:.2f}ms")
            print(f"  Min Response: {min_rt:.2f}ms")
            print(f"  Max Response: {max_rt:.2f}ms")
            print(f"  Slow Requests: {slow} ({slow_percentage:.1f}%)")

        print("="*80)

if __name__ == "__main__":
    # Define endpoints to monitor
    endpoints_to_monitor = [
        ('GET', '/api/tasks', None),
        ('POST', '/api/tasks', {'title': 'Monitor Task', 'description': 'For monitoring', 'status': 'pending'}),
        ('GET', '/api/tasks/1', None),
    ]

    # Initialize monitor
    monitor = APIResponseMonitor("http://localhost:8000", threshold_ms=500)

    # Generate initial report
    monitor.generate_report()

    # Uncomment to start continuous monitoring
    # monitor.monitor_continuously(endpoints_to_monitor, interval_seconds=30, duration_hours=1)
```

## Performance Optimization Techniques

### 1. Backend Optimizations

```python
# backend/main.py - Add response time monitoring middleware
from fastapi import Request
from time import time
import logging

# Set up logging for performance
logging.basicConfig(level=logging.INFO)
perf_logger = logging.getLogger("performance")

async def add_process_time_header(request: Request, call_next):
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    # Log slow requests
    process_time_ms = process_time * 1000
    if process_time_ms > 500:  # Log requests taking more than 500ms
        perf_logger.warning(
            f"SLOW REQUEST: {request.method} {request.url.path} took {process_time_ms:.2f}ms"
        )

    return response

# Add middleware to app
app.middleware("http")(add_process_time_header)
```

### 2. Database Query Optimization

```python
# backend/database.py - Optimized database queries
from sqlmodel import select, func
from sqlalchemy.orm import selectinload

# Use selectinload to reduce N+1 queries
def get_user_tasks_optimized(user_id: int, skip: int = 0, limit: int = 20):
    """Optimized query to get user tasks with minimal database hits"""
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .order_by(Task.created_at.desc())
    )

    tasks = session.exec(statement).all()
    return tasks

# Add database connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,  # Adjust based on expected load
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
)
```

### 3. Caching Implementation

```python
# backend/cache.py - Add caching for expensive operations
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def cache_result(expiration=300):  # Cache for 5 minutes
    """Decorator to cache function results in Redis"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)

            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))

            return result
        return wrapper
    return decorator

# Apply to expensive endpoints
@cache_result(expiration=300)
def get_popular_tasks():
    """Get popular tasks that don't change frequently"""
    # Expensive calculation or query
    pass
```

## Monitoring and Alerting

### 1. Health Check Endpoint

```python
# backend/routes/health.py
from fastapi import APIRouter
from datetime import datetime
import time
import subprocess

router = APIRouter(prefix="/health")

@router.get("/")
async def health_check():
    """Comprehensive health check including response time"""
    start_time = time.time()

    # Check database connectivity
    try:
        db_start = time.time()
        # Simple database query to check connectivity
        db_result = session.exec(select(func.count(Task.id))).one()
        db_time = (time.time() - db_start) * 1000
        db_status = "healthy"
    except Exception as e:
        db_time = 0
        db_status = f"error: {str(e)}"

    response_time = (time.time() - start_time) * 1000

    return {
        "status": "healthy" if response_time < 500 else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "response_time_ms": round(response_time, 2),
        "database": {
            "status": db_status,
            "response_time_ms": round(db_time, 2) if db_time else 0
        },
        "checks": {
            "response_time_under_500ms": response_time < 500,
            "database_connected": "error" not in db_status
        }
    }
```

### 2. Response Time SLA Dashboard

```python
# dashboard.py - Simple dashboard to visualize response times
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

def create_response_time_dashboard(db_path="api_monitor.db"):
    """Create a dashboard showing API response time trends"""
    conn = sqlite3.connect(db_path)

    # Get data for last 24 hours
    df = pd.read_sql_query('''
        SELECT
            datetime(timestamp) as timestamp,
            method,
            endpoint,
            response_time,
            success
        FROM response_times
        WHERE timestamp >= datetime('now', '-24 hours')
        ORDER BY timestamp
    ''', conn)

    conn.close()

    if df.empty:
        print("No data available for dashboard")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Response Time Trends', 'Endpoint Comparison',
                       'Success Rate Over Time', 'Response Time Distribution'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )

    # Response time trend
    for endpoint in df['endpoint'].unique():
        endpoint_data = df[df['endpoint'] == endpoint]
        fig.add_trace(
            go.Scatter(x=endpoint_data['timestamp'], y=endpoint_data['response_time'],
                      mode='lines+markers', name=f'{endpoint} Response Time'),
            row=1, col=1
        )

    # Add 500ms threshold line
    fig.add_hline(y=500, line_dash="dash", line_color="red",
                  annotation_text="500ms Threshold", row=1, col=1)

    # Endpoint comparison box plot
    for endpoint in df['endpoint'].unique():
        endpoint_data = df[df['endpoint'] == endpoint]['response_time']
        fig.add_trace(
            go.Box(y=endpoint_data, name=endpoint, showlegend=False),
            row=1, col=2
        )

    # Success rate over time
    df['date_minute'] = df['timestamp'].dt.floor('5min')
    success_rate = df.groupby('date_minute').agg({
        'success': lambda x: (x.sum() / len(x)) * 100
    }).reset_index()

    fig.add_trace(
        go.Scatter(x=success_rate['date_minute'], y=success_rate['success'],
                  mode='lines+markers', name='Success Rate (%)', line=dict(color='green')),
        row=2, col=1
    )

    # Response time distribution histogram
    fig.add_trace(
        go.Histogram(x=df['response_time'], nbinsx=50, name='Distribution'),
        row=2, col=2
    )

    fig.update_layout(height=800, title_text="API Response Time Dashboard")
    fig.show()

if __name__ == "__main__":
    create_response_time_dashboard()
```

## Testing Checklist

### Before Performance Testing
- [ ] Ensure database is properly indexed
- [ ] Set up monitoring tools
- [ ] Prepare test environment
- [ ] Establish baseline metrics
- [ ] Configure appropriate timeouts

### During Testing
- [ ] Monitor API response times continuously
- [ ] Track error rates and timeouts
- [ ] Monitor server resource usage
- [ ] Record concurrent user behavior
- [ ] Document any slow endpoints

### After Testing
- [ ] Analyze response time distributions
- [ ] Identify endpoints exceeding 500ms
- [ ] Document performance bottlenecks
- [ ] Create optimization recommendations
- [ ] Set up ongoing monitoring

## Remediation Strategies

### For Endpoints Exceeding 500ms
1. **Database Optimization**: Add indexes, optimize queries
2. **Caching**: Implement result caching for expensive operations
3. **Pagination**: Implement efficient pagination for large datasets
4. **Connection Pooling**: Optimize database connection handling
5. **Code Profiling**: Identify and optimize slow code paths
6. **Infrastructure Scaling**: Increase server resources if needed

This comprehensive approach ensures that all API endpoints meet the 500ms response time requirement while providing tools for ongoing monitoring and optimization.