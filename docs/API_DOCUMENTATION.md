# API Documentation

This document provides comprehensive documentation for the Full-Stack Todo Application API endpoints, including request/response formats, authentication requirements, and usage examples.

## Base URL

- Development: `http://localhost:8000`
- Production: `[Production URL]`

## Authentication

All protected endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt-token>
```

JWT tokens are obtained through the authentication endpoints and are valid for 24 hours by default.

## Common Response Format

Successful responses follow this format:
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

Error responses follow this format:
```json
{
  "success": false,
  "error": "Error message",
  "details": "Optional error details"
}
```

## Authentication Endpoints

### Register User
`POST /api/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe"
    },
    "token": "jwt-token-here"
  },
  "message": "User registered successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Validation error",
  "details": "Email already exists or invalid input"
}
```

### Login User
`POST /api/auth/login`

Authenticate a user and return JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe"
    },
    "token": "jwt-token-here"
  },
  "message": "Login successful"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "success": false,
  "error": "Invalid credentials",
  "details": "Email or password is incorrect"
}
```

## Task Management Endpoints

### Get All Tasks
`GET /api/tasks`

Retrieve all tasks for the authenticated user.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": 1,
        "title": "Complete project",
        "description": "Finish the full-stack todo app",
        "status": "pending",
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z",
        "user_id": 1
      },
      {
        "id": 2,
        "title": "Review code",
        "description": "Review pull requests",
        "status": "completed",
        "created_at": "2024-01-01T11:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z",
        "user_id": 1
      }
    ]
  },
  "message": "Tasks retrieved successfully"
}
```

### Create Task
`POST /api/tasks`

Create a new task for the authenticated user.

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "New Task",
  "description": "Task description here",
  "status": "pending"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "task": {
      "id": 3,
      "title": "New Task",
      "description": "Task description here",
      "status": "pending",
      "created_at": "2024-01-01T13:00:00Z",
      "updated_at": "2024-01-01T13:00:00Z",
      "user_id": 1
    }
  },
  "message": "Task created successfully"
}
```

### Get Task by ID
`GET /api/tasks/{task_id}`

Retrieve a specific task by ID.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Path Parameters:**
- `task_id` (integer): The ID of the task to retrieve

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "task": {
      "id": 1,
      "title": "Complete project",
      "description": "Finish the full-stack todo app",
      "status": "pending",
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z",
      "user_id": 1
    }
  },
  "message": "Task retrieved successfully"
}
```

**Error Response (404 Not Found):**
```json
{
  "success": false,
  "error": "Task not found",
  "details": "The requested task does not exist or does not belong to the authenticated user"
}
```

### Update Task
`PUT /api/tasks/{task_id}`

Update an existing task.

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Path Parameters:**
- `task_id` (integer): The ID of the task to update

**Request Body:**
```json
{
  "title": "Updated Task Title",
  "description": "Updated task description",
  "status": "completed"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "task": {
      "id": 1,
      "title": "Updated Task Title",
      "description": "Updated task description",
      "status": "completed",
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T14:00:00Z",
      "user_id": 1
    }
  },
  "message": "Task updated successfully"
}
```

### Partially Update Task
`PATCH /api/tasks/{task_id}`

Partially update a task (e.g., change only the status).

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Path Parameters:**
- `task_id` (integer): The ID of the task to update

**Request Body (any combination of fields):**
```json
{
  "status": "completed"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "task": {
      "id": 1,
      "title": "Complete project",
      "description": "Finish the full-stack todo app",
      "status": "completed",
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T15:00:00Z",
      "user_id": 1
    }
  },
  "message": "Task updated successfully"
}
```

### Delete Task
`DELETE /api/tasks/{task_id}`

Delete a task by ID.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Path Parameters:**
- `task_id` (integer): The ID of the task to delete

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1
  },
  "message": "Task deleted successfully"
}
```

## Error Codes

The API uses the following HTTP status codes:

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource does not exist
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- 100 requests per minute per IP address
- 1000 requests per hour per authenticated user

## CORS Policy

The API allows requests from:
- `http://localhost:3000` (development)
- `[Production frontend URL]` (production)

## Chat Endpoints

### Get Chat History
`GET /api/{user_id}/history`

Retrieve chat history for the authenticated user, with optional pagination and conversation filtering.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Path Parameters:**
- `user_id` (string): The ID of the user whose history to retrieve

**Query Parameters:**
- `conversation_id` (optional, integer): Filter history by specific conversation ID
- `limit` (optional, integer): Number of messages to return (default: 20, min: 1, max: 100)
- `offset` (optional, integer): Number of messages to skip (default: 0)

**Response (200 OK):**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hello, how can I add a task?",
      "created_at": "2024-01-01T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "You can say 'Add a task called test'",
      "created_at": "2024-01-01T10:01:00Z"
    }
  ],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 50,
    "has_more": true,
    "next_offset": 20,
    "prev_offset": null
  }
}
```

### Chat Endpoint
`POST /api/{user_id}/chat`

Send a message to the AI assistant and receive a streamed response with tool calls.

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Path Parameters:**
- `user_id` (string): The ID of the user sending the message

**Request Body:**
```json
{
  "message": "Add a task called 'Buy groceries'",
  "conversation_id": 123
}
```

**Response (200 OK with SSE stream):**
Streamed response containing:
- Tool calls: `data: {"tool": "add_task"}`
- Text chunks: `data: {"chunk": "Sure, I'll add that task for you."}`
- Completion: `data: {"done": true, "conversation_id": 124}`
- Errors: `data: {"error": "Error message"}`

### Get All Conversations
`GET /api/{user_id}/conversations`

Retrieve all conversations for the authenticated user.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Path Parameters:**
- `user_id` (string): The ID of the user whose conversations to retrieve

**Response (200 OK):**
```json
{
  "conversations": [
    {
      "id": 123,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T15:30:00Z",
      "preview": "Add a task called 'Buy groceries'...",
      "message_count": 5
    }
  ]
}
```

### Delete Conversation
`DELETE /api/{user_id}/conversations/{conversation_id}`

Delete a specific conversation and all its messages.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Path Parameters:**
- `user_id` (string): The ID of the user
- `conversation_id` (integer): The ID of the conversation to delete

**Response (200 OK):**
```json
{
  "message": "Conversation deleted successfully"
}
```

## Testing API Endpoints

You can test the API endpoints using tools like Postman, curl, or directly in your application:

**Example using curl:**
```bash
# Get all tasks
curl -H "Authorization: Bearer <your-jwt-token>" \
     http://localhost:8000/api/tasks

# Create a task
curl -X POST \
     -H "Authorization: Bearer <your-jwt-token>" \
     -H "Content-Type: application/json" \
     -d '{"title":"Test Task","description":"Test description","status":"pending"}' \
     http://localhost:8000/api/tasks

# Get chat history
curl -H "Authorization: Bearer <your-jwt-token>" \
     "http://localhost:8000/api/user123/history?limit=10&offset=0"

# Send a chat message
curl -X POST \
     -H "Authorization: Bearer <your-jwt-token>" \
     -H "Content-Type: application/json" \
     -d '{"message":"Add a task called test","conversation_id":123}' \
     http://localhost:8000/api/user123/chat
```