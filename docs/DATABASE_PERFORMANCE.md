# Database Query Performance Verification Guide

This document provides comprehensive instructions for analyzing, monitoring, and optimizing database query performance in the Full-Stack Todo Application.

## Overview

Database performance is critical for application responsiveness and scalability. This guide covers tools, techniques, and best practices for monitoring and optimizing query performance in the PostgreSQL database used by the application.

## Performance Baselines

### Target Benchmarks

- **Simple SELECT queries**: < 10ms average execution time
- **Complex queries with JOINs**: < 50ms average execution time
- **INSERT/UPDATE/DELETE operations**: < 20ms average execution time
- **Query response time at 95th percentile**: < 100ms
- **Database connection time**: < 5ms
- **Index utilization**: > 95% of queries should use indexes

## Database Schema Analysis

### Current Schema Review

Based on the application's models, the following tables are expected:

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);
```

### Expected Indexes

```sql
-- Essential indexes for performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX idx_users_email ON users(email);
```

## Query Performance Monitoring

### Using PostgreSQL EXPLAIN

Analyze query execution plans using EXPLAIN:

```sql
-- Analyze a typical query
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT t.id, t.title, t.description, t.status, t.created_at
FROM tasks t
WHERE t.user_id = 1
ORDER BY t.created_at DESC
LIMIT 10;

-- Check index usage
EXPLAIN ANALYZE
SELECT * FROM tasks WHERE user_id = $1 AND status = $2;
```

### Query Analysis Commands

```sql
-- Find slow queries (> 100ms)
SELECT query, mean_time, calls
FROM pg_stat_statements
WHERE mean_time > 100
ORDER BY mean_time DESC;

-- Check for missing indexes
SELECT schemaname, tablename, attname, inherited, n_distinct
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;

-- Monitor active queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '10 seconds';
```

## Performance Testing Scripts

### Load Testing Queries

Create a script to test database performance under load:

```python
# database_performance_test.py
import asyncio
import time
import psycopg2
from concurrent.futures import ThreadPoolExecutor
import statistics

# Database connection parameters
DB_CONFIG = {
    'dbname': 'todo_app',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

def execute_query(query, params=None, connection_params=None):
    """Execute a single query and return execution time"""
    if connection_params is None:
        connection_params = DB_CONFIG

    start_time = time.time()

    try:
        with psycopg2.connect(**connection_params) as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                results = cur.fetchall()
    except Exception as e:
        print(f"Query failed: {e}")
        return float('inf'), []

    execution_time = time.time() - start_time
    return execution_time, results

def test_get_user_tasks(user_id, iterations=100):
    """Test performance of getting user tasks"""
    query = """
    SELECT t.id, t.title, t.description, t.status, t.created_at
    FROM tasks t
    WHERE t.user_id = %s
    ORDER BY t.created_at DESC
    LIMIT 20
    """

    times = []
    for _ in range(iterations):
        exec_time, _ = execute_query(query, (user_id,))
        times.append(exec_time)

    return times

def test_create_task(user_id, iterations=50):
    """Test performance of creating tasks"""
    query = """
    INSERT INTO tasks (title, description, status, user_id)
    VALUES (%s, %s, %s, %s)
    RETURNING id
    """

    times = []
    for i in range(iterations):
        exec_time, _ = execute_query(
            query,
            (f"Performance Test Task {i}", f"Description for test {i}", "pending", user_id)
        )
        times.append(exec_time)

    return times

def test_update_task(iterations=50):
    """Test performance of updating tasks"""
    # First get some task IDs to update
    get_query = "SELECT id FROM tasks WHERE status = 'pending' LIMIT %s"
    _, task_ids = execute_query(get_query, (iterations,))

    query = """
    UPDATE tasks
    SET status = 'completed', updated_at = NOW()
    WHERE id = %s
    """

    times = []
    for row in task_ids[:iterations]:
        task_id = row[0]
        exec_time, _ = execute_query(query, (task_id,))
        times.append(exec_time)

    return times

def analyze_performance_results(times, operation_name):
    """Analyze and print performance metrics"""
    if not times:
        print(f"No results for {operation_name}")
        return

    # Filter out infinite times (failed queries)
    valid_times = [t for t in times if t != float('inf')]

    if not valid_times:
        print(f"All queries failed for {operation_name}")
        return

    print(f"\n--- {operation_name} Performance ---")
    print(f"Total queries: {len(times)}")
    print(f"Successful queries: {len(valid_times)}")
    print(f"Failed queries: {len(times) - len(valid_times)}")
    print(f"Average time: {statistics.mean(valid_times)*1000:.2f}ms")
    print(f"Median time: {statistics.median(valid_times)*1000:.2f}ms")
    print(f"95th percentile: {sorted(valid_times)[int(0.95*len(valid_times))]*1000:.2f}ms")
    print(f"Slowest query: {max(valid_times)*1000:.2f}ms")
    print(f"Fastest query: {min(valid_times)*1000:.2f}ms")

def run_comprehensive_test():
    """Run comprehensive database performance tests"""
    print("Starting database performance tests...")

    # Test 1: Get user tasks
    print("\n1. Testing GET user tasks performance...")
    get_times = test_get_user_tasks(user_id=1, iterations=100)
    analyze_performance_results(get_times, "Get User Tasks")

    # Test 2: Create tasks
    print("\n2. Testing CREATE task performance...")
    create_times = test_create_task(user_id=1, iterations=50)
    analyze_performance_results(create_times, "Create Task")

    # Test 3: Update tasks
    print("\n3. Testing UPDATE task performance...")
    update_times = test_update_task(iterations=50)
    analyze_performance_results(update_times, "Update Task")

    # Test 4: Concurrent operations
    print("\n4. Testing concurrent operations...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []

        # Submit multiple concurrent requests
        for i in range(20):
            future = executor.submit(test_get_user_tasks, user_id=i%5+1, iterations=5)
            futures.append(future)

        concurrent_times = []
        for future in futures:
            times = future.result()
            concurrent_times.extend(times)

    analyze_performance_results(concurrent_times, "Concurrent Operations")

if __name__ == "__main__":
    run_comprehensive_test()
```

## Index Optimization

### Recommended Indexes

```sql
-- Primary indexes for the application
CREATE INDEX CONCURRENTLY idx_tasks_user_id_status ON tasks(user_id, status);
CREATE INDEX CONCURRENTLY idx_tasks_created_at_desc ON tasks(created_at DESC);
CREATE INDEX CONCURRENTLY idx_tasks_updated_at_desc ON tasks(updated_at DESC);

-- Composite index for common query patterns
CREATE INDEX CONCURRENTLY idx_tasks_user_status_created ON tasks(user_id, status, created_at DESC);

-- Text search index if needed for title/description search
CREATE INDEX CONCURRENTLY idx_tasks_title_gin ON tasks USING gin(to_tsvector('english', title));
```

### Index Monitoring

```sql
-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch,
    idx_scan
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Find unused indexes (potential candidates for removal)
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
AND idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

## Query Optimization Techniques

### Application-Level Optimizations

1. **Use Connection Pooling**:
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
)
```

2. **Implement Query Batching**:
```python
# Instead of multiple individual queries
for task_id in task_ids:
    db.execute(update_query, {'id': task_id, 'status': 'completed'})

# Batch update
query = "UPDATE tasks SET status = 'completed' WHERE id = ANY(:ids)"
db.execute(query, {'ids': task_ids})
```

3. **Use Efficient Pagination**:
```sql
-- Good: Cursor-based pagination
SELECT * FROM tasks
WHERE user_id = $1 AND id > $2
ORDER BY id ASC LIMIT $3;

-- Instead of OFFSET/LIMIT which becomes slower with higher offsets
SELECT * FROM tasks
WHERE user_id = $1
ORDER BY id ASC
LIMIT $2 OFFSET $3;
```

### Database Configuration Optimization

```sql
-- Shared buffer optimization (typically 25% of system RAM)
ALTER SYSTEM SET shared_buffers = '256MB';  -- Adjust based on your system

-- Effective cache size (typically 50-75% of system RAM)
ALTER SYSTEM SET effective_cache_size = '1GB';  -- Adjust based on your system

-- Work memory for sorting operations
ALTER SYSTEM SET work_mem = '4MB';

-- Maintenance work memory for maintenance operations
ALTER SYSTEM SET maintenance_work_mem = '64MB';
```

## Monitoring Tools

### Using pg_stat_statements

Enable and configure statement statistics:

```sql
-- Enable pg_stat_statements extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Reset statistics (do this before performance testing)
SELECT pg_stat_statements_reset();

-- Query the most time-consuming statements
SELECT
    query,
    calls,
    total_time,
    mean_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
WHERE userid = (SELECT usesysid FROM pg_user WHERE usename = current_user)
ORDER BY total_time DESC
LIMIT 10;
```

### Custom Monitoring Script

```python
# database_monitor.py
import psycopg2
import time
from datetime import datetime

class DatabaseMonitor:
    def __init__(self, connection_params):
        self.connection_params = connection_params
        self.connections = []

    def get_db_stats(self):
        """Get current database statistics"""
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor() as cur:
                # Get connection count
                cur.execute("SELECT count(*) FROM pg_stat_activity;")
                connections = cur.fetchone()[0]

                # Get active queries
                cur.execute("""
                    SELECT pid, now() - pg_stat_activity.query_start AS duration, query
                    FROM pg_stat_activity
                    WHERE (now() - pg_stat_activity.query_start) > interval '5 seconds'
                """)
                long_running_queries = cur.fetchall()

                # Get cache hit ratio
                cur.execute("""
                    SELECT
                        sum(blks_read) as blks_read,
                        sum(blks_hit) as blks_hit,
                        CASE
                            WHEN sum(blks_hit + blks_read) > 0
                            THEN (sum(blks_hit)::float / (sum(blks_hit + blks_read)::float) * 100)
                            ELSE 0
                        END as cache_hit_ratio
                    FROM pg_stat_database
                    WHERE datname = current_database();
                """)
                cache_stats = cur.fetchone()

                return {
                    'timestamp': datetime.now(),
                    'connections': connections,
                    'long_running_queries': long_running_queries,
                    'cache_hit_ratio': cache_stats[2]
                }

    def monitor_continuously(self, interval=10, duration=300):
        """Monitor database performance continuously"""
        start_time = time.time()

        while time.time() - start_time < duration:
            stats = self.get_db_stats()

            print(f"[{stats['timestamp']}] Connections: {stats['connections']}, "
                  f"Cache Hit Ratio: {stats['cache_hit_ratio']:.2f}%")

            if stats['long_running_queries']:
                print(f"Long running queries: {len(stats['long_running_queries'])}")
                for pid, duration, query in stats['long_running_queries'][:3]:  # Show top 3
                    print(f"  PID {pid}: {duration} - {query[:100]}...")

            time.sleep(interval)

# Usage
if __name__ == "__main__":
    monitor = DatabaseMonitor({
        'dbname': 'todo_app',
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost',
        'port': '5432'
    })

    # Monitor for 5 minutes, checking every 10 seconds
    monitor.monitor_continuously(interval=10, duration=300)
```

## Performance Testing Checklist

### Before Testing
- [ ] Ensure database is properly indexed
- [ ] Set up monitoring tools
- [ ] Prepare test data (1000+ records recommended)
- [ ] Configure connection pooling
- [ ] Set up baseline metrics

### During Testing
- [ ] Monitor query execution times
- [ ] Track database resource usage
- [ ] Record error rates
- [ ] Monitor cache hit ratios
- [ ] Watch for long-running queries

### After Testing
- [ ] Analyze performance metrics
- [ ] Identify slow queries
- [ ] Recommend optimizations
- [ ] Document findings
- [ ] Set up alerts for performance degradation

## Common Performance Issues and Solutions

### Issue 1: Slow Query Response Times

**Symptoms**: Queries taking > 100ms consistently
**Solutions**:
- Add appropriate indexes
- Optimize query structure
- Consider query result caching
- Increase database resources

### Issue 2: High Database Connection Usage

**Symptoms**: Connection timeouts, 503 errors
**Solutions**:
- Implement connection pooling
- Reduce connection lifetime
- Optimize query execution time
- Increase max_connections if needed

### Issue 3: Poor Cache Performance

**Symptoms**: Low cache hit ratio (< 80%)
**Solutions**:
- Increase shared_buffers
- Optimize query patterns
- Consider application-level caching

### Issue 4: Lock Contention

**Symptoms**: Deadlocks, queries hanging
**Solutions**:
- Optimize transaction isolation levels
- Reduce transaction scope
- Implement retry logic in application
- Use advisory locks for coordination

## Performance Optimization Recommendations

### Immediate Actions
1. Ensure all foreign key columns are indexed
2. Add composite indexes for common query patterns
3. Set up connection pooling with appropriate sizing
4. Enable query logging for slow queries

### Medium-term Improvements
1. Implement read replicas for read-heavy operations
2. Add application-level caching (Redis)
3. Optimize database configuration parameters
4. Implement query result caching

### Long-term Scaling
1. Database sharding for large datasets
2. Read/write separation
3. Asynchronous processing for heavy operations
4. Advanced monitoring and alerting

## Performance Monitoring Dashboard

Consider setting up a monitoring dashboard using tools like:
- **pgAdmin**: Built-in PostgreSQL monitoring
- **Grafana + Prometheus**: Custom dashboards
- **Superset**: Data visualization
- **Custom scripts**: Tailored monitoring solutions

This guide provides a comprehensive approach to monitoring and optimizing database query performance in the Full-Stack Todo Application, ensuring optimal performance under various load conditions.