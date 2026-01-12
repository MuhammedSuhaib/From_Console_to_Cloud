# Concurrent User Testing Guide

This document outlines procedures and best practices for testing the Full-Stack Todo Application with multiple concurrent users to ensure scalability and reliability.

## Overview

Testing with multiple concurrent users is essential to validate the application's performance, data isolation, and stability under realistic usage conditions. This guide covers different approaches to simulate concurrent users and validate the system's behavior.

## Testing Objectives

- **Data Isolation**: Verify that users cannot access each other's data
- **Performance**: Ensure acceptable response times under load
- **Stability**: Confirm the application remains stable with multiple concurrent sessions
- **Authentication**: Validate JWT token handling with multiple users
- **Database Concurrency**: Test database operations with concurrent access

## Testing Scenarios

### 1. Basic Data Isolation Test

**Objective**: Verify that users can only access their own tasks.

**Steps**:
1. Create two user accounts: User A and User B
2. User A creates 5 tasks
3. User B creates 3 tasks
4. User A logs in and verifies they only see their 5 tasks
5. User B logs in and verifies they only see their 3 tasks
6. Verify neither user can access the other's tasks through API calls

**Expected Results**:
- Each user only sees their own tasks
- API calls return 404 or 403 for other users' tasks
- No data leakage between users

### 2. Concurrent Task Operations Test

**Objective**: Test simultaneous CRUD operations by multiple users.

**Steps**:
1. Create 5 user accounts
2. Have each user simultaneously:
   - Create a new task
   - Update an existing task
   - Delete a task
   - Retrieve their task list
3. Monitor response times and error rates
4. Verify data integrity after operations

**Expected Results**:
- All operations complete successfully
- Response times remain acceptable (< 500ms)
- No race conditions occur
- Data integrity is maintained

### 3. High-Concurrency Load Test

**Objective**: Test the application under high concurrent load.

**Steps**:
1. Use load testing tools (e.g., Artillery, k6, JMeter)
2. Simulate 50-100 concurrent users performing mixed operations
3. Monitor server resource usage (CPU, memory, database connections)
4. Track error rates and response time percentiles

**Expected Results**:
- Server handles load without crashing
- Error rate < 1%
- 95th percentile response time < 1000ms
- Database connections don't exceed limits

## Manual Testing Approach

### Setup Multiple Browser Sessions

1. **Prepare Test Accounts**:
   ```bash
   # Create test users via API
   curl -X POST http://localhost:8000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test1@example.com", "password":"password123", "name":"Test User 1"}'

   curl -X POST http://localhost:8000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test2@example.com", "password":"password123", "name":"Test User 2"}'
   ```

2. **Browser Sessions**:
   - Open multiple browser windows/incognito mode
   - Log in with different test accounts
   - Perform concurrent operations
   - Monitor each session independently

### API-Based Testing

Create a test script to simulate multiple users:

```javascript
// concurrent-test.js
const axios = require('axios');

// Test users configuration
const testUsers = [
  {
    email: 'test1@example.com',
    password: 'password123',
    token: null,
    tasks: []
  },
  {
    email: 'test2@example.com',
    password: 'password123',
    token: null,
    tasks: []
  }
  // Add more users as needed
];

const API_BASE = 'http://localhost:8000';

async function authenticateUser(user) {
  try {
    const response = await axios.post(`${API_BASE}/api/auth/login`, {
      email: user.email,
      password: user.password
    });

    user.token = response.data.data.token;
    console.log(`User ${user.email} authenticated`);
    return true;
  } catch (error) {
    console.error(`Failed to authenticate user ${user.email}:`, error.message);
    return false;
  }
}

async function createUserTasks(user, count = 3) {
  for (let i = 0; i < count; i++) {
    try {
      const response = await axios.post(`${API_BASE}/api/tasks`, {
        title: `Concurrent Task ${i + 1}`,
        description: `Task created by ${user.email}`,
        status: 'pending'
      }, {
        headers: {
          'Authorization': `Bearer ${user.token}`
        }
      });

      user.tasks.push(response.data.data.task.id);
      console.log(`Task created by ${user.email}: ${response.data.data.task.id}`);
    } catch (error) {
      console.error(`Failed to create task for ${user.email}:`, error.message);
    }
  }
}

async function runConcurrentTest() {
  console.log('Starting concurrent user test...');

  // Authenticate all users
  const authPromises = testUsers.map(user => authenticateUser(user));
  await Promise.all(authPromises);

  // Create tasks concurrently
  const taskPromises = testUsers.map(user => createUserTasks(user));
  await Promise.all(taskPromises);

  // Verify data isolation
  for (const user of testUsers) {
    try {
      const response = await axios.get(`${API_BASE}/api/tasks`, {
        headers: {
          'Authorization': `Bearer ${user.token}`
        }
      });

      const taskCount = response.data.data.tasks.length;
      console.log(`User ${user.email} sees ${taskCount} tasks`);

      // Verify user only sees their own tasks
      if (taskCount !== user.tasks.length) {
        console.error(`Data isolation violation for ${user.email}: expected ${user.tasks.length}, got ${taskCount}`);
      } else {
        console.log(`✓ Data isolation maintained for ${user.email}`);
      }
    } catch (error) {
      console.error(`Failed to get tasks for ${user.email}:`, error.message);
    }
  }

  console.log('Concurrent user test completed');
}

// Run the test
runConcurrentTest().catch(console.error);
```

## Automated Testing with Load Testing Tools

### Using Artillery

Create a load test scenario:

```yaml
# concurrent-test.yml
config:
  target: 'http://localhost:8000'
  phases:
    - duration: 60
      arrivalRate: 5
      name: "Warm up phase"
    - duration: 300
      arrivalRate: 10
      name: "Sustained load phase"
  defaults:
    headers:
      Content-Type: 'application/json'

scenarios:
  - name: "User task operations"
    weight: 3
    flow:
      - function: "generateUserSession"
      - post:
          url: "/api/auth/login"
          json:
            email: "{{ $processEnvironment.email }}"
            password: "{{ $processEnvironment.password }}"
          capture:
            - json: "$.data.token"
              as: "token"
      - get:
          url: "/api/tasks"
          headers:
            Authorization: "Bearer {{ token }}"
      - post:
          url: "/api/tasks"
          headers:
            Authorization: "Bearer {{ token }}"
          json:
            title: "Load test task"
            description: "Created during load test"
            status: "pending"

  - name: "User registration"
    weight: 1
    flow:
      - function: "generateRandomUser"
      - post:
          url: "/api/auth/register"
          json:
            email: "{{ $environment.email }}"
            password: "{{ $environment.password }}"
            name: "{{ $environment.name }}"
```

### Using k6

```javascript
// k6-concurrent-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 10 },    // Ramp up to 10 users
    { duration: '5m', target: 10 },    // Maintain 10 users
    { duration: '1m', target: 0 },     // Ramp down to 0
  ],
};

// Test user data
const testUsers = [
  { email: 'test1@example.com', password: 'password123', name: 'Test User 1' },
  { email: 'test2@example.com', password: 'password123', name: 'Test User 2' },
  // Add more users as needed
];

export default function () {
  // Select a random user for this VU (virtual user)
  const user = testUsers[Math.floor(Math.random() * testUsers.length)];

  // Login
  const loginRes = http.post('http://localhost:8000/api/auth/login', JSON.stringify({
    email: user.email,
    password: user.password,
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  check(loginRes, {
    'login successful': (r) => r.status === 200,
    'has token': (r) => r.json().data.token !== undefined,
  });

  if (loginRes.status === 200) {
    const token = loginRes.json().data.token;

    // Get tasks
    const tasksRes = http.get('http://localhost:8000/api/tasks', {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    });

    check(tasksRes, {
      'get tasks successful': (r) => r.status === 200,
    });

    // Create a task
    const createRes = http.post('http://localhost:8000/api/tasks', JSON.stringify({
      title: `Task from VU ${__VU}`,
      description: `Created at ${Date.now()}`,
      status: 'pending',
    }), {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    });

    check(createRes, {
      'create task successful': (r) => r.status === 201,
    });
  }

  sleep(1); // Wait 1 second between iterations
}
```

## Database Concurrency Testing

### Testing Database Connections

Monitor database connection usage during concurrent testing:

```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'todo_app';

-- Check for connection limits
SHOW max_connections;

-- Monitor long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
```

### Race Condition Testing

Test for potential race conditions in task updates:

```javascript
// Race condition test
async function testRaceCondition() {
  const user = testUsers[0];

  // Authenticate user
  await authenticateUser(user);

  // Create a task
  const taskRes = await axios.post(`${API_BASE}/api/tasks`, {
    title: 'Race condition test',
    description: 'Testing concurrent updates',
    status: 'pending'
  }, {
    headers: { 'Authorization': `Bearer ${user.token}` }
  });

  const taskId = taskRes.data.data.task.id;

  // Simulate concurrent updates to the same task
  const updatePromises = Array.from({ length: 5 }, (_, i) =>
    axios.put(`${API_BASE}/api/tasks/${taskId}`, {
      title: `Updated by request ${i}`,
      description: 'Updated during race condition test',
      status: 'in-progress'
    }, {
      headers: { 'Authorization': `Bearer ${user.token}` }
    })
  );

  const results = await Promise.allSettled(updatePromises);

  // Count successful vs failed updates
  const successful = results.filter(r => r.status === 'fulfilled').length;
  const failed = results.filter(r => r.status === 'rejected').length;

  console.log(`Race condition test - Successful: ${successful}, Failed: ${failed}`);

  // Verify final state of the task
  const finalRes = await axios.get(`${API_BASE}/api/tasks/${taskId}`, {
    headers: { 'Authorization': `Bearer ${user.token}` }
  });

  console.log('Final task state:', finalRes.data.data.task);
}
```

## Monitoring and Metrics

### Key Metrics to Track

1. **Response Times**:
   - Average response time
   - 95th percentile response time
   - 99th percentile response time

2. **Throughput**:
   - Requests per second (RPS)
   - Transactions per second (TPS)

3. **Error Rates**:
   - HTTP error rate (< 1% target)
   - Server error rate (5xx errors)

4. **Resource Utilization**:
   - CPU usage
   - Memory usage
   - Database connections
   - Network I/O

### Monitoring Commands

```bash
# Monitor server resources during testing
htop

# Monitor database connections
docker exec -it from_console_to_cloud-db-1 psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Monitor API responses
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/api/tasks"

# curl-format.txt content:
time_namelookup:  %{time_namelookup}\n
time_connect:  %{time_connect}\n
time_appconnect:  %{time_appconnect}\n
time_pretransfer:  %{time_pretransfer}\n
time_redirect:  %{time_redirect}\n
time_starttransfer:  %{time_starttransfer}\n
time_total:  %{time_total}\n
```

## Expected Results and Pass Criteria

### Performance Benchmarks

- **Response Time**: < 500ms for 95% of requests under normal load
- **Throughput**: Support 10+ concurrent users performing operations
- **Error Rate**: < 1% error rate during testing
- **Data Integrity**: 100% data isolation maintained

### Scalability Indicators

- Linear response time growth with increasing load
- Graceful degradation under heavy load (no crashes)
- Proper error handling when resources are exhausted

## Troubleshooting Common Issues

### Data Leakage Between Users

**Symptoms**: Users see tasks belonging to other users
**Causes**:
- Missing user_id filters in database queries
- Improper JWT token validation
- Authentication bypass vulnerabilities

**Solutions**:
- Verify all database queries filter by user_id
- Double-check JWT token validation middleware
- Test authentication required endpoints without tokens

### Database Connection Exhaustion

**Symptoms**: 500 errors, slow response times
**Causes**: Too many concurrent database connections
**Solutions**:
- Implement connection pooling
- Optimize database queries
- Add circuit breaker patterns

### Memory Leaks Under Load

**Symptoms**: Gradually increasing memory usage
**Causes**: Unclosed connections, cached data accumulation
**Solutions**:
- Implement proper resource cleanup
- Add memory monitoring
- Optimize session management

## Reporting and Documentation

After concurrent user testing, document:

1. **Test Results**: Response times, throughput, error rates
2. **Issues Found**: Any data isolation violations or performance problems
3. **Recommendations**: Optimizations needed for production
4. **Scalability Limits**: Maximum supported concurrent users
5. **Configuration Notes**: Optimal settings for different load levels

This testing approach ensures the application can handle real-world usage patterns with multiple users accessing the system simultaneously while maintaining data security and performance standards.