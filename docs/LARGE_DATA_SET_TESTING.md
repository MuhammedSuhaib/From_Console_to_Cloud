# Large Data Set Testing Guide (100+ Tasks)

This document provides instructions and tools for testing the Full-Stack Todo Application with large data sets containing 100 or more tasks per user, ensuring optimal performance and scalability.

## Overview

Testing with large data sets is crucial to validate the application's performance, memory usage, and responsiveness when handling substantial amounts of data. This guide covers data generation, performance testing, and optimization strategies for scenarios with 100+ tasks per user.

## Testing Objectives

- **Performance**: Ensure acceptable response times with large data sets
- **Memory Usage**: Monitor memory consumption during large data operations
- **Pagination**: Verify efficient data retrieval and pagination
- **Search/Filter**: Test filtering and search functionality with large data
- **UI Responsiveness**: Ensure frontend remains responsive with large data sets
- **Database Efficiency**: Validate efficient database queries with large data

## Data Generation Strategies

### 1. Automated Data Generation Script

Create a script to populate the database with 100+ tasks per user:

```python
# generate_large_dataset.py
import asyncio
import psycopg2
import random
import string
from datetime import datetime, timedelta
import uuid

# Database connection
DB_CONFIG = {
    'dbname': 'todo_app',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

# Sample data for realistic task generation
TASK_TITLES = [
    "Complete project proposal", "Review quarterly reports", "Team meeting preparation",
    "Client presentation", "Code review", "Bug fixes", "Feature development",
    "Documentation update", "Security audit", "Performance optimization",
    "Database migration", "API integration", "Testing automation", "CI/CD setup",
    "User feedback analysis", "Market research", "Competitor analysis", "Strategy planning"
]

TASK_DESCRIPTIONS = [
    "Detailed analysis and completion of the assigned project proposal",
    "Thorough review of quarterly financial and operational reports",
    "Preparation of materials and agenda for upcoming team meetings",
    "Development and refinement of client presentation materials",
    "Systematic review of code changes and improvements",
    "Identification and resolution of reported bugs",
    "Implementation of new features and functionality",
    "Updating and maintaining project documentation",
    "Comprehensive security assessment and audit",
    "Optimization of application performance and efficiency"
]

TASK_STATUSES = ['pending', 'in-progress', 'completed', 'blocked']

def generate_random_text(length=20):
    """Generate random text for task titles/descriptions"""
    return ' '.join(random.choices(string.ascii_lowercase.split(), k=length))

def generate_realistic_task(user_id, index):
    """Generate a realistic task with varied attributes"""
    title = random.choice(TASK_TITLES) + f" #{index}"
    description = random.choice(TASK_DESCRIPTIONS) + f" - Item #{index}"
    status = random.choice(TASK_STATUSES)

    # Random creation date within the last 30 days
    created_date = datetime.now() - timedelta(days=random.randint(0, 30))

    return {
        'title': title,
        'description': description,
        'status': status,
        'user_id': user_id,
        'created_at': created_date,
        'updated_at': created_date
    }

def create_test_users(cursor, num_users=5):
    """Create test users in the database"""
    users = []

    for i in range(num_users):
        email = f"testuser{i+1}@example.com"
        name = f"Test User {i+1}"
        password_hash = f"$2b$12${uuid.uuid4().hex}"  # Mock hash

        cursor.execute(
            "INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s) RETURNING id",
            (email, name, password_hash)
        )

        user_id = cursor.fetchone()[0]
        users.append({'id': user_id, 'email': email, 'name': name})
        print(f"Created user: {email} (ID: {user_id})")

    return users

def populate_tasks_for_user(cursor, user_id, num_tasks=150):
    """Populate tasks for a specific user"""
    print(f"Creating {num_tasks} tasks for user {user_id}...")

    # Generate all tasks first
    tasks_data = []
    for i in range(1, num_tasks + 1):
        task = generate_realistic_task(user_id, i)
        tasks_data.append((
            task['title'], task['description'], task['status'],
            task['user_id'], task['created_at'], task['updated_at']
        ))

    # Bulk insert using executemany
    insert_query = """
    INSERT INTO tasks (title, description, status, user_id, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.executemany(insert_query, tasks_data)
    print(f"Created {num_tasks} tasks for user {user_id}")

def generate_large_dataset(num_users=5, tasks_per_user=150):
    """Generate large dataset for testing"""
    print(f"Starting large dataset generation...")
    print(f"Creating {num_users} users with {tasks_per_user} tasks each ({num_users * tasks_per_user} total tasks)")

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                # Create test users
                users = create_test_users(cursor, num_users)

                # Create tasks for each user
                for user in users:
                    populate_tasks_for_user(cursor, user['id'], tasks_per_user)

                # Commit all changes
                conn.commit()
                print(f"\nDataset generation completed successfully!")
                print(f"Total: {num_users} users, {num_users * tasks_per_user} tasks")

    except Exception as e:
        print(f"Error during dataset generation: {e}")
        raise

def cleanup_test_data():
    """Remove test data from the database"""
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                # Delete tasks and users created during testing
                cursor.execute("""
                DELETE FROM tasks WHERE user_id IN (
                    SELECT id FROM users WHERE email LIKE 'testuser%@example.com'
                );
                """)

                cursor.execute("""
                DELETE FROM users WHERE email LIKE 'testuser%@example.com';
                """)

                conn.commit()
                print("Test data cleanup completed.")

    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        cleanup_test_data()
    else:
        # Generate dataset with default parameters
        generate_large_dataset(num_users=5, tasks_per_user=150)
```

### 2. API-Based Data Generation

Create a script that uses the application's API to generate data:

```javascript
// api-data-generator.js
const axios = require('axios');

const API_BASE = 'http://localhost:8000';
const NUM_USERS = 3;
const TASKS_PER_USER = 200;

// Sample data
const TITLES = [
  'Project Task', 'Research Task', 'Development Task', 'Testing Task',
  'Documentation Task', 'Meeting Preparation', 'Code Review',
  'Bug Fix', 'Feature Implementation', 'System Upgrade'
];

const DESCRIPTIONS = [
  'Detailed task description for comprehensive work.',
  'Implementation and testing of new functionality.',
  'Review and optimization of existing code.',
  'Documentation and reporting of progress.',
  'Coordination and communication with stakeholders.'
];

async function createUser(email, password, name) {
  try {
    const response = await axios.post(`${API_BASE}/api/auth/register`, {
      email,
      password,
      name
    });

    console.log(`Created user: ${email}`);
    return response.data.data.token;
  } catch (error) {
    console.error(`Failed to create user ${email}:`, error.response?.data || error.message);
    return null;
  }
}

async function createTasks(token, userId, count) {
  console.log(`Creating ${count} tasks for user ${userId}...`);

  for (let i = 0; i < count; i++) {
    const title = `${TITLES[i % TITLES.length]} ${i + 1}`;
    const description = `${DESCRIPTIONS[i % DESCRIPTIONS.length]} - Task #${i + 1}`;
    const status = ['pending', 'in-progress', 'completed'][i % 3];

    try {
      await axios.post(`${API_BASE}/api/tasks`, {
        title,
        description,
        status
      }, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if ((i + 1) % 50 === 0) {
        console.log(`Created ${i + 1}/${count} tasks...`);
      }
    } catch (error) {
      console.error(`Failed to create task ${i + 1}:`, error.response?.data || error.message);
    }
  }

  console.log(`Completed creating ${count} tasks for user ${userId}`);
}

async function generateLargeDataset() {
  console.log(`Generating large dataset: ${NUM_USERS} users with ${TASKS_PER_USER} tasks each`);

  for (let i = 0; i < NUM_USERS; i++) {
    const email = `large-data-user${i + 1}@example.com`;
    const password = 'SecurePass123!';
    const name = `Large Data User ${i + 1}`;

    console.log(`\nProcessing user ${i + 1}/${NUM_USERS}: ${email}`);

    const token = await createUser(email, password, name);
    if (token) {
      await createTasks(token, i + 1, TASKS_PER_USER);
    }

    // Small delay between users to avoid overwhelming the system
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  console.log('\nLarge dataset generation completed!');
}

// Run the data generation
generateLargeDataset().catch(console.error);
```

## Performance Testing with Large Data Sets

### 1. API Performance Testing

Create comprehensive tests for API endpoints with large data sets:

```python
# large_data_performance_test.py
import time
import requests
import threading
from concurrent.futures import ThreadPoolExecutor
import statistics
import json

class LargeDataSetTester:
    def __init__(self, base_url, auth_tokens):
        self.base_url = base_url
        self.auth_tokens = auth_tokens
        self.results = {
            'get_tasks': [],
            'create_task': [],
            'update_task': [],
            'delete_task': []
        }

    def time_api_call(self, method, endpoint, headers=None, data=None):
        """Time an API call and return execution time"""
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

            execution_time = time.time() - start_time
            return execution_time, response.status_code, response.json() if response.content else {}
        except Exception as e:
            execution_time = time.time() - start_time
            return execution_time, 500, {'error': str(e)}

    def test_get_tasks_performance(self, token, user_id, iterations=10):
        """Test performance of getting tasks with large data set"""
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        times = []
        for i in range(iterations):
            exec_time, status, response = self.time_api_call(
                'GET', f'/api/tasks', headers
            )
            times.append(exec_time)

            if status != 200:
                print(f"Warning: GET /api/tasks returned {status}")

        avg_time = statistics.mean(times) if times else 0
        print(f"GET /api/tasks for user {user_id}: {avg_time*1000:.2f}ms avg over {iterations} calls")

        # Store results
        self.results['get_tasks'].extend(times)
        return times

    def test_pagination_performance(self, token, user_id, page_size=20):
        """Test pagination performance with large data sets"""
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        times = []
        offset = 0
        total_tasks_fetched = 0

        print(f"Testing pagination for user {user_id}...")

        while True:
            # Simulate pagination (though our API might use different approach)
            exec_time, status, response = self.time_api_call(
                'GET', f'/api/tasks?limit={page_size}&offset={offset}', headers
            )

            times.append(exec_time)

            if status != 200 or not response.get('data', {}).get('tasks'):
                break

            tasks_count = len(response.get('data', {}).get('tasks', []))
            total_tasks_fetched += tasks_count

            if tasks_count < page_size:
                break

            offset += page_size

            if len(times) % 5 == 0:  # Progress indicator
                print(f"  Fetched {total_tasks_fetched} tasks...")

        avg_time = statistics.mean(times) if times else 0
        print(f"Pagination test for user {user_id}: {avg_time*1000:.2f}ms avg, {total_tasks_fetched} total tasks")

        return times

    def test_search_filter_performance(self, token, user_id):
        """Test search and filter performance"""
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        test_filters = [
            {'status': 'pending'},
            {'status': 'completed'},
            {'limit': 50},  # Test with different limits
            {'limit': 100},
        ]

        times = []

        for filter_params in test_filters:
            param_str = '&'.join([f"{k}={v}" for k, v in filter_params.items()])
            endpoint = f"/api/tasks?{param_str}"

            exec_time, status, response = self.time_api_call(
                'GET', endpoint, headers
            )

            times.append(exec_time)
            print(f"  Filter {filter_params}: {exec_time*1000:.2f}ms")

        avg_time = statistics.mean(times) if times else 0
        print(f"Search/Filter test for user {user_id}: {avg_time*1000:.2f}ms avg")

        return times

    def run_comprehensive_tests(self):
        """Run comprehensive performance tests"""
        print("Starting large data set performance tests...\n")

        for i, token in enumerate(self.auth_tokens):
            user_id = i + 1

            print(f"=== Testing User {user_id} ===")

            # Test basic get tasks performance
            self.test_get_tasks_performance(token, user_id, iterations=5)

            # Test pagination
            self.test_pagination_performance(token, user_id)

            # Test search/filter performance
            self.test_search_filter_performance(token, user_id)

            print()  # Empty line for readability

        # Calculate overall statistics
        self.calculate_overall_stats()

    def calculate_overall_stats(self):
        """Calculate and display overall performance statistics"""
        print("=== Overall Performance Statistics ===")

        for operation, times in self.results.items():
            if times:
                print(f"\n{operation.upper()}:")
                print(f"  Total calls: {len(times)}")
                print(f"  Average time: {statistics.mean(times)*1000:.2f}ms")
                print(f"  Median time: {statistics.median(times)*1000:.2f}ms")
                print(f"  95th percentile: {sorted(times)[int(0.95*len(times))]*1000:.2f}ms")
                print(f"  Min time: {min(times)*1000:.2f}ms")
                print(f"  Max time: {max(times)*1000:.2f}ms")
                print(f"  Success rate: {len([t for t in times if t < 2.0])}/{len(times)} (under 2s)")

# Usage example
if __name__ == "__main__":
    # Example tokens (these would come from authentication)
    test_tokens = [
        "token1", "token2", "token3"  # Replace with actual tokens
    ]

    tester = LargeDataSetTester("http://localhost:8000", test_tokens)
    tester.run_comprehensive_tests()
```

### 2. Frontend Performance Testing

Test the frontend's ability to handle large data sets:

```javascript
// frontend-performance-test.js
class FrontendPerformanceTester {
  constructor() {
    this.metrics = {
      renderTimes: [],
      memoryUsage: [],
      interactionDelays: []
    };
  }

  async measureRenderTime(renderFunction) {
    const startTime = performance.now();
    await renderFunction();
    const endTime = performance.now();
    const renderTime = endTime - startTime;

    this.metrics.renderTimes.push(renderTime);
    return renderTime;
  }

  async measureMemoryUsage() {
    if (performance.memory) {
      const memoryInfo = {
        used: performance.memory.usedJSHeapSize,
        total: performance.memory.totalJSHeapSize,
        limit: performance.memory.jsHeapSizeLimit
      };

      this.metrics.memoryUsage.push(memoryInfo);
      return memoryInfo;
    }
    return null;
  }

  async testTaskListRendering(taskCount) {
    console.log(`Testing rendering of ${taskCount} tasks...`);

    // Simulate task data
    const tasks = Array.from({ length: taskCount }, (_, i) => ({
      id: i + 1,
      title: `Task ${i + 1}`,
      description: `Description for task ${i + 1}`,
      status: ['pending', 'in-progress', 'completed'][i % 3],
      createdAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000)
    }));

    // Measure render time
    const renderTime = await this.measureRenderTime(async () => {
      // Simulate rendering a task list component
      const taskElements = tasks.map(task => {
        return `
          <div class="task-item" data-id="${task.id}">
            <h3>${task.title}</h3>
            <p>${task.description}</p>
            <span class="status">${task.status}</span>
          </div>
        `;
      }).join('');

      // In a real test, this would be mounted to the DOM
      // document.getElementById('task-list').innerHTML = taskElements;
    });

    const memoryInfo = await this.measureMemoryUsage();

    console.log(`Rendered ${taskCount} tasks in ${renderTime.toFixed(2)}ms`);
    if (memoryInfo) {
      console.log(`Memory used: ${(memoryInfo.used / 1024 / 1024).toFixed(2)} MB`);
    }
  }

  async testPaginationPerformance(totalTasks, pageSize = 20) {
    console.log(`Testing pagination with ${totalTasks} total tasks, ${pageSize} per page...`);

    const totalPages = Math.ceil(totalTasks / pageSize);
    const pageRenderTimes = [];

    for (let page = 1; page <= totalPages; page++) {
      const startIndex = (page - 1) * pageSize;
      const endIndex = Math.min(startIndex + pageSize, totalTasks);
      const pageTasks = Array.from({ length: endIndex - startIndex }, (_, i) => ({
        id: startIndex + i + 1,
        title: `Task ${startIndex + i + 1}`,
        status: ['pending', 'in-progress', 'completed'][(startIndex + i) % 3]
      }));

      const renderTime = await this.measureRenderTime(async () => {
        // Simulate rendering a page of tasks
        const pageElements = pageTasks.map(task => `
          <div class="task-item" data-id="${task.id}">
            <span>${task.title}</span>
            <span class="status">${task.status}</span>
          </div>
        `).join('');

        // In a real test, this would be mounted to the DOM
      });

      pageRenderTimes.push(renderTime);

      if (page % 10 === 0) {
        console.log(`Completed page ${page}/${totalPages}`);
      }
    }

    const avgPageTime = pageRenderTimes.reduce((a, b) => a + b, 0) / pageRenderTimes.length;
    console.log(`Average page render time: ${avgPageTime.toFixed(2)}ms`);
  }

  async runTests() {
    console.log("Starting frontend performance tests...\n");

    // Test with different sizes
    const testSizes = [50, 100, 200, 500];

    for (const size of testSizes) {
      await this.testTaskListRendering(size);
      console.log(); // Empty line
    }

    // Test pagination
    await this.testPaginationPerformance(300, 25);

    // Display summary
    this.displaySummary();
  }

  displaySummary() {
    console.log("\n=== Frontend Performance Summary ===");

    if (this.metrics.renderTimes.length > 0) {
      const avgRenderTime = this.metrics.renderTimes.reduce((a, b) => a + b, 0) / this.metrics.renderTimes.length;
      const maxRenderTime = Math.max(...this.metrics.renderTimes);
      const minRenderTime = Math.min(...this.metrics.renderTimes);

      console.log(`Render Times:`);
      console.log(`  Average: ${avgRenderTime.toFixed(2)}ms`);
      console.log(`  Min: ${minRenderTime.toFixed(2)}ms`);
      console.log(`  Max: ${maxRenderTime.toFixed(2)}ms`);
    }

    if (this.metrics.memoryUsage.length > 0) {
      const avgMemory = this.metrics.memoryUsage.reduce((sum, mem) => sum + mem.used, 0) / this.metrics.memoryUsage.length;
      console.log(`Memory Usage:`);
      console.log(`  Average: ${(avgMemory / 1024 / 1024).toFixed(2)} MB`);
    }
  }
}

// Run the tests
const tester = new FrontendPerformanceTester();
tester.runTests().catch(console.error);
```

## Optimization Strategies

### 1. Database Optimization

```sql
-- Optimize queries for large data sets
-- Add composite indexes for common query patterns
CREATE INDEX CONCURRENTLY idx_tasks_user_status_created ON tasks(user_id, status, created_at DESC);

-- Optimize for pagination
CREATE INDEX CONCURRENTLY idx_tasks_user_id_created ON tasks(user_id, created_at DESC);

-- Consider partial indexes for common filters
CREATE INDEX CONCURRENTLY idx_tasks_pending_user ON tasks(user_id) WHERE status = 'pending';
```

### 2. API Level Optimization

```python
# backend/routers/tasks.py optimization
from fastapi import Query
from typing import Optional
import math

# Add pagination support
@app.get("/api/tasks")
async def get_user_tasks(
    current_user: dict = Security(verify_token),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by task status"),
    search: Optional[str] = Query(None, description="Search in title/description")
):
    user_id = current_user["sub"]

    # Build query with filters
    query = select(Task).where(Task.user_id == user_id)

    if status:
        query = query.where(Task.status == status)

    if search:
        query = query.where(
            Task.title.contains(search) | Task.description.contains(search)
        )

    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(Task.created_at.desc())

    tasks = session.exec(query).all()

    # Get total count for pagination metadata
    count_query = select(func.count(Task.id)).where(Task.user_id == user_id)
    if status:
        count_query = count_query.where(Task.status == status)
    if search:
        count_query = count_query.where(
            Task.title.contains(search) | Task.description.contains(search)
        )

    total_count = session.exec(count_query).one()

    return {
        "data": {
            "tasks": [task.dict() for task in tasks],
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total_count,
                "pages": math.ceil(total_count / limit),
                "current_page": math.ceil(skip / limit) + 1
            }
        },
        "message": "Tasks retrieved successfully"
    }
```

### 3. Frontend Optimization

```typescript
// frontend/lib/hooks/usePaginatedTasks.ts
import { useState, useEffect, useCallback } from 'react';
import { api } from '../api';

interface PaginationParams {
  page: number;
  limit: number;
  status?: string;
  search?: string;
}

interface PaginatedTasks {
  tasks: Task[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}

export const usePaginatedTasks = () => {
  const [paginatedTasks, setPaginatedTasks] = useState<PaginatedTasks>({
    tasks: [],
    pagination: { page: 1, limit: 20, total: 0, pages: 0 }
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async (params: PaginationParams) => {
    setLoading(true);
    setError(null);

    try {
      // In a real implementation, this would call the paginated API
      const response = await api.request(`/api/tasks?page=${params.page}&limit=${params.limit}${params.status ? `&status=${params.status}` : ''}${params.search ? `&search=${params.search}` : ''}`);

      setPaginatedTasks(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  }, []);

  return { paginatedTasks, loading, error, fetchTasks };
};
```

## Testing Checklist

### Before Testing Large Data Sets
- [ ] Ensure database has sufficient storage space
- [ ] Verify backup procedures are in place
- [ ] Set up monitoring tools for performance metrics
- [ ] Prepare cleanup scripts for test data
- [ ] Configure appropriate timeout values

### During Testing
- [ ] Monitor database performance metrics
- [ ] Track API response times
- [ ] Monitor memory usage
- [ ] Record error rates and exceptions
- [ ] Watch for timeout issues

### After Testing
- [ ] Analyze performance metrics
- [ ] Document any performance bottlenecks
- [ ] Cleanup test data
- [ ] Compare results with baseline metrics
- [ ] Identify optimization opportunities

## Expected Results

With proper optimization, the application should handle 100+ tasks per user with:
- API response times < 500ms for standard operations
- Page load times < 2 seconds for task lists
- Smooth pagination performance
- Acceptable memory usage (< 100MB for task views)
- No significant degradation in user experience

This testing approach ensures the application can scale effectively with growing data volumes while maintaining optimal performance.